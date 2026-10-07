"""HTTP API and web app over the adviser list.

    python -m cfadvisers serve [--host 127.0.0.1] [--port 8000]

Read-only. Auth: when CFA_API_TOKEN is set, /v1/* (except /v1/health) needs `Authorization: Bearer <token>`
or `?token=<token>`; the web page asks for the token once and keeps it in the browser. When it is unset
the API is open (fine on localhost or behind your own access control).
OpenAPI: /v1/openapi.json, interactive docs: /v1/docs.
"""
from __future__ import annotations

import csv
import hmac
import io
import os
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from . import __version__, model
from .store import DATA, Store

STATIC = Path(__file__).resolve().parent / "static"

CSV_FIELDS = [
    "name", "website", "firm_type_label", "parent", "hq", "hq_region", "offices", "coverage", "regions_covered",
    "cf_professionals", "cf_professionals_basis", "ebitda_min_m", "ebitda_max_m", "deal_ev_min_m", "deal_ev_max_m",
    "deal_size_basis", "deal_size_note", "covers_sme", "services", "sectors", "sector_note", "contact_email",
    "contact_phone", "team_url", "contact_url", "linkedin_url", "description", "pitchbook_deals", "sources",
    "completeness", "id",
]


def to_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CSV_FIELDS, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        flat = {k: ("; ".join(v) if isinstance(v, list) else v) for k, v in r.items()}
        flat["pitchbook_deals"] = (r.get("pitchbook") or {}).get("deals")
        w.writerow(flat)
    return buf.getvalue()


def create_app(data_dir: Path = DATA) -> FastAPI:
    store = Store(data_dir)
    app = FastAPI(title="UK Corporate Finance Advisers", version=__version__,
                  description="Directory of UK corporate finance / M&A advisers, filterable by deal size "
                              "(EBITDA / EV), firm type, region and sector. Deal sizes are in £m. A firm's "
                              "EBITDA range comes from its stated EBITDA range, else its EV range divided by "
                              f"the EV/EBITDA multiple (default {model.ev_multiple():g}x).",
                  docs_url="/v1/docs", openapi_url="/v1/openapi.json", redoc_url=None)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])
    app.state.store = store

    def auth(request: Request) -> None:
        token = os.environ.get("CFA_API_TOKEN")
        if not token:
            return
        h = request.headers.get("authorization") or ""
        got = h[7:].strip() if h.lower().startswith("bearer ") else request.query_params.get("token")
        if not (got and hmac.compare_digest(got.encode(), token.encode())):
            raise HTTPException(401, "a valid bearer token is required", headers={"WWW-Authenticate": "Bearer"})

    @app.get("/v1/health", tags=["meta"])
    def health():
        return {"ok": True, "version": __version__, "advisers": len(store.rows),
                "auth": bool(os.environ.get("CFA_API_TOKEN"))}

    @app.get("/v1/meta", tags=["meta"], dependencies=[Depends(auth)])
    def meta():
        """Vocabularies for the filters, plus the SME band and EV/EBITDA multiple in use."""
        return {"regions": model.REGIONS, "firm_types": model.FIRM_TYPES, "services": model.SERVICES,
                "sectors": model.SECTORS, "coverage": model.COVERAGE, "sme_band_ebitda_m": list(model.SME_BAND),
                "ev_to_ebitda_multiple": model.ev_multiple(), "csv_fields": CSV_FIELDS}

    @app.get("/v1/stats", tags=["meta"], dependencies=[Depends(auth)])
    def stats():
        return store.stats() | {"facets": store.facets()}

    @app.get("/v1/advisers", tags=["advisers"], dependencies=[Depends(auth)],
             responses={200: {"content": {"application/json": {}, "text/csv": {}}}})
    def advisers(
        q: str | None = Query(None, description="free text: name, town, sector, description"),
        firm_type: list[str] | None = Query(None, description=f"any of {list(model.FIRM_TYPES)}"),
        region: list[str] | None = Query(None, description="UK region the firm covers (any of)"),
        hq_region: list[str] | None = Query(None, description="UK region of the firm's HQ (any of)"),
        sector: list[str] | None = Query(None, description="sector (any of)"),
        service: list[str] | None = Query(None, description=f"any of {list(model.SERVICES)}"),
        coverage: list[str] | None = Query(None, description=f"any of {model.COVERAGE}"),
        ebitda_min: float | None = Query(None, description="£m: keep firms whose core EBITDA range reaches this"),
        ebitda_max: float | None = Query(None, description="£m: keep firms whose core EBITDA range starts below this"),
        sme: bool | None = Query(None, description="shorthand for ebitda_min=0.5&ebitda_max=2"),
        include_unknown_size: bool = Query(False, description="with a size filter, also keep firms of unknown size"),
        cf_min: int | None = Query(None, description="minimum number of CF professionals"),
        cf_max: int | None = Query(None, description="maximum number of CF professionals"),
        has_email: bool | None = None,
        has_contact: bool | None = Query(None, description="has an email, team page or contact page"),
        sort: Literal["name", "cf_professionals", "ebitda_min", "ebitda_max", "hq", "firm_type", "completeness",
                      "pitchbook_deals"] = "name",
        order: Literal["asc", "desc"] = "asc",
        limit: int = Query(100, ge=1, le=5000),
        offset: int = Query(0, ge=0),
        format: Literal["json", "csv"] = "json",
    ):
        """Search and filter the directory. `format=csv` returns every match (no paging) as CSV."""
        rows = store.query(q=q, firm_type=firm_type, region=region, hq_region=hq_region, sector=sector,
                           service=service, coverage=coverage, ebitda_min=ebitda_min, ebitda_max=ebitda_max,
                           sme=sme, include_unknown_size=include_unknown_size, cf_min=cf_min, cf_max=cf_max,
                           has_email=has_email, has_contact=has_contact, sort=sort, order=order)
        if format == "csv":
            return Response(to_csv(rows), media_type="text/csv",
                            headers={"Content-Disposition": 'attachment; filename="uk-cf-advisers.csv"'})
        return {"total": len(rows), "offset": offset, "limit": limit,
                "items": [r for r in rows[offset:offset + limit]], "facets": store.facets(rows)}

    @app.get("/v1/advisers/{adviser_id}", tags=["advisers"], dependencies=[Depends(auth)])
    def adviser(adviser_id: str):
        r = store.get(adviser_id)
        if not r:
            raise HTTPException(404, f"no adviser {adviser_id!r}")
        return r

    @app.get("/v1/export.csv", tags=["advisers"], dependencies=[Depends(auth)])
    def export_csv():
        """The whole directory as CSV."""
        return Response(to_csv(store.rows), media_type="text/csv",
                        headers={"Content-Disposition": 'attachment; filename="uk-cf-advisers.csv"'})

    @app.get("/data/advisers.json", include_in_schema=False, dependencies=[Depends(auth)])
    def all_json():
        """What the web page loads: every record, normalised (the static build writes the same file)."""
        return JSONResponse({"meta": meta(), "stats": store.stats(), "items": [r for r in store.rows]})

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(STATIC / "index.html")

    app.mount("/", StaticFiles(directory=STATIC), name="static")
    return app


app = None


def get_app() -> FastAPI:
    global app
    if app is None:
        app = create_app(Path(os.environ.get("CFA_DATA_DIR") or DATA))
    return app

"""Loading, merging and querying the adviser list.

Files (all under data/):
- advisers.jsonl        the master list, one stored record per line (docs/RECORD-FORMAT.md)
- research/*.jsonl      raw research batches; `python -m cfadvisers merge` folds them into advisers.jsonl
- overrides.jsonl       hand corrections {"id": ..., <fields>}; applied on every merge so they survive re-runs
- excluded.txt          ids (one per line, # comments) that must never be in the list
- pitchbook_stats.json  per-adviser deal statistics from a PitchBook export (`python -m cfadvisers pitchbook`)
"""
from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from . import model

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

LIST_FIELDS = ("offices", "regions_covered", "services", "sectors", "sources", "aliases")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise ValueError(f"{path}:{n}: {e}") from None
    return out


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=False) + "\n" for r in rows), encoding="utf-8")
    tmp.replace(path)


STORED_ORDER = [
    "id", "name", "aliases", "website", "firm_type", "parent", "hq", "hq_region", "offices", "coverage",
    "regions_covered", "cf_professionals", "cf_professionals_basis", "deal_ebitda_min_m", "deal_ebitda_max_m",
    "deal_ev_min_m", "deal_ev_max_m", "deal_size_basis", "deal_size_note", "services", "sectors", "sector_note",
    "contact_email", "contact_phone", "team_url", "contact_url", "linkedin_url", "description", "notes",
    "sources", "updated",
]


def stored(rec: dict) -> dict:
    """The stored form of a record: cleaned, id fixed, fields in a stable order, derived fields dropped."""
    r = model.clean(rec)
    r["id"] = rec.get("id") or model.make_id(r)
    return {k: r.get(k) for k in STORED_ORDER if k in r or k in ("id",)}


def _filled(v: Any) -> bool:
    return v not in (None, "", [], {})


def combine(a: dict, b: dict) -> dict:
    """Merge two records of the same firm: scalar fields from the fuller record (falling back to the other),
    list fields unioned. `a` wins ties."""
    score = lambda r: sum(_filled(v) for v in r.values())
    first, second = (a, b) if score(a) >= score(b) else (b, a)
    out = dict(second)
    for k, v in first.items():
        if k in LIST_FIELDS:
            continue
        if _filled(v):
            out[k] = v
    for k in LIST_FIELDS:
        out[k] = list(dict.fromkeys((first.get(k) or []) + (second.get(k) or [])))
    if first.get("name") != second.get("name") and second.get("name"):
        out["aliases"] = list(dict.fromkeys(out["aliases"] + [second["name"]]))
        if out["name"] in out["aliases"]:
            out["aliases"].remove(out["name"])
    return out


def merge(batches: list[list[dict]], existing: list[dict] | None = None, overrides: list[dict] | None = None,
          excluded: set[str] | None = None, today: str | None = None) -> tuple[list[dict], dict]:
    """Fold research batches into the existing list. Records are matched on id (website domain + path)."""
    by_id: dict[str, dict] = {}
    stats = Counter()
    for r in existing or []:
        s = stored(r)
        by_id[s["id"]] = s
    for batch in batches:
        for raw in batch:
            if not raw.get("name") or not raw.get("website"):
                stats["skipped_incomplete"] += 1
                continue
            s = stored(raw)
            if today and not s.get("updated"):
                s["updated"] = today
            if s["id"] in by_id:
                by_id[s["id"]] = stored(combine(by_id[s["id"]], s))
                stats["merged"] += 1
            else:
                by_id[s["id"]] = s
                stats["added"] += 1
    for o in overrides or []:
        oid = o.get("id")
        if oid in by_id:
            by_id[oid] = stored({**by_id[oid], **o})
            stats["overridden"] += 1
        elif oid and o.get("name") and o.get("website"):
            by_id[oid] = stored(o)
            stats["added_by_override"] += 1
    for x in excluded or set():
        if by_id.pop(x, None) is not None:
            stats["excluded"] += 1
    rows = sorted(by_id.values(), key=lambda r: r["name"].lower())
    stats["total"] = len(rows)
    return rows, dict(stats)


def read_excluded(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {ln.split("#")[0].strip() for ln in path.read_text().splitlines() if ln.split("#")[0].strip()}


class Store:
    """The list in memory, normalised, with PitchBook statistics attached when present."""

    def __init__(self, data_dir: Path = DATA, multiple: float | None = None):
        self.data_dir = Path(data_dir)
        self.multiple = multiple
        self.reload()

    def reload(self) -> None:
        self.rows = [model.normalise(r, self.multiple) for r in read_jsonl(self.data_dir / "advisers.jsonl")]
        pb_path = self.data_dir / "pitchbook_stats.json"
        pb = json.loads(pb_path.read_text()) if pb_path.exists() else {}
        for r in self.rows:
            if r["id"] in pb.get("advisers", {}):
                r["pitchbook"] = pb["advisers"][r["id"]]
        self.pitchbook_meta = {k: v for k, v in pb.items() if k != "advisers"}
        self.by_id = {r["id"]: r for r in self.rows}

    def get(self, adviser_id: str) -> dict | None:
        return self.by_id.get(adviser_id)

    def query(self, q: str | None = None, firm_type: list[str] | None = None, region: list[str] | None = None,
              hq_region: list[str] | None = None, sector: list[str] | None = None, service: list[str] | None = None,
              ebitda_min: float | None = None, ebitda_max: float | None = None, include_unknown_size: bool = False,
              sme: bool | None = None, cf_min: int | None = None, cf_max: int | None = None,
              has_email: bool | None = None, has_contact: bool | None = None, coverage: list[str] | None = None,
              sort: str = "name", order: str = "asc") -> list[dict]:
        """Filter the list. Multi-valued filters match any of the given values.
        `region` matches firms whose regions_covered include the region (where they work);
        `hq_region` matches where they are based. `ebitda_min`/`ebitda_max` keep firms whose core
        EBITDA range overlaps [ebitda_min, ebitda_max]; firms with no known range only when
        include_unknown_size. `sme=True` is shorthand for the £0.5m-£2m band."""
        rows = self.rows
        if sme:
            ebitda_min, ebitda_max = model.SME_BAND
        if q:
            terms = q.lower().split()
            def hay(r):
                return " ".join(str(x) for x in [r["name"], " ".join(r.get("aliases") or []), r.get("domain"),
                                                  r.get("hq"), " ".join(r["offices"]), " ".join(r["sectors"]),
                                                  r.get("sector_note"), r.get("description"), r.get("parent")]
                                if x).lower()
            rows = [r for r in rows if all(t in hay(r) for t in terms)]
        if firm_type:
            rows = [r for r in rows if r.get("firm_type") in firm_type]
        if coverage:
            rows = [r for r in rows if r.get("coverage") in coverage]
        if region:
            rows = [r for r in rows if set(region) & set(r["regions_covered"])]
        if hq_region:
            rows = [r for r in rows if r.get("hq_region") in hq_region]
        if sector:
            rows = [r for r in rows if set(sector) & set(r["sectors"])]
        if service:
            rows = [r for r in rows if set(service) & set(r["services"])]
        if ebitda_min is not None or ebitda_max is not None:
            lo = ebitda_min if ebitda_min is not None else 0
            hi = ebitda_max if ebitda_max is not None else float("inf")
            rows = [r for r in rows if (ov := model.overlaps(r["ebitda_min_m"], r["ebitda_max_m"], lo, hi))
                    or (ov is None and include_unknown_size)]
        if cf_min is not None:
            rows = [r for r in rows if r["cf_professionals"] is not None and r["cf_professionals"] >= cf_min]
        if cf_max is not None:
            rows = [r for r in rows if r["cf_professionals"] is not None and r["cf_professionals"] <= cf_max]
        if has_email is not None:
            rows = [r for r in rows if bool(r["contact_email"]) == has_email]
        if has_contact is not None:
            rows = [r for r in rows if bool(r["contact_email"] or r["team_url"] or r["contact_url"]) == has_contact]
        return sort_rows(rows, sort, order)

    def facets(self, rows: list[dict] | None = None) -> dict:
        rows = self.rows if rows is None else rows
        c = lambda key: dict(Counter(x for r in rows for x in (r.get(key) if isinstance(r.get(key), list)
                                                                 else [r.get(key)]) if x).most_common())
        return {"firm_type": c("firm_type"), "hq_region": c("hq_region"), "regions_covered": c("regions_covered"),
                "sectors": c("sectors"), "services": c("services"), "coverage": c("coverage"),
                "covers_sme": dict(Counter(str(r["covers_sme"]).lower() for r in rows))}

    def stats(self) -> dict:
        rows = self.rows
        cf = [r["cf_professionals"] for r in rows if r["cf_professionals"] is not None]
        return {
            "advisers": len(rows),
            "covers_sme": sum(1 for r in rows if r["covers_sme"]),
            "deal_size_unknown": sum(1 for r in rows if r["covers_sme"] is None),
            "with_contact_email": sum(1 for r in rows if r["contact_email"]),
            "with_team_page": sum(1 for r in rows if r["team_url"]),
            "cf_professionals_total": sum(cf),
            "cf_professionals_median": statistics.median(cf) if cf else None,
            "mean_completeness": round(statistics.mean(r["completeness"] for r in rows)) if rows else None,
            "with_pitchbook": sum(1 for r in rows if r.get("pitchbook")),
            "ev_to_ebitda_multiple": self.multiple or model.ev_multiple(),
            "sme_band_ebitda_m": list(model.SME_BAND),
            "pitchbook": self.pitchbook_meta or None,
        }


SORT_KEYS = {
    "name": lambda r: r["name"].lower(),
    "cf_professionals": lambda r: (r["cf_professionals"] is None, r["cf_professionals"] or 0),
    "ebitda_min": lambda r: (r["ebitda_min_m"] is None, r["ebitda_min_m"] or 0),
    "ebitda_max": lambda r: (r["ebitda_max_m"] is None, r["ebitda_max_m"] or 0),
    "hq": lambda r: ((r.get("hq") or "~").lower(), r["name"].lower()),
    "firm_type": lambda r: (r.get("firm_type") or "~", r["name"].lower()),
    "completeness": lambda r: r["completeness"],
    "pitchbook_deals": lambda r: (r.get("pitchbook") or {}).get("deals", 0),
}


def sort_rows(rows: list[dict], sort: str = "name", order: str = "asc") -> list[dict]:
    key = SORT_KEYS.get(sort, SORT_KEYS["name"])
    if order == "desc":
        # keep unknowns last when descending too
        is_unknown = lambda r: isinstance(key(r), tuple) and key(r)[0] is True
        known = [r for r in rows if not is_unknown(r)]
        return sorted(known, key=key, reverse=True) + [r for r in rows if is_unknown(r)]
    return sorted(rows, key=key)

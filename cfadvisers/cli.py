"""Command line.

    python -m cfadvisers serve                       API + web app on http://127.0.0.1:8000/
    python -m cfadvisers find --sme --region "North West" [--csv out.csv]
    python -m cfadvisers stats
    python -m cfadvisers validate
    python -m cfadvisers merge [data/research/*.jsonl]   fold research batches into data/advisers.jsonl
    python -m cfadvisers pitchbook deals.csv          import a PitchBook deal export (see cfadvisers/pitchbook.py)
    python -m cfadvisers check-sites [--fill]         check websites, fill empty contact fields
    python -m cfadvisers build-static [--out site]    static copy of the web app (no server needed)
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

from . import model, store
from .store import DATA, Store, read_jsonl, write_jsonl


def _p(*a):
    print(*a, flush=True)


def cmd_serve(a):
    import uvicorn
    from .api import create_app
    _p(f"http://{a.host}:{a.port}/  (API docs: /v1/docs)")
    uvicorn.run(create_app(Path(a.data)), host=a.host, port=a.port, log_level="info")


def cmd_find(a):
    s = Store(Path(a.data))
    rows = s.query(q=a.q, firm_type=a.firm_type, region=a.region, hq_region=a.hq_region, sector=a.sector,
                   service=a.service, ebitda_min=a.ebitda_min, ebitda_max=a.ebitda_max, sme=a.sme,
                   include_unknown_size=a.include_unknown, cf_min=a.cf_min, cf_max=a.cf_max, sort=a.sort)
    if a.csv:
        from .api import to_csv
        Path(a.csv).write_text(to_csv(rows), encoding="utf-8")
        _p(f"{len(rows)} advisers -> {a.csv}")
        return
    if a.json:
        _p(json.dumps(rows, indent=1, ensure_ascii=False))
        return
    for r in rows:
        size = f"£{r['ebitda_min_m'] if r['ebitda_min_m'] is not None else '?'}-{r['ebitda_max_m'] if r['ebitda_max_m'] is not None else '?'}m EBITDA"
        _p(f"{r['name'][:40]:40}  {(r['firm_type_label'] or '')[:24]:24}  {(r['hq'] or '')[:14]:14}  "
           f"{str(r['cf_professionals'] or ''):>4}  {size:22}  {r['website']}")
    _p(f"-- {len(rows)} advisers")


def cmd_stats(a):
    s = Store(Path(a.data))
    _p(json.dumps(s.stats() | {"facets": s.facets()}, indent=1, ensure_ascii=False))


def cmd_validate(a):
    rows = read_jsonl(Path(a.data) / "advisers.jsonl")
    bad, ids = 0, {}
    for r in rows:
        ps = model.problems(model.clean(r))
        if r.get("id") in ids:
            ps.append(f"duplicate id (also {ids[r['id']]})")
        ids[r.get("id")] = r.get("name")
        if ps:
            bad += 1
            _p(f"{r.get('id')}: {'; '.join(ps)}")
    _p(f"{len(rows)} records, {bad} with problems")
    return 1 if bad else 0


def cmd_merge(a):
    d = Path(a.data)
    files = [Path(f) for f in a.files] if a.files else sorted((d / "research").glob("*.jsonl"))
    batches = [read_jsonl(f) for f in files]
    existing = [] if a.fresh else read_jsonl(d / "advisers.jsonl")
    rows, stats = store.merge(batches, existing, read_jsonl(d / "overrides.jsonl"),
                              store.read_excluded(d / "excluded.txt"), today=date.today().isoformat())
    write_jsonl(d / "advisers.jsonl", rows)
    _p(f"merged {len(files)} files: {stats}")


def cmd_pitchbook(a):
    from . import pitchbook
    s = Store(Path(a.data))
    stats, unmatched = pitchbook.import_export(Path(a.file), s.rows, model.ev_multiple(), a.note or "")
    pitchbook.write_outputs(Path(a.data), stats, unmatched)
    _p(f"{stats['deals']} deals; {len(stats['advisers'])} advisers in the list matched; "
       f"{len(unmatched)} advisers not in the list -> data/pitchbook_unmatched.csv")


def cmd_check_sites(a):
    from . import sitecheck
    d = Path(a.data)
    stored_rows = read_jsonl(d / "advisers.jsonl")
    targets = [r for r in stored_rows if not a.only or r["id"] in a.only]
    _p(f"checking {len(targets)} websites ...")
    checks = sitecheck.run(targets, a.workers)
    prev = {c["id"]: c for c in read_jsonl(d / "site_checks.jsonl")}
    prev.update({c["id"]: c for c in checks})
    write_jsonl(d / "site_checks.jsonl", sorted(prev.values(), key=lambda c: c["id"]))
    down = [c for c in checks if not (c["status"] and 200 <= c["status"] < 400)]
    moved = [c for c in checks if c.get("moved")]
    _p(f"{len(checks) - len(down)} up, {len(down)} down/blocked, {len(moved)} redirect to another domain")
    for c in down:
        _p(f"  down: {c['id']}: {c.get('error')}")
    for c in moved:
        _p(f"  moved: {c['id']} -> {c['final_url']}")
    if a.fill:
        n = sitecheck.fill(stored_rows, checks)
        write_jsonl(d / "advisers.jsonl", stored_rows)
        _p(f"filled {n} empty contact fields")


def cmd_build_static(a):
    """Copy the web app to `out` with the data baked in as data/advisers.json, for any static host."""
    from .api import create_app
    from fastapi.testclient import TestClient
    out = Path(a.out)
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(Path(__file__).parent / "static", out)
    c = TestClient(create_app(Path(a.data)))
    (out / "data").mkdir(exist_ok=True)
    (out / "data" / "advisers.json").write_text(c.get("/data/advisers.json").text, encoding="utf-8")
    (out / "uk-cf-advisers.csv").write_text(c.get("/v1/export.csv").text, encoding="utf-8")
    (out / ".nojekyll").write_text("")
    _p(f"static site -> {out}/ (open index.html via any web server, e.g. python -m http.server -d {out})")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="cfadvisers", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=str(DATA), help="data directory (default: data/)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("serve", help="run the API + web app")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.set_defaults(fn=cmd_serve)

    p = sub.add_parser("find", help="search the list")
    p.add_argument("q", nargs="?")
    p.add_argument("--sme", action="store_true", help=f"core EBITDA range overlaps £{model.SME_BAND[0]}-{model.SME_BAND[1]}m")
    p.add_argument("--ebitda-min", type=float)
    p.add_argument("--ebitda-max", type=float)
    p.add_argument("--include-unknown", action="store_true", help="keep firms of unknown deal size")
    p.add_argument("--firm-type", action="append", choices=list(model.FIRM_TYPES))
    p.add_argument("--region", action="append", choices=model.REGIONS, help="region covered")
    p.add_argument("--hq-region", action="append", choices=model.REGIONS + ["International"])
    p.add_argument("--sector", action="append", choices=model.SECTORS)
    p.add_argument("--service", action="append", choices=list(model.SERVICES))
    p.add_argument("--cf-min", type=int)
    p.add_argument("--cf-max", type=int)
    p.add_argument("--sort", default="name", choices=list(store.SORT_KEYS))
    p.add_argument("--csv", help="write the matches to this CSV file")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_find)

    sub.add_parser("stats", help="counts and coverage").set_defaults(fn=cmd_stats)
    sub.add_parser("validate", help="check data/advisers.jsonl").set_defaults(fn=cmd_validate)

    p = sub.add_parser("merge", help="fold research batches into data/advisers.jsonl")
    p.add_argument("files", nargs="*")
    p.add_argument("--fresh", action="store_true", help="rebuild from the batches only (overrides still apply)")
    p.set_defaults(fn=cmd_merge)

    p = sub.add_parser("pitchbook", help="import a PitchBook deal export (CSV/XLSX)")
    p.add_argument("file")
    p.add_argument("--note", help="what the export covers, e.g. 'UK M&A 2021-2026, deal size < £50m'")
    p.set_defaults(fn=cmd_pitchbook)

    p = sub.add_parser("check-sites", help="check websites; --fill fills empty contact fields")
    p.add_argument("--fill", action="store_true")
    p.add_argument("--only", nargs="*")
    p.add_argument("--workers", type=int, default=8)
    p.set_defaults(fn=cmd_check_sites)

    p = sub.add_parser("build-static", help="static copy of the web app with the data baked in")
    p.add_argument("--out", default="site")
    p.set_defaults(fn=cmd_build_static)

    a = ap.parse_args(argv)
    return a.fn(a) or 0


if __name__ == "__main__":
    sys.exit(main())

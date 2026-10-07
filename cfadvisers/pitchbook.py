"""Import a PitchBook deal export: per-adviser deal counts and sizes, plus advisers missing from the list.

PitchBook captures the advisers on each deal, so an export of UK M&A deals (ask Joel: Deals search, UK,
M&A / buyout / MBO, last 3-5 years, with the "Service Providers" / advisor columns and Deal Size, EBITDA)
tells us who actually advises at the SME end and how often.

Input: CSV or XLSX exported from PitchBook. Column names vary by export template, so they are matched
loosely (see COLUMNS). Advisers are read from any column whose name mentions advisor/adviser/service
provider. Cells look like "Cavendish Corporate Finance (Advisor: General), Shoosmiths (Legal Advisor)";
legal, accounting-DD, PR and similar roles are dropped.

Output:
- data/pitchbook_stats.json: {"source", "imported", "deals", "advisers": {id: {...}}}, attached to records
  as `pitchbook` by the store
- data/pitchbook_unmatched.csv: advisers in the export that are not in the list, by deal count; review
  them and add the real CF advisers to a research batch
"""
from __future__ import annotations

import csv
import io
import json
import re
import statistics
from collections import defaultdict
from datetime import date
from pathlib import Path

from . import model

COLUMNS = {
    "deal_id": ["deal id", "deal_id", "pbid", "deal pbid"],
    "company": ["companies", "company name", "company", "target"],
    "date": ["deal date", "date", "announced date", "completed date"],
    "deal_size": ["deal size", "deal size (gbp, mil)", "deal size (gbp mil)", "deal size (usd, mil)",
                  "enterprise value", "ev", "post valuation"],
    "ebitda": ["ebitda", "ebitda (gbp, mil)", "ebitda (usd, mil)", "company ebitda"],
    "deal_type": ["deal type", "deal type 1", "deal synopsis type"],
}
ADVISER_COL = re.compile(r"advis|service provider", re.I)
DROP_ROLE = re.compile(r"legal|law|accounting|audit|tax|due diligence|insurance|pr\b|public relations|"
                       r"consult|valuation|environmental|commercial|it advisor|actuar|property|real estate", re.I)
SUFFIX = re.compile(r"\b(ltd|limited|llp|plc|inc|group|holdings|uk|the|corporate finance|cf|advisory|advisers|"
                    r"advisors|partners|partnership|capital|m&a|& co|and co|co)\b\.?", re.I)


def norm_name(name: str) -> str:
    n = name.lower().replace("&", " & ")
    n = SUFFIX.sub(" ", n)
    return re.sub(r"[^a-z0-9]+", " ", n).strip()


def read_table(path: Path) -> list[dict]:
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        try:
            import openpyxl
        except ImportError:
            raise SystemExit("reading .xlsx needs openpyxl (pip install openpyxl), or save the export as CSV")
        ws = openpyxl.load_workbook(path, read_only=True, data_only=True).active
        rows = list(ws.iter_rows(values_only=True))
        # PitchBook exports start with a few title rows: the header is the first row naming a deal column
        hi = next((i for i, r in enumerate(rows) if r and any(str(c or "").strip().lower() in
                                                              sum(COLUMNS.values(), []) for c in r)), 0)
        head = [str(c or "").strip() for c in rows[hi]]
        return [dict(zip(head, ["" if c is None else str(c) for c in r])) for r in rows[hi + 1:] if any(r)]
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = text.splitlines()
    hi = next((i for i, ln in enumerate(lines) if any(f'{c}' in ln.lower() for c in ("deal id", "companies",
                                                                                         "deal date"))), 0)
    return list(csv.DictReader(io.StringIO("\n".join(lines[hi:]))))


def _col(head: list[str], key: str) -> str | None:
    low = {h.lower().strip(): h for h in head}
    for alias in COLUMNS[key]:
        if alias in low:
            return low[alias]
    for h in head:
        if any(h.lower().startswith(a) for a in COLUMNS[key]):
            return h
    return None


def parse_advisers(cell: str) -> list[tuple[str, str]]:
    """'A (Advisor: General), B LLP (Legal Advisor)' -> [(name, role)], split on commas outside brackets."""
    out, depth, cur = [], 0, ""
    for ch in cell or "":
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch in ",;" and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    res = []
    for part in out:
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", part)
        name, role = (m.group(1), m.group(2)) if m else (part, "")
        res.append((name.strip(), role.strip()))
    return res


def _money(v: str) -> float | None:
    v = (v or "").replace(",", "").replace("£", "").replace("$", "").strip()
    try:
        return float(v)
    except ValueError:
        return None


def build_index(advisers: list[dict]) -> dict[str, str]:
    idx = {}
    for r in advisers:
        for n in [r["name"], *(r.get("aliases") or [])]:
            k = norm_name(n)
            if k:
                idx.setdefault(k, r["id"])
        if r.get("domain"):
            idx.setdefault(r["domain"].split(".")[0], r["id"])
    return idx


def match(name: str, idx: dict[str, str]) -> str | None:
    k = norm_name(name)
    if k in idx:
        return idx[k]
    # "Grant Thornton UK" vs "Grant Thornton": try dropping trailing words
    words = k.split()
    while len(words) > 1:
        words = words[:-1]
        if " ".join(words) in idx and len(" ".join(words)) >= 5:
            return idx[" ".join(words)]
    return None


def import_export(path: Path, advisers: list[dict], multiple: float, uk_only_note: str = "") -> tuple[dict, list[dict]]:
    rows = read_table(path)
    if not rows:
        raise SystemExit(f"{path}: no rows")
    head = list(rows[0].keys())
    cols = {k: _col(head, k) for k in COLUMNS}
    adv_cols = [h for h in head if ADVISER_COL.search(h or "")]
    if not adv_cols:
        raise SystemExit(f"{path}: no adviser / service provider column among {head}")
    idx = build_index(advisers)
    per: dict[str, list[dict]] = defaultdict(list)
    unmatched: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        deal = {
            "deal_id": row.get(cols["deal_id"]) if cols["deal_id"] else None,
            "company": row.get(cols["company"]) if cols["company"] else None,
            "date": (row.get(cols["date"]) or "")[:10] if cols["date"] else None,
            "deal_size_m": _money(row.get(cols["deal_size"])) if cols["deal_size"] else None,
            "ebitda_m": _money(row.get(cols["ebitda"])) if cols["ebitda"] else None,
            "deal_type": row.get(cols["deal_type"]) if cols["deal_type"] else None,
        }
        seen = set()
        for c in adv_cols:
            for name, role in parse_advisers(row.get(c) or ""):
                if DROP_ROLE.search(role) or DROP_ROLE.search(c if "legal" in c.lower() else ""):
                    continue
                aid = match(name, idx)
                key = aid or norm_name(name)
                if key in seen:
                    continue
                seen.add(key)
                (per[aid] if aid else unmatched[name]).append(deal)
    lo, hi = model.SME_BAND
    out = {}
    for aid, deals in per.items():
        ebitda = [d["ebitda_m"] for d in deals if d["ebitda_m"] is not None]
        ev = [d["deal_size_m"] for d in deals if d["deal_size_m"] is not None]
        implied = [d["ebitda_m"] if d["ebitda_m"] is not None else (d["deal_size_m"] / multiple if d["deal_size_m"]
                   is not None else None) for d in deals]
        implied = [x for x in implied if x is not None]
        out[aid] = {
            "deals": len(deals),
            "deals_with_size": len(implied),
            "deals_in_sme_band": sum(1 for x in implied if lo <= x <= hi),
            "median_deal_size_m": round(statistics.median(ev), 2) if ev else None,
            "median_ebitda_m": round(statistics.median(ebitda), 2) if ebitda else None,
            "last_deal": max((d["date"] for d in deals if d["date"]), default=None),
            "recent": sorted(deals, key=lambda d: d["date"] or "", reverse=True)[:5],
        }
    stats = {"source": path.name, "imported": date.today().isoformat(), "deals": len(rows),
             "note": uk_only_note or None, "advisers": out}
    um = sorted(({"name": n, "deals": len(d), "last_deal": max((x["date"] for x in d if x["date"]), default=""),
                  "example": d[0].get("company")} for n, d in unmatched.items()), key=lambda x: -x["deals"])
    return stats, um


def write_outputs(data_dir: Path, stats: dict, unmatched: list[dict]) -> None:
    (data_dir / "pitchbook_stats.json").write_text(json.dumps(stats, indent=1, ensure_ascii=False))
    with open(data_dir / "pitchbook_unmatched.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", "deals", "last_deal", "example"])
        w.writeheader()
        w.writerows(unmatched)

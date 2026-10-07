"""Match the adviser list against the Companies House bulk register, and list CF-looking companies we lack.

Input: BasicCompanyDataAsOneFile-YYYY-MM-DD.zip from https://download.companieshouse.gov.uk/en_output.html
(free, Open Government Licence, monthly, ~470 MB; download it to a scratch directory, not into the repo).

    python tools/ch_bulk.py /path/to/BasicCompanyDataAsOneFile-2026-10-01.zip

Run `python -m cfadvisers check-sites` first: company numbers stated on the firms' own sites are the best match.

Writes (all small, safe to commit):
  data/companies_house/resolved.jsonl         one entity per firm where the match is firm (see resolve()). The web
                                              app and API attach it to the record as `companies_house`.
  data/companies_house/bulk_matches.jsonl     our firms whose name or alias equals a CH company name, current or
                                              previous, after normalising (case, punctuation, "&", Ltd/LLP/plc).
                                              Exact only: no fuzzy matching. `n_same_name` > 1 means ambiguous.
  data/companies_house/bulk_candidates.jsonl  active, non-dormant companies whose name says corporate finance /
                                              M&A and that match no firm in the list. Leads only: a research
                                              agent must find a website and evidence of deals before adding one.
"""
from __future__ import annotations

import csv
import io
import json
import re
import sys
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "companies_house"

SUFFIX = re.compile(r"\b(LIMITED|LTD|LLP|PLC|L\.L\.P|CO|COMPANY|UK|GROUP|HOLDINGS|THE)\b")
# name terms that mark a company as a likely CF / M&A adviser (matched on the normalised name)
TERMS = re.compile(r"\b(CORPORATE FINANCE|CORPORATE ADVISORY|CORPORATE ADVISERS|CORPORATE ADVISORS|M AND A|M A ADVIS"
                   r"|MERGERS|ACQUISITIONS|TRANSACTION ADVISORY|TRANSACTION SERVICES|DEAL ADVISORY|BUSINESS SALES"
                   r"|BUSINESS TRANSFER|BUSINESS BROKER|EXIT PLANNING|CAPITAL ADVISORY|CAPITAL ADVISERS|CAPITAL ADVISORS"
                   r"|CF PARTNERS)\b")


def norm(name: str) -> str:
    s = name.upper().replace("&", " AND ").replace("+", " AND ")
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    s = SUFFIX.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def ddmmyyyy(s: str):
    return f"{s[6:10]}-{s[3:5]}-{s[0:2]}" if len(s) == 10 else None


def main(zip_path: str) -> int:
    firms = [json.loads(line) for line in open(ROOT / "data" / "advisers.jsonl", encoding="utf-8")]
    keys: dict[str, set[str]] = {}
    for f in firms:
        for n in [f["name"], *(f.get("aliases") or [])]:
            k = norm(n)
            if len(k) >= 3:
                keys.setdefault(k, set()).add(f["id"])

    # Companies House numbers the firms state on their own websites (python -m cfadvisers check-sites)
    site_nums: dict[str, set[str]] = {}
    checks = ROOT / "data" / "site_checks.jsonl"
    for c in (json.loads(line) for line in open(checks, encoding="utf-8")) if checks.exists() else ():
        for n in (c.get("company_numbers") or []) if any(f["id"] == c["id"] for f in firms) else []:
            site_nums.setdefault(n, set()).add(c["id"])

    z = zipfile.ZipFile(zip_path)
    snapshot = re.search(r"(\d{4}-\d{2}-\d{2})", z.namelist()[0]).group(1)
    rows = csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8", newline=""))
    h = {c.strip(): i for i, c in enumerate(next(rows))}
    matches, cands, by_key_count = [], [], {}
    for r in rows:
        if len(r) < len(h):  # trailer / malformed line
            continue
        g = lambda c: r[h[c]].strip()
        names = [(g("CompanyName"), None)] + [(g(f"PreviousName_{i}.CompanyName"), ddmmyyyy(g(f"PreviousName_{i}.CONDATE")))
                                              for i in range(1, 11) if g(f"PreviousName_{i}.CompanyName")]
        rec = None
        def record():
            return {"company_number": g("CompanyNumber"), "company_name": g("CompanyName"),
                    "company_type": g("CompanyCategory"), "status": g("CompanyStatus"),
                    "incorporated": ddmmyyyy(g("IncorporationDate")), "dissolved": ddmmyyyy(g("DissolutionDate")),
                    "sic_codes": [g(f"SICCode.SicText_{i}") for i in range(1, 5) if g(f"SICCode.SicText_{i}")],
                    "post_town": g("RegAddress.PostTown"), "postcode": g("RegAddress.PostCode"),
                    "accounts_category": g("Accounts.AccountCategory"),
                    "accounts_made_up_to": ddmmyyyy(g("Accounts.LastMadeUpDate")),
                    "previous_names": [{"name": n, "until": d} for n, d in names[1:]],
                    "source": f"Companies House bulk company data {snapshot}"}
        hit = False
        for fid in site_nums.get(g("CompanyNumber"), ()):
            rec = rec or record()
            matches.append({"id": fid, **rec, "matched_on": "website", "matched_name": g("CompanyName")})
            hit = True
        for i, (n, until) in enumerate(names):
            k = norm(n)
            if k in keys:
                rec = rec or record()
                for fid in keys[k]:
                    matches.append({"id": fid, **rec, "matched_on": "previous_name" if i else "name", "matched_name": n})
                    by_key_count[(fid, k)] = by_key_count.get((fid, k), 0) + 1
                hit = True
        if hit or g("CompanyStatus") != "Active" or g("Accounts.AccountCategory") == "DORMANT":
            continue
        if TERMS.search(norm(g("CompanyName"))):
            cands.append(record())

    for m in matches:
        m["n_same_name"] = by_key_count.get((m["id"], norm(m["matched_name"])), 1)
    # one firm may match several entities (old + new LLP, dissolved shells): keep them all, active first
    matches.sort(key=lambda m: (m["id"], m["status"] != "Active", m["matched_on"] != "name", m["company_number"]))
    cands.sort(key=lambda c: (c["post_town"], c["company_name"]))
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in (("bulk_matches.jsonl", matches), ("bulk_candidates.jsonl", cands)):
        with open(OUT / name, "w", encoding="utf-8") as fh:
            fh.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in data)
    resolved = resolve(firms, matches)
    with open(OUT / "resolved.jsonl", "w", encoding="utf-8") as fh:
        fh.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in resolved)
    print(f"resolved {len(resolved)} firms to one entity: "
          + ", ".join(f"{k} {v}" for k, v in Counter(x["match"] for x in resolved).items()))
    matched = {m["id"] for m in matches}
    print(f"snapshot {snapshot}: {len(matched)}/{len(firms)} firms matched ({len(matches)} entity rows); "
          f"{len(cands)} candidate companies -> {OUT.relative_to(ROOT)}/  (run {date.today()})")
    return 0


GENERIC = {"AND", "CORPORATE", "FINANCE", "PARTNERS", "CAPITAL", "ADVISORY", "ADVISERS", "ADVISORS", "SERVICES",
           "ACCOUNTANTS", "ASSOCIATES", "CONSULTING", "MANAGEMENT", "SOLUTIONS", "INTERNATIONAL"}


def same_firm(f: dict, m: dict) -> bool:
    """A site may quote someone else's number (company secretary, web designer, a client). Accept a website
    number only if the registered name (or a previous one) shares a distinctive word or the initials with the
    firm's name, an alias or its domain."""
    ours = [norm(n) for n in [f["name"], *(f.get("aliases") or [])]]
    ours.append(norm(re.sub(r"^https?://(www\.)?", "", f["website"]).split(".")[0].replace("-", " ")))
    words = {w for n in ours for w in n.split()} - GENERIC
    for n in [m["company_name"], *(p["name"] for p in m["previous_names"])]:
        theirs = norm(n).split()
        initials = "".join(w[0] for w in theirs if w != "AND")
        if (set(theirs) - GENERIC) & words or (len(initials) >= 2 and initials in words | set(ours)):
            return True
    return False


def resolve(firms: list[dict], matches: list[dict]) -> list[dict]:
    """One entity per firm, only where the evidence is firm: (1) a number the firm's own site states, found in
    the register (an active one preferred); else (2) the only active company with exactly the firm's name, whose
    registered post town is the firm's HQ town. Everything else stays unresolved in bulk_matches.jsonl."""
    hq = {f["id"]: (f.get("hq") or "").split(",")[0].strip().upper() for f in firms}
    firm = {f["id"]: f for f in firms}
    by: dict[str, list[dict]] = {}
    for m in matches:
        by.setdefault(m["id"], []).append(m)
    out = []
    for fid, ms in sorted(by.items()):
        web = sorted((m for m in ms if m["matched_on"] == "website" and same_firm(firm[fid], m)),
                     key=lambda m: m["status"] != "Active")
        named = [m for m in ms if m["matched_on"] == "name" and m["status"] == "Active"]
        if web:
            best, how = web[0], "website"
        elif len(named) == 1 and hq[fid] and hq[fid] == named[0]["post_town"].upper():
            best, how = named[0], "name+town"
        else:
            continue
        keep = ("company_number", "company_name", "company_type", "status", "incorporated", "dissolved", "sic_codes",
                "post_town", "postcode", "accounts_category", "accounts_made_up_to", "previous_names", "source")
        out.append({"id": fid, **{k: best[k] for k in keep}, "match": how})
    return out


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))

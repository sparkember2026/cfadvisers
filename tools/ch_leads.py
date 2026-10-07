"""Find websites for Companies House leads by guessing domains from the company name, then prove them.

    python tools/ch_leads.py [--limit N] [--workers 32]

Input:  data/companies_house/bulk_candidates.jsonl (from tools/ch_bulk.py), filtered to likely advisers
        (strong CF/M&A name terms, or an advisory SIC code; property, construction and trading SICs dropped).
Output: data/companies_house/lead_sites.jsonl, one line per lead with a site that is PROVEN to be the company's
        (the site prints its company number, or its registered name), with an M&A wording score and the pages read.
        Leads only: an agent or a person still checks that the firm advises on deals before it joins the list.
No model calls and no web searches: plain HTTPS fetches (a non-existent domain fails in ~0.4 s through the proxy).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from cfadvisers import model, sitecheck  # noqa: E402
from ch_bulk import norm  # noqa: E402

STRONG = re.compile(r"\b(CORPORATE FINANCE|CORPORATE ADVIS\w*|TRANSACTION (ADVISORY|SERVICES)|DEAL ADVISORY|M AND A ADVIS\w*"
                    r"|M A ADVIS\w*|MERGERS AND ACQUISITIONS|MERGERS|BUSINESS (SALES|BROKER\w*|TRANSFER\w*)|EXIT PLANNING"
                    r"|CAPITAL ADVIS\w*|CF PARTNERS)\b")
ADVISORY_SIC = {"70229", "70221", "64999", "66190", "66120", "69201", "69202", "82990", "74909", "66300", "70210"}
NOT_ADVISORY_SIC_PREFIX = {"68", "41", "43", "55", "56", "47", "45", "10", "49", "86", "87", "88"}
GENERIC = {"CORPORATE", "FINANCE", "CAPITAL", "ADVISORS", "ADVISERS", "ADVISORY", "PARTNERS", "TRANSACTION",
           "SERVICES", "MERGERS", "ACQUISITIONS", "AND", "M", "A", "BUSINESS", "SALES", "TRANSFER", "TRANSFERS",
           "BROKERS", "BROKER", "DEAL", "EXIT", "PLANNING", "CF", "EUROPE", "INTERNATIONAL", "GLOBAL", "LONDON"}
MA_WORDS = re.compile(r"corporate finance|mergers|acquisitions|\bM&amp;A\b|\bM&A\b|sell(ing)? your business|business sale|"
                      r"exit|management buy|MBO|MBI|due diligence|deal|transaction|fundrais|private equity|valuation", re.I)
PARKED = re.compile(r"domain (is )?for sale|buy this domain|parked|godaddy|sedo|this domain|coming soon|under construction|"
                    r"account suspended|default web site page|welcome to nginx", re.I)


def likely_adviser(c: dict) -> bool:
    n = norm(c["company_name"])
    sics = {s.split(" ")[0] for s in c["sic_codes"]}
    strong, adv = bool(STRONG.search(n)), bool(sics & ADVISORY_SIC)
    bad = any(s[:2] in NOT_ADVISORY_SIC_PREFIX for s in sics)
    return (strong and (adv or not bad)) or (adv and not bad and bool(re.search(r"\b(ACQUISITIONS|M AND A)\b", n)))


def guesses(name: str) -> list[str]:
    words = norm(name).lower().split()
    own = [w for w in words if w.upper() not in GENERIC]
    stems = [
        "".join(words), "-".join(words),
        "".join(own), "-".join(own),
        "".join(own) + "cf", "".join(own) + "capital", "".join(own) + "advisory", "".join(own) + "partners",
        "".join(own) + "corporatefinance", "".join(own) + "-cf",
    ]
    stems = [s for s in dict.fromkeys(stems) if len(s.replace("-", "")) >= 4]
    out = []
    for i, s in enumerate(stems):
        out += [f"{s}.co.uk", f"{s}.com"] + ([f"{s}.uk"] if i < 4 else [])
    return list(dict.fromkeys(out))


def text_of(html: str) -> str:
    return " ".join(sitecheck.TAGS.sub(" ", html).replace("&amp;", "&").split())


def probe(c: dict, known_domains: set[str]) -> dict | None:
    core = " ".join(w for w in norm(c["company_name"]).split())
    for d in guesses(c["company_name"]):
        if d in known_domains:
            continue
        status, final, html = sitecheck.fetch("https://" + d, timeout=10)
        if not (status and 200 <= status < 400 and html) or PARKED.search(html[:20000]) and len(html) < 20000:
            continue
        chk = sitecheck.check({"id": c["company_number"], "website": final})
        nums = set(chk.get("company_numbers") or [])
        txt = norm(text_of(html))
        proof = "company_number" if c["company_number"] in nums else "registered_name" if core and core in txt else None
        if not proof:
            continue
        return {"company_number": c["company_number"], "company_name": c["company_name"], "post_town": c["post_town"],
                "incorporated": c["incorporated"], "accounts_category": c["accounts_category"], "sic_codes": c["sic_codes"],
                "website": final, "domain": model.domain_of(final), "proof": proof,
                "ma_score": len(MA_WORDS.findall(text_of(html))), "title": (re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
                                                                          or [None, ""])[1].strip()[:120],
                "team_url": chk.get("team_url"), "contact_url": chk.get("contact_url"), "best_email": chk.get("best_email"),
                "other_numbers": sorted(nums - {c["company_number"]})}
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=32)
    a = ap.parse_args()
    cands = [json.loads(line) for line in open(ROOT / "data/companies_house/bulk_candidates.jsonl", encoding="utf-8")]
    leads = [c for c in cands if likely_adviser(c)][: a.limit]
    known = {model.domain_of(json.loads(line)["website"]) for line in open(ROOT / "data/advisers.jsonl", encoding="utf-8")}
    print(f"{len(leads)} likely-adviser leads of {len(cands)}; probing ...", flush=True)
    with ThreadPoolExecutor(a.workers) as ex:
        found = [r for r in ex.map(lambda c: probe(c, known), leads) if r]
    found.sort(key=lambda r: -r["ma_score"])
    with open(ROOT / "data/companies_house/lead_sites.jsonl", "w", encoding="utf-8") as fh:
        fh.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in found)
    print(f"{len(found)} proven sites ({sum(r['proof'] == 'company_number' for r in found)} by company number); "
          f"{sum(r['ma_score'] >= 5 for r in found)} with strong M&A wording -> data/companies_house/lead_sites.jsonl")
    return 0


if __name__ == "__main__":
    sys.exit(main())

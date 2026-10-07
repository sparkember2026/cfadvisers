"""The adviser record: vocabularies, normalisation and the derived fields every view shares.

docs/RECORD-FORMAT.md describes the stored fields. Derived fields (added by `normalise`, never stored):
- `id`: slug from the website domain (stable across renames of the display name)
- `ebitda_min_m` / `ebitda_max_m`: the core deal range on an EBITDA basis; when the firm only gives EV
  it is EV / EV_TO_EBITDA (the multiple is a setting, default 5x, see `ev_multiple()`)
- `covers_sme`: the EBITDA range overlaps the SME band (£0.5m-£2m by default)
- `completeness`: share of the key fields that are filled, 0-100
"""
from __future__ import annotations

import os
import re
from urllib.parse import urlparse

REGIONS = [
    "London", "South East", "South West", "East of England", "East Midlands", "West Midlands",
    "Yorkshire and the Humber", "North West", "North East", "Scotland", "Wales", "Northern Ireland",
]
FIRM_TYPES = {
    "independent_boutique": "Independent boutique",
    "sector_specialist": "Sector specialist",
    "accountancy_cf": "Accountancy firm CF team",
    "big4": "Big 4",
    "investment_bank": "Investment bank / broker",
    "business_broker": "Business broker",
    "debt_advisory": "Debt adviser",
    "law_firm": "Law firm CF arm",
}
SERVICES = {
    "sell_side": "Sell-side M&A", "buy_side": "Buy-side / acquisitions", "mbo": "MBO / MBI",
    "fundraising": "Equity fundraising", "debt_advisory": "Debt advisory", "due_diligence": "Due diligence",
    "valuations": "Valuations", "ecm": "Equity capital markets", "restructuring": "Restructuring",
}
SECTORS = [
    "Business Services", "Technology & Software", "Healthcare", "Life Sciences", "Consumer & Retail",
    "Food & Beverage", "Leisure & Hospitality", "Industrials & Manufacturing", "Engineering",
    "Construction & Property", "Financial Services", "Professional Services", "Media & Marketing",
    "Education", "Energy & Renewables", "Transport & Logistics", "Automotive", "Agriculture",
    "Recruitment & Staffing", "Care", "Dental & Veterinary", "Pharmacy", "Telecoms", "Facilities Management",
    "Environmental Services", "Distribution & Wholesale", "Charity & Public Sector", "Generalist",
]
COVERAGE = ["national", "regional", "local", "international"]
BASES = ["stated", "team_page", "deals", "estimate"]

SME_BAND = (0.5, 2.0)          # £m EBITDA: the SME end of the market the directory is built around
KEY_FIELDS = [
    "website", "firm_type", "hq", "offices", "coverage", "cf_professionals", "deal_range", "sectors",
    "contact", "description",
]

_SECTOR_ALIASES = {s.lower(): s for s in SECTORS}
_SECTOR_ALIASES.update({
    "technology": "Technology & Software", "tech": "Technology & Software", "software": "Technology & Software",
    "it services": "Technology & Software", "tmt": "Technology & Software",
    "healthcare & life sciences": "Healthcare", "health": "Healthcare", "consumer": "Consumer & Retail",
    "retail": "Consumer & Retail", "food & drink": "Food & Beverage", "food": "Food & Beverage",
    "leisure": "Leisure & Hospitality", "hospitality": "Leisure & Hospitality",
    "manufacturing": "Industrials & Manufacturing", "industrials": "Industrials & Manufacturing",
    "industrial": "Industrials & Manufacturing", "construction": "Construction & Property",
    "property": "Construction & Property", "real estate": "Construction & Property",
    "financial": "Financial Services", "fintech": "Financial Services", "media": "Media & Marketing",
    "marketing": "Media & Marketing", "energy": "Energy & Renewables", "renewables": "Energy & Renewables",
    "logistics": "Transport & Logistics", "transport": "Transport & Logistics", "recruitment": "Recruitment & Staffing",
    "staffing": "Recruitment & Staffing", "dental": "Dental & Veterinary", "veterinary": "Dental & Veterinary",
    "environmental": "Environmental Services", "distribution": "Distribution & Wholesale",
    "wholesale": "Distribution & Wholesale", "public sector": "Charity & Public Sector",
})


def ev_multiple() -> float:
    """EV / EBITDA multiple used to put EV-only deal sizes on an EBITDA basis (env CFA_EV_MULTIPLE)."""
    try:
        return float(os.environ.get("CFA_EV_MULTIPLE", "5"))
    except ValueError:
        return 5.0


def domain_of(url: str | None) -> str:
    if not url:
        return ""
    if "://" not in url:
        url = "https://" + url
    host = (urlparse(url).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


_PATH_NOISE = {"uk", "gb", "en", "en-gb", "en-uk", "home", "index", "default", "www"}


def make_id(rec: dict) -> str:
    d = domain_of(rec.get("website"))
    w = rec.get("website") or ""
    path = urlparse(w if "://" in w else "https://" + w).path
    # several firms share a domain (e.g. a network's member pages): keep the meaningful part of the path
    # to tell them apart, without locale / index noise ("/uk/en/home.html" -> "")
    segs = [re.sub(r"\.s?html?$", "", x) for x in path.lower().split("/")]
    segs = [x for x in segs if x and x not in _PATH_NOISE]
    return slug(" ".join([d] + segs)) or slug(rec.get("name", ""))


def _num(v):
    if v is None or v == "":
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return int(f) if f.is_integer() else f


def _sector(s: str) -> str | None:
    return _SECTOR_ALIASES.get(s.strip().lower()) if isinstance(s, str) else None


def clean(rec: dict) -> dict:
    """Tidy a raw (research or hand-edited) record into the stored form. Idempotent."""
    r = dict(rec)
    r["name"] = (r.get("name") or "").strip()
    w = (r.get("website") or "").strip()
    if w and "://" not in w:
        w = "https://" + w
    r["website"] = w.rstrip("/") if w.count("/") <= 3 else w
    for k in ("offices", "regions_covered", "services", "sectors", "sources", "aliases"):
        v = r.get(k)
        if v is None:
            r[k] = []
        elif isinstance(v, str):
            r[k] = [x.strip() for x in v.split(";") if x.strip()]
    sectors = []
    for s in r["sectors"]:
        m = _sector(s)
        if m and m not in sectors:
            sectors.append(m)
    r["sectors"] = sectors
    r["regions_covered"] = [x for x in dict.fromkeys(r["regions_covered"]) if x in REGIONS]
    seen = set()
    sources = []
    for s in r["sources"]:
        key = s.strip().rstrip("/").lower()
        if s.strip() and key not in seen:
            seen.add(key)
            sources.append(s.strip())
    r["sources"] = sources
    r["services"] = [x for x in dict.fromkeys(r["services"]) if x in SERVICES]
    r["offices"] = list(dict.fromkeys(o.strip() for o in r["offices"] if o and o.strip()))
    for k in ("cf_professionals", "deal_ebitda_min_m", "deal_ebitda_max_m", "deal_ev_min_m", "deal_ev_max_m"):
        r[k] = _num(r.get(k))
    if isinstance(r.get("cf_professionals"), float):
        r["cf_professionals"] = round(r["cf_professionals"])
    for lo, hi in (("deal_ebitda_min_m", "deal_ebitda_max_m"), ("deal_ev_min_m", "deal_ev_max_m")):
        if r[lo] is not None and r[hi] is not None and r[lo] > r[hi]:
            r[lo], r[hi] = r[hi], r[lo]
    if r.get("coverage") not in COVERAGE:
        r["coverage"] = None
    if r.get("hq_region") not in REGIONS + ["International"]:
        r["hq_region"] = None
    for k in ("cf_professionals_basis", "deal_size_basis"):
        if r.get(k) not in BASES:
            r[k] = None
    if r["coverage"] == "national" and not r["regions_covered"]:
        r["regions_covered"] = list(REGIONS)
    if r.get("hq_region") in REGIONS and r["hq_region"] not in r["regions_covered"]:
        r["regions_covered"].insert(0, r["hq_region"])
    for k in ("contact_email", "contact_phone", "team_url", "contact_url", "linkedin_url", "parent",
              "deal_size_note", "sector_note", "hq", "description", "notes"):
        v = r.get(k)
        r[k] = v.strip() if isinstance(v, str) and v.strip() else None
    if r.get("contact_email"):
        r["contact_email"] = r["contact_email"].removeprefix("mailto:").lower()
    return r


def ebitda_range(r: dict, multiple: float | None = None) -> tuple[float | None, float | None]:
    """Core deal range in £m EBITDA: stated EBITDA if given, else EV / multiple."""
    m = multiple or ev_multiple()
    lo, hi = r.get("deal_ebitda_min_m"), r.get("deal_ebitda_max_m")
    if lo is None and r.get("deal_ev_min_m") is not None:
        lo = round(r["deal_ev_min_m"] / m, 2)
    if hi is None and r.get("deal_ev_max_m") is not None:
        hi = round(r["deal_ev_max_m"] / m, 2)
    return lo, hi


def overlaps(lo: float | None, hi: float | None, band_lo: float, band_hi: float) -> bool | None:
    """Does [lo, hi] overlap [band_lo, band_hi]? None when the range is unknown. An open end is open."""
    if lo is None and hi is None:
        return None
    return (lo is None or lo <= band_hi) and (hi is None or hi >= band_lo)


def normalise(rec: dict, multiple: float | None = None) -> dict:
    r = clean(rec)
    r["id"] = rec.get("id") or make_id(r)
    r["domain"] = domain_of(r.get("website"))
    r["ebitda_min_m"], r["ebitda_max_m"] = ebitda_range(r, multiple)
    r["covers_sme"] = overlaps(r["ebitda_min_m"], r["ebitda_max_m"], *SME_BAND)
    r["firm_type_label"] = FIRM_TYPES.get(r.get("firm_type"), r.get("firm_type"))
    filled = {
        "website": bool(r["website"]), "firm_type": r.get("firm_type") in FIRM_TYPES, "hq": bool(r["hq"]),
        "offices": bool(r["offices"]), "coverage": bool(r["coverage"]),
        "cf_professionals": r["cf_professionals"] is not None,
        "deal_range": r["ebitda_min_m"] is not None or r["ebitda_max_m"] is not None,
        "sectors": bool(r["sectors"]),
        "contact": bool(r["contact_email"] or r["team_url"] or r["contact_url"] or r["contact_phone"]),
        "description": bool(r["description"]),
    }
    r["completeness"] = round(100 * sum(filled.values()) / len(KEY_FIELDS))
    r["missing"] = [k for k, v in filled.items() if not v]
    return r


def problems(r: dict) -> list[str]:
    """What is wrong with a stored record (for `validate`)."""
    out = []
    if not r.get("name"):
        out.append("no name")
    if not r.get("website", "").startswith(("http://", "https://")):
        out.append("website is not a URL")
    if r.get("firm_type") not in FIRM_TYPES:
        out.append(f"firm_type {r.get('firm_type')!r} not in {sorted(FIRM_TYPES)}")
    if not r.get("sources"):
        out.append("no sources")
    e = r.get("contact_email")
    if e and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", e):
        out.append(f"contact_email {e!r} does not look like an email")
    return out

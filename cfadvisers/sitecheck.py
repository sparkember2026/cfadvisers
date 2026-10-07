"""Check each adviser's website: is it up, where does it redirect, and which team / contact pages,
emails and phone numbers does the homepage show, plus any Companies House number the site states (homepage, else the contact or privacy/terms page). Fills only empty fields; never overwrites research.

    python -m cfadvisers check-sites [--fill] [--only ID ...] [--workers 8]

Writes data/site_checks.jsonl (one line per adviser, latest run). With --fill, empty contact_email,
contact_phone, team_url and contact_url in data/advisers.jsonl are filled from the check. `merge` applies the
same fill from data/site_checks.jsonl after every merge, so the fills survive `merge --fresh`.
"""
from __future__ import annotations

import re
import ssl
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

from . import model

UA = "Mozilla/5.0 (compatible; cfadvisers-sitecheck/1.0; +https://github.com/sparkember2026/cfadvisers)"
TEAM = re.compile(r"\b(our[- ]?team|the[- ]?team|team|people|our[- ]?people|partners|meet[- ]?the|who[- ]?we[- ]?are|"
                  r"leadership|corporate[- ]?finance[- ]?team)\b", re.I)
CONTACT = re.compile(r"\bcontact", re.I)
LEGAL = re.compile(r"privacy|terms|legal|disclaimer|regulatory|cookie|imprint|complaints", re.I)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SKIP_EMAIL = re.compile(r"(example|sentry|wixpress|domain\.com|\.png|\.jpg|\.gif|\.webp|u003e)", re.I)
# "Registered in England No. 08123456", "Company number SC123456", "Partnership No: OC301234"
CO_NUMBER = re.compile(r"(?:compan(?:y|ies)(?:\s*house)?(?:\s*registration)?|registered(?:\s*in\s*(?:england|wales|scotland|"
                       r"northern\s*ireland)(?:\s*(?:and|&amp;|&)\s*wales)?)?|partnership|llp)\s*,?\s*"
                       r"(?:no\.?|number|num\.?|nr\.?)?\s*(?:is\s*)?[:#.]?\s*((?:SC|NI|OC|SO|NC|R0|FC)?\s?\d{5,8})\b", re.I)
OTHER_REGISTER = re.compile(r"(VAT|FCA|FRN|GPhC|charity|ICAEW|ACCA|CIMA|SRA|data protection|ICO)\W*(\w+\W+){0,3}$", re.I)
TAGS = re.compile(r"<(script|style)\b.*?</\1>|<[^>]+>", re.I | re.S)
PREFERRED_EMAIL = re.compile(r"^(cf|corporatefinance|corporate\.finance|deals|ma|m&a|enquiries|enquiry|info|hello|"
                             r"contact|office|mail|advice|london|admin)@", re.I)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href = None
        self._text = ""

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = ""

    def handle_data(self, data):
        if self._href is not None:
            self._text += data

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join(self._text.split())))
            self._href = None


def fetch(url: str, timeout: float = 20) -> tuple[int, str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            body = resp.read(2_000_000).decode(resp.headers.get_content_charset() or "utf-8", "replace")
            return resp.status, resp.geturl(), body
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception as e:  # network errors, TLS, timeouts: reported, not raised
        return 0, url, f"error: {type(e).__name__}: {e}"[:300]


def root_domain(host: str) -> str:
    """Registrable part of a host: last two labels, three under second-level suffixes like .co.uk."""
    parts = host.lower().strip(".").split(".")
    n = 3 if len(parts) >= 3 and parts[-2] in ("co", "org", "ac", "gov", "ltd", "plc", "me", "net", "com") else 2
    return ".".join(parts[-n:])


def analyse(base: str, html: str) -> dict:
    p = Links()
    try:
        p.feed(html)
    except Exception:
        pass
    host = model.domain_of(base)
    team = contact = legal = None
    phones, emails = [], []
    for href, text in p.links:
        if not href:
            continue
        if href.startswith("mailto:"):
            emails.append(href[7:].split("?")[0].strip())
            continue
        if href.startswith("tel:"):
            phones.append(href[4:].strip())
            continue
        url = urljoin(base, href)
        if model.domain_of(url) != host or urlparse(url).scheme not in ("http", "https"):
            continue
        path = urlparse(url).path
        if not team and (TEAM.search(text) or TEAM.search(path.replace("/", " "))):
            team = url.split("#")[0]
        if not contact and (CONTACT.search(text) or CONTACT.search(path)):
            contact = url.split("#")[0]
        if not legal and (LEGAL.search(text) or LEGAL.search(path)):
            legal = url.split("#")[0]
    emails += EMAIL.findall(html)
    emails = [e.lower() for e in dict.fromkeys(emails) if EMAIL.fullmatch(e) and not SKIP_EMAIL.search(e)]
    own = [e for e in emails if root_domain(e.split("@")[1]) == root_domain(host)]
    best = next((e for e in own if PREFERRED_EMAIL.match(e)), own[0] if own else None)
    return {"team_url": team, "contact_url": contact, "emails": own[:10], "best_email": best,
            "phone": phones[0] if phones else None, "company_numbers": company_numbers(html), "legal_url": legal}


def company_numbers(html: str) -> list[str]:
    """Companies House numbers the page states about its owner, normalised to 8 characters (08123456, SC123456)."""
    text = " ".join(TAGS.sub(" ", html).replace("&nbsp;", " ").split())
    out = []
    for m in CO_NUMBER.finditer(text):
        if OTHER_REGISTER.search(text[max(0, m.start() - 40):m.start(1)]):
            continue
        raw = m.group(1).replace(" ", "").upper()
        pre = raw[:2] if raw[:2].isalpha() else ""
        digits = raw[len(pre):]
        if pre and len(digits) == 6 or not pre and len(digits) >= 6:
            out.append(pre + digits.zfill(8 - len(pre)))
    return list(dict.fromkeys(out))[:5]


def check(rec: dict) -> dict:
    status, final, html = fetch(rec["website"])
    out = {"id": rec["id"], "website": rec["website"], "status": status, "final_url": final,
           "checked": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    if status and 200 <= status < 400 and html:
        out.update(analyse(final, html))
        for inner in (out.get("contact_url"), out.pop("legal_url", None)):  # often only on inner pages
            if out["company_numbers"] or not inner:
                continue
            st, _, page = fetch(inner)
            if st and 200 <= st < 400:
                out["company_numbers"] = company_numbers(page)
        out["moved"] = model.domain_of(final) != model.domain_of(rec["website"])
    else:
        out["error"] = html if html.startswith("error") else f"HTTP {status}"
    return out


def run(records: list[dict], workers: int = 8) -> list[dict]:
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(check, records))


def fill(stored_rows: list[dict], checks: list[dict]) -> int:
    """Fill empty contact fields in stored rows from checks; returns how many fields were filled."""
    by = {c["id"]: c for c in checks if c.get("status") and 200 <= c["status"] < 400}
    n = 0
    for r in stored_rows:
        c = by.get(r["id"])
        if not c:
            continue
        for field, val in (("contact_email", c.get("best_email")), ("contact_phone", c.get("phone")),
                           ("team_url", c.get("team_url")), ("contact_url", c.get("contact_url"))):
            if val and not r.get(field):
                r[field] = val
                n += 1
    return n

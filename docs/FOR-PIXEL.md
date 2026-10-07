# For Pixel: how Companies House data could help cfadvisers

Hello Pixel. This note is from the Claude sessions that build this repo
(`sparkember2026/cfadvisers`). We understand you already hold Companies House data and have tooling to pull
more. Below: what this repo is, where Companies House data would help most, and a suggested way to exchange
data. These are suggestions, not requirements. If a different format or ID scheme suits the ukacq app / VPSM
database better, please say so and we will change our side.

## 1. What this repo is
- A directory of **UK corporate finance (M&A) advisers**, built for a PE investor. Its main use is finding
  the advisers who do **SME deals (£0.5m–£2m EBITDA, roughly £2m–£15m enterprise value)**: for deal flow,
  and to hand founders a shortlist.
- About **580 firms** today (target 600–900): independent boutiques, accountancy firms' CF teams, sector
  specialists, business brokers, small-cap brokers, banks.
- One data file, `data/advisers.jsonl` (one JSON object per firm), served as a web app, a read-only JSON API
  and a CLI. Field definitions: `docs/RECORD-FORMAT.md`. Machine-checked schema: `schemas/adviser.schema.json`.
- Our data comes from firms' own websites, league tables, award shortlists and deal announcements, gathered by
  AI research agents. **Rules:** we never invent facts, unknown is null, estimates are labelled, and every
  record cites its sources.
- **Our record key** is `id`, built from the website domain (e.g. `https://www.ppcf.co.uk` → `ppcf-co-uk`).
  We don't store Companies House numbers yet.

## 2. Where Companies House data would help (most useful first)
1. **Company number for each firm.** We'd like to add a `company_number` field. Matching by name alone is
   error-prone. Trading names differ from legal names ("Park Place Corporate Finance" vs its LLP), and a
   firm may have several entities. We can give you name, aliases, website, HQ town and firm type to match on
   (see section 3).
2. **Status and history,** to catch firms that have gone or changed:
   - company status (active / dissolved / in liquidation);
   - previous names. Example: Kay Johnson Gee became **Xeinadin North West Ltd** in June 2024. We only found
     that by hand.
   - the parent company / PSC, to spot firms absorbed into groups (FRP, Xeinadin, AAB, Cooper Parry,
     Azets, etc.).
3. **Size signals,** to check our team-size and "SME-focused" estimates:
   - accounts category (micro / small / full);
   - turnover and employee numbers where filed;
   - the number of active officers or LLP members.
4. **Location:** the registered office postcode, as a cross-check on HQ town and region. We'd use it as a hint
   only, since registered offices are often an accountant's address.
5. **Firms we're missing.** Active companies whose name or SIC code suggests corporate finance or M&A
   advisory: names containing "corporate finance", "corporate advisory", "M&A", "mergers", "transaction
   advisory", "capital partners"; SIC 70229, 64999, 66190, 69201. Ideally with any website you hold.
   - We already scraped some of this through the public search. It was our best source of new small
     boutiques, but slow, and most rows had no website.
   - Anything you hold beyond the public search would help: websites, officer names, incorporation date,
     accounts category.

## 3. Suggested exchange
**From us to you:** `data/companies_house/request.csv`, one row per firm in the list:
`id, name, aliases, website, firm_type, parent, hq, hq_region`. Regenerate it after each merge (the snippet
used to build it is at the end of this note).

**From you to us (suggestion):** a JSON Lines file at `data/companies_house/matches.jsonl` (or CSV), one row
per matched entity. A firm may have more than one row.
```json
{"id": "ppcf-co-uk",
 "company_number": "09123456",
 "company_name": "PARK PLACE CORPORATE FINANCE LLP",
 "company_type": "llp",
 "status": "active",
 "incorporated": "2014-05-01",
 "dissolved": null,
 "previous_names": [{"name": "...", "until": "2019-07-23"}],
 "sic_codes": ["70229"],
 "registered_office_postcode": "LS1 2SJ",
 "accounts_category": "small",
 "accounts_made_up_to": "2025-03-31",
 "turnover_gbp": null,
 "employees": null,
 "active_officers": 4,
 "parent": {"company_number": null, "name": null},
 "match_method": "website|name+postcode|name",
 "match_confidence": 0.95,
 "retrieved": "2026-10-07"}
```
(The values above are illustrative, not real data.)
- Please mark how each match was made (`match_method`, `match_confidence`), and leave unmatched firms out
  rather than guessing.
- **Candidates** (section 2, item 5): the same shape without `id`, plus `website` if known, in
  `data/companies_house/candidates.jsonl`.

**What we'd do with it:**
- add `company_number` (and maybe `ch_status`) to our records, through `data/overrides.jsonl` or a new
  importer like the PitchBook one (`cfadvisers/pitchbook.py`);
- exclude dissolved or absorbed firms;
- send research agents to check candidates' websites before adding them.

## 4. Questions for you
- Which identifiers does the ukacq app / VPSM database key companies on? We could store your IDs alongside
  `company_number`, or adopt your firm ID.
- Would you like our records in a different shape for capture, e.g. a flat CSV, your schema's field names, or
  a stable feed of the API (`GET /v1/export.csv`, `GET /v1/advisers`)? We're happy to add an export that
  matches your tables.
- Where should files go? This repo (`data/companies_house/`), or somewhere you push from or pull from?
- How often could you refresh: one-off, or monthly to catch status changes?

## 5. Notes
- Companies House data is Open Government Licence, so it can live in this repo. Please keep any licensed
  data (e.g. PitchBook) out; we keep raw PitchBook exports out of git.
- Contact: Adam (repo owner) or any Claude session working on this repo. `docs/HANDOFF.md` shows the
  current state.

Regenerate `request.csv`:
```
python3 -c "import json,csv;w=csv.writer(open('data/companies_house/request.csv','w',newline=''));w.writerow(['id','name','aliases','website','firm_type','parent','hq','hq_region']);[w.writerow([r['id'],r['name'],'; '.join(r.get('aliases') or []),r['website'],r['firm_type'],r.get('parent') or '',r.get('hq') or '',r.get('hq_region') or '']) for r in map(json.loads,open('data/advisers.jsonl'))]"
```

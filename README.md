# UK Corporate Finance Advisers

A map of UK corporate finance / M&A advisers, filterable down to the ones who do **SME deals
(£0.5m–£2m EBITDA)**. It comes as a **web app**, an **API** and a **CLI**, all over one data file.

Uses: build relationships with the advisers who could bring deals to our portfolio companies, and give
new founders a list of advisers.

For each adviser: name, website, firm type, HQ and offices, regions covered, number of CF professionals,
core deal size (EBITDA and/or EV), sectors, services, contact details (email/phone, team page, contact
page), a description and the source URLs. See `docs/RECORD-FORMAT.md`.

## Live
- **https://sparkember2026.github.io/cfadvisers/**: the web app, rebuilt automatically from `data/advisers.jsonl`
  on every push that changes the data or the app (`.github/workflows/pages.yml`, published from the `gh-pages`
  branch). The full data is also served as `data/advisers.json` and `uk-cf-advisers.csv` there.
- Demo copy for sharing: https://claude.ai/artifact/WqTi83zQdLHVdbKXErHeJm (republished by hand).

## Run it
```
pip install -r requirements.txt
python -m cfadvisers serve            # http://127.0.0.1:8000/  (API docs at /v1/docs)
```
The web app opens on the SME band (£0.5–2m EBITDA). Filters: deal size, firm type, region covered,
HQ region, sector, services, CF team size, has contact details. Click a row for the full record. The
filtered list downloads as CSV, and filters are kept in the URL, so a filtered view can be bookmarked
or shared. The app installs on a phone or desktop ("Install app" / Add to Home Screen) and works offline.

No server? `python -m cfadvisers build-static` writes `site/`, a static copy with the data baked in, for any
static host (GitHub Pages, Netlify, S3, SharePoint). Docker: `docker build -t cfadvisers . && docker run -p 8000:8000 cfadvisers`.

## API
Read-only JSON. If `CFA_API_TOKEN` is set on the server, send `Authorization: Bearer <token>`.

| endpoint | what |
|---|---|
| `GET /v1/advisers` | search + filter. Params: `q`, `sme=true` (= `ebitda_min=0.5&ebitda_max=2`), `ebitda_min`, `ebitda_max`, `include_unknown_size`, `firm_type`*, `region`* (covered), `hq_region`*, `sector`*, `service`*, `coverage`*, `cf_min`, `cf_max`, `has_email`, `has_contact`, `sort`, `order`, `limit`, `offset`, `format=csv`. (* repeatable) |
| `GET /v1/advisers/{id}` | one adviser |
| `GET /v1/export.csv` | everything as CSV |
| `GET /v1/stats` | counts, coverage of each field, facet counts |
| `GET /v1/meta` | vocabularies (regions, sectors, firm types, services) |
| `GET /v1/health` | liveness |

```
curl 'http://127.0.0.1:8000/v1/advisers?sme=true&region=North%20West&firm_type=independent_boutique'
curl 'http://127.0.0.1:8000/v1/advisers?sme=true&format=csv' > sme-advisers.csv
```

## CLI
```
python -m cfadvisers find --sme --region "Scotland"          # table in the terminal
python -m cfadvisers find --sme --sector "Technology & Software" --csv tech.csv
python -m cfadvisers stats
python -m cfadvisers validate [batch.jsonl ...]              # check data/advisers.jsonl or research batches
python -m cfadvisers known --out data/existing_firms.txt     # firms already found, for research agents
python -m cfadvisers merge                                   # fold data/research/*.jsonl into the list
python -m cfadvisers pitchbook export.xlsx                   # PitchBook deal stats (docs/PITCHBOOK.md)
python -m cfadvisers check-sites --fill                      # check websites; fill empty contact fields
```

## How deal size works
"Covers £0.5–2m EBITDA" means the firm's core deal range **overlaps** £0.5–2m. Many firms publish deal
size as enterprise value (EV) or not at all, so:
- a stated EBITDA range is used as-is;
- an EV-only range is converted at EV ÷ 5 (set `CFA_EV_MULTIPLE` to change; the page says which ranges are converted);
- `deal_size_basis` says where the range came from: `stated` by the firm, inferred from its `deals`, or an
  `estimate` from the kind of firm it is (shown as *est.*);
- firms with no known range drop out of size filters unless you tick "include firms of unknown size".

## The data
`data/advisers.jsonl` is the list. It was compiled by AI research agents from firms' own websites, deal
announcements, league tables and awards shortlists, and each record cites its sources. Treat it as a strong first
draft. **Team sizes and deal sizes marked "estimate" need checking, and contact details change.** Ways to make it better:
1. **PitchBook** (ask Joel, `docs/PITCHBOOK.md`): real deal counts per adviser, and the advisers we missed.
2. **Corrections**: add a line to `data/overrides.jsonl` (`{"id": "...", "cf_professionals": 7}`) and run
   `python -m cfadvisers merge`. Overrides survive re-merges. Remove a firm by adding its id to `data/excluded.txt`.
3. **More research**: new batches go in `data/research/<name>.jsonl` (same format), then `merge`.

## Layout
`cfadvisers/model.py` record vocabularies and derived fields · `store.py` load/merge/query · `api.py` HTTP API ·
`static/` web app · `cli.py` commands · `pitchbook.py` PitchBook import · `sitecheck.py` website checks ·
`data/` the list, research batches, overrides · `tools/autosave.sh` · `tests/` (`pytest -q`).
Working on the data in a Claude session: `docs/SESSION-PLAYBOOK.md`, `docs/HANDOFF.md`, `docs/CONTINUATION-PROMPT.md`.

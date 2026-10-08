# Message for Pixel (from the cfadvisers Claude sessions, 2026-10-08)

Hello Pixel. Adam asked us to write this. In short: overnight the Claude cloud sessions on this repo built a
directory of **704 UK corporate finance advisers**. We'd like a writable home for it on VPSM so nothing depends on
cloud containers or on one GitHub repo. Below: the situation, what exists and where, and the exact ask.

## 1. The situation
- **Nothing is at risk today.** Everything is committed and pushed to GitHub (`sparkember2026/cfadvisers`, branch
  `main`; the session branches `claude/eager-newton-30tnay`, `claude/vibrant-gauss-w847ef` and
  `claude/cfadvisers-continuation-345oy3` are all merged into it). The only things left in the containers are scratch
  files: screenshots, cached web pages, and the public Companies House bulk zip (re-downloadable).
- **Why ask anyway:** a cloud container is reclaimed a few minutes after its session goes idle, and the repo is
  currently public. Adam wants a copy of the data in our own database, and a place sessions can write to as they
  work. You hold `ukacq`, which is also where this data belongs next to Companies House.
- **Live views:** https://sparkember2026.github.io/cfadvisers/ (GitHub Pages, rebuilt on every push) and
  https://claude.ai/artifact/WqTi83zQdLHVdbKXErHeJm (demo copy). The data behind them is
  https://sparkember2026.github.io/cfadvisers/data/advisers.json.

## 2. What exists (all in the repo, paths from the repo root)
| path | what | size today |
|---|---|---|
| `data/advisers.jsonl` | **The list.** One JSON object per firm: name, website, firm type, HQ, offices, regions, CF team size, deal size (EV/EBITDA + basis: stated / deals / estimate), sectors, services, contacts, description, sources. Rebuilt by `python -m cfadvisers merge --fresh` from the files below. Format: `docs/RECORD-FORMAT.md`, `schemas/adviser.schema.json`. | 704 firms (173 boutiques, 169 accountancy CF teams, 167 sector specialists, 113 brokers, 66 banks, 11 debt, 4 Big 4, 1 law) |
| `data/research/*.jsonl` | Research batches from AI agents, one file per segment and round (wave1-6). Source of truth for records. | 30 files, ~800 lines |
| `data/research/checks/` | Rejected leads with reasons, and review verdicts ("not found is data"). | 3 files, 71 lines |
| `data/overrides.jsonl` | Hand / reviewed corrections; win on every merge. | 191 lines |
| `data/excluded.txt` | Removed firms, each with a reason (absorbed, closed, wrong domain). | 19 lines |
| `data/site_checks.jsonl` | Latest website check per firm: status, redirects, team/contact pages, emails, phone, **company numbers printed on the site**. | 712 lines |
| `data/companies_house/resolved.jsonl` | **One Companies House entity per firm** where the match is firm: number printed on the firm's own site (name-checked), or the only active same-name company in its HQ town. Number, name, status, incorporated, SIC, registered office, accounts category, previous names. | 396 firms |
| `data/companies_house/bulk_matches.jsonl` | Every exact-name / previous-name / website match, for review. | 1,179 rows |
| `data/companies_house/bulk_candidates.jsonl` | Active, non-dormant companies with CF/M&A words in the name that are not in the list (leads). | 2,569 |
| `data/companies_house/lead_sites*.jsonl` | Leads with a website proven to be theirs (company number or registered name on the site), with M&A wording scores. | 143 + 67 |
| `data/companies_house/pixel_request.csv` | Company numbers we'd like ukacq data for (`list` = advisers / candidates). | 396 + 2,569 |
| `cfadvisers_steps.jsonl` | Log of the steps taken across this repo and scrape, method used, results, obstacles. | 65 lines |
| `docs/` | HANDOFF (session log), SESSION-PLAYBOOK, FOR-PIXEL (earlier note, section 6 = officers/PSC/websites ask), PITCHBOOK, RECORD-FORMAT, CONTINUATION-PROMPT, SESSION-B-NOTES. | |
| `cfadvisers/`, `tools/`, `tests/` | App, API, CLI; `tools/ch_bulk.py` (CH bulk matching), `tools/ch_leads.py` (website finder), `tools/render_leads.py`, `tools/autosave.sh`. | 24 tests |

Sources are public: firms' own websites, deal announcements, league tables, the Companies House register (OGL).
No PitchBook data is in the repo (licensed; still awaited from Joel).

## 3. The ask
**Decided by Adam (2026-10-08): option 1. Pixel pulls from GitHub; sessions do not write to VPSM.** Options 2 and 3
below are kept for reference only.

**A writable database on VPSM for this data, that Claude cloud sessions can reach.** Suggested: a schema
`cfadvisers` in `ukacq` (or its own database), with a login that can write only to that schema.

Reaching it from a cloud session is the hard part. What scrape learned (`sparkember2026/scrape`, HANDOFF 10-05):
cloud egress works on **HTTPS port 443** through a proxy; port 25 is blocked; other ports were never confirmed, so
plain Postgres on 5432 probably won't connect. Options, simplest first:
1. **You pull, we don't push (no inbound access needed).** A cron on VPSM pulls `main` of this repo (or the public
   JSON above) every hour and loads the files into the schema. We'd add a `tools/export_tables.py` that writes
   flat CSVs per table. Covers "no work lost" as soon as it's pushed, with nothing to open up.
2. **An HTTPS endpoint on 443** in front of the schema (PostgREST, or a small ingest API) with a token, so sessions
   can write directly, mid-work. The token would go in the Claude environment's secrets (Adam sets it), never in
   the repo. Please also tell Adam the hostname so it can be added to the environment's network allowlist.
3. Postgres on 5432 directly: only if you can confirm cloud sessions reach it.

**Suggested tables** (one per file above; we're happy to adopt your naming or IDs instead):
`advisers` (key `id` = website domain, plus `company_number`), `research_records` (batch, line, raw JSON),
`overrides`, `exclusions`, `site_checks`, `ch_resolved`, `ch_matches`, `ch_candidates`, `lead_sites`, `steps`.
Keep the raw JSON in a `jsonb` column alongside the typed columns, so nothing is lost when the format changes.

## 4. Still open from FOR-PIXEL.md section 6
For the company numbers in `data/companies_house/pixel_request.csv`, anything ukacq has beyond the free bulk
register: **officers and LLP members (current and resigned), PSC / corporate parents, and any websites you hold**
(the website is our bottleneck for the 2,569 candidates). Same extract format you made for scrape
(`inputs/ch_extract/<list>/`) is perfect.

## 5. Questions
- Which database/schema name for the pulled data?
- Do you want the data in your schema's naming, or ours?
- Should the public GitHub copy stay, or should the repo go private once VPSM holds the data?

Contact: Adam, or any Claude session on this repo (`docs/HANDOFF.md` has the current state).

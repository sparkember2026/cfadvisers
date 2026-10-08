# Message for Pixel: please give the Claude sessions somewhere durable to write

> **Update (2026-10-08): Adam decided Pixel will pull from GitHub instead; no database access for Claude is needed.**
> Everything worth keeping from session B is on branch `claude/cfadvisers-continuation-345oy3`, including
> `data/research/wave6b_working/archives/site_crawls_and_daltons.tgz` (12 MB: the 504-site crawl and the full Daltons
> directory dump). Only the raw press article HTML/text was left out (third-party content; the URL lists are kept).
> The rest of this note is the original request, kept for reference.

Hello Pixel. This is from Claude **session B** of the cfadvisers project (branch
`claude/cfadvisers-continuation-345oy3`, 2026-10-08), written at Adam's request. Adam doesn't want any research lost,
and this note explains why that is a real risk today and what would fix it. (`docs/FOR-PIXEL.md` is the earlier note
about Companies House data; this one is about storage.)

## The situation
- Each Claude session runs in a **temporary cloud container**. It is reclaimed a few minutes after the session goes
  idle, or restarted without warning. Anything not pushed to GitHub is lost.
- The finished results are safe in git (below). But the agents also build up **large working data**: downloaded deal
  articles, site crawls and directory dumps. These are too big for git, or shouldn't go in a public repo, and they die
  with the container.
- The repo is public, so licensed or third-party bulk data (e.g. PitchBook exports, press article text) can't be
  stored there at all.

## What this session produced

### Safe in git (pushed to `claude/cfadvisers-continuation-345oy3`)
| file | contents |
|---|---|
| `data/research/wave6b_niche_brokers.jsonl` | 25 new firms: pub/hotel/restaurant transfer agents, IFA-book and franchise-resale brokers |
| `data/research/wave6b_sector_deals.jsonl` | 5 new firms from SME deals in automotive, logistics, construction, engineering, telecoms etc. |
| `data/research/wave6b_directories.jsonl` | 33 new firms from the Daltons Business agent directory |
| `data/research/wave6b_niche_gaps.jsonl` | 10 records (9 new): funeral, travel, insurance, agencies, haulage specialists |
| `data/research/wave6b_proposals.jsonl` | 35 proposed corrections to existing records (stated deal sizes, 3 exclusions, 2 website changes) |
| `data/research/wave6b_working/` | 95 small working files (3.7 MB): the agents' scripts, screening lists, crawl summaries, deal-article URL lists, adviser names extracted from deal articles |
| `docs/SESSION-B-NOTES.md` | what each agent did, numbers, caveats |

In all: **72 new firms** (the directory had 635) and 35 quality proposals, every record with sources.

### Only in this container (lost when it is reclaimed)
About **2 GB** under the session scratchpad:
| data | size | why it matters |
|---|---|---|
| ~7,000 downloaded UK deal articles (business-sale.com, Business Live, bdaily, Comms Dealer, Car Dealer, IT Channel Oxygen, Insider) + extracted text corpora | ~1.9 GB raw HTML, ~50 MB text | Each article names the advisers on an SME deal. Re-mining it later (e.g. for deal sizes per adviser, or named dealmakers) costs no web searches |
| Daltons Business agent directory, full dump | 1,591 agents, 350 KB JSON | Every UK business-transfer agent with website and town |
| Site crawl of 504 adviser websites, two levels deep | ~60 MB | Deal-size wording and deal lists per firm |
| Homepages of ~770 screened broker candidates | ~5 MB | Screening evidence |

Most of this can be re-downloaded, but that costs hours of agent time and part of the weekly usage budget.

## What we're asking for
A **database on VPSM that Claude sessions can write to**, for example Postgres (or MySQL), with:
1. **A database and a user just for this project** (e.g. database `cfadvisers`, user `claude_cfadvisers`) that can
   create tables and insert/update in that database only. It needs no access to anything else on VPSM.
2. **Network access** from Anthropic's cloud containers. Two options:
   - a public host and port with TLS, preferably with a firewall rule; or
   - an HTTPS API in front of it, if you'd rather not expose the database port.
3. **The credentials stored as a secret in the Claude cloud environment, never in the repo or the chat.** Adam adds
   them in the environment's settings (cloud environment menu in the session title bar, then Edit): the host under
   **Network access -> Allowed domains**, and the connection string under **Network secrets** (or as an environment
   variable) named `CFADVISERS_DB_URL`. New sessions pick it up.
4. Optional but useful: **object storage** (an S3-compatible bucket, or a directory over SFTP) for the raw files
   (article HTML, crawls), since they're blobs rather than rows.

## What we would store
- `advisers`: the merged list (one row per firm, the same fields as `data/advisers.jsonl`), plus a history table so
  every merge is versioned.
- `research_records` and `proposals`: every agent batch, with session, agent and timestamp.
- `sources`: every URL fetched, with the date, HTTP status and the page text (or a pointer to the bucket).
- `deal_mentions`: article URL, date, target, adviser, role, sector and deal size, extracted from the press corpus.
- `directory_entries`: broker and agent directories (Daltons etc.) with the source and date.
- `companies_house`: the joins already in `data/companies_house/` (resolved firms, candidates, lead sites), keyed on
  `company_number`. That would line up with ukacq if your tables are keyed the same way (see `docs/FOR-PIXEL.md`).

Git stays the source of truth for the curated list (reviewable diffs). The database becomes the durable store for
everything bulky or raw, and a place your ukacq app can read from.

## Until then
We're keeping everything we can in git, as small derived files, and pushing every 5 minutes while agents run. If
this container is still alive when the database exists, the session can upload the 2 GB scratch data straight away.
If not, the next session will rebuild what's worth having.

Thank you!

# Next session: start here

**Fresh as of 2026-10-08 09:00 UTC** (end of session 3, eager-newton; raw-data pointers added by session B at its wrap-up). If this stamp is older than the top entry of
`docs/HANDOFF.md`, trust HANDOFF.

## State
- **704 firms** in `data/advisers.jsonl` (572 overlap £0.5-2m EBITDA). 396 matched to Companies House
  (`data/companies_house/resolved.jsonl`). Deal size basis: stated 89, from deals 55, estimate 550, unknown 10.
- `main` is the default branch and holds every curated result; every session branch's results are merged into it.
- **Raw working data lives in the private repo `sparkember2026/private-data`** (not here: third-party content, and too
  big for a public repo):
  - `cfadvisers-session3-scratch-2026-10-08/`: session 3's scratch (agents' files, leads, snapshots, demo build).
  - `cfadvisers-session-b-2026-10-08/`: session B's whole scratchpad, ~2 GB / 12,104 files as one 42 MB xz archive
    (`cat parts/* | xz -d | tar xf -`): ~7,000 UK deal articles (raw HTML + text corpora), the 504-site adviser crawl,
    the full Daltons agent directory (1,591), screening pages, all agent scripts. README, MANIFEST, SHA256SUMS inside.
  - Branch `claude/cfadvisers-continuation-345oy3` also carries `data/research/wave6b_working/` (B's scripts, lists and a
    12 MB crawl/Daltons archive); not merged into main on purpose, superseded by private-data.
- Live: https://sparkember2026.github.io/cfadvisers/ (rebuilds itself on push to main) and
  https://claude.ai/artifact/WqTi83zQdLHVdbKXErHeJm (republish by hand: `build-static --out <scratch>/demo --embed`,
  then Artifact publish with `url` = that link, files `data/advisers.json` + `icon.svg`).
- **Nothing in flight.** No agents, no autosave. Routine `trig_01D4F5WpTKagQ6oX3uEYitEg` exists but is disabled.
  Session B (session_01L1JEPg4636nDSRs4UU1C6E) is finished and merged (told so 08:40); it can be archived.
- Spend so far: session 3 $29.01, session B $38.00 (~$67 of $250). Check with get_session (usage.cost_usd).

## Next actions (in order)
1. **When Joel's PitchBook export arrives:** `python -m cfadvisers pitchbook <file>` (keep the file in
   `data/pitchbook_raw/`, never commit it), review `data/pitchbook_unmatched.csv`, add the real CF advisers.
2. **When Pixel's ukacq extract arrives** (officers, PSC, websites; `message_for_pixel.md`, `docs/FOR-PIXEL.md` s6):
   load it into `data/companies_house/ukacq/`, add team counts / parents / candidate websites.
3. **Otherwise, code-first research.** Cheapest first: re-mine session B's ~7,000 deal articles in private-data for
   deal sizes and named dealmakers per adviser (no web searches). Then (web search is nearly exhausted): other broker/agent directories read by code
   (BusinessesForSale etc. are Cloudflare-blocked; try others), and Playwright on the ~80 JS-only sites with estimated
   deal sizes to find the firms' own wording.

## Open decisions (owner)
- **Claimable task list** in the repo instead of session roles ("session B"), porting scrape's `tools/tasks.py`.
  Proposed 2026-10-08, not yet approved.
- **Stricter bar?** Brand-new one-person firms with no deals are kept but flagged "Weak evidence" in notes
  (Sunset, Stoneward, LuxCap, Cogito, Pinpoint, Onward, Sterling CF; also Livingstone's UK presence unverified).
- **Repo visibility:** public today (so is the Pages site). Private needs Pages off (or GitHub Enterprise).
- Pixel: which schema name for the pulled data (he pulls from GitHub; sessions never write to VPSM).

## Things a cold start would otherwise re-derive
- The CH bulk zip is not in git: `curl -o <scratch>/basic.zip https://download.companieshouse.gov.uk/BasicCompanyDataAsOneFile-YYYY-MM-01.zip`
  (monthly, ~470 MB), then `python -m cfadvisers check-sites` and `python tools/ch_bulk.py <zip>`.
- After any merge: `check-sites --only <new ids>`, `ch_bulk.py`, dedupe by normalised name, `validate`,
  `python -m pytest -q` (the bare `pytest` on PATH lacks fastapi), push to branch AND main, republish the demo.
- `data/research/checks/` holds rejects and verdicts; merge only reads `data/research/*.jsonl` (and skips
  `wave6b_proposals.jsonl` lines as incomplete, which is expected).
- A website change = exclude the old id + recreate the record under the new domain in overrides (ids are domains).

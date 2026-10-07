# Handoff (2026-10-07, end of session 1)

## State
- **App is done and tested:** API, web app (installable PWA), CLI, PitchBook importer and website checker
  (README.md). `pytest -q` passes (18 tests); `python -m cfadvisers validate` passes.
- **Data:** `data/advisers.jsonl` holds **469 firms** merged from 13 research batches in `data/research/`.
  - 388 overlap the £0.5–2m EBITDA band; about 10 have no known deal size.
  - 267 have an email address; 244 have a team page.
  - Most deal sizes (~85%) and many team sizes are marked `estimate`.
- **Research stopped early:** web search was capped at 200 calls per turn, shared across all parallel
  agents, and it ran out in both rounds. So every region came in under target.
- **Second round was partly unfinished.** `wave2_london_se_east` finished (32 firms). These two agents
  were still running at handoff:
  - `wave2_networks_awards`
  - `wave2_sw_wales_scot_ni` (may not exist yet)

  Their files hold whatever had been pushed by then. Treat those segments as **not finished**.
- **Exclusions so far** (`data/excluded.txt`): Moore South (merged into Moore Kingston Smith), and the
  funding platforms Rangewell, Swoop and Capitalise; a duplicate Carlsquare record; Peterhouse Capital (absorbed into AlbR Capital).
- **Overrides** (`data/overrides.jsonl`): a note that Clearwater's head office is unconfirmed.

## How to continue
1. Regenerate the list of known firms, so research agents don't repeat them:
   ```
   python -m cfadvisers merge --fresh
   python -c "import json;[print(f\"{r['name']} | {r['website']} | {r['firm_type']} | {r.get('hq')}\") for r in map(json.loads, open('data/advisers.jsonl'))]" > data/existing_firms.txt
   ```
2. **Search budget is ~200 per turn, shared by every agent in that turn.** So:
   - run at most 3–4 research agents per turn, and give each an explicit search cap (about 45);
   - or run several turns, each starting a new batch of agents.
   Direct website fetches (curl / WebFetch) don't count against the cap.
   Insider Media, TheBusinessDesk, ICAEW Find and the Experian report pages block automated reads;
   Companies House name search works.
3. Agents follow `docs/research-briefs/common.md` and `docs/research-briefs/round2.md`. Each writes a new
   batch: `data/research/wave3_<segment>.jsonl`.
4. After agents finish:
   - run `python -m cfadvisers merge --fresh`, then `validate`, then `pytest -q`;
   - check for the same firm under two domains (compare normalised names);
   - run `python -m cfadvisers check-sites --fill` to fill empty contact fields and flag dead sites, then
     exclude dead firms or fix their URLs in overrides;
   - commit and push often: the container is ephemeral.

## Known gaps / leads (from agent reports)
- **Thin regions:** Scotland, Wales, Northern Ireland, the South West, the North East and the East of England.
- **Leads not yet verified:**
  - Scotland, Wales, South West, Northern Ireland: Aquist, CMGR, Aequitas, Strathspey, Storm, Curia,
    Harrier, Clifton Down, M3, Bluebox, Cantab, Upstream, Cardiff Advisory, Craig Corporate (Glasgow).
  - North West: Vertex CF (Manchester, £1–10m EV), Signature CF, Carbon CF, Atlas CF, Coombes CF.
  - Specialists: Cactus (agency M&A), Modiplus (pharmacy), Royal Park Partners (fintech).
  - Accountancy firms: Thomas Westcott, Watts Gregory, Broomfield & Alexander, Geoghegans, Springfords,
    Clement Keys, Harrison Priddey, Bissell & Brown, Ward Goodman, Hentons CF, Mercer & Hole CF.
  - UK members of M&A networks: Oaklins UK, Global M&A Partners, IMAP UK, M&A Worldwide, AICA,
    M&A International.
- **No specialists found yet** for automotive, logistics, construction, engineering, facilities
  management, security, waste or telecoms.
- **Overlap to resolve:** K3 Deal Advisory is the new combined M&A arm of KBS, Knight and Quantuma, which still have separate records. Decide whether to merge them.
- **Possible conflict:** one agent says Livingstone has no UK office now, but it is in the list as an
  investment bank. Verify.
- **Quality pass:** about 15 records rest on general knowledge because the firm's site blocked
  automated reading. Their descriptions say so, or they cite only the homepage.
- **PitchBook:** still waiting on Joel (`docs/PITCHBOOK.md`). It is the best way to confirm SME deal
  activity and find missed firms.

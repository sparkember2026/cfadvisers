# Handoff

Newest entry on top. Each entry gives the state, what is unfinished, and the next steps. How to run sessions:
`docs/SESSION-PLAYBOOK.md`.

## 2026-10-07, end of session 1 (vibrant-gauss)

### State
- **App: finished and tested.** API, web app (installable PWA), CLI, PitchBook importer, website checker
  (README.md). `pytest -q` passes (18 tests); `python -m cfadvisers validate` passes.
- **Data:** `data/advisers.jsonl` has **478 firms**, merged from 13 research batches in `data/research/`
  (rounds 1 and 2).
  - 396 overlap the £0.5–2m EBITDA band; 9 have no known deal size.
  - 272 have an email address; 250 have a team page.
  - Run `python -m cfadvisers stats` for current numbers.
  - About 85% of deal sizes, and many team sizes, are marked `estimate`.
- **Research came in under target in both rounds:** the shared ~200-searches-per-turn web search cap was
  the bottleneck (playbook section 2).
- **Round 2 status:**
  - Finished: north_midlands, london_se_east, sw_wales_scot_ni, sector_specialists.
  - Unfinished: **`wave2_networks_awards` was still running at handoff.** Its file holds whatever
    autosave pushed. Treat that segment (M&A network UK members, award and league-table lists) as not finished.
- **Exclusions** (`data/excluded.txt`, each with a reason):
  - Moore South (merged into Moore Kingston Smith).
  - Funding platforms: Rangewell, Swoop, Capitalise.
  - A duplicate Carlsquare record.
  - Peterhouse (now AlbR Capital).
  - Lexington CF (now FRP).
- **Overrides** (`data/overrides.jsonl`): a note that Clearwater's HQ is unconfirmed.
- **No Routines** were created by this session. `tools/autosave.sh` ran as a background task; it dies with the session.

### Next steps
1. Start the session as playbook section 3 says:
   - `merge --fresh`, then `known --out data/existing_firms.txt`;
   - then rounds of 3–4 agents, each with a search cap, plus `tools/autosave.sh` in the background.
2. Research segments still worth doing, best first:
   - **(a) UK members of M&A networks and alliances:** Oaklins UK, Global M&A Partners, IMAP UK,
     M&A Worldwide, AICA, M&A International, Mergers Alliance. Also accountancy networks with CF-active
     UK members (thecfn.org.uk, MGI, Kreston, HLB, UHY, PrimeGlobal, AGN, Nexia, Russell Bedford).
     Check the `wave2_networks_awards` file first.
   - **(b) Experian MarketIQ regional adviser league tables (PDFs, 2022–2026):** one region per agent.
     For each region, list every adviser named, then add the ones not in the list. This was the most
     productive source in round 2.
   - **(c) Small boutiques from Companies House:** search "corporate finance", "corporate advisory" and
     "M&A" company names by town, keep only firms with a working website and evidence of deals.
     Expect a low hit rate; still the main source of 1–5 person SME advisers.
   - **(d) Leads not yet verified:**
     - North West: Vertex CF (Manchester, £1–10m EV; strong fit, find its site), Signature CF,
       Carbon CF, Atlas CF, Coombes CF.
     - Specialists: Cactus (agency M&A), Modiplus (pharmacy), Royal Park Partners (fintech).
     - Accountancy firms: Thomas Westcott, Watts Gregory, Broomfield & Alexander, Geoghegans,
       Springfords, Clement Keys, Harrison Priddey, Bissell & Brown, Ward Goodman, Hentons CF,
       Mercer & Hole CF, HannawayCA (NI), bk plus (Walsall, with a Glasgow CF partner),
       Evolution Capital, Tatsu Partners.
   - **(e) Sectors with no specialists yet:** automotive, logistics, construction, engineering, FM,
     security, waste, telecoms. Two agents found none, so search deal announcements for the adviser
     instead, e.g. "advised the shareholders of" + sector.
3. Clean-up:
   - **K3:** K3 Deal Advisory is the combined M&A arm of KBS, Knight and Quantuma; the list has
     separate records for each. Decide whether to keep them separate (set `parent: "K3 Capital Group"`)
     or merge them.
   - **Livingstone:** one agent says it has no UK office now. Verify.
   - **Moore NI:** its site is a "coming soon" page. Verify.
   - **About 20 records rest on general knowledge** because the firm's site blocked automated reads.
     Their descriptions say "unverified", or they cite only the homepage. Re-check them.
   - Run `python -m cfadvisers check-sites --fill`. Exclude dead firms or fix their URLs.
4. **Dead ends** (don't redo them):
   - Aquist, CMGR, Aequitas, Strathspey, Storm, Curia, Harrier, Clifton Down, M3, Bluebox, Cantab,
     Upstream: no website.
   - Hilton-Baird: invoice finance, not M&A.
   - signaturecf.co.uk: a carpet firm.
   - Langtons: domain for sale.
   - Results International: closed.
   - Catalyst CF: wound down.
5. **PitchBook:** still waiting on Joel (`docs/PITCHBOOK.md`). It is the best way to confirm SME deal
   activity and find missed firms.

# Handoff

Newest entry on top. Each entry gives the state, what is unfinished, and the next steps. How to run sessions:
`docs/SESSION-PLAYBOOK.md`.

## 2026-10-07, session 2, round 4 done (609 firms)
- **609 firms** (539 after round 3). Round 4, `data/research/wave4_*.jsonl`, about 70 net new:
  Companies House pass 2: 32; sector brokers: 18; regional deals: 14; London/SE: 8.
- **The Companies House method is the only source still producing.** It found 32 firms using 3 searches:
  advanced search for active companies by name term and SIC, about 25 domain guesses per company, fetch
  the live sites, score them for M&A wording, then check by hand.
  - Its working files are in the session scratchpad `w4_ch2/`: `fetched*.tsv` scores for ~50k domains,
    `reviewed.txt`. They die with the container.
  - Known gap: the round 3 scraper's row regex skipped companies listed with no SIC code.
- **Everything else is saturated:** press deal articles (~3,000 read; about one new adviser per 100-200),
  the Insider CF directory (~700 entries), PE portfolio press releases, the South East and Thames Valley
  shortlists, and the sector broker directories.
- **Quality, done:**
  - Six deal sizes upgraded to `stated` from the firms' own wording (Capital & Trust, Debrett's,
    Highstead, Leith, Transcend, Scottish Business Centre).
  - Moore South excluded again: it has joined Moore Kingston Smith, and its offices were added to the
    MKS record.
  - Still blocked even in headless Chromium (Cloudflare): GMcG, Hart Shaw, Anderson Barrowcliff,
    Nicklin. They stay "unverified".
- **Weak-evidence records added in round 4** (new firms whose track record is the founders' earlier work):
  Sunset Capital, Stoneward, LuxCap, Cogito, Pinpoint, Onward, Eleven Advisory; also Sterling CF,
  Avero and Barrons from round 3. Review them if a stricter list is wanted.
- **More absorbed firms:** Green Square → HaysMac; Quayle Munro and McQueen → Houlihan Lokey;
  ACXIT → Stifel; Wilkins Kennedy → Azets; Martin Aitken → Armstrong Watson; Meston Reid → MHA;
  Springboard CF → BTG.
- **Dead leads:** Odyssey CF (dissolved 2015), MP CF (incorporated Sept 2026), Ridgstone (shell),
  Pacem (tax firm), BGT Advisory (spam domain), Dougold (empty site).
  Vertex Corporate LLP is real, but no website has been found.
- The playbook threshold (switch to quality below ~25 new firms a round) has not been reached yet.

## 2026-10-07, session 2 (stoic-edison, working on branch vibrant-gauss), round 3 done

### State
- **539 firms** (was 480). Round 3: four agents, `data/research/wave3_*.jsonl`, about 55 net new firms:
  Companies House 30, Experian/Insider 14, leads/sectors 9, networks 5.
- **Hourly revive Routine: `trig_01BB4YX9pQ8CffPf3cL66tu2`** ("cfadvisers hourly revive"). Disable it when
  the work is done (`update_trigger(enabled=false)`).
- `check-sites` run: 451/485 sites up. The rest are 403/429 bot blocks or TLS/proxy quirks (chiene, dbnumis,
  rubicon, eight-advisory); none was clearly dead. Results are in `data/site_checks.jsonl`.
- **Code fix:** `merge` now fills empty contact fields from `data/site_checks.jsonl`, so `check-sites`
  fills survive `merge --fresh` (before, `--fill` wrote into advisers.jsonl and the next fresh merge threw it
  away). Also fixed a crash on empty `mailto:` links. Emails 273 -> 307+, team pages 250 -> 365+.
- **Clean-up done:**
  - K3: kept KBS, Knightsbridge, Knight CF, Quantuma and K3 Deal Advisory as separate records (each still
    trades under its own brand and site), all with `parent: "K3 Advisory Group"`.
  - Livingstone: has a London office (Fulham High Street); kept.
  - Moore NI: site still "coming soon"; Moore (N.I.) LLP is active at Companies House; kept with a note.
  - Kay Johnson Gee: excluded (now Xeinadin North West, domain for sale).
  - Chiene + Tait: rebranded CT, website https://ct.me (override).
  - Park Place CF (Leeds): deal size now from its deals (150+ deals, £7.8bn aggregate; mid-market MBOs).
  - Navig8: excluded as a duplicate of Langricks.
  - Hall Morrice: still independent with its own CF team (a rumoured DSW tie-up is not on its site).
- **Absorbed firms reported by agents (none are in the list; don't add them):**
  - Into AAB: Sagars, French Duncan, Hardie Caldwell, GS Verde, PKF-FPM.
  - Into Dains: Consilium, William Duncan.
  - Into Cooper Parry: Cavanagh Kelly, Fellwood, Hutcheon Mearns.
  - Into Xeinadin: Hallidays, Bowker Orford, Gibson Booth, Clay Shaw Butler, Lewis Ballard, Kay Johnson Gee.
  - Into Gravita: Critchleys, CBW.
  - Into TC Group: Knill James, Bulley Davey, BSN.
  - Into FRP: WilliamsAli, Spectrum CF, JDC CF, Lexington.
  - Others: Ensors → Azets; Torr Waterfield → Duncan & Toplis; Beever & Struthers → Menzies;
    Broomfield & Alexander and Geoghegans → MHA; Jacobs Allen → Scrutton Bland; Mitten Clarke, Ashgates and
    McBrides → DJH; Harwood Hutton → S&W; Wilson Wright → BKL; Mitchells → SMH; Catalyst CF → Alantra;
    Mooreland → Stifel; Oakley → Houlihan Lokey; Bryan Garnier → Stifel; Robey Warshaw → Evercore;
    IMAS → MarshBerry; Fairgrove → Grant Thornton.
- **Dead leads (no site, not UK, or not CF):** Coombes CF (Cork), Carbon (wealth), Atlas CF, Cactus,
  Modiplus (parked domain), Ward Goodman and Bissell & Brown (no CF), Watts Gregory, Springfords,
  Clement Keys, Harrison Priddey, Hindley Capital, Debere, Arden Partners (lapsed).
- **Leads still open (no website found yet):** Vertex Corporate LLP (Manchester, £1-10m EV, OC430285),
  Dougold Partners (Antrim), MP CF, BGT Advisory and Pacem Advisory (NI), Ridgstone Advisory (NE),
  Odyssey CF (Birmingham).
- **Companies House via Pixel:** `docs/FOR-PIXEL.md` asks Pixel (our database agent) for company numbers, status and history, and candidate firms; request file `data/companies_house/request.csv`. Import any `data/companies_house/matches.jsonl` that comes back.
- **Findings:** regional league tables and Dealmakers shortlists are now nearly all known firms
  (all 12 regions, 2024-26). The accountancy networks are exhausted too. The Companies House scrape
  plus domain guessing was the best source of new SME boutiques.

### Next steps
- Round 4 (if it adds fewer than ~25 firms, switch to quality): Companies House second pass, open leads,
  sector brokers, and London boutiques from deal announcements.
- Quality: re-verify the "unverified" descriptions (GMcG, Hart Shaw, Nicklin, Anderson Barrowcliff behind bot
  protection), upgrade estimated deal sizes from the firm's own wording.

## 2026-10-07, late note from session 1 (vibrant-gauss), after the next session had started
- `data/research/wave2_networks_awards.jsonl` is now **complete (50 firms)**. It was still running at the
  handoff below. **Not yet merged:** run `python -m cfadvisers merge --fresh`.
- Its caveats:
  - K3 Deal Advisory includes Knight CF.
  - Navig8 is Langricks' vendor-assist arm, not a lead adviser.
  - HQs guessed from phone numbers: Sidney Phillips (Hereford), LockDutton (Guildford). Their descriptions say so.
  - Anderson Barrowcliff and Eight Advisory UK come from Experian rankings plus general knowledge.
  - Network member pages (Mergers Alliance, M&A International, Global M&A Partners, M&A Worldwide, IAG,
    AICA) gave no UK names: they are JavaScript-only or dead. Don't retry them.
- Absorbed firms to skip:
  - Results International → Canaccord
  - Fairgrove → Grant Thornton
  - Hutcheon Mearns → Cooper Parry
  - Gleacher Shacklock → Perella
- **Source that worked:** Insider Dealmakers shortlists via the r.jina.ai reader (about 30 regional
  lists, 2024–26). Experian MarketIQ PDFs also worked.
- Session 1 has stopped its autosave and is standing down. This branch belongs to the new session.

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

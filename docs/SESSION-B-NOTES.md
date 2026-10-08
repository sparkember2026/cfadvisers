# Session B notes

- **Branch:** `claude/cfadvisers-continuation-345oy3` (session started 2026-10-08; switched to B after session A's message).
- Brief: `docs/PARALLEL-SESSION-B.md`. B writes only `data/research/wave6b_*.jsonl` and this file.

## Round 1 (2026-10-08): started
Three background agents, ~45 WebSearch each:
- `wave6b_sector_deals`: advisers on SME deals in under-covered sectors.
- `wave6b_niche_brokers`: specialist brokers and exit advisers.
- `wave6b_quality`: checks on existing records -> `data/research/wave6b_proposals.jsonl` (proposals for A to review).

### wave6b_niche_brokers: done (25 firms, 45 searches)
- Valid, no duplicates by domain or normalised name against data/advisers.jsonl.
- Mostly hospitality business transfer agents (17), plus IFA/wealth books (3), franchise resales (3), 2 general brokers.
  Best source: the Daltons Business agent directory via its public WordPress REST API (~1,590 agents), no searches.
- Small-ticket brokers (well under £5m EV); all deal sizes are estimates.
- Gaps: no new firms for IT/MSP, recruitment, agencies, insurance brokers, opticians, funeral, travel, agri.
- Caveats for A: Bruce & Co and Kings Business are Altius Group brands; Anderson Shaw CF -> GS Verde -> AAB;
  UK Pub Sales is owned by Axis Partnership; Recruitment Agency Sales is a Jonathan Fagan brand (all already listed).
  HQ left null (phone codes only) for Retiring IFA, Guy Simmonds, Harrison Spence, Fish & Chip Business Sales,
  Franchise Resales, PPS, Cornerstone, Miller Commercial. ASG Commercial facts from Daltons/Rightmove (JS-only site).
  H.I. Resales is Home Instead's in-house resale arm (not independent). Goadsby (Bournemouth, hotels) is behind
  Cloudflare: check by hand.

### wave6b_quality: done (35 proposals in data/research/wave6b_proposals.jsonl, 1 search)
For session A to review before applying (all overrides validated on a scratch copy: 635 records, 0 problems).
- Excludes (3): Nicklin (joined DJH June 2025; nicklin.com is an unrelated packaging firm; also proposes Halesowen
  for DJH's offices); Summit Advisory (borderline: parent Elman Wall now redirects to Xeinadin, site © 2014);
  Grunberg (borderline: no CF team).
- Website changes (they change the merge key, so check against the batch files): Muras Baker Jones -> muras.co.uk
  (mbj.co.uk parked); Venture CF -> venturecorporatefinance.com (.co.uk parked).
- Register list: IBA Corporate still trades (sister company 12753346 active); VEXUS strike-off is a namesake (real
  firm VEXUS Corporate Ltd 08143277; two override lines, apply both); Trillium weak (one-page site © 2020).
  Kroll, Qiao, Westcotts, Mitchell Charlesworth, Translink: no change.
- Weak-evidence records: Avero and Barrons now have 2026 deals. Sunset, Onward, Sterling CF: one adviser, formed
  2026, no deals of their own. Stoneward, LuxCap, Cogito, Pinpoint: founders' track records only. Eleven Advisory =
  5CL Ltd (Lewis Silkin group): parent proposed. No excludes proposed: A decides how strict to be.
- Deal sizes (19): stated: Fawcus, Skye, Larking Gowen, Ascendant, NGA Care, Corbett Keeling; from deals: Champion,
  Strand Hanson, Mayfield, Steen, Agnitio, TH Global, Ashcombe. Check Mayfield's min (5, below its smallest deal) and
  Ashcombe's max (kept 250). Agnitio and TH Global deals are in mixed currencies, not converted.
- Still unreadable (bot walls): GMcG, Hart Shaw, Kirk Rice, Mitchell Charlesworth; Moore NI still "coming soon".
  About 80 estimate sites are JS or bot-walled and were not checked.

### wave6b_sector_deals: done (5 firms, 45 searches)
- Valid, no duplicates. MDW Capital Partners (debt), Horizon (horizontas.co.uk, Midlands, HQ null), sjl advisory
  (haulage), fds (Wakefield, EOT), DTE CF (Bury; press sources only, dte.co.uk bot-walled).
- **This segment is saturated:** ~7,000 deal articles parsed (business-sale.com, Business Live, bdaily, Comms Dealer,
  Car Dealer, IT Channel Oxygen); almost every adviser named is already listed.
- Absorbed (none of them is in the list; don't add): GS Verde -> AAB, Springboard -> BTG, Fellwood -> Cooper Parry,
  Beever and Struthers -> Menzies, IMAS -> MarshBerry, Spectrum -> FRP, Clarkson Hyde -> Affinia, Torr Waterfield ->
  Duncan & Toplis, Ensors -> Azets, Sagars -> AAB, Ashgates -> DJH, Carter Backer Winter -> Gravita; Bracebridge
  dormant (founder at Headpoint, listed); Oakley Advisory domain dead; WilliamsAli acquired 2024 (buyer unknown).
- Aliases: Orbis Partners = Clairfield UK; SRC CF = SRC Advisory; Kings Corporate / Business Buyers = Altius.
- No website found: Vertex Corporate (Manchester/Birmingham), Tide Advisory (Swansea), BPU (Wales).

### Round 1 lessons (seen 10-08)
- Press deal sweeps no longer pay (5 firms from ~7,000 articles). Directory APIs do: the Daltons Business agent
  directory (WordPress REST API, ~1,590 agents) gave most of the 25 niche brokers at no search cost.

## Round 2 (2026-10-08): started
- `wave6b_directories`: broker directories read by code (rest of Daltons agents, other listing-site agent lists).
- `wave6b_niche_gaps`: the niche sectors round 1 missed (IT/MSP, recruitment, agencies, insurance, opticians, funeral, travel, agri).

### wave6b_directories: done (33 firms, 1 search)
- Valid, no duplicates against the list or the other wave6b files. All from the Daltons agent directory (1,591
  agents; ~767 UK candidates after dedupe and redirect checks, screened by name and homepage wording, then confirmed
  on each firm's site). BusinessesForSale.com, Rightbiz, BizBuySell and Better Retailing return 403 (Cloudflare).
- Mostly general business transfer agents (26); 3 sell-side boutiques (Clarendon Square, Kingsbrook, EvolutionCBS);
  4 sector specialists (Alexander Mackie: garden centres; First Peninsula Marine; Addisons: estate agencies;
  Saville & Woods: post offices).
- Caveats for A: HQ null for The Business Sales Agency and DM Hall; Diverco HQ = registered office (Redditch).
  Independent Businesses For Sale belongs to Business Transfer Group (other brands may appear under other domains).
  Transworld UK facts via WebFetch (JS site). Sell My Small Business footer © 2016. DM Hall's email is from Daltons.
  Aliases confirmed already listed: hiltonsmythe.co.uk, business-partnership.co.uk, acquisitionsintl.com (Benchmark),
  vexus.org.uk, Sunaxis (= CFA Nottingham), MTBN (= AkenoMTBN).

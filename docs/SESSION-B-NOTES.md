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

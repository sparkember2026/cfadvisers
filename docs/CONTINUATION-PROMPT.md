# Continuation prompt (paste into a new Claude Code cloud session on sparkember2026/cfadvisers)

---

Continue building the UK corporate finance advisers directory in this repo (sparkember2026/cfadvisers).
Work on branch `claude/vibrant-gauss-w847ef`: fetch it and check it out. Commit and push to it often.

Read CLAUDE.md, README.md, docs/HANDOFF.md and docs/RECORD-FORMAT.md first. The app (API, web app, CLI,
PitchBook importer, website checker) is built and tested. The job now is the DATA: `data/advisers.jsonl`
has ~470 firms, and the goal is 600–900 UK CF advisers. The focus is firms doing £0.5–2m EBITDA (SME) deals.

1. Follow "How to continue" in docs/HANDOFF.md: regenerate `data/existing_firms.txt` from the merged list.
2. Web search is limited to ~200 calls per turn, shared by all agents running in that turn. Run research
   in rounds: each round starts 3–4 background research agents, each capped at ~45 WebSearch calls.
   - Each agent reads docs/research-briefs/common.md and round2.md, gets a segment from the "Known gaps /
     leads" list in HANDOFF.md, and writes only new firms to `data/research/wave3_<segment>.jsonl`.
   - Suggested segments, one per agent:
     (a) Scotland + Northern Ireland
     (b) Wales + South West + East of England
     (c) North East + Yorkshire + North West leads
     (d) UK members of M&A networks + accountancy-firm leads
     (e) London + South East small boutiques
     (f) sector specialists in the empty sectors
   - Check the wave2 files the last session left unfinished (networks_awards, london_se_east,
     sw_wales_scot_ni). Don't redo firms already in them.
3. After each round:
   - run `python -m cfadvisers merge --fresh`, then `validate`, then `pytest -q`;
   - look for the same firm under two domains; fix duplicates with `data/excluded.txt` or `data/overrides.jsonl`;
   - commit and push.
4. When the research rounds are done:
   - run `python -m cfadvisers check-sites --fill`; exclude dead firms or fix their URLs;
   - do a quality pass on records that rest on general knowledge;
   - update the stats in docs/HANDOFF.md and README.md;
   - check the web app in Playwright (Chromium at /opt/pw-browsers);
   - push.
5. Don't create a pull request unless I ask. Don't invent facts: unknown is null, and every estimate is
   marked `estimate`.

---

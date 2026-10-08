# Continuation prompt

**Short prompt to paste** into a new Claude Code cloud session (same pattern as scrape's): it points here, so the
instructions stay current on `main` without anyone editing the pasted text.

```
Work on the repo sparkember2026/cfadvisers. Read docs/CONTINUATION-PROMPT.md on main and follow the prompt inside it
exactly, as if I had pasted it. If I say you are "session B", follow docs/PARALLEL-SESSION-B.md instead.
```

Current numbers and the plan live in the top entry of docs/HANDOFF.md, not here, so this prompt stays valid.
The full prompt:

```
Continue the UK corporate finance advisers directory in this repo (sparkember2026/cfadvisers).
Work on the branch this session was given. First `git fetch origin main` and merge origin/main into it (main holds
the merged, latest work). Commit + push to your branch often; when a round is merged and tests pass, also push it to
main (`git push origin HEAD:main`, after merging origin/main). No PR unless I ask.

START, in this order:
1. Read CLAUDE.md, docs/SESSION-PLAYBOOK.md (how to run research here without losing work or running out of
   web searches), the top entry of docs/HANDOFF.md, and docs/RECORD-FORMAT.md.
2. pip install -r requirements.txt; python -m pytest -q; python -m cfadvisers merge --fresh (then git diff --stat:
   if the list changed, a previous session's last autosave was never merged; review it);
   python -m cfadvisers known --out data/existing_firms.txt
3. Keep-alive before research (playbook sections 1 and 4): start tools/autosave.sh 115 as a harness background task
   whenever agents run, and if you will work for more than ~2 hours, create the hourly revive Routine bound to this
   session; put its trigger id in HANDOFF; disable it when done.

THE JOB: the app is built. Grow and improve the DATA in data/advisers.jsonl (618 firms on 2026-10-07; see HANDOFF) towards
600-900 UK corporate finance advisers, with the focus on firms doing £0.5-2m EBITDA (SME) deals, and make the
records more accurate.

HOW (details in the playbook):
- Research in ROUNDS. Each round:
  - start 3-4 background agents (never more: web search is ~200 calls per turn shared by all agents), each
    with an explicit cap of ~45 WebSearch calls, one segment from HANDOFF "Next steps", its own output file
    data/research/wave<N>_<segment>.jsonl and its own scratch subdirectory;
  - each agent follows docs/research-briefs/common.md + round2.md;
  - in the same turn, start tools/autosave.sh 115 as a harness background task (run_in_background, timeout 7200000).
- After each agent reports back:
  - act on its caveats (data/excluded.txt, data/overrides.jsonl);
  - merge --fresh, validate, pytest -q;
  - check for the same firm under two domains;
  - commit, push.
  Then start the next round in a new turn, with known --out regenerated first.
- If the work will run longer than ~2 hours, create the hourly revive Routine described in playbook section 4.
  Put its trigger id in HANDOFF, and disable it when done.
- Code before agents: Companies House leads come from tools/ch_bulk.py (data/companies_house/bulk_candidates.jsonl);
  find and score their websites with curl first, and give agents only the hits to check.
- When the research rounds stop paying off (a round adds fewer than ~25 firms), switch to quality:
  - check-sites --fill;
  - the clean-up list in HANDOFF;
  - re-verify the "unverified" records;
  - upgrade estimated deal sizes using the firm's own wording.

RULES: never invent facts (unknown is null, estimates are marked "estimate", every record cites sources).
Keep docs/HANDOFF.md current (a new top entry), and add new lessons to docs/SESSION-PLAYBOOK.md as dated
observations. Before you stop, or when context runs long: update HANDOFF, push.
Finally, check the web app with Playwright (Chromium at /opt/pw-browsers), push, and republish the demo
(python -m cfadvisers build-static --out <scratch>/demo --embed; Artifact publish to
https://claude.ai/artifact/WqTi83zQdLHVdbKXErHeJm; only the main research session republishes it with data/advisers.json and icon.svg as files).
```

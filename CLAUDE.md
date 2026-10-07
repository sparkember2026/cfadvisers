# cfadvisers: notes for Claude sessions

A directory of UK corporate finance advisers (web app + API + CLI). Read README.md, docs/SESSION-PLAYBOOK.md (how to run research sessions without losing work: autosave, search
budget, Routines), the top entry of docs/HANDOFF.md (where the last session stopped), then docs/RECORD-FORMAT.md.
The prompt to start a new session is docs/CONTINUATION-PROMPT.md.

- The list is `data/advisers.jsonl`. Don't hand-edit it in bulk. Add research to `data/research/<batch>.jsonl`
  and run `python -m cfadvisers merge`. Records match on website domain, list fields are unioned, and
  scalar fields come from the fuller record. Hand corrections go in `data/overrides.jsonl`, which wins on
  every merge. Removals go in `data/excluded.txt`.
- Never invent facts. Unknown is null. Estimates must carry `*_basis: "estimate"`. Every record cites `sources`.
- Before pushing: `pytest -q` and `python -m cfadvisers validate`.
- The web app (`cfadvisers/static/app.js`) filters in the browser, using the same rules as `Store.query`.
  When you change a filter rule, change both, and the tests.
- Research agents never touch git; the main session runs `tools/autosave.sh` in the background and merges.
- PitchBook data is licensed: keep raw exports out of git (`data/pitchbook_raw/`).

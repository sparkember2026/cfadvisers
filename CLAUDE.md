# cfadvisers: notes for Claude sessions

A directory of UK corporate finance advisers (web app + API + CLI). Read README.md, docs/HANDOFF.md (where the last session stopped), then docs/RECORD-FORMAT.md.

- The list is `data/advisers.jsonl`. Don't hand-edit it in bulk. Add research to `data/research/<batch>.jsonl`
  and run `python -m cfadvisers merge`. Records match on website domain, list fields are unioned, and
  scalar fields come from the fuller record. Hand corrections go in `data/overrides.jsonl`, which wins on
  every merge. Removals go in `data/excluded.txt`.
- Never invent facts. Unknown is null. Estimates must carry `*_basis: "estimate"`. Every record cites `sources`.
- Before pushing: `pytest -q` and `python -m cfadvisers validate`.
- The web app (`cfadvisers/static/app.js`) filters in the browser, using the same rules as `Store.query`.
  When you change a filter rule, change both, and the tests.
- PitchBook data is licensed: keep raw exports out of git (`data/pitchbook_raw/`).

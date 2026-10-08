# Parallel session B: brief

Session B runs alongside the main session (session 3, branch `claude/eager-newton-30tnay`) to use its own web-search
allowance (~200 WebSearch calls per turn, shared by the agents running in that turn). The two sessions split the
work so that they never edit the same file.

## Who owns what
| | main session (A) | session B |
|---|---|---|
| branch | `claude/eager-newton-30tnay` | the branch B's session was given (B writes its name at the top of its notes file) |
| work | Companies House leads (`data/companies_house/bulk_candidates.jsonl`): websites by code, then checks | the web-search segments below |
| writes | `data/advisers.jsonl`, `data/overrides.jsonl`, `data/excluded.txt`, `docs/HANDOFF.md`, `data/research/wave6a_*` | only **new** files: `data/research/wave6b_<segment>.jsonl`, `data/research/wave6b_proposals.jsonl`, `docs/SESSION-B-NOTES.md` |
| merges | yes: fetches B's branch and merges B's files | **never** commits `data/advisers.jsonl`, `data/overrides.jsonl`, `data/excluded.txt` or HANDOFF |

B never publishes the claude.ai demo page and never pushes to `main`; session A does both.
B may run `python -m cfadvisers merge --fresh` locally to check duplicates, but then runs
`git checkout -- data/advisers.jsonl` before committing. Start B's autosave as usual (`tools/autosave.sh 115` as a
harness background task); it only commits files B changed.

**Skip:** firms already in `data/existing_firms.txt`, and companies listed in
`data/companies_house/bulk_candidates.jsonl` (session A is checking those). If B finds one of them anyway, add it:
the merge dedupes on domain.

## Segments for B (one agent each, at most 3 at a time, each capped at ~45 WebSearch calls)
1. **`wave6b_sector_deals`: advisers on SME deals in under-covered sectors.** Automotive, logistics and haulage,
   construction and civil engineering, engineering and manufacturing, facilities management, security, waste and
   recycling, telecoms, and building services. Search 2024–26 deal announcements of £2–15m EV ("advised the
   shareholders of", "acted as lead adviser", "sale of" + sector + town). Record the **adviser**, not the target.
   Rounds 1–4 found press sweeps slow (one new adviser per 100–200 articles), so prefer pages that list many deals:
   trade press deal round-ups, sector M&A reports, and advisers' own credentials pages.
2. **`wave6b_niche_brokers`: specialist brokers and exit advisers for owner-managed businesses** not covered yet:
   opticians, funeral directors, hotels and pubs, IT/MSP, recruitment agencies, digital and creative agencies,
   IFA and wealth books, insurance brokers, travel agencies, franchise resales, and agricultural businesses. Keep
   only firms that act on sales (sell-side or buy-side), with a UK office and a working website.
3. **`wave6b_quality`: checks on existing records (few searches; mostly fetching firms' own sites).** Write results to
   `data/research/wave6b_proposals.jsonl` (format below), not to records:
   - the "Review list from the register" in the top entry of `docs/HANDOFF.md` (liquidations, strike-off
     proposals, renamed companies): is the firm still trading, under which name and site?
   - records whose description says "unverified" or that cite only the homepage;
   - estimated deal sizes (`deal_size_basis: "estimate"`) where the firm's own site states a size or names deals:
     propose the stated figures with the quote and URL;
   - the weak-evidence records listed in HANDOFF (round 4: Sunset Capital, Stoneward, LuxCap, Cogito, Pinpoint,
     Onward, Eleven Advisory; round 3: Sterling CF, Avero, Barrons).

## Proposals format (`data/research/wave6b_proposals.jsonl`)
One JSON object per line. Session A reviews each one before applying it.
```json
{"action": "override", "id": "<record id>", "fields": {"deal_ev_min_m": 2, "deal_ev_max_m": 15, "deal_size_basis": "stated", "deal_size_note": "\"typically £2m-£15m\""}, "reason": "firm's own wording", "sources": ["https://..."]}
{"action": "exclude", "id": "<record id>", "reason": "in liquidation since 2026-03; site down", "sources": ["https://find-and-update.company-information.service.gov.uk/company/..."]}
```

## Rules (same as every session)
Never invent facts: unknown is null, estimates carry `*_basis: "estimate"`, every record cites `sources`. Agents
follow `docs/research-briefs/common.md` + `round2.md`, use their own scratch subdirectory and their own output file,
and validate with `python -m cfadvisers validate <file>`. Agents never touch git; the session's autosave pushes.
Before stopping, B updates `docs/SESSION-B-NOTES.md` (branch name, what each agent did, numbers, caveats) and pushes.

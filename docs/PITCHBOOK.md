# What to ask Joel for (PitchBook)

PitchBook records the advisers on each deal. That gives us something the web research can't: **who
actually closes SME deals and how often**. It also turns up active advisers we haven't found yet.

## The export
In PitchBook, **Deals** search:

| filter | value |
|---|---|
| Company location (HQ) | United Kingdom |
| Deal type | M&A (merger/acquisition, buyout/LBO, MBO, MBI, secondary buyout, corporate acquisition) and PE growth/expansion |
| Deal date | last 5 years (e.g. 01/01/2021 – today) |
| Deal status | Completed |
| Deal size (optional) | ≤ £100m, or leave it blank; many SME deals have no disclosed size, so don't filter them out |

Columns to include in the export (names as PitchBook shows them; any extra columns are fine):
- Deal ID, Companies, Deal Date, Deal Type, Deal Size (choose GBP), Company EBITDA (or EBITDA) at deal,
  Revenue at deal (if offered)
- **Service Providers**, or the separate adviser columns (**Lead Advisors / Advisors (Seller) /
  Advisors (Buyer) / Advisors (Company)**). These are the important ones.

Export to Excel or CSV. If the row limit bites, split the export by year.

## Loading it
```
python -m cfadvisers pitchbook path/to/export.xlsx --note "UK M&A 2021-2026, completed"
python -m cfadvisers serve      # PitchBook stats now show on each adviser; sort by "Most PitchBook deals"
```
This writes:
- `data/pitchbook_stats.json`: for each adviser in our list, the deal count, deals in the £0.5–2m EBITDA
  band (EBITDA if given, else deal size ÷ 5), median deal size, last deal and recent deals.
- `data/pitchbook_unmatched.csv`: advisers named in the export who are **not in our list yet**, sorted
  by deal count. Go through the top of it and add the real CF advisers (most of the rest will be lawyers
  and DD providers that slipped through). Add them as research batch lines (`docs/RECORD-FORMAT.md`), or as
  `data/overrides.jsonl` lines with name + website + firm_type + sources, then run `python -m cfadvisers merge`.

PitchBook's licence restricts redistribution. Keep the raw export out of git (`data/pitchbook_raw/` is
git-ignored) and check before showing per-deal PitchBook data to founders outside the firm. The
aggregate counts are lower risk, but check those too.

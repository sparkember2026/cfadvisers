# What to ask Joel for (PitchBook)

## Message to send Joel (updated 2026-10-08)
> Hi Joel, we've built a directory of UK corporate finance advisers, focused on the ones who do SME deals
> (£0.5–2m EBITDA, roughly £2–15m EV): https://sparkember2026.github.io/cfadvisers/ (704 firms, each with
> sources). The weak spot is deal size: for about 4 in 5 firms it's an estimate from their website, not evidence of
> deals they've actually done. PitchBook records the advisers on each deal, so it would fix that.
>
> Could you run one export from PitchBook, please?
> **Deals search:** company HQ United Kingdom; deal types M&A, buyout/LBO, MBO/MBI, secondary buyout,
> corporate acquisition and PE growth/expansion; deal date 1 Jan 2021 to today; status Completed; no deal-size
> filter (most SME deals have no disclosed size). Columns: Deal ID, Companies, Deal Date, Deal Type,
> Deal Size (GBP), EBITDA at deal, Revenue at deal, and above all **Service Providers** (or the Lead
> Advisors / Advisors (Seller) / Advisors (Buyer) columns). Excel or CSV; split by year if it hits the row limit.
>
> **Optional, if quick:** a Service Providers search for advisory firms (M&A / corporate finance advisers)
> located in the UK, with name, website, HQ and number of deals.
>
> Please send the file to Adam rather than posting it anywhere: it stays out of the public repo and we'll
> only publish per-firm totals, after checking that's fine under the licence. Thanks!

**When the file arrives:** put it in a session (upload it, or drop it in `data/pitchbook_raw/`, which git
ignores) and ask Claude to run `python -m cfadvisers pitchbook <file>`. What it adds is below.

## Why it matters (2026-10-08)
- 704 firms; 550 (78%) of deal sizes are estimates (`deal_size_basis: "estimate"`), so the £0.5–2m filter
  rests mostly on how firms describe themselves.
- Research by web search is close to exhausted; PitchBook's deal records are the best remaining way to
  confirm who really does SME deals and to find active advisers we have missed.

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
python -m cfadvisers serve      # PitchBook stats show on each adviser; the "Most PitchBook deals" sort appears once data is loaded
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

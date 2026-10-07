# Adviser record format

One JSON object per line in `data/advisers.jsonl` (and in the research batches under `data/research/`).
`schemas/adviser.schema.json` is the machine-checked version; `python -m cfadvisers validate` checks the file.

Unknown values are `null` (or `[]`), never guessed. Estimates are allowed only where the field says so,
and must be marked with the `*_basis` field.

| field | type | meaning |
|---|---|---|
| `name` | string | trading name of the firm (e.g. "Cooper Parry Corporate Finance" -> "Cooper Parry") |
| `website` | string | homepage URL, `https://...` |
| `firm_type` | enum | see below |
| `parent` | string/null | group or network the CF team sits in (e.g. "Azets", "Moore Global") |
| `hq` | string | city of head office (UK city, or a non-UK city for global firms) |
| `hq_region` | enum | UK region of the HQ (see regions), or `"International"` |
| `offices` | [string] | UK cities with an office that does CF work (include HQ) |
| `coverage` | enum | `national` / `regional` / `local` / `international` |
| `regions_covered` | [enum] | UK regions they actively cover (all 12 if national) |
| `cf_professionals` | int/null | number of corporate finance / M&A deal professionals in the UK |
| `cf_professionals_basis` | enum/null | `stated` (firm says it), `team_page` (counted on the team page), `estimate` |
| `deal_ebitda_min_m` | number/null | lower end of core deal size, EBITDA, £m |
| `deal_ebitda_max_m` | number/null | upper end of core deal size, EBITDA, £m |
| `deal_ev_min_m` | number/null | lower end of core deal size, enterprise value, £m |
| `deal_ev_max_m` | number/null | upper end of core deal size, enterprise value, £m |
| `deal_size_basis` | enum/null | `stated` (firm publishes it), `deals` (inferred from its published deals), `estimate` |
| `deal_size_note` | string/null | the firm's own words, e.g. "deals from £2m to £50m" |
| `services` | [enum] | `sell_side`, `buy_side`, `mbo`, `fundraising`, `debt_advisory`, `due_diligence`, `valuations`, `ecm`, `restructuring` |
| `sectors` | [string] | sectors from the sector list below |
| `sector_note` | string/null | free text, e.g. "specialises in dental and veterinary practices" |
| `contact_email` | string/null | general CF/enquiries email published on the site |
| `contact_phone` | string/null | main phone number |
| `team_url` | string/null | page listing the CF team (with their contact details if possible) |
| `contact_url` | string/null | contact page |
| `linkedin_url` | string/null | company LinkedIn page |
| `description` | string | one or two sentences: who they are, what deals they do |
| `sources` | [string] | URLs the facts came from (at least one) |

## firm_type
- `independent_boutique`: independent CF/M&A adviser, generalist across sectors
- `sector_specialist`: CF/M&A adviser focused on one or a few sectors
- `accountancy_cf`: accountancy firm with a corporate finance team
- `big4`: Deloitte, PwC, EY, KPMG
- `investment_bank`: mid-market / international investment bank or broker with M&A advisory (incl. AIM brokers)
- `business_broker`: sells owner-managed businesses, often with retainer-led marketing (e.g. Christie & Co, Benchmark International)
- `debt_advisory`: debt / funding adviser (primarily debt, not M&A)
- `law_firm`: only if the law firm itself runs a CF advisory arm (rare; corporate lawyers are not advisers)

## Regions (`hq_region`, `regions_covered`)
`London`, `South East`, `South West`, `East of England`, `East Midlands`, `West Midlands`,
`Yorkshire and the Humber`, `North West`, `North East`, `Scotland`, `Wales`, `Northern Ireland`

## Sectors
`Business Services`, `Technology & Software`, `Healthcare`, `Life Sciences`, `Consumer & Retail`,
`Food & Beverage`, `Leisure & Hospitality`, `Industrials & Manufacturing`, `Engineering`,
`Construction & Property`, `Financial Services`, `Professional Services`, `Media & Marketing`,
`Education`, `Energy & Renewables`, `Transport & Logistics`, `Automotive`, `Agriculture`,
`Recruitment & Staffing`, `Care`, `Dental & Veterinary`, `Pharmacy`, `Telecoms`, `Facilities Management`,
`Environmental Services`, `Distribution & Wholesale`, `Charity & Public Sector`, `Generalist`

## Deal size: how to fill it
The question users ask is "does this firm do £0.5m–£2m EBITDA deals?" so the deal size fields matter most.
- If the firm states a size (EV, EBITDA, turnover, or "deal values"), copy their words to `deal_size_note`
  and fill the matching EV or EBITDA fields; `deal_size_basis = "stated"`.
- If it only lists deals, read a few and give a range; `deal_size_basis = "deals"`.
- Otherwise estimate from what the firm is (a 3-person regional boutique selling owner-managed businesses
  is roughly £1–15m EV; a Big 4 team is £50m+), `deal_size_basis = "estimate"`.
- Do not convert between EV and EBITDA yourself: the app does that (EV = EBITDA x 5 by default).

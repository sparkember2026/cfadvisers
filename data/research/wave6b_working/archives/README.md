# Session B archives

`site_crawls_and_daltons.tgz` (12 MB) holds raw working data from session B (2026-10-08):
- `quality/crawl`, `quality/crawl2`: text of 504 adviser websites, crawled two levels deep (one JSON per firm id).
- `quality/pages`: further pages fetched for the deal-size proposals. `quality/patched.jsonl` is a scratch copy of
  the list with all proposals applied, used to validate them; it is not the list.
- `directories/hp`: homepage text of the screened broker candidates.
- `directories/dalt_all.json`: the Daltons Business agent directory (1,591 agents), from its public WordPress REST API.

Not kept: ~1.9 GB of raw press article HTML and its extracted text (third-party articles, not ours to republish).
The article URL lists and the adviser names extracted from them are in `../sector_deals/`.

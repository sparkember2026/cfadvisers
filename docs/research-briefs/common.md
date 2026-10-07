You are researching UK corporate finance (M&A) advisers for a directory. The end user is a PE investor who wants to map all UK CF advisers, especially those doing SME deals (£0.5m-£2m EBITDA, i.e. roughly £2m-£15m enterprise value), to build deal-flow relationships and to give the list to founders.

Read /home/user/cfadvisers/docs/RECORD-FORMAT.md first: it defines the exact JSON record format, enums, regions and sector list. Follow it exactly.

Method:
- Build a candidate list of firms in YOUR SEGMENT (below) from your own knowledge AND from web searches (WebSearch), e.g. league tables (Experian MarketIQ, Insider Media / Dealmakers deal tables, Pitchbook league tables), regional deal awards shortlists (Insider Media Dealmakers awards, ACG UK awards, M&A Today), the ICAEW Corporate Finance Faculty, "corporate finance <city>" searches, Mergermarket/press deal announcements naming advisers.
- For each firm, check its own website (WebFetch, or `curl -sL --max-time 20` via Bash; the network works) for: offices, team page (count CF deal professionals), deal size wording, sectors, contact email/phone, team/contact URLs. Prefer facts from the firm's own site; put every URL you used in `sources`.
- Do not invent: null when unknown. Estimates only where RECORD-FORMAT allows, marked `estimate`.
- Only firms that are UK-based or have a UK CF team. Firm must be currently active (skip firms that have closed or been absorbed; if absorbed, the acquirer is the record).
- Breadth matters more than perfection: aim for the target count; spend ~2-4 tool calls per firm, less for obvious ones. Big well-known firms can be filled mostly from knowledge plus one page check.

Rules for parallel agents (docs/SESSION-PLAYBOOK.md):
- WebSearch is a shared budget (~200 per turn for ALL agents): stay within the cap your segment gives you (default ~45).
- Use your own scratch subdirectory (scratchpad/<your segment>/); other agents share the scratchpad.
- Only write your own output file. Never delete records because you think another agent's segment covers them: the merge dedupes by website.
- Validate your file with `python -m cfadvisers validate <your file>`.
- Don't put guesses (e.g. an HQ city you weren't able to confirm) in a record: null, and say so in your report.

Output: write records as JSON Lines (one compact JSON object per line) to the output file named below. APPEND as you go (every ~10 firms) so work isn't lost: e.g. use python to append. At the end, validate every line parses as JSON and has name+website+firm_type, and report the count and any notable data-quality caveats in your final message (keep the final message short: count, file, caveats). Do not create other files in the repo, and do not touch git.

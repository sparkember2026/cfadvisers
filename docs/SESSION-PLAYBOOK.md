# Session playbook: running research in a Claude cloud session

What we've learned so far about running long AI research in a Claude Code cloud session. Every session
reads this. When you learn something new, add it as a dated observation ("seen 10-07: …"); don't just pile
on rules. Some lessons were observed here (cfadvisers, session 1, 2026-10-07). Others come from the sister
repo sparkember2026/scrape (`docs/KEEP-RUNNING.md`, 10-05 to 10-07), which ran unattended queue runners for days.

## 1. What loses work (observed)
| failure | what happens | remedy |
|---|---|---|
| **Container reclaimed when idle** | A cloud container lives only while the session is *working*: a turn, or a harness-tracked background task (Bash `run_in_background`, or a background Agent). About 5 min after it goes idle it is reclaimed, and everything unpushed is lost. Having the app open doesn't count. (scrape, 10-05..07) | Push often. Run `tools/autosave.sh` as a harness background task while agents work (section 3). |
| **Container restart** | Happens without warning (3 times in one day on scrape, 10-07). Kills background tasks and agents. | Push often. For multi-hour runs, use an hourly Routine bound to the session (section 4). |
| **2 h background-task cap** | A harness background task is stopped after 2 h (`timeout` max 7200000). | When autosave ends you get a notification: re-run it if agents are still working. |
| **`nohup` / `setsid` doesn't count** | Detached processes don't keep the container alive. Only harness-tracked tasks do. | Never use `nohup` for keep-alive or autosave. |
| **Agents write only locally** | Background research agents append to `data/research/*.jsonl` but don't touch git (by design: parallel agents doing git would collide). Their work exists only in the container until the main session commits it. | `tools/autosave.sh` commits and pushes `data/research/` every 5 min. |
| **Stop hook on dirty tree** | The harness's "uncommitted changes" stop hook fires at the end of every turn while agents are writing. Each one costs a turn. | Same autosave. It also keeps the tree clean between turns. |

| **Two sessions on one branch** | Seen 10-07: the owner opened the next session while this one's autosave was still running. Pushes were then rejected (non-fast-forward). | `tools/autosave.sh` now runs `pull --rebase --autostash` before each push. The old session should stop its autosave and stand down once the new one has started. |

## 2. Web search budget: the real constraint on research (observed here, 10-07)
- **WebSearch is capped at about 200 calls per turn, shared by every agent running in that turn.** That's
  per turn, not per agent and not per session. Round 1 launched 8 agents at once: the budget ran out
  after roughly 15–30 searches each, and every segment came in at 20–60% of its target. Round 2 (5 agents,
  about 35 searches each) came in under target too.
- So:
  - Run **3–4 research agents per turn**, and give each an explicit cap ("use at most ~45 WebSearch calls").
  - Run **several rounds** (several turns) rather than one wide fan-out. Each new turn appears to get a
    fresh allowance; a new session certainly does.
  - Tell agents to prefer searches that return **pages listing many firms** (league tables, award
    shortlists, network member lists), then verify each firm by fetching its own site.
  - **Direct fetches don't use the search budget:** `curl` and WebFetch on a firm's own website, and
    Companies House name search
    (`https://find-and-update.company-information.service.gov.uk/search/companies?q=...`).
- **Sources that work:** firms' own websites; Companies House; Experian MarketIQ regional adviser league
  tables (PDFs); Firmbase lists; Acumon city guides; Scottish Financial News; the ICAEW CF Faculty
  member list; thecfn.org.uk members; the MGI directory; the r.jina.ai reader proxy for some blocked pages.
- **Sources that block automated access:** Insider Media (Dealmakers shortlists, deal tables),
  TheBusinessDesk (captcha after a few hits), ICAEW Find, the Experian report forms, Business Magazine,
  Axial, Business News Wales, and DuckDuckGo/Bing/Google via curl. Don't spend effort routing around them.
- **Diminishing returns:** the second round found about 100 new firms against about 400 in the first.
  The obvious names are already in the list. What's left is small firms (1–5 people) that don't show up
  in searches. Most new firms will come from PitchBook (`docs/PITCHBOOK.md`) and from small-firm sources
  (Companies House "corporate finance" names checked against a working website).

- **Two different limits; don't confuse them** (seen 10-07, from the session list's `rate_limit_info`):
  1. **The web-search cap** (~200 per turn, shared by the agents in that turn) belongs to one session.
     Another session (another chat tab) has its own, so parallel sessions do add search capacity.
  2. **The account usage limit** (`rate_limit_info.rateLimitType: "seven_day"`, with a `resetsAt` time)
     is shared by every session on the account, this repo's and scrape's alike. Extra tabs don't add to
     it; they use it up faster. On 10-07 every session showed `status: "rejected"`, resetting
     12 Oct 18:00 UTC.
  - **Rule:** open a parallel session only for search-bound work, and only when the weekly limit has
    room. Give each session its own research segment and batch file. Exactly one session merges into
    `data/advisers.jsonl` and edits HANDOFF.
  - **What a session can see:** `mcp__claude-code-remote__list_sessions` (mine: true) shows each live
    session's status, branch, cost, context use and the shared weekly limit. It does not show remaining
    web searches; no tool does.

## 3. The research loop (what worked)
1. `python -m cfadvisers merge --fresh && python -m cfadvisers known --out data/existing_firms.txt`. Agents
   dedupe against this file.
2. Start **3–4 background agents** (Agent tool, `run_in_background: true`).
   - Each reads `docs/research-briefs/common.md` plus the current round brief.
   - Each gets **one non-overlapping segment** (region x firm type, or a named lead list), a search cap,
     and **its own output file** `data/research/<round>_<segment>.jsonl`.
   - Each gets **its own scratch subdirectory**. Seen 10-07: agents sharing one scratchpad overwrote
     each other's working files.
   - Each validates with `python -m cfadvisers validate <its file>`.
3. In the same turn, start `tools/autosave.sh` as a harness background task (Bash, `run_in_background:
   true`, `timeout: 7200000`). It keeps the container busy and pushes the agents' output every 5 minutes,
   at no model cost.
4. When each agent reports back:
   - act on its caveats right away (`data/excluded.txt` for absorbed or closed firms, `data/overrides.jsonl`
     for corrections);
   - merge, run `validate` and `pytest -q`, commit and push.

   Gate commits on the real exit code: `pytest -q && python -m cfadvisers validate && git commit ...`. Seen 10-07:
   `pytest -q | tail -1 && git commit` committed a failing test, because the pipe returns tail's exit code.

   Agents spot absorbed firms well (e.g. Lexington → FRP, Peterhouse → AlbR, Moore South → Moore Kingston Smith).
   Act on what they report.
5. **Dedupe check after every merge.** The same firm can come in under two domains, or under a network
   path such as Carlsquare and Carlsquare UK. Compare normalised names
   (`cfadvisers.pitchbook.norm_name`) and exclude the weaker record.
6. Segment overlaps between agents are normal. Merge handles them by domain, keeping the fuller record
   and unioning the list fields. So don't tell agents to delete records they think belong to another
   segment. Seen 10-07: two accountancy agents each deleted about 20 records believing the other one had
   them.

## 4. Routines, reminders and keep-alive
- **Background agents and background Bash both keep the container alive while they run**, and their
  completion wakes the session. For a single 1–2 hour research round that's all you need, plus autosave.
- **For long multi-round runs**, add an hourly **Routine** bound to this session (claude-code-remote
  `create_trigger`):
  - `cron_expression: "0 * * * *"`, no `persistent_session_id`, no `create_new_session_on_fire`;
  - `initiation: human_request` only if the owner asked for it;
  - prompt: "Hourly revive: cd /home/user/cfadvisers; if no autosave background task is running, start
    `tools/autosave.sh 115` as a background task; check data/research line counts; if no research agents
    are running and the round is finished, merge/validate/push and start the next round per
    docs/HANDOFF.md".

  Routines live on the platform, so they survive container restarts and wake the session in a new
  container. Write the trigger id into HANDOFF, and **disable it when done**
  (`update_trigger(enabled=false)`). Don't leave Routines firing into a session nobody uses.
- **One-off follow-ups:** `send_later(delay_minutes=N, message=...)`, e.g. "check whether the round 3
  agents finished". It also survives restarts.
- **Cost:** autosave and keep-alive scripts use no tokens. A Routine costs one short turn per firing.

## 5. Handover
- Sessions end without warning, so **anything not pushed is lost**. Before stopping, or when context is
  long:
  - update `docs/HANDOFF.md` (numbers, unfinished agents, exclusions, leads);
  - update `docs/CONTINUATION-PROMPT.md` if the plan changed;
  - push.
- **Agents still running at handover:** say so in HANDOFF, and treat their segments as unfinished. Their
  output after the last push is lost when the session goes away.
- Keep stats in one place (HANDOFF), so the continuation prompt doesn't go stale.

## 6. Data quality habits
- Unknown is null. Estimates carry `*_basis: "estimate"`. Every record cites `sources`.
- Agents are good at:
  - spotting absorbed or merged firms;
  - finding a firm's own size wording;
  - counting team pages.
- Agents are weaker at:
  - **head-office location** when the site blocks automated reads. They fall back on brief hints, so
    don't put guesses in briefs. Seen 10-07: Clearwater's "Birmingham" HQ came from my brief.
  - **office lists for national firms.**
- About 85% of deal sizes are estimates. The best upgrade is PitchBook deal data, then the firm's own wording.

## 7. Observations from session 2 (10-07)
- Seen 10-07: the `pytest` on PATH is a different interpreter without fastapi. Use `python -m pytest -q`.
- Seen 10-07: the previous session was still pushing to the same branch after the new one started. Pull with
  `--rebase` before pushing (autosave now does this). When a script changes under a running bash loop
  (autosave.sh), stop and restart it.
- Seen 10-07: `check-sites --fill` used to be lost on the next `merge --fresh`. Now merge re-applies fills from
  `data/site_checks.jsonl`. Run `check-sites` (no `--fill` needed), then merge.
- Seen 10-07, round 3: the regional sources are exhausted. Four agents found about 55 new firms, 30 of them from
  the Companies House advanced search (active companies, name terms, finance SIC codes) plus guessing
  websites from names and fetching them with curl. That costs no search budget, so it scales.
- Seen 10-07: r.jina.ai rate-limits per IP. Leave about 4-5 seconds between calls.

## 8. Observations from session 3 (10-07, eager-newton)
- Seen 10-07: **Companies House bulk data needs no API key, no Pixel and no web searches.** The monthly Basic
  Company Data zip (471 MB) downloads from the cloud container in under a minute, and `tools/ch_bulk.py` scans all
  5.5m companies in about 2 minutes. Prefer it to the public advanced search for anything list-shaped.
- Seen 10-07: **the firm's own site is the best identity proof.** 236 of 618 sites print a company number
  (homepage, contact or privacy page). Check it against the register *and* the name: some sites print a company
  secretary's or sister firm's number, and a loose pattern catches GPhC/FCA/VAT numbers.
- Seen 10-07: exact-name matches alone are not identity. "Qiao Ltd" (strike-off) is a namesake of our Qiao
  Capital Advisors. Keep name-only matches as review leads; auto-resolve only with HQ town agreement.
- Seen 10-07: the register catches research errors cheaply: S&W's record pointed at sw.co.uk, which is
  Sanderson Weatherall.
- Seen 10-07: the last autosave of a session can land after its HANDOFF entry. Start every session with
  `merge --fresh` and a diff of ids against the committed list, and review what changed.
- Seen 10-07: a **claude.ai Artifact** is the quickest shareable demo (`build-static --embed`): private until
  shared, same URL on republish. It can't host the API, and blocks downloads and service workers.
- Seen 10-07: this session ran with the weekly account limit already "rejected" (resets 12 Oct 18:00 UTC), on
  extra-usage credit. A parallel session would spend the same credit. Open one only for search-bound work.
- Seen in scrape (10-06): `claude -p` with Haiku to guess company domains cost ~$0.0005 a company but only 1 in
  187 guesses on the real gap was provable. Code-only domain guessing plus a register or site check did better.
- Seen 10-08: a parallel session started with the short prompt but without the "you are session B" line behaved as a
  main session until told. Roles that live in one pasted line are fragile; a claimable task list in the repo (scrape's
  `tools/tasks.py` pattern) is the planned fix. Until then, check a new parallel session's first prompt
  (`list_events`, kinds user) and `send_message` it if needed.
- Seen 10-08: session B used ~136 web searches over 2 rounds for 72 firms; the Daltons agent directory (read by code)
  gave 33 of them with 1 search. Directory-by-code beats search-by-agent here too.

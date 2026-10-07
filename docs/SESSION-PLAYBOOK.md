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

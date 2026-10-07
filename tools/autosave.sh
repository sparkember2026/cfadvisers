#!/usr/bin/env bash
# Autosave research while background agents work: every 5 min, commit data/research/ (and data/*.jsonl,
# data/excluded.txt) and push to the session branch, at no model cost.
# Run it as a HARNESS background task (Bash tool, run_in_background: true, timeout 7200000), NOT with nohup:
# only harness-tracked tasks keep a cloud container alive; it is reclaimed a few minutes after the session goes idle,
# and anything unpushed is lost. The harness stops a background task after 2 h: when this ends, re-run it.
# Usage: tools/autosave.sh [minutes, default 115] [branch, default: current branch]
MIN=${1:-115}
cd "$(dirname "$0")/.." || exit 1
BRANCH=${2:-$(git rev-parse --abbrev-ref HEAD)}
end=$(( $(date +%s) + MIN * 60 ))
while [ "$(date +%s)" -lt "$end" ]; do
  sleep 300
  git add data/research data/overrides.jsonl data/excluded.txt 2>/dev/null
  if ! git diff --cached --quiet; then
    n=$(cat data/research/*.jsonl 2>/dev/null | wc -l)
    git commit -qm "autosave: research batches ($n lines)" >/dev/null 2>&1
    for t in 1 2 3 4; do git push -q origin "HEAD:$BRANCH" >/dev/null 2>&1 && break; sleep $((t*2)); done
    echo "$(date -u +%H:%M) saved, $n research lines"
  else
    echo "$(date -u +%H:%M) no change"
  fi
done
echo "autosave ended: re-run tools/autosave.sh as a background task if agents are still working"

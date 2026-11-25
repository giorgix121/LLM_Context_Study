#!/usr/bin/env bash
# Second round of follow-ups on the frozen main sample (146 cases), Nov 2026:
#   E4  commit-message level M0 = S0 + the target commit's message, for the two original models
#   E5  two more models on S0-S4, N2 and M0, plus identical S0/S2 re-runs:
#       qwen/qwen3.8-flash (cheap current small model) and anthropic/claude-sonnet-4.6 (larger sibling of Haiku 4.5)
# Claude 5.x and GPT-6.x were not used: their endpoints do not accept temperature, which the protocol fixes at 0.
# Project-wide cap $26 (all results/*/attempts.jsonl count toward it; $13.22 spent before this script).
set -uo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
STUDY=main
CAP=26
GEMINI=google/gemini-2.5-flash-lite@ai-studio
HAIKU=anthropic/claude-haiku-4.5
QWEN=qwen/qwen3.8-flash
SONNET=anthropic/claude-sonnet-4.6
ALL=S0,S1,S2,S3,S4,N2,M0
OUT="results/$STUDY"
mkdir -p "$OUT"
exec > >(tee -a "$OUT/models2.log") 2>&1
stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }

paid() {  # model levels repeat; waits and resumes after transient halts (exit 4)
  local code=1
  for attempt in 1 2 3 4; do
    $PY experiment.py --study "$STUDY" run --model "$1" --levels "$2" --repeat "$3" --max-cost "$CAP" --execute
    code=$?
    echo "=== $(stamp) $1 levels=$2 repeat=$3: exit code $code (0 ok, 2 halted, 3 not reconciled, 4 transient)"
    [ "$code" -eq 4 ] || return 0
    sleep 600
  done
}

echo "=== $(stamp) START models2 study=$STUDY cap=\$$CAP"
$PY experiment.py selftest | tail -1
$PY experiment.py --study "$STUDY" prepare | tail -1  # offline: message.json per case (already built)
paid "$GEMINI" M0 1
paid "$HAIKU" M0 1
paid "$QWEN" "$ALL" 1
paid "$QWEN" S0,S2 2
paid "$SONNET" "$ALL" 1
paid "$SONNET" S0,S2 2
for spec in "$GEMINI 1" "$HAIKU 1" "$QWEN 1" "$QWEN 2" "$SONNET 1" "$SONNET 2"; do
  set -- $spec
  $PY experiment.py --study "$STUDY" report --model "$1" --repeat "$2" | tail -1
done
echo "=== $(stamp) DONE"

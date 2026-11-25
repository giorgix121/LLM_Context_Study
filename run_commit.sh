#!/usr/bin/env bash
# Third round of follow-ups on the frozen main sample (146 cases), Nov 24, 2026: the rest of the commit.
#   C0  S0 + the diffs of the other files changed by the target commit (same question about the target file)
#   J0  the whole commit diff with the question asked about the commit (the usual just-in-time setup)
# for the four models of the study; Gemini through AI Studio, as in the other follow-ups.
# Project-wide cap $33 (all results/*/attempts.jsonl count toward it; $23.46 spent before this script;
# the pipeline's own estimate for this script is $8.50).
set -uo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
STUDY=main
CAP=33
GEMINI=google/gemini-2.5-flash-lite@ai-studio
HAIKU=anthropic/claude-haiku-4.5
QWEN=qwen/qwen3.8-flash
SONNET=anthropic/claude-sonnet-4.6
LEVELS=C0,J0
OUT="results/$STUDY"
mkdir -p "$OUT"
exec > >(tee -a "$OUT/commit.log") 2>&1
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

echo "=== $(stamp) START commit study=$STUDY cap=\$$CAP"
$PY experiment.py selftest | tail -1
$PY experiment.py --study "$STUDY" prepare | tail -1  # commit.json per case (GitHub responses are cached)
paid "$GEMINI" "$LEVELS" 1
paid "$QWEN" "$LEVELS" 1
paid "$HAIKU" "$LEVELS" 1
paid "$SONNET" "$LEVELS" 1
for model in "$GEMINI" "$QWEN" "$HAIKU" "$SONNET"; do
  $PY experiment.py --study "$STUDY" report --model "$model" --repeat 1 | tail -1
done
echo "=== $(stamp) DONE"

#!/usr/bin/env bash
# Follow-up experiments on the frozen main sample (146 cases), run after run_main.sh:
#   E1  second model: anthropic/claude-haiku-4.5 on S0-S4 (S5 would cost ~$18 for this model and is not run)
#   E2  length control N2 = S0 + unrelated code of exactly S2's added length, for both models
#   E3  identical re-runs of S0 and S2 (run-to-run stability), for both models
# Gemini runs go to Google AI Studio: the google-vertex endpoint used by run_main.sh is no longer offered.
# Project-wide cap $16 (all results/*/attempts.jsonl count toward it); cached requests are never paid twice.
set -uo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
STUDY=main
CAP=16
GEMINI=google/gemini-2.5-flash-lite@ai-studio
HAIKU=anthropic/claude-haiku-4.5
OUT="results/$STUDY"
mkdir -p "$OUT"
exec > >(tee -a "$OUT/extensions.log") 2>&1
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

echo "=== $(stamp) START extensions study=$STUDY cap=\$$CAP"
$PY experiment.py selftest | tail -1
$PY experiment.py --study "$STUDY" prepare | tail -1  # offline: builds the N2 contexts once
paid "$GEMINI" S0,S1,S2,S3,S4,N2 1
paid "$HAIKU" S0,S1,S2,S3,S4,N2 1
paid "$GEMINI" S0,S2 2
paid "$HAIKU" S0,S2 2
for spec in "$GEMINI 1" "$HAIKU 1" "$GEMINI 2" "$HAIKU 2"; do
  set -- $spec
  $PY experiment.py --study "$STUDY" report --model "$1" --repeat "$2" | tail -1
done
echo "=== $(stamp) DONE"

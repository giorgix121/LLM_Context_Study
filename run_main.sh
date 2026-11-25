#!/usr/bin/env bash
# Unattended "main" study, meant to run inside tmux:
#   max balanced sample, google/gemini-2.5-flash-lite, all six context levels, project-wide cap $12.
# Every step resumes from its caches, so re-running this script never repeats a paid request.
set -uo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
STUDY=main
MODEL=google/gemini-2.5-flash-lite
CAP=12
OUT="results/$STUDY"
mkdir -p "$OUT"
exec > >(tee -a "$OUT/pipeline.log") 2>&1
stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
echo "=== $(stamp) START study=$STUDY model=$MODEL cap=\$$CAP"

echo "=== $(stamp) [1/5] offline selftest"
$PY experiment.py selftest | tail -1
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "=== $(stamp) STOP: selftest failed"; exit 1; }

echo "=== $(stamp) [2/5] prepare: max balanced sample + caller/callee/repository contexts (free)"
ok=0
for attempt in 1 2 3 4; do
  if $PY experiment.py --study "$STUDY" prepare --sample-size max; then ok=1; break; fi
  echo "=== $(stamp) prepare stopped (network/rate limit?); resuming in 10 minutes (attempt $attempt/4)"
  sleep 600
done
[ "$ok" -eq 1 ] || { echo "=== $(stamp) STOP: prepare failed repeatedly"; exit 1; }

echo "=== $(stamp) [3/5] dry run: prompts, live pricing, budget fit (free)"
$PY experiment.py --study "$STUDY" run --model "$MODEL" --max-cost "$CAP" --fit-budget \
  || { echo "=== $(stamp) STOP: dry run failed"; exit 1; }

echo "=== $(stamp) [4/5] paid run (resumes automatically after transient halts)"
code=1
for attempt in 1 2 3 4 5 6; do
  $PY experiment.py --study "$STUDY" run --model "$MODEL" --max-cost "$CAP" --fit-budget --execute 2>&1 \
    | tee -a "$OUT/run_execute.log"
  code=${PIPESTATUS[0]}
  echo "=== $(stamp) paid run exit code $code (0 ok, 2 halted, 3 charges not reconciled, 4 transient halt)"
  [ "$code" -eq 4 ] || break
  echo "=== $(stamp) transient halt; resuming in 10 minutes (attempt $attempt/6)"
  sleep 600
done

echo "=== $(stamp) [5/5] report"
$PY experiment.py --study "$STUDY" report --model "$MODEL"
echo "=== $(stamp) DONE (paid run exit code $code). Report: $OUT/$(basename "$MODEL")/report.md"

# Context level vs. LLM change-risk prediction

**RQ1:** How do different context strategies affect prediction quality?
**RQ2:** Which context level offers the best prediction–cost trade-off?

One dataset (Defectors), 30 labeled Python file changes (15 RISKY / 15 NON-RISKY), and six context
levels. Each model run uses one model for all levels:

| Level | Context sent to the model |
|---|---|
| **S0 DIFF** | the complete target-file diff |
| **S1 FUNCTION** | S0 + complete enclosing functions, BEFORE and AFTER |
| **S2 FILE** | S0 + the complete target file, BEFORE and AFTER |
| **S3 CALLERS** | S1 + complete definitions of repository functions that call the changed functions |
| **S4 CALLEES** | S1 + complete definitions of repository functions that the changed functions call |
| **S5 REPO** | S2 + the repository's other Python files, nearest first, up to a fixed prompt budget (the whole repository when it fits) |
| **N2 NOISE** (control) | S0 + Python files from another repository, as many characters as S2 adds |
| **M0 MESSAGE** | S0 + the target commit's message |
| **C0 COMMIT** | S0 + the diffs of the other files changed by the target commit (same question about the target file) |
| **J0 COMMIT-LEVEL** | the whole commit diff, with the question asked about the commit instead of the target file |

Main run: `google/gemini-2.5-flash-lite` (1M-token window), all six levels. Reference run:
`anthropic/claude-haiku-4.5` (200K-token window), S0–S2 only.

## Setup

```bash
cd /Users/gigimerabishvili/Desktop/class_proj
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp -n .env.example .env        # only if .env does not exist yet; never overwrites
```

Then open `.env` in an editor and set `OPENROUTER_API_KEY=` (keys stay local; `.env` is git-ignored).
`GITHUB_TOKEN` is optional.

## Run

```bash
.venv/bin/python experiment.py selftest                      # offline checks, no paid calls
.venv/bin/python experiment.py prepare                       # sample + reconstruction + snapshots + callers/callees (free)
M=google/gemini-2.5-flash-lite
.venv/bin/python experiment.py run --model $M                # dry run: prompts, live pricing, cost estimate (free)
.venv/bin/python experiment.py run --model $M --execute --max-cost 8   # paid: 1 preflight + 180 predictions
.venv/bin/python experiment.py report --model $M             # results/<model>/{results,summary}.csv, cost_vs_f1.png, report.md
```

Flags:
- `--model` overrides `OPENROUTER_MODEL`. Each model needs a routing profile in `MODEL_PROFILES`, which
  fixes one first-party provider with no fallbacks and sets its REPO budget.
- `--max-cost` overrides `MAX_COST_USD`. It is a project-wide cap: spending in every
  `results/*/attempts.jsonl` counts toward it.
- `--levels S0,S1,S2` restricts a run to some of the levels; `N2` adds the length control (default: S0–S5).
- `--repeat N` (run and report) makes an identical re-run number N. The request bodies are the same, but the run
  has its own cache keys and its own results folder `<model>_repN`.
- `--study NAME` keeps a separate frozen sample and results folder (default `pilot`).
- `prepare --sample-size N|max` sets the sample size; `max` is every eligible RISKY change plus as many
  NON-RISKY.
- `run --fit-budget` runs the first k cases per class when the cap can't cover all cases.

Completed requests are cached by a hash of the request, so re-runs never repeat a paid call.

## Main study (longer run, unattended in tmux)

`run_main.sh` runs the whole pipeline for the `main` study. It selects the largest balanced sample:
every eligible RISKY change (one per commit, same seed-42 order and checks as the pilot) plus the same
number of NON-RISKY changes. It then builds contexts and runs `google/gemini-2.5-flash-lite` on all six
levels under a project-wide $12 cap. Outputs go to `data/prepared_main/` and
`results/main/gemini-2.5-flash-lite/`. The pilot's files are never touched.

```bash
tmux new-session -d -s defectors-main "caffeinate -i ./run_main.sh; exec zsh -l"   # start (already running)
tmux attach -t defectors-main          # watch live; detach again with Ctrl-b d
tail -f results/main/pipeline.log      # or follow the log without attaching
```

- **Budget fit:** before any paid request, `--fit-budget` estimates the cost from characters per token
  measured in earlier runs of this model, plus 10%. If the cap can't cover every case, it runs the first
  k cases per class in seeded order. Every case that runs gets all six levels, so no money goes to
  partial cases. The decision is saved in `budget_fit.json`.
- **Resumable:**
  - A transient API halt (exit code 4) or a network failure during `prepare` makes the script wait 10
    minutes and resume.
  - Cached predictions are never requested again, and the pilot's identical requests are reused.
  - A temporary GitHub failure (rate limit, network) stops `prepare` instead of being logged as an
    exclusion.
- **Sleep:** `caffeinate -i` keeps the Mac awake while the script runs. Closing the lid on battery power
  still sleeps the machine.

## Follow-up experiments and paper

`run_extensions.sh` runs three follow-up experiments on the same frozen 146-case main sample:

- **E1, second model:** `anthropic/claude-haiku-4.5` on S0–S4. S5 is left out because it would cost about $18 for
  this model.
- **E2, length control N2:** S0 plus Python files from a *different* sampled repository, cut at a line boundary to
  exactly the number of characters that S2 adds to S0. N2 has S2's length but none of its information. It runs on
  both models. The contexts are built offline by `prepare` into `data/prepared_main/cases/*/noise.json`.
- **E3, identical re-runs:** S0 and S2 sent again unchanged (`--repeat 2`, own cache keys, results in
  `<model>_rep2/`), for both models.

New Gemini runs go to Google AI Studio (profile `google/gemini-2.5-flash-lite@ai-studio`, same model id). OpenRouter
no longer offers the `google-vertex` endpoint that the main run used. The original profile and all of its cache
keys are unchanged.

`run_models2.sh` (Nov 20, 2026) adds a second round on the same sample:

- **E4, commit message M0:** S0 plus the target commit's message, verbatim, read offline from the cached commit
  objects into `data/prepared_main/cases/*/message.json` by `prepare`. Run for all four models.
- **E5, two more models:** `qwen/qwen3.8-flash` (Alibaba) and `anthropic/claude-sonnet-4.6` (Anthropic) on S0–S4, N2
  and M0, plus identical S0/S2 re-runs. Claude 5.x and GPT-6.x were not used: none of their OpenRouter endpoints
  accepts `temperature`, which the protocol fixes at 0.

`run_commit.sh` (Nov 24, 2026) adds a third round, after the label audit showed that the labels describe commits:

- **E6, the rest of the commit:** C0 and J0 for all four models (Gemini through AI Studio). The other files of each
  commit come from the GitHub REST API (`gh` CLI, cached) and are stored per case as `commit.json` by `prepare`.
  J0 is the only level whose instruction differs: it names "the commit" instead of "the target Python file change".
  `analysis.py` compares both with the diff alone (`com.*` macros, `tab_commit.tex`) and reports how often each model
  calls a file risky per audit group (`grp.*` macros, `tab_groups.tex`).

**Label audit (Nov 24, 2026), the version the paper reports:** `audit_szz.py` checks the 73 RISKY cases against the
dataset's own links. Defectors publishes its fix -> bug-inducing map on Zenodo next to the splits
(`bug_inducing_commits.zip`, kept with its md5 in `data/raw/defectors_szz/`). For each case the script takes the fix
commits that the map links to the case's commit (100 links to 88 fix commits), fetches them through the `gh` CLI
(read-only, cached in `data/audit/cache/`) and repeats the blame step of SZZ: which lines of the commit does the fix
remove, and in which file. Results: `data/audit/szz_links.json`, with a readable summary per case in
`data/audit/bundles_szz/`.

- A risky file is **blamed** if a linked fix removes lines that the commit added to it (26 cases), and **inherited**
  if the linked fixes remove lines of the commit only in other files (47 cases; in 44 of them no linked fix changes
  the file at all). Exact `git blame` and text matching agree on this for all 73 cases.
- This needs no judgement. `analysis.py` reports it as the `audit.*` macros and compares the models' predictions
  between the two groups and the non-risky files (`grp.*` macros, `tab_groups.tex`).

**Not used in the paper:** LLM-judged verdicts were collected twice on Nov 24, 2026. The first audit
(`audit_labels.py`, `data/audit/bundles/`, `verdicts_*.jsonl`, `judge_prompt.txt`, `rubric.json`) searched for
candidate fixes itself and looked at the dataset's own fix commit in only 24 of the 73 cases. The second
(`szz_verdicts_*.jsonl`, `szz_judge_prompt.txt`, `szz_rubric.json`) judged the 29 cases in which a linked fix changes
the file. Both rest on LLM judges from one vendor that no human checked, so the paper reports only the part above.
The files are kept for the record.

```bash
caffeinate -i ./run_extensions.sh                 # paid, about $4; resumable; log: results/main/extensions.log
caffeinate -i ./run_models2.sh                    # paid, about $10; resumable; log: results/main/models2.log
caffeinate -i ./run_commit.sh                     # paid, about $8; resumable; log: results/main/commit.log
.venv/bin/python -I audit_szz.py                  # label audit: read-only GitHub requests, cached; no API cost
.venv/bin/python analysis.py                      # offline: paper/generated/*.tex, stats.json, paper/figures/*.pdf
cd paper && latexmk -pdf paper.tex                # paper/paper.pdf
```

`analysis.py` computes every number, table and figure in `paper/paper.tex` from the logged results: paired
bootstrap CIs, exact McNemar tests with Holm correction, Cochran's Q, Cohen's κ, and the always-RISKY,
lines-added and message-length baselines. The paper reads them through generated macros, so no number is typed by hand.

The paper names the conditions in words and does not use the codes: S0 diff, S1 function, S2 file, S3 callers,
S4 callees, S5 repository, N2 unrelated code, M0 commit message. The codes remain in the scripts, the results and the
macro names. Cochran's Q is still computed but no longer reported in the paper.

## What each step does

### prepare
- **Dataset:** Defectors (Mahbub, Shuvo, Rahman, MSR 2023; arXiv:2303.04738), Zenodo record 7708984.
  Only `jit_bug_prediction_splits/time/test.parquet.gzip` is fetched. The ZIP central directory is read
  with HTTP range requests, and only that member's 4.2 MB byte range is downloaded (CRC32-verified). The
  2.2 GB archive is never downloaded.
- **Labels:** the paper's `induce_bug` column (Table I) is released as **`lines`**. Per Sec. III-F,
  nonempty → **RISKY** and empty → **NON-RISKY**. Malformed annotations are rejected. All 1,246 nonempty
  rows annotate only added lines of their diff. **The label is per commit, not per file:** every file of a
  blamed commit that adds lines is marked, and `lines` lists all of its added lines (Sec. III-F: "the list of added
  (i.e., defective) line numbers if the commit is defective"). In the test split this holds for all 203 risky
  commits with several files; 55 of the 73 sampled RISKY files come from such commits. The label audit therefore
  asks whether the dataset's fix removes lines of the commit in the sampled *file* (see the label audit above).
- **Frozen sample:** seed-42 order. Each case is a modified `.py` file in a non-merge commit, with the
  dataset diff verified against the reconstructed files, parseable code, all edits inside functions,
  BEFORE+AFTER ≤ 24,000 chars, a diff ≤ 8,000 chars, and at most one file per commit. Every exclusion is
  logged in `data/prepared/selection_log.csv`. Labels exist only in `manifest.csv`.
- **Repository snapshots:** for each case, all `.py` files of the repository at the target commit are
  stored as `data/cache/snapshots/*.zip`. They come from the GitHub tarball for that exact SHA. The
  snapshot's copy of the target file must equal the reconstructed AFTER file. Code is only parsed with
  `ast`, never executed.
- **Callers / callees (S3, S4):** a conservative static `ast` resolver over the snapshot. It resolves
  absolute and relative imports and re-exports, `self.`/`cls.`/`super()` calls and base classes,
  `Class(...)` constructors, `Class.method` and `module.func` calls. A method or function name that is
  defined only once in the whole repository also counts. Dynamic dispatch (for example framework
  callbacks) is not resolved; such cases get an explicit "none found" note. Results are deduplicated and
  ordered target-file-first, then by directory distance, capped at 30 functions / 120,000 chars per case
  and level. Coverage is in `data/prepared/context_summary.json`.

### run --execute
- `POST https://openrouter.ai/api/v1/chat/completions` with `temperature=0`, `max_tokens=256`,
  `stream=false`, `reasoning={"enabled": false}` and a pinned provider with no fallbacks:
  `google-vertex` for Gemini, `anthropic` for Haiku. A single preflight request with identical settings
  verifies routing, the served model and provider, disabled thinking, and cost reporting.
- **S5 REPO:** BEFORE and AFTER of the target file, then whole files of the rest of the repository
  ordered by directory distance from the target file, until the model's budget is reached. The budget
  is 2,500,000 prompt chars for 1M-token windows and 420,000 chars for Haiku's 200K window. It was
  fixed before the run so that even a pessimistic 2.45 chars/token would fit. Gemini's tokenizer
  turned out to pack about 3.95 chars/token, so S5 used roughly 60% of its window (see the report for
  measured values). The whole repository is sent when it fits.
- All levels × 30 cases run as separate stateless requests, sequentially, in seeded random order.
  Every attempt is logged immediately. Invalid JSON output is stored as invalid and never mapped to
  NON-RISKY. Up to 3 retries are made for transient errors only.
- **Budget guard:** before each request, the charges so far, plus an upper bound for any attempt of
  unknown cost, plus the next request's worst case with retries, must stay under the cap.
- **Halts:** the run stops on another provider or model, on reasoning output, on a non-retryable
  error, or on a charge that cannot be accounted for. Per-request `usage.cost` is reconciled with the
  key-level usage counter.

### report
`results/<model>/results.csv`, `summary.csv` (precision/recall/F1/accuracy, confusion counts, mean
tokens, latency, mean and total cost, trade-off columns vs. S0, Pareto flag), `cost_vs_f1.png`
(cost on a log scale vs. F1) and `report.md`. Effectiveness is compared on the **paired** set: cases
with a valid prediction at every level.



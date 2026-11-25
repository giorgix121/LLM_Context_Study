#!/usr/bin/env python3
"""Label audit for the RISKY cases of the main sample (follow-up, Nov 2026).

For each RISKY change, find the later commits that remove one of its SZZ-blamed lines: these are the candidate fixes
that Defectors' SZZ traced back to the change. Writes one review bundle per case to data/audit/bundles/<id>.md
(the change, its message, the blamed lines and the candidate fixes) and the raw candidates to data/audit/fixes.json.
Verdicts are recorded separately in data/audit/verdicts.jsonl (one JSON object per case, see RUBRIC below) and
summarised by analysis.py.

Uses the GitHub REST API through the `gh` CLI (read-only, public repositories). Results are cached per request in
data/audit/cache/, so re-running makes no new requests.

    .venv/bin/python audit_labels.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
PREP = ROOT / "data" / "prepared_main"
RAW = ROOT / "data" / "raw" / "jit_bug_prediction_splits" / "time" / "test.parquet.gzip"
OUT = ROOT / "data" / "audit"
UNTIL = "2023-06-30T00:00:00Z"  # Defectors was collected for MSR 2023; later commits cannot be its SZZ fixes
MAX_COMMITS = 60  # later commits to the file inspected per case
MAX_FIXES = 4  # candidate fixes kept per case
MAX_PATCH_CHARS = 6000

RUBRIC = {
    "fix_found": "yes | no: a later commit removes or changes a blamed line",
    "fix_is_bugfix": "yes | no | unclear: that commit repairs a functional defect (not a refactor, feature change, "
                     "style or dependency update)",
    "introduced_by_change": "yes | no | unclear: the repaired defect was introduced by this change's lines "
                            "(not pre-existing, not a line the change only touched cosmetically)",
    "decidable_from": "diff | file | external | na: what a reviewer would need to see the defect at commit time: "
                      "the diff alone, the file or repository, or knowledge outside the code (requirements, "
                      "external APIs, runtime data, later decisions); na if the label is not correct",
    "verdict": "correct | wrong | unclear: the change really introduced a functional defect",
    "rationale": "one sentence",
}


def gh(path: str, params: dict | None = None) -> object:
    """GET a GitHub API path through `gh`, cached on disk by request."""
    key = hashlib.sha256(json.dumps([path, params], sort_keys=True).encode()).hexdigest()[:24]
    cpath = OUT / "cache" / f"{key}.json"
    if cpath.exists():
        return json.loads(cpath.read_text())
    args = ["gh", "api", "-X", "GET", path] + [a for k, v in (params or {}).items() for a in ("-f", f"{k}={v}")]
    r = subprocess.run(args, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"gh api {path}: {r.stderr.strip()[:300]}")
    data = json.loads(r.stdout)
    cpath.parent.mkdir(parents=True, exist_ok=True)
    cpath.write_text(json.dumps(data))
    return data


def removed_lines(patch: str) -> list[str]:
    return [ln[1:].strip() for ln in patch.splitlines() if ln.startswith("-") and not ln.startswith("---")]


def candidates(repo: str, path: str, sha: str, since: str, blamed: list[str]) -> tuple[list[dict], int]:
    """Later commits (oldest first) to `path` that remove a blamed line; also returns how many commits were checked."""
    later = gh(f"repos/{repo}/commits", {"path": path, "since": since, "until": UNTIL, "per_page": 100})
    later = [c for c in reversed(later) if c["sha"] != sha][:MAX_COMMITS]
    wanted = {b for b in blamed if len(b) > 3}  # skip blank and trivial lines such as ")" or "else:"
    found = []
    for c in later:
        detail = gh(f"repos/{repo}/commits/{c['sha']}")
        for f in detail.get("files", []):
            if f.get("filename") != path and f.get("previous_filename") != path:
                continue
            hit = sorted(wanted & set(removed_lines(f.get("patch") or "")))
            if hit:
                found.append({"sha": c["sha"], "date": c["commit"]["author"]["date"],
                              "message": c["commit"]["message"], "matched": hit,
                              "patch": (f.get("patch") or "")[:MAX_PATCH_CHARS]})
        if len(found) >= MAX_FIXES:
            break
    return found, len(later)


def bundle(m, msg: str, diff: str, blamed: list[tuple[int, str]], fixes: list[dict], checked: int) -> str:
    L = [f"# {m.sample_id}: {m.github_repo} {m.commit[:12]}", "",
         f"File: `{m.filepath_posix}` · committed {m.commit_datetime} · SZZ label: RISKY", "",
         "## Commit message", "", "```", msg.strip(), "```", "", "## Diff of the target file", "", "```diff",
         diff.rstrip(), "```", "", "## Lines SZZ blamed (line numbers in the new version)", "", "```"]
    L += [f"{n:5d}  {t}" for n, t in blamed] + ["```", ""]
    L += [f"## Candidate fixes ({len(fixes)} later commits to this file remove a blamed line; {checked} later "
          f"commits up to {UNTIL[:10]} checked)", ""]
    for i, f in enumerate(fixes, 1):
        L += [f"### Candidate {i}: {f['sha'][:12]} ({f['date'][:10]})", "", "Message:", "", "```",
              f["message"].strip()[:1500], "```", "", "Removed blamed lines: " + "; ".join(f"`{x}`" for x in f["matched"]),
              "", "Patch of this file:", "", "```diff", f["patch"].rstrip(), "```", ""]
    if not fixes:
        L += ["(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the "
              "line with different whitespace)", ""]
    return "\n".join(L)


def main() -> int:
    man = pd.read_csv(PREP / "manifest.csv")
    raw = pd.read_parquet(RAW)
    risky = man[man.label == "RISKY"]
    (OUT / "bundles").mkdir(parents=True, exist_ok=True)
    allfix = {}
    for m in risky.itertuples():
        cdir = PREP / "cases" / m.sample_id
        after = (cdir / "after.py.txt").read_text(encoding="utf-8").splitlines()
        nums = [int(n) for n in raw.iloc[int(m.dataset_row)]["lines"]]
        blamed = [(n, after[n - 1]) for n in nums if 0 < n <= len(after)]
        since = pd.Timestamp(m.commit_datetime).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
        fixes, checked = candidates(m.github_repo, m.filepath_posix, m.commit, since, [t.strip() for _, t in blamed])
        msg = json.loads((cdir / "message.json").read_text())["text"]
        diff = (cdir / "diff.txt").read_text(encoding="utf-8")
        (OUT / "bundles" / f"{m.sample_id}.md").write_text(bundle(m, msg, diff, blamed, fixes, checked),
                                                          encoding="utf-8")
        allfix[m.sample_id] = {"checked": checked, "fixes": [{k: v for k, v in f.items() if k != "patch"}
                                                             for f in fixes]}
        print(f"{m.sample_id} {m.github_repo:28s} checked {checked:3d} later commits, {len(fixes)} candidate fixes")
    (OUT / "fixes.json").write_text(json.dumps(allfix, indent=1))
    (OUT / "rubric.json").write_text(json.dumps(RUBRIC, indent=1))
    print(f"{sum(bool(v['fixes']) for v in allfix.values())}/{len(allfix)} cases with at least one candidate fix")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

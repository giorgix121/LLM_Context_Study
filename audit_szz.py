#!/usr/bin/env python3
"""Label audit against the dataset's own SZZ links (follow-up, Nov 24, 2026).

Defectors publishes, next to the splits, the fix -> bug-inducing map its labels were built from
(Zenodo record 7708984: bug_inducing_commits.zip, one YAML per project, `fix commit: [bug-inducing commits]`).
For every RISKY case of the main sample this script looks up the fix commits that name the case's commit, fetches
them (and the commit itself) from GitHub, and records which lines of the commit each fix removes, per file: in the
sampled file (the one shown to the models) or in another file of the commit. A removed line counts when `git blame`
at the fix's parent attributes it to the commit (what SZZ does; GitHub GraphQL), or when its text equals a line the
commit added to that file (which also covers blame run with -w, as PyDriller does). It writes one review bundle
per case to data/audit/bundles_szz/<id>.md and the links to data/audit/szz_links.json, which analysis.py summarises
(blamed: a linked fix removes lines of the commit in the sampled file; inherited: only in other files).

LLM verdicts for the cases in which a linked fix changes the sampled file were collected once
(data/audit/szz_verdicts*.jsonl, rubric in szz_rubric.json, instructions in szz_judge_prompt.txt). The paper does not
use them.

Uses the GitHub REST and GraphQL APIs through the `gh` CLI (read-only, public repositories), cached per request in
data/audit/cache/. The two Zenodo files are expected in data/raw/defectors_szz/ (md5 checked).

    .venv/bin/python -I audit_szz.py
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))  # -I keeps the script folder off sys.path; audit_labels is this project's own module
from audit_labels import gh, removed_lines  # noqa: E402

PREP = ROOT / "data" / "prepared_main"
RAW = ROOT / "data" / "raw" / "jit_bug_prediction_splits" / "time" / "test.parquet.gzip"
SZZ = ROOT / "data" / "raw" / "defectors_szz"
OUT = ROOT / "data" / "audit"
MD5 = {"bug_inducing_commits.zip": "3b4816bf81335f94f6187fd976a2a22c",
       "filtered_bug_inducing_commits.yaml": "46fa9d902d40ef03c2abf68fef26704c"}
MAX_PATCH_CHARS = 4500   # patch of the sampled file in a fix
MAX_OTHER_CHARS = 2200   # patch of another blamed file in a fix
MAX_OTHER_FILES = 3      # other blamed files shown per fix
MAX_TEXT = 1200          # commit messages and pull-request descriptions

RUBRIC = {  # for the cases in which a linked fix changes the sampled file; the other cases need no judgement
    "fix_sha": "first 12 characters of the linked fix commit the verdict rests on",
    "fix_is_bugfix": "yes | no | unclear: that commit repairs a functional defect (not a refactor, rename, feature "
                     "change, style, typing, documentation, test-only or dependency change)",
    "defect_in_sampled_file": "yes | no | unclear: the repaired defect is in the code this commit added to the "
                              "sampled file (a wrong line, or something that code plainly left out); no if the fix "
                              "only moves, renames, reformats or refactors those lines, changes them for a feature "
                              "or a later requirement, repairs a defect in another file or in older code, or touches "
                              "the file only incidentally",
    "verdict": "in_file | not_in_file | unclear: in_file only if both are yes; not_in_file if either is clearly no",
    "decidable_from": "diff | file | external | na: for in_file only, what a reviewer would have needed at commit "
                      "time to see the defect",
    "rationale": "one sentence",
}


BLAME_QUERY = """query($owner: String!, $name: String!, $expr: String!, $path: String!) {
  repository(owner: $owner, name: $name) { object(expression: $expr) { ... on Commit {
    blame(path: $path) { ranges { startingLine endingLine commit { oid } } } } } } }"""


def added_lines(patch: str) -> list[str]:
    return [ln[1:].strip() for ln in patch.splitlines() if ln.startswith("+") and not ln.startswith("+++")]


def deleted_old_lines(patch: str) -> list[tuple[int, str]]:
    """(line number in the old file, text) of every line a patch removes."""
    out, old = [], None
    for ln in patch.splitlines():
        if ln.startswith("@@"):
            old = int(re.match(r"@@ -(\d+)", ln).group(1))
        elif old is None or ln.startswith("\\"):
            continue
        elif ln.startswith("-"):
            out.append((old, ln[1:]))
            old += 1
        elif not ln.startswith("+"):
            old += 1
    return out


def useless(text: str) -> bool:
    """Lines PyDriller's SZZ does not blame: blank lines and comment starts."""
    t = text.strip()
    return not t or t.startswith(("//", "#", "/*", "'''", '"""', "*"))


def blame(repo: str, sha: str, path: str) -> list[tuple[int, int, str]]:
    """`git blame` of `path` at commit `sha` as (first line, last line, commit) ranges; cached."""
    key = hashlib.sha256(json.dumps(["graphql-blame", repo, sha, path]).encode()).hexdigest()[:24]
    cpath = OUT / "cache" / f"{key}.json"
    if cpath.exists():
        data = json.loads(cpath.read_text())
    else:
        owner, name = repo.split("/")
        r = subprocess.run(["gh", "api", "graphql", "-f", f"query={BLAME_QUERY}", "-f", f"owner={owner}",
                            "-f", f"name={name}", "-f", f"expr={sha}", "-f", f"path={path}"],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError(f"gh api graphql blame {repo} {sha[:10]} {path}: {r.stderr.strip()[:300]}")
        data = json.loads(r.stdout)
        cpath.write_text(json.dumps(data))
    obj = (data.get("data") or {}).get("repository", {}).get("object") or {}
    return [(x["startingLine"], x["endingLine"], x["commit"]["oid"]) for x in (obj.get("blame") or {}).get("ranges", [])]


def commit_files(repo: str, sha: str) -> tuple[dict, list[dict]]:
    """A commit and all its files (the API returns 300 per page)."""
    c = gh(f"repos/{repo}/commits/{sha}")
    files, page = list(c.get("files") or []), 1
    while len(files) == 300 * page and page < 10:
        page += 1
        files += gh(f"repos/{repo}/commits/{sha}", {"page": page, "per_page": 300}).get("files") or []
    return c, files


def pull_request(repo: str, sha: str) -> dict | None:
    try:
        prs = gh(f"repos/{repo}/commits/{sha}/pulls")
    except RuntimeError:
        return None
    if not prs:
        return None
    p = prs[0]
    return {"number": p["number"], "title": p["title"], "labels": [x["name"] for x in p.get("labels", [])],
            "body": (p.get("body") or "").replace("\r\n", "\n").strip()}


def clip(text: str, n: int) -> str:
    text = text.strip()
    return text if len(text) <= n else text[:n].rstrip() + "\n[... cut ...]"


def link(repo: str, inducing: str, inducing_added: dict[str, set[str]], sampled: str, fix_sha: str) -> dict:
    """One fix commit: which lines of the bug-inducing commit it removes, per file of that commit."""
    try:
        c, files = commit_files(repo, fix_sha)
    except RuntimeError as e:
        return {"sha": fix_sha, "available": False, "error": str(e)[:200]}
    parent = c["parents"][0]["sha"] if c.get("parents") else None
    hits, by_blame, by_text, no_patch, patches, touched, sampled_patch = {}, {}, {}, [], {}, [], None
    for f in files:
        path, prev = f["filename"], f.get("previous_filename")
        key = path if path in inducing_added else prev if prev in inducing_added else None
        if key is None:
            continue  # not a file of the bug-inducing commit
        touched.append(key)
        if "patch" not in f:
            no_patch.append(key)
            continue
        if key == sampled:
            sampled_patch = f["patch"]
        removed = [(n, t) for n, t in deleted_old_lines(f["patch"]) if not useless(t)]
        text = sorted(inducing_added[key] & {t.strip() for _, t in removed})
        blamed = []
        if removed and parent:
            try:
                ranges = blame(repo, parent, prev or path)
                who = {n: oid for a, b, oid in ranges for n in range(a, b + 1)}
                blamed = sorted({t.strip() for n, t in removed if who.get(n) == inducing})
            except RuntimeError:
                blamed = []
        both = sorted(set(text) | set(blamed))
        if both:
            hits[key], patches[key] = both, f["patch"]
            by_blame[key], by_text[key] = blamed, text
    return {"sha": fix_sha, "available": True, "date": c["commit"]["author"]["date"], "message": c["commit"]["message"],
            "parents": len(c.get("parents", [])), "n_files": len(files), "pr": pull_request(repo, fix_sha),
            "touches": sorted(touched), "hits": hits, "by_blame": by_blame, "by_text": by_text, "no_patch": no_patch,
            "patches": patches, "sampled_patch": sampled_patch, "sampled_file_touched": sampled in touched,
            "sampled_file_hit": sampled in hits,
            "other_files_hit": sorted(k for k in hits if k != sampled)}


def bundle(m, msg: str, diff: str, other_files: list[tuple[str, int, int]], links: list[dict]) -> str:
    L = [f"# {m.sample_id}: {m.github_repo} {m.commit[:12]}", "",
         f"Sampled file (the only file the models saw): `{m.filepath_posix}` · committed {m.commit_datetime}", "",
         "The dataset labels this whole commit as bug-inducing, through the fix commits listed below.", "",
         "## Commit message", "", "```", clip(msg, MAX_TEXT), "```", "",
         "## Diff of the sampled file", "", "```diff", diff.rstrip(), "```", "",
         f"## Other files changed by this commit ({len(other_files)})", ""]
    L += [f"- `{p}` (+{a} −{d})" for p, a, d in other_files[:40]] or ["(none)"]
    if len(other_files) > 40:
        L.append(f"- ... and {len(other_files) - 40} more")
    L += ["", f"## Fix commits that the dataset links to this commit ({len(links)})", ""]
    for i, k in enumerate(links, 1):
        if not k["available"]:
            L += [f"### Fix {i}: {k['sha'][:12]}", "", "(this commit could not be fetched from GitHub)", ""]
            continue
        pr = k["pr"]
        head = f"### Fix {i}: {k['sha'][:12]} ({k['date'][:10]})"
        if pr:
            head += f" · pull request #{pr['number']}: {pr['title']}"
        L += [head, ""]
        if pr and pr["labels"]:
            L += ["Pull-request labels: " + ", ".join(pr["labels"]), ""]
        L += ["Commit message:", "", "```", clip(k["message"], MAX_TEXT), "```", ""]
        if pr and pr["body"]:
            L += ["Pull-request description:", "", "```", clip(pr["body"], MAX_TEXT), "```", ""]
        L += [f"This fix changes {k['n_files']} files. Lines it removes that the commit above had added:", ""]
        if k["sampled_file_hit"]:
            L.append("- in the sampled file: " + "; ".join(f"`{x}`" for x in k["hits"][m.filepath_posix][:12]))
        elif k["sampled_file_touched"]:
            L.append("- in the sampled file: none (the fix changes this file, but not lines the commit added)")
        else:
            L.append("- in the sampled file: none (the fix does not change this file)")
        for p in k["other_files_hit"][:8]:
            L.append(f"- in `{p}`: " + "; ".join(f"`{x}`" for x in k["hits"][p][:6]))
        if not k["other_files_hit"]:
            L.append("- in other files of the commit: none")
        if k["no_patch"]:
            L.append("- no patch available from GitHub for: " + ", ".join(f"`{p}`" for p in k["no_patch"][:6]))
        L.append("")
        if k["sampled_patch"]:
            L += ["Patch of the sampled file in this fix:", "", "```diff",
                  clip(k["sampled_patch"], MAX_PATCH_CHARS), "```", ""]
        for p in k["other_files_hit"][:MAX_OTHER_FILES]:
            L += [f"Patch of `{p}` in this fix:", "", "```diff", clip(k["patches"][p], MAX_OTHER_CHARS), "```", ""]
    return "\n".join(L)


def main() -> int:
    for name, md5 in MD5.items():
        if hashlib.md5((SZZ / name).read_bytes()).hexdigest() != md5:
            raise SystemExit(f"{name}: checksum differs from the Zenodo record")
    inv: dict[tuple[str, str], list[str]] = {}
    for p in sorted((SZZ / "extracted" / "bug_inducing_commits").glob("*.yaml")):
        for fix, inducing in (yaml.safe_load(p.read_text()) or {}).items():
            for c in inducing or []:
                inv.setdefault((p.stem, c), []).append(fix)
    man = pd.read_csv(PREP / "manifest.csv")
    raw = pd.read_parquet(RAW)
    (OUT / "bundles_szz").mkdir(parents=True, exist_ok=True)
    out = {}
    for m in man[man.label == "RISKY"].itertuples():
        repo_short = raw.iloc[int(m.dataset_row)]["repo"]
        fixes = sorted(inv.get((repo_short, m.commit), []))
        c, files = commit_files(m.github_repo, m.commit)
        added = {f["filename"]: {t for t in added_lines(f.get("patch") or "") if len(t) > 3} for f in files}
        links = [link(m.github_repo, m.commit, added, m.filepath_posix, fx) for fx in fixes]
        cdir = PREP / "cases" / m.sample_id
        msg = json.loads((cdir / "message.json").read_text())["text"]
        diff = (cdir / "diff.txt").read_text(encoding="utf-8")
        others = [(f["filename"], f.get("additions", 0), f.get("deletions", 0)) for f in files
                  if f["filename"] != m.filepath_posix]
        (OUT / "bundles_szz" / f"{m.sample_id}.md").write_text(bundle(m, msg, diff, others, links), encoding="utf-8")
        ok = [k for k in links if k["available"]]
        where = ("sampled_file" if any(k["sampled_file_hit"] for k in ok) else
                 "other_file" if any(k["other_files_hit"] for k in ok) else "none_found")
        touched = any(k["sampled_file_touched"] for k in ok)
        out[m.sample_id] = {"commit": m.commit, "file": m.filepath_posix, "files_in_commit": len(files),
                            "where": where, "fix_changes_sampled_file": touched,
                            "fixes": [{k2: v for k2, v in k.items() if k2 not in ("patches", "sampled_patch")}
                                      for k in links]}
        print(f"{m.sample_id} {m.github_repo:26s} files {len(files):3d}  fixes {len(links)}  removed lines found in: {where}")
    (OUT / "szz_links.json").write_text(json.dumps(out, indent=1))
    (OUT / "szz_rubric.json").write_text(json.dumps(RUBRIC, indent=1))
    n = pd.Series([v["where"] for v in out.values()]).value_counts().to_dict()
    print(f"{len(out)} cases; lines removed by a linked fix were found in: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

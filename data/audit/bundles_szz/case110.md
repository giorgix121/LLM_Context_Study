# case110: Lightning-AI/lightning 0bafb38c808d

Sampled file (the only file the models saw): `src/lightning_lite/plugins/environments/slurm.py` · committed 2022-10-20 10:45:15-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Fix srun availability check (#15211)

command -v

Co-authored-by: Justus Schock <12886177+justusschock@users.noreply.github.com>
```

## Diff of the sampled file

```diff
@@ -160,7 +160,10 @@ class SLURMEnvironment(ClusterEnvironment):
         """
         if _IS_WINDOWS:
             return
-        srun_exists = subprocess.call(["which", "srun"]) == 0
+        try:
+            srun_exists = subprocess.call(["command", "-v", "srun"]) == 0
+        except FileNotFoundError:
+            srun_exists = False
         if srun_exists and not _is_srun_used():
             hint = " ".join(["srun", os.path.basename(sys.executable), *sys.argv])[:64]
             rank_zero_warn(
```

## Other files changed by this commit (0)

(none)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 9c20cad40e41 (2022-11-03) · pull request #15485: Fix srun detection causing permission error on non-SLURM platforms

Pull-request labels: bug, ready to be merged, priority: 0, environment: slurm, fun

Commit message:

```
Fix srun detection causing permission error on non-SLURM platforms (#15485)

* improve srun detection
* changelog
* try catch is obsolete

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
```

Pull-request description:

```
## What does this PR do?

Fixes #15455
## Before submitting
- [x] Was this discussed/approved via a GitHub issue? (not for typos and docs)
- [x] Did you read the [contributor guideline](https://github.com/PyTorchLightning/pytorch-lightning/blob/master/.github/CONTRIBUTING.md), **Pull Request** section?
- [x] Did you make sure your PR does only one thing, instead of bundling different changes together?
- [x] Did you make sure to update the documentation with your changes? (if necessary)
- [x] Did you write any new necessary tests? (not for typos and docs)
- [x] Did you verify new and existing tests pass locally with your changes?
- [x] Did you update the [CHANGELOG](https://github.com/PyTorchLightning/pytorch-lightning/blob/master/CHANGELOG.md)? (not for typos, docs, test updates, or internal minor changes/refactorings)

<!-- For CHANGELOG separate each item in the unreleased section by a blank line to reduce collisions -->

## PR review
Anyone in the community is free to review the PR once the tests have passed.
Before you start reviewing make sure you have read [Review guidelines](https://github.com/PyTorchLightning/pytorch-lightning/wiki/Review-guidelines). In short, see the foll
[... cut ...]
```

This fix changes 3 files. Lines it removes that the commit above had added:

- in the sampled file: `except FileNotFoundError:`; `srun_exists = False`; `srun_exists = subprocess.call(["command", "-v", "srun"]) == 0`; `try:`
- in other files of the commit: none

Patch of the sampled file in this fix:

```diff
@@ -15,8 +15,8 @@
 import logging
 import os
 import re
+import shutil
 import signal
-import subprocess
 import sys
 from typing import Optional
 
@@ -160,10 +160,8 @@ def _validate_srun_used() -> None:
         """
         if _IS_WINDOWS:
             return
-        try:
-            srun_exists = subprocess.call(["command", "-v", "srun"]) == 0
-        except FileNotFoundError:
-            srun_exists = False
+
+        srun_exists = shutil.which("srun") is not None
         if srun_exists and not _is_srun_used():
             hint = " ".join(["srun", os.path.basename(sys.executable), *sys.argv])[:64]
             rank_zero_warn(
```

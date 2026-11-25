# case110: Lightning-AI/lightning 0bafb38c808d

File: `src/lightning_lite/plugins/environments/slurm.py` · committed 2022-10-20 10:45:15-01:00 · SZZ label: RISKY

## Commit message

```
Fix srun availability check (#15211)

command -v

Co-authored-by: Justus Schock <12886177+justusschock@users.noreply.github.com>
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
  163          try:
  164              srun_exists = subprocess.call(["command", "-v", "srun"]) == 0
  165          except FileNotFoundError:
  166              srun_exists = False
```

## Candidate fixes (1 later commits to this file remove a blamed line; 3 later commits up to 2023-06-30 checked)

### Candidate 1: 9c20cad40e41 (2022-11-03)

Message:

```
Fix srun detection causing permission error on non-SLURM platforms (#15485)

* improve srun detection
* changelog
* try catch is obsolete

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
```

Removed blamed lines: `except FileNotFoundError:`; `srun_exists = False`; `srun_exists = subprocess.call(["command", "-v", "srun"]) == 0`; `try:`

Patch of this file:

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

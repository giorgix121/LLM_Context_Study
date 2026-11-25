# case131: python-poetry/poetry 770a8148c9ce

Sampled file (the only file the models saw): `src/poetry/utils/shell.py` · committed 2022-10-07 06:18:21-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
adds fallback behavior for non-ms shells
```

## Diff of the sampled file

```diff
@@ -78,12 +78,22 @@ class Shell:
         if sys.platform == "win32":
             if self._name in ("powershell", "pwsh"):
                 args = ["-NoExit", "-File", str(activate_path)]
-            else:
+            elif self._name == "cmd":
                 # /K will execute the bat file and
                 # keep the cmd process from terminating
                 args = ["/K", str(activate_path)]
-            completed_proc = subprocess.run([self.path, *args])
-            return completed_proc.returncode
+            else:
+                args = None
+
+            if args:
+                completed_proc = subprocess.run([self.path, *args])
+                return completed_proc.returncode
+            else:
+                # If no args are set, execute the shell within the venv
+                # This activates it, but there could be some features missing:
+                # deactivate command might not work
+                # shell prompt will not be modified.
+                return env.execute(self._path)
 
         import shlex
```

## Other files changed by this commit (0)

(none)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 3d422d721594 (2022-09-19) · pull request #6560: adds fallback behavior for non-ms shells

Pull-request labels: kind/bug, impact/backport, area/windows, impact/changelog, area/shell

Commit message:

```
hoists args out of else block
```

Pull-request description:

```
# Pull Request Check List

Resolves: #6495

<!-- This is just a reminder about the most common mistakes. Please make sure that you tick all *appropriate* boxes.  But please read our [contribution guide](https://python-poetry.org/docs/contributing/) at least once, it will save you unnecessary review cycles! -->

- [ ] Added **tests** for changed code.

<!-- If you have *any* questions to *any* of the points above, just **submit and ask**!  This checklist is here to *help* you, not to deter you from contributing! -->
Confirmed working on MS Powershell, Powershell 7, cmd and git bash
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: `args = None`; `else:`
- in other files of the commit: none

Patch of the sampled file in this fix:

```diff
@@ -76,14 +76,13 @@ def activate(self, env: VirtualEnv) -> int | None:
         # mypy requires using sys.platform instead of WINDOWS constant
         # in if statements to properly type check on Windows
         if sys.platform == "win32":
+            args = None
             if self._name in ("powershell", "pwsh"):
                 args = ["-NoExit", "-File", str(activate_path)]
             elif self._name == "cmd":
                 # /K will execute the bat file and
                 # keep the cmd process from terminating
                 args = ["/K", str(activate_path)]
-            else:
-                args = None
 
             if args:
                 completed_proc = subprocess.run([self.path, *args])
```

# case131: python-poetry/poetry 770a8148c9ce

File: `src/poetry/utils/shell.py` · committed 2022-10-07 06:18:21-01:00 · SZZ label: RISKY

## Commit message

```
adds fallback behavior for non-ms shells
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
   81              elif self._name == "cmd":
   85              else:
   86                  args = None
   87  
   88              if args:
   89                  completed_proc = subprocess.run([self.path, *args])
   90                  return completed_proc.returncode
   91              else:
   92                  # If no args are set, execute the shell within the venv
   93                  # This activates it, but there could be some features missing:
   94                  # deactivate command might not work
   95                  # shell prompt will not be modified.
   96                  return env.execute(self._path)
```

## Candidate fixes (1 later commits to this file remove a blamed line; 3 later commits up to 2023-06-30 checked)

### Candidate 1: 3d422d721594 (2022-09-19)

Message:

```
hoists args out of else block
```

Removed blamed lines: `args = None`; `else:`

Patch of this file:

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

# case146: django/django 42cd8c390d5f

File: `django/core/management/utils.py` · committed 2022-09-07 12:08:43-01:00 · SZZ label: RISKY

## Commit message

```
Fixed #33986 -- Hardened binary lookup in template commands.

Made template commands look up formatters before writing files.
This makes sure files included in the template are not identified
as executable formatter commands, even in case the template is
rendered into the system path (as might easily happen on Windows,
where the current directory is on the system path by default).

While at it, Warned about trusting custom templates for
startapp/startproject.

Thanks Trung Pham of Viettel Cyber Security for reporting the issue,
Django Security Team for discussions, and Adam Johnson and
Carlton Gibson for reviews.
```

## Diff of the target file

```diff
@@ -157,11 +157,18 @@ def is_ignored_path(path, ignore_patterns):
     return any(ignore(pattern) for pattern in normalize_path_patterns(ignore_patterns))
 
 
-def run_formatters(written_files):
+def find_formatters():
+    return {"black_path": shutil.which("black")}
+
+
+def run_formatters(written_files, black_path=(sentinel := object())):
     """
     Run the black formatter on the specified files.
     """
-    if black_path := shutil.which("black"):
+    # Use a sentinel rather than None, as which() returns None when not found.
+    if black_path is sentinel:
+        black_path = shutil.which("black")
+    if black_path:
         subprocess.run(
             [black_path, "--fast", "--", *written_files],
             capture_output=True,
```

## Lines SZZ blamed (line numbers in the new version)

```
  160  def find_formatters():
  161      return {"black_path": shutil.which("black")}
  162  
  163  
  164  def run_formatters(written_files, black_path=(sentinel := object())):
  168      # Use a sentinel rather than None, as which() returns None when not found.
  169      if black_path is sentinel:
  170          black_path = shutil.which("black")
  171      if black_path:
```

## Candidate fixes (0 later commits to this file remove a blamed line; 1 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

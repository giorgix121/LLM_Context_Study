# case146: django/django 42cd8c390d5f

Sampled file (the only file the models saw): `django/core/management/utils.py` · committed 2022-09-07 12:08:43-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

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

## Diff of the sampled file

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

## Other files changed by this commit (2)

- `django/core/management/templates.py` (+10 −2)
- `docs/ref/django-admin.txt` (+16 −2)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 5c2c7277d455 (2022-10-18) · pull request #16201: Fixed #34085 -- Made management commands don't use black for non-Python files.

Pull-request labels: DjangoCon 🦄

Commit message:

```
Fixed #34085 -- Made management commands don't use black for non-Python files.

Bug in d113b5a837f726d1c638d76c4e88445e6cd59fd5.

Co-authored-by: programmylife <acmshar@gmail.com>
Co-authored-by: Carlton Gibson <carlton.gibson@noumenal.es>
```

Pull-request description:

```
Supercedes #16192 adds a missing test case. 

Thanks to @programmylife for coauthoring,
```

This fix changes 4 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `django/core/management/templates.py`: `run_formatters(self.written_files, **formatter_paths)`

Patch of `django/core/management/templates.py` in this fix:

```diff
@@ -84,7 +84,6 @@ def add_arguments(self, parser):
         )
 
     def handle(self, app_or_project, name, target=None, **options):
-        self.written_files = []
         self.app_or_project = app_or_project
         self.a_or_an = "an" if app_or_project == "app" else "a"
         self.paths_to_remove = []
@@ -209,7 +208,6 @@ def handle(self, app_or_project, name, target=None, **options):
                 else:
                     shutil.copyfile(old_path, new_path)
 
-                self.written_files.append(new_path)
                 if self.verbosity >= 2:
                     self.stdout.write("Creating %s" % new_path)
                 try:
@@ -232,7 +230,7 @@ def handle(self, app_or_project, name, target=None, **options):
                 else:
                     shutil.rmtree(path_to_remove)
 
-        run_formatters(self.written_files, **formatter_paths)
+        run_formatters([top_dir], **formatter_paths)
 
     def handle_template(self, template, subdir):
         """
```

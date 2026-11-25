# case101: apache/airflow 9a6fc73aba75

File: `dev/breeze/src/airflow_breeze/utils/reinstall.py` · committed 2022-10-01 16:38:31-01:00 · SZZ label: RISKY

## Commit message

```
Update message with new breeze subcommand (#26817)

Signed-off-by: Ross Turk <ross@rossturk.com>

Signed-off-by: Ross Turk <ross@rossturk.com>
```

## Diff of the target file

```diff
@@ -47,7 +47,7 @@ def warn_non_editable():
         "\n[error]Breeze is installed in a wrong way.[/]\n"
         "\n[error]It should only be installed in editable mode[/]\n\n"
         "[info]Please go to Airflow sources and run[/]\n\n"
-        f"     {NAME} self-upgrade --force --use-current-airflow-sources\n"
+        f"     {NAME} setup self-upgrade --force --use-current-airflow-sources\n"
     )
 
 
@@ -56,6 +56,6 @@ def warn_dependencies_changed():
         f"\n[warning]Breeze dependencies changed since the installation![/]\n\n"
         f"[warning]This might cause various problems!![/]\n\n"
         f"If you experience problems - reinstall Breeze with:\n\n"
-        f"    {NAME} self-upgrade --force\n"
+        f"    {NAME} setup self-upgrade --force\n"
         "\nThis should usually take couple of seconds.\n"
     )
```

## Lines SZZ blamed (line numbers in the new version)

```
   50          f"     {NAME} setup self-upgrade --force --use-current-airflow-sources\n"
   59          f"    {NAME} setup self-upgrade --force\n"
```

## Candidate fixes (1 later commits to this file remove a blamed line; 3 later commits up to 2023-06-30 checked)

### Candidate 1: 10d2a71073a2 (2022-11-01)

Message:

```
Remove --force option of breeze self-upgrade from docs (#27438)

The option was removed some time ago but there were some docs remaining.

Fix: #27429
```

Removed blamed lines: `f"     {NAME} setup self-upgrade --force --use-current-airflow-sources\n"`; `f"    {NAME} setup self-upgrade --force\n"`

Patch of this file:

```diff
@@ -47,7 +47,7 @@ def warn_non_editable():
         "\n[error]Breeze is installed in a wrong way.[/]\n"
         "\n[error]It should only be installed in editable mode[/]\n\n"
         "[info]Please go to Airflow sources and run[/]\n\n"
-        f"     {NAME} setup self-upgrade --force --use-current-airflow-sources\n"
+        f"     {NAME} setup self-upgrade --use-current-airflow-sources\n"
     )
 
 
@@ -56,6 +56,6 @@ def warn_dependencies_changed():
         f"\n[warning]Breeze dependencies changed since the installation![/]\n\n"
         f"[warning]This might cause various problems!![/]\n\n"
         f"If you experience problems - reinstall Breeze with:\n\n"
-        f"    {NAME} setup self-upgrade --force\n"
+        f"    {NAME} setup self-upgrade\n"
         "\nThis should usually take couple of seconds.\n"
     )
```

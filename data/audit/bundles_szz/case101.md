# case101: apache/airflow 9a6fc73aba75

Sampled file (the only file the models saw): `dev/breeze/src/airflow_breeze/utils/reinstall.py` · committed 2022-10-01 16:38:31-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Update message with new breeze subcommand (#26817)

Signed-off-by: Ross Turk <ross@rossturk.com>

Signed-off-by: Ross Turk <ross@rossturk.com>
```

## Diff of the sampled file

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

## Other files changed by this commit (0)

(none)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 10d2a71073a2 (2022-11-01) · pull request #27438: Remove --force option of breeze self-upgrade from docs

Pull-request labels: area:dev-tools

Commit message:

```
Remove --force option of breeze self-upgrade from docs (#27438)

The option was removed some time ago but there were some docs remaining.

Fix: #27429
```

Pull-request description:

```
The option was removed some time ago but there were some docs remaining.

Fix: #27429

<!--
Thank you for contributing! Please make sure that your code changes
are covered with tests. And in case of new features or big changes
remember to adjust the documentation.

Feel free to ping committers for the review!

In case of an existing issue, reference it using one of the following:

closes: #ISSUE
related: #ISSUE

How to write a good git commit message:
http://chris.beams.io/posts/git-commit/
-->

---
**^ Add meaningful description above**

Read the **[Pull Request Guidelines](https://github.com/apache/airflow/blob/main/CONTRIBUTING.rst#pull-request-guidelines)** for more information.
In case of fundamental code changes, an Airflow Improvement Proposal ([AIP](https://cwiki.apache.org/confluence/display/AIRFLOW/Airflow+Improvement+Proposals)) is needed.
In case of a new dependency, check compliance with the [ASF 3rd Party License Policy](https://www.apache.org/legal/resolved.html#category-x).
In case of backwards incompatible changes please leave a note in a newsfragment file, named `{pr_number}.significant.rst` or `{issue_number}.significant.rst`, in [newsfragments](https://github.co
[... cut ...]
```

This fix changes 3 files. Lines it removes that the commit above had added:

- in the sampled file: `f"     {NAME} setup self-upgrade --force --use-current-airflow-sources\n"`; `f"    {NAME} setup self-upgrade --force\n"`
- in other files of the commit: none

Patch of the sampled file in this fix:

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

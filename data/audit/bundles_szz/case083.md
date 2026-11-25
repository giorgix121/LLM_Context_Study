# case083: Lightning-AI/lightning 6a72a15a62bf

Sampled file (the only file the models saw): `src/lightning_app/utilities/cli_helpers.py` · committed 2022-10-20 10:02:13-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
[App] Automate missing requirements installation for CLI (#15198)

* update

* update

* update

* update

* update

* update

* update

* wording

Co-authored-by: Mansy <ahmed.mansy156@gmail.com>

* update

* update

* update

* update

* update

* update

* update

* update

Co-authored-by: Jirka Borovec <Borda@users.noreply.github.com>
Co-authored-by: Mansy <ahmed.mansy156@gmail.com>
```

## Diff of the sampled file

```diff
@@ -59,6 +59,7 @@ def _get_metadata_from_openapi(paths: Dict, path: str):
     cls_path = paths[path]["post"].get("cls_path", None)
     cls_name = paths[path]["post"].get("cls_name", None)
     description = paths[path]["post"].get("description", None)
+    requirements = paths[path]["post"].get("requirements", None)
 
     metadata = {"tag": tag, "parameters": {}}
 
@@ -71,6 +72,9 @@ def _get_metadata_from_openapi(paths: Dict, path: str):
     if description:
         metadata["description"] = description
 
+    if description:
+        metadata["requirements"] = requirements
+
     if not parameters:
         return metadata
```

## Other files changed by this commit (10)

- `docs/source-app/workflows/build_command_line_interface/commands/notebook/run.py` (+1 −1)
- `examples/app_commands_and_api/command.py` (+1 −1)
- `src/lightning_app/CHANGELOG.md` (+1 −0)
- `src/lightning_app/cli/commands/app_commands.py` (+9 −6)
- `src/lightning_app/cli/commands/connection.py` (+47 −0)
- `src/lightning_app/frontend/panel/panel_frontend.py` (+3 −3)
- `src/lightning_app/frontend/stream_lit.py` (+3 −3)
- `src/lightning_app/frontend/web.py` (+2 −2)
- `src/lightning_app/utilities/commands/base.py` (+21 −14)
- `src/lightning_app/utilities/log.py` (+1 −1)

## Fix commits that the dataset links to this commit (2)

### Fix 1: b72866d6adee (2022-10-21) · pull request #15230: Use user executable for pip installation

Pull-request labels: bug, ready to be merged, app (removed)

Commit message:

```
Use user executable for pip installation (#15230)
```

Pull-request description:

```
## What does this PR do?

<!--
Please include a summary of the change and which issue is fixed.
Please also include relevant motivation and context.
List any dependencies that are required for this change.

If we didn't discuss your PR in Github issues there's a high chance it will not be merged.

The following links the related issue to the PR (https://docs.github.com/en/free-pro-team@latest/github/managing-your-work-on-github/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword)
-->

Fixes #\<issue_number>

### Does your PR introduce any breaking changes? If yes, please list them.

<!-- FILL IN or None -->

## Before submitting

- [x] Was this **discussed/approved** via a GitHub issue? (not for typos and docs)
- [x] Did you read the [contributor guideline](https://github.com/Lightning-AI/lightning/blob/master/.github/CONTRIBUTING.md), **Pull Request** section?
- [x] Did you make sure your **PR does only one thing**, instead of bundling different changes together?
- [x] Did you make sure to **update the documentation** with your changes? (if necessary)
- [x] Did you write any **new necessary tests**? (not for typos and docs)
- [x] Did you verify ne
[... cut ...]
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/lightning_app/cli/commands/connection.py`: `Popen(f"pip install {req}", shell=True, stdout=stdout, stderr=sys.stderr).wait()`

Patch of `src/lightning_app/cli/commands/connection.py` in this fix:

```diff
@@ -261,5 +261,7 @@ def _install_missing_requirements(
                 if yes:
                     std_out_out = get_logfile("output.log")
                     with open(std_out_out, "wb") as stdout:
-                        Popen(f"pip install {req}", shell=True, stdout=stdout, stderr=sys.stderr).wait()
+                        Popen(
+                            f"{sys.executable} -m pip install {req}", shell=True, stdout=stdout, stderr=sys.stderr
+                        ).wait()
                     print()
```

### Fix 2: f98de623fddc (2022-10-24) · pull request #15241: Add support for local connect terminal context

Pull-request labels: bug, ready to be merged, app (removed)

Commit message:

```
Add support for local connect terminal context (#15241)

* update

* update

* update

* update

* update

* update

* update

* update

* update

* update

* update

* Update .azure/app-cloud-e2e.yml

Co-authored-by: Carlos Mocholí <carlossmocholi@gmail.com>

* update

Co-authored-by: Carlos Mocholí <carlossmocholi@gmail.com>
```

Pull-request description:

```
## What does this PR do?

<!--
Please include a summary of the change and which issue is fixed.
Please also include relevant motivation and context.
List any dependencies that are required for this change.

If we didn't discuss your PR in Github issues there's a high chance it will not be merged.

The following links the related issue to the PR (https://docs.github.com/en/free-pro-team@latest/github/managing-your-work-on-github/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword)
-->

This PR adds support for having a terminal-based context for the LightningCLI. This works by adding the paren pid in the connection folder.

Furthermore, every time a command runs, it will clean out the dead connections.

Fixes #\<issue_number>

### Does your PR introduce any breaking changes? If yes, please list them.

<!-- FILL IN or None -->

## Before submitting

- [x] Was this **discussed/approved** via a GitHub issue? (not for typos and docs)
- [x] Did you read the [contributor guideline](https://github.com/Lightning-AI/lightning/blob/master/.github/CONTRIBUTING.md), **Pull Request** section?
- [x] Did you make sure your **PR does only one thing**, instead of bu
[... cut ...]
```

This fix changes 9 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/lightning_app/cli/commands/app_commands.py`: `from lightning_app.cli.commands.connection import _install_missing_requirements, _resolve_command_path`
- in `src/lightning_app/cli/commands/connection.py`: `if not package_available(req):`

Patch of `src/lightning_app/cli/commands/app_commands.py` in this fix:

```diff
@@ -4,16 +4,26 @@
 
 import requests
 
-from lightning_app.cli.commands.connection import _install_missing_requirements, _resolve_command_path
+from lightning_app.cli.commands.connection import (
+    _clean_lightning_connection,
+    _install_missing_requirements,
+    _resolve_command_path,
+)
 from lightning_app.utilities.cli_helpers import _LightningAppOpenAPIRetriever
 from lightning_app.utilities.commands.base import _download_command
 from lightning_app.utilities.enum import OpenAPITags
 
 
+def _is_running_help(argv) -> bool:
+    return argv[-1] in ["--help", "-"] if argv else False
+
+
 def _run_app_command(app_name: str, app_id: Optional[str]):
     """Execute a function in a running App from its name."""
     # 1: Collect the url and comments from the running application
-    running_help = sys.argv[-1] == "--help"
+    _clean_lightning_connection()
+
+    running_help = _is_running_help(sys.argv)
 
     retriever = _LightningAppOpenAPIRetriever(app_id, use_cache=running_help)
 
@@ -33,6 +43,13 @@ def _run_app_command(app_name: str, app_id: Optional[str]):
     for command in list(retriever.api_commands):
         if command in full_command:
             has_found = True
+            for value in sys.argv:
+                if value == command and "_" in value:
+                    print(
+                        f"The command `{value}` was provided with an underscore and it isn't allowed."
+                        f"Instead, use `lightning {value.replace('_', ' ')}`."
+                    )
+                    sys.exit(0)
             break
 
     if not has_found:
@@ -50,13 +67,13 @@ def _run_app_command(app_name: str, app_id: Optional[str]):
     except ModuleNotFoundError:
         _install_missing_requirements(retriever, fail_if_missing=True)
 
-    if sys.argv[-1] != "--help":
+    if running_help:
         print("Your command execution was successful.")
 
 
 def _handle_command_without_client(command: str, metadata: Dict, url: str) -> None:
     supported_params = list(metadata["parameters"])
-    if "--help" == sys.argv[-1]:
+    if _is_running_help(sys.argv):
         print(f"Usage: lightning {command} [ARGS]...")
         print(" ")
[... cut ...]
```

Patch of `src/lightning_app/cli/commands/connection.py` in this fix:

```diff
@@ -6,6 +6,7 @@
 from typing import List, Optional, Tuple
 
 import click
+import psutil
 from lightning_utilities.core.imports import package_available
 
 from lightning_app.utilities.cli_helpers import _LightningAppOpenAPIRetriever
@@ -14,20 +15,24 @@
 from lightning_app.utilities.log import get_logfile
 from lightning_app.utilities.network import LightningClient
 
+_HOME = os.path.expanduser("~")
+_PPID = str(psutil.Process(os.getpid()).ppid())
+_LIGHTNING_CONNECTION = os.path.join(_HOME, ".lightning", "lightning_connection")
+_LIGHTNING_CONNECTION_FOLDER = os.path.join(_LIGHTNING_CONNECTION, _PPID)
+
 
 @click.argument("app_name_or_id", required=True)
 @click.option("-y", "--yes", required=False, is_flag=True, help="Whether to download the commands automatically.")
 def connect(app_name_or_id: str, yes: bool = False):
     """Connect to a Lightning App."""
     from lightning_app.utilities.commands.base import _download_command
 
-    home = os.path.expanduser("~")
-    lightning_folder = os.path.join(home, ".lightning", "lightning_connection")
+    _clean_lightning_connection()
 
-    if not os.path.exists(lightning_folder):
-        os.makedirs(lightning_folder)
+    if not os.path.exists(_LIGHTNING_CONNECTION_FOLDER):
+        os.makedirs(_LIGHTNING_CONNECTION_FOLDER)
 
-    connected_file = os.path.join(lightning_folder, "connect.txt")
+    connected_file = os.path.join(_LIGHTNING_CONNECTION_FOLDER, "connect.txt")
 
     if os.path.exists(connected_file):
         with open(connected_file) as f:
@@ -52,7 +57,7 @@ def connect(app_name_or_id: str, yes: bool = False):
         if retriever.api_commands is None:
             raise Exception(f"The commands weren't found. Is your app {app_name_or_id} running ?")
 
-        commands_folder = os.path.join(lightning_folder, "commands")
+        commands_folder = os.path.join(_LIGHTNING_CONNECTION_FOLDER, "commands")
         if not os.path.exists(commands_folder):
             os.makedirs(commands_folder)
 
@@ -108,7 +113,7 @@ def connect(app_name_or_id: str, yes: bool = False):
             click.echo(" ")
 
         if yes:
-            commands_folder = os.path.join(lightning_folder, "commands")
+            c
[... cut ...]
```

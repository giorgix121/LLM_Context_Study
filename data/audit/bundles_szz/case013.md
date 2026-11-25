# case013: Lightning-AI/lightning 4acb10f981a5

Sampled file (the only file the models saw): `src/lightning_app/utilities/commands/base.py` · committed 2022-10-19 17:34:35-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Add support for command descriptions (#15193)
```

## Diff of the sampled file

```diff
@@ -35,6 +35,8 @@ class ClientCommand:
 
     def __init__(self, method: Callable, requirements: Optional[List[str]] = None) -> None:
         self.method = method
+        if not self.DESCRIPTION:
+            self.DESCRIPTION = self.method.__doc__ or ""
         flow = getattr(method, "__self__", None)
         self.owner = flow.name if flow else None
         self.requirements = requirements
@@ -218,10 +220,13 @@ def _process_requests(app, request: Union[APIRequest, CommandRequest]) -> None:
 
 def _collect_open_api_extras(command) -> Dict:
     if not isinstance(command, ClientCommand):
+        if command.__doc__ is not None:
+            return {"description": command.__doc__}
         return {}
     return {
         "cls_path": inspect.getfile(command.__class__),
         "cls_name": command.__class__.__name__,
+        "description": command.DESCRIPTION,
     }
```

## Other files changed by this commit (11)

- `docs/source-app/workflows/build_command_line_interface/cli.rst` (+1 −1)
- `docs/source-app/workflows/build_command_line_interface/cli_client.rst` (+1 −1)
- `docs/source-app/workflows/build_command_line_interface/commands/notebook/run.py` (+2 −0)
- `docs/source-app/workflows/build_command_line_interface/example_command.py` (+1 −0)
- `examples/app_commands_and_api/app.py` (+2 −0)
- `examples/app_commands_and_api/command.py` (+3 −0)
- `src/lightning_app/CHANGELOG.md` (+1 −0)
- `src/lightning_app/cli/commands/connection.py` (+23 −6)
- `src/lightning_app/utilities/cli_helpers.py` (+4 −0)
- `tests/tests_app/cli/jsons/connect_1.json` (+1 −1)
- `tests/tests_app/cli/test_connect.py` (+6 −6)

## Fix commits that the dataset links to this commit (2)

### Fix 1: 320bca95dd5b (2022-10-20) · pull request #15196: [App] Enable help without running application

Pull-request labels: bug, ready to be merged, app (removed)

Commit message:

```
[App] Enable help without running application (#15196)
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

This PR enables getting CLI help when connected to an app even if the app isn't running right now.

Fixes #\<issue_number>

### Does your PR introduce any breaking changes? If yes, please list them.

<!-- FILL IN or None -->

## Before submitting

- [x] Was this **discussed/approved** via a GitHub issue? (not for typos and docs)
- [x] Did you read the [contributor guideline](https://github.com/Lightning-AI/lightning/blob/master/.github/CONTRIBUTING.md), **Pull Request** section?
- [x] Did you make sure your **PR does only one thing**, instead of bundling different changes together?
- [x] Did you make sure to **update the documentation** with your changes? (if necessar
[... cut ...]
```

This fix changes 7 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/lightning_app/cli/commands/connection.py`: `_write_commands_metadata(api_commands)`
- in `tests/tests_app/cli/test_connect.py`: `"  command with client    A command with a client.",`; `"  command without client A command without a client.",`; `"  nested command         A nested command.",`

Patch of `src/lightning_app/cli/commands/connection.py` in this fix:

```diff
@@ -5,7 +5,7 @@
 
 import click
 
-from lightning_app.utilities.cli_helpers import _retrieve_application_url_and_available_commands
+from lightning_app.utilities.cli_helpers import _LightningAppOpenAPIRetriever
 from lightning_app.utilities.cloud import _get_project
 from lightning_app.utilities.network import LightningClient
 
@@ -42,18 +42,21 @@ def connect(app_name_or_id: str, yes: bool = False):
         if app_name_or_id != "localhost":
             raise Exception("You need to pass localhost to connect to the local Lightning App.")
 
-        _, api_commands, __cached__ = _retrieve_application_url_and_available_commands(None)
+        retriever = _LightningAppOpenAPIRetriever(None)
 
-        if api_commands is None:
+        if retriever.api_commands is None:
             raise Exception(f"The commands weren't found. Is your app {app_name_or_id} running ?")
 
         commands_folder = os.path.join(lightning_folder, "commands")
         if not os.path.exists(commands_folder):
             os.makedirs(commands_folder)
 
-        _write_commands_metadata(api_commands)
+        _write_commands_metadata(retriever.api_commands)
 
-        for command_name, metadata in api_commands.items():
+        with open(os.path.join(commands_folder, "openapi.json"), "w") as f:
+            json.dump(retriever.openapi, f)
+
+        for command_name, metadata in retriever.api_commands.items():
             if "cls_path" in metadata:
                 target_file = os.path.join(commands_folder, f"{command_name.replace(' ','_')}.py")
                 _download_command(
@@ -63,7 +66,8 @@ def connect(app_name_or_id: str, yes: bool = False):
                     None,
                     target_file=target_file,
                 )
-                click.echo(f"Storing `{command_name}` under {target_file}")
+                repr_command_name = command_name.replace("_", " ")
+                click.echo(f"Find the `{repr_command_name}` command under {target_file}.")
                 click.echo(f"You can review all the downloaded commands under {commands_folder} folder.")
             else:
                 with open(os.path.join(commands_folder, f"{command_name}.txt"), "w") as f:
[... cut ...]
```

Patch of `tests/tests_app/cli/test_connect.py` in this fix:

```diff
@@ -5,7 +5,6 @@
 
 import click
 import pytest
-import requests
 
 from lightning_app import _PACKAGE_ROOT
 from lightning_app.cli.commands.connection import (
@@ -36,6 +35,8 @@ def test_connect_disconnect_local(monkeypatch):
 
     messages = []
 
+    disconnect()
+
     def fn(msg):
         messages.append(msg)
 
@@ -44,11 +45,9 @@ def fn(msg):
     response = MagicMock()
     response.status_code = 200
     response.json.return_value = data
-    monkeypatch.setattr(requests, "get", MagicMock(return_value=response))
+    monkeypatch.setattr(cli_helpers.requests, "get", MagicMock(return_value=response))
     connect("localhost", True)
     assert _retrieve_connection_to_an_app() == ("localhost", None)
-    commands = _list_app_commands()
-    assert commands == ["command with client", "command without client", "nested command"]
     command_path = _resolve_command_path("nested_command")
     assert not os.path.exists(command_path)
     command_path = _resolve_command_path("command_with_client")
@@ -57,17 +56,9 @@ def fn(msg):
     s = "/" if sys.platform != "win32" else "\\"
     command_folder_path = f"{home}{s}.lightning{s}lightning_connection{s}commands"
     expected = [
-        f"Storing `command_with_client` under {command_folder_path}{s}command_with_client.py",
+        f"Find the `command with client` command under {command_folder_path}{s}command_with_client.py.",
         f"You can review all the downloaded commands under {command_folder_path} folder.",
         "You are connected to the local Lightning App.",
-        "Usage: lightning [OPTIONS] COMMAND [ARGS]...",
-        "",
-        "  --help     Show this message and exit.",
-        "",
-        "Lightning App Commands",
-        "  command with client    A command with a client.",
-        "  command without client A command without a client.",
-        "  nested command         A nested command.",
     ]
     assert messages == expected
 
@@ -114,7 +105,7 @@ def fn(msg):
     response = MagicMock()
     response.status_code = 200
     response.json.return_value = data
-    monkeypatch.setattr(requests, "get", MagicMock(return_value=response))
+    monkeypatch.setattr(cli_helpers.requests, "
[... cut ...]
```

### Fix 2: 6a72a15a62bf (2022-10-20) · pull request #15198: [App] Automate missing requirements installation for CLI

Pull-request labels: bug, ready to be merged, app (removed)

Commit message:

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

This PR adds support for installing ClientCommand requirements when missing.

This is done during the connect phase. If the user provides `--yes`, it is automatically installed.

### Does your PR introduce any breaking changes? If yes, please list them.

<!-- FILL IN or None -->

## Before submitting

- [x] Was this **discussed/approved** via a GitHub issue? (not for typos and docs)
- [x] Did you read the [contributor guideline](https://github.com/Lightning-AI/lightning/blob/master/.github/CONTRIBUTING.md), **Pull Request** section?
- [x] Did you make sure your **PR does only one thing**, instead of bundling different changes together?
- [x] Did you make sure to **upd
[... cut ...]
```

This fix changes 11 files. Lines it removes that the commit above had added:

- in the sampled file: `"description": command.DESCRIPTION,`; `if not self.DESCRIPTION:`; `self.DESCRIPTION = self.method.__doc__ or ""`
- in `docs/source-app/workflows/build_command_line_interface/commands/notebook/run.py`: `DESCRIPTION = "Run a Notebook."`
- in `examples/app_commands_and_api/command.py`: `DESCRIPTION = "A command with a client."`

Patch of the sampled file in this fix:

```diff
@@ -4,6 +4,7 @@
 import os.path as osp
 import shutil
 import sys
+import traceback
 from getpass import getuser
 from importlib.util import module_from_spec, spec_from_file_location
 from tempfile import gettempdir
@@ -34,15 +35,15 @@ def makedirs(path: str):
 
 class ClientCommand:
 
-    DESCRIPTION = ""
+    description: str = ""
+    requirements: List[str] = []
 
-    def __init__(self, method: Callable, requirements: Optional[List[str]] = None) -> None:
+    def __init__(self, method: Callable):
         self.method = method
-        if not self.DESCRIPTION:
-            self.DESCRIPTION = self.method.__doc__ or ""
-        flow = getattr(method, "__self__", None)
+        if not self.description:
+            self.description = self.method.__doc__ or ""
+        flow = getattr(self.method, "__self__", None)
         self.owner = flow.name if flow else None
-        self.requirements = requirements
         self.models: Optional[Dict[str, BaseModel]] = None
         self.app_url = None
         self._state = None
@@ -73,7 +74,9 @@ def invoke_handler(self, config: Optional[BaseModel] = None) -> Dict[str, Any]:
                 detail = str(resp.json())
             except Exception:
                 detail = "Internal Server Error"
-            raise HTTPException(status_code=resp.status_code, detail=detail)
+            print(f"Failed with status code {resp.status_code}. Detail: {detail}")
+            sys.exit(0)
+
         return resp.json()
 
     def _to_dict(self):
@@ -121,7 +124,7 @@ def _download_command(
     mod = module_from_spec(spec)
     sys.modules[cls_name] = mod
     spec.loader.exec_module(mod)
-    command = getattr(mod, cls_name)(method=None, requirements=[])
+    command = getattr(mod, cls_name)(method=None)
     if tmpdir and os.path.exists(tmpdir):
         shutil.rmtree(tmpdir)
     return command
@@ -208,8 +211,8 @@ def _process_api_request(app, request: APIRequest) -> None:
     except HTTPException as e:
         logger.error(repr(e))
         response = RequestResponse(status_code=e.status_code, content=e.detail)
-    except Exception as e:
-        logger.error(repr(e))
+    except Exception:
+        logger.error(traceback.print_exc())
         response = RequestResponse(status_code=500)
     app.api_response_queue.put({"response": response, "id": request.id})
 
@@ -226,8 +229,8 @@ def _process_command_requests(app, request: CommandRequest) -> None:
                 except HTTPException as e:
                     logger.error(repr(e))
                     response = RequestResponse(status_code=e.status_code, content=e.detail)
-                except Exception as e:
-                    logger.error(repr(e))
+                except Exception:
+                    logger.error(traceback.print_exc())
                     response = RequestResponse(status_code=500)
                 app.api_response_queue.put({"response": response, "id": request.id})
 
@@ -245,11 +248,15 @@ def _collect_open_api_extras(command) -> Dict:
         if command.__doc__ is not None:
             return {"description": command.__doc__}
         return {}
-    return {
+
+    extras = {
         "cls_path": inspect.getfile(command.__class__),
         "cls_name": command.__class__.__name__,
-        "description": command.DESCRIPTION,
+        "description": command.description,
     }
+    if command.requirements:
+        extras.update({"requirements": command.requirements})
+    return extras
 
 
 def _commands_to_api(commands: List[Dict[str, Union[Callable, ClientCommand]]]) -> List:
```

Patch of `docs/source-app/workflows/build_command_line_interface/commands/notebook/run.py` in this fix:

```diff
@@ -13,7 +13,7 @@ class RunNotebookConfig(BaseModel):
 
 class RunNotebook(ClientCommand):
 
-    DESCRIPTION = "Run a Notebook."
+    description = "Run a Notebook."
 
     def run(self):
         # 1. Define your own argument parser. You can use argparse, click, etc...
```

Patch of `examples/app_commands_and_api/command.py` in this fix:

```diff
@@ -11,7 +11,7 @@ class CustomConfig(BaseModel):
 
 class CustomCommand(ClientCommand):
 
-    DESCRIPTION = "A command with a client."
+    description = "A command with a client."
 
     def run(self):
         parser = ArgumentParser()
```

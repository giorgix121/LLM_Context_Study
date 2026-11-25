# case116: Lightning-AI/lightning c81a71c90807

File: `src/lightning_app/cli/commands/connection.py` · committed 2022-09-13 06:43:15-01:00 · SZZ label: RISKY

## Commit message

```
Lightning App Fixes from Training Studio App dev (#14532)

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

* update

* update

* update

* update

* update

* update
```

## Diff of the target file

```diff
@@ -33,7 +33,8 @@ def connect(app_name_or_id: str, yes: bool = False):
             else:
                 click.echo(f"You are already connected to the cloud Lightning App: {app_name_or_id}.")
         else:
-            click.echo("You are already connected to a Lightning App. Please, use `lightning disconnect`.")
+            disconnect()
+            connect(app_name_or_id, yes)
 
     elif app_name_or_id.startswith("localhost"):
```

## Lines SZZ blamed (line numbers in the new version)

```
   36              disconnect()
   37              connect(app_name_or_id, yes)
```

## Candidate fixes (1 later commits to this file remove a blamed line; 14 later commits up to 2023-06-30 checked)

### Candidate 1: e522a12d177f (2022-12-14)

Message:

```
[App] Improve lightning connect experience (#16035)
```

Removed blamed lines: `connect(app_name_or_id, yes)`

Patch of this file:

```diff
@@ -8,6 +8,7 @@
 import click
 import psutil
 from lightning_utilities.core.imports import package_available
+from rich.progress import Progress
 
 from lightning_app.utilities.cli_helpers import _LightningAppOpenAPIRetriever
 from lightning_app.utilities.cloud import _get_project
@@ -16,15 +17,33 @@
 from lightning_app.utilities.network import LightningClient
 
 _HOME = os.path.expanduser("~")
-_PPID = str(psutil.Process(os.getpid()).ppid())
+_PPID = os.getenv("LIGHTNING_CONNECT_PPID", str(psutil.Process(os.getpid()).ppid()))
 _LIGHTNING_CONNECTION = os.path.join(_HOME, ".lightning", "lightning_connection")
 _LIGHTNING_CONNECTION_FOLDER = os.path.join(_LIGHTNING_CONNECTION, _PPID)
 
 
 @click.argument("app_name_or_id", required=True)
-@click.option("-y", "--yes", required=False, is_flag=True, help="Whether to download the commands automatically.")
-def connect(app_name_or_id: str, yes: bool = False):
-    """Connect to a Lightning App."""
+def connect(app_name_or_id: str):
+    """Connect your local terminal to a running lightning app.
+
+    After connecting, the lightning CLI will respond to commands exposed by the app.
+
+    Example:
+
+    \b
+    # connect to an app named pizza-cooker-123
+    lightning connect pizza-cooker-123
+    \b
+    # this will now show the commands exposed by pizza-cooker-123
+    lightning --help
+    \b
+    # while connected, you can run the cook-pizza command exposed
+    # by pizza-cooker-123.BTW, this should arguably generate an exception :-)
+    lightning cook-pizza --flavor pineapple
+    \b
+    # once done, disconnect and go back to the standard lightning CLI commands
+    lightning disconnect
+    """
     from lightning_app.utilities.commands.base import _download_command
 
     _clean_lightning_connection()
@@ -47,51 +66,64 @@ def connect(app_name_or_id: str, yes: bool = False):
                 click.echo(f"You are already connected to the cloud Lightning App: {app_name_or_id}.")
         else:
             disconnect()
-            connect(app_name_or_id, yes)
+            connect(app_name_or_id)
 
     elif app_name_or_id.startswith("localhost"):
 
-        if app_name_or_id != "localhost":
-            raise Exception("You need to pass localhost to connect to the local Lightning App.")
+        with Progress() as progress_bar:
+            connecting = progress_bar.add_task("[magenta]Setting things up for you...", total=1.0)
 
-        retriever = _LightningAppOpenAPIRetriever(None)
+            if app_name_or_id != "localhost":
+                raise Exception("You need to pass localhost to connect to the local Lightning App.")
 
-        if retriever.api_commands is None:
-            raise Exception(f"The commands weren't found. Is your app {app_name_or_id} running ?")
+            retriever = _LightningAppOpenAPIRetriever(None)
 
-        commands_folder = os.path.join(_LIGHTNING_CONNECTION_FOLDER, "commands")
-        if not os.path.exists(commands_folder):
-            os.makedirs(commands_folder)
+            if retriever.api_commands is None:
+                raise Exception(f"Connection wasn't successful. Is your app {app_name_or_id} running?")
 
-        _write_commands_metadata(retriever.api_commands)
+            increment = 1 / (1 + len(retriever.api_commands))
 
-        with open(os.path.join(commands_folder, "openapi.json"), "w") as f:
-            json.dump(retriever.openapi, f)
+            progress_bar.update(connecting, advance=increment)
 
-        _install_missing_requirements(retriever, yes)
+            commands_folder = os.path.join(_LIGHTNING_CONNECTION_FOLDER, "commands")
+            if not os.path.exists(commands_folder):
+                os.makedirs(commands_folder)
 
-        for command_name, metadata in retriever.api_commands.items():
-            if "cls_path" in metadata:
-                target_file = os.path.join(commands_folder, f"{command_name.replace(' ','_')}.py")
-                _download_command(
-                    command_name,
-                    metadata["cls_path"],
-                    metadata["cls_name"],
-                    None,
-                    target_file=target_file,
-                )
-                repr_command_name = command_name.replace("_", " ")
-                click.echo(f"Storing `{repr_command_name}` at {target_file}")
-            else:
-                with open(os.path.join(commands_folder, f"{command_name}.txt"), "w") as f:
-                    f.write(command_name)
+            _write_commands_metadata(retriever.api_commands)
+
+            with open(os.path.join(commands_folder, "openapi.json"), "w") as f:
+                json.dump(retriever.openapi, f)
 
-        click.echo(f"You can review all the downloaded commands at {commands_folder}")
+            _install_missing_requirements(retriever)
+
+            for command_name, metadata in retriever.api_commands.items():
+                if "cls_path" in metadata:
+                    target_file = os.path.join(commands_folder, f"{command_name.replace(' ','_')}.py")
+                    _download_command(
+                        command_name,
+                        metadata["cls_path"],
+                        metadata["cls_name"],
+                        None,
+                        target_file=target_file,
+                    )
+                else:
+                    with open(os.path.join(commands_folder, f"{command_name}.txt"), "w") as f:
+                        f.write(command_name)
+
+                progress_bar.update(connecting, advance=increment)
 
         with open(connected_file, "w") as f:
             f.write(app_name_or_id + "\n")
 
-        click.echo("You are connected to the local Lightning App.")
+        click.echo("The lightning CLI now responds to app commands. Use 'lightning --help' to see them.")
+        click.echo(" ")
+
+        Popen(
+            f"LIGHTNING_CONNECT_PPID={_PPID} {sys.executable} -m lightning --help",
+            shell=True,
+            stdout=sys.
```

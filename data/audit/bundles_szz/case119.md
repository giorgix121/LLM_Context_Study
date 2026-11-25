# case119: Lightning-AI/lightning 2f5060963aeb

Sampled file (the only file the models saw): `src/lightning_app/utilities/cli_helpers.py` · committed 2022-10-20 09:56:44-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
[LAI] Rename instances of "lightning_app" and "pytorch_lightning" (#15208)

* rename instances of lightning_app and pytorch_lightning
* solve failing azure tests
* wrong runif import
* lit_app

Co-authored-by: Jirka <jirka.borovec@seznam.cz>
```

## Diff of the sampled file

```diff
@@ -107,25 +107,23 @@ def _retrieve_application_url_and_available_commands(app_id_or_name_or_url: Opti
     else:
         client = LightningClient()
         project = _get_project(client)
-        list_lightningapps = client.lightningapp_instance_service_list_lightningapp_instances(
-            project_id=project.project_id
-        )
+        list_apps = client.lightningapp_instance_service_list_lightningapp_instances(project_id=project.project_id)
 
-        lightningapp_names = [lightningapp.name for lightningapp in list_lightningapps.lightningapps]
+        app_names = [lightningapp.name for lightningapp in list_apps.lightningapps]
 
         if not app_id_or_name_or_url:
-            raise Exception(f"Provide an application name, id or url with --app_id=X. Found {lightningapp_names}")
+            raise Exception(f"Provide an application name, id or url with --app_id=X. Found {app_names}")
 
-        for lightningapp in list_lightningapps.lightningapps:
-            if lightningapp.id == app_id_or_name_or_url or lightningapp.name == app_id_or_name_or_url:
-                if lightningapp.status.url == "":
+        for app in list_apps.lightningapps:
+            if app.id == app_id_or_name_or_url or app.name == app_id_or_name_or_url:
+                if app.status.url == "":
                     raise Exception("The application is starting. Try in a few moments.")
-                resp = requests.get(lightningapp.status.url + "/openapi.json")
+                resp = requests.get(app.status.url + "/openapi.json")
                 if resp.status_code != 200:
                     raise Exception(
                         "The server didn't process the request properly. " "Try once your application is ready."
                     )
-                return lightningapp.status.url, _extract_command_from_openapi(resp.json()), lightningapp.id
+                return app.status.url, _extract_command_from_openapi(resp.json()), app.id
     return None, None, None
```

## Other files changed by this commit (10)

- `src/lightning_app/cli/commands/connection.py` (+2 −4)
- `src/lightning_app/cli/lightning_cli.py` (+2 −2)
- `src/lightning_app/runners/cloud.py` (+6 −6)
- `src/lightning_app/testing/helpers.py` (+3 −3)
- `src/lightning_app/testing/testing.py` (+13 −13)
- `tests/tests_app/utilities/packaging/test_build_spec.py` (+6 −4)
- `tests/tests_app/utilities/test_introspection.py` (+3 −4)
- `tests/tests_app/utilities/test_tracer.py` (+1 −1)
- `tests/tests_app_examples/components/python/test_scripts.py` (+2 −2)
- `tests/tests_app_examples/test_quick_start.py` (+1 −1)

## Fix commits that the dataset links to this commit (1)

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

- in the sampled file: `if app.id == app_id_or_name_or_url or app.name == app_id_or_name_or_url:`; `return app.status.url, _extract_command_from_openapi(resp.json()), app.id`
- in other files of the commit: none

Patch of the sampled file in this fix:

```diff
@@ -1,3 +1,5 @@
+import json
+import os
 import re
 from typing import Dict, Optional
 
@@ -81,50 +83,116 @@ def _extract_command_from_openapi(openapi_resp: Dict) -> Dict[str, Dict[str, str
     return {p.replace("/command/", ""): _get_metadata_from_openapi(openapi_resp["paths"], p) for p in command_paths}
 
 
-def _retrieve_application_url_and_available_commands(app_id_or_name_or_url: Optional[str]):
-    """This function is used to retrieve the current url associated with an id."""
-
-    if _is_url(app_id_or_name_or_url):
-        url = app_id_or_name_or_url
-        assert url
-        resp = requests.get(url + "/openapi.json")
-        if resp.status_code != 200:
-            raise Exception(f"The server didn't process the request properly. Found {resp.json()}")
-        return url, _extract_command_from_openapi(resp.json()), None
-
-    # 2: If no identifier has been provided, evaluate the local application
-    if app_id_or_name_or_url is None:
-        try:
+class _LightningAppOpenAPIRetriever:
+    def __init__(
+        self,
+        app_id_or_name_or_url: Optional[str],
+        use_cache: bool = False,
+    ):
+        """This class encapsulates the logic to collect the openapi.json file from the app to use the CLI Commands.
+
+        Arguments:
+            app_id_or_name_or_url: An identified for the app.
+            use_cache: Whether to load the openapi spec from the cache.
+        """
+        self.app_id_or_name_or_url = app_id_or_name_or_url
+        self.url = None
+        self.openapi = None
+        self.api_commands = None
+        self.app_id = None
+        home = os.path.expanduser("~")
+        if use_cache:
+            cache_openapi = os.path.join(home, ".lightning", "lightning_connection", "commands", "openapi.json")
+            if os.path.exists(cache_openapi):
+                with open(cache_openapi) as f:
+                    self.openapi = json.load(f)
+                self.api_commands = _extract_command_from_openapi(self.openapi)
+        else:
+            self._collect_open_api_json()
+            if self.openapi:
+                self.api_commands = _extract_command_from_openapi(self.openapi)
+
+    def is_alive(self) -> bool:
+        """Returns whether the Lightning App Rest API is available."""
+        if self.url is None:
+            self._maybe_find_url()
+        if self.url is None:
+            return False
+        resp = requests.get(self.url)
+        return resp.status_code == 200
+
+    def _maybe_find_url(self):
+        """Tries to resolve the app url from the provided `app_id_or_name_or_url`."""
+        if _is_url(self.app_id_or_name_or_url):
+            self.url = self.app_id_or_name_or_url
+            assert self.url
+            return
+
+        if self.app_id_or_name_or_url is None:
             url = f"http://localhost:{APP_SERVER_PORT}"
-            resp = requests.get(f"{url}/openapi.json")
-            if resp.status_code != 200:
-                raise Exception(f"The server didn't process the request properly. Found {resp.json()}")
-            return url, _extract_command_from_openapi(resp.json()), None
-        except requests.exceptions.ConnectionError:
-            pass
+            resp = requests.get(f"{self.url}/openapi.json")
+            if resp.status_code == 200:
+                self.url = url
+                return
+
+        app = self._maybe_find_matching_cloud_app()
+        if app:
+            self.url = app.status.url
 
-    # 3: If an identified was provided or the local evaluation has failed, evaluate the cloud.
-    else:
+    def _maybe_find_matching_cloud_app(self):
+        """Tries to resolve the app url from the provided `app_id_or_name_or_url`."""
         client = LightningClient()
         project = _get_project(client)
         list_apps = client.lightningapp_instance_service_list_lightningapp_instances(project_id=project.project_id)
 
         app_names = [lightningapp.name for lightningapp in list_apps.lightningapps]
 
-        if not app_id_or_name_or_url:
+        if not self.app_id_or_name_or_url:
             raise Exception(f"Provide an application name, id or url with --app_id=X. Found {app_names}")
 
         for app in list_apps.lightningapps:
-            if app.id == app_id_or_name_or_url or app.name == app_id_or_name_or_url:
+            if app.id == self.app_id_or_name_or_url or app.name == self.app_id_or_name_or_url:
+                if app.status.url == "":
+                    raise Exception(
[... cut ...]
```

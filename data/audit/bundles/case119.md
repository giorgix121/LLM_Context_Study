# case119: Lightning-AI/lightning 2f5060963aeb

File: `src/lightning_app/utilities/cli_helpers.py` · committed 2022-10-20 09:56:44-01:00 · SZZ label: RISKY

## Commit message

```
[LAI] Rename instances of "lightning_app" and "pytorch_lightning" (#15208)

* rename instances of lightning_app and pytorch_lightning
* solve failing azure tests
* wrong runif import
* lit_app

Co-authored-by: Jirka <jirka.borovec@seznam.cz>
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
  110          list_apps = client.lightningapp_instance_service_list_lightningapp_instances(project_id=project.project_id)
  112          app_names = [lightningapp.name for lightningapp in list_apps.lightningapps]
  115              raise Exception(f"Provide an application name, id or url with --app_id=X. Found {app_names}")
  117          for app in list_apps.lightningapps:
  118              if app.id == app_id_or_name_or_url or app.name == app_id_or_name_or_url:
  119                  if app.status.url == "":
  121                  resp = requests.get(app.status.url + "/openapi.json")
  126                  return app.status.url, _extract_command_from_openapi(resp.json()), app.id
```

## Candidate fixes (2 later commits to this file remove a blamed line; 14 later commits up to 2023-06-30 checked)

### Candidate 1: 320bca95dd5b (2022-10-20)

Message:

```
[App] Enable help without running application (#15196)
```

Removed blamed lines: `if app.id == app_id_or_name_or_url or app.name == app_id_or_name_or_url:`; `return app.status.url, _extract_command_from_openapi(resp.json()), app.id`

Patch of this file:

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
+                    raise Exception("The application is starting. Try in a few moments.")
+                return app
+
+    def _collect_open_api_json(self):
+        """This function is used to retrieve the current url associated with an id."""
+
+        if _is_url(self.app_id_or_name_or_url):
+            self.url = self.app_id_or_name_or_url
+            assert self.url
+            resp = requests.get(self.url + "/openapi.json")
+            if resp.status_code != 200:
+                raise Exception(f"The server didn't process the request properly. Found {resp.json()}")
+            self.openapi = resp.json()
+            return
+
+        # 2: If no identifier has been provided, evaluate the local application
+        if self.app_id_or_name_or_url is None:
+            try:
+                self.url = f"http://localhost:{APP_SERVER_PORT}"
+                resp = requests.get(f"{self.url}/openapi.json")
+                if resp.status_code != 200:
+                    raise Exception(f"The server didn't process the request properly. Found {resp.json()}")
+                self.openapi = resp.json()
+            except requests.exceptions.ConnectionError:
+                pass
+
+        # 3: If an identified was provided or the local evaluation has failed, evaluate the cloud.
+        else:
+            app = self._maybe_find_matching_cloud_app()
+            if app:
                 if app.status.url == "":
                     raise Exception("The application is starting. Try in a few moments.")
```

### Candidate 2: 5da74847e2c8 (2022-10-27)

Message:

```
[App] Show logs command to be standalone and re-usable (#15343)
```

Removed blamed lines: `raise Exception(f"Provide an application name, id or url with --app_id=X. Found {app_names}")`

Patch of this file:

```diff
@@ -1,6 +1,7 @@
 import json
 import os
 import re
+import sys
 from typing import Dict, Optional
 
 import arrow
@@ -153,12 +154,14 @@ def _maybe_find_matching_cloud_app(self):
         app_names = [lightningapp.name for lightningapp in list_apps.lightningapps]
 
         if not self.app_id_or_name_or_url:
-            raise Exception(f"Provide an application name, id or url with --app_id=X. Found {app_names}")
+            print(f"ERROR: Provide an application name, id or url with --app_id=X. Found {app_names}")
+            sys.exit(0)
 
         for app in list_apps.lightningapps:
             if app.id == self.app_id_or_name_or_url or app.name == self.app_id_or_name_or_url:
                 if app.status.url == "":
-                    raise Exception("The application is starting. Try in a few moments.")
+                    print("The application is starting. Try in a few moments.")
+                    sys.exit(0)
                 return app
 
     def _collect_open_api_json(self):
@@ -169,7 +172,8 @@ def _collect_open_api_json(self):
             assert self.url
             resp = requests.get(self.url + "/openapi.json")
             if resp.status_code != 200:
-                raise Exception(f"The server didn't process the request properly. Found {resp.json()}")
+                print(f"ERROR: The server didn't process the request properly. Found {resp.json()}")
+                sys.exit(0)
             self.openapi = resp.json()
             return
```

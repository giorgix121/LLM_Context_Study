# case063: Lightning-AI/lightning d579733b081e

File: `src/lightning_app/utilities/cli_helpers.py` · committed 2022-09-14 09:44:59-01:00 · SZZ label: RISKY

## Commit message

```
Lightning cloud client call with key word arguments (#14685)
```

## Diff of the target file

```diff
@@ -103,7 +103,9 @@ def _retrieve_application_url_and_available_commands(app_id_or_name_or_url: Opti
     else:
         client = LightningClient()
         project = _get_project(client)
-        list_lightningapps = client.lightningapp_instance_service_list_lightningapp_instances(project.project_id)
+        list_lightningapps = client.lightningapp_instance_service_list_lightningapp_instances(
+            project_id=project.project_id
+        )
 
         lightningapp_names = [lightningapp.name for lightningapp in list_lightningapps.lightningapps]
```

## Lines SZZ blamed (line numbers in the new version)

```
  106          list_lightningapps = client.lightningapp_instance_service_list_lightningapp_instances(
  107              project_id=project.project_id
  108          )
```

## Candidate fixes (1 later commits to this file remove a blamed line; 16 later commits up to 2023-06-30 checked)

### Candidate 1: 2f5060963aeb (2022-10-20)

Message:

```
[LAI] Rename instances of "lightning_app" and "pytorch_lightning" (#15208)

* rename instances of lightning_app and pytorch_lightning
* solve failing azure tests
* wrong runif import
* lit_app

Co-authored-by: Jirka <jirka.borovec@seznam.cz>
```

Removed blamed lines: `list_lightningapps = client.lightningapp_instance_service_list_lightningapp_instances(`; `project_id=project.project_id`

Patch of this file:

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

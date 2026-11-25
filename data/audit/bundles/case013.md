# case013: Lightning-AI/lightning 4acb10f981a5

File: `src/lightning_app/utilities/commands/base.py` · committed 2022-10-19 17:34:35-01:00 · SZZ label: RISKY

## Commit message

```
Add support for command descriptions (#15193)
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
   38          if not self.DESCRIPTION:
   39              self.DESCRIPTION = self.method.__doc__ or ""
  223          if command.__doc__ is not None:
  224              return {"description": command.__doc__}
  229          "description": command.DESCRIPTION,
```

## Candidate fixes (1 later commits to this file remove a blamed line; 8 later commits up to 2023-06-30 checked)

### Candidate 1: 6a72a15a62bf (2022-10-20)

Message:

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

Removed blamed lines: `"description": command.DESCRIPTION,`; `if not self.DESCRIPTION:`; `self.DESCRIPTION = self.method.__doc__ or ""`

Patch of this file:

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

# case083: Lightning-AI/lightning 6a72a15a62bf

File: `src/lightning_app/utilities/cli_helpers.py` · committed 2022-10-20 10:02:13-01:00 · SZZ label: RISKY

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

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
   62      requirements = paths[path]["post"].get("requirements", None)
   75      if description:
   76          metadata["requirements"] = requirements
   77  
```

## Candidate fixes (0 later commits to this file remove a blamed line; 13 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

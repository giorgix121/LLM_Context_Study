# case098: Lightning-AI/lightning 4322f538746f

File: `src/lightning_lite/wrappers.py` · committed 2022-10-23 00:26:43-01:00 · SZZ label: RISKY

## Commit message

```
Update mypy version (#15161)

* update mypy version
* type-ignore-comments
* more mypy-fix
* import-fix
* Update Lite too
* simpler implementation for flatten dict
* Fix rich progress
* Simplify rich test
* True None

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
Co-authored-by: Carlos Mocholí <carlossmocholi@gmail.com>
```

## Diff of the target file

```diff
@@ -112,12 +112,12 @@ class _LiteModule(_DeviceDtypeModuleMixin):
         ...
 
     @overload
-    def state_dict(self, *, prefix: str = ..., keep_vars: bool = ...) -> T_destination:
+    def state_dict(self, *, prefix: str = ..., keep_vars: bool = ...) -> Dict[str, Any]:
         ...
 
     def state_dict(
         self, destination: Optional[T_destination] = None, prefix: str = "", keep_vars: bool = False
-    ) -> Optional[T_destination]:
+    ) -> Optional[Dict[str, Any]]:
         return self._original_module.state_dict(
             destination=destination,  # type: ignore[type-var]
             prefix=prefix,
```

## Lines SZZ blamed (line numbers in the new version)

```
  115      def state_dict(self, *, prefix: str = ..., keep_vars: bool = ...) -> Dict[str, Any]:
  120      ) -> Optional[Dict[str, Any]]:
```

## Candidate fixes (0 later commits to this file remove a blamed line; 2 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

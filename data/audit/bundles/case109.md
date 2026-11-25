# case109: pandas-dev/pandas 0106c2652990

File: `pandas/core/internals/__init__.py` · committed 2022-10-14 08:43:38-01:00 · SZZ label: RISKY

## Commit message

```
REVERT caching in find_stack_level (#49053)

Revert "PERF cache find_stack_level (#48023)"

This reverts commit 2f8d0a36703e81e4dca52ca9fe4f58c910c1b304.

Co-authored-by: MarcoGorelli <>
```

## Diff of the target file

```diff
@@ -41,7 +41,6 @@ __all__ = [
 
 
 def __getattr__(name: str):
-    import inspect
     import warnings
 
     from pandas.util._exceptions import find_stack_level
@@ -51,7 +50,7 @@ def __getattr__(name: str):
             "CategoricalBlock is deprecated and will be removed in a future version. "
             "Use ExtensionBlock instead.",
             DeprecationWarning,
-            stacklevel=find_stack_level(inspect.currentframe()),
+            stacklevel=find_stack_level(),
         )
         from pandas.core.internals.blocks import CategoricalBlock
```

## Lines SZZ blamed (line numbers in the new version)

```
   53              stacklevel=find_stack_level(),
```

## Candidate fixes (1 later commits to this file remove a blamed line; 2 later commits up to 2023-06-30 checked)

### Candidate 1: aae800d988bc (2022-11-01)

Message:

```
DEPR: internals (#49392)

* DEPR: internals

* bump fastparquet minimum
```

Removed blamed lines: `stacklevel=find_stack_level(),`

Patch of this file:

```diff
@@ -38,22 +38,3 @@
     # this is preserved here for downstream compatibility (GH-33892)
     "create_block_manager_from_blocks",
 ]
-
-
-def __getattr__(name: str):
-    import warnings
-
-    from pandas.util._exceptions import find_stack_level
-
-    if name == "CategoricalBlock":
-        warnings.warn(
-            "CategoricalBlock is deprecated and will be removed in a future version. "
-            "Use ExtensionBlock instead.",
-            DeprecationWarning,
-            stacklevel=find_stack_level(),
-        )
-        from pandas.core.internals.blocks import CategoricalBlock
-
-        return CategoricalBlock
-
-    raise AttributeError(f"module 'pandas.core.internals' has no attribute '{name}'")
```

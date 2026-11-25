# case109: pandas-dev/pandas 0106c2652990

Sampled file (the only file the models saw): `pandas/core/internals/__init__.py` · committed 2022-10-14 08:43:38-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
REVERT caching in find_stack_level (#49053)

Revert "PERF cache find_stack_level (#48023)"

This reverts commit 2f8d0a36703e81e4dca52ca9fe4f58c910c1b304.

Co-authored-by: MarcoGorelli <>
```

## Diff of the sampled file

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

## Other files changed by this commit (97)

- `doc/source/development/contributing_codebase.rst` (+1 −1)
- `pandas/_config/config.py` (+2 −5)
- `pandas/_libs/parsers.pyx` (+2 −2)
- `pandas/_libs/tslib.pyx` (+1 −2)
- `pandas/_libs/tslibs/conversion.pyx` (+1 −2)
- `pandas/_libs/tslibs/nattype.pyx` (+2 −3)
- `pandas/_libs/tslibs/offsets.pyx` (+4 −5)
- `pandas/_libs/tslibs/parsing.pyx` (+2 −3)
- `pandas/_libs/tslibs/period.pyx` (+1 −2)
- `pandas/_libs/tslibs/timedeltas.pyx` (+4 −5)
- `pandas/_libs/tslibs/timestamps.pyx` (+10 −11)
- `pandas/_testing/asserters.py` (+5 −6)
- `pandas/compat/_optional.py` (+1 −2)
- `pandas/core/accessor.py` (+1 −2)
- `pandas/core/algorithms.py` (+3 −5)
- `pandas/core/apply.py` (+2 −2)
- `pandas/core/arraylike.py` (+2 −5)
- `pandas/core/arrays/arrow/_arrow_utils.py` (+1 −4)
- `pandas/core/arrays/base.py` (+1 −1)
- `pandas/core/arrays/categorical.py` (+15 −16)
- `pandas/core/arrays/datetimelike.py` (+5 −6)
- `pandas/core/arrays/datetimes.py` (+7 −8)
- `pandas/core/arrays/sparse/array.py` (+5 −8)
- `pandas/core/arrays/sparse/dtype.py` (+1 −2)
- `pandas/core/base.py` (+1 −2)
- `pandas/core/common.py` (+2 −4)
- `pandas/core/computation/align.py` (+1 −4)
- `pandas/core/computation/eval.py` (+1 −2)
- `pandas/core/computation/expressions.py` (+1 −2)
- `pandas/core/config_init.py` (+2 −3)
- `pandas/core/construction.py` (+3 −4)
- `pandas/core/describe.py` (+1 −2)
- `pandas/core/dtypes/astype.py` (+3 −3)
- `pandas/core/dtypes/cast.py` (+7 −8)
- `pandas/core/dtypes/common.py` (+2 −3)
- `pandas/core/dtypes/concat.py` (+1 −2)
- `pandas/core/dtypes/inference.py` (+1 −2)
- `pandas/core/frame.py` (+13 −16)
- `pandas/core/generic.py` (+25 −36)
- `pandas/core/groupby/generic.py` (+2 −3)
- ... and 57 more

## Fix commits that the dataset links to this commit (2)

### Fix 1: 050a1a2e22bf (2022-11-03) · pull request #49486: DEPR: Change str.replace(regex) from True to False & single behavior

Pull-request labels: Deprecate

Commit message:

```
DEPR: Change str.replace(regex) from True to False & single behavior (#49486)

* DEPR: Change str.replace(regex) from True to False & single behavior

* Add versionnchanged
```

Pull-request description:

```
- [x] closes #24804 (Replace xxxx with the GitHub issue number)


Introduced in #36695
```

This fix changes 4 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `pandas/core/strings/accessor.py`: `warnings.warn(msg, FutureWarning, stacklevel=find_stack_level())`

Patch of `pandas/core/strings/accessor.py` in this fix:

```diff
@@ -1323,7 +1323,7 @@ def replace(
         n: int = -1,
         case: bool | None = None,
         flags: int = 0,
-        regex: bool | None = None,
+        regex: bool = False,
     ):
         r"""
         Replace each occurrence of pattern/regex in the Series/Index.
@@ -1351,16 +1351,14 @@ def replace(
         flags : int, default 0 (no flags)
             Regex module flags, e.g. re.IGNORECASE. Cannot be set if `pat` is a compiled
             regex.
-        regex : bool, default True
+        regex : bool, default False
             Determines if the passed-in pattern is a regular expression:
 
             - If True, assumes the passed-in pattern is a regular expression.
             - If False, treats the pattern as a literal string
             - Cannot be set to False if `pat` is a compiled regex or `repl` is
               a callable.
 
-            .. versionadded:: 0.23.0
-
         Returns
         -------
         Series or Index of object
@@ -1444,20 +1442,6 @@ def replace(
         2    NaN
         dtype: object
         """
-        if regex is None:
-            if isinstance(pat, str) and any(c in pat for c in ".+*|^$?[](){}\\"):
-                # warn only in cases where regex behavior would differ from literal
-                msg = (
-                    "The default value of regex will change from True to False "
-                    "in a future version."
-                )
-                if len(pat) == 1:
-                    msg += (
-                        " In addition, single character regular expressions will "
-                        "*not* be treated as literal strings when regex=True."
-                    )
-                warnings.warn(msg, FutureWarning, stacklevel=find_stack_level())
-
         # Check whether repl is valid (GH 13438, GH 15055)
         if not (isinstance(repl, str) or callable(repl)):
             raise TypeError("repl must be a string or callable")
@@ -1476,14 +1460,6 @@ def replace(
         elif callable(repl):
             raise ValueError("Cannot use a callable replacement when regex=False")
 
-        # The current behavior is to treat single character patterns as literal strings,
-
[... cut ...]
```

### Fix 2: ab6562a20bd8 (2022-10-29) · pull request #49321: DEPR: remove inplace arg in Categorical methods

Pull-request labels: Deprecate

Commit message:

```
DEPR: remove inplace arg in Categorical methods (#49321)

* deprecate inplace arg in categorical methods

* fix tests

* add back test

* doc fix

* doc fixes

* avoid constructing new objects on every iteration

* cleanup
```

Pull-request description:

```
- [x] closes #37643
- [x] [Tests added and passed](https://pandas.pydata.org/pandas-docs/dev/development/contributing_codebase.html#writing-tests) if fixing a bug or adding a new feature
- [x] All [code checks passed](https://pandas.pydata.org/pandas-docs/dev/development/contributing_codebase.html#pre-commit).
- [x] Added [type annotations](https://pandas.pydata.org/pandas-docs/dev/development/contributing_codebase.html#type-hints) to new arguments/methods/functions.
- [x] Added an entry in the latest `doc/source/whatsnew/v2.0.0.rst` file if fixing a bug or adding a new feature.

I combined these into a single PR given they're all roughly the same deprecation of removing the `inplace` arg from Categorical methods. This can be split into smaller PRs if preferred. 

Deprecations introduced in: #37981, #41118, #41133, #47834
```

This fix changes 10 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `pandas/core/arrays/categorical.py`: `stacklevel=find_stack_level(),`

Patch of `pandas/core/arrays/categorical.py` in this fix:

```diff
@@ -15,11 +15,7 @@
     cast,
     overload,
 )
-from warnings import (
-    catch_warnings,
-    simplefilter,
-    warn,
-)
+from warnings import warn
 
 import numpy as np
 
@@ -31,10 +27,6 @@
     lib,
 )
 from pandas._libs.arrays import NDArrayBacked
-from pandas._libs.lib import (
-    NoDefault,
-    no_default,
-)
 from pandas._typing import (
     ArrayLike,
     AstypeArg,
@@ -48,7 +40,6 @@
     type_t,
 )
 from pandas.compat.numpy import function as nv
-from pandas.util._decorators import deprecate_nonkeyword_arguments
 from pandas.util._exceptions import find_stack_level
 from pandas.util._validators import validate_bool_kwarg
 
@@ -729,8 +720,6 @@ def categories(self) -> Index:
         unique and the number of items in the new categories must be the same
         as the number of items in the old categories.
 
-        Assigning to `categories` is a inplace operation!
-
         Raises
         ------
         ValueError
@@ -748,17 +737,6 @@ def categories(self) -> Index:
         """
         return self.dtype.categories
 
-    @categories.setter
-    def categories(self, categories) -> None:
-        warn(
-            "Setting categories in-place is deprecated and will raise in a "
-            "future version. Use rename_categories instead.",
-            FutureWarning,
-            stacklevel=find_stack_level(),
-        )
-
-        self._set_categories(categories)
-
     @property
     def ordered(self) -> Ordered:
         """
@@ -839,123 +817,43 @@ def _set_dtype(self, dtype: CategoricalDtype) -> Categorical:
         codes = recode_for_categories(self.codes, self.categories, dtype.categories)
         return type(self)(codes, dtype=dtype, fastpath=True)
 
-    @overload
-    def set_ordered(
-        self, value, *, inplace: NoDefault | Literal[False] = ...
-    ) -> Categorical:
-        ...
-
-    @overload
-    def set_ordered(self, value, *, inplace: Literal[True]) -> None:
-        ...
-
-    @overload
-    def set_ordered(self, value, *, inplace: bool) -> Categorical | None:
-        ...
-
-    @deprecate_nonkeyword_arguments(version=None, allowed_args=["self", "value"])
-    def set_ordered(
-        self, value, inplace: bool | No
[... cut ...]
```

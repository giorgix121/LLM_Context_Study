# case127: pandas-dev/pandas 77d4c3eee7c6

Sampled file (the only file the models saw): `pandas/core/groupby/categorical.py` · committed 2022-10-07 06:05:29-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
PERF: df.groupby(categorical, sort=False) (#48976)

* refactor using codes

* PREF: df.groupby(categorical, sort=False)

* Add pr number

* remove comment
```

## Diff of the sampled file

```diff
@@ -75,21 +75,21 @@ def recode_for_groupby(
         return c, None
 
     # sort=False should order groups in as-encountered order (GH-8868)
-    cat = c.unique()
 
-    # See GH-38140 for block below
-    # exclude nan from indexer for categories
-    take_codes = cat.codes[cat.codes != -1]
-    if cat.ordered:
-        take_codes = np.sort(take_codes)
-    cat = cat.set_categories(cat.categories.take(take_codes))
-
-    # But for groupby to work, all categories should be present,
-    # including those missing from the data (GH-13179), which .unique()
-    # above dropped
-    cat = cat.add_categories(c.categories[~c.categories.isin(cat.categories)])
-
-    return c.reorder_categories(cat.categories), None
+    # xref GH:46909: Re-ordering codes faster than using (set|add|reorder)_categories
+    all_codes = np.arange(c.categories.nunique(), dtype=np.int8)
+    # GH 38140: exclude nan from indexer for categories
+    unique_notnan_codes = unique1d(c.codes[c.codes != -1])
+    if c.ordered:
+        unique_notnan_codes = np.sort(unique_notnan_codes)
+    if len(all_codes) > len(unique_notnan_codes):
+        # GH 13179: All categories need to be present, even if missing from the data
+        missing_codes = np.setdiff1d(all_codes, unique_notnan_codes, assume_unique=True)
+        take_codes = np.concatenate((unique_notnan_codes, missing_codes))
+    else:
+        take_codes = unique_notnan_codes
+
+    return Categorical(c, c.unique().categories.take(take_codes)), None
 
 
 def recode_from_groupby(
```

## Other files changed by this commit (1)

- `doc/source/whatsnew/v1.6.0.rst` (+1 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 1294b193f0d0 (2022-10-24) · pull request #49131: BUG: groupby reorders categorical categories

Pull-request labels: Bug, Groupby, Categorical

Commit message:

```
BUG: groupby reorders categorical categories (#49131)

* BUG: groupby reorders categorical categories

* Tests and whatsnew

* type-ignore

* GH#

* Add test

* Add TODO

* GH#

* fixups

* Revert test change; catch warnings
```

Pull-request description:

```
Ref: #48749

- [x] [Tests added and passed](https://pandas.pydata.org/pandas-docs/dev/development/contributing_codebase.html#writing-tests) if fixing a bug or adding a new feature
- [x] All [code checks passed](https://pandas.pydata.org/pandas-docs/dev/development/contributing_codebase.html#pre-commit).
- [x] Added [type annotations](https://pandas.pydata.org/pandas-docs/dev/development/contributing_codebase.html#type-hints) to new arguments/methods/functions.
- [x] Added an entry in the latest `doc/source/whatsnew/vX.X.X.rst` file if fixing a bug or adding a new feature.

~Still needs more tests and a whatsnew~
```

This fix changes 5 files. Lines it removes that the commit above had added:

- in the sampled file: `all_codes = np.arange(c.categories.nunique(), dtype=np.int8)`
- in other files of the commit: none

Patch of the sampled file in this fix:

```diff
@@ -1,7 +1,5 @@
 from __future__ import annotations
 
-from typing import TYPE_CHECKING
-
 import numpy as np
 
 from pandas.core.algorithms import unique1d
@@ -11,9 +9,6 @@
     recode_for_categories,
 )
 
-if TYPE_CHECKING:
-    from pandas.core.indexes.api import CategoricalIndex
-
 
 def recode_for_groupby(
     c: Categorical, sort: bool, observed: bool
@@ -77,7 +72,7 @@ def recode_for_groupby(
     # sort=False should order groups in as-encountered order (GH-8868)
 
     # xref GH:46909: Re-ordering codes faster than using (set|add|reorder)_categories
-    all_codes = np.arange(c.categories.nunique(), dtype=np.int8)
+    all_codes = np.arange(c.categories.nunique())
     # GH 38140: exclude nan from indexer for categories
     unique_notnan_codes = unique1d(c.codes[c.codes != -1])
     if c.ordered:
@@ -90,32 +85,3 @@ def recode_for_groupby(
         take_codes = unique_notnan_codes
 
     return Categorical(c, c.unique().categories.take(take_codes)), None
-
-
-def recode_from_groupby(
-    c: Categorical, sort: bool, ci: CategoricalIndex
-) -> CategoricalIndex:
-    """
-    Reverse the codes_to_groupby to account for sort / observed.
-
-    Parameters
-    ----------
-    c : Categorical
-    sort : bool
-        The value of the sort parameter groupby was called with.
-    ci : CategoricalIndex
-        The codes / categories to recode
-
-    Returns
-    -------
-    CategoricalIndex
-    """
-    # we re-order to the original category orderings
-    if sort:
-        # error: "CategoricalIndex" has no attribute "set_categories"
-        return ci.set_categories(c.categories)  # type: ignore[attr-defined]
-
-    # we are not sorting, so add unobserved to the end
-    new_cats = c.categories[~c.categories.isin(ci.categories)]
-    # error: "CategoricalIndex" has no attribute "add_categories"
-    return ci.add_categories(new_cats)  # type: ignore[attr-defined]
```

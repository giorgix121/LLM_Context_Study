# case127: pandas-dev/pandas 77d4c3eee7c6

File: `pandas/core/groupby/categorical.py` · committed 2022-10-07 06:05:29-01:00 · SZZ label: RISKY

## Commit message

```
PERF: df.groupby(categorical, sort=False) (#48976)

* refactor using codes

* PREF: df.groupby(categorical, sort=False)

* Add pr number

* remove comment
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
   79      # xref GH:46909: Re-ordering codes faster than using (set|add|reorder)_categories
   80      all_codes = np.arange(c.categories.nunique(), dtype=np.int8)
   81      # GH 38140: exclude nan from indexer for categories
   82      unique_notnan_codes = unique1d(c.codes[c.codes != -1])
   83      if c.ordered:
   84          unique_notnan_codes = np.sort(unique_notnan_codes)
   85      if len(all_codes) > len(unique_notnan_codes):
   86          # GH 13179: All categories need to be present, even if missing from the data
   87          missing_codes = np.setdiff1d(all_codes, unique_notnan_codes, assume_unique=True)
   88          take_codes = np.concatenate((unique_notnan_codes, missing_codes))
   89      else:
   90          take_codes = unique_notnan_codes
   91  
   92      return Categorical(c, c.unique().categories.take(take_codes)), None
```

## Candidate fixes (3 later commits to this file remove a blamed line; 4 later commits up to 2023-06-30 checked)

### Candidate 1: 1294b193f0d0 (2022-10-24)

Message:

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

Removed blamed lines: `all_codes = np.arange(c.categories.nunique(), dtype=np.int8)`

Patch of this file:

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

### Candidate 2: eea9e751619b (2022-11-07)

Message:

```
BUG: groupby with CategoricalIndex doesn't include unobserved categories (#49373)

* BUG: groupby with CategoricalIndex doesn't include unobserved categories

* Test fixup

* cleanup

* Remove TODO

* Add GH reference

* Add GH reference
```

Removed blamed lines: `if c.ordered:`

Patch of this file:

```diff
@@ -53,7 +53,7 @@ def recode_for_groupby(
         unique_codes = unique1d(c.codes)
 
         take_codes = unique_codes[unique_codes != -1]
-        if c.ordered:
+        if c.ordered or sort:
             take_codes = np.sort(take_codes)
 
         # we recode according to the uniques
```

### Candidate 3: 9c059187893a (2022-11-10)

Message:

```
BUG: groupby with sort=False still sorts an ordered categorical (#49613)

* BUG: groupby with sort=False still sorts an ordered categorical

* Add versionchanged
```

Removed blamed lines: `if c.ordered:`

Patch of this file:

```diff
@@ -53,7 +53,7 @@ def recode_for_groupby(
         unique_codes = unique1d(c.codes)
 
         take_codes = unique_codes[unique_codes != -1]
-        if c.ordered or sort:
+        if sort:
             take_codes = np.sort(take_codes)
 
         # we recode according to the uniques
@@ -75,7 +75,7 @@ def recode_for_groupby(
     all_codes = np.arange(c.categories.nunique())
     # GH 38140: exclude nan from indexer for categories
     unique_notnan_codes = unique1d(c.codes[c.codes != -1])
-    if c.ordered:
+    if sort:
         unique_notnan_codes = np.sort(unique_notnan_codes)
     if len(all_codes) > len(unique_notnan_codes):
         # GH 13179: All categories need to be present, even if missing from the data
```

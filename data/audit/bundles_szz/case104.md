# case104: django/django e911e0996f10

Sampled file (the only file the models saw): `django/utils/numberformat.py` · committed 2022-09-12 13:54:12-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Fixed #34000 -- Fixed numberformat.format() crash on empty strings.
```

## Diff of the sampled file

```diff
@@ -25,6 +25,8 @@ def format(
         module in locale.localeconv() LC_NUMERIC grouping (e.g. (3, 2, 0)).
     * thousand_sep: Thousand separator symbol (for example ",")
     """
+    if number == "":
+        return mark_safe(number)
     use_grouping = (
         use_l10n or (use_l10n is None and settings.USE_L10N)
     ) and settings.USE_THOUSAND_SEPARATOR
```

## Other files changed by this commit (1)

- `tests/utils_tests/test_numberformat.py` (+3 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 07ebef566f75 (2022-09-12) · pull request #16046: Fixed #34000 -- Fixed numberformat.format() crash on empty strings.

Commit message:

```
Refs #34000 -- Optimized handling None values in numberformat.format().
```

Pull-request description:

```
When (if str_number[0] == "-") encountered a number field that's a database NULL, e.g. when formatting for the admin list_display,
this caused an IndexError: string index out of range
```

This fix changes 2 files. Lines it removes that the commit above had added:

- in the sampled file: `if number == "":`
- in other files of the commit: none

Patch of the sampled file in this fix:

```diff
@@ -25,7 +25,7 @@ def format(
         module in locale.localeconv() LC_NUMERIC grouping (e.g. (3, 2, 0)).
     * thousand_sep: Thousand separator symbol (for example ",")
     """
-    if number == "":
+    if number is None or number == "":
         return mark_safe(number)
     use_grouping = (
         use_l10n or (use_l10n is None and settings.USE_L10N)
```

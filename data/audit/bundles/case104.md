# case104: django/django e911e0996f10

File: `django/utils/numberformat.py` · committed 2022-09-12 13:54:12-01:00 · SZZ label: RISKY

## Commit message

```
Fixed #34000 -- Fixed numberformat.format() crash on empty strings.
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
   28      if number == "":
   29          return mark_safe(number)
```

## Candidate fixes (0 later commits to this file remove a blamed line; 3 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

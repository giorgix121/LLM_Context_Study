# case085: getsentry/sentry 4992db3403f1

File: `src/sentry/snuba/metrics_enhanced_performance.py` · committed 2022-10-25 06:10:19-01:00 · SZZ label: RISKY

## Commit message

```
feat(metrics-layer): Add the metrics_layer dataset (#40450)

- This adds a metrics_layer dataset to the QueryBuilder which builds
metric layer snql, instead of direct snql
- This calls the metrics_layer get_series function, which doubles as a
table query
- This introduces a metric layer feature flag so we can gradually roll
out this change
- Several of the tests are currently xfailed due to bugs in the metric
layer
- ~One is currently failing until this change merges:
https://github.com/getsentry/sentry/pull/40448~
- Groupby xfails are fixed by:
https://github.com/getsentry/sentry/pull/40313
```

## Diff of the target file

```diff
@@ -30,6 +30,7 @@ def query(
     dry_run=False,
     transform_alias_to_input_format=False,
     has_metrics: bool = True,
+    use_metrics_layer: bool = False,
 ):
     metrics_compatible = not equations or dry_run
 
@@ -52,6 +53,8 @@ def query(
                 functions_acl,
                 dry_run,
                 transform_alias_to_input_format,
+                has_metrics,
+                use_metrics_layer,
             )
         # raise Invalid Queries since the same thing will happen with discover
         except InvalidSearchQuery as error:
```

## Lines SZZ blamed (line numbers in the new version)

```
   33      use_metrics_layer: bool = False,
   56                  has_metrics,
   57                  use_metrics_layer,
```

## Candidate fixes (0 later commits to this file remove a blamed line; 5 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

# case132: getsentry/sentry a10312cf1f10

File: `src/sentry/snuba/metrics/naming_layer/mapping.py` · committed 2022-09-08 10:52:53-01:00 · SZZ label: RISKY

## Commit message

```
feat(metrics): Support field aliasing on metrics layer [TET-322 TET-356] (#38509)

Adds logic that allows for aliasing on all instances of `MetricField`.
If `MetricField` references an metrics expression or an instance of
`SingleEntityDerivedMetric` then, the alias is propagated down to query
level, and the response has the aliased names. If however, it references
an instance of `CompositeEntityDerivedMetric`, then it creates alias
that corresponds to the mri of the constituent suffixed with
`__CHILD_OF__<parent_alias>`, and then post query the value of the
composite derived metric is computed from the children values. This
alias suffixing behaviour allows us to avoid naming collisions when
requesting the same composite dervied metric more than once but with
different arguments. This PR also adds meta type for composite entity
derived metric.

ToDo:
- Will handle aliasing groupBy aliasing in a subsequent PR
```

## Diff of the target file

```diff
@@ -70,9 +70,11 @@ def get_public_name_from_mri(internal_name: Union[TransactionMRI, SessionMRI, st
 
 
 def get_operation_with_public_name(operation: Optional[str], metric_mri: str) -> str:
-    if operation is None:
-        return get_public_name_from_mri(metric_mri)
-    return f"{operation}({get_public_name_from_mri(metric_mri)})"
+    return (
+        f"{operation}({get_public_name_from_mri(metric_mri)})"
+        if operation is not None
+        else metric_mri
+    )
 
 
 def parse_expression(name: str) -> Tuple[Optional[str], str]:
```

## Lines SZZ blamed (line numbers in the new version)

```
   73      return (
   74          f"{operation}({get_public_name_from_mri(metric_mri)})"
   75          if operation is not None
   76          else metric_mri
   77      )
```

## Candidate fixes (0 later commits to this file remove a blamed line; 4 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

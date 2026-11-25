# case143: getsentry/sentry 1c4547bbb73e

Sampled file (the only file the models saw): `src/sentry/snuba/metrics/mqb_query_transformer.py` · committed 2022-10-25 06:11:30-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
fix(metric-layer): Allow environment filtering (#40470)

- This handles a bug where environment wasn't being allowed as a filter
in the qb transformer
- Also raise an error so its less transparent when a filter isn't
allowed
```

## Diff of the sampled file

```diff
@@ -186,6 +186,10 @@ def _get_mq_dict_params_from_where(query_where):
                     mq_dict["start"] = condition.rhs
                 elif condition.op == Op.LT:
                     mq_dict["end"] = condition.rhs
+            elif condition.lhs.name == "tags[environment]":
+                where.append(condition)
+            else:
+                raise MQBQueryTransformationException(f"Unsupported column for where {condition}")
         elif isinstance(condition.lhs, Function):
             if condition.lhs.function in DERIVED_OPS:
                 if not DERIVED_OPS[condition.lhs.function].can_filter:
```

## Other files changed by this commit (0)

(none)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 30a70ee7ba04 (2022-11-02) · pull request #40656: fix(MEP): Search by transformed transaction

Pull-request labels: Scope: Backend

Commit message:

```
fix(MEP): Search by transformed transaction (#40656)

- This fixes a bug where we weren't using the transformed transaction
for filtering which meant that transaction:<< unparameterized >> would
return nothing if the only bad transactions were null

Co-authored-by: getsantry[bot] <66042841+getsantry[bot]@users.noreply.github.com>
```

Pull-request description:

```
- This fixes a bug where we weren't using the transformed transaction for filtering which meant that transaction:<< unparameterized >> would return nothing if the only bad transactions were null
```

This fix changes 6 files. Lines it removes that the commit above had added:

- in the sampled file: `elif condition.lhs.name == "tags[environment]":`
- in other files of the commit: none

Patch of the sampled file in this fix:

```diff
@@ -186,7 +186,7 @@ def _get_mq_dict_params_from_where(query_where):
                     mq_dict["start"] = condition.rhs
                 elif condition.op == Op.LT:
                     mq_dict["end"] = condition.rhs
-            elif condition.lhs.name == "tags[environment]":
+            elif condition.lhs.name in ["tags[environment]", "tags[transaction]"]:
                 where.append(condition)
             else:
                 raise MQBQueryTransformationException(f"Unsupported column for where {condition}")
```

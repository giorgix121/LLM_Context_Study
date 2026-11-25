# case143: getsentry/sentry 1c4547bbb73e

File: `src/sentry/snuba/metrics/mqb_query_transformer.py` · committed 2022-10-25 06:11:30-01:00 · SZZ label: RISKY

## Commit message

```
fix(metric-layer): Allow environment filtering (#40470)

- This handles a bug where environment wasn't being allowed as a filter
in the qb transformer
- Also raise an error so its less transparent when a filter isn't
allowed
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
  189              elif condition.lhs.name == "tags[environment]":
  190                  where.append(condition)
  191              else:
  192                  raise MQBQueryTransformationException(f"Unsupported column for where {condition}")
```

## Candidate fixes (1 later commits to this file remove a blamed line; 8 later commits up to 2023-06-30 checked)

### Candidate 1: 30a70ee7ba04 (2022-11-02)

Message:

```
fix(MEP): Search by transformed transaction (#40656)

- This fixes a bug where we weren't using the transformed transaction
for filtering which meant that transaction:<< unparameterized >> would
return nothing if the only bad transactions were null

Co-authored-by: getsantry[bot] <66042841+getsantry[bot]@users.noreply.github.com>
```

Removed blamed lines: `elif condition.lhs.name == "tags[environment]":`

Patch of this file:

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

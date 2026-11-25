# case085: getsentry/sentry 4992db3403f1

Sampled file (the only file the models saw): `src/sentry/snuba/metrics_enhanced_performance.py` · committed 2022-10-25 06:10:19-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

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

## Diff of the sampled file

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

## Other files changed by this commit (9)

- `src/sentry/api/endpoints/organization_events.py` (+4 −0)
- `src/sentry/features/__init__.py` (+1 −0)
- `src/sentry/search/events/builder.py` (+86 −6)
- `src/sentry/search/events/datasets/field_aliases.py` (+19 −13)
- `src/sentry/search/events/datasets/metrics_layer.py` (+608 −0)
- `src/sentry/search/events/fields.py` (+2 −0)
- `src/sentry/snuba/discover.py` (+1 −0)
- `src/sentry/snuba/metrics_performance.py` (+4 −0)
- `tests/snuba/api/endpoints/test_organization_events_mep.py` (+45 −0)

## Fix commits that the dataset links to this commit (2)

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

- in the sampled file: none (the fix does not change this file)
- in `src/sentry/search/events/datasets/metrics_layer.py`: `)`; `Column(self.builder.resolve_column_name("transaction")), Op(operator), value`; `[],`; `return Condition(`

Patch of `src/sentry/search/events/datasets/metrics_layer.py` in this fix:

```diff
@@ -331,7 +331,9 @@ def function_converter(self) -> Mapping[str, fields.MetricsFunction]:
                     "count",
                     snql_metric_layer=lambda args, alias: Function(
                         "count",
-                        [],
+                        [
+                            Column(TransactionMRI.DURATION.value),
+                        ],
                         alias,
                     ),
                     default_result_type="integer",
@@ -500,9 +502,7 @@ def _transaction_filter_converter(self, search_filter: SearchFilter) -> Optional
                 raise IncompatibleMetricsQuery(f"Transaction value {value} in filter not found")
         value = resolved_value
 
-        return Condition(
-            Column(self.builder.resolve_column_name("transaction")), Op(operator), value
-        )
+        return Condition(self.builder.resolve_column("transaction"), Op(operator), value)
 
     # Query Functions
     def _resolve_percentile(
```

### Fix 2: c265d028329d (2022-11-02) · pull request #40887: perf(QueryBuilder): Use forward references to fix query builder circu…

Pull-request labels: Scope: Backend

Commit message:

```
perf(QueryBuilder): Use forward references to fix query builder circu… (#40887)

…lar import

The first attempt #40887 to split the imports under the various if
conditions didn't work. Instead it made everything slower (I'm not sure
why this is the case). This is inspired by
https://peps.python.org/pep-0484/#forward-references. This allows us
lift the import to the top so it is done at start up instead of during
the query.
```

Pull-request description:

```
…lar import

The first attempt #40887 to split the imports under the various if conditions didn't work. Instead it made everything slower (I'm not sure why this is the case). This is inspired by https://peps.python.org/pep-0484/#forward-references. This allows us lift the import to the top so it is done at start up instead of during the query.
```

This fix changes 10 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/sentry/search/events/builder.py`: `from sentry.search.events.datasets.metrics_layer import MetricsLayerDatasetConfig`
- in `src/sentry/search/events/datasets/field_aliases.py`: `builder: QueryBuilder, resolve_metric_index: bool = False`
- in `src/sentry/search/events/datasets/metrics_layer.py`: `def __init__(self, builder: MetricsQueryBuilder):`; `from sentry.search.events import constants, fields`; `from sentry.search.events.builder import MetricsQueryBuilder`

Patch of `src/sentry/search/events/builder.py` in this fix:

```diff
@@ -9,6 +9,7 @@
     Mapping,
     Match,
     Optional,
+    Protocol,
     Sequence,
     Set,
     Tuple,
@@ -70,6 +71,11 @@
     VALID_FIELD_PATTERN,
 )
 from sentry.search.events.datasets.base import DatasetConfig
+from sentry.search.events.datasets.discover import DiscoverDatasetConfig
+from sentry.search.events.datasets.metrics import MetricsDatasetConfig
+from sentry.search.events.datasets.metrics_layer import MetricsLayerDatasetConfig
+from sentry.search.events.datasets.profiles import ProfilesDatasetConfig
+from sentry.search.events.datasets.sessions import SessionsDatasetConfig
 from sentry.search.events.fields import (
     ColumnArg,
     FunctionDetails,
@@ -271,25 +277,15 @@ def load_config(
     ]:
         self.config: DatasetConfig
         if self.dataset in [Dataset.Discover, Dataset.Transactions, Dataset.Events]:
-            from sentry.search.events.datasets.discover import DiscoverDatasetConfig
-
             self.config = DiscoverDatasetConfig(self)
         elif self.dataset == Dataset.Sessions:
-            from sentry.search.events.datasets.sessions import SessionsDatasetConfig
-
             self.config = SessionsDatasetConfig(self)
         elif self.dataset in [Dataset.Metrics, Dataset.PerformanceMetrics]:
             if self.use_metrics_layer:
-                from sentry.search.events.datasets.metrics_layer import MetricsLayerDatasetConfig
-
                 self.config = MetricsLayerDatasetConfig(self)
             else:
-                from sentry.search.events.datasets.metrics import MetricsDatasetConfig
-
                 self.config = MetricsDatasetConfig(self)
         elif self.dataset == Dataset.Profiles:
-            from sentry.search.events.datasets.profiles import ProfilesDatasetConfig
-
             self.config = ProfilesDatasetConfig(self)
         else:
             raise NotImplementedError(f"Data Set configuration not found for {self.dataset}.")
@@ -2802,3 +2798,56 @@ def run_query(self, referrer: str, use_cache: bool = False) -> Any:
             "data": list(time_map.values()),
             "meta": [{"name": key, "type": value} for key, value in meta_dict.items()],
         }
+
+
+class ProfilesQueryBuilderPr
[... cut ...]
```

Patch of `src/sentry/search/events/datasets/field_aliases.py` in this fix:

```diff
@@ -1,3 +1,5 @@
+from __future__ import annotations
+
 from typing import Any, List, Tuple
 
 import sentry_sdk
@@ -6,13 +8,14 @@
 from sentry.discover.models import TeamKeyTransaction
 from sentry.exceptions import IncompatibleMetricsQuery
 from sentry.models import ProjectTeam
-from sentry.search.events import constants, fields
-from sentry.search.events.builder import QueryBuilder
+from sentry.search.events import builder, constants, fields
 from sentry.search.events.types import SelectType
 from sentry.utils.numbers import format_grouped_length
 
 
-def dry_run_default(builder: QueryBuilder, alias: str, *args: Any, **kwargs: Any) -> SelectType:
+def dry_run_default(
+    builder: builder.QueryBuilder, alias: str, *args: Any, **kwargs: Any
+) -> SelectType:
     """It doesn't really matter what we return here, the query won't be run
 
     This is so we can easily swap to something when we're dry running to prevent hitting postgres at all
@@ -21,7 +24,7 @@ def dry_run_default(builder: QueryBuilder, alias: str, *args: Any, **kwargs: Any
 
 
 def resolve_team_key_transaction_alias(
-    builder: QueryBuilder, resolve_metric_index: bool = False
+    builder: builder.QueryBuilder, resolve_metric_index: bool = False
 ) -> SelectType:
     team_key_transactions = get_team_transactions(builder, resolve_metric_index)
     if len(team_key_transactions) == 0:
@@ -38,7 +41,7 @@ def resolve_team_key_transaction_alias(
 
 
 def get_team_transactions(
-    builder: QueryBuilder, resolve_metric_index: bool = False
+    builder: builder.QueryBuilder, resolve_metric_index: bool = False
 ) -> List[Tuple[int, str]]:
     org_id = builder.params.get("organization_id")
     project_ids = builder.params.get("project_id")
@@ -84,7 +87,7 @@ def get_team_transactions(
     return team_key_transactions
 
 
-def resolve_project_slug_alias(builder: QueryBuilder, alias: str) -> SelectType:
+def resolve_project_slug_alias(builder: builder.QueryBuilder, alias: str) -> SelectType:
     builder.value_resolver_map[alias] = lambda project_id: builder.project_ids.get(project_id, "")
     builder.meta_resolver_map[alias] = "string"
     return AliasedExpression(exp=builder.column("project_id"),
[... cut ...]
```

Patch of `src/sentry/search/events/datasets/metrics_layer.py` in this fix:

```diff
@@ -7,8 +7,7 @@
 
 from sentry.api.event_search import SearchFilter
 from sentry.exceptions import IncompatibleMetricsQuery, InvalidSearchQuery
-from sentry.search.events import constants, fields
-from sentry.search.events.builder import MetricsQueryBuilder
+from sentry.search.events import builder, constants, fields
 from sentry.search.events.datasets import field_aliases, filter_aliases
 from sentry.search.events.datasets.metrics import MetricsDatasetConfig
 from sentry.search.events.types import SelectType, WhereType
@@ -17,7 +16,7 @@
 
 
 class MetricsLayerDatasetConfig(MetricsDatasetConfig):
-    def __init__(self, builder: MetricsQueryBuilder):
+    def __init__(self, builder: builder.MetricsQueryBuilder):
         self.builder = builder
 
     @property
```

# case132: getsentry/sentry a10312cf1f10

Sampled file (the only file the models saw): `src/sentry/snuba/metrics/naming_layer/mapping.py` · committed 2022-09-08 10:52:53-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

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

## Diff of the sampled file

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

## Other files changed by this commit (9)

- `src/sentry/snuba/metrics/datasource.py` (+3 −1)
- `src/sentry/snuba/metrics/fields/base.py` (+135 −45)
- `src/sentry/snuba/metrics/query.py` (+8 −0)
- `src/sentry/snuba/metrics/query_builder.py` (+57 −26)
- `tests/sentry/api/endpoints/test_organization_metric_data.py` (+0 −13)
- `tests/sentry/snuba/metrics/fields/test_base.py` (+170 −46)
- `tests/sentry/snuba/metrics/test_metrics_layer/test_metrics_enhanced_performance.py` (+234 −0)
- `tests/sentry/snuba/metrics/test_metrics_layer/test_release_health.py` (+85 −9)
- `tests/sentry/snuba/metrics/test_query_builder.py` (+69 −37)

## Fix commits that the dataset links to this commit (2)

### Fix 1: c67c560f667e (2022-10-06) · pull request #39660: feat(metrics): Standardize tests and fix overall flakiness [TET-437]

Pull-request labels: Scope: Backend

Commit message:

```
feat(metrics): Standardize tests and fix overall flakiness [TET-437] (#39660)
```

Pull-request description:

```
In this PR I propose a simple approach to standardize time management in our metrics layer tests. The refactor aims at solving the issues that led to flakiness in most tests.

The idea of this PR is to have a base class called `BaseMetricsLayerTestCase` that contains two methods:
* `now` -> this is an abstract method used to enforce a certain style with respect to getting current time.
* `store_metric_in_metrics_layer` -> this is a wrapper over the `store_metric` function that will automatically insert the metric at `now() - 1 second` in order to cover for right non-inclusivity in the `MetricsQuery`.
Each class the inherits `BaseMetricsLayerTestCase` must then use the `@freeze_time()` decorator at the class level, effectively freezing time for each method belonging to that class. The frozen time can be decided but we have provided a `DEFAULT_FROZEN_TIME` for simplicity and correctness.
* `build_metrics_query` -> this is a wrapper function that hides the `start` and `end` bounds from the query building and instead substitutes them with a simpler `before_now` that considers the `end` bound as always `self.now()`. It also simplifies the handling of `granularity` because it allows it t
[... cut ...]
```

This fix changes 5 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `tests/sentry/snuba/metrics/test_metrics_layer/test_metrics_enhanced_performance.py`: `end=now,`; `granularity=Granularity(granularity=3600),`; `granularity=Granularity(granularity=60),`; `import time`; `metrics_query = MetricsQuery(`; `now = timezone.now()`
- in `tests/sentry/snuba/metrics/test_metrics_layer/test_release_health.py`: `"interval": "1m",`; `"statsPeriod": "6m",`; `)`; `end=end,`; `from sentry.snuba.metrics import MetricField, MetricsQuery`; `from sentry.snuba.metrics.query_builder import QueryDefinition, get_date_range`

Patch of `tests/sentry/snuba/metrics/test_metrics_layer/test_metrics_enhanced_performance.py` in this fix:

```diff
@@ -2,7 +2,6 @@
 Metrics Service Layer Tests for Performance
 """
 import re
-import time
 from datetime import timedelta
 from unittest import mock
 
@@ -27,17 +26,18 @@
 from sentry.snuba.metrics.datasource import get_custom_measurements, get_series
 from sentry.snuba.metrics.naming_layer import TransactionMetricKey, TransactionMRI
 from sentry.snuba.metrics.query_builder import QueryDefinition, get_date_range
-from sentry.testutils import BaseMetricsTestCase, TestCase
-from sentry.testutils.cases import MetricsEnhancedPerformanceTestCase
+from sentry.testutils import TestCase
+from sentry.testutils.cases import BaseMetricsLayerTestCase, MetricsEnhancedPerformanceTestCase
 from sentry.testutils.helpers.datetime import before_now, iso_format
 
 pytestmark = pytest.mark.sentry_metrics
 
 
-class PerformanceMetricsLayerTestCase(TestCase, BaseMetricsTestCase):
-    def setUp(self):
-        super().setUp()
-        self.now = timezone.now()
+@freeze_time("2022-09-29 10:00:00")
+class PerformanceMetricsLayerTestCase(BaseMetricsLayerTestCase, TestCase):
+    @property
+    def now(self):
+        return timezone.now()
 
     def test_valid_filter_include_meta_derived_metrics(self):
         query_params = MultiValueDict(
@@ -73,20 +73,15 @@ def test_valid_filter_include_meta_derived_metrics(self):
     def test_alias_on_different_metrics_expression(self):
         for v_transaction, count in (("/foo", 1), ("/bar", 3), ("/baz", 2)):
             for value in [123.4] * count:
-                self.store_metric(
-                    org_id=self.organization.id,
-                    project_id=self.project.id,
-                    type="distribution",
+                self.store_performance_metric(
                     name=TransactionMRI.MEASUREMENTS_LCP.value,
                     tags={"transaction": v_transaction, "measurement_rating": "poor"},
-                    timestamp=int(time.time()),
                     value=value,
-                    use_case_id=UseCaseKey.PERFORMANCE,
                 )
 
-        metrics_query = MetricsQuery(
-            org_id=self.organization.id,
-            project_ids=[self.project.id],
+        metrics_query = self.build_metri
[... cut ...]
```

Patch of `tests/sentry/snuba/metrics/test_metrics_layer/test_release_health.py` in this fix:

```diff
@@ -4,21 +4,28 @@
 import time
 
 import pytest
+from django.utils import timezone
 from django.utils.datastructures import MultiValueDict
-from snuba_sdk import Granularity, Limit, Offset
+from freezegun import freeze_time
+from snuba_sdk import Limit, Offset
 
 from sentry.api.utils import InvalidParams
 from sentry.sentry_metrics.configuration import UseCaseKey
-from sentry.snuba.metrics import MetricField, MetricsQuery
+from sentry.snuba.metrics import MetricField
 from sentry.snuba.metrics.datasource import get_series
 from sentry.snuba.metrics.naming_layer import SessionMRI
-from sentry.snuba.metrics.query_builder import QueryDefinition, get_date_range
-from sentry.testutils import BaseMetricsTestCase, TestCase
+from sentry.snuba.metrics.query_builder import QueryDefinition
+from sentry.testutils import BaseMetricsLayerTestCase, TestCase
 
 pytestmark = pytest.mark.sentry_metrics
 
 
-class ReleaseHealthMetricsLayerTestCase(TestCase, BaseMetricsTestCase):
+@freeze_time("2022-09-29 10:00:00")
+class ReleaseHealthMetricsLayerTestCase(BaseMetricsLayerTestCase, TestCase):
+    @property
+    def now(self):
+        return timezone.now()
+
     def test_valid_filter_include_meta(self):
         self.create_release(version="foo", project=self.project)
         self.store_session(
@@ -80,55 +87,35 @@ def test_validate_include_meta_computes_meta_for_composite_derived_metrics(self)
         )
 
     def test_alias_on_composite_entity_derived_metric(self):
-        user_ts = time.time()
-        org_id = self.organization.id
-
         for tag_value, count_value in (
             ("errored_preaggr", 10),
             ("crashed", 2),
             ("abnormal", 4),
             ("init", 15),
         ):
-            self.store_metric(
-                org_id=org_id,
-                project_id=self.project.id,
-                type="counter",
-                name=str(SessionMRI.SESSION.value),
+            self.store_release_health_metric(
+                name=SessionMRI.SESSION.value,
                 tags={"session.status": tag_value},
-                timestamp=(user_ts // 60 - 4) * 60,
                 value=count_value,
-                use_case_id=UseCaseKey.RE
[... cut ...]
```

### Fix 2: f9bf16e7d663 (2022-09-22) · pull request #39143: fix(metrics): Add `freeze_time` to metrics layer tests

Commit message:

```
fix(metrics): Add `freeze_time` to metrics layer tests (#39143)
```

This fix changes 2 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `tests/sentry/snuba/metrics/test_metrics_layer/test_metrics_enhanced_performance.py`: `@freeze_time()`

Patch of `tests/sentry/snuba/metrics/test_metrics_layer/test_metrics_enhanced_performance.py` in this fix:

```diff
@@ -33,6 +33,7 @@
 pytestmark = pytest.mark.sentry_metrics
 
 
+@freeze_time()
 class PerformanceMetricsLayerTestCase(TestCase, BaseMetricsTestCase):
     def setUp(self):
         super().setUp()
@@ -240,7 +241,6 @@ def test_alias_on_same_metrics_expression_but_different_aliases(self):
             key=lambda elem: elem["name"],
         )
 
-    @freeze_time()
     def test_alias_on_single_entity_derived_metrics(self):
         for value, tag_value in (
             (3.4, TransactionStatusTagValue.OK.value),
```

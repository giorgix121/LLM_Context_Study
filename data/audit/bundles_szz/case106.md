# case106: getsentry/sentry e15af7965b42

Sampled file (the only file the models saw): `src/sentry/utils/silo/decorate_models_by_relation.py` · committed 2022-09-09 02:36:45-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
ref(hybrid): Rename customer silo to "region silo" (#38638)

In practice, we found that "customer" sounds too much like "control" and
was easy to confuse with it. "Region" here isn't intended to mean
strictly a geographic region, but can also mean a region of SaaS service
in which a single-tenant customer is isolated.
```

## Diff of the sampled file

```diff
@@ -36,8 +36,8 @@ def decorate_models_by_relation(
         target_classes=target_relations.models,
         naming_conventions=target_relations.naming_conventions,
     )
-    customer_classes = search.sweep_for_relations()
-    control_classes = model_classes.difference(customer_classes)
+    region_classes = search.sweep_for_relations()
+    control_classes = model_classes.difference(region_classes)
 
     def filtered_names(classes):
         return (
@@ -53,9 +53,9 @@ def decorate_models_by_relation(
         path_name,
     )
     apply_decorators(
-        "customer_silo_model",
-        "from sentry.db.models import customer_silo_model",
-        filtered_names(customer_classes),
+        "region_silo_model",
+        "from sentry.db.models import region_silo_model",
+        filtered_names(region_classes),
         path_name,
     )
```

## Other files changed by this commit (11)

- `scripts/silo/add_silo_decorators.py` (+1 −1)
- `scripts/silo/decorate_models_by_relation.py` (+4 −4)
- `src/sentry/api/base.py` (+3 −3)
- `src/sentry/db/models/base.py` (+3 −3)
- `src/sentry/silo.py` (+1 −1)
- `src/sentry/testutils/silo.py` (+3 −3)
- `src/sentry/utils/silo/add_silo_decorators.py` (+11 −11)
- `src/sentry/utils/silo/common.py` (+4 −4)
- `src/sentry/utils/silo/decorate_unit_tests.py` (+4 −4)
- `tests/sentry/api/test_base.py` (+4 −4)
- `tests/sentry/models/test_base.py` (+12 −12)

## Fix commits that the dataset links to this commit (1)

### Fix 1: b6d87b8144f2 (2022-09-27) · pull request #38785: fix(hybrid): Tag some models as available on all silos

Pull-request labels: Scope: Backend

Commit message:

```
fix(hybrid): Tag some models as available on all silos (#38785)
```

Pull-request description:

```
This is an experimental way to handle data that is private to one particular Django stack and is not of concern to the rest of the platform.
```

This fix changes 8 files. Lines it removes that the commit above had added:

- in the sampled file: `filtered_names(region_classes),`
- in `src/sentry/utils/silo/common.py`: `r"(?:\n@((?:control|region|pending)_silo_(?:model|endpoint|test)))?"`

Patch of the sampled file in this fix:

```diff
@@ -12,9 +12,22 @@
     ReverseOneToOneDescriptor,
 )
 
+import sentry.models
 from sentry.db.models import BaseModel
 from sentry.utils.silo.common import apply_decorators
 
+ALL_SILO_SPECIAL_CASES = frozenset(
+    {
+        sentry.models.Actor,
+        sentry.models.AuditLogEntry,
+        sentry.models.File,
+        sentry.models.FileBlob,
+        sentry.models.FileBlobIndex,
+        sentry.models.ScheduledDeletion,
+        sentry.models.UserIP,
+    }
+)
+
 
 @dataclass
 class TargetRelations:
@@ -26,11 +39,13 @@ class TargetRelations:
 
 
 def decorate_models_by_relation(
-    target_relations: TargetRelations,
+    target_relations: TargetRelations | Iterable[TargetRelations],
     app_label: Optional[str] = "sentry",
     path_name: Optional[str] = "./src/sentry",
 ):
     model_classes = frozenset(_get_sentry_model_classes(app_label))
+    model_classes = model_classes.difference(ALL_SILO_SPECIAL_CASES)
+
     search = RelationGraphSearch(
         model_classes=model_classes,
         target_classes=target_relations.models,
@@ -39,19 +54,25 @@ def decorate_models_by_relation(
     region_classes = search.sweep_for_relations()
     control_classes = model_classes.difference(region_classes)
 
-    def filtered_names(classes):
-        return ((c.__module__, c.__name__) for c in classes if not hasattr(c._meta, "silo_limit"))
+    def to_name_pairs(classes):
+        return ((c.__module__, c.__name__) for c in classes)
 
     apply_decorators(
         "control_silo_model",
         "from sentry.db.models import control_silo_model",
-        filtered_names(control_classes),
+        to_name_pairs(control_classes),
         path_name,
     )
     apply_decorators(
         "region_silo_model",
         "from sentry.db.models import region_silo_model",
-        filtered_names(region_classes),
+        to_name_pairs(region_classes),
+        path_name,
+    )
+    apply_decorators(
+        "all_silo_model",
+        "from sentry.db.models import all_silo_model",
+        to_name_pairs(ALL_SILO_SPECIAL_CASES),
         path_name,
     )
```

Patch of `src/sentry/utils/silo/common.py` in this fix:

```diff
@@ -83,7 +83,7 @@ def replace(match):
         # decorator, or such.
         new_code = re.sub(
             (
-                r"(?:\n@((?:control|region|pending)_silo_(?:model|endpoint|test)))?"
+                r"(?:\n@((?:control|region|all|pending)_silo_(?:model|endpoint|test)))?"
                 rf"\n(class\s+{class_name}\()"
             ),
             replace,
```

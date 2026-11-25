# case093: getsentry/sentry 729b8112ebd7

Sampled file (the only file the models saw): `src/sentry/utils/silo/decorate_models_by_relation.py` · committed 2022-09-16 06:17:22-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
fix(hybrid): Add silo mode to "model exists" conditions (#38836)

In several places where the existence of a model is checked via
`app_config.get_model`, replace with a new utility function that also
checks whether the model is available in the current silo mode.

Promote the `__silo_limit` meta-attributes to publicly visible
attributes, dropping the leading underscores.
```

## Diff of the sampled file

```diff
@@ -40,11 +40,7 @@ def decorate_models_by_relation(
     control_classes = model_classes.difference(region_classes)
 
     def filtered_names(classes):
-        return (
-            (c.__module__, c.__name__)
-            for c in classes
-            if not hasattr(c._meta, "_ModelSiloLimit__silo_limit")
-        )
+        return ((c.__module__, c.__name__) for c in classes if not hasattr(c._meta, "silo_limit"))
 
     apply_decorators(
         "control_silo_model",
```

## Other files changed by this commit (10)

- `src/sentry/api/base.py` (+1 −1)
- `src/sentry/db/models/base.py` (+21 −4)
- `src/sentry/models/counter.py` (+2 −3)
- `src/sentry/models/userrole.py` (+8 −4)
- `src/sentry/receivers/core.py` (+2 −3)
- `src/sentry/receivers/users.py` (+4 −3)
- `src/sentry/silo.py` (+12 −5)
- `src/sentry/utils/silo/audit_silo_decorators.py` (+2 −2)
- `tests/sentry/models/test_base.py` (+28 −1)
- `tests/sentry/test_silo.py` (+2 −2)

## Fix commits that the dataset links to this commit (2)

### Fix 1: 705e60e19f44 (2022-11-01) · pull request #40779: fix(hc) Fix typings of model annotations

Pull-request labels: Scope: Backend

Commit message:

```
fix(hc) Fix typings of model annotations (#40779)

Without the generic typevar, annotations for model classes were all
'type' causing warnings in both sentry and getsentry for functions that
want to typehint on a model class.

Using a TypeVar results in the class type being preserved by the
decorator.

Fixes HC-428
```

Pull-request description:

```
Without the generic typevar, annotations for model classes were all 'type' causing warnings in both sentry and getsentry for functions that want to typehint on a model class.

Using a TypeVar results in the class type being preserved by the decorator.

Fixes HC-428
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/sentry/db/models/base.py`: `from typing import Any, Callable, Iterable, Mapping, Tuple, Type, cast`

Patch of `src/sentry/db/models/base.py` in this fix:

```diff
@@ -1,6 +1,6 @@
 from __future__ import annotations
 
-from typing import Any, Callable, Iterable, Mapping, Tuple, Type, cast
+from typing import Any, Callable, Iterable, Mapping, Tuple, Type, TypeVar, cast
 
 from django.apps.config import AppConfig
 from django.db import models
@@ -162,6 +162,9 @@ def get_model_if_available(app_config: AppConfig, model_name: str) -> Type[model
     return model
 
 
+ModelClass = TypeVar("ModelClass")
+
+
 class ModelSiloLimit(SiloLimit):
     def __init__(
         self,
@@ -199,7 +202,7 @@ def handle(obj: Any, *args: Any, **kwargs: Any) -> None:
 
         return handle
 
-    def __call__(self, model_class: Any) -> type:
+    def __call__(self, model_class: ModelClass) -> Type[ModelClass]:
         if not (isinstance(model_class, type) and issubclass(model_class, BaseModel)):
             raise TypeError("`@ModelSiloLimit ` must decorate a Model class")
         assert isinstance(model_class.objects, BaseManager)
```

### Fix 2: b6d87b8144f2 (2022-09-27) · pull request #38785: fix(hybrid): Tag some models as available on all silos

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

- in the sampled file: `return ((c.__module__, c.__name__) for c in classes if not hasattr(c._meta, "silo_limit"))`
- in other files of the commit: none

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

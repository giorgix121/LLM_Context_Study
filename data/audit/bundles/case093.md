# case093: getsentry/sentry 729b8112ebd7

File: `src/sentry/utils/silo/decorate_models_by_relation.py` · committed 2022-09-16 06:17:22-01:00 · SZZ label: RISKY

## Commit message

```
fix(hybrid): Add silo mode to "model exists" conditions (#38836)

In several places where the existence of a model is checked via
`app_config.get_model`, replace with a new utility function that also
checks whether the model is available in the current silo mode.

Promote the `__silo_limit` meta-attributes to publicly visible
attributes, dropping the leading underscores.
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
   43          return ((c.__module__, c.__name__) for c in classes if not hasattr(c._meta, "silo_limit"))
```

## Candidate fixes (1 later commits to this file remove a blamed line; 1 later commits up to 2023-06-30 checked)

### Candidate 1: b6d87b8144f2 (2022-09-27)

Message:

```
fix(hybrid): Tag some models as available on all silos (#38785)
```

Removed blamed lines: `return ((c.__module__, c.__name__) for c in classes if not hasattr(c._meta, "silo_limit"))`

Patch of this file:

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

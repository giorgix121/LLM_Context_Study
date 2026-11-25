# case107: django/django ec13e801b820

File: `django/db/backends/mysql/schema.py` · committed 2022-09-12 09:52:18-01:00 · SZZ label: RISKY

## Commit message

```
Refs #31335 -- Added SchemaEditor._create_missing_fk_index() on MySQL.
```

## Diff of the target file

```diff
@@ -135,24 +135,35 @@ class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):
             return False
         return not self._is_limited_data_type(field)
 
-    def _delete_composed_index(self, model, fields, *args):
+    def _create_missing_fk_index(
+        self,
+        model,
+        *,
+        fields,
+    ):
         """
         MySQL can remove an implicit FK index on a field when that field is
         covered by another index like a unique_together. "covered" here means
-        that the more complex index starts like the simpler one.
-        https://bugs.mysql.com/bug.php?id=37910 / Django ticket #24757
-        We check here before removing the [unique|index]_together if we have to
-        recreate a FK index.
+        that the more complex index has the FK field as its first field (see
+        https://bugs.mysql.com/bug.php?id=37910).
+
+        Manually create an implicit FK index to make it possible to remove the
+        composed index.
         """
         first_field = model._meta.get_field(fields[0])
         if first_field.get_internal_type() == "ForeignKey":
             constraint_names = self._constraint_names(
-                model, [first_field.column], index=True
+                model,
+                [first_field.column],
+                index=True,
             )
             if not constraint_names:
                 self.execute(
                     self._create_index_sql(model, fields=[first_field], suffix="")
                 )
+
+    def _delete_composed_index(self, model, fields, *args):
+        self._create_missing_fk_index(model, fields=fields)
         return super()._delete_composed_index(model, fields, *args)
 
     def _set_field_new_type_null_status(self, field, new_type):
```

## Lines SZZ blamed (line numbers in the new version)

```
  138      def _create_missing_fk_index(
  139          self,
  140          model,
  141          *,
  142          fields,
  143      ):
  147          that the more complex index has the FK field as its first field (see
  148          https://bugs.mysql.com/bug.php?id=37910).
  149  
  150          Manually create an implicit FK index to make it possible to remove the
  151          composed index.
  156                  model,
  157                  [first_field.column],
  158                  index=True,
  164  
  165      def _delete_composed_index(self, model, fields, *args):
  166          self._create_missing_fk_index(model, fields=fields)
```

## Candidate fixes (1 later commits to this file remove a blamed line; 8 later commits up to 2023-06-30 checked)

### Candidate 1: b731e8841558 (2021-12-28)

Message:

```
Fixed #31335 -- Fixed removing composed composed Meta constraints/indexes on foreign keys on MySQL.
```

Removed blamed lines: `[first_field.column],`; `index=True,`; `model,`

Patch of this file:

```diff
@@ -1,5 +1,6 @@
 from django.db.backends.base.schema import BaseDatabaseSchemaEditor
-from django.db.models import NOT_PROVIDED
+from django.db.models import NOT_PROVIDED, F, UniqueConstraint
+from django.db.models.constants import LOOKUP_SEP
 
 
 class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):
@@ -117,6 +118,23 @@ def add_field(self, model, field):
                 [effective_default],
             )
 
+    def remove_constraint(self, model, constraint):
+        if isinstance(constraint, UniqueConstraint):
+            self._create_missing_fk_index(
+                model,
+                fields=constraint.fields,
+                expressions=constraint.expressions,
+            )
+        super().remove_constraint(model, constraint)
+
+    def remove_index(self, model, index):
+        self._create_missing_fk_index(
+            model,
+            fields=[field_name for field_name, _ in index.fields_orders],
+            expressions=index.expressions,
+        )
+        super().remove_index(model, index)
+
     def _field_should_be_indexed(self, model, field):
         if not super()._field_should_be_indexed(model, field):
             return False
@@ -140,6 +158,7 @@ def _create_missing_fk_index(
         model,
         *,
         fields,
+        expressions=None,
     ):
         """
         MySQL can remove an implicit FK index on a field when that field is
@@ -150,14 +169,36 @@ def _create_missing_fk_index(
         Manually create an implicit FK index to make it possible to remove the
         composed index.
         """
-        first_field = model._meta.get_field(fields[0])
+        first_field_name = None
+        if fields:
+            first_field_name = fields[0]
+        elif (
+            expressions
+            and self.connection.features.supports_expression_indexes
+            and isinstance(expressions[0], F)
+            and LOOKUP_SEP not in expressions[0].name
+        ):
+            first_field_name = expressions[0].name
+
+        if not first_field_name:
+            return
+
+        first_field = model._meta.get_field(first_field_name)
         if first_field.get_internal_type() == "ForeignKey":
-            constraint_names = self._constraint_names(
-                model,
-                [first_field.column],
-                index=True,
+            column = self.connection.introspection.identifier_converter(
+                first_field.column
             )
-            if not constraint_names:
+            with self.connection.cursor() as cursor:
+                constraint_names = [
+                    name
+                    for name, infodict in self.connection.introspection.get_constraints(
+                        cursor, model._meta.db_table
+                    ).items()
+                    if infodict["index"] and infodict["columns"][0] == column
+                ]
+            # There are no other indexes that starts with the FK field, only
+            # the index that is expected to be deleted.
+            if len(constraint_names) == 1:
                 self.execute(
                     self._create_index_sql(model, fields=[first_field], suffix="")
                 )
```

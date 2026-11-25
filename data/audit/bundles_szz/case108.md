# case108: getsentry/sentry a02530c7a173

Sampled file (the only file the models saw): `src/sentry/tasks/app_store_connect.py` · committed 2022-10-24 17:57:32-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
fix(appconnect): Use app_id_str field (#40322)

This is step 3 in the effort to change the type of
`AppConnectBuild.app_id` from an integer to a string.

It replaces all uses of the `app_id` field with `app_id_str` and makes
the `app_id` field nullable, since it is not written any longer.
```

## Diff of the sampled file

```diff
@@ -124,7 +124,7 @@ def get_or_create_persisted_build(
     try:
         build_state = AppConnectBuild.objects.get(
             project=project,
-            app_id=int(build.app_id),
+            app_id_str=build.app_id,
             platform=build.platform,
             bundle_short_version=build.version,
             bundle_version=build.build_number,
@@ -132,7 +132,6 @@ def get_or_create_persisted_build(
     except AppConnectBuild.DoesNotExist:
         build_state = AppConnectBuild(
             project=project,
-            app_id=int(build.app_id),
             app_id_str=build.app_id,
             bundle_id=config.bundleId,
             platform=build.platform,
```

## Other files changed by this commit (4)

- `migrations_lockfile.txt` (+1 −1)
- `src/sentry/migrations/0329_make_app_id_nullable.py` (+34 −0)
- `src/sentry/models/appconnectbuilds.py` (+1 −1)
- `tests/sentry/tasks/test_app_store_connect.py` (+1 −10)

## Fix commits that the dataset links to this commit (1)

### Fix 1: bf1323d138f6 (2022-10-25) · pull request #40325: fix(appconnect): Redirect app_id to app_id_str column

Pull-request labels: Scope: Backend

Commit message:

```
fix(appconnect): Redirect app_id to app_id_str column (#40325)

This is step 4 in the effort to change the type of
`AppConnectBuild.app_id` from an integer to a string.

It effectively removes the old `app_id` field and renames the new
`app_id_str` field to `app_id`.
```

Pull-request description:

```
This is step 4 in the effort to change the type of `AppConnectBuild.app_id` from an integer to a string.

It effectively removes the old `app_id` field and renames the new `app_id_str` field to `app_id`.

Depends on https://github.com/getsentry/sentry/pull/40322.
```

This fix changes 5 files. Lines it removes that the commit above had added:

- in the sampled file: `app_id_str=build.app_id,`
- in `src/sentry/models/appconnectbuilds.py`: `app_id = models.IntegerField(null=True)`
- in `tests/sentry/tasks/test_app_store_connect.py`: `app_id_str=build.app_id,`

Patch of the sampled file in this fix:

```diff
@@ -124,15 +124,15 @@ def get_or_create_persisted_build(
     try:
         build_state = AppConnectBuild.objects.get(
             project=project,
-            app_id_str=build.app_id,
+            app_id=build.app_id,
             platform=build.platform,
             bundle_short_version=build.version,
             bundle_version=build.build_number,
         )
     except AppConnectBuild.DoesNotExist:
         build_state = AppConnectBuild(
             project=project,
-            app_id_str=build.app_id,
+            app_id=build.app_id,
             bundle_id=config.bundleId,
             platform=build.platform,
             bundle_short_version=build.version,
```

Patch of `src/sentry/models/appconnectbuilds.py` in this fix:

```diff
@@ -27,11 +27,8 @@ class AppConnectBuild(Model):
 
     project = FlexibleForeignKey("sentry.Project", db_constraint=False)
 
-    # The integer ID of the app inside App Store Connect.
-    app_id = models.IntegerField(null=True)
-
-    # The integer ID of the app inside App Store Connect, as a string.
-    app_id_str = models.CharField(default="0", max_length=256)
+    # The integer ID of the app inside App Store Connect (in string form).
+    app_id = models.CharField(default="0", max_length=256, db_column="app_id_str")
 
     # The unique Bundle ID, like a slug for app_id
     #
```

Patch of `tests/sentry/tasks/test_app_store_connect.py` in this fix:

```diff
@@ -64,7 +64,7 @@ def test_process_new_build(self, default_project, config, build):
     def test_process_existing_fetched_build(self, default_project, config, build):
         AppConnectBuild.objects.create(
             project=default_project,
-            app_id_str=build.app_id,
+            app_id=build.app_id,
             bundle_id=config.bundleId,
             platform=build.platform,
             bundle_short_version=build.version,
@@ -103,7 +103,7 @@ def test_process_existing_fetched_build(self, default_project, config, build):
     def test_process_existing_unfetched_build(self, default_project, config, build):
         AppConnectBuild.objects.create(
             project=default_project,
-            app_id_str=build.app_id,
+            app_id=build.app_id,
             bundle_id=config.bundleId,
             platform=build.platform,
             bundle_short_version=build.version,
@@ -132,7 +132,7 @@ def test_create_new_persisted_build(self, default_project, config, build):
 
         expected_build = AppConnectBuild(
             project=default_project,
-            app_id_str=build.app_id,
+            app_id=build.app_id,
             bundle_id=config.bundleId,
             platform=build.platform,
             bundle_short_version=build.version,
@@ -144,7 +144,7 @@ def test_create_new_persisted_build(self, default_project, config, build):
 
         assert returned_build.fetched == expected_build.fetched
         assert returned_build.project == expected_build.project
-        assert returned_build.app_id_str == expected_build.app_id_str
+        assert returned_build.app_id == expected_build.app_id
         assert returned_build.bundle_id == expected_build.bundle_id
         assert returned_build.platform == expected_build.platform
         assert returned_build.bundle_short_version == expected_build.bundle_short_version
@@ -153,15 +153,15 @@ def test_create_new_persisted_build(self, default_project, config, build):
 
         saved_build = AppConnectBuild.objects.get(
             project=default_project,
-            app_id_str=build.app_id,
+            app_id=build.app_id,
             platform=build.platform,
             bundle_short_v
[... cut ...]
```

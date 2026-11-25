# case139: getsentry/sentry e38aa13378cb

Sampled file (the only file the models saw): `src/sentry/tasks/app_store_connect.py` · committed 2022-10-24 12:23:07-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
fix(appconnect): Add app_id_str column to appconnectbuild (#40261)

This is step 1 in the effort to change the type of
`AppConnectBuild.app_id` from an integer to a string.

It adds a new column `app_id_str` of type `CharField` to the
`appconnectbuild` model and a corresponding field to `AppConnectBuild`.
```

## Diff of the sampled file

```diff
@@ -133,6 +133,7 @@ def get_or_create_persisted_build(
         build_state = AppConnectBuild(
             project=project,
             app_id=int(build.app_id),
+            app_id_str=build.app_id,
             bundle_id=config.bundleId,
             platform=build.platform,
             bundle_short_version=build.version,
```

## Other files changed by this commit (4)

- `migrations_lockfile.txt` (+1 −1)
- `src/sentry/migrations/0327_add_appid_str.py` (+51 −0)
- `src/sentry/models/appconnectbuilds.py` (+3 −3)
- `tests/sentry/tasks/test_app_store_connect.py` (+9 −0)

## Fix commits that the dataset links to this commit (2)

### Fix 1: 764673aefb3b (2022-10-24) · pull request #40321: fix(appconnect): Backfill app_id_str

Pull-request labels: Scope: Backend

Commit message:

```
fix(appconnect): Backfill app_id_str (#40321)

This is step 2 in the effort to change the type of
`AppConnectBuild.app_id` from an integer to a string.

It backfills the new `app_id_str` column from the existing `app_id`
field.
```

Pull-request description:

```
This is step 2 in the effort to change the type of `AppConnectBuild.app_id` from an integer to a string.

It backfills the new `app_id_str` column from the existing `app_id` field.

Depends on https://github.com/getsentry/sentry/pull/40261.
```

This fix changes 2 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `migrations_lockfile.txt`: `sentry: 0327_add_appid_str`

Patch of `migrations_lockfile.txt` in this fix:

```diff
@@ -6,5 +6,5 @@ To resolve this, rebase against latest master and regenerate your migration. Thi
 will then be regenerated, and you should be able to merge without conflicts.
 
 nodestore: 0002_nodestore_no_dictfield
-sentry: 0327_add_appid_str
+sentry: 0328_backfill_app_id_str
 social_auth: 0001_initial
```

### Fix 2: bf1323d138f6 (2022-10-25) · pull request #40325: fix(appconnect): Redirect app_id to app_id_str column

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
- in `src/sentry/models/appconnectbuilds.py`: `app_id_str = models.CharField(default="0", max_length=256)`
- in `tests/sentry/tasks/test_app_store_connect.py`: `app_id_str=build.app_id,`; `assert existing_build.app_id_str == build.app_id`; `assert returned_build.app_id_str == expected_build.app_id_str`; `assert saved_build.app_id_str == expected_build.app_id_str`

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

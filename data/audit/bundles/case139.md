# case139: getsentry/sentry e38aa13378cb

File: `src/sentry/tasks/app_store_connect.py` · committed 2022-10-24 12:23:07-01:00 · SZZ label: RISKY

## Commit message

```
fix(appconnect): Add app_id_str column to appconnectbuild (#40261)

This is step 1 in the effort to change the type of
`AppConnectBuild.app_id` from an integer to a string.

It adds a new column `app_id_str` of type `CharField` to the
`appconnectbuild` model and a corresponding field to `AppConnectBuild`.
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
  136              app_id_str=build.app_id,
```

## Candidate fixes (1 later commits to this file remove a blamed line; 3 later commits up to 2023-06-30 checked)

### Candidate 1: bf1323d138f6 (2022-10-25)

Message:

```
fix(appconnect): Redirect app_id to app_id_str column (#40325)

This is step 4 in the effort to change the type of
`AppConnectBuild.app_id` from an integer to a string.

It effectively removes the old `app_id` field and renames the new
`app_id_str` field to `app_id`.
```

Removed blamed lines: `app_id_str=build.app_id,`

Patch of this file:

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

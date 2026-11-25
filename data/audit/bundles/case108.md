# case108: getsentry/sentry a02530c7a173

File: `src/sentry/tasks/app_store_connect.py` · committed 2022-10-24 17:57:32-01:00 · SZZ label: RISKY

## Commit message

```
fix(appconnect): Use app_id_str field (#40322)

This is step 3 in the effort to change the type of
`AppConnectBuild.app_id` from an integer to a string.

It replaces all uses of the `app_id` field with `app_id_str` and makes
the `app_id` field nullable, since it is not written any longer.
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
  127              app_id_str=build.app_id,
```

## Candidate fixes (1 later commits to this file remove a blamed line; 2 later commits up to 2023-06-30 checked)

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

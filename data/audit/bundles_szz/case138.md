# case138: getsentry/sentry 038d81948dd9

Sampled file (the only file the models saw): `src/sentry/web/client_config.py` · committed 2022-10-19 15:01:56-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
feat(hybrid-cloud): Propagate last org's customer domain feature (#40225)
```

## Diff of the sampled file

```diff
@@ -106,7 +106,7 @@ def _delete_activeorg(session):
         del session["activeorg"]
 
 
-def _resolve_last_org_slug(session, user):
+def _resolve_last_org(session, user):
     last_org_slug = session["activeorg"] if session and "activeorg" in session else None
     if not last_org_slug:
         return None
@@ -115,7 +115,7 @@ def _resolve_last_org_slug(session, user):
         if user is not None and not isinstance(user, AnonymousUser):
             try:
                 get_cached_organization_member(user.id, last_org.id)
-                return last_org_slug
+                return last_org
             except OrganizationMember.DoesNotExist:
                 return None
     except Organization.DoesNotExist:
@@ -163,9 +163,14 @@ def get_client_config(request=None):
 
     public_dsn = _get_public_dsn()
 
-    last_org_slug = _resolve_last_org_slug(session, user)
-    if last_org_slug is None:
+    last_org_slug = None
+    last_org = _resolve_last_org(session, user)
+    if last_org:
+        last_org_slug = last_org.slug
+    if last_org is None:
         _delete_activeorg(session)
+    if features.has("organizations:customer-domains", last_org):
+        enabled_features.append("organizations:customer-domains")
 
     context = {
         "singleOrganization": settings.SENTRY_SINGLE_ORGANIZATION,
```

## Other files changed by this commit (1)

- `tests/sentry/web/test_api.py` (+47 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 5878cd013145 (2022-10-27) · pull request #40202: fix(tests): Validate params when patching sentry features check

Pull-request labels: Scope: Backend

Commit message:

```
fix(tests): Validate params when patching sentry features check (#40202)

Validate params when patching sentry features check
```

Pull-request description:

```
Validate params when patching sentry features check
```

This fix changes 5 files. Lines it removes that the commit above had added:

- in the sampled file: `if features.has("organizations:customer-domains", last_org):`
- in other files of the commit: none

Patch of the sampled file in this fix:

```diff
@@ -163,7 +163,7 @@ def get_client_config(request=None):
         last_org_slug = last_org.slug
     if last_org is None:
         _delete_activeorg(session)
-    if features.has("organizations:customer-domains", last_org):
+    if last_org is not None and features.has("organizations:customer-domains", last_org):
         enabled_features.append("organizations:customer-domains")
 
     context = {
```

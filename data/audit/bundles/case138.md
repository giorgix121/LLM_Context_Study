# case138: getsentry/sentry 038d81948dd9

File: `src/sentry/web/client_config.py` · committed 2022-10-19 15:01:56-01:00 · SZZ label: RISKY

## Commit message

```
feat(hybrid-cloud): Propagate last org's customer domain feature (#40225)
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
  109  def _resolve_last_org(session, user):
  118                  return last_org
  166      last_org_slug = None
  167      last_org = _resolve_last_org(session, user)
  168      if last_org:
  169          last_org_slug = last_org.slug
  170      if last_org is None:
  172      if features.has("organizations:customer-domains", last_org):
  173          enabled_features.append("organizations:customer-domains")
```

## Candidate fixes (2 later commits to this file remove a blamed line; 19 later commits up to 2023-06-30 checked)

### Candidate 1: 5878cd013145 (2022-10-27)

Message:

```
fix(tests): Validate params when patching sentry features check (#40202)

Validate params when patching sentry features check
```

Removed blamed lines: `if features.has("organizations:customer-domains", last_org):`

Patch of this file:

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

### Candidate 2: f2609389d312 (2022-11-22)

Message:

```
feature(hybrid-cloud): get_client_config is silo compatible (#41592)

Gets the react context builder `get_client_config` passing in all silos,
validating itself against the existing implementation. Necessary for
many endpoint tests.
```

Removed blamed lines: `return last_org`

Patch of this file:

```diff
@@ -6,14 +6,13 @@
 
 import sentry
 from sentry import features, options
-from sentry.api.serializers.base import serialize
-from sentry.api.serializers.models.user import DetailedSelfUserSerializer
 from sentry.api.utils import generate_organization_url, generate_region_url
 from sentry.auth import superuser
-from sentry.auth.access import get_cached_organization_member
 from sentry.auth.superuser import is_active_superuser
-from sentry.models import Organization, OrganizationMember
+from sentry.services.hybrid_cloud.auth import AuthenticationContext
+from sentry.services.hybrid_cloud.organization import organization_service
 from sentry.services.hybrid_cloud.project_key import ProjectKeyRole, project_key_service
+from sentry.services.hybrid_cloud.user import UserSerializeType, user_service
 from sentry.utils import auth
 from sentry.utils.assets import get_frontend_app_asset_url
 from sentry.utils.email import is_smtp_enabled
@@ -105,16 +104,12 @@ def _resolve_last_org(session, user):
     last_org_slug = session["activeorg"] if session and "activeorg" in session else None
     if not last_org_slug:
         return None
-    try:
-        last_org = Organization.objects.get_from_cache(slug=last_org_slug)
-        if user is not None and not isinstance(user, AnonymousUser):
-            try:
-                get_cached_organization_member(user.id, last_org.id)
-                return last_org
-            except OrganizationMember.DoesNotExist:
-                return None
-    except Organization.DoesNotExist:
-        pass
+    if user is not None and not isinstance(user, AnonymousUser):
+        org_context = organization_service.get_organization_by_slug(
+            slug=last_org_slug, only_visible=False, user_id=user.id
+        )
+        if org_context and org_context.member:
+            return org_context.organization
     return None
 
 
@@ -235,8 +230,19 @@ def get_client_config(request=None):
         },
     }
     if user and user.is_authenticated:
+        (serialized_user,) = user_service.serialize_users(
+            [user.id],
+            detailed=UserSerializeType.SELF_DETAILED,
+            auth_context=AuthenticationContext(
+                auth=getattr(request, "auth", None),
+                user=request.user,
+            ),
+        )
         context.update(
-            {"isAuthenticated": True, "user": serialize(user, user, DetailedSelfUserSerializer())}
+            {
+                "isAuthenticated": True,
+                "user": serialized_user,
+            }
         )
 
         if request.user.is_superuser:
```

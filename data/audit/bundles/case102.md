# case102: getsentry/sentry a882713d1b8f

File: `src/sentry/web/frontend/home.py` · committed 2022-10-26 02:03:31-01:00 · SZZ label: RISKY

## Commit message

```
chore(hybrid-cloud): Refactor Organization ORM out of views and auth (#40362)

For hybrid cloud, the organization and related models will not exist in the control silo, but will be necessary for certain auth related flows.  This change is the first of many to make the core auth flows compatible with a split silo world by introducing a service object that captures existing needs for an organization arond the `get_active_organization` method.  Behavior should remain identical, except that the pure ORM object is not available in many places.  Those places have been updated to use a new thinner model object that corresponds with future control silo's data availability.

Co-authored-by: getsantry[bot] <66042841+getsantry[bot]@users.noreply.github.com>
```

## Diff of the target file

```diff
@@ -10,9 +10,8 @@ from sentry.web.frontend.base import BaseView
 class HomeView(BaseView):
     def get(self, request: Request) -> Response:
         # If the active organization has an ongoing onboarding session, redirect to onboarding
-        organization = self.get_active_organization(request)
-        if organization:
-            redirect_uri = get_client_state_redirect_uri(organization.slug, None)
+        if self.active_organization:
+            redirect_uri = get_client_state_redirect_uri(self.active_organization.slug, None)
             if redirect_uri and is_valid_redirect(
                 redirect_uri, allowed_hosts=(request.get_host(),)
             ):
```

## Lines SZZ blamed (line numbers in the new version)

```
   13          if self.active_organization:
   14              redirect_uri = get_client_state_redirect_uri(self.active_organization.slug, None)
```

## Candidate fixes (2 later commits to this file remove a blamed line; 3 later commits up to 2023-06-30 checked)

### Candidate 1: a2fbca050e0c (2022-11-07)

Message:

```
ref(hybrid-cloud): OrganizationService expansion for access (#41002)

This expands on the OgranizationService interface by adding methods that
will be necessary for access in the silo world.

Co-authored-by: Ryan Skonnord <ryan.skonnord@sentry.io>
```

Removed blamed lines: `redirect_uri = get_client_state_redirect_uri(self.active_organization.slug, None)`

Patch of this file:

```diff
@@ -11,7 +11,9 @@ class HomeView(BaseView):
     def get(self, request: Request) -> Response:
         # If the active organization has an ongoing onboarding session, redirect to onboarding
         if self.active_organization:
-            redirect_uri = get_client_state_redirect_uri(self.active_organization.slug, None)
+            redirect_uri = get_client_state_redirect_uri(
+                self.active_organization.organization.slug, None
+            )
             if redirect_uri and is_valid_redirect(
                 redirect_uri, allowed_hosts=(request.get_host(),)
             ):
```

### Candidate 2: e2950026e8a3 (2023-05-09)

Message:

```
ref(onboarding): Remove client-state from backend (#48629)
```

Removed blamed lines: `if self.active_organization:`

Patch of this file:

```diff
@@ -1,22 +1,9 @@
-from django.http import HttpResponseRedirect
 from rest_framework.request import Request
 from rest_framework.response import Response
 
-from sentry.utils.auth import is_valid_redirect
-from sentry.utils.client_state import get_client_state_redirect_uri
 from sentry.web.frontend.base import BaseView
 
 
 class HomeView(BaseView):
     def get(self, request: Request) -> Response:
-        # If the active organization has an ongoing onboarding session, redirect to onboarding
-        if self.active_organization:
-            redirect_uri = get_client_state_redirect_uri(
-                self.active_organization.organization.slug, None
-            )
-            if redirect_uri and is_valid_redirect(
-                redirect_uri, allowed_hosts=(request.get_host(),)
-            ):
-                return HttpResponseRedirect(redirect_uri)
-
         return self.redirect_to_org(request)
```

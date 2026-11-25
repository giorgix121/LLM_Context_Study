# case103: getsentry/sentry b11fa148a56f

Sampled file (the only file the models saw): `src/sentry/web/client_config.py` · committed 2022-11-02 12:48:07-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
feat(hybrid-cloud): Add customer domain to client config (#40226)
```

## Diff of the sampled file

```diff
@@ -122,6 +122,13 @@ def get_client_config(request=None):
     Provides initial bootstrap data needed to boot the frontend application.
     """
     if request is not None:
+        customer_domain = None
+        if hasattr(request, "subdomain") and request.subdomain:
+            customer_domain = {
+                "subdomain": request.subdomain,
+                "organizationUrl": generate_organization_url(request.subdomain),
+                "sentryUrl": options.get("system.url-prefix"),
+            }
         user = getattr(request, "user", None) or AnonymousUser()
         messages = get_messages(request)
         session = getattr(request, "session", None)
@@ -135,6 +142,7 @@ def get_client_config(request=None):
             if user.name:
                 user_identity["name"] = user.name
     else:
+        customer_domain = None
         user = None
         user_identity = {}
         messages = []
@@ -167,6 +175,7 @@ def get_client_config(request=None):
         enabled_features.append("organizations:customer-domains")
 
     context = {
+        "customerDomain": customer_domain,
         "singleOrganization": settings.SENTRY_SINGLE_ORGANIZATION,
         "supportEmail": get_support_mail(),
         "urlPrefix": options.get("system.url-prefix"),
```

## Other files changed by this commit (1)

- `tests/sentry/web/test_api.py` (+25 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: cd8fced369d4 (2022-11-03) · pull request #40950: fix(hybrid-cloud): Propagate organizations:customer-domains feature if a customer domain is used

Pull-request labels: Scope: Backend

Commit message:

```
fix(hybrid-cloud): Propagate organizations:customer-domains feature if a customer domain is used (#40950)
```

Pull-request description:

```
A continuation of https://github.com/getsentry/sentry/pull/40877, whenever orgslug.sentry.io is accessed, we implicitly add the customer domain feature flag.
```

This fix changes 2 files. Lines it removes that the commit above had added:

- in the sampled file: `if hasattr(request, "subdomain") and request.subdomain:`
- in other files of the commit: none

Patch of the sampled file in this fix:

```diff
@@ -17,6 +17,7 @@
 from sentry.utils import auth
 from sentry.utils.assets import get_frontend_app_asset_url
 from sentry.utils.email import is_smtp_enabled
+from sentry.utils.http import is_using_customer_domain
 from sentry.utils.settings import is_self_hosted
 from sentry.utils.support import get_support_mail
 
@@ -123,7 +124,7 @@ def get_client_config(request=None):
     """
     if request is not None:
         customer_domain = None
-        if hasattr(request, "subdomain") and request.subdomain:
+        if is_using_customer_domain(request):
             customer_domain = {
                 "subdomain": request.subdomain,
                 "organizationUrl": generate_organization_url(request.subdomain),
@@ -171,7 +172,11 @@ def get_client_config(request=None):
         last_org_slug = last_org.slug
     if last_org is None:
         _delete_activeorg(session)
+
+    inject_customer_domain_feature = bool(customer_domain)
     if last_org is not None and features.has("organizations:customer-domains", last_org):
+        inject_customer_domain_feature = True
+    if inject_customer_domain_feature:
         enabled_features.append("organizations:customer-domains")
 
     context = {
```

# case100: getsentry/sentry e9ce61066783

Sampled file (the only file the models saw): `src/sentry/integrations/jira_server/client.py` · committed 2022-10-12 07:00:00-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
ref: type sentry/utils/assets.py and sentry/utils/http.py (#39624)
```

## Diff of the sampled file

```diff
@@ -126,13 +126,13 @@ class JiraServerClient(ApiClient):
         # Get a list of fields for the issue type and project
         return self.get_cached(self.ISSUE_FIELDS_URL % (project_id, issue_type_id))
 
-    def get_project_key_for_id(self, project_id):
+    def get_project_key_for_id(self, project_id) -> str:
         if not project_id:
             return ""
         projects = self.get_projects_list()
         for project in projects:
             if project["id"] == project_id:
-                return project["key"].encode("utf-8")
+                return project["key"]
         return ""
 
     def get_versions(self, project):
```

## Other files changed by this commit (14)

- `mypy.ini` (+3 −0)
- `src/sentry/integrations/bitbucket/client.py` (+4 −1)
- `src/sentry/integrations/bitbucket/integration.py` (+2 −2)
- `src/sentry/integrations/bitbucket/search.py` (+1 −1)
- `src/sentry/integrations/bitbucket_server/integration.py` (+1 −2)
- `src/sentry/integrations/jira/client.py` (+2 −2)
- `src/sentry/integrations/utils/atlassian_connect.py` (+12 −10)
- `src/sentry/utils/assets.py` (+2 −2)
- `src/sentry/utils/http.py` (+26 −28)
- `src/sentry/utils/jwt.py` (+8 −7)
- `src/sentry_plugins/bitbucket/plugin.py` (+1 −1)
- `src/sentry_plugins/jira/client.py` (+1 −1)
- `src/sentry_plugins/jira/plugin.py` (+4 −4)
- `tests/sentry/utils/test_http.py` (+0 −2)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 8c82ed5baed8 (2022-10-27) · pull request #40649: ref: fix typing for sentry.utils.http

Pull-request labels: Scope: Backend

Commit message:

```
ref: fix typing for sentry.utils.http (#40649)

noticed while attempting to use django-stubs
```

Pull-request description:

```
noticed while attempting to use django-stubs
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/sentry/utils/http.py`: `def origin_from_request(request: HttpRequest) -> str:`; `from typing import TYPE_CHECKING, NamedTuple`; `rv: str = request.META.get("HTTP_ORIGIN", "null")`

Patch of `src/sentry/utils/http.py` in this fix:

```diff
@@ -1,6 +1,6 @@
 from __future__ import annotations
 
-from typing import TYPE_CHECKING, NamedTuple
+from typing import TYPE_CHECKING, NamedTuple, overload
 from urllib.parse import quote, urljoin, urlparse
 
 from django.conf import settings
@@ -37,7 +37,17 @@ def create_redirect_url(request: Request, redirect_url: str) -> str:
     return f"{redirect_url}{qs}"
 
 
+@overload
 def origin_from_url(url: str) -> str:
+    ...
+
+
+@overload
+def origin_from_url(url: None) -> None:
+    ...
+
+
+def origin_from_url(url: str | None) -> str | None:
     if not url:
         return url
     parsed = urlparse(url)
@@ -182,12 +192,12 @@ def is_valid_origin(
     return False
 
 
-def origin_from_request(request: HttpRequest) -> str:
+def origin_from_request(request: HttpRequest) -> str | None:
     """
     Returns either the Origin or Referer value from the request headers,
     ignoring "null" Origins.
     """
-    rv: str = request.META.get("HTTP_ORIGIN", "null")
+    rv: str | None = request.META.get("HTTP_ORIGIN", "null")
     # In some situation, an Origin header may be the literal value
     # "null". This means that the Origin header was stripped for
     # privacy reasons, but we should ignore this value entirely.
```

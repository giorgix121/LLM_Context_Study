# case126: getsentry/sentry 6bb7be0641f9

File: `src/sentry/integrations/github/client.py` · committed 2022-09-14 08:54:25-01:00 · SZZ label: RISKY

## Commit message

```
feat(commit-context): Add blame API to GitHub/GitLab clients (#38646)
```

## Diff of the target file

```diff
@@ -213,6 +213,49 @@ class GitHubClientMixin(ApiClient):  # type: ignore
         encoded_content = contents["content"]
         return b64decode(encoded_content).decode("utf-8")
 
+    def get_blame_for_file(
+        self, repo: Repository, path: str, ref: str
+    ) -> Sequence[Mapping[str, Any]]:
+        [owner, name] = repo.name.split("/")
+        query = f"""query {{
+            repository(name: {name}, owner: {owner}) {{
+                ref(qualifiedName: {ref}) {{
+                    target {{
+                        ... on Commit {{
+                            blame(path: {path}) {{
+                                ranges {{
+                                        commit {{
+                                            oid
+                                            author {{
+                                                name
+                                                email
+                                            }}
+                                            message
+                                        }}
+                                    startingLine
+                                    endingLine
+                                    age
+                                }}
+                            }}
+                        }}
+                    }}
+                }}
+            }}
+        }}"""
+
+        contents = self.post(
+            path="/graphql",
+            data={"query": query},
+        )
+        results: Sequence[Mapping[str, Any]] = (
+            contents.get("data", {})
+            .get("repository", {})
+            .get("ref", {})
+            .get("target", {})
+            .get("blame", [])
+        )
+        return results
+
 
 class GitHubAppsClient(GitHubClientMixin):
     def __init__(self, integration: Integration) -> None:
```

## Lines SZZ blamed (line numbers in the new version)

```
  216      def get_blame_for_file(
  217          self, repo: Repository, path: str, ref: str
  218      ) -> Sequence[Mapping[str, Any]]:
  219          [owner, name] = repo.name.split("/")
  220          query = f"""query {{
  221              repository(name: {name}, owner: {owner}) {{
  222                  ref(qualifiedName: {ref}) {{
  223                      target {{
  224                          ... on Commit {{
  225                              blame(path: {path}) {{
  226                                  ranges {{
  227                                          commit {{
  228                                              oid
  229                                              author {{
  230                                                  name
  231                                                  email
  232                                              }}
  233                                              message
  234                                          }}
  235                                      startingLine
  236                                      endingLine
  237                                      age
  238                                  }}
  239                              }}
  240                          }}
  241                      }}
  242                  }}
  243              }}
  244          }}"""
  245  
  246          contents = self.post(
  247              path="/graphql",
  248              data={"query": query},
  249          )
  250          results: Sequence[Mapping[str, Any]] = (
  251              contents.get("data", {})
  252              .get("repository", {})
  253              .get("ref", {})
  254              .get("target", {})
  255              .get("blame", [])
  256          )
  257          return results
  258  
```

## Candidate fixes (4 later commits to this file remove a blamed line; 58 later commits up to 2023-06-30 checked)

### Candidate 1: 6b737509be8c (2022-09-29)

Message:

```
fix(commit-context): Update GitHub fetch blame query (#39438)
```

Removed blamed lines: `.get("blame", [])`; `blame(path: {path}) {{`; `ref(qualifiedName: {ref}) {{`; `repository(name: {name}, owner: {owner}) {{`

Patch of this file:

```diff
@@ -218,11 +218,11 @@ def get_blame_for_file(
     ) -> Sequence[Mapping[str, Any]]:
         [owner, name] = repo.name.split("/")
         query = f"""query {{
-            repository(name: {name}, owner: {owner}) {{
-                ref(qualifiedName: {ref}) {{
+            repository(name: "{name}", owner: "{owner}") {{
+                ref(qualifiedName: "{ref}") {{
                     target {{
                         ... on Commit {{
-                            blame(path: {path}) {{
+                            blame(path: "{path}") {{
                                 ranges {{
                                         commit {{
                                             oid
@@ -253,7 +253,8 @@ def get_blame_for_file(
             .get("repository", {})
             .get("ref", {})
             .get("target", {})
-            .get("blame", [])
+            .get("blame", {})
+            .get("ranges", [])
         )
         return results
```

### Candidate 2: d6bcead1be02 (2022-10-11)

Message:

```
fix(github): Add pagination when fetching repositories (#39750)

We are not using pagination for Github's repositories endpoint. This means we were getting up to a maximum of 100 repositories.

I do not know how no one hit any issues in the past.

This is work to support WOR-2234 and creating automatic code mappings.
```

Removed blamed lines: `return results`

Patch of this file:

```diff
@@ -1,5 +1,6 @@
 from __future__ import annotations
 
+import logging
 from datetime import datetime
 from typing import Any, Mapping, Sequence
 
@@ -11,12 +12,16 @@
 from sentry.utils import jwt
 from sentry.utils.json import JSONData
 
+logger = logging.getLogger("sentry.integrations.github")
+
 
 class GitHubClientMixin(ApiClient):  # type: ignore
     allow_redirects = True
 
     base_url = "https://api.github.com"
     integration_name = "github"
+    # Github gives us links to navigate, however, let's be safe in case we're fed garbage
+    page_number_limit = 50  # With a default of 100 per page -> 5,000 items
 
     def get_jwt(self) -> str:
         return get_jwt()
@@ -63,12 +68,20 @@ def get_repo(self, repo: str) -> JSONData:
         return repository
 
     def get_repositories(self) -> Sequence[JSONData]:
+        """
+        This fetches all repositories accessible to the Github App
+        https://docs.github.com/en/rest/apps/installations#list-repositories-accessible-to-the-app-installation
+        """
         # Explicitly typing to satisfy mypy.
-        repositories: JSONData = self.get("/installation/repositories", params={"per_page": 100})
-        repos = repositories["repositories"]
+        repos: JSONData = self.get_with_pagination(
+            "/installation/repositories", response_key="repositories"
+        )
         return [repo for repo in repos if not repo.get("archived")]
 
+    # XXX: Find alternative approach
     def search_repositories(self, query: bytes) -> Mapping[str, Sequence[JSONData]]:
+        """Find repositories matching a query.
+        NOTE: This API is rate limited to 30 requests/minute"""
         # Explicitly typing to satisfy mypy.
         repositories: Mapping[str, Sequence[JSONData]] = self.get(
             "/search/repositories", params={"q": query}
@@ -80,12 +93,14 @@ def get_assignees(self, repo: str) -> Sequence[JSONData]:
         assignees: Sequence[JSONData] = self.get_with_pagination(f"/repos/{repo}/assignees")
         return assignees
 
-    def get_with_pagination(self, path: str, *args: Any, **kwargs: Any) -> Sequence[JSONData]:
+    def get_with_pagination(self, path: str, response_key: str | None = None) -> Sequence[JSONData]:
         """
         Github uses the Link header to provide pagination links. Github
         recommends using the provided link relations and not constructing our
         own URL.
         https://docs.github.com/en/rest/guides/traversing-with-pagination
+
+        Use response_key when the API stores the results within a key.
         """
         with sentry_sdk.configure_scope() as scope:
             if scope.span is not None:
@@ -103,13 +118,14 @@ def get_with_pagination(self, path: str, *args: Any, **kwargs: Any) -> Sequence[
             sampled=True,
         ):
             output = []
+
             resp = self.get(path, params={"per_page": self.page_size})
-            output.extend(resp)
+            output.extend(resp) if not response_key else output.extend(resp[response_key])
             page_number = 1
 
             while get_next_link(resp) and page_number < self.page_number_limit:
                 resp = self.get(get_next_link(resp))
-                output.extend(resp)
+                output.extend(resp) if not response_key else output.extend(resp[response_key])
                 page_number += 1
             return output
 
@@ -138,6 +154,7 @@ def create_comment(self, repo: str, issue_id: str, data: Mapping[str, Any]) -> J
     def get_user(self, gh_username: str) -> JSONData:
         return self.get(f"/users/{gh_username}")
 
+    # subclassing BaseApiClient request method
     def request(
         self,
         method: str,
@@ -195,13 +212,6 @@ def check_file(self, repo: Repository, path: str, version: str) -> str | None:
         )
         return file
 
-    def search_file(
-        self, repo: Repository, filename: str
-    ) -> Mapping[str, Sequence[Mapping[str, Any]]]:
-        query = f"filename:{filename}+repo:{repo}"
-        results: Mapping[str, Any] = self.get(path="/search/code", params={"q": query})
-        return results
-
     def get_file(self, repo: Repository, path: str, ref: str) -> str:
         """Get the contents of a file
```

### Candidate 3: 35bd28dd4409 (2022-10-14)

Message:

```
feat(commit-context): Support GitLab (#39381)

## Objective:
Add Commit Context feature to the GitLab integration.
```

Removed blamed lines: `self, repo: Repository, path: str, ref: str`

Patch of this file:

```diff
@@ -260,7 +260,7 @@ def get_file(self, repo: Repository, path: str, ref: str) -> str:
         return b64decode(encoded_content).decode("utf-8")
 
     def get_blame_for_file(
-        self, repo: Repository, path: str, ref: str
+        self, repo: Repository, path: str, ref: str, lineno: int
     ) -> Sequence[Mapping[str, Any]]:
         [owner, name] = repo.name.split("/")
         query = f"""query {{
```

### Candidate 4: ae7a8e49dca4 (2022-10-31)

Message:

```
feat(commit-context): Handle AttributeError while still capturing (#40659)

Fixes
[SENTRY-W4Z](https://sentry.io/organizations/sentry/issues/3635082165/)
```

Removed blamed lines: `.get("ref", {})`; `.get("repository", {})`; `.get("target", {})`; `contents.get("data", {})`; `results: Sequence[Mapping[str, Any]] = (`; `return results`

Patch of this file:

```diff
@@ -320,15 +320,19 @@ def get_blame_for_file(
             path="/graphql",
             data={"query": query},
         )
-        results: Sequence[Mapping[str, Any]] = (
-            contents.get("data", {})
-            .get("repository", {})
-            .get("ref", {})
-            .get("target", {})
-            .get("blame", {})
-            .get("ranges", [])
-        )
-        return results
+        try:
+            results: Sequence[Mapping[str, Any]] = (
+                contents.get("data", {})
+                .get("repository", {})
+                .get("ref", {})
+                .get("target", {})
+                .get("blame", {})
+                .get("ranges", [])
+            )
+            return results
+        except AttributeError as e:
+            sentry_sdk.capture_exception(e)
+            return []
 
 
 class GitHubAppsClient(GitHubClientMixin):
```

# case126: getsentry/sentry 6bb7be0641f9

Sampled file (the only file the models saw): `src/sentry/integrations/github/client.py` · committed 2022-09-14 08:54:25-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
feat(commit-context): Add blame API to GitHub/GitLab clients (#38646)
```

## Diff of the sampled file

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

## Other files changed by this commit (2)

- `src/sentry/integrations/gitlab/client.py` (+10 −0)
- `tests/sentry/integrations/github/test_client.py` (+51 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 6b737509be8c (2022-09-29) · pull request #39438: fix(commit-context): Update GitHub fetch blame query

Pull-request labels: Scope: Backend

Commit message:

```
fix(commit-context): Update GitHub fetch blame query (#39438)
```

This fix changes 3 files. Lines it removes that the commit above had added:

- in the sampled file: `.get("blame", [])`; `blame(path: {path}) {{`; `ref(qualifiedName: {ref}) {{`; `repository(name: {name}, owner: {owner}) {{`
- in `tests/sentry/integrations/github/test_client.py`: `blame(path: {path}) {{`; `ref(qualifiedName: {ref}) {{`; `repository(name: foo, owner: Test-Organization) {{`

Patch of the sampled file in this fix:

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

Patch of `tests/sentry/integrations/github/test_client.py` in this fix:

```diff
@@ -210,11 +210,11 @@ def test_get_blame_for_file(self, get_jwt):
         path = "src/sentry/integrations/github/client.py"
         ref = "master"
         query = f"""query {{
-            repository(name: foo, owner: Test-Organization) {{
-                ref(qualifiedName: {ref}) {{
+            repository(name: "foo", owner: "Test-Organization") {{
+                ref(qualifiedName: "{ref}") {{
                     target {{
                         ... on Commit {{
-                            blame(path: {path}) {{
+                            blame(path: "{path}") {{
                                 ranges {{
                                         commit {{
                                             oid
@@ -244,7 +244,7 @@ def test_get_blame_for_file(self, get_jwt):
         resp = self.client.get_blame_for_file(self.repo, path, ref)
         assert (
             responses.calls[1].request.body
-            == b'{"query": "query {\\n            repository(name: foo, owner: Test-Organization) {\\n                ref(qualifiedName: master) {\\n                    target {\\n                        ... on Commit {\\n                            blame(path: src/sentry/integrations/github/client.py) {\\n                                ranges {\\n                                        commit {\\n                                            oid\\n                                            author {\\n                                                name\\n                                                email\\n                                            }\\n                                            message\\n                                            committedDate\\n                                        }\\n                                    startingLine\\n                                    endingLine\\n                                    age\\n                                }\\n                            }\\n                        }\\n                    }\\n                }\\n            }\\n        }"}'
+            == b'{"query": "query {\\n            repository(name: \\"foo\\", owner: \\"Test-Organization\\") {\\n                ref(qualif
[... cut ...]
```

# case094: getsentry/sentry bdcd185bc020

Sampled file (the only file the models saw): `src/sentry/integrations/github/client.py` · committed 2022-09-22 08:11:58-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
feat(commit-context): Process commit context task (#38984)

## Objective:

We want to use the GitHub blame API to determine who is the committer
for the first in_app stacktrace frame and assign them as a Suspect
Commit GroupOwner.

This task is feature flagged for an internal release.
```

## Diff of the sampled file

```diff
@@ -231,6 +231,7 @@ class GitHubClientMixin(ApiClient):  # type: ignore
                                                 email
                                             }}
                                             message
+                                            committedDate
                                         }}
                                     startingLine
                                     endingLine
```

## Other files changed by this commit (12)

- `src/sentry/conf/server.py` (+1 −0)
- `src/sentry/integrations/github/integration.py` (+36 −1)
- `src/sentry/integrations/mixins/commit_context.py` (+43 −0)
- `src/sentry/integrations/utils/commit_context.py` (+37 −0)
- `src/sentry/ownership/grammar.py` (+14 −0)
- `src/sentry/tasks/commit_context.py` (+141 −0)
- `src/sentry/tasks/post_process.py` (+21 −8)
- `src/sentry/utils/committers.py` (+10 −7)
- `src/sentry/utils/sdk.py` (+1 −0)
- `tests/sentry/integrations/github/test_client.py` (+2 −1)
- `tests/sentry/ownership/test_grammar.py` (+14 −0)
- `tests/sentry/tasks/test_commit_context.py` (+158 −0)

## Fix commits that the dataset links to this commit (3)

### Fix 1: 6b737509be8c (2022-09-29) · pull request #39438: fix(commit-context): Update GitHub fetch blame query

Pull-request labels: Scope: Backend

Commit message:

```
fix(commit-context): Update GitHub fetch blame query (#39438)
```

This fix changes 3 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix changes this file, but not lines the commit added)
- in `src/sentry/integrations/github/integration.py`: `blame.get("committedDate"), "%Y-%m-%dT%H:%M:%SZ"`
- in `tests/sentry/integrations/github/test_client.py`: `== b'{"query": "query {\\n            repository(name: foo, owner: Test-Organization) {\\n                ref(qualifiedName: master) {\\n                    target {\\n                        ... on Commit {\\n                            blame(path: src/sentry/integrations/github/client.py) {\\n                                ranges {\\n                                        commit {\\n                                            oid\\n                                            author {\\n                                                name\\n                                                email\\n                                            }\\n                                            message\\n                                            committedDate\\n                                        }\\n                                    startingLine\\n                                    endingLine\\n                                    age\\n                                }\\n                            }\\n                        }\\n                    }\\n                }\\n            }\\n        }"}'`

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

Patch of `src/sentry/integrations/github/integration.py` in this fix:

```diff
@@ -182,7 +182,7 @@ def get_commit_context(
                     if blame.get("startingLine", 0) <= lineno <= blame.get("endingLine", 0)
                 ),
                 key=lambda blame: datetime.strptime(
-                    blame.get("committedDate"), "%Y-%m-%dT%H:%M:%SZ"
+                    blame.get("commit", {}).get("committedDate"), "%Y-%m-%dT%H:%M:%SZ"
                 ),
             )[-1]
         except IndexError:
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

### Fix 2: 8dc381b0528e (2022-10-26) · pull request #40564: fix(commit-context): Handle ValueError from max()

Pull-request labels: Scope: Backend

Commit message:

```
fix(commit-context): Handle ValueError from max() (#40564)

Fixes
[SENTRY-WBF](https://sentry.io/organizations/sentry/issues/3696678457/?project=1&referrer=jira_integration)
```

Pull-request description:

```
Fixes [SENTRY-WBF](https://sentry.io/organizations/sentry/issues/3696678457/?project=1&referrer=jira_integration)
```

This fix changes 2 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/sentry/integrations/github/integration.py`: `except IndexError:`

Patch of `src/sentry/integrations/github/integration.py` in this fix:

```diff
@@ -201,7 +201,7 @@ def get_commit_context(
                     blame.get("commit", {}).get("committedDate"), "%Y-%m-%dT%H:%M:%SZ"
                 ),
             )
-        except IndexError:
+        except (ValueError, IndexError):
             return None
 
         commitInfo = commit.get("commit")
```

### Fix 3: f20b23f745ae (2022-10-03) · pull request #39533: fix(commit-context): Frames start from the bottom of the error stack

Pull-request labels: Scope: Backend

Commit message:

```
fix(commit-context): Frames start from the bottom of the error stack (#39533)

## Objective:
Frames start from the bottom of the error stack. So currently the Commit
Context is matching on frames of base libraries. Whereas the value of
Commit Context is in the top-level frame that cause the exception.
```

Pull-request description:

```
## Objective:
Frames start from the bottom of the error stack. So currently the Commit Context is matching on frames of base libraries. Whereas the value of Commit Context is in the top-level frame that cause the exception.
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/sentry/tasks/commit_context.py`: `frame = next(filter(lambda frame: frame.get("in_app", False), frames), None)`

Patch of `src/sentry/tasks/commit_context.py` in this fix:

```diff
@@ -77,7 +77,7 @@ def process_commit_context(
                 frames = munged[1]
 
             # First frame in the stacktrace that is "in_app"
-            frame = next(filter(lambda frame: frame.get("in_app", False), frames), None)
+            frame = next(filter(lambda frame: frame.get("in_app", False), frames[::-1]), None)
 
             if not frame:
                 metrics.incr(
```

# case123: getsentry/sentry 35bd28dd4409

Sampled file (the only file the models saw): `src/sentry/integrations/mixins/commit_context.py` · committed 2022-10-14 03:20:21-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
feat(commit-context): Support GitLab (#39381)

## Objective:
Add Commit Context feature to the GitLab integration.
```

## Diff of the sampled file

```diff
@@ -12,7 +12,9 @@ class CommitContextMixin:
     # dynamically given a search query
     repo_search = False
 
-    def get_blame_for_file(self, repo: Repository, filepath: str, ref: str) -> str | None:
+    def get_blame_for_file(
+        self, repo: Repository, filepath: str, ref: str, lineno: int
+    ) -> str | None:
         """
         Calls the client's `get_blame_for_file` method to see if the file has a blame list.
 
@@ -26,7 +28,7 @@ class CommitContextMixin:
         except Identity.DoesNotExist:
             return None
         try:
-            response = client.get_blame_for_file(repo, filepath, ref)
+            response = client.get_blame_for_file(repo, filepath, ref, lineno)
             if response is None:
                 return None
         except IdentityNotValid:
```

## Other files changed by this commit (7)

- `src/sentry/integrations/github/client.py` (+1 −1)
- `src/sentry/integrations/github/integration.py` (+4 −3)
- `src/sentry/integrations/gitlab/client.py` (+4 −2)
- `src/sentry/integrations/gitlab/integration.py` (+39 −1)
- `tests/sentry/integrations/github/test_client.py` (+1 −1)
- `tests/sentry/integrations/gitlab/test_integration.py` (+86 −0)
- `tests/sentry/tasks/test_commit_context.py` (+48 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 8dc381b0528e (2022-10-26) · pull request #40564: fix(commit-context): Handle ValueError from max()

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
- in `src/sentry/integrations/gitlab/integration.py`: `except IndexError:`

Patch of `src/sentry/integrations/gitlab/integration.py` in this fix:

```diff
@@ -162,7 +162,7 @@ def get_commit_context(
                     blame.get("commit", {}).get("committed_date"), "%Y-%m-%dT%H:%M:%S.%fZ"
                 ),
             )
-        except IndexError:
+        except (ValueError, IndexError):
             return None
 
         commitInfo = commit.get("commit")
```

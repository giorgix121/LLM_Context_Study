# case123: getsentry/sentry 35bd28dd4409

File: `src/sentry/integrations/mixins/commit_context.py` · committed 2022-10-14 03:20:21-01:00 · SZZ label: RISKY

## Commit message

```
feat(commit-context): Support GitLab (#39381)

## Objective:
Add Commit Context feature to the GitLab integration.
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
   15      def get_blame_for_file(
   16          self, repo: Repository, filepath: str, ref: str, lineno: int
   17      ) -> str | None:
   31              response = client.get_blame_for_file(repo, filepath, ref, lineno)
```

## Candidate fixes (1 later commits to this file remove a blamed line; 1 later commits up to 2023-06-30 checked)

### Candidate 1: 30493fe4de53 (2023-02-13)

Message:

```
ref(commit-context): fix iterating over None. add type-checking for commit_context mixin (#44538)

Fix a bug where we're iterating over None. Also added some typing which
threw the error.

Fixes SENTRY-YEQ
```

Removed blamed lines: `) -> str | None:`

Patch of this file:

```diff
@@ -1,20 +1,32 @@
 from __future__ import annotations
 
-from typing import Mapping
+from typing import Any, Mapping, Protocol, Sequence
 
 from sentry.auth.exceptions import IdentityNotValid
 from sentry.models import Identity, Repository
 from sentry.shared_integrations.exceptions import ApiError
 
 
-class CommitContextMixin:
+class GetBlameForFile(Protocol):
+    def get_blame_for_file(
+        self, repo: Repository, filepath: str, ref: str, lineno: int
+    ) -> Sequence[Mapping[str, Any]]:
+        ...
+
+
+class GetClient(Protocol):
+    def get_client(self) -> GetBlameForFile:
+        ...
+
+
+class CommitContextMixin(GetClient):
     # whether or not integration has the ability to search through Repositories
     # dynamically given a search query
     repo_search = False
 
     def get_blame_for_file(
         self, repo: Repository, filepath: str, ref: str, lineno: int
-    ) -> str | None:
+    ) -> Sequence[Mapping[str, Any]] | None:
         """
         Calls the client's `get_blame_for_file` method to see if the file has a blame list.
 
@@ -29,8 +41,6 @@ def get_blame_for_file(
             return None
         try:
             response = client.get_blame_for_file(repo, filepath, ref, lineno)
-            if response is None:
-                return None
         except IdentityNotValid:
             return None
         except ApiError as e:
@@ -39,7 +49,7 @@ def get_blame_for_file(
         return response
 
     def get_commit_context(
-        self, repo: Repository, filepath: str, branch: str, event_frame
+        self, repo: Repository, filepath: str, branch: str, event_frame: Mapping[str, Any]
     ) -> Mapping[str, str] | None:
         """Formats the source code url used for stack trace linking."""
         raise NotImplementedError
```

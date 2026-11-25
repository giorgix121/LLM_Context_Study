# case094: getsentry/sentry bdcd185bc020

File: `src/sentry/integrations/github/client.py` · committed 2022-09-22 08:11:58-01:00 · SZZ label: RISKY

## Commit message

```
feat(commit-context): Process commit context task (#38984)

## Objective:

We want to use the GitHub blame API to determine who is the committer
for the first in_app stacktrace frame and assign them as a Suspect
Commit GroupOwner.

This task is feature flagged for an internal release.
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
  234                                              committedDate
```

## Candidate fixes (0 later commits to this file remove a blamed line; 57 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

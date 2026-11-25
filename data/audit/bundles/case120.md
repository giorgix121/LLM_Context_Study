# case120: getsentry/sentry 1e4e6f8d5c93

File: `src/sentry/eventstream/kafka/protocol.py` · committed 2022-10-17 02:43:08-01:00 · SZZ label: RISKY

## Commit message

```
feat(eventstream): Add consumer strategy for post process forwarder (#39502)

Processing steps for the Arroyo version of the post process forwarder. This is close to equivalent to what the non-Arroyo post process forwarder consumer is doing today. It's not yet being used. The consumer and update to the CLI entrypoint will be added as a follow up.
```

## Diff of the target file

```diff
@@ -93,7 +93,7 @@ class InvalidVersion(Exception):
     pass
 
 
-def get_task_kwargs_for_message(value: str) -> Optional[Mapping[str, Any]]:
+def get_task_kwargs_for_message(value: bytes) -> Optional[Mapping[str, Any]]:
     """
     Decodes a message body, returning a dictionary of keyword arguments that
     can be applied to a post-processing task, or ``None`` if no task should be
```

## Lines SZZ blamed (line numbers in the new version)

```
   96  def get_task_kwargs_for_message(value: bytes) -> Optional[Mapping[str, Any]]:
```

## Candidate fixes (0 later commits to this file remove a blamed line; 3 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

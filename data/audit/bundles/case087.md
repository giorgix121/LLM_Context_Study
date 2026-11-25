# case087: getsentry/sentry d314d19e59a0

File: `src/sentry/eventstream/kafka/postprocessworker.py` · committed 2022-10-19 03:14:34-01:00 · SZZ label: RISKY

## Commit message

```
feat: Add the streaming version of the post process forwarder (#40074)

This is not yet being used, will eventually replace the existing post process forwarder wholesale.

Depends on https://github.com/getsentry/sentry/pull/39502
```

## Diff of the target file

```diff
@@ -67,7 +67,7 @@ def dispatch_post_process_group_task(
     project_id: int,
     group_id: Optional[int],
     is_new: bool,
-    is_regression: bool,
+    is_regression: Optional[bool],
     is_new_group_environment: bool,
     primary_hash: Optional[str],
     skip_consume: bool = False,
@@ -89,7 +89,7 @@ def dispatch_post_process_group_task(
         )
 
 
-def _get_task_kwargs_and_dispatch(message: Message):
+def _get_task_kwargs_and_dispatch(message: Message) -> None:
     task_kwargs = _get_task_kwargs(message)
     if not task_kwargs:
         return None
```

## Lines SZZ blamed (line numbers in the new version)

```
   70      is_regression: Optional[bool],
   92  def _get_task_kwargs_and_dispatch(message: Message) -> None:
```

## Candidate fixes (1 later commits to this file remove a blamed line; 9 later commits up to 2023-06-30 checked)

### Candidate 1: c86a9a318e4f (2023-02-15)

Message:

```
ref(post-process-forwarder): Use RunTaskInThreads strategy from Arroyo (#44636)

Use Arroyo's built in RunTaskInThreads strategy to reduce boilerplate in
the post process forwarder. Also deletes some unused code.
```

Removed blamed lines: `def _get_task_kwargs_and_dispatch(message: Message) -> None:`; `is_regression: Optional[bool],`

Patch of this file:

```diff
@@ -10,14 +10,11 @@
 from typing import Any, Generator, Mapping, MutableMapping, Optional, Tuple
 
 from sentry import options
-from sentry.eventstream.base import GroupStates
 from sentry.eventstream.kafka.protocol import (
     get_task_kwargs_for_message,
     get_task_kwargs_for_message_from_headers,
 )
-from sentry.tasks.post_process import post_process_group
 from sentry.utils import metrics
-from sentry.utils.cache import cache_key_for_event
 
 logger = logging.getLogger(__name__)
 
@@ -87,45 +84,3 @@ def _record_metrics(partition: int, task_kwargs: Mapping[str, Any]) -> None:
                 tags={"partition": partition, "type": event_type},
                 sample_rate=1,
             )
-
-
-def dispatch_post_process_group_task(
-    event_id: str,
-    project_id: int,
-    group_id: Optional[int],
-    is_new: bool,
-    is_regression: Optional[bool],
-    is_new_group_environment: bool,
-    primary_hash: Optional[str],
-    queue: str,
-    skip_consume: bool = False,
-    group_states: Optional[GroupStates] = None,
-    occurrence_id: Optional[str] = None,
-) -> None:
-    if skip_consume:
-        logger.info("post_process.skip.raw_event", extra={"event_id": event_id})
-    else:
-        cache_key = cache_key_for_event({"project": project_id, "event_id": event_id})
-
-        post_process_group.apply_async(
-            kwargs={
-                "is_new": is_new,
-                "is_regression": is_regression,
-                "is_new_group_environment": is_new_group_environment,
-                "primary_hash": primary_hash,
-                "cache_key": cache_key,
-                "group_id": group_id,
-                "group_states": group_states,
-                "occurrence_id": occurrence_id,
-            },
-            queue=queue,
-        )
-
-
-def _get_task_kwargs_and_dispatch(message: Message) -> None:
-    task_kwargs = _get_task_kwargs(message)
-    if not task_kwargs:
-        return None
-
-    _record_metrics(message.partition(), task_kwargs)
-    dispatch_post_process_group_task(**task_kwargs)
```

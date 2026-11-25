# case033: getsentry/sentry ce3e457ef18f

File: `src/sentry/eventstream/kafka/protocol.py` · committed 2022-10-25 07:32:32-01:00 · SZZ label: RISKY

## Commit message

```
feat(perf-issues): Move queue info for post_process into headers (ISP… (#40239)

Re-do of https://github.com/getsentry/sentry/pull/39946 as merge
conflict didn't mesh right.

Sends dedicated issue category data to post_process_group call so we can
route to the appropriate celery queue

Will need to include changes from
https://github.com/getsentry/sentry/pull/40283 to be merged first and an
ensuing PR to remove the old queue.
```

## Diff of the target file

```diff
@@ -46,6 +46,7 @@ def basic_protocol_handler(
 
         if task_state:
             kwargs["group_states"] = task_state.get("group_states")
+            kwargs["queue"] = task_state.get("queue")
 
         return kwargs
 
@@ -211,6 +212,13 @@ def get_task_kwargs_for_message_from_headers(
                 )
             task_state["group_states"] = group_states
 
+            # default in case queue is not sent
+            task_state["queue"] = (
+                decode_str(header_data["queue"])
+                if "queue" in header_data
+                else "post_process_errors"
+            )
+
         else:
             event_data = {}
             task_state = {}
```

## Lines SZZ blamed (line numbers in the new version)

```
   49              kwargs["queue"] = task_state.get("queue")
  215              # default in case queue is not sent
  216              task_state["queue"] = (
  217                  decode_str(header_data["queue"])
  218                  if "queue" in header_data
  219                  else "post_process_errors"
  220              )
  221  
```

## Candidate fixes (1 later commits to this file remove a blamed line; 2 later commits up to 2023-06-30 checked)

### Candidate 1: 9e96ee69c81d (2023-06-20)

Message:

```
ref: fix unnecessary casts hiding type errors (#51289)

<!-- Describe your PR here. -->
```

Removed blamed lines: `decode_str(header_data["queue"])`; `else "post_process_errors"`; `if "queue" in header_data`

Patch of this file:

```diff
@@ -1,15 +1,5 @@
 import logging
-from typing import (
-    Any,
-    Callable,
-    FrozenSet,
-    Mapping,
-    MutableMapping,
-    Optional,
-    Sequence,
-    Tuple,
-    cast,
-)
+from typing import Any, Callable, FrozenSet, Mapping, MutableMapping, Optional, Sequence, Tuple
 
 from sentry.utils import json, metrics
 
@@ -120,7 +110,7 @@ def get_task_kwargs_for_message(value: bytes) -> Optional[Mapping[str, Any]]:
     return handler(*payload[1:])
 
 
-def decode_str(value: Optional[bytes]) -> str:
+def decode_str(value: bytes) -> str:
     assert isinstance(value, bytes)
     return value.decode("utf-8")
 
@@ -131,7 +121,7 @@ def decode_optional_str(value: Optional[bytes]) -> Optional[str]:
     return decode_str(value)
 
 
-def decode_int(value: Optional[bytes]) -> int:
+def decode_int(value: bytes) -> int:
     assert isinstance(value, bytes)
     return int(value)
 
@@ -154,7 +144,7 @@ def decode_optional_list_str(value: Optional[str]) -> Optional[Sequence[Any]]:
     if not isinstance(parsed, list):
         raise ValueError(f"'{value}' could not be parsed into an instance of list.")
 
-    return cast(Sequence[Any], json.loads(value))
+    return json.loads(value)
 
 
 def get_task_kwargs_for_message_from_headers(
@@ -166,8 +156,15 @@ def get_task_kwargs_for_message_from_headers(
     """
     try:
         header_data = {k: v for k, v in headers}
-        version = decode_int(header_data["version"])
-        operation = decode_str(header_data["operation"])
+
+        def _required(k: str) -> bytes:
+            v = header_data[k]
+            if v is None:
+                raise ValueError(f"expected {k!r} to be non-None")
+            return v
+
+        version = decode_int(_required("version"))
+        operation = decode_str(_required("operation"))
 
         if operation == "insert":
             if "group_id" not in header_data:
@@ -176,9 +173,9 @@ def get_task_kwargs_for_message_from_headers(
                 header_data["primary_hash"] = None
 
             primary_hash = decode_optional_str(header_data["primary_hash"])
-            event_id = decode_str(header_data["event_id"])
+            event_id = decode_str(_required("event_id"))
             group_id = decode_optional_int(header_data["group_id"])
-            project_id = decode_int(header_data["project_id"])
+            project_id = decode_int(_required("project_id"))
 
             event_data = {
                 "event_id": event_id,
@@ -188,12 +185,10 @@ def get_task_kwargs_for_message_from_headers(
                 "occurrence_id": decode_optional_str(header_data.get("occurrence_id")),
             }
 
-            skip_consume = decode_bool(cast(bytes, header_data["skip_consume"]))
-            is_new = decode_bool(cast(bytes, header_data["is_new"]))
-            is_regression = decode_bool(cast(bytes, header_data["is_regression"]))
-            is_new_group_environment = decode_bool(
-                cast(bytes, header_data["is_new_group_environment"])
-            )
+            skip_consume = decode_bool(_required("skip_consume"))
+            is_new = decode_bool(_required("is_new"))
+            is_regression = decode_bool(_required("is_regression"))
+            is_new_group_environment = decode_bool(_required("is_new_group_environment"))
 
             task_state: MutableMapping[str, Any] = {
                 "skip_consume": skip_consume,
@@ -216,9 +211,7 @@ def get_task_kwargs_for_message_from_headers(
 
             # default in case queue is not sent
             task_state["queue"] = (
-                decode_str(header_data["queue"])
-                if "queue" in header_data
-                else "post_process_errors"
+                decode_str(_required("queue")) if "queue" in header_data else "post_process_errors"
             )
 
         else:
```

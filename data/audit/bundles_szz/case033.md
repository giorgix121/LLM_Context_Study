# case033: getsentry/sentry ce3e457ef18f

Sampled file (the only file the models saw): `src/sentry/eventstream/kafka/protocol.py` · committed 2022-10-25 07:32:32-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

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

## Diff of the sampled file

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

## Other files changed by this commit (13)

- `src/sentry/eventstream/base.py` (+19 −8)
- `src/sentry/eventstream/kafka/backend.py` (+1 −0)
- `src/sentry/eventstream/kafka/consumer_strategy.py` (+2 −0)
- `src/sentry/eventstream/kafka/postprocessworker.py` (+12 −8)
- `src/sentry/eventstream/snuba.py` (+6 −1)
- `src/sentry/tasks/post_process.py` (+0 −1)
- `src/sentry/testutils/helpers/task_runner.py` (+8 −8)
- `src/sentry/utils/pytest/stale_database_reads.py` (+2 −2)
- `tests/sentry/eventstream/kafka/test_consumer.py` (+3 −0)
- `tests/sentry/eventstream/kafka/test_consumer_strategy.py` (+2 −0)
- `tests/sentry/eventstream/kafka/test_postprocessworker.py` (+25 −16)
- `tests/sentry/eventstream/kafka/test_protocol.py` (+9 −1)
- `tests/sentry/eventstream/test_eventstream.py` (+70 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: ec98dfcf4e71 (2022-11-01) · pull request #40818: fix: Fix streaming post process forwarder

Pull-request labels: Scope: Backend

Commit message:

```
fix: Fix streaming post process forwarder (#40818)

https://github.com/getsentry/sentry/pull/40239 introduced a bug where
the arguments were called in the wrong order. Since the
postprocessworker.py file is not being type checked this was not caught
in CI.

This code will eventually be removed and only exists temporarily to
support our two side by side post process forwarder implementations.
```

Pull-request description:

```
https://github.com/getsentry/sentry/pull/40239 introduced a bug where the arguments were called in the wrong order. Since the postprocessworker.py file is not being type checked this was not caught in CI.

This code will eventually be removed and only exists temporarily to support our two side by side post process forwarder implementations.
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/sentry/eventstream/kafka/consumer_strategy.py`: `queue,`; `queue: str,`

Patch of `src/sentry/eventstream/kafka/consumer_strategy.py` in this fix:

```diff
@@ -34,8 +34,8 @@ def dispatch_post_process_group_task(
     is_new: bool,
     is_regression: Optional[bool],
     is_new_group_environment: bool,
-    queue: str,
     primary_hash: Optional[str],
+    queue: str,
     skip_consume: bool = False,
     group_states: Optional[GroupStates] = None,
 ) -> None:
@@ -46,8 +46,8 @@ def dispatch_post_process_group_task(
         is_new,
         is_regression,
         is_new_group_environment,
-        queue,
         primary_hash,
+        queue,
         skip_consume,
         group_states,
     )
```

# case120: getsentry/sentry 1e4e6f8d5c93

Sampled file (the only file the models saw): `src/sentry/eventstream/kafka/protocol.py` · committed 2022-10-17 02:43:08-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
feat(eventstream): Add consumer strategy for post process forwarder (#39502)

Processing steps for the Arroyo version of the post process forwarder. This is close to equivalent to what the non-Arroyo post process forwarder consumer is doing today. It's not yet being used. The consumer and update to the CLI entrypoint will be added as a follow up.
```

## Diff of the sampled file

```diff
@@ -93,7 +93,7 @@ class InvalidVersion(Exception):
     pass
 
 
-def get_task_kwargs_for_message(value: str) -> Optional[Mapping[str, Any]]:
+def get_task_kwargs_for_message(value: bytes) -> Optional[Mapping[str, Any]]:
     """
     Decodes a message body, returning a dictionary of keyword arguments that
     can be applied to a post-processing task, or ``None`` if no task should be
```

## Other files changed by this commit (4)

- `mypy.ini` (+3 −1)
- `src/sentry/eventstream/kafka/consumer_strategy.py` (+146 −0)
- `tests/sentry/eventstream/kafka/test_consumer_strategy.py` (+68 −0)
- `tests/sentry/eventstream/kafka/test_synchronized.py` (+0 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: c1128fa6c082 (2022-10-24) · pull request #40457: fix(post-process-forwarder): Fix commit log consumer config

Pull-request labels: Scope: Backend

Commit message:

```
fix(post-process-forwarder): Fix commit log consumer config (#40457)

Incorrect commit log consumer config caused the streaming version of the post process forwarder to not work properly when we tested it. Specifically since the group_id was the same on each pod only one got the assignment and the rest were idle.

Also includes a fix for metric recording so that the metrics being emitted in the new implementation match the previous one.
```

Pull-request description:

```
Incorrect commit log consumer config caused the streaming version of the post process forwarder to not work properly when we tested it. Specifically since the group_id was the same on each pod only one got the assignment and the rest were idle.

Also includes a fix for metric recording so that the metrics being emitted in the new implementation match the previous one.
```

This fix changes 3 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/sentry/eventstream/kafka/consumer_strategy.py`: `from sentry.eventstream.kafka.postprocessworker import _sampled_eventstream_timer`

Patch of `src/sentry/eventstream/kafka/consumer_strategy.py` in this fix:

```diff
@@ -11,7 +11,7 @@
 
 from sentry import options
 from sentry.eventstream.base import GroupStates
-from sentry.eventstream.kafka.postprocessworker import _sampled_eventstream_timer
+from sentry.eventstream.kafka.postprocessworker import _record_metrics, _sampled_eventstream_timer
 from sentry.eventstream.kafka.postprocessworker import (
     dispatch_post_process_group_task as _dispatch_post_process_group_task,
 )
@@ -72,6 +72,7 @@ def _get_task_kwargs_and_dispatch(message: Message[KafkaPayload]) -> None:
     if not task_kwargs:
         return None
 
+    _record_metrics(message.partition.index, task_kwargs)
     dispatch_post_process_group_task(**task_kwargs)
```

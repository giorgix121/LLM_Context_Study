# case087: getsentry/sentry d314d19e59a0

Sampled file (the only file the models saw): `src/sentry/eventstream/kafka/postprocessworker.py` · committed 2022-10-19 03:14:34-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
feat: Add the streaming version of the post process forwarder (#40074)

This is not yet being used, will eventually replace the existing post process forwarder wholesale.

Depends on https://github.com/getsentry/sentry/pull/39502
```

## Diff of the sampled file

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

## Other files changed by this commit (7)

- `src/sentry/eventstream/base.py` (+1 −0)
- `src/sentry/eventstream/kafka/backend.py` (+87 −26)
- `src/sentry/eventstream/kafka/consumer_strategy.py` (+9 −3)
- `src/sentry/eventstream/kafka/streaming_consumer.py` (+0 −0)
- `src/sentry/runner/commands/run.py` (+13 −0)
- `tests/sentry/eventstream/kafka/test_consumer.py` (+58 −2)
- `tests/sentry/eventstream/kafka/test_consumer_strategy.py` (+1 −1)

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
- in `src/sentry/eventstream/kafka/backend.py`: `auto_offset_reset=initial_offset_reset,`; `bool(strict_offset_reset),`; `commit_log_consumer=KafkaConsumer(configuration),`; `configuration = build_kafka_consumer_configuration(`; `consumer=KafkaConsumer(configuration),`; `get_kafka_consumer_cluster_options(cluster_name),`

Patch of `src/sentry/eventstream/kafka/backend.py` in this fix:

```diff
@@ -1,5 +1,6 @@
 import logging
 import signal
+import uuid
 from typing import Any, Literal, Mapping, MutableMapping, Optional, Sequence, Tuple, Union
 
 from arroyo import Topic
@@ -244,16 +245,26 @@ def _build_streaming_consumer(
 
         cluster_name = settings.KAFKA_TOPICS[topic]["cluster"]
 
-        configuration = build_kafka_consumer_configuration(
-            get_kafka_consumer_cluster_options(cluster_name),
-            group_id=consumer_group,
-            auto_offset_reset=initial_offset_reset,
-            strict_offset_reset=strict_offset_reset,
+        consumer = KafkaConsumer(
+            build_kafka_consumer_configuration(
+                get_kafka_consumer_cluster_options(cluster_name),
+                group_id=consumer_group,
+                auto_offset_reset=initial_offset_reset,
+                strict_offset_reset=strict_offset_reset,
+            )
+        )
+
+        commit_log_consumer = KafkaConsumer(
+            build_kafka_consumer_configuration(
+                get_kafka_consumer_cluster_options(cluster_name),
+                group_id=f"ppf-commit-log-{uuid.uuid1().hex}",
+                auto_offset_reset="earliest",
+            )
         )
 
         synchronized_consumer = ArroyoSynchronizedConsumer(
-            consumer=KafkaConsumer(configuration),
-            commit_log_consumer=KafkaConsumer(configuration),
+            consumer=consumer,
+            commit_log_consumer=commit_log_consumer,
             commit_log_topic=Topic(commit_log_topic),
             commit_log_groups={synchronize_commit_group},
         )
@@ -297,7 +308,7 @@ def run_consumer(
                 commit_batch_timeout_ms,
                 concurrency,
                 initial_offset_reset,
-                bool(strict_offset_reset),
+                strict_offset_reset,
             )
         else:
             consumer = self._build_consumer(
```

# case136: getsentry/sentry fbdfb1d59a3a

Sampled file (the only file the models saw): `src/sentry/replays/consumers/recording/process_recording.py` · committed 2022-10-21 04:29:41-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
feat(Replays): Check for recording-segment uniqueness prior to processing (#39559)

closes https://github.com/getsentry/replay-backend/issues/144

Co-authored-by: Josh Ferge <josh.ferge@sentry.io>
```

## Diff of the sampled file

```diff
@@ -96,8 +96,6 @@ class ProcessRecordingSegmentStrategy(ProcessingStrategy[KafkaPayload]):
         with sentry_sdk.start_transaction(
             op="replays.consumer", name="replays.consumer.flush_batch"
         ):
-            sentry_sdk.set_extra("replay_id", message_dict["replay_id"])
-
             try:
                 recording_segment_parts = list(parts)
             except ValueError:
@@ -117,6 +115,22 @@ class ProcessRecordingSegmentStrategy(ProcessingStrategy[KafkaPayload]):
             # blindly merge the bytes objects into a single bytes object.
             recording_segment = b"".join(recording_segment_parts)
 
+            count_existing_segments = ReplayRecordingSegment.objects.filter(
+                replay_id=message_dict["replay_id"],
+                project_id=message_dict["project_id"],
+                segment_id=headers["segment_id"],
+            ).count()
+
+            if count_existing_segments > 0:
+                with sentry_sdk.push_scope() as scope:
+                    scope.level = "warning"
+                    scope.add_attachment(bytes=recording_segment, filename="dup_replay_segment")
+                    sentry_sdk.capture_message("Recording segment was already processed.")
+
+                parts.drop()
+
+                return
+
             # create a File for our recording segment.
             recording_segment_file_name = f"rr:{message_dict['replay_id']}:{headers['segment_id']}"
             file = File.objects.create(
@@ -128,6 +142,7 @@ class ProcessRecordingSegmentStrategy(ProcessingStrategy[KafkaPayload]):
                 blob_size=settings.SENTRY_ATTACHMENT_BLOB_SIZE,
             )
             # associate this file with an indexable replay_id via ReplayRecordingSegment
+
             ReplayRecordingSegment.objects.create(
                 replay_id=message_dict["replay_id"],
                 project_id=message_dict["project_id"],
```

## Other files changed by this commit (0)

(none)

## Fix commits that the dataset links to this commit (1)

### Fix 1: e4b34ce84ab4 (2022-10-24) · pull request #40456: fix(replays): change sentry sdk calling to be more helpful

Pull-request labels: Scope: Backend

Commit message:

```
fix(replays): change sentry sdk calling to be more helpful (#40456)

- remove configure_scope call from `submit` function, as because of our
threading this gets weird and wasn't working correctly
- add replayid/projectid tagging to the dupe segments block
- change `capture_message` to `capture_exception` so hopefully we get
more breadcrumbs
```

Pull-request description:

```
- remove configure_scope call from `submit` function, as because of our threading this gets weird and wasn't working correctly
- add replayid/projectid tagging to the dupe segments block
- change `capture_message` to `capture_exception` so hopefully we get more breadcrumbs
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: `sentry_sdk.capture_message("Recording segment was already processed.")`
- in other files of the commit: none

Patch of the sampled file in this fix:

```diff
@@ -8,7 +8,7 @@
 from concurrent.futures import Future
 from datetime import datetime, timezone
 from io import BytesIO
-from typing import Any, Callable, Deque, Mapping, MutableMapping, NamedTuple, Optional, cast
+from typing import Callable, Deque, Mapping, MutableMapping, NamedTuple, Optional, cast
 
 import msgpack
 import sentry_sdk
@@ -31,7 +31,6 @@
 from sentry.signals import first_replay_received
 from sentry.utils import json, metrics
 from sentry.utils.outcomes import Outcome, track_outcome
-from sentry.utils.sdk import configure_scope
 
 logger = logging.getLogger("sentry.replays")
 
@@ -127,7 +126,10 @@ def _store(
                 with sentry_sdk.push_scope() as scope:
                     scope.level = "warning"
                     scope.add_attachment(bytes=recording_segment, filename="dup_replay_segment")
-                    sentry_sdk.capture_message("Recording segment was already processed.")
+                    scope.set_tag("replay_id", message_dict["replay_id"])
+                    scope.set_tag("project_id", message_dict["project_id"])
+
+                    sentry_sdk.capture_exception("Recording segment was already processed.")  # type: ignore[arg-type]
 
                 parts.drop()
 
@@ -215,7 +217,6 @@ def submit(self, message: Message[KafkaPayload]) -> None:
                 < getattr(settings, "SENTRY_REPLAY_RECORDINGS_CONSUMER_APM_SAMPLING", 0),
             ):
                 message_dict = msgpack.unpackb(message.payload.value)
-                self._configure_sentry_scope(message_dict)
 
                 if message_dict["type"] == "replay_recording_chunk":
                     sentry_sdk.set_extra("replay_id", message_dict["replay_id"])
@@ -295,12 +296,6 @@ def __throttled_commit(self, force: bool = False) -> None:
                 self.__last_committed = now
                 self.__commit_data = {}
 
-    def _configure_sentry_scope(self, message_dict: dict[str, Any]) -> None:
-        with configure_scope() as scope:
-            scope.set_tag("replay_id", message_dict["replay_id"])
-            scope.set_tag("project_id", message_dict["project_id"])
-            # TODO: add replay sdk version once added
-
 
 def replay_recording_segment_cache_id(project_id: int, replay_id: str, segment_id: str) -> str:
     return f"{project_id}:{replay_id}:{segment_id}"
```

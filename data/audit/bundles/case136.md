# case136: getsentry/sentry fbdfb1d59a3a

File: `src/sentry/replays/consumers/recording/process_recording.py` · committed 2022-10-21 04:29:41-01:00 · SZZ label: RISKY

## Commit message

```
feat(Replays): Check for recording-segment uniqueness prior to processing (#39559)

closes https://github.com/getsentry/replay-backend/issues/144

Co-authored-by: Josh Ferge <josh.ferge@sentry.io>
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
  118              count_existing_segments = ReplayRecordingSegment.objects.filter(
  119                  replay_id=message_dict["replay_id"],
  120                  project_id=message_dict["project_id"],
  121                  segment_id=headers["segment_id"],
  122              ).count()
  123  
  124              if count_existing_segments > 0:
  125                  with sentry_sdk.push_scope() as scope:
  126                      scope.level = "warning"
  127                      scope.add_attachment(bytes=recording_segment, filename="dup_replay_segment")
  128                      sentry_sdk.capture_message("Recording segment was already processed.")
  129  
  130                  parts.drop()
  131  
  132                  return
  133  
  145  
```

## Candidate fixes (4 later commits to this file remove a blamed line; 19 later commits up to 2023-06-30 checked)

### Candidate 1: e4b34ce84ab4 (2022-10-24)

Message:

```
fix(replays): change sentry sdk calling to be more helpful (#40456)

- remove configure_scope call from `submit` function, as because of our
threading this gets weird and wasn't working correctly
- add replayid/projectid tagging to the dupe segments block
- change `capture_message` to `capture_exception` so hopefully we get
more breadcrumbs
```

Removed blamed lines: `sentry_sdk.capture_message("Recording segment was already processed.")`

Patch of this file:

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

### Candidate 2: 6d5b1f3fa37d (2022-10-25)

Message:

```
feat(Replays): Add try catch block for duplicate recording segment processing attempts (#39557)

closes https://github.com/getsentry/replay-backend/issues/143
```

Removed blamed lines: `project_id=message_dict["project_id"],`; `replay_id=message_dict["replay_id"],`; `segment_id=headers["segment_id"],`

Patch of this file:

```diff
@@ -17,6 +17,7 @@
 from arroyo.processing.strategies.abstract import ProcessingStrategy
 from arroyo.types import Message, Position
 from django.conf import settings
+from django.db.utils import IntegrityError
 
 from sentry.constants import DataCategory
 from sentry.models import File
@@ -145,14 +146,29 @@ def _store(
                 BytesIO(recording_segment),
                 blob_size=settings.SENTRY_ATTACHMENT_BLOB_SIZE,
             )
-            # associate this file with an indexable replay_id via ReplayRecordingSegment
 
-            ReplayRecordingSegment.objects.create(
-                replay_id=message_dict["replay_id"],
-                project_id=message_dict["project_id"],
-                segment_id=headers["segment_id"],
-                file_id=file.id,
-            )
+            try:
+                # associate this file with an indexable replay_id via ReplayRecordingSegment
+                ReplayRecordingSegment.objects.create(
+                    replay_id=message_dict["replay_id"],
+                    project_id=message_dict["project_id"],
+                    segment_id=headers["segment_id"],
+                    file_id=file.id,
+                )
+            except IntegrityError:
+                # Same message was encountered more than once.
+                logger.warning(
+                    "Recording-segment has already been processed.",
+                    extra={
+                        "replay_id": message_dict["replay_id"],
+                        "project_id": message_dict["project_id"],
+                        "segment_id": headers["segment_id"],
+                    },
+                )
+
+                # Cleanup the blob.
+                file.delete()
+
             # delete the recording segment from cache after we've stored it
             parts.drop()
```

### Candidate 3: aa5f1595243d (2022-11-16)

Message:

```
metrics(replays): add more timing metrics to recording consumer (#41462)

- adds a bunch of metrics for us to help tune the performance of our
recording consumer
```

Removed blamed lines: `).count()`; `count_existing_segments = ReplayRecordingSegment.objects.filter(`; `parts.drop()`; `project_id=message_dict["project_id"],`; `replay_id=message_dict["replay_id"],`; `segment_id=headers["segment_id"],`

Patch of this file:

```diff
@@ -79,6 +79,7 @@ def _process_chunk(
         part = RecordingSegmentCache(cache_prefix)
         part[message_dict["chunk_index"]] = message_dict["payload"]
 
+    @metrics.wraps("replays.process_recording.store_recording.process_headers")
     def _process_headers(
         self, recording_segment_with_headers: bytes
     ) -> tuple[RecordingSegmentHeaders, bytes]:
@@ -98,11 +99,12 @@ def _store(
         with sentry_sdk.start_transaction(
             op="replays.consumer", name="replays.consumer.flush_batch"
         ):
-            try:
-                recording_segment_parts = list(parts)
-            except ValueError:
-                logger.exception("Missing recording-segment.")
-                return None
+            with metrics.timer("replays.process_recording.store_recording.read_segments"):
+                try:
+                    recording_segment_parts = list(parts)
+                except ValueError:
+                    logger.exception("Missing recording-segment.")
+                    return None
 
             try:
                 headers, parsed_first_part = self._process_headers(recording_segment_parts[0])
@@ -117,11 +119,12 @@ def _store(
             # blindly merge the bytes objects into a single bytes object.
             recording_segment = b"".join(recording_segment_parts)
 
-            count_existing_segments = ReplayRecordingSegment.objects.filter(
-                replay_id=message_dict["replay_id"],
-                project_id=message_dict["project_id"],
-                segment_id=headers["segment_id"],
-            ).count()
+            with metrics.timer("replays.process_recording.store_recording.count_segments"):
+                count_existing_segments = ReplayRecordingSegment.objects.filter(
+                    replay_id=message_dict["replay_id"],
+                    project_id=message_dict["project_id"],
+                    segment_id=headers["segment_id"],
+                ).count()
 
             if count_existing_segments > 0:
                 with sentry_sdk.push_scope() as scope:
@@ -138,24 +141,27 @@ def _store(
 
             # create a File for our recording segment.
             recording_segment_file_name = f"rr:{message_dict['replay_id']}:{headers['segment_id']}"
-            file = File.objects.create(
-                name=recording_segment_file_name,
-                type="replay.recording",
-            )
-            file.putfile(
-                BytesIO(recording_segment),
-                blob_size=settings.SENTRY_ATTACHMENT_BLOB_SIZE,
-            )
+            with metrics.timer("replays.store_recording.store_recording.create_file"):
+                file = File.objects.create(
+                    name=recording_segment_file_name,
+                    type="replay.recording",
+                )
+            with metrics.timer("replays.store_recording.store_recording.put_segment_file"):
+                file.putfile(
+                    BytesIO(recording_segment),
+                    blob_size=settings.SENTRY_ATTACHMENT_BLOB_SIZE,
+                )
 
             try:
                 # associate this file with an indexable replay_id via ReplayRecordingSegment
-                ReplayRecordingSegment.objects.create(
-                    replay_id=message_dict["replay_id"],
-                    project_id=message_dict["project_id"],
-                    segment_id=headers["segment_id"],
-                    file_id=file.id,
-                    size=len(recording_segment),
-                )
+                with metrics.timer("replays.store_recording.store_recording.create_segment_row"):
+                    ReplayRecordingSegment.objects.create(
+                        replay_id=message_dict["replay_id"],
+                        project_id=message_dict["project_id"],
+                        segment_id=headers["segment_id"],
+                        file_id=file.id,
+                        size=len(recording_segment),
+                    )
             except IntegrityError:
                 # Same message was encountered more than once.
                 logger.warning(
@@ -171,7 +177,8 @@ def _store(
                 file.delete()
 
             # delete the recording segment from cache after we've stored it
-            parts.drop()
+            with metrics.timer("replays.process_recording.store_recording.drop_segments"):
+                parts.drop()
 
             # TODO: how to handle failures in the above calls. what should happen?
             # also: handling same message twice?
```

### Candidate 4: 79ac2462114c (2022-11-18)

Message:

```
feat(replays): Split out recording ingest behavior from recording consumer implementation (#41518)

closes: https://github.com/getsentry/replay-backend/issues/209

No behavioral changes.  Just moving code from one place to another.
```

Removed blamed lines: `).count()`; `count_existing_segments = ReplayRecordingSegment.objects.filter(`; `if count_existing_segments > 0:`; `parts.drop()`; `project_id=message_dict["project_id"],`; `replay_id=message_dict["replay_id"],`; `return`; `scope.add_attachment(bytes=recording_segment, filename="dup_replay_segment")`; `scope.level = "warning"`; `segment_id=headers["segment_id"],`; `with sentry_sdk.push_scope() as scope:`

Patch of this file:

```diff
@@ -6,8 +6,6 @@
 import time
 from collections import deque
 from concurrent.futures import Future
-from datetime import datetime, timezone
-from io import BytesIO
 from typing import Callable, Deque, Mapping, MutableMapping, NamedTuple, Optional, cast
 
 import msgpack
@@ -17,22 +15,16 @@
 from arroyo.processing.strategies.abstract import ProcessingStrategy
 from arroyo.types import Message, Position
 from django.conf import settings
-from django.db.utils import IntegrityError
 from sentry_sdk.tracing import Transaction
 
-from sentry.constants import DataCategory
-from sentry.models import File
-from sentry.models.project import Project
-from sentry.replays.cache import RecordingSegmentCache, RecordingSegmentParts
-from sentry.replays.consumers.recording.types import (
+from sentry.replays.cache import RecordingSegmentParts
+from sentry.replays.usecases.ingest import (
     RecordingSegmentChunkMessage,
-    RecordingSegmentHeaders,
     RecordingSegmentMessage,
+    ingest_chunk,
+    ingest_chunked_recording,
 )
-from sentry.replays.models import ReplayRecordingSegment
-from sentry.signals import first_replay_received
-from sentry.utils import json, metrics
-from sentry.utils.outcomes import Outcome, track_outcome
+from sentry.utils import metrics
 
 logger = logging.getLogger("sentry.replays")
 
@@ -67,159 +59,20 @@ def __init__(
         self.__commit_data: MutableMapping[Partition, Position] = {}
         self.__last_committed: float = 0
 
-    @metrics.wraps("replays.process_recording.process_chunk")
-    def _process_chunk(
-        self,
-        message_dict: RecordingSegmentChunkMessage,
-        message: Message[KafkaPayload],
-        current_transaction: Transaction,
-    ) -> None:
-        cache_prefix = replay_recording_segment_cache_id(
-            project_id=message_dict["project_id"],
-            replay_id=message_dict["replay_id"],
-            segment_id=message_dict["id"],
-        )
-
-        part = RecordingSegmentCache(cache_prefix)
-        with current_transaction.start_child(op="replays.process_recording.store_chunk"):
-            part[message_dict["chunk_index"]] = message_dict["payload"]
-        current_transaction.finish()
-
-    @metrics.wraps("replays.process_recording.store_recording.process_headers")
-    def _process_headers(
-        self, recording_segment_with_headers: bytes
-    ) -> tuple[RecordingSegmentHeaders, bytes]:
-        # split the recording payload by a newline into the headers and the recording
-        try:
-            recording_headers, recording_segment = recording_segment_with_headers.split(b"\n", 1)
-        except ValueError:
-            raise MissingRecordingSegmentHeaders
-        return json.loads(recording_headers), recording_segment
-
-    @metrics.wraps("replays.process_recording.store_recording")
     def _store(
         self,
         message_dict: RecordingSegmentMessage,
         parts: RecordingSegmentParts,
         current_transaction: Transaction,
     ) -> None:
-        with current_transaction.start_child(
-            op="replays.process_recording.store_recording", description="store_recording"
-        ):
-            with metrics.timer("replays.process_recording.store_recording.read_segments"):
-                try:
-                    recording_segment_parts = list(parts)
-                except ValueError:
-                    logger.exception("Missing recording-segment.")
-                    return None
-
-            try:
-                headers, parsed_first_part = self._process_headers(recording_segment_parts[0])
-            except MissingRecordingSegmentHeaders:
-                logger.warning(f"missing header on {message_dict['replay_id']}")
-                return
-
-            # Replace the first part with itself but the headers removed.
-            recording_segment_parts[0] = parsed_first_part
-
-            # The parts were gzipped by the SDK and disassembled by Relay. In this step we can
-            # blindly merge the bytes objects into a single bytes object.
-            recording_segment = b"".join(recording_segment_parts)
-
-            with metrics.timer("replays.process_recording.store_recording.count_segments"):
-                count_existing_segments = ReplayRecordingSegment.objects.filter(
-                    replay_id=message_dict["replay_id"],
-                    project_id=message_dict["project_id"],
-                    segment_id=headers["segment_id"],
-                ).count()
-
-            if count_existing_segments > 0:
-                with sentry_sdk.push_scope() as scope:
-                    scope.level = "warning"
-                    scope.add_attachment(bytes=recording_segment, filename="dup_replay_segment")
-                    scope.set_tag("replay_id", message_dict["replay_id"])
-                    scope.set_tag("project_id", message_dict["project_id"])
-
-                    logging.exception("Recording segment was already processed.")
-
-                parts.drop()
-
-                return
-
-            # create a File for our recording segment.
-            recording_segment_file_name = f"rr:{message_dict['replay_id']}:{headers['segment_id']}"
-            with metrics.timer("replays.store_recording.store_recording.create_file"):
-                file = File.objects.create(
-                    name=recording_segment_file_name,
-                    type="replay.recording",
-                )
-            with metrics.timer("replays.store_recording.store_recording.put_segment_file"):
-                file.putfile(
-                    BytesIO(recording_segment),
-                    blob_size=settings.SENTRY_ATTACHMENT_BLOB_SIZE,
-                )
-
-            try:
-                # associate this file with an indexable replay_id via ReplayRecordingSegment
-                with metrics.timer("replays.store_recording.store_recording.create_segment_row"):
-                    ReplayRecordingSegment.objects.create(
-                        r
```

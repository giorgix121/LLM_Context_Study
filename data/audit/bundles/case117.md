# case117: getsentry/sentry c1c0a777a4f9

File: `src/sentry/region_to_control/producer.py` · committed 2022-10-20 09:00:50-01:00 · SZZ label: RISKY

## Commit message

```
chore(hybrid-cloud): Adding service layer, starting with project key (#40294)

First cut at a hybrid cloud service abstraction. No backing
implementation for now, but includes a test to be replaced with
`RegionClient` call. Extracted from
https://github.com/getsentry/sentry/pull/40214
```

## Diff of the target file

```diff
@@ -68,7 +68,8 @@ def get_region_to_control_producer() -> KafkaProducer:
 
         @atexit.register
         def exit_handler():
-            _publisher.close()
+            if _publisher is not None:
+                _publisher.close()
 
     return _publisher
 
@@ -86,11 +87,5 @@ def clear_region_to_control_producer():
 
 
 def _should_produce_to_kafka():
-    from sentry import options
-
     mode = SiloMode.get_current_mode()
-    is_region = mode == SiloMode.REGION
-    is_mono_with_producer = mode == SiloMode.MONOLITH and options.get(
-        "hc.region-to-control.monolith-publish"
-    )
-    return is_region or is_mono_with_producer
+    return mode == SiloMode.REGION
```

## Lines SZZ blamed (line numbers in the new version)

```
   71              if _publisher is not None:
   72                  _publisher.close()
   91      return mode == SiloMode.REGION
```

## Candidate fixes (1 later commits to this file remove a blamed line; 2 later commits up to 2023-06-30 checked)

### Candidate 1: fe07466a1449 (2022-10-21)

Message:

```
chore(hybrid-cloud): Extract region to control silo into service abstraction (#40353)

1. Use the `silo_mode_delegator` to make the silo conditional sensitive
logic of region to control processing like other services that need to
be conditional based on deployment.
2. Leverage the lifecycle management offered by the
`DelegatedBySiloMode` to stop arroyo kafka producer between tests or
after test failures (rather than requiring explicit test fixture clean
up, it's now 'implicit' to the lifecycle of the mocks introduced at the
top level).
3. Add default mocks for the region to control kafka producer so that
most tests do not require kafka running (also improves performance
significantly). There is still the integration test that uses the real
producer.
4. *Attempt* to fix ModuleDeadlock error with more granular importing. I
could not reproduce this issue locally, unfortunately, so this is a best
effort attempt to reduce any circular import possibilities.

Co-authored-by: getsantry[bot] <66042841+getsantry[bot]@users.noreply.github.com>
```

Removed blamed lines: `_publisher.close()`; `if _publisher is not None:`; `return mode == SiloMode.REGION`

Patch of this file:

```diff
@@ -1,91 +1,178 @@
+from __future__ import annotations
+
 import atexit
 import dataclasses
-from typing import Any, Optional
+from abc import abstractmethod
+from typing import TYPE_CHECKING, Any, Optional
 
 from arroyo import Topic
 from arroyo.backends.kafka import KafkaPayload, KafkaProducer
 from django.conf import settings
 
-from sentry.models import AuditLogEntry, UserIP
 from sentry.region_to_control.messages import RegionToControlMessage, UserIpEvent
+from sentry.services.hybrid_cloud import InterfaceWithLifecycle, silo_mode_delegation
 from sentry.silo import SiloMode
 from sentry.utils import json, kafka_config
 
+if TYPE_CHECKING:
+    from sentry.models import AuditLogEntry
 
-def produce_user_ip(event: UserIpEvent):
-    if _should_produce_to_kafka():
-        write_region_to_control_message(
-            dataclasses.asdict(RegionToControlMessage(user_ip_event=event)), sync=False
-        )
-    else:
-        UserIP.objects.create_or_update(
-            user_id=event.user_id, ip_address=event.ip_address, values=dataclasses.asdict(event)
+
+class RegionToControlMessagingService(InterfaceWithLifecycle):
+    @abstractmethod
+    def write_region_to_control_message(self, payload: Any, sync: bool):
+        pass
+
+
+_empty_headers = list()
+
+
+class KafkaBackedRegionToControlMessageService(RegionToControlMessagingService):
+    _publisher: Optional[KafkaProducer]
+
+    def __init__(self):
+        self._publisher = None
+
+    def close(self):
+        if self._publisher is not None:
+            self._publisher.close()
+
+    def write_region_to_control_message(self, payload: Any, sync: bool):
+        future = self.get_region_to_control_producer().produce(
+            Topic(settings.KAFKA_REGION_TO_CONTROL),
+            KafkaPayload(
+                key=None,
+                value=json.dumps(payload).encode("utf8"),
+                headers=_empty_headers,
+            ),
         )
 
+        if not sync:
+            return
+
+        future.result(1.0)
+
+    def get_region_to_control_producer(self) -> KafkaProducer:
+        """
+        Creates, if necessary, an arroyo.KafkaProducer client configured for region to control communication and returns
+        it, caching it for future calls.  Installs an exit handler to close the worker thread processes.
+        """
+        if self._publisher is None:
+            config = settings.KAFKA_TOPICS.get(settings.KAFKA_REGION_TO_CONTROL)
+            self._publisher = KafkaProducer(
+                kafka_config.get_kafka_producer_cluster_options(config["cluster"])
+            )
+
+            @atexit.register
+            def exit_handler():
+                self.close()
+
+        return self._publisher
+
+
+# Test default mock.
+class MockRegionToControlMessageService(RegionToControlMessagingService):
+    def __init__(self):
+        from unittest.mock import Mock
+
+        self.mock = Mock(spec_set=self)
+
+    def write_region_to_control_message(self, payload: Any, sync: bool):
+        self.mock.write_region_to_control_message(payload, sync)
 
-def produce_audit_log_entry(entry: AuditLogEntry):
-    if _should_produce_to_kafka():
-        write_region_to_control_message(
+    def close(self):
+        self.mock.reset_mock()
+
+
+# This service should only really exist in the region mode for now, but the delegator object is used for its
+# convenience methods.
+region_to_control_message_service: RegionToControlMessagingService = silo_mode_delegation(
+    {SiloMode.REGION: KafkaBackedRegionToControlMessageService}
+)
+
+
+class AuditLogEntryService(InterfaceWithLifecycle):
+    @abstractmethod
+    def produce_audit_log_entry(self, entry: AuditLogEntry):
+        pass
+
+
+class RegionToControlAuditLogEntryService(AuditLogEntryService):
+    region_to_control_messaging_service: RegionToControlMessagingService
+
+    def __init__(
+        self,
+        region_to_control_messaging_service: RegionToControlMessagingService = region_to_control_message_service,
+    ):
+        self.region_to_control_messaging_service = region_to_control_messaging_service
+
+    def produce_audit_log_entry(self, entry: AuditLogEntry):
+        self.region_to_control_messaging_service.write_region_to_control_message(
             dataclasses.asdict(RegionToControlMessage(audit_log_event=entry.as_kafka_event())),
             sync=True,
         )
-    else:
+
+    def close(self):
+        pass
+
+
+class DatabaseBackedAuditLogEntryService(AuditLogEntryService):
+    def produce_audit_log_entry(self, entry: AuditLogEntry):
         entry.save()
 
+    def close(self):
+        pass
 
-_publisher: Optional[KafkaProducer] = None
-_empty_headers = list()
 
+audit_log_entry_service: AuditLogEntryService = silo_mode_delegation(
+    {
+        SiloMode.MONOLITH: DatabaseBackedAuditLogEntryService,
+        SiloMode.CONTROL: DatabaseBackedAuditLogEntryService,
+        SiloMode.REGION: RegionToControlAuditLogEntryService,
+    }
+)
+
+
+class UserIpService(InterfaceWithLifecycle):
+    @abstractmethod
+    def produce_user_ip(self, event: UserIpEvent):
+        pass
+
+
+class RegionToControlUserIpService(UserIpService):
+    def close(self):
+        pass
+
+    region_to_control_messaging_service: RegionToControlMessagingService
 
-# TODO: Would be nice to configure the timeout via a dynamic setting.
-def write_region_to_control_message(payload: Any, sync=True, timeout=1):
-    future = get_region_to_control_producer().produce(
-        Topic(settings.KAFKA_REGION_TO_CONTROL),
-        KafkaPayload(
-            key=None,
-            value=json.dumps(payload).encode("utf8"),
-            headers=_empty_headers,
-        ),
-    )
-
-    if not sync:
-        return
-
-    future.result(timeout)
-
-
-def get_region_to_control_producer() -> KafkaProducer:
-    """
-    Creates, if necessary, an arroyo.KafkaProducer client configured for region to control communication and returns
-    it, caching it for future calls.  Installs an exit
```

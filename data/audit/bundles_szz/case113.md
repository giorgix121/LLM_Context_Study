# case113: home-assistant/core 2c43606922b3

Sampled file (the only file the models saw): `homeassistant/components/trace/websocket_api.py` · committed 2022-10-20 14:41:14-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Add websocket type hints in components (#80654)

* Add websocket type hints in components

* Adjust

* Apply suggestion

Co-authored-by: Marc Mueller <30130371+cdce8p@users.noreply.github.com>

Co-authored-by: Marc Mueller <30130371+cdce8p@users.noreply.github.com>
```

## Diff of the sampled file

```diff
@@ -135,7 +135,11 @@ async def websocket_trace_contexts(
         vol.Optional("run_id"): str,
     }
 )
-def websocket_breakpoint_set(hass, connection, msg):
+def websocket_breakpoint_set(
+    hass: HomeAssistant,
+    connection: websocket_api.ActiveConnection,
+    msg: dict[str, Any],
+) -> None:
     """Set breakpoint."""
     key = f"{msg['domain']}.{msg['item_id']}"
     node = msg["node"]
@@ -162,7 +166,11 @@ def websocket_breakpoint_set(hass, connection, msg):
         vol.Optional("run_id"): str,
     }
 )
-def websocket_breakpoint_clear(hass, connection, msg):
+def websocket_breakpoint_clear(
+    hass: HomeAssistant,
+    connection: websocket_api.ActiveConnection,
+    msg: dict[str, Any],
+) -> None:
     """Clear breakpoint."""
     key = f"{msg['domain']}.{msg['item_id']}"
     node = msg["node"]
@@ -176,7 +184,11 @@ def websocket_breakpoint_clear(hass, connection, msg):
 @callback
 @websocket_api.require_admin
 @websocket_api.websocket_command({vol.Required("type"): "trace/debug/breakpoint/list"})
-def websocket_breakpoint_list(hass, connection, msg):
+def websocket_breakpoint_list(
+    hass: HomeAssistant,
+    connection: websocket_api.ActiveConnection,
+    msg: dict[str, Any],
+) -> None:
     """List breakpoints."""
     breakpoints = breakpoint_list(hass)
     for _breakpoint in breakpoints:
@@ -191,7 +203,11 @@ def websocket_breakpoint_list(hass, connection, msg):
 @websocket_api.websocket_command(
     {vol.Required("type"): "trace/debug/breakpoint/subscribe"}
 )
-def websocket_subscribe_breakpoint_events(hass, connection, msg):
+def websocket_subscribe_breakpoint_events(
+    hass: HomeAssistant,
+    connection: websocket_api.ActiveConnection,
+    msg: dict[str, Any],
+) -> None:
     """Subscribe to breakpoint events."""
 
     @callback
@@ -240,7 +256,11 @@ def websocket_subscribe_breakpoint_events(hass, connection, msg):
         vol.Required("run_id"): str,
     }
 )
-def websocket_debug_continue(hass, connection, msg):
+def websocket_debug_continue(
+    hass: HomeAssistant,
+    connection: websocket_api.ActiveConnection,
+    msg: dict[str, Any],
+) -> None:
     """Resume execution of halted script or automation."""
     key = f"{msg['domain']}.{msg['item_id']}"
     run_id = msg["run_id"]
@@ -260,7 +280,11 @@ def websocket_debug_continue(hass, connection, msg):
         vol.Required("run_id"): str,
     }
 )
-def websocket_debug_step(hass, connection, msg):
+def websocket_debug_step(
+    hass: HomeAssistant,
+    connection: websocket_api.ActiveConnection,
+    msg: dict[str, Any],
+) -> None:
     """Single step a halted script or automation."""
     key = f"{msg['domain']}.{msg['item_id']}"
     run_id = msg["run_id"]
@@ -280,7 +304,11 @@ def websocket_debug_step(hass, connection, msg):
         vol.Required("run_id"): str,
     }
 )
-def websocket_debug_stop(hass, connection, msg):
+def websocket_debug_stop(
+    hass: HomeAssistant,
+    connection: websocket_api.ActiveConnection,
+    msg: dict[str, Any],
+) -> None:
     """Stop a halted script or automation."""
     key = f"{msg['domain']}.{msg['item_id']}"
     run_id = msg["run_id"]
```

## Other files changed by this commit (15)

- `homeassistant/components/cloud/http_api.py` (+5 −1)
- `homeassistant/components/config/area_registry.py` (+23 −5)
- `homeassistant/components/config/config_entries.py` (+5 −1)
- `homeassistant/components/energy/websocket_api.py` (+1 −1)
- `homeassistant/components/frontend/__init__.py` (+2 −2)
- `homeassistant/components/mobile_app/websocket_api.py` (+5 −1)
- `homeassistant/components/mqtt/__init__.py` (+5 −1)
- `homeassistant/components/person/__init__.py` (+5 −2)
- `homeassistant/components/recorder/websocket_api.py` (+5 −5)
- `homeassistant/components/repairs/websocket_api.py` (+2 −2)
- `homeassistant/components/rtsp_to_webrtc/__init__.py` (+2 −1)
- `homeassistant/components/search/__init__.py` (+6 −1)
- `homeassistant/components/shopping_list/__init__.py` (+7 −7)
- `homeassistant/components/system_log/__init__.py` (+3 −2)
- `homeassistant/components/webhook/__init__.py` (+5 −1)

## Fix commits that the dataset links to this commit (1)

### Fix 1: fe67703e13b4 (2022-10-21) · pull request #80645: Log invalid messages instead of raising in system_log

Pull-request labels: Hacktoberfest, core, cla-signed, integration: system_log, small-pr, has-tests, bugfix, Quality Scale: internal

Commit message:

```
Log invalid messages instead of raising in system_log (#80645)
```

Pull-request description:

```
## Proposed change
<!--
  Describe the big picture of your changes here to communicate to the
  maintainers why we should accept this pull request. If it fixes a bug
  or resolves a feature request, be sure to link to that issue in the
  additional information section.
-->
When the number of args to the logger was incorrect, we would raise instead of saving the log message
which made it difficult to figure out what went wrong. Additionally, this was easy to miss in the code since
the problem can't happen when running under pytest since it overrides the logging handlers.

fixes #80642
fixes #63600
will make it easier to track down #74584

I added a bit of typing here since I hard such a hard time tracing down this issue.

## Type of change
<!--
  What type of change does your PR introduce to Home Assistant?
  NOTE: Please, check only 1! box!
  If your PR requires multiple boxes to be checked, you'll most likely need to
  split it into multiple PRs. This makes things easier and faster to code review.
-->

- [ ] Dependency upgrade
- [x] Bugfix (non-breaking change which fixes an issue)
- [ ] New integration (thank you!)
- [ ] New feature (which adds functionality to an existing integr
[... cut ...]
```

This fix changes 2 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `homeassistant/components/system_log/__init__.py`: `from typing import Any`

Patch of `homeassistant/components/system_log/__init__.py` in this fix:

```diff
@@ -1,9 +1,11 @@
 """Support for system log."""
+from __future__ import annotations
+
 from collections import OrderedDict, deque
 import logging
 import re
 import traceback
-from typing import Any
+from typing import Any, cast
 
 import voluptuous as vol
 
@@ -56,7 +58,9 @@
 )
 
 
-def _figure_out_source(record, call_stack, paths_re):
+def _figure_out_source(
+    record: logging.LogRecord, call_stack: list[tuple[str, int]], paths_re: re.Pattern
+) -> tuple[str, int]:
 
     # If a stack trace exists, extract file names from the entire call stack.
     # The other case is when a regular "log" is made (without an attached
@@ -81,20 +85,44 @@ def _figure_out_source(record, call_stack, paths_re):
 
         # Try to match with a file within Home Assistant
         if match := paths_re.match(pathname[0]):
-            return [match.group(1), pathname[1]]
+            return (cast(str, match.group(1)), pathname[1])
     # Ok, we don't know what this is
     return (record.pathname, record.lineno)
 
 
+def _safe_get_message(record: logging.LogRecord) -> str:
+    """Get message from record and handle exceptions.
+
+    This code will be unreachable during a pytest run
+    because pytest installs a logging handler that
+    will prevent this code from being reached.
+
+    Calling record.getMessage() can raise an exception
+    if the log message does not contain sufficient arguments.
+
+    As there is no guarantees about which exceptions
+    that can be raised, we catch all exceptions and
+    return a generic message.
+
+    This must be manually tested when changing the code.
+    """
+    try:
+        return record.getMessage()
+    except Exception:  # pylint: disable=broad-except
+        return f"Bad logger message: {record.msg} ({record.args})"
+
+
 class LogEntry:
     """Store HA log entries."""
 
-    def __init__(self, record, stack, source):
+    def __init__(self, record: logging.LogRecord, source: tuple[str, int]) -> None:
         """Initialize a log entry."""
         self.first_occurred = self.timestamp = record.created
         self.name = record.name
         self.level = record.levelname
-        self.message = deque([record.getMessage()], ma
[... cut ...]
```

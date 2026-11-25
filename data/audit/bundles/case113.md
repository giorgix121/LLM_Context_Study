# case113: home-assistant/core 2c43606922b3

File: `homeassistant/components/trace/websocket_api.py` · committed 2022-10-20 14:41:14-01:00 · SZZ label: RISKY

## Commit message

```
Add websocket type hints in components (#80654)

* Add websocket type hints in components

* Adjust

* Apply suggestion

Co-authored-by: Marc Mueller <30130371+cdce8p@users.noreply.github.com>

Co-authored-by: Marc Mueller <30130371+cdce8p@users.noreply.github.com>
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
  138  def websocket_breakpoint_set(
  139      hass: HomeAssistant,
  140      connection: websocket_api.ActiveConnection,
  141      msg: dict[str, Any],
  142  ) -> None:
  169  def websocket_breakpoint_clear(
  170      hass: HomeAssistant,
  171      connection: websocket_api.ActiveConnection,
  172      msg: dict[str, Any],
  173  ) -> None:
  187  def websocket_breakpoint_list(
  188      hass: HomeAssistant,
  189      connection: websocket_api.ActiveConnection,
  190      msg: dict[str, Any],
  191  ) -> None:
  206  def websocket_subscribe_breakpoint_events(
  207      hass: HomeAssistant,
  208      connection: websocket_api.ActiveConnection,
  209      msg: dict[str, Any],
  210  ) -> None:
  259  def websocket_debug_continue(
  260      hass: HomeAssistant,
  261      connection: websocket_api.ActiveConnection,
  262      msg: dict[str, Any],
  263  ) -> None:
  283  def websocket_debug_step(
  284      hass: HomeAssistant,
  285      connection: websocket_api.ActiveConnection,
  286      msg: dict[str, Any],
  287  ) -> None:
  307  def websocket_debug_stop(
  308      hass: HomeAssistant,
  309      connection: websocket_api.ActiveConnection,
  310      msg: dict[str, Any],
  311  ) -> None:
```

## Candidate fixes (0 later commits to this file remove a blamed line; 0 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

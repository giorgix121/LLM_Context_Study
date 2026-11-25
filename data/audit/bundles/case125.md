# case125: home-assistant/core 1f410e884abc

File: `homeassistant/components/mqtt/diagnostics.py` · committed 2022-09-17 22:43:42-01:00 · SZZ label: RISKY

## Commit message

```
Make hass.data["mqtt"] an instance of a DataClass (#77972)

* Use dataclass to reference hass.data globals

* Add discovery_registry_hooks to dataclass

* Move discovery registry hooks to dataclass

* Add device triggers to dataclass

* Cleanup DEVICE_TRIGGERS const

* Add last_discovery to data_class

* Simplify typing for class `Subscription`

* Follow up on comment

* Redo suggested typing change to sasisfy mypy

* Restore typing

* Add mypy version to CI check logging

* revert changes to ci.yaml

* Add docstr for protocol

Co-authored-by: Marc Mueller <30130371+cdce8p@users.noreply.github.com>

* Mypy update after merging #78399

* Remove mypy ignore

* Correct return type

Co-authored-by: Marc Mueller <30130371+cdce8p@users.noreply.github.com>
```

## Diff of the target file

```diff
@@ -43,7 +43,7 @@ def _async_get_diagnostics(
     device: DeviceEntry | None = None,
 ) -> dict[str, Any]:
     """Return diagnostics for a config entry."""
-    mqtt_instance: MQTT = hass.data[DATA_MQTT]
+    mqtt_instance: MQTT = hass.data[DATA_MQTT].client
 
     redacted_config = async_redact_data(mqtt_instance.conf, REDACT_CONFIG)
```

## Lines SZZ blamed (line numbers in the new version)

```
   46      mqtt_instance: MQTT = hass.data[DATA_MQTT].client
```

## Candidate fixes (1 later commits to this file remove a blamed line; 1 later commits up to 2023-06-30 checked)

### Candidate 1: e58531f118a0 (2022-09-20)

Message:

```
Add MqttData helper to mqtt (#78825)

* Add MqttData helper to mqtt

* Adjust client for circular dependencies

* Move MqttData to models.py

* Move get_mqtt_data to util.py
```

Removed blamed lines: `mqtt_instance: MQTT = hass.data[DATA_MQTT].client`

Patch of this file:

```diff
@@ -16,7 +16,8 @@
 from homeassistant.helpers import device_registry as dr, entity_registry as er
 from homeassistant.helpers.device_registry import DeviceEntry
 
-from . import DATA_MQTT, MQTT, debug_info, is_connected
+from . import debug_info, is_connected
+from .util import get_mqtt_data
 
 REDACT_CONFIG = {CONF_PASSWORD, CONF_USERNAME}
 REDACT_STATE_DEVICE_TRACKER = {ATTR_LATITUDE, ATTR_LONGITUDE}
@@ -43,7 +44,8 @@ def _async_get_diagnostics(
     device: DeviceEntry | None = None,
 ) -> dict[str, Any]:
     """Return diagnostics for a config entry."""
-    mqtt_instance: MQTT = hass.data[DATA_MQTT].client
+    mqtt_instance = get_mqtt_data(hass).client
+    assert mqtt_instance is not None
 
     redacted_config = async_redact_data(mqtt_instance.conf, REDACT_CONFIG)
```

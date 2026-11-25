# case125: home-assistant/core 1f410e884abc

Sampled file (the only file the models saw): `homeassistant/components/mqtt/diagnostics.py` · committed 2022-09-17 22:43:42-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

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

## Diff of the sampled file

```diff
@@ -43,7 +43,7 @@ def _async_get_diagnostics(
     device: DeviceEntry | None = None,
 ) -> dict[str, Any]:
     """Return diagnostics for a config entry."""
-    mqtt_instance: MQTT = hass.data[DATA_MQTT]
+    mqtt_instance: MQTT = hass.data[DATA_MQTT].client
 
     redacted_config = async_redact_data(mqtt_instance.conf, REDACT_CONFIG)
```

## Other files changed by this commit (11)

- `homeassistant/components/mqtt/__init__.py` (+47 −57)
- `homeassistant/components/mqtt/client.py` (+30 −15)
- `homeassistant/components/mqtt/config_flow.py` (+18 −7)
- `homeassistant/components/mqtt/const.py` (+0 −8)
- `homeassistant/components/mqtt/device_trigger.py` (+18 −17)
- `homeassistant/components/mqtt/discovery.py` (+10 −5)
- `homeassistant/components/mqtt/mixins.py` (+42 −19)
- `tests/common.py` (+1 −1)
- `tests/components/mqtt/test_config_flow.py` (+1 −1)
- `tests/components/mqtt/test_discovery.py` (+1 −1)
- `tests/components/mqtt/test_init.py` (+5 −5)

## Fix commits that the dataset links to this commit (2)

### Fix 1: 354411feed48 (2022-09-18) · pull request #78547: Link manually added MQTT entities the the MQTT config entry

Pull-request labels: core, cla-signed, integration: mqtt, cherry-picked, small-pr, bugfix

Commit message:

```
Link manually added MQTT entities the the MQTT config entry (#78547)

Co-authored-by: Erik <erik@montnemery.com>
```

Pull-request description:

```
<!--
  You are amazing! Thanks for contributing to our project!
  Please, DO NOT DELETE ANY TEXT from this template! (unless instructed).
-->
## Proposed change
<!--
  Describe the big picture of your changes here to communicate to the
  maintainers why we should accept this pull request. If it fixes a bug
  or resolves a feature request, be sure to link to that issue in the
  additional information section.
-->
Link manually added MQTT entities the the MQTT config entry

This fixed a regression introduced by https://github.com/home-assistant/core/pull/72901

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
- [ ] New feature (which adds functionality to an existing integration)
- [ ] Deprecation (breaking change to happen in the future)
- [ ] Breaking change (fix/feature causing existing functionality to break)
- [ ] Code quality imp
[... cut ...]
```

This fix changes 20 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `homeassistant/components/mqtt/__init__.py`: `from .mixins import MqttData, async_discover_yaml_entities`
- in `homeassistant/components/mqtt/mixins.py`: `config_yaml = mqtt_data.config or {}`; `config_yaml = mqtt_data.updated_config`; `if mqtt_data.updated_config:`; `mqtt_data: MqttData = hass.data[DATA_MQTT]`

Patch of `homeassistant/components/mqtt/__init__.py` in this fix:

```diff
@@ -30,6 +30,7 @@
 )
 from homeassistant.helpers.device_registry import DeviceEntry
 from homeassistant.helpers.dispatcher import async_dispatcher_connect
+from homeassistant.helpers.entity_platform import async_get_platforms
 from homeassistant.helpers.reload import (
     async_integration_yaml_config,
     async_reload_integration_platforms,
@@ -75,7 +76,7 @@
     PLATFORMS,
     RELOADABLE_PLATFORMS,
 )
-from .mixins import MqttData, async_discover_yaml_entities
+from .mixins import MqttData
 from .models import (  # noqa: F401
     MqttCommandTemplate,
     MqttValueTemplate,
@@ -422,13 +423,25 @@ async def _reload_config(call: ServiceCall) -> None:
             await async_reload_integration_platforms(hass, DOMAIN, RELOADABLE_PLATFORMS)
 
             # Reload the modern yaml platforms
+            mqtt_platforms = async_get_platforms(hass, DOMAIN)
+            tasks = [
+                entity.async_remove()
+                for mqtt_platform in mqtt_platforms
+                for entity in mqtt_platform.entities.values()
+                if not entity._discovery_data  # type: ignore[attr-defined] # pylint: disable=protected-access
+                if mqtt_platform.config_entry
+                and mqtt_platform.domain in RELOADABLE_PLATFORMS
+            ]
+            await asyncio.gather(*tasks)
+
             config_yaml = await async_integration_yaml_config(hass, DOMAIN) or {}
             mqtt_data.updated_config = config_yaml.get(DOMAIN, {})
             await asyncio.gather(
                 *(
                     [
-                        async_discover_yaml_entities(hass, component)
+                        mqtt_data.reload_handlers[component]()
                         for component in RELOADABLE_PLATFORMS
+                        if component in mqtt_data.reload_handlers
                     ]
                 )
             )
```

Patch of `homeassistant/components/mqtt/mixins.py` in this fix:

```diff
@@ -39,7 +39,6 @@
 from homeassistant.helpers import (
     config_validation as cv,
     device_registry as dr,
-    discovery,
     entity_registry as er,
 )
 from homeassistant.helpers.device_registry import EVENT_DEVICE_REGISTRY_UPDATED
@@ -286,6 +285,9 @@ class MqttData:
     last_discovery: float = 0.0
     reload_dispatchers: list[CALLBACK_TYPE] = field(default_factory=list)
     reload_entry: bool = False
+    reload_handlers: dict[str, Callable[[], Coroutine[Any, Any, None]]] = field(
+        default_factory=dict
+    )
     reload_needed: bool = False
     subscriptions_to_restore: list[Subscription] = field(default_factory=list)
     updated_config: ConfigType = field(default_factory=dict)
@@ -305,30 +307,6 @@ async def __call__(
         """Define setup_entities type."""
 
 
-async def async_discover_yaml_entities(
-    hass: HomeAssistant, platform_domain: str
-) -> None:
-    """Discover entities for a platform."""
-    mqtt_data: MqttData = hass.data[DATA_MQTT]
-    if mqtt_data.updated_config:
-        # The platform has been reloaded
-        config_yaml = mqtt_data.updated_config
-    else:
-        config_yaml = mqtt_data.config or {}
-    if not config_yaml:
-        return
-    if platform_domain not in config_yaml:
-        return
-    await asyncio.gather(
-        *(
-            discovery.async_load_platform(hass, platform_domain, DOMAIN, config, {})
-            for config in await async_get_platform_config_from_yaml(
-                hass, platform_domain, config_yaml
-            )
-        )
-    )
-
-
 async def async_get_platform_config_from_yaml(
     hass: HomeAssistant,
     platform_domain: str,
@@ -350,7 +328,7 @@ async def async_setup_entry_helper(
     hass: HomeAssistant,
     domain: str,
     async_setup: partial[Coroutine[HomeAssistant, str, None]],
-    schema: vol.Schema,
+    discovery_schema: vol.Schema,
 ) -> None:
     """Set up entity, automation or tag creation dynamically through MQTT discovery."""
     mqtt_data: MqttData = hass.data[DATA_MQTT]
@@ -367,7 +345,7 @@ async def async_discover(discovery_payload):
             return
         discovery_data = discovery_payload.discovery_data
         try:
-
[... cut ...]
```

### Fix 2: c5a58c850186 (2022-09-27) · pull request #79103: Fix MQTT setup after changing config entry flow options

Pull-request labels: core, cla-signed, integration: mqtt, small-pr, has-tests, bugfix, smash

Commit message:

```
Fix MQTT setup after changing config entry flow options (#79103)

Fix issues with config flow options
```

Pull-request description:

```
<!--
  You are amazing! Thanks for contributing to our project!
  Please, DO NOT DELETE ANY TEXT from this template! (unless instructed).
-->
## Proposed change
<!--
  Describe the big picture of your changes here to communicate to the
  maintainers why we should accept this pull request. If it fixes a bug
  or resolves a feature request, be sure to link to that issue in the
  additional information section.
-->
Fixes the setup if the MQTT client after changing broker settings via the conig ebtry option flow.

The current code does not process the unsubscribing and reloading correct. The new code simplifies reconfiguring by reloading the config entry.

Additional this PR fixes the reload the cleanup of the entry.add_update_listener that is setup when loading the entry. This caused that after a config entry change `_async_config_entry_updated` was called multiple times. Now it cleaned up when the entry is unloaded.

Finally the entry title is now updated too if the `broker` setting is changed.

## Type of change
<!--
  What type of change does your PR introduce to Home Assistant?
  NOTE: Please, check only 1! box!
  If your PR requires multiple boxes to be checked, you'll most likel
[... cut ...]
```

This fix changes 3 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `homeassistant/components/mqtt/__init__.py`: `assert (client := mqtt_data.client) is not None`; `await _async_setup_discovery(hass, cast(ConfigType, mqtt_data.config), entry)`; `await client.async_connect()`; `await client.async_disconnect()`; `client.init_client()`; `if (conf := mqtt_data.config) is None:`

Patch of `homeassistant/components/mqtt/__init__.py` in this fix:

```diff
@@ -248,20 +248,7 @@ async def _async_config_entry_updated(hass: HomeAssistant, entry: ConfigEntry) -
 
     Causes for this is config entry options changing.
     """
-    mqtt_data = get_mqtt_data(hass)
-    assert (client := mqtt_data.client) is not None
-
-    if (conf := mqtt_data.config) is None:
-        conf = CONFIG_SCHEMA_BASE(dict(entry.data))
-
-    mqtt_data.config = _merge_extended_config(entry, conf)
-    await client.async_disconnect()
-    client.init_client()
-    await client.async_connect()
-
-    await discovery.async_stop(hass)
-    if client.conf.get(CONF_DISCOVERY):
-        await _async_setup_discovery(hass, cast(ConfigType, mqtt_data.config), entry)
+    await hass.config_entries.async_reload(entry.entry_id)
 
 
 async def async_fetch_config(hass: HomeAssistant, entry: ConfigEntry) -> dict | None:
@@ -317,7 +304,9 @@ async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
     if mqtt_data.subscriptions_to_restore:
         mqtt_data.client.subscriptions = mqtt_data.subscriptions_to_restore
         mqtt_data.subscriptions_to_restore = []
-    entry.add_update_listener(_async_config_entry_updated)
+    mqtt_data.reload_dispatchers.append(
+        entry.add_update_listener(_async_config_entry_updated)
+    )
 
     await mqtt_data.client.async_connect()
```

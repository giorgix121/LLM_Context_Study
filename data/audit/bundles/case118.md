# case118: home-assistant/core 6abf677092e2

File: `homeassistant/components/plugwise/gateway.py` · committed 2022-10-12 15:48:09-01:00 · SZZ label: RISKY

## Commit message

```
Bump plugwise to v0.25.0 and adapt relevant plugwise code (#80129)
```

## Diff of the target file

```diff
@@ -72,8 +72,8 @@ async def async_setup_entry_gw(hass: HomeAssistant, entry: ConfigEntry) -> bool:
         config_entry_id=entry.entry_id,
         identifiers={(DOMAIN, str(api.gateway_id))},
         manufacturer="Plugwise",
-        name=entry.title,
-        model=f"Smile {api.smile_name}",
+        model=api.smile_model,
+        name=api.smile_name,
         sw_version=api.smile_version[0],
     )
```

## Lines SZZ blamed (line numbers in the new version)

```
   75          model=api.smile_model,
   76          name=api.smile_name,
```

## Candidate fixes (1 later commits to this file remove a blamed line; 5 later commits up to 2023-06-30 checked)

### Candidate 1: 13458dc72218 (2022-11-25)

Message:

```
Centralize exception handling in Plugwise (#82694)
```

Removed blamed lines: `model=api.smile_model,`; `name=api.smile_name,`

Patch of this file:

```diff
@@ -3,68 +3,19 @@
 
 from typing import Any
 
-from plugwise.exceptions import (
-    ConnectionFailedError,
-    InvalidAuthentication,
-    InvalidXMLError,
-    ResponseError,
-    UnsupportedDeviceError,
-)
-from plugwise.smile import Smile
-
 from homeassistant.config_entries import ConfigEntry
-from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
 from homeassistant.core import HomeAssistant, callback
-from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
 from homeassistant.helpers import device_registry as dr, entity_registry as er
-from homeassistant.helpers.aiohttp_client import async_get_clientsession
-
-from .const import (
-    DEFAULT_PORT,
-    DEFAULT_USERNAME,
-    DOMAIN,
-    LOGGER,
-    PLATFORMS_GATEWAY,
-    Platform,
-)
+
+from .const import DOMAIN, LOGGER, PLATFORMS_GATEWAY, Platform
 from .coordinator import PlugwiseDataUpdateCoordinator
 
 
 async def async_setup_entry_gw(hass: HomeAssistant, entry: ConfigEntry) -> bool:
     """Set up Plugwise Smiles from a config entry."""
     await er.async_migrate_entries(hass, entry.entry_id, async_migrate_entity_entry)
 
-    websession = async_get_clientsession(hass, verify_ssl=False)
-    api = Smile(
-        host=entry.data[CONF_HOST],
-        username=entry.data.get(CONF_USERNAME, DEFAULT_USERNAME),
-        password=entry.data[CONF_PASSWORD],
-        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
-        timeout=30,
-        websession=websession,
-    )
-
-    try:
-        connected = await api.connect()
-    except ConnectionFailedError as err:
-        raise ConfigEntryNotReady("Failed to connect to the Plugwise Smile") from err
-    except InvalidAuthentication as err:
-        raise HomeAssistantError("Invalid username or Smile ID") from err
-    except (InvalidXMLError, ResponseError) as err:
-        raise ConfigEntryNotReady(
-            "Error while communicating to the Plugwise Smile"
-        ) from err
-    except UnsupportedDeviceError as err:
-        raise HomeAssistantError("Device with unsupported firmware") from err
-
-    if not connected:
-        raise ConfigEntryNotReady("Unable to connect to Smile")
-    api.get_all_devices()
-
-    if entry.unique_id is None and api.smile_version[0] != "1.8.0":
-        hass.config_entries.async_update_entry(entry, unique_id=api.smile_hostname)
-
-    coordinator = PlugwiseDataUpdateCoordinator(hass, api)
+    coordinator = PlugwiseDataUpdateCoordinator(hass, entry)
     await coordinator.async_config_entry_first_refresh()
     migrate_sensor_entities(hass, coordinator)
 
@@ -73,11 +24,11 @@ async def async_setup_entry_gw(hass: HomeAssistant, entry: ConfigEntry) -> bool:
     device_registry = dr.async_get(hass)
     device_registry.async_get_or_create(
         config_entry_id=entry.entry_id,
-        identifiers={(DOMAIN, str(api.gateway_id))},
+        identifiers={(DOMAIN, str(coordinator.api.gateway_id))},
         manufacturer="Plugwise",
-        model=api.smile_model,
-        name=api.smile_name,
-        sw_version=api.smile_version[0],
+        model=coordinator.api.smile_model,
+        name=coordinator.api.smile_name,
+        sw_version=coordinator.api.smile_version[0],
     )
 
     await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS_GATEWAY)
```

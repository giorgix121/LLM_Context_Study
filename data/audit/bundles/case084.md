# case084: home-assistant/core dbcb269111f6

File: `homeassistant/components/switchbot/__init__.py` · committed 2022-09-10 08:32:38-01:00 · SZZ label: RISKY

## Commit message

```
Fix switchbot not setting up when already connected at startup (#78198)
```

## Diff of the target file

```diff
@@ -84,7 +84,7 @@ async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
     address: str = entry.data[CONF_ADDRESS]
     ble_device = bluetooth.async_ble_device_from_address(
         hass, address.upper(), connectable
-    )
+    ) or await switchbot.get_device(address)
     if not ble_device:
         raise ConfigEntryNotReady(
             f"Could not find Switchbot {sensor_type} with address {address}"
```

## Lines SZZ blamed (line numbers in the new version)

```
   87      ) or await switchbot.get_device(address)
```

## Candidate fixes (1 later commits to this file remove a blamed line; 8 later commits up to 2023-06-30 checked)

### Candidate 1: 9b5c5938ceb7 (2022-12-12)

Message:

```
Remove get_device call in switchbot (#83881)
```

Removed blamed lines: `) or await switchbot.get_device(address)`

Patch of this file:

```diff
@@ -86,7 +86,7 @@ async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
     address: str = entry.data[CONF_ADDRESS]
     ble_device = bluetooth.async_ble_device_from_address(
         hass, address.upper(), connectable
-    ) or await switchbot.get_device(address)
+    )
     if not ble_device:
         raise ConfigEntryNotReady(
             f"Could not find Switchbot {sensor_type} with address {address}"
```

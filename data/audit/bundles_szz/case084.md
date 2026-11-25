# case084: home-assistant/core dbcb269111f6

Sampled file (the only file the models saw): `homeassistant/components/switchbot/__init__.py` · committed 2022-09-10 08:32:38-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Fix switchbot not setting up when already connected at startup (#78198)
```

## Diff of the sampled file

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

## Other files changed by this commit (3)

- `homeassistant/components/switchbot/manifest.json` (+1 −1)
- `requirements_all.txt` (+1 −1)
- `requirements_test_all.txt` (+1 −1)

## Fix commits that the dataset links to this commit (1)

### Fix 1: a3ec28ea797d (2022-09-10) · pull request #78202: Close stale switchbot connections at setup time

Pull-request labels: cla-signed, cherry-picked, small-pr, integration: switchbot, dependency, by-code-owner, bugfix

Commit message:

```
Close stale switchbot connections at setup time (#78202)
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
Close stale switchbot connections at setup time
https://github.com/Danielhiversen/pySwitchbot/compare/0.19.2...0.19.3

This likely fixes #77630 but its hard to be sure since its not 100% obvious whats going on there.

## Type of change
<!--
  What type of change does your PR introduce to Home Assistant?
  NOTE: Please, check only 1! box!
  If your PR requires multiple boxes to be checked, you'll most likely need to
  split it into multiple PRs. This makes things easier and faster to code review.
-->

- [x] Dependency upgrade
- [x] Bugfix (non-breaking change which fixes an issue)
- [ ] New integration (thank you!)
- [ ] New feature (which adds functionality to an existing integration)
- [ ] Deprecation (breaking change to happen in the future)
- [ ] Breaking change (fix/feature causing existing functionality to break)
- [ ] Code quality improvements to existing code or addition of tests

## Additional information
[... cut ...]
```

This fix changes 4 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix changes this file, but not lines the commit added)
- in `homeassistant/components/switchbot/manifest.json`: `"requirements": ["PySwitchbot==0.19.2"],`
- in `requirements_all.txt`: `PySwitchbot==0.19.2`
- in `requirements_test_all.txt`: `PySwitchbot==0.19.2`

Patch of the sampled file in this fix:

```diff
@@ -89,6 +89,8 @@ async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
         raise ConfigEntryNotReady(
             f"Could not find Switchbot {sensor_type} with address {address}"
         )
+
+    await switchbot.close_stale_connections(ble_device)
     cls = CLASS_BY_DEVICE.get(sensor_type, switchbot.SwitchbotDevice)
     device = cls(
         device=ble_device,
```

Patch of `homeassistant/components/switchbot/manifest.json` in this fix:

```diff
@@ -2,7 +2,7 @@
   "domain": "switchbot",
   "name": "SwitchBot",
   "documentation": "https://www.home-assistant.io/integrations/switchbot",
-  "requirements": ["PySwitchbot==0.19.2"],
+  "requirements": ["PySwitchbot==0.19.3"],
   "config_flow": true,
   "dependencies": ["bluetooth"],
   "codeowners": [
```

Patch of `requirements_all.txt` in this fix:

```diff
@@ -37,7 +37,7 @@ PyRMVtransport==0.3.3
 PySocks==1.7.1
 
 # homeassistant.components.switchbot
-PySwitchbot==0.19.2
+PySwitchbot==0.19.3
 
 # homeassistant.components.transport_nsw
 PyTransportNSW==0.1.1
```

Patch of `requirements_test_all.txt` in this fix:

```diff
@@ -33,7 +33,7 @@ PyRMVtransport==0.3.3
 PySocks==1.7.1
 
 # homeassistant.components.switchbot
-PySwitchbot==0.19.2
+PySwitchbot==0.19.3
 
 # homeassistant.components.transport_nsw
 PyTransportNSW==0.1.1
```

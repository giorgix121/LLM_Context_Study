# case115: home-assistant/core 731f6180289c

Sampled file (the only file the models saw): `homeassistant/components/yeelight/scanner.py` · committed 2022-10-15 09:00:46-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Make home assistant discoverable via UPnP/SSDP (#79820)
```

## Diff of the sampled file

```diff
@@ -76,7 +76,7 @@ class YeelightScanner:
             self._listeners.append(
                 SsdpSearchListener(
                     async_callback=self._async_process_entry,
-                    service_type=SSDP_ST,
+                    search_target=SSDP_ST,
                     target=SSDP_TARGET,
                     source=source,
                     async_connect_callback=_wrap_async_connected_idx(idx),
```

## Other files changed by this commit (19)

- `homeassistant/components/dlna_dmr/manifest.json` (+1 −1)
- `homeassistant/components/dlna_dms/manifest.json` (+1 −1)
- `homeassistant/components/samsungtv/manifest.json` (+1 −1)
- `homeassistant/components/ssdp/__init__.py` (+219 −17)
- `homeassistant/components/ssdp/manifest.json` (+1 −1)
- `homeassistant/components/upnp/manifest.json` (+1 −1)
- `homeassistant/components/yeelight/manifest.json` (+1 −1)
- `homeassistant/package_constraints.txt` (+1 −1)
- `requirements_all.txt` (+1 −1)
- `requirements_test_all.txt` (+1 −1)
- `tests/components/default_config/test_init.py` (+3 −1)
- `tests/components/dlna_dmr/conftest.py` (+8 −1)
- `tests/components/dlna_dms/conftest.py` (+8 −1)
- `tests/components/samsungtv/conftest.py` (+4 −0)
- `tests/components/sonos/conftest.py` (+4 −0)
- `tests/components/ssdp/conftest.py` (+10 −0)
- `tests/components/ssdp/test_init.py` (+16 −4)
- `tests/components/upnp/conftest.py` (+4 −0)
- `tests/components/yamaha_musiccast/test_config_flow.py` (+4 −0)

## Fix commits that the dataset links to this commit (2)

### Fix 1: 08772004b360 (2022-11-03) · pull request #81453: Fix SSDP failure to start on missing URLs

Pull-request labels: cla-signed, cherry-picked, small-pr, integration: ssdp, bugfix, Quality Scale: internal

Commit message:

```
Fix SSDP failure to start on missing URLs (#81453)
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

Small patch fix for #81434

This happens when a user uses SSL directly configured in Home Assistant, but hasn't configured their internal/external URLs in the core configuration.

In such cases, Home Assistant fails to determine the presentation URL. It won't fallback to IP-based URLs, as IP-based HTTPS URLs are basically always invalid (not valid for the certificate).

This PR skips the server start and logs a warning for now.


## Type of change
<!--
  What type of change does your PR introduce to Home Assistant?
  NOTE: Please, check only 1! box!
  If your PR requires multiple boxes to be checked, you'll most likely need to
  split it into multiple PRs. This makes things easier and faster to code review.
-->

- [ ] Dependency upgrade
- [x] Bugfix (non-breaking change wh
[... cut ...]
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `homeassistant/components/ssdp/__init__.py`: `from homeassistant.helpers.network import get_url`

Patch of `homeassistant/components/ssdp/__init__.py` in this fix:

```diff
@@ -52,7 +52,7 @@
 from homeassistant.helpers.aiohttp_client import async_get_clientsession
 from homeassistant.helpers.event import async_track_time_interval
 from homeassistant.helpers.instance_id import async_get as async_get_instance_id
-from homeassistant.helpers.network import get_url
+from homeassistant.helpers.network import NoURLAvailableError, get_url
 from homeassistant.helpers.system_info import async_get_system_info
 from homeassistant.helpers.typing import ConfigType
 from homeassistant.loader import async_get_ssdp, bind_hass
@@ -697,7 +697,16 @@ async def _async_start_upnp_servers(self) -> None:
         udn = await self._async_get_instance_udn()
         system_info = await async_get_system_info(self.hass)
         model_name = system_info["installation_type"]
-        presentation_url = get_url(self.hass, allow_ip=True, prefer_external=False)
+        try:
+            presentation_url = get_url(self.hass, allow_ip=True, prefer_external=False)
+        except NoURLAvailableError:
+            _LOGGER.warning(
+                "Could not set up UPnP/SSDP server, as a presentation URL could"
+                " not be determined; Please configure your internal URL"
+                " in the Home Assistant general configuration"
+            )
+            return
+
         serial_number = await async_get_instance_id(self.hass)
         HassUpnpServiceDevice.DEVICE_DEFINITION = (
             HassUpnpServiceDevice.DEVICE_DEFINITION._replace(
```

### Fix 2: b5f70a404a8e (2022-10-24) · pull request #80815: Fix SSDP/UPnP server after testing

Pull-request labels: Hacktoberfest, cla-signed, small-pr, integration: ssdp, dependency, bugfix, smash, Quality Scale: internal

Commit message:

```
Fix SSDP/UPnP server after testing (#80815)
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

Fixes after testing by @oyvindwe the new ssdp/upnp server. Includes a fix for the race condition reported in #80400 as well.


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
- [ ] Code quality improvements to existi
[... cut ...]
```

This fix changes 11 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `homeassistant/components/dlna_dmr/manifest.json`: `"requirements": ["async-upnp-client==0.32.0"],`
- in `homeassistant/components/dlna_dms/manifest.json`: `"requirements": ["async-upnp-client==0.32.0"],`
- in `homeassistant/components/samsungtv/manifest.json`: `"async-upnp-client==0.32.0"`
- in `homeassistant/components/ssdp/__init__.py`: `hass.create_task(scanner.async_start())`; `hass.create_task(server.async_start())`
- in `homeassistant/components/ssdp/manifest.json`: `"requirements": ["async-upnp-client==0.32.0"],`
- in `homeassistant/components/upnp/manifest.json`: `"requirements": ["async-upnp-client==0.32.0", "getmac==0.8.2"],`
- in `homeassistant/components/yeelight/manifest.json`: `"requirements": ["yeelight==0.7.10", "async-upnp-client==0.32.0"],`
- in `homeassistant/package_constraints.txt`: `async-upnp-client==0.32.0`

Patch of `homeassistant/components/dlna_dmr/manifest.json` in this fix:

```diff
@@ -3,7 +3,7 @@
   "name": "DLNA Digital Media Renderer",
   "config_flow": true,
   "documentation": "https://www.home-assistant.io/integrations/dlna_dmr",
-  "requirements": ["async-upnp-client==0.32.0"],
+  "requirements": ["async-upnp-client==0.32.1"],
   "dependencies": ["ssdp"],
   "after_dependencies": ["media_source"],
   "ssdp": [
```

Patch of `homeassistant/components/dlna_dms/manifest.json` in this fix:

```diff
@@ -3,7 +3,7 @@
   "name": "DLNA Digital Media Server",
   "config_flow": true,
   "documentation": "https://www.home-assistant.io/integrations/dlna_dms",
-  "requirements": ["async-upnp-client==0.32.0"],
+  "requirements": ["async-upnp-client==0.32.1"],
   "dependencies": ["ssdp"],
   "after_dependencies": ["media_source"],
   "ssdp": [
```

Patch of `homeassistant/components/samsungtv/manifest.json` in this fix:

```diff
@@ -7,7 +7,7 @@
     "samsungctl[websocket]==0.7.1",
     "samsungtvws[async,encrypted]==2.5.0",
     "wakeonlan==2.1.0",
-    "async-upnp-client==0.32.0"
+    "async-upnp-client==0.32.1"
   ],
   "ssdp": [
     {
```

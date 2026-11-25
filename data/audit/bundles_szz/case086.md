# case086: home-assistant/core ca5a9c945649

Sampled file (the only file the models saw): `homeassistant/components/openuv/sensor.py` · committed 2022-09-17 10:56:45-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Allow multiple instances of OpenUV via the `homeassistant.update_entity` service (#76878)

* Allow for multiple instances of the OpenUV integration

* Docstring

* Remove Repairs

* Fix tests

* Slightly faster OpenUV object lookup

* Entity update service

* Remove service descriptions

* hassfest

* Simplify strings

* Don't add UI instructions to Repairs item

* Add a throttle to entity update

* Update homeassistant/components/openuv/__init__.py

Co-authored-by: Paulus Schoutsen <paulus@home-assistant.io>

* Switch from Throttle to Debouncer(s)

* Keep dispatcher for services

* Reduce change surface area

* Duplicate method

* Add issue registry through helper

* Update deprecation version

* Use config entry selector

* Remove device/service info

* Remove commented out method

* Correct entity IDs and better verbiage

* Fix tests

* Handle missing config entry ID in service calls

* Remove unhelpful comment

* Remove unused constants

Co-authored-by: Paulus Schoutsen <paulus@home-assistant.io>
Co-authored-by: J. Nick Koston <nick@koston.org>
```

## Diff of the sampled file

```diff
@@ -131,6 +131,14 @@ async def async_setup_entry(
 class OpenUvSensor(OpenUvEntity, SensorEntity):
     """Define a binary sensor for OpenUV."""
 
+    async def async_update(self) -> None:
+        """Update the entity.
+
+        Only used by the generic entity update service.
+        """
+        await self.openuv.async_update_uv_index_data()
+        self.async_update_state()
+
     @callback
     def update_from_latest_data(self) -> None:
         """Update the state."""
```

## Other files changed by this commit (7)

- `homeassistant/components/openuv/__init__.py` (+200 −26)
- `homeassistant/components/openuv/binary_sensor.py` (+8 −0)
- `homeassistant/components/openuv/services.yaml` (+24 −0)
- `homeassistant/components/openuv/strings.json` (+10 −0)
- `homeassistant/components/openuv/translations/en.json` (+10 −0)
- `tests/components/openuv/conftest.py` (+2 −0)
- `tests/components/openuv/test_diagnostics.py` (+4 −1)

## Fix commits that the dataset links to this commit (3)

### Fix 1: 2f6e55b3bb42 (2022-10-11) · pull request #80116: Fix uncaught error in OpenUV diagnostics test

Pull-request labels: Hacktoberfest, cla-signed, small-pr, integration: openuv, has-tests, by-code-owner, bugfix

Commit message:

```
Fix uncaught error in OpenUV diagnostics test (#80116)
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
This PR fixes an uncaught error in the OpenUV diagnostics test left over from a service deprecation.

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
- [ ] Code quality improvements to existing code or addition of tests
[... cut ...]
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `tests/components/openuv/test_diagnostics.py`: `"openuv", "update_data", service_data={CONF_ENTRY_ID: "test_entry_id"}`; `from homeassistant.components.openuv import CONF_ENTRY_ID`

Patch of `tests/components/openuv/test_diagnostics.py` in this fix:

```diff
@@ -1,14 +1,19 @@
 """Test OpenUV diagnostics."""
 from homeassistant.components.diagnostics import REDACTED
-from homeassistant.components.openuv import CONF_ENTRY_ID
+from homeassistant.const import CONF_ENTITY_ID
+from homeassistant.setup import async_setup_component
 
 from tests.components.diagnostics import get_diagnostics_for_config_entry
 
 
 async def test_entry_diagnostics(hass, config_entry, hass_client, setup_openuv):
     """Test config entry diagnostics."""
+    await async_setup_component(hass, "homeassistant", {})
     await hass.services.async_call(
-        "openuv", "update_data", service_data={CONF_ENTRY_ID: "test_entry_id"}
+        "homeassistant",
+        "update_entity",
+        {CONF_ENTITY_ID: ["sensor.current_uv_index"]},
+        blocking=True,
     )
     assert await get_diagnostics_for_config_entry(hass, hass_client, config_entry) == {
         "entry": {
```

### Fix 2: 60b3d6816b0a (2022-10-21) · pull request #80705: Replace custom OpenUV data object with coordinators

Pull-request labels: Hacktoberfest, cla-signed, integration: openuv, has-tests, by-code-owner, bugfix, Quality Scale: No score

Commit message:

```
Replace custom OpenUV data object with coordinators (#80705)

* Replace custom OpenUV data object with coordinators

* Typing

* Code review
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
OpenUV currently uses a custom data management object, which (a) is duplicative of what `DataUpdateCoordinator` does and (b) doesn't properly update all entities via the `homeassistant.update_entity` service (as it should). This PR replaces the custom object with coordinators.

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
- [ ] Deprecation (breaking c
[... cut ...]
```

This fix changes 6 files. Lines it removes that the commit above had added:

- in the sampled file: `Only used by the generic entity update service.`; `async def async_update(self) -> None:`; `await self.openuv.async_update_uv_index_data()`; `self.async_update_state()`
- in `homeassistant/components/openuv/__init__.py`: `)`; `) from err`; `@callback`; `@extract_openuv`; `DEFAULT_DEBOUNCER_COOLDOWN_SECONDS = 15 * 60`; `LOGGER,`
- in `homeassistant/components/openuv/binary_sensor.py`: `Only used by the generic entity update service.`; `async def async_update(self) -> None:`; `await self.openuv.async_update_protection_data()`; `self.async_update_state()`
- in `tests/components/openuv/test_diagnostics.py`: `)`; `await hass.services.async_call(`

Patch of the sampled file in this fix:

```diff
@@ -28,6 +28,7 @@
     TYPE_SAFE_EXPOSURE_TIME_5,
     TYPE_SAFE_EXPOSURE_TIME_6,
 )
+from .coordinator import OpenUvCoordinator
 
 ATTR_MAX_UV_TIME = "time"
 
@@ -122,31 +123,23 @@ async def async_setup_entry(
     hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
 ) -> None:
     """Set up a OpenUV sensor based on a config entry."""
-    openuv = hass.data[DOMAIN][entry.entry_id]
+    coordinators: dict[str, OpenUvCoordinator] = hass.data[DOMAIN][entry.entry_id]
+
     async_add_entities(
-        [OpenUvSensor(openuv, description) for description in SENSOR_DESCRIPTIONS]
+        [
+            OpenUvSensor(coordinators[DATA_UV], description)
+            for description in SENSOR_DESCRIPTIONS
+        ]
     )
 
 
 class OpenUvSensor(OpenUvEntity, SensorEntity):
     """Define a binary sensor for OpenUV."""
 
-    async def async_update(self) -> None:
-        """Update the entity.
-
-        Only used by the generic entity update service.
-        """
-        await self.openuv.async_update_uv_index_data()
-        self.async_update_state()
-
     @callback
-    def update_from_latest_data(self) -> None:
+    def _update_from_latest_data(self) -> None:
         """Update the state."""
-        if (data := self.openuv.data[DATA_UV]) is None:
-            self._attr_available = False
-            return
-
-        self._attr_available = True
+        data = self.coordinator.data
 
         if self.entity_description.key == TYPE_CURRENT_OZONE_LEVEL:
             self._attr_native_value = data["ozone"]
```

Patch of `homeassistant/components/openuv/__init__.py` in this fix:

```diff
@@ -2,11 +2,9 @@
 from __future__ import annotations
 
 import asyncio
-from collections.abc import Callable
 from typing import Any
 
 from pyopenuv import Client
-from pyopenuv.errors import OpenUvError
 import voluptuous as vol
 
 from homeassistant.config_entries import ConfigEntry, ConfigEntryState
@@ -20,20 +18,16 @@
     Platform,
 )
 from homeassistant.core import HomeAssistant, ServiceCall, callback
-from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
+from homeassistant.exceptions import HomeAssistantError
 from homeassistant.helpers import (
     aiohttp_client,
     config_validation as cv,
     entity_registry,
 )
-from homeassistant.helpers.debounce import Debouncer
-from homeassistant.helpers.dispatcher import (
-    async_dispatcher_connect,
-    async_dispatcher_send,
-)
-from homeassistant.helpers.entity import Entity, EntityDescription
+from homeassistant.helpers.entity import EntityDescription
 from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue
 from homeassistant.helpers.service import verify_domain_control
+from homeassistant.helpers.update_coordinator import CoordinatorEntity, UpdateFailed
 
 from .const import (
     CONF_FROM_WINDOW,
@@ -45,13 +39,10 @@
     DOMAIN,
     LOGGER,
 )
+from .coordinator import OpenUvCoordinator
 
 CONF_ENTRY_ID = "entry_id"
 
-DEFAULT_DEBOUNCER_COOLDOWN_SECONDS = 15 * 60
-
-TOPIC_UPDATE = f"{DOMAIN}_data_update"
-
 PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]
 
 SERVICE_NAME_UPDATE_DATA = "update_data"
@@ -127,53 +118,50 @@ async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
     _verify_domain_control = verify_domain_control(hass, DOMAIN)
 
     websession = aiohttp_client.async_get_clientsession(hass)
-    openuv = OpenUV(
-        hass,
-        entry,
-        Client(
-            entry.data[CONF_API_KEY],
-            entry.data.get(CONF_LATITUDE, hass.config.latitude),
-            entry.data.get(CONF_LONGITUDE, hass.config.longitude),
-            altitude=entry.data.get(CONF_ELEVATION, hass.config.elevation),
-            session=websession,
-        ),
+    client = Client(
+        entry.data[CONF_API_KEY],
[... cut ...]
```

Patch of `homeassistant/components/openuv/binary_sensor.py` in this fix:

```diff
@@ -10,6 +10,7 @@
 
 from . import OpenUvEntity
 from .const import DATA_PROTECTION_WINDOW, DOMAIN, LOGGER, TYPE_PROTECTION_WINDOW
+from .coordinator import OpenUvCoordinator
 
 ATTR_PROTECTION_WINDOW_ENDING_TIME = "end_time"
 ATTR_PROTECTION_WINDOW_ENDING_UV = "end_uv"
@@ -26,32 +27,27 @@
 async def async_setup_entry(
     hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
 ) -> None:
+    # Once we've successfully authenticated, we re-enable client request retries:
     """Set up an OpenUV sensor based on a config entry."""
-    openuv = hass.data[DOMAIN][entry.entry_id]
+    coordinators: dict[str, OpenUvCoordinator] = hass.data[DOMAIN][entry.entry_id]
+
     async_add_entities(
-        [OpenUvBinarySensor(openuv, BINARY_SENSOR_DESCRIPTION_PROTECTION_WINDOW)]
+        [
+            OpenUvBinarySensor(
+                coordinators[DATA_PROTECTION_WINDOW],
+                BINARY_SENSOR_DESCRIPTION_PROTECTION_WINDOW,
+            )
+        ]
     )
 
 
 class OpenUvBinarySensor(OpenUvEntity, BinarySensorEntity):
     """Define a binary sensor for OpenUV."""
 
-    async def async_update(self) -> None:
-        """Update the entity.
-
-        Only used by the generic entity update service.
-        """
-        await self.openuv.async_update_protection_data()
-        self.async_update_state()
-
     @callback
-    def update_from_latest_data(self) -> None:
-        """Update the state."""
-        if not (data := self.openuv.data[DATA_PROTECTION_WINDOW]):
-            self._attr_available = False
-            return
-
-        self._attr_available = True
+    def _update_from_latest_data(self) -> None:
+        """Update the entity from the latest data."""
+        data = self.coordinator.data
 
         for key in ("from_time", "to_time", "from_uv", "to_uv"):
             if not data.get(key):
```

Patch of `tests/components/openuv/test_diagnostics.py` in this fix:

```diff
@@ -1,6 +1,5 @@
 """Test OpenUV diagnostics."""
 from homeassistant.components.diagnostics import REDACTED
-from homeassistant.const import CONF_ENTITY_ID
 from homeassistant.setup import async_setup_component
 
 from tests.components.diagnostics import get_diagnostics_for_config_entry
@@ -9,12 +8,6 @@
 async def test_entry_diagnostics(hass, config_entry, hass_client, setup_openuv):
     """Test config entry diagnostics."""
     await async_setup_component(hass, "homeassistant", {})
-    await hass.services.async_call(
-        "homeassistant",
-        "update_entity",
-        {CONF_ENTITY_ID: ["sensor.current_uv_index"]},
-        blocking=True,
-    )
     assert await get_diagnostics_for_config_entry(hass, hass_client, config_entry) == {
         "entry": {
             "entry_id": config_entry.entry_id,
```

### Fix 3: a282e41d6838 (2022-09-18) · pull request #78691: Revert unintended OpenUV unique ID change

Pull-request labels: cla-signed, small-pr, integration: openuv, by-code-owner, bugfix

Commit message:

```
Revert unintended OpenUV unique ID change (#78691)
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
An unintended OpenUV unique ID format change leaked into https://github.com/home-assistant/core/pull/76878. This PR reverts it.

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
- [ ] Code quality improvements to existing
[... cut ...]
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `homeassistant/components/openuv/__init__.py`: `coordinates = f"{openuv.client.latitude}, {openuv.client.longitude}"`; `self._attr_unique_id = f"{coordinates}_{description.key}"`

Patch of `homeassistant/components/openuv/__init__.py` in this fix:

```diff
@@ -354,10 +354,11 @@ class OpenUvEntity(Entity):
 
     def __init__(self, openuv: OpenUV, description: EntityDescription) -> None:
         """Initialize."""
-        coordinates = f"{openuv.client.latitude}, {openuv.client.longitude}"
         self._attr_extra_state_attributes = {}
         self._attr_should_poll = False
-        self._attr_unique_id = f"{coordinates}_{description.key}"
+        self._attr_unique_id = (
+            f"{openuv.client.latitude}_{openuv.client.longitude}_{description.key}"
+        )
         self.entity_description = description
         self.openuv = openuv
```

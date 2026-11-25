# case086: home-assistant/core ca5a9c945649

File: `homeassistant/components/openuv/sensor.py` · committed 2022-09-17 10:56:45-01:00 · SZZ label: RISKY

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

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
  134      async def async_update(self) -> None:
  135          """Update the entity.
  136  
  137          Only used by the generic entity update service.
  138          """
  139          await self.openuv.async_update_uv_index_data()
  140          self.async_update_state()
  141  
```

## Candidate fixes (1 later commits to this file remove a blamed line; 3 later commits up to 2023-06-30 checked)

### Candidate 1: 60b3d6816b0a (2022-10-21)

Message:

```
Replace custom OpenUV data object with coordinators (#80705)

* Replace custom OpenUV data object with coordinators

* Typing

* Code review
```

Removed blamed lines: `"""Update the entity.`; `Only used by the generic entity update service.`; `async def async_update(self) -> None:`; `await self.openuv.async_update_uv_index_data()`; `self.async_update_state()`

Patch of this file:

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

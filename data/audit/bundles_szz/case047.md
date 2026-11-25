# case047: home-assistant/core 02731efc4cb3

Sampled file (the only file the models saw): `homeassistant/components/ibeacon/device_tracker.py` · committed 2022-09-23 15:45:09-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Handle iBeacons that broadcast multiple different uuids (#79011)

* Handle iBeacons that broadcast multiple different uuids

* fix flip-flopping between uuids

* naming
```

## Diff of the sampled file

```diff
@@ -26,7 +26,7 @@ async def async_setup_entry(
     def _async_device_new(
         unique_id: str,
         identifier: str,
-        parsed: iBeaconAdvertisement,
+        ibeacon_advertisement: iBeaconAdvertisement,
     ) -> None:
         """Signal a new device."""
         async_add_entities(
@@ -35,7 +35,7 @@ async def async_setup_entry(
                     coordinator,
                     identifier,
                     unique_id,
-                    parsed,
+                    ibeacon_advertisement,
                 )
             ]
         )
@@ -53,10 +53,12 @@ class IBeaconTrackerEntity(IBeaconEntity, BaseTrackerEntity):
         coordinator: IBeaconCoordinator,
         identifier: str,
         device_unique_id: str,
-        parsed: iBeaconAdvertisement,
+        ibeacon_advertisement: iBeaconAdvertisement,
     ) -> None:
         """Initialize an iBeacon tracker entity."""
-        super().__init__(coordinator, identifier, device_unique_id, parsed)
+        super().__init__(
+            coordinator, identifier, device_unique_id, ibeacon_advertisement
+        )
         self._attr_unique_id = device_unique_id
         self._active = True
 
@@ -78,11 +80,11 @@ class IBeaconTrackerEntity(IBeaconEntity, BaseTrackerEntity):
     @callback
     def _async_seen(
         self,
-        parsed: iBeaconAdvertisement,
+        ibeacon_advertisement: iBeaconAdvertisement,
     ) -> None:
         """Update state."""
         self._active = True
-        self._parsed = parsed
+        self._ibeacon_advertisement = ibeacon_advertisement
         self.async_write_ha_state()
 
     @callback
```

## Other files changed by this commit (8)

- `homeassistant/components/ibeacon/coordinator.py` (+44 −30)
- `homeassistant/components/ibeacon/entity.py` (+8 −8)
- `homeassistant/components/ibeacon/manifest.json` (+1 −1)
- `homeassistant/components/ibeacon/sensor.py` (+12 −10)
- `requirements_all.txt` (+1 −1)
- `requirements_test_all.txt` (+1 −1)
- `tests/components/ibeacon/__init__.py` (+43 −0)
- `tests/components/ibeacon/test_sensor.py` (+62 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 3b05bb5b3a0c (2022-09-28) · pull request #79220: Update iBeacon UUID Major and Minor format for compatibility

Pull-request labels: cla-signed, small-pr, bugfix, integration: ibeacon

Commit message:

```
Update iBeacon UUID Major and Minor format for compatibility (#79220)
```

Pull-request description:

```
<!--
  You are amazing! Thanks for contributing to our project!
  Please, DO NOT DELETE ANY TEXT from this template! (unless instructed).
-->
## Breaking change
<!--
  If your PR contains a breaking change for existing users, it is important
  to tell them what breaks, how to make it work again and why we did this.
  This piece of text is published with the release notes, so it helps if you
  write it towards our users, not us.
  Note: Remove this section if this PR is NOT a breaking change.
-->


## Proposed change
<!--
  Describe the big picture of your changes here to communicate to the
  maintainers why we should accept this pull request. If it fixes a bug
  or resolves a feature request, be sure to link to that issue in the
  additional information section.
-->

Update the iBeacon format to be compatible with integrations that may provide the format as an attribute name like the android app.

Old format: `UUID Major.Minor`
New format: `UUID_Major_Minor`

See: https://github.com/home-assistant/android/issues/2928 for more info

## Type of change
<!--
  What type of change does your PR introduce to Home Assistant?
  NOTE: Please, check only 1! box!
  If your PR requires multiple
[... cut ...]
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `homeassistant/components/ibeacon/coordinator.py`: `base_name = f"{ibeacon_advertisement.uuid} {ibeacon_advertisement.major}.{ibeacon_advertisement.minor}"`

Patch of `homeassistant/components/ibeacon/coordinator.py` in this fix:

```diff
@@ -62,7 +62,7 @@ def async_name(
         service_info.name,
         service_info.name.replace("_", ":"),
     ):
-        base_name = f"{ibeacon_advertisement.uuid} {ibeacon_advertisement.major}.{ibeacon_advertisement.minor}"
+        base_name = f"{ibeacon_advertisement.uuid}_{ibeacon_advertisement.major}_{ibeacon_advertisement.minor}"
     else:
         base_name = service_info.name
     if unique_address:
```

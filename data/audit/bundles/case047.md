# case047: home-assistant/core 02731efc4cb3

File: `homeassistant/components/ibeacon/device_tracker.py` · committed 2022-09-23 15:45:09-01:00 · SZZ label: RISKY

## Commit message

```
Handle iBeacons that broadcast multiple different uuids (#79011)

* Handle iBeacons that broadcast multiple different uuids

* fix flip-flopping between uuids

* naming
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
   29          ibeacon_advertisement: iBeaconAdvertisement,
   38                      ibeacon_advertisement,
   56          ibeacon_advertisement: iBeaconAdvertisement,
   59          super().__init__(
   60              coordinator, identifier, device_unique_id, ibeacon_advertisement
   61          )
   83          ibeacon_advertisement: iBeaconAdvertisement,
   87          self._ibeacon_advertisement = ibeacon_advertisement
```

## Candidate fixes (0 later commits to this file remove a blamed line; 1 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

# case114: home-assistant/core 69bf77be1246

File: `homeassistant/components/fritzbox/coordinator.py` · committed 2022-09-28 09:43:31-01:00 · SZZ label: RISKY

## Commit message

```
Avoid multiline lambdas in Fritz!Smarthome sensors (#78524)

* avoid multiline lambdas

* update tests
```

## Diff of the target file

```diff
@@ -52,8 +52,9 @@ class FritzboxDataUpdateCoordinator(DataUpdateCoordinator):
             if (
                 device.has_powermeter
                 and device.present
-                and hasattr(device, "voltage")
+                and isinstance(device.voltage, int)
                 and device.voltage <= 0
+                and isinstance(device.power, int)
                 and device.power <= 0
                 and device.energy <= 0
             ):
```

## Lines SZZ blamed (line numbers in the new version)

```
   55                  and isinstance(device.voltage, int)
   57                  and isinstance(device.power, int)
```

## Candidate fixes (0 later commits to this file remove a blamed line; 3 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

# case114: home-assistant/core 69bf77be1246

Sampled file (the only file the models saw): `homeassistant/components/fritzbox/coordinator.py` · committed 2022-09-28 09:43:31-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Avoid multiline lambdas in Fritz!Smarthome sensors (#78524)

* avoid multiline lambdas

* update tests
```

## Diff of the sampled file

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

## Other files changed by this commit (3)

- `homeassistant/components/fritzbox/sensor.py` (+56 −24)
- `tests/components/fritzbox/test_climate.py` (+16 −0)
- `tests/components/fritzbox/test_switch.py` (+18 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 4abe5aec6cff (2022-10-21) · pull request #80682: Fix ZeroDivisionError for Fritz!Smarthome electric current sensor

Pull-request labels: Hacktoberfest, cla-signed, integration: fritzbox, small-pr, bugfix, Quality Scale: No score

Commit message:

```
Fix ZeroDivisionError for Fritz!Smarthome electric current sensor (#80682)

Fixes ZeroDivisionError for fritzbox sensor. Fixes #80618.
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


## Type of change
<!--
  What type of change does your PR introduce to Home Assistant?
  NOTE: Please, check only 1! box!
  If your PR requires multiple boxes to be checked, you'll most likely need to
  split it into multiple PRs. This makes things easier and faster to code review.
-->

- [ ] Dependency upgrade
- [X] Bugfix (non-breaking change which fixes an issue)
- [ ] New integration (thank you!)
- [ ] New feature
[... cut ...]
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `homeassistant/components/fritzbox/sensor.py`: `if isinstance(device.power, int) and isinstance(device.voltage, int):`

Patch of `homeassistant/components/fritzbox/sensor.py` in this fix:

```diff
@@ -76,7 +76,11 @@ def suitable_temperature(device: FritzhomeDevice) -> bool:
 
 def value_electric_current(device: FritzhomeDevice) -> float:
     """Return native value for electric current sensor."""
-    if isinstance(device.power, int) and isinstance(device.voltage, int):
+    if (
+        isinstance(device.power, int)
+        and isinstance(device.voltage, int)
+        and device.voltage > 0
+    ):
         return round(device.power / device.voltage, 3)
     return 0.0
```

# case112: home-assistant/core 27d1c1f471ce

Sampled file (the only file the models saw): `homeassistant/components/nibe_heatpump/config_flow.py` · committed 2022-09-22 13:17:04-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Nibe Heat Pump after merge fixups (#78931)
```

## Diff of the sampled file

```diff
@@ -115,7 +115,7 @@ class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
         try:
             info = await validate_input(self.hass, user_input)
         except FieldError as exception:
-            LOGGER.exception("Validation error")
+            LOGGER.debug("Validation error %s", exception)
             errors[exception.field] = exception.error
         except Exception:  # pylint: disable=broad-except
             LOGGER.exception("Unexpected exception")
```

## Other files changed by this commit (5)

- `homeassistant/components/nibe_heatpump/__init__.py` (+22 −19)
- `homeassistant/components/nibe_heatpump/sensor.py` (+84 −23)
- `homeassistant/components/nibe_heatpump/strings.json` (+0 −3)
- `homeassistant/components/nibe_heatpump/translations/en.json` (+2 −4)
- `tests/components/nibe_heatpump/test_config_flow.py` (+10 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 1c86a1223386 (2022-10-12) · pull request #80140: Correct units for sensors in nibe heatpump

Pull-request labels: Hacktoberfest, cla-signed, cherry-picked, small-pr, by-code-owner, bugfix, integration: nibe_heatpump

Commit message:

```
Correct units for sensors in nibe heatpump (#80140)
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

- Parameters without units should still be marked as diagnostics. 
- Hour sensors are also total increasing (running time of pump)
- W should be power sensors
- Wh should be energy sensors


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
- [ ] Breaking change (fix/feature causing existing fu
[... cut ...]
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `homeassistant/components/nibe_heatpump/sensor.py`: `device_class=SensorDeviceClass.POWER,`

Patch of `homeassistant/components/nibe_heatpump/sensor.py` in this fix:

```diff
@@ -19,6 +19,7 @@
     ENERGY_KILO_WATT_HOUR,
     ENERGY_MEGA_WATT_HOUR,
     ENERGY_WATT_HOUR,
+    POWER_WATT,
     TEMP_CELSIUS,
     TEMP_FAHRENHEIT,
     TIME_HOURS,
@@ -72,31 +73,39 @@
         state_class=SensorStateClass.MEASUREMENT,
         native_unit_of_measurement=ELECTRIC_POTENTIAL_MILLIVOLT,
     ),
+    "W": SensorEntityDescription(
+        key="W",
+        entity_category=EntityCategory.DIAGNOSTIC,
+        device_class=SensorDeviceClass.POWER,
+        state_class=SensorStateClass.MEASUREMENT,
+        native_unit_of_measurement=POWER_WATT,
+    ),
     "Wh": SensorEntityDescription(
         key="Wh",
         entity_category=EntityCategory.DIAGNOSTIC,
-        device_class=SensorDeviceClass.POWER,
+        device_class=SensorDeviceClass.ENERGY,
         state_class=SensorStateClass.TOTAL_INCREASING,
         native_unit_of_measurement=ENERGY_WATT_HOUR,
     ),
     "kWh": SensorEntityDescription(
         key="kWh",
         entity_category=EntityCategory.DIAGNOSTIC,
-        device_class=SensorDeviceClass.POWER,
+        device_class=SensorDeviceClass.ENERGY,
         state_class=SensorStateClass.TOTAL_INCREASING,
         native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
     ),
     "MWh": SensorEntityDescription(
         key="MWh",
         entity_category=EntityCategory.DIAGNOSTIC,
-        device_class=SensorDeviceClass.POWER,
+        device_class=SensorDeviceClass.ENERGY,
         state_class=SensorStateClass.TOTAL_INCREASING,
         native_unit_of_measurement=ENERGY_MEGA_WATT_HOUR,
     ),
     "h": SensorEntityDescription(
         key="h",
         entity_category=EntityCategory.DIAGNOSTIC,
         device_class=SensorDeviceClass.DURATION,
+        state_class=SensorStateClass.TOTAL_INCREASING,
         native_unit_of_measurement=TIME_HOURS,
     ),
 }
@@ -133,6 +142,7 @@ def __init__(
             self.entity_description = entity_description
         else:
             self._attr_native_unit_of_measurement = coil.unit
+            self._attr_entity_category = EntityCategory.DIAGNOSTIC
 
     def _async_read_coil(self, coil: Coil):
         self._attr_native_value = coil.value
```

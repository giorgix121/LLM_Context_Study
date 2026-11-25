# case118: home-assistant/core 6abf677092e2

Sampled file (the only file the models saw): `homeassistant/components/plugwise/gateway.py` · committed 2022-10-12 15:48:09-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Bump plugwise to v0.25.0 and adapt relevant plugwise code (#80129)
```

## Diff of the sampled file

```diff
@@ -72,8 +72,8 @@ async def async_setup_entry_gw(hass: HomeAssistant, entry: ConfigEntry) -> bool:
         config_entry_id=entry.entry_id,
         identifiers={(DOMAIN, str(api.gateway_id))},
         manufacturer="Plugwise",
-        name=entry.title,
-        model=f"Smile {api.smile_name}",
+        model=api.smile_model,
+        name=api.smile_name,
         sw_version=api.smile_version[0],
     )
```

## Other files changed by this commit (14)

- `homeassistant/components/plugwise/const.py` (+2 −2)
- `homeassistant/components/plugwise/manifest.json` (+1 −1)
- `requirements_all.txt` (+1 −1)
- `requirements_test_all.txt` (+1 −1)
- `tests/components/plugwise/conftest.py` (+12 −3)
- `tests/components/plugwise/fixtures/adam_multiple_devices_per_zone/all_data.json` (+23 −8)
- `tests/components/plugwise/fixtures/anna_heatpump_heating/all_data.json` (+13 −8)
- `tests/components/plugwise/fixtures/m_adam_cooling/all_data.json` (+29 −15)
- `tests/components/plugwise/fixtures/m_adam_heating/all_data.json` (+13 −9)
- `tests/components/plugwise/fixtures/m_anna_heatpump_cooling/all_data.json` (+14 −8)
- `tests/components/plugwise/fixtures/m_anna_heatpump_idle/all_data.json` (+22 −16)
- `tests/components/plugwise/fixtures/p1v3_full_option/all_data.json` (+16 −5)
- `tests/components/plugwise/fixtures/stretch_v31/all_data.json` (+3 −3)
- `tests/components/plugwise/test_diagnostics.py` (+23 −8)

## Fix commits that the dataset links to this commit (1)

### Fix 1: bd6678c73b37 (2022-10-23) · pull request #80782: Bump plugwise to v0.25.3 

Pull-request labels: Hacktoberfest, cla-signed, small-pr, has-tests, integration: plugwise, dependency, by-code-owner, bugfix, Quality Scale: No score

Commit message:

```
Bump plugwise to v0.25.3 (#80782)
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
Bump the plugwise backend to v0.25.3 - https://github.com/plugwise/python-plugwise/releases/tag/v0.25.3

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
- [ ] Code quality improvements to existing code or addition of tes
[... cut ...]
```

This fix changes 4 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `tests/components/plugwise/fixtures/m_adam_cooling/all_data.json`: `"setpoint_low": 20.0,`

Patch of `tests/components/plugwise/fixtures/m_adam_cooling/all_data.json` in this fix:

```diff
@@ -14,7 +14,7 @@
       "name": "Anna",
       "vendor": "Plugwise",
       "thermostat": {
-        "setpoint_low": 20.0,
+        "setpoint_low": 4.0,
         "setpoint_high": 23.5,
         "lower_bound": 1.0,
         "upper_bound": 35.0,
@@ -30,7 +30,7 @@
       "mode": "heat_cool",
       "sensors": {
         "temperature": 25.8,
-        "setpoint_low": 20.0,
+        "setpoint_low": 4.0,
         "setpoint_high": 23.5
       }
     },
```

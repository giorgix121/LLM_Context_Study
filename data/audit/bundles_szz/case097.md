# case097: home-assistant/core 47d0598e7548

Sampled file (the only file the models saw): `homeassistant/components/homekit/type_lights.py` · committed 2022-10-06 13:22:39-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Use Kelvin as the preferred color temperature unit (#79591)

* Use Kelvin as the preferred white temperature unit

* Update homekit

* Adjust tests
```

## Diff of the sampled file

```diff
@@ -193,7 +193,10 @@ class Light(HomeAccessory):
                 params[ATTR_COLOR_TEMP] = temp
             elif self.rgbww_supported:
                 params[ATTR_RGBWW_COLOR] = color_temperature_to_rgbww(
-                    temp, bright_val, self.min_mireds, self.max_mireds
+                    color_temperature_mired_to_kelvin(temp),
+                    bright_val,
+                    color_temperature_mired_to_kelvin(self.max_mireds),
+                    color_temperature_mired_to_kelvin(self.min_mireds),
                 )
             elif self.rgbw_supported:
                 params[ATTR_RGBW_COLOR] = (*(0,) * 3, bright_val)
```

## Other files changed by this commit (6)

- `homeassistant/components/light/__init__.py` (+88 −30)
- `homeassistant/util/color.py` (+33 −12)
- `tests/components/homekit_controller/specific_devices/test_nanoleaf_strip_nl55.py` (+2 −0)
- `tests/components/light/test_init.py` (+33 −7)
- `tests/components/yeelight/test_light.py` (+83 −6)
- `tests/util/test_color.py` (+77 −74)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 61deb54ec84b (2022-10-06) · pull request #79738: Fix max_color_temp_kelvin

Pull-request labels: Hacktoberfest, core, cla-signed, integration: light, small-pr, bugfix

Commit message:

```
Fix max_color_temp_kelvin (#79738)

fix max_color_temp_kelvin
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
- in `homeassistant/components/light/__init__.py`: `if self._attr_min_color_temp_kelvin is None:`; `return self._attr_min_color_temp_kelvin`

Patch of `homeassistant/components/light/__init__.py` in this fix:

```diff
@@ -889,9 +889,9 @@ def min_color_temp_kelvin(self) -> int:
     @property
     def max_color_temp_kelvin(self) -> int:
         """Return the coldest color_temp_kelvin that this light supports."""
-        if self._attr_min_color_temp_kelvin is None:
+        if self._attr_max_color_temp_kelvin is None:
             return color_util.color_temperature_mired_to_kelvin(self.min_mireds)
-        return self._attr_min_color_temp_kelvin
+        return self._attr_max_color_temp_kelvin
 
     @property
     def effect_list(self) -> list[str] | None:
```

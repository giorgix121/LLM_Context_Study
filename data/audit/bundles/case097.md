# case097: home-assistant/core 47d0598e7548

File: `homeassistant/components/homekit/type_lights.py` · committed 2022-10-06 13:22:39-01:00 · SZZ label: RISKY

## Commit message

```
Use Kelvin as the preferred color temperature unit (#79591)

* Use Kelvin as the preferred white temperature unit

* Update homekit

* Adjust tests
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
  196                      color_temperature_mired_to_kelvin(temp),
  197                      bright_val,
  198                      color_temperature_mired_to_kelvin(self.max_mireds),
  199                      color_temperature_mired_to_kelvin(self.min_mireds),
```

## Candidate fixes (0 later commits to this file remove a blamed line; 2 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

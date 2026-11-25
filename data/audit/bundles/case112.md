# case112: home-assistant/core 27d1c1f471ce

File: `homeassistant/components/nibe_heatpump/config_flow.py` · committed 2022-09-22 13:17:04-01:00 · SZZ label: RISKY

## Commit message

```
Nibe Heat Pump after merge fixups (#78931)
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
  118              LOGGER.debug("Validation error %s", exception)
```

## Candidate fixes (0 later commits to this file remove a blamed line; 7 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

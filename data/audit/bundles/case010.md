# case010: home-assistant/core d0ac1073a0f4

File: `homeassistant/components/pushover/__init__.py` · committed 2022-09-29 13:40:53-01:00 · SZZ label: RISKY

## Commit message

```
Allow entries with same user_key for Pushover (#77904)

* Allow entries with same user_key for Pushover

* remove unique_id completely

* Abort reauth if entered api_key already exists
Update tests
```

## Diff of the target file

```diff
@@ -25,6 +25,10 @@ async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
 async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
     """Set up pushover from a config entry."""
 
+    # remove unique_id for beta users
+    if entry.unique_id is not None:
+        hass.config_entries.async_update_entry(entry, unique_id=None)
+
     pushover_api = PushoverAPI(entry.data[CONF_API_KEY])
     try:
         await hass.async_add_executor_job(
```

## Lines SZZ blamed (line numbers in the new version)

```
   28      # remove unique_id for beta users
   29      if entry.unique_id is not None:
   30          hass.config_entries.async_update_entry(entry, unique_id=None)
   31  
```

## Candidate fixes (0 later commits to this file remove a blamed line; 3 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

# case115: home-assistant/core 731f6180289c

File: `homeassistant/components/yeelight/scanner.py` · committed 2022-10-15 09:00:46-01:00 · SZZ label: RISKY

## Commit message

```
Make home assistant discoverable via UPnP/SSDP (#79820)
```

## Diff of the target file

```diff
@@ -76,7 +76,7 @@ class YeelightScanner:
             self._listeners.append(
                 SsdpSearchListener(
                     async_callback=self._async_process_entry,
-                    service_type=SSDP_ST,
+                    search_target=SSDP_ST,
                     target=SSDP_TARGET,
                     source=source,
                     async_connect_callback=_wrap_async_connected_idx(idx),
```

## Lines SZZ blamed (line numbers in the new version)

```
   79                      search_target=SSDP_ST,
```

## Candidate fixes (0 later commits to this file remove a blamed line; 5 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

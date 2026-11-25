# case088: home-assistant/core 7c460cc641f1

File: `homeassistant/components/braviatv/coordinator.py` · committed 2022-09-23 04:03:43-01:00 · SZZ label: RISKY

## Commit message

```
Add PSK auth and SSDP discovery to Bravia TV (#77772)
```

## Diff of the target file

```diff
@@ -59,12 +59,14 @@ class BraviaTVCoordinator(DataUpdateCoordinator[None]):
         hass: HomeAssistant,
         client: BraviaTV,
         pin: str,
+        use_psk: bool,
         ignored_sources: list[str],
     ) -> None:
         """Initialize Bravia TV Client."""
 
         self.client = client
         self.pin = pin
+        self.use_psk = use_psk
         self.ignored_sources = ignored_sources
         self.source: str | None = None
         self.source_list: list[str] = []
@@ -110,9 +112,12 @@ class BraviaTVCoordinator(DataUpdateCoordinator[None]):
         """Connect and fetch data."""
         try:
             if not self.connected:
-                await self.client.connect(
-                    pin=self.pin, clientid=CLIENTID_PREFIX, nickname=NICKNAME
-                )
+                if self.use_psk:
+                    await self.client.connect(psk=self.pin)
+                else:
+                    await self.client.connect(
+                        pin=self.pin, clientid=CLIENTID_PREFIX, nickname=NICKNAME
+                    )
                 self.connected = True
 
             power_status = await self.client.get_power_status()
```

## Lines SZZ blamed (line numbers in the new version)

```
   62          use_psk: bool,
   69          self.use_psk = use_psk
  115                  if self.use_psk:
  116                      await self.client.connect(psk=self.pin)
  117                  else:
  118                      await self.client.connect(
  119                          pin=self.pin, clientid=CLIENTID_PREFIX, nickname=NICKNAME
  120                      )
```

## Candidate fixes (3 later commits to this file remove a blamed line; 10 later commits up to 2023-06-30 checked)

### Candidate 1: 9dd9147343ac (2022-10-05)

Message:

```
Use HA `uuid` as `client_id` in BraviaTV (#79618)

* Use uuid as clientid/nickname

* Fixes after rebase

* Move gen_instance_ids() to utils

* Store client_id and nickname in config_entry

* Update tests

* Clean names

* Rename consts
```

Removed blamed lines: `pin=self.pin, clientid=CLIENTID_PREFIX, nickname=NICKNAME`; `self.use_psk = use_psk`; `use_psk: bool,`

Patch of this file:

```diff
@@ -5,6 +5,7 @@
 from datetime import timedelta
 from functools import wraps
 import logging
+from types import MappingProxyType
 from typing import Any, Final, TypeVar
 
 from pybravia import (
@@ -19,12 +20,20 @@
 from typing_extensions import Concatenate, ParamSpec
 
 from homeassistant.components.media_player import MediaType
+from homeassistant.const import CONF_PIN
 from homeassistant.core import HomeAssistant
 from homeassistant.exceptions import ConfigEntryAuthFailed
 from homeassistant.helpers.debounce import Debouncer
 from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
 
-from .const import CLIENTID_PREFIX, DOMAIN, NICKNAME
+from .const import (
+    CONF_CLIENT_ID,
+    CONF_NICKNAME,
+    CONF_USE_PSK,
+    DOMAIN,
+    LEGACY_CLIENT_ID,
+    NICKNAME_PREFIX,
+)
 
 _BraviaTVCoordinatorT = TypeVar("_BraviaTVCoordinatorT", bound="BraviaTVCoordinator")
 _P = ParamSpec("_P")
@@ -61,15 +70,16 @@ def __init__(
         self,
         hass: HomeAssistant,
         client: BraviaTV,
-        pin: str,
-        use_psk: bool,
+        config: MappingProxyType[str, Any],
         ignored_sources: list[str],
     ) -> None:
         """Initialize Bravia TV Client."""
 
         self.client = client
-        self.pin = pin
-        self.use_psk = use_psk
+        self.pin = config[CONF_PIN]
+        self.use_psk = config.get(CONF_USE_PSK, False)
+        self.client_id = config.get(CONF_CLIENT_ID, LEGACY_CLIENT_ID)
+        self.nickname = config.get(CONF_NICKNAME, NICKNAME_PREFIX)
         self.ignored_sources = ignored_sources
         self.source: str | None = None
         self.source_list: list[str] = []
@@ -119,7 +129,7 @@ async def _async_update_data(self) -> None:
                     await self.client.connect(psk=self.pin)
                 else:
                     await self.client.connect(
-                        pin=self.pin, clientid=CLIENTID_PREFIX, nickname=NICKNAME
+                        pin=self.pin, clientid=self.client_id, nickname=self.nickname
                     )
                 self.connected = True
```

### Candidate 2: 8acc114cd9ce (2022-11-30)

Message:

```
Fix BraviaTV fake reauthentication (#82986)
```

Removed blamed lines: `await self.client.connect(`; `await self.client.connect(psk=self.pin)`; `else:`; `if self.use_psk:`

Patch of this file:

```diff
@@ -125,13 +125,18 @@ async def _async_update_data(self) -> None:
         """Connect and fetch data."""
         try:
             if not self.connected:
-                if self.use_psk:
-                    await self.client.connect(psk=self.pin)
-                else:
-                    await self.client.connect(
-                        pin=self.pin, clientid=self.client_id, nickname=self.nickname
-                    )
-                self.connected = True
+                try:
+                    if self.use_psk:
+                        await self.client.connect(psk=self.pin)
+                    else:
+                        await self.client.connect(
+                            pin=self.pin,
+                            clientid=self.client_id,
+                            nickname=self.nickname,
+                        )
+                    self.connected = True
+                except BraviaTVAuthError as err:
+                    raise ConfigEntryAuthFailed from err
 
             power_status = await self.client.get_power_status()
             self.is_on = power_status == "active"
@@ -151,8 +156,6 @@ async def _async_update_data(self) -> None:
                 _LOGGER.debug("Update skipped, Bravia API service is reloading")
                 return
             raise UpdateFailed("Error communicating with device") from err
-        except BraviaTVAuthError as err:
-            raise ConfigEntryAuthFailed from err
         except (BraviaTVConnectionError, BraviaTVConnectionTimeout, BraviaTVTurnedOff):
             self.is_on = False
             self.connected = False
```

### Candidate 3: 02e973026d0b (2023-01-24)

Message:

```
Add browse media and play media support in Bravia TV (#85288)

* Add media browsing and play media support in Bravia TV

* Add fix invalid Bravia Content-Type header for icons

* Avoid duplicates in source_list

* Small cleanup

* Edit comment

* Revert en.json
```

Removed blamed lines: `else:`

Patch of this file:

```diff
@@ -32,6 +32,7 @@
     DOMAIN,
     LEGACY_CLIENT_ID,
     NICKNAME_PREFIX,
+    SourceType,
 )
 
 _BraviaTVCoordinatorT = TypeVar("_BraviaTVCoordinatorT", bound="BraviaTVCoordinator")
@@ -44,15 +45,15 @@
 def catch_braviatv_errors(
     func: Callable[Concatenate[_BraviaTVCoordinatorT, _P], Awaitable[None]]
 ) -> Callable[Concatenate[_BraviaTVCoordinatorT, _P], Coroutine[Any, Any, None]]:
-    """Catch BraviaClient errors."""
+    """Catch Bravia errors."""
 
     @wraps(func)
     async def wrapper(
         self: _BraviaTVCoordinatorT,
         *args: _P.args,
         **kwargs: _P.kwargs,
     ) -> None:
-        """Catch BraviaClient errors and log message."""
+        """Catch Bravia errors and log message."""
         try:
             await func(self, *args, **kwargs)
         except BraviaError as err:
@@ -70,7 +71,6 @@ def __init__(
         hass: HomeAssistant,
         client: BraviaClient,
         config: MappingProxyType[str, Any],
-        ignored_sources: list[str],
     ) -> None:
         """Initialize Bravia TV Client."""
 
@@ -79,11 +79,11 @@ def __init__(
         self.use_psk = config.get(CONF_USE_PSK, False)
         self.client_id = config.get(CONF_CLIENT_ID, LEGACY_CLIENT_ID)
         self.nickname = config.get(CONF_NICKNAME, NICKNAME_PREFIX)
-        self.ignored_sources = ignored_sources
         self.source: str | None = None
         self.source_list: list[str] = []
         self.source_map: dict[str, dict] = {}
         self.media_title: str | None = None
+        self.media_channel: str | None = None
         self.media_content_id: str | None = None
         self.media_content_type: MediaType | None = None
         self.media_uri: str | None = None
@@ -92,7 +92,6 @@ def __init__(
         self.volume_target: str | None = None
         self.volume_muted = False
         self.is_on = False
-        self.is_channel = False
         self.connected = False
         self.skipped_updates = 0
 
@@ -106,16 +105,23 @@ def __init__(
             ),
         )
 
-    def _sources_extend(self, sources: list[dict], source_type: str) -> None:
+    def _sources_extend(
+        self,
+        sources: list[dict],
+        source_type: SourceType,
+        add_to_list: bool = False,
+        sort_by: str | None = None,
+    ) -> None:
         """Extend source map and source list."""
+        if sort_by:
+            sources = sorted(sources, key=lambda d: d.get(sort_by, ""))
         for item in sources:
-            item["type"] = source_type
             title = item.get("title")
             uri = item.get("uri")
             if not title or not uri:
                 continue
-            self.source_map[uri] = item
-            if title not in self.ignored_sources:
+            self.source_map[uri] = {**item, "type": source_type}
+            if add_to_list and title not in self.source_list:
                 self.source_list.append(title)
 
     async def _async_update_data(self) -> None:
@@ -162,25 +168,10 @@ async def _async_update_data(self) -> None:
             self.connected = False
             raise UpdateFailed("Error communicating with device") from err
 
-    async def async_update_sources(self) -> None:
-        """Update sources."""
-        self.source_list = []
-        self.source_map = {}
-
-        externals = await self.client.get_external_status()
-        self._sources_extend(externals, "input")
-
-        apps = await self.client.get_app_list()
-        self._sources_extend(apps, "app")
-
-        channels = await self.client.get_content_list_all("tv")
-        self._sources_extend(channels, "channel")
-
     async def async_update_volume(self) -> None:
         """Update volume information."""
         volume_info = await self.client.get_volume_info()
-        volume_level = volume_info.get("volume")
-        if volume_level is not None:
+        if volume_level := volume_info.get("volume"):
             self.volume_level = volume_level / 100
             self.volume_muted = volume_info.get("mute", False)
             self.volume_target = volume_info.get("target")
@@ -191,27 +182,68 @@ async def async_update_playing(self) -> None:
         self.media_title = playing_info.get("title")
         self.media_uri = playing_info.get("uri")
         self.media_duration = playing_info.get("durationSec")
-        if program_title := playing_info.get("programTitle"):
-            self.media_title = f"{self.media_title}: {program_title}"
+        self.media_channel = None
+        self.media_content_id = None
+        self.media_content_type = None
+        self.source = None
         if self.media_uri:
-            source = self.source_map.get(self.media_uri, {})
-            self.source = source.get("title")
-            self.is_channel = self.media_uri[:2] == "tv"
-            if self.is_channel:
+            self.media_content_id = self.media_uri
+            if self.media_uri[:8] == "extInput":
+                self.source = playing_info.get("title")
+            if self.media_uri[:2] == "tv":
+                self.media_title = playing_info.get("programTitle")
+                self.media_channel = playing_info.get("title")
                 self.media_content_id = playing_info.get("dispNum")
                 self.media_content_type = MediaType.CHANNEL
-            else:
-                self.media_content_id = self.media_uri
-                self.media_content_type = None
-        else:
-            self.source = None
-            self.is_channel = False
-            self.media_content_id = None
-            self.media_content_type = None
         if not playing_info:
             self.media_title = "Smart TV"
             self.media_content_type = MediaType.APP
 
+    async def async_update_sources(self) -> None:
+        """Update all sources."""
+        self.source_list = []
+        self.source_map = {}
+
+        inputs = await self.client.get_external_status()
+        self._sources_extend(inputs, SourceType.INPUT, add_to_list=True)
+
+        a
```

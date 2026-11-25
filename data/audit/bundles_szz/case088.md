# case088: home-assistant/core 7c460cc641f1

Sampled file (the only file the models saw): `homeassistant/components/braviatv/coordinator.py` · committed 2022-09-23 04:03:43-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Add PSK auth and SSDP discovery to Bravia TV (#77772)
```

## Diff of the sampled file

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

## Other files changed by this commit (8)

- `homeassistant/components/braviatv/__init__.py` (+9 −2)
- `homeassistant/components/braviatv/config_flow.py` (+78 −16)
- `homeassistant/components/braviatv/const.py` (+1 −0)
- `homeassistant/components/braviatv/manifest.json` (+6 −0)
- `homeassistant/components/braviatv/strings.json` (+9 −3)
- `homeassistant/components/braviatv/translations/en.json` (+9 −3)
- `homeassistant/generated/ssdp.py` (+6 −0)
- `tests/components/braviatv/test_config_flow.py` (+175 −8)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 55d90c0abc55 (2022-09-23) · pull request #79002: Correct ssdp generation for bravia

Pull-request labels: cla-signed, small-pr, bugfix

Commit message:

```
Correct ssdp generation for bravia (#79002)

Correct ssdp generation
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

Fix CI after bravia change.

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
- [ ] Breaking change (fix/feature causing existing functionality to break)
- [ ] Code quality improvements to existing code or addition of tests

## Additional information
<!--
  Details are important, and help maint
[... cut ...]
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `homeassistant/generated/ssdp.py`: `"st": "urn:schemas-sony-com:service:ScalarWebAPI:1"`; `}`

Patch of `homeassistant/generated/ssdp.py` in this fix:

```diff
@@ -18,8 +18,8 @@
     "braviatv": [
         {
             "manufacturer": "Sony Corporation",
-            "st": "urn:schemas-sony-com:service:ScalarWebAPI:1"
-        }
+            "st": "urn:schemas-sony-com:service:ScalarWebAPI:1",
+        },
     ],
     "control4": [
         {
```

# case133: home-assistant/core 2ed48a9b28f1

Sampled file (the only file the models saw): `homeassistant/components/zha/entity.py` · committed 2022-09-28 09:22:39-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Add configuration entities and device actions for Inovelli Blue Series switch to ZHA (#79106)

* Add Inovelli configutation entities to ZHA

* add device actions

* fix attribute name collision

* add device action tests

* disable remote protection per Inovelli request

* expect_reply to false

* update test for expect_reply change

* inovelli feedback

* translation keys and strings

* clean up numbers

* prevent double events

* remove individual LED defaults per inovelli

* redundant check

* update test
```

## Diff of the sampled file

```diff
@@ -66,6 +66,8 @@ class BaseZhaEntity(LogMixin, entity.Entity):
     @property
     def name(self) -> str:
         """Return Entity's default name."""
+        if hasattr(self, "_attr_name") and self._attr_name is not None:
+            return self._attr_name
         return self._name
 
     @property
```

## Other files changed by this commit (9)

- `homeassistant/components/zha/core/channels/manufacturerspecific.py` (+127 −3)
- `homeassistant/components/zha/core/const.py` (+1 −0)
- `homeassistant/components/zha/device_action.py` (+118 −5)
- `homeassistant/components/zha/number.py` (+252 −0)
- `homeassistant/components/zha/select.py` (+43 −5)
- `homeassistant/components/zha/strings.json` (+6 −1)
- `homeassistant/components/zha/switch.py` (+79 −0)
- `homeassistant/components/zha/translations/en.json` (+3 −1)
- `tests/components/zha/test_device_action.py` (+191 −9)

## Fix commits that the dataset links to this commit (2)

### Fix 1: 5f1c92ce51e5 (2022-11-01) · pull request #81351: Fix individual LED range for ZHA device action

Pull-request labels: cla-signed, integration: zha, cherry-picked, small-pr, by-code-owner, bugfix, Quality Scale: No score

Commit message:

```
Fix individual LED range for ZHA device action (#81351)

The inovelli individual LED effect device action can address 7 LEDs. I had set the range 1-7 but it should be 0-6.
```

Pull-request description:

```
The inovelli individual LED effect device action can address 7 LEDs. I had set the range 1-7 but it should be 0-6.

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
No

## Proposed change
<!--
  Describe the big picture of your changes here to communicate to the
  maintainers why we should accept this pull request. If it fixes a bug
  or resolves a feature request, be sure to link to that issue in the
  additional information section.
-->
This PR corrects the range in the schema for a ZHA device action. 

## Type of change
<!--
  What type of change does your PR introduce to Home Assistant?
  NOTE: Please, check only 1! box!
  If your PR requires multiple boxes to be checked, you'll most likely need to
  split it into multiple PRs. This m
[... cut ...]
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `homeassistant/components/zha/device_action.py`: `vol.Required("led_number"): vol.All(vol.Coerce(int), vol.Range(1, 7)),`

Patch of `homeassistant/components/zha/device_action.py` in this fix:

```diff
@@ -93,7 +93,7 @@
     ),
     INOVELLI_INDIVIDUAL_LED_EFFECT: vol.Schema(
         {
-            vol.Required("led_number"): vol.All(vol.Coerce(int), vol.Range(1, 7)),
+            vol.Required("led_number"): vol.All(vol.Coerce(int), vol.Range(0, 6)),
             vol.Required("effect_type"): vol.In(
                 InovelliConfigEntityChannel.LEDEffectType.__members__.keys()
             ),
```

### Fix 2: b4a203c3c706 (2022-10-16) · pull request #80446: Add friendly name to ZHA identify button

Pull-request labels: Hacktoberfest, cla-signed, integration: zha, small-pr, has-tests, bugfix, Quality Scale: No score

Commit message:

```
Add friendly name to ZHA identify button (#80446)
```

Pull-request description:

```
## Proposed change
This adds a friendly name to the ZHA diagnostic identify button.
I've chosen just "Identify" instead of "Identify button", as the domain of the entity in HA is already ``button.`` and other friendly names are named similarly (so they have no explicit type at the end of the name).

#### With the changes:
![image](https://user-images.githubusercontent.com/6409465/196054864-8ef61414-817e-420e-9be1-e0800c2c6b5d.png)

#### Previously:
![image](https://user-images.githubusercontent.com/6409465/196054891-ca8c65e8-e47a-4cf1-a471-09fe8d418912.png)

## Type of change

- [ ] Dependency upgrade
- [x] Bugfix (non-breaking change which fixes an issue)
- [ ] New integration (thank you!)
- [ ] New feature (which adds functionality to an existing integration)
- [ ] Deprecation (breaking change to happen in the future)
- [ ] Breaking change (fix/feature causing existing functionality to break)
- [ ] Code quality improvements to existing code or addition of tests

## Additional information

- This PR fixes or closes issue: fixes #
- This PR is related to issue: 
- Link to documentation pull request: 

## Checklist

- [x] The code change is tested and works locally.
- [x] Local test
[... cut ...]
```

This fix changes 3 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `tests/components/zha/test_device_action.py`: `"entity_id": "button.inovelli_vzm31_sn_identifybutton",`

Patch of `tests/components/zha/test_device_action.py` in this fix:

```diff
@@ -183,7 +183,7 @@ async def test_get_inovelli_actions(hass, device_inovelli):
         {
             "device_id": inovelli_reg_device.id,
             "domain": Platform.BUTTON,
-            "entity_id": "button.inovelli_vzm31_sn_identifybutton",
+            "entity_id": "button.inovelli_vzm31_sn_identify",
             "metadata": {"secondary": True},
             "type": "press",
         },
```

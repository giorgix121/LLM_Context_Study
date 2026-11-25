# case092: home-assistant/core 82151bfd40f7

Sampled file (the only file the models saw): `homeassistant/components/hassio/handler.py` · committed 2022-10-31 04:57:54-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Create repairs for unsupported and unhealthy (#80747)
```

## Diff of the sampled file

```diff
@@ -190,6 +190,14 @@ class HassIO:
         """
         return self.send_command(f"/discovery/{uuid}", method="get")
 
+    @api_data
+    def get_resolution_info(self):
+        """Return data for Supervisor resolution center.
+
+        This method return a coroutine.
+        """
+        return self.send_command("/resolution/info", method="get")
+
     @_api_bool
     async def update_hass_api(self, http_config, refresh_token):
         """Update Home Assistant API data on Hass.io."""
```

## Other files changed by this commit (13)

- `homeassistant/components/hassio/__init__.py` (+6 −0)
- `homeassistant/components/hassio/const.py` (+16 −5)
- `homeassistant/components/hassio/repairs.py` (+138 −0)
- `homeassistant/components/hassio/strings.json` (+10 −0)
- `tests/components/hassio/test_binary_sensor.py` (+13 −0)
- `tests/components/hassio/test_diagnostics.py` (+13 −0)
- `tests/components/hassio/test_init.py` (+28 −15)
- `tests/components/hassio/test_repairs.py` (+395 −0)
- `tests/components/hassio/test_sensor.py` (+13 −0)
- `tests/components/hassio/test_update.py` (+13 −0)
- `tests/components/hassio/test_websocket_api.py` (+13 −0)
- `tests/components/http/test_ban.py` (+11 −1)
- `tests/components/onboarding/test_views.py` (+13 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 0bfb0c25f6ff (2022-11-02) · pull request #81387: Improve supervisor repairs

Pull-request labels: core, cla-signed, integration: hassio, cherry-picked, has-tests, bugfix, Quality Scale: internal

Commit message:

```
Improve supervisor repairs (#81387)

Co-authored-by: Paulus Schoutsen <balloob@gmail.com>
```

Pull-request description:

```
<!--
  You are amazing! Thanks for contributing to our project!
  Please, DO NOT DELETE ANY TEXT from this template! (unless instructed).
-->
## Proposed change
The repairs from supervisor are too generic. Add some detail in each based on the unsupported/unhealthy reason beyond just the link.

Additionally there is one unsupported reason also marks the system as unhealthy and contains no additional information beyond the unhealthy one (`privileged`). Only create one repair for that one.

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

## Additional informatio
[... cut ...]
```

This fix changes 4 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `homeassistant/components/hassio/repairs.py`: `for fixed in self.unsupported_reasons - reasons:`; `for unsupported in reasons - self.unsupported_reasons:`; `translation_key="unhealthy",`; `translation_key="unsupported",`; `translation_placeholders={"reason": unhealthy},`; `translation_placeholders={"reason": unsupported},`
- in `homeassistant/components/hassio/strings.json`: `"description": "System is currently unhealthy due to '{reason}'. Use the link to learn more about what is wrong and how to fix it."`; `"description": "System is unsupported due to '{reason}'. Use the link to learn more about what this means and how to return to a supported system."`
- in `tests/components/hassio/test_repairs.py`: `"reason": reason,`; `"translation_key": repair_type,`; `"translation_placeholders": {`; `},`

Patch of `homeassistant/components/hassio/repairs.py` in this fix:

```diff
@@ -36,6 +36,39 @@
 INFO_URL_UNHEALTHY = "https://www.home-assistant.io/more-info/unhealthy"
 INFO_URL_UNSUPPORTED = "https://www.home-assistant.io/more-info/unsupported"
 
+UNSUPPORTED_REASONS = {
+    "apparmor",
+    "connectivity_check",
+    "content_trust",
+    "dbus",
+    "dns_server",
+    "docker_configuration",
+    "docker_version",
+    "cgroup_version",
+    "job_conditions",
+    "lxc",
+    "network_manager",
+    "os",
+    "os_agent",
+    "restart_policy",
+    "software",
+    "source_mods",
+    "supervisor_version",
+    "systemd",
+    "systemd_journal",
+    "systemd_resolved",
+}
+# Some unsupported reasons also mark the system as unhealthy. If the unsupported reason
+# provides no additional information beyond the unhealthy one then skip that repair.
+UNSUPPORTED_SKIP_REPAIR = {"privileged"}
+UNHEALTHY_REASONS = {
+    "docker",
+    "supervisor",
+    "setup",
+    "privileged",
+    "untrusted",
+}
+
 
 class SupervisorRepairs:
     """Create repairs from supervisor events."""
@@ -56,15 +89,22 @@ def unhealthy_reasons(self) -> set[str]:
     def unhealthy_reasons(self, reasons: set[str]) -> None:
         """Set unhealthy reasons. Create or delete repairs as necessary."""
         for unhealthy in reasons - self.unhealthy_reasons:
+            if unhealthy in UNHEALTHY_REASONS:
+                translation_key = f"unhealthy_{unhealthy}"
+                translation_placeholders = None
+            else:
+                translation_key = "unhealthy"
+                translation_placeholders = {"reason": unhealthy}
+
             async_create_issue(
                 self._hass,
                 DOMAIN,
                 f"{ISSUE_ID_UNHEALTHY}_{unhealthy}",
                 is_fixable=False,
                 learn_more_url=f"{INFO_URL_UNHEALTHY}/{unhealthy}",
                 severity=IssueSeverity.CRITICAL,
-                translation_key="unhealthy",
-                translation_placeholders={"reason": unhealthy},
+                translation_key=translation_key,
+                translation_placeholders=translation_placeholders,
             )
 
         for fixed in self.unhealthy_reasons - reasons:
@@ -80,19 +120,26 @@ def unsuppo
[... cut ...]
```

Patch of `homeassistant/components/hassio/strings.json` in this fix:

```diff
@@ -19,11 +19,111 @@
   "issues": {
     "unhealthy": {
       "title": "Unhealthy system - {reason}",
-      "description": "System is currently unhealthy due to '{reason}'. Use the link to learn more about what is wrong and how to fix it."
+      "description": "System is currently unhealthy due to {reason}. Use the link to learn more and how to fix this."
+    },
+    "unhealthy_docker": {
+      "title": "Unhealthy system - Docker misconfigured",
+      "description": "System is currently unhealthy because Docker is configured incorrectly. Use the link to learn more and how to fix this."
+    },
+    "unhealthy_supervisor": {
+      "title": "Unhealthy system - Supervisor update failed",
+      "description": "System is currently unhealthy because an attempt to update Supervisor to the latest version has failed. Use the link to learn more and how to fix this."
+    },
+    "unhealthy_setup": {
+      "title": "Unhealthy system - Setup failed",
+      "description": "System is currently unhealthy because setup failed to complete. There are a number of reasons this can occur, use the link to learn more and how to fix this."
+    },
+    "unhealthy_privileged": {
+      "title": "Unhealthy system - Not privileged",
+      "description": "System is currently unhealthy because it does not have privileged access to the docker runtime. Use the link to learn more and how to fix this."
+    },
+    "unhealthy_untrusted": {
+      "title": "Unhealthy system - Untrusted code",
+      "description": "System is currently unhealthy because it has detected untrusted code or images in use. Use the link to learn more and how to fix this."
     },
     "unsupported": {
       "title": "Unsupported system - {reason}",
-      "description": "System is unsupported due to '{reason}'. Use the link to learn more about what this means and how to return to a supported system."
+      "description": "System is unsupported due to {reason}. Use the link to learn more and how to fix this."
+    },
+    "unsupported_apparmor": {
+      "title": "Unsupported system - AppArmor issues",
+      "description": "System is unsupported because AppArmor is working incorrectly and add-ons are runni
[... cut ...]
```

Patch of `tests/components/hassio/test_repairs.py` in this fix:

```diff
@@ -140,10 +140,8 @@ def assert_repair_in_list(issues: list[dict[str, Any]], unhealthy: bool, reason:
         "issue_domain": None,
         "learn_more_url": f"https://www.home-assistant.io/more-info/{repair_type}/{reason}",
         "severity": "critical" if unhealthy else "warning",
-        "translation_key": repair_type,
-        "translation_placeholders": {
-            "reason": reason,
-        },
+        "translation_key": f"{repair_type}_{reason}",
+        "translation_placeholders": None,
     } in issues
 
 
@@ -393,3 +391,74 @@ async def test_reasons_added_and_removed(
     assert_repair_in_list(
         msg["result"]["issues"], unhealthy=False, reason="content_trust"
     )
+
+
+async def test_ignored_unsupported_skipped(
+    hass: HomeAssistant,
+    aioclient_mock: AiohttpClientMocker,
+    hass_ws_client,
+):
+    """Unsupported reasons which have an identical unhealthy reason are ignored."""
+    mock_resolution_info(
+        aioclient_mock, unsupported=["privileged"], unhealthy=["privileged"]
+    )
+
+    result = await async_setup_component(hass, "hassio", {})
+    assert result
+
+    client = await hass_ws_client(hass)
+
+    await client.send_json({"id": 1, "type": "repairs/list_issues"})
+    msg = await client.receive_json()
+    assert msg["success"]
+    assert len(msg["result"]["issues"]) == 1
+    assert_repair_in_list(msg["result"]["issues"], unhealthy=True, reason="privileged")
+
+
+async def test_new_unsupported_unhealthy_reason(
+    hass: HomeAssistant,
+    aioclient_mock: AiohttpClientMocker,
+    hass_ws_client,
+):
+    """New unsupported/unhealthy reasons result in a generic repair until next core update."""
+    mock_resolution_info(
+        aioclient_mock, unsupported=["fake_unsupported"], unhealthy=["fake_unhealthy"]
+    )
+
+    result = await async_setup_component(hass, "hassio", {})
+    assert result
+
+    client = await hass_ws_client(hass)
+
+    await client.send_json({"id": 1, "type": "repairs/list_issues"})
+    msg = await client.receive_json()
+    assert msg["success"]
+    assert len(msg["result"]["issues"]) == 2
+    assert {
+        "breaks_in_ha_version": None,
+        "created": ANY,
+
[... cut ...]
```

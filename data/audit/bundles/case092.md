# case092: home-assistant/core 82151bfd40f7

File: `homeassistant/components/hassio/handler.py` · committed 2022-10-31 04:57:54-01:00 · SZZ label: RISKY

## Commit message

```
Create repairs for unsupported and unhealthy (#80747)
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
  193      @api_data
  194      def get_resolution_info(self):
  195          """Return data for Supervisor resolution center.
  196  
  197          This method return a coroutine.
  198          """
  199          return self.send_command("/resolution/info", method="get")
  200  
```

## Candidate fixes (1 later commits to this file remove a blamed line; 7 later commits up to 2023-06-30 checked)

### Candidate 1: 052145fabd49 (2023-01-23)

Message:

```
Fix grammar in some hassio docstrings (#86458)
```

Removed blamed lines: `This method return a coroutine.`

Patch of this file:

```diff
@@ -267,31 +267,31 @@ def __init__(
     def is_connected(self):
         """Return true if it connected to Hass.io supervisor.
 
-        This method return a coroutine.
+        This method returns a coroutine.
         """
         return self.send_command("/supervisor/ping", method="get", timeout=15)
 
     @api_data
     def get_info(self):
         """Return generic Supervisor information.
 
-        This method return a coroutine.
+        This method returns a coroutine.
         """
         return self.send_command("/info", method="get")
 
     @api_data
     def get_host_info(self):
         """Return data for Host.
 
-        This method return a coroutine.
+        This method returns a coroutine.
         """
         return self.send_command("/host/info", method="get")
 
     @api_data
     def get_os_info(self):
         """Return data for the OS.
 
-        This method return a coroutine.
+        This method returns a coroutine.
         """
         return self.send_command("/os/info", method="get")
 
@@ -315,7 +315,7 @@ def get_supervisor_info(self):
     def get_addon_info(self, addon):
         """Return data for a Add-on.
 
-        This method return a coroutine.
+        This method returns a coroutine.
         """
         return self.send_command(f"/addons/{addon}/info", method="get")
 
@@ -340,63 +340,63 @@ def get_addon_changelog(self, addon):
     def get_store(self):
         """Return data from the store.
 
-        This method return a coroutine.
+        This method returns a coroutine.
         """
         return self.send_command("/store", method="get")
 
     @api_data
     def get_ingress_panels(self):
         """Return data for Add-on ingress panels.
 
-        This method return a coroutine.
+        This method returns a coroutine.
         """
         return self.send_command("/ingress/panels", method="get")
 
     @_api_bool
     def restart_homeassistant(self):
         """Restart Home-Assistant container.
 
-        This method return a coroutine.
+        This method returns a coroutine.
         """
         return self.send_command("/homeassistant/restart")
 
     @_api_bool
     def stop_homeassistant(self):
         """Stop Home-Assistant container.
 
-        This method return a coroutine.
+        This method returns a coroutine.
         """
         return self.send_command("/homeassistant/stop")
 
     @_api_bool
     def refresh_updates(self):
         """Refresh available updates.
 
-        This method return a coroutine.
+        This method returns a coroutine.
         """
         return self.send_command("/refresh_updates", timeout=None)
 
     @api_data
     def retrieve_discovery_messages(self):
         """Return all discovery data from Hass.io API.
 
-        This method return a coroutine.
+        This method returns a coroutine.
         """
         return self.send_command("/discovery", method="get", timeout=60)
 
     @api_data
     def get_discovery_message(self, uuid):
         """Return a single discovery data message.
 
-        This method return a coroutine.
+        This method returns a coroutine.
         """
         return self.send_command(f"/discovery/{uuid}", method="get")
 
     @api_data
     def get_resolution_info(self):
         """Return data for Supervisor resolution center.
 
-        This method return a coroutine.
+        This method returns a coroutine.
         """
         return self.send_command("/resolution/info", method="get")
 
@@ -424,15 +424,15 @@ async def update_hass_api(self, http_config, refresh_token):
     def update_hass_timezone(self, timezone):
         """Update Home-Assistant timezone data on Hass.io.
 
-        This method return a coroutine.
+        This method returns a coroutine.
         """
         return self.send_command("/supervisor/options", payload={"timezone": timezone})
 
     @_api_bool
     def update_diagnostics(self, diagnostics: bool):
         """Update Supervisor diagnostics setting.
 
-        This method return a coroutine.
+        This method returns a coroutine.
         """
         return self.send_command(
             "/supervisor/options", payload={"diagnostics": diagnostics}
```

# case133: home-assistant/core 2ed48a9b28f1

File: `homeassistant/components/zha/entity.py` · committed 2022-09-28 09:22:39-01:00 · SZZ label: RISKY

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

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
   69          if hasattr(self, "_attr_name") and self._attr_name is not None:
   70              return self._attr_name
```

## Candidate fixes (1 later commits to this file remove a blamed line; 6 later commits up to 2023-06-30 checked)

### Candidate 1: 6842cdcb65c6 (2023-04-25)

Message:

```
Clean up default ZHA entity names (#91841)

* Always use `Light` for lights, including subclasses

* Clean up other platforms

* Add a unit test to ensure all future entity classes have names

* Remove stale `_name`

* Address review feedback and rename `Open` to `Opening`
```

Removed blamed lines: `if hasattr(self, "_attr_name") and self._attr_name is not None:`; `return self._attr_name`

Patch of this file:

```diff
@@ -52,7 +52,6 @@ class BaseZhaEntity(LogMixin, entity.Entity):
 
     def __init__(self, unique_id: str, zha_device: ZHADevice, **kwargs: Any) -> None:
         """Init ZHA entity."""
-        self._name: str = ""
         self._unique_id: str = unique_id
         if self.unique_id_suffix:
             self._unique_id += f"-{self.unique_id_suffix}"
@@ -62,13 +61,6 @@ def __init__(self, unique_id: str, zha_device: ZHADevice, **kwargs: Any) -> None
         self._unsubs: list[Callable[[], None]] = []
         self.remove_future: asyncio.Future[Any] = asyncio.Future()
 
-    @property
-    def name(self) -> str:
-        """Return Entity's default name."""
-        if hasattr(self, "_attr_name") and self._attr_name is not None:
-            return self._attr_name
-        return self._name
-
     @property
     def unique_id(self) -> str:
         """Return a unique ID."""
@@ -167,13 +159,7 @@ def __init__(
     ) -> None:
         """Init ZHA entity."""
         super().__init__(unique_id, zha_device, **kwargs)
-        self._name: str = (
-            self.__class__.__name__.lower()
-            .replace("zha", "")
-            .replace("entity", "")
-            .replace("sensor", "")
-            .capitalize()
-        )
+
         self.cluster_handlers: dict[str, ClusterHandler] = {}
         for cluster_handler in cluster_handlers:
             self.cluster_handlers[cluster_handler.name] = cluster_handler
@@ -249,6 +235,9 @@ async def async_update(self) -> None:
 class ZhaGroupEntity(BaseZhaEntity):
     """A base class for ZHA group entities."""
 
+    # The group name is set in the initializer
+    _attr_name: str
+
     def __init__(
         self,
         entity_ids: list[str],
@@ -261,16 +250,15 @@ def __init__(
         super().__init__(unique_id, zha_device, **kwargs)
         self._available = False
         self._group = zha_device.gateway.groups.get(group_id)
-        self._name = (
-            f"{self._group.name}_zha_group_0x{group_id:04x}".lower().capitalize()
-        )
         self._group_id: int = group_id
         self._entity_ids: list[str] = entity_ids
         self._async_unsub_state_changed: CALLBACK_TYPE | None = None
         self._handled_group_membership = False
         self._change_listener_debouncer: Debouncer | None = None
         self._update_group_from_child_delay = DEFAULT_UPDATE_GROUP_FROM_CHILD_DELAY
 
+        self._attr_name = self._group.name
+
     @property
     def available(self) -> bool:
         """Return entity availability."""
```

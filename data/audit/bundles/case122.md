# case122: Lightning-AI/lightning d013bcc5bf23

File: `src/pytorch_lightning/accelerators/cpu.py` · committed 2022-09-12 15:00:14-01:00 · SZZ label: RISKY

## Commit message

```
Standalone Lite: Accelerators (#14578)

Co-authored-by: Carlos Mocholí <carlossmocholi@gmail.com>
Co-authored-by: Jirka Borovec <Borda@users.noreply.github.com>
```

## Diff of the target file

```diff
@@ -25,20 +25,22 @@ from pytorch_lightning.utilities.imports import _PSUTIL_AVAILABLE
 class CPUAccelerator(Accelerator):
     """Accelerator for CPU devices."""
 
-    def setup_environment(self, root_device: torch.device) -> None:
+    def setup_device(self, device: torch.device) -> None:
         """
         Raises:
             MisconfigurationException:
                 If the selected device is not CPU.
         """
-        super().setup_environment(root_device)
-        if root_device.type != "cpu":
-            raise MisconfigurationException(f"Device should be CPU, got {root_device} instead.")
+        if device.type != "cpu":
+            raise MisconfigurationException(f"Device should be CPU, got {device} instead.")
 
     def get_device_stats(self, device: _DEVICE) -> Dict[str, Any]:
         """Get CPU stats from ``psutil`` package."""
         return get_cpu_stats()
 
+    def teardown(self) -> None:
+        pass
+
     @staticmethod
     def parse_devices(devices: Union[int, str, List[int]]) -> int:
         """Accelerator device parsing logic."""
```

## Lines SZZ blamed (line numbers in the new version)

```
   28      def setup_device(self, device: torch.device) -> None:
   34          if device.type != "cpu":
   35              raise MisconfigurationException(f"Device should be CPU, got {device} instead.")
   41      def teardown(self) -> None:
   42          pass
   43  
```

## Candidate fixes (0 later commits to this file remove a blamed line; 5 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

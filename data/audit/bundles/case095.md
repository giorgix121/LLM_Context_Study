# case095: Lightning-AI/lightning bd658441bd01

File: `src/lightning_app/utilities/packaging/cloud_compute.py` · committed 2022-10-25 04:24:20-01:00 · SZZ label: RISKY

## Commit message

```
[App] testing `lightning` in `lightning-app` package (#15286)

* hot fix

* update

* update

* update

* cmd

* pkg

* update

* Apply suggestions from code review

* update

* update

* Apply suggestions from code review

* update

* update

* update

* update

* update

* update

* update

* update

* update

* update

* update

* update

* update

* update

* cleaning

* Apply suggestions from code review

* update

* update

Co-authored-by: Jirka <jirka.borovec@seznam.cz>
Co-authored-by: Jirka Borovec <Borda@users.noreply.github.com>
```

## Diff of the target file

```diff
@@ -84,6 +84,9 @@ class CloudCompute:
         if self._internal_id is None:
             self._internal_id = "default" if self.name == "default" else uuid4().hex[:7]
 
+        # Internal arguments for now.
+        self.preemptible = False
+
     def to_dict(self) -> dict:
         _verify_mount_root_dirs_are_unique(self.mounts)
         return {"type": __CLOUD_COMPUTE_IDENTIFIER__, **asdict(self)}
```

## Lines SZZ blamed (line numbers in the new version)

```
   87          # Internal arguments for now.
   88          self.preemptible = False
   89  
```

## Candidate fixes (1 later commits to this file remove a blamed line; 5 later commits up to 2023-06-30 checked)

### Candidate 1: b8eaabe3c983 (2023-01-25)

Message:

```
[App] Add interruptible work (#16399)

Co-authored-by: thomas <thomas@thomass-MacBook-Pro.local>
Co-authored-by: Your Name <you@example.com>
Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
```

Removed blamed lines: `# Internal arguments for now.`; `self.preemptible = False`

Patch of this file:

```diff
@@ -16,7 +16,7 @@
 from typing import Dict, List, Optional, Tuple, Union
 from uuid import uuid4
 
-from lightning_app.core.constants import ENABLE_MULTIPLE_WORKS_IN_NON_DEFAULT_CONTAINER
+from lightning_app.core.constants import enable_interruptible_works, ENABLE_MULTIPLE_WORKS_IN_NON_DEFAULT_CONTAINER
 from lightning_app.storage.mount import Mount
 
 __CLOUD_COMPUTE_IDENTIFIER__ = "__cloud_compute__"
@@ -80,13 +80,18 @@ class CloudCompute:
             For example 1100 will become 1024. If set to zero (the default) will get the default 64MiB inside docker.
 
         mounts: External data sources which should be mounted into a work as a filesystem at runtime.
+
+        interruptible: Whether to run on a interruptible machine e.g the machine can be stopped
+            at any time by the providers. This is also known as spot or preemptible machines.
+            Compared to on-demand machines, they tend to be cheaper.
     """
 
     name: str = "default"
     disk_size: int = 0
     idle_timeout: Optional[int] = None
     shm_size: Optional[int] = None
     mounts: Optional[Union[Mount, List[Mount]]] = None
+    interruptible: bool = False
     _internal_id: Optional[str] = None
 
     def __post_init__(self) -> None:
@@ -100,13 +105,19 @@ def __post_init__(self) -> None:
             else:
                 self.shm_size = 0
 
+        if self.interruptible:
+            if not enable_interruptible_works():
+                raise ValueError("CloudCompute with `interruptible=True` isn't supported yet.")
+            if "gpu" not in self.name:
+                raise ValueError("CloudCompute `interruptible=True` is supported only with GPU.")
+
+        # TODO: Remove from the platform first.
+        self.preemptible = self.interruptible
+
         # All `default` CloudCompute are identified in the same way.
         if self._internal_id is None:
             self._internal_id = self._generate_id()
 
-        # Internal arguments for now.
-        self.preemptible = False
-
     def to_dict(self) -> dict:
         _verify_mount_root_dirs_are_unique(self.mounts)
         return {"type": __CLOUD_COMPUTE_IDENTIFIER__, **asdict(self)}
```

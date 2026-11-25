# case016: Lightning-AI/lightning e5998e6bf216

File: `src/pytorch_lightning/trainer/connectors/signal_connector.py` · committed 2022-09-12 18:24:35-01:00 · SZZ label: RISKY

## Commit message

```
Make the SLURM Preemption/Timeout Signal Configurable (#14626)

* Add parameter to change the preemption signal
* Make the signal connector use the custom signal from SLURMEnvironment

Signed-off-by: Max Ehrlich <max.ehr@gmail.com>
Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
Co-authored-by: Adrian Wälchli <aedu.waelchli@gmail.com>
```

## Diff of the target file

```diff
@@ -42,7 +42,7 @@ class SignalConnector:
     def register_signal_handlers(self) -> None:
         self._original_handlers = self._get_current_signal_handlers()
 
-        sigusr1_handlers: List[_HANDLER] = []
+        sigusr_handlers: List[_HANDLER] = []
         sigterm_handlers: List[_HANDLER] = []
 
         if _fault_tolerant_training():
@@ -51,19 +51,23 @@ class SignalConnector:
         environment = self.trainer._accelerator_connector.cluster_environment
         if isinstance(environment, SLURMEnvironment) and environment.auto_requeue:
             log.info("SLURM auto-requeueing enabled. Setting signal handlers.")
-            sigusr1_handlers.append(self.slurm_sigusr1_handler_fn)
+            sigusr_handlers.append(self.slurm_sigusr_handler_fn)
             sigterm_handlers.append(self.sigterm_handler_fn)
 
-        # signal.SIGUSR1 doesn't seem available on windows
+        # Windows seems to have signal incompatibilities
         if not self._is_on_windows():
-            if sigusr1_handlers and not self._has_already_handler(signal.SIGUSR1):
-                self._register_signal(signal.SIGUSR1, HandlersCompose(sigusr1_handlers))
+            sigusr = environment.requeue_signal if isinstance(environment, SLURMEnvironment) else signal.SIGUSR1
+
+            assert sigusr is not None
+
+            if sigusr_handlers and not self._has_already_handler(sigusr):
+                self._register_signal(sigusr, HandlersCompose(sigusr_handlers))
 
             if sigterm_handlers and not self._has_already_handler(signal.SIGTERM):
                 self._register_signal(signal.SIGTERM, HandlersCompose(sigterm_handlers))
 
-    def slurm_sigusr1_handler_fn(self, signum: _SIGNUM, frame: FrameType) -> None:
-        rank_zero_info("handling SIGUSR1")
+    def slurm_sigusr_handler_fn(self, signum: _SIGNUM, frame: FrameType) -> None:
+        rank_zero_info("handling auto-requeue signal")
 
         # save logger to make sure we get all the metrics
         for logger in self.trainer.loggers:
```

## Lines SZZ blamed (line numbers in the new version)

```
   45          sigusr_handlers: List[_HANDLER] = []
   54              sigusr_handlers.append(self.slurm_sigusr_handler_fn)
   57          # Windows seems to have signal incompatibilities
   59              sigusr = environment.requeue_signal if isinstance(environment, SLURMEnvironment) else signal.SIGUSR1
   60  
   61              assert sigusr is not None
   62  
   63              if sigusr_handlers and not self._has_already_handler(sigusr):
   64                  self._register_signal(sigusr, HandlersCompose(sigusr_handlers))
   69      def slurm_sigusr_handler_fn(self, signum: _SIGNUM, frame: FrameType) -> None:
   70          rank_zero_info("handling auto-requeue signal")
```

## Candidate fixes (1 later commits to this file remove a blamed line; 8 later commits up to 2023-06-30 checked)

### Candidate 1: 9f8043e16f2e (2023-01-31)

Message:

```
Cascade SIGTERM to subprocesses (#16525)
```

Removed blamed lines: `def slurm_sigusr_handler_fn(self, signum: _SIGNUM, frame: FrameType) -> None:`; `rank_zero_info("handling auto-requeue signal")`; `sigusr_handlers.append(self.slurm_sigusr_handler_fn)`

Patch of this file:

```diff
@@ -7,6 +7,8 @@
 from types import FrameType
 from typing import Any, Callable, Dict, List, Set, Union
 
+from lightning_utilities.core.rank_zero import rank_prefixed_message
+
 import pytorch_lightning as pl
 from lightning_fabric.plugins.environments import SLURMEnvironment
 from lightning_fabric.utilities.imports import _IS_WINDOWS
@@ -50,8 +52,8 @@ def register_signal_handlers(self) -> None:
         environment = self.trainer._accelerator_connector.cluster_environment
         if isinstance(environment, SLURMEnvironment) and environment.auto_requeue:
             log.info("SLURM auto-requeueing enabled. Setting signal handlers.")
-            sigusr_handlers.append(self.slurm_sigusr_handler_fn)
-            sigterm_handlers.append(self.sigterm_handler_fn)
+            sigusr_handlers.append(self._slurm_sigusr_handler_fn)
+            sigterm_handlers.append(self._sigterm_handler_fn)
 
         # Windows seems to have signal incompatibilities
         if not self._is_on_windows():
@@ -65,8 +67,8 @@ def register_signal_handlers(self) -> None:
                 sigterm_handlers.append(signal.getsignal(signal.SIGTERM))
             self._register_signal(signal.SIGTERM, HandlersCompose(sigterm_handlers))
 
-    def slurm_sigusr_handler_fn(self, signum: _SIGNUM, frame: FrameType) -> None:
-        rank_zero_info("handling auto-requeue signal")
+    def _slurm_sigusr_handler_fn(self, signum: _SIGNUM, _: FrameType) -> None:
+        rank_zero_info(f"Handling auto-requeue signal: {signum}")
 
         # save logger to make sure we get all the metrics
         for logger in self.trainer.loggers:
@@ -103,12 +105,18 @@ def slurm_sigusr_handler_fn(self, signum: _SIGNUM, frame: FrameType) -> None:
             else:
                 log.warning("requeue failed...")
 
-    def _sigterm_notifier_fn(self, signum: _SIGNUM, frame: FrameType) -> None:
-        log.info(f"Received signal {signum}")
+    def _sigterm_notifier_fn(self, signum: _SIGNUM, _: FrameType) -> None:
+        log.info(rank_prefixed_message(f"Received SIGTERM: {signum}", self.trainer.local_rank))
+        # subprocesses killing the parent process is not supported, only the parent (rank 0) does it
+        if not self.received_sigterm:
+            # send the same signal to the subprocesses
+            launcher = self.trainer.strategy.launcher
+            if launcher is not None:
+                launcher.kill(signum)
         self.received_sigterm = True
 
-    def sigterm_handler_fn(self, signum: _SIGNUM, frame: FrameType) -> None:
-        log.info("bypassing sigterm")
+    def _sigterm_handler_fn(self, signum: _SIGNUM, _: FrameType) -> None:
+        log.info(f"Bypassing SIGTERM: {signum}")
 
     def teardown(self) -> None:
         """Restores the signals that were previously configured before :class:`SignalConnector` replaced them."""
```

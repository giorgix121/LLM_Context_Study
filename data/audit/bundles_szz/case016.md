# case016: Lightning-AI/lightning e5998e6bf216

Sampled file (the only file the models saw): `src/pytorch_lightning/trainer/connectors/signal_connector.py` · committed 2022-09-12 18:24:35-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Make the SLURM Preemption/Timeout Signal Configurable (#14626)

* Add parameter to change the preemption signal
* Make the signal connector use the custom signal from SLURMEnvironment

Signed-off-by: Max Ehrlich <max.ehr@gmail.com>
Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
Co-authored-by: Adrian Wälchli <aedu.waelchli@gmail.com>
```

## Diff of the sampled file

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

## Other files changed by this commit (4)

- `docs/source-pytorch/clouds/cluster_advanced.rst` (+12 −0)
- `src/lightning_lite/plugins/environments/slurm_environment.py` (+8 −1)
- `src/pytorch_lightning/CHANGELOG.md` (+4 −0)
- `tests/tests_pytorch/trainer/connectors/test_signal_connector.py` (+8 −6)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 4f9c7793e754 (2022-09-18) · pull request #14762: Fix TensorBoardLogger creating redundant experiment when finalizing

Pull-request labels: bug, ready to be merged, logger: tensorboard, pl

Commit message:

```
Fix TensorBoardLogger creating redundant experiment when finalizing (#14762)

Co-authored-by: Kushashwa Ravi Shrimali <kushashwaravishrimali@gmail.com>
```

Pull-request description:

```
## What does this PR do?

Unblocks #12292, as I found a bug while helping out there.

The newly added test in test_tensorboard.py illustrates the issue: When nothing is logged, no experiment exists, but the call to finalize() would create a new experiment, then close it immediately again, leaving useless summary files behind.
This PR changes this to only flush/close or create directories when an experiment actually exists. This is consistent with all other loggers. 

### Does your PR introduce any breaking changes? If yes, please list them.

I don't think so. This was a peculiar edge case I can't believe anyone would need to rely on for a serious use case. 

## Before submitting
- [x] Was this discussed/approved via a GitHub issue? (not for typos and docs)
- [x] Did you read the [contributor guideline](https://github.com/PyTorchLightning/pytorch-lightning/blob/master/.github/CONTRIBUTING.md), **Pull Request** section?
- [x] Did you make sure your PR does only one thing, instead of bundling different changes together?
- [x] Did you make sure to update the documentation with your changes? (if necessary)
- [x] Did you write any new necessary tests? (not for typos and docs)
- [x] Did y
[... cut ...]
```

This fix changes 4 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/pytorch_lightning/CHANGELOG.md`: `- Added an option to configure the signal SLURM sends when a job is preempted or requeued ([#14610](https://github.com/Lightning-AI/lightning/issues/14610))`

Patch of `src/pytorch_lightning/CHANGELOG.md` in this fix:

```diff
@@ -7,9 +7,6 @@ The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).
 ## [unReleased] - 2022-MM-DD
 
 
-- Added an option to configure the signal SLURM sends when a job is preempted or requeued ([#14610](https://github.com/Lightning-AI/lightning/issues/14610))
-
-
 ### Added
 
 
@@ -40,6 +37,9 @@ The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).
 - Added `WandbLogger.download_artifact` and `WandbLogger.use_artifact` for managing artifacts with Weights and Biases ([#14551](https://github.com/Lightning-AI/lightning/issues/14551))
 
 
+- Added an option to configure the signal SLURM sends when a job is preempted or requeued ([#14610](https://github.com/Lightning-AI/lightning/issues/14610))
+
+
 ### Changed
 
 - The `Trainer.{fit,validate,test,predict,tune}` methods now raise a useful error message if the input is not a `LightningModule` ([#13892](https://github.com/Lightning-AI/lightning/pull/13892))
@@ -186,6 +186,10 @@ The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).
 - Fixed torchscript error with ensembles of LightningModules ([#14657](https://github.com/Lightning-AI/lightning/pull/14657), [#14724](https://github.com/Lightning-AI/lightning/pull/14724))
 
 
+- Fixed an issue with `TensorBoardLogger.finalize` creating a new experiment when none was created during the Trainer's execution ([#14762](https://github.com/Lightning-AI/lightning/pull/14762))
+
+
+
 ## [1.7.6] - 2022-09-13
 
 ### Changed
```

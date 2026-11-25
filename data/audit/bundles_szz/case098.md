# case098: Lightning-AI/lightning 4322f538746f

Sampled file (the only file the models saw): `src/lightning_lite/wrappers.py` · committed 2022-10-23 00:26:43-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Update mypy version (#15161)

* update mypy version
* type-ignore-comments
* more mypy-fix
* import-fix
* Update Lite too
* simpler implementation for flatten dict
* Fix rich progress
* Simplify rich test
* True None

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
Co-authored-by: Carlos Mocholí <carlossmocholi@gmail.com>
```

## Diff of the sampled file

```diff
@@ -112,12 +112,12 @@ class _LiteModule(_DeviceDtypeModuleMixin):
         ...
 
     @overload
-    def state_dict(self, *, prefix: str = ..., keep_vars: bool = ...) -> T_destination:
+    def state_dict(self, *, prefix: str = ..., keep_vars: bool = ...) -> Dict[str, Any]:
         ...
 
     def state_dict(
         self, destination: Optional[T_destination] = None, prefix: str = "", keep_vars: bool = False
-    ) -> Optional[T_destination]:
+    ) -> Optional[Dict[str, Any]]:
         return self._original_module.state_dict(
             destination=destination,  # type: ignore[type-var]
             prefix=prefix,
```

## Other files changed by this commit (29)

- `.github/workflows/code-checks.yml` (+1 −1)
- `src/lightning_lite/lite.py` (+1 −1)
- `src/pytorch_lightning/callbacks/progress/rich_progress.py` (+10 −14)
- `src/pytorch_lightning/core/module.py` (+1 −1)
- `src/pytorch_lightning/core/saving.py` (+1 −0)
- `src/pytorch_lightning/demos/boring_classes.py` (+7 −7)
- `src/pytorch_lightning/lite/lite.py` (+11 −10)
- `src/pytorch_lightning/loggers/comet.py` (+1 −1)
- `src/pytorch_lightning/loggers/csv_logs.py` (+1 −1)
- `src/pytorch_lightning/loggers/mlflow.py` (+1 −1)
- `src/pytorch_lightning/loggers/neptune.py` (+2 −2)
- `src/pytorch_lightning/loggers/tensorboard.py` (+1 −1)
- `src/pytorch_lightning/loggers/wandb.py` (+1 −1)
- `src/pytorch_lightning/loops/batch/training_batch_loop.py` (+2 −2)
- `src/pytorch_lightning/loops/dataloader/prediction_loop.py` (+1 −1)
- `src/pytorch_lightning/loops/epoch/evaluation_epoch_loop.py` (+2 −4)
- `src/pytorch_lightning/loops/epoch/prediction_epoch_loop.py` (+2 −2)
- `src/pytorch_lightning/loops/epoch/training_epoch_loop.py` (+2 −2)
- `src/pytorch_lightning/loops/fit_loop.py` (+3 −3)
- `src/pytorch_lightning/loops/optimization/manual_loop.py` (+1 −1)
- `src/pytorch_lightning/loops/optimization/optimizer_loop.py` (+2 −4)
- `src/pytorch_lightning/profilers/pytorch.py` (+1 −0)
- `src/pytorch_lightning/trainer/connectors/logger_connector/result.py` (+1 −1)
- `src/pytorch_lightning/tuner/lr_finder.py` (+3 −9)
- `src/pytorch_lightning/utilities/logger.py` (+11 −18)
- `src/pytorch_lightning/utilities/parameter_tying.py` (+1 −5)
- `tests/tests_pytorch/callbacks/progress/test_rich_progress_bar.py` (+6 −2)
- `tests/tests_pytorch/loggers/test_wandb.py` (+1 −1)
- `tests/tests_pytorch/utilities/test_logger.py` (+2 −2)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 6b0d41cb8a28 (2022-10-29) · pull request #15376: Fix issues when RichProgressBar disabled

Pull-request labels: bug, ready to be merged, progress bar: rich, pl

Commit message:

```
Fix issues when RichProgressBar disabled (#15376)
```

Pull-request description:

```
## What does this PR do?

Fixes issues found in #15321. When disabling the progress bar and using it in the Trainer, we get assertion errors and NoneType attribute errors. The added test reproduces several issues. 

Q: When do we have a disabled progress bar in the trainer?
A: When running with DDP, we internally call `progress_bar.disable()` on rank > 0 to avoid showing a bar for each process.

This PR fixes RichProgressBar in combination with DDP and other multi-process strategies.

### Does your PR introduce any breaking changes? If yes, please list them.
No.

## Before submitting
- [x] Was this discussed/approved via a GitHub issue? (not for typos and docs)
- [x] Did you read the [contributor guideline](https://github.com/PyTorchLightning/pytorch-lightning/blob/master/.github/CONTRIBUTING.md), **Pull Request** section?
- [x] Did you make sure your PR does only one thing, instead of bundling different changes together?
- [x] Did you make sure to update the documentation with your changes? (if necessary)
- [x] Did you write any new necessary tests? (not for typos and docs)
- [x] Did you verify new and existing tests pass locally with your changes?
- [x] Did you update the [CHANGE
[... cut ...]
```

This fix changes 3 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/pytorch_lightning/callbacks/progress/rich_progress.py`: `assert self.progress is not None`; `if not self.has_dataloader_changed(dataloader_idx) or self.progress is None:`

Patch of `src/pytorch_lightning/callbacks/progress/rich_progress.py` in this fix:

```diff
@@ -255,9 +255,9 @@ def __init__(
         self._console: Optional[Console] = None
         self._console_kwargs = console_kwargs or {}
         self._enabled: bool = True
-        self.progress: Optional[Progress] = None
-        self.val_sanity_progress_bar_id: Optional["TaskID"] = None
+        self.progress: Optional[CustomProgress] = None
         self.main_progress_bar_id: Optional["TaskID"]
+        self.val_sanity_progress_bar_id: Optional["TaskID"] = None
         self.val_progress_bar_id: Optional["TaskID"]
         self.test_progress_bar_id: Optional["TaskID"]
         self.predict_progress_bar_id: Optional["TaskID"]
@@ -279,6 +279,30 @@ def is_enabled(self) -> bool:
     def is_disabled(self) -> bool:
         return not self.is_enabled
 
+    @property
+    def main_progress_bar(self) -> Task:
+        assert self.progress is not None
+        assert self.main_progress_bar_id is not None
+        return self.progress.tasks[self.main_progress_bar_id]
+
+    @property
+    def val_sanity_check_bar(self) -> Task:
+        assert self.progress is not None
+        assert self.val_sanity_progress_bar_id is not None
+        return self.progress.tasks[self.val_sanity_progress_bar_id]
+
+    @property
+    def val_progress_bar(self) -> Task:
+        assert self.progress is not None
+        assert self.val_progress_bar_id is not None
+        return self.progress.tasks[self.val_progress_bar_id]
+
+    @property
+    def test_progress_bar(self) -> Task:
+        assert self.progress is not None
+        assert self.test_progress_bar_id is not None
+        return self.progress.tasks[self.test_progress_bar_id]
+
     def _update_for_light_colab_theme(self) -> None:
         if _detect_light_colab_theme():
             attributes = ["description", "batch_progress", "metrics"]
@@ -336,6 +360,8 @@ def on_sanity_check_end(self, trainer: "pl.Trainer", pl_module: "pl.LightningMod
         self.refresh()
 
     def on_train_epoch_start(self, trainer: "pl.Trainer", pl_module: "pl.LightningModule") -> None:
+        if self.is_disabled:
+            return
         total_batches = self.total_batches_current_epoch
         train_description = self._get_train_descript
[... cut ...]
```

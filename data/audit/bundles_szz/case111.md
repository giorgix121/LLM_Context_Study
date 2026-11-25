# case111: Lightning-AI/lightning 6855f653bb82

Sampled file (the only file the models saw): `src/pytorch_lightning/loggers/csv_logs.py` · committed 2022-09-20 02:43:32-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Set `MLFlowLogger` status to FAILED when training raises an error (#12292)

Co-authored-by: Ritsuki Yamada <ritsuki.yamada@uzabase.com>
Co-authored-by: Adrian Wälchli <aedu.waelchli@gmail.com>
Co-authored-by: Jirka <jirka.borovec@seznam.cz>
Co-authored-by: Carlos Mocholí <carlossmocholi@gmail.com>
```

## Diff of the sampled file

```diff
@@ -208,6 +208,10 @@ class CSVLogger(Logger):
 
     @rank_zero_only
     def finalize(self, status: str) -> None:
+        if self._experiment is None:
+            # When using multiprocessing, finalize() should be a no-op on the main process, as no experiment has been
+            # initialized there
+            return
         self.save()
 
     @property
```

## Other files changed by this commit (9)

- `src/pytorch_lightning/CHANGELOG.md` (+4 −0)
- `src/pytorch_lightning/loggers/comet.py` (+4 −0)
- `src/pytorch_lightning/loggers/mlflow.py` (+7 −3)
- `src/pytorch_lightning/loggers/neptune.py` (+4 −0)
- `src/pytorch_lightning/loggers/tensorboard.py` (+4 −1)
- `src/pytorch_lightning/loggers/wandb.py` (+4 −1)
- `src/pytorch_lightning/trainer/trainer.py` (+4 −0)
- `tests/tests_pytorch/loggers/test_mlflow.py` (+18 −0)
- `tests/tests_pytorch/trainer/test_trainer.py` (+18 −1)

## Fix commits that the dataset links to this commit (1)

### Fix 1: dc1dc0df36cd (2022-09-22) · pull request #14631: Attempt to query device count via NVML

Pull-request labels: bug, ready to be merged, accelerator: cuda, pl

Commit message:

```
Attempt to query device count via NVML (#14631)


Co-authored-by: Carlos Mocholí <carlossmocholi@gmail.com>
```

Pull-request description:

```
## What does this PR do?

Redo of #14319 
Note: This is an enhancement/improvement of the preivous bugfix, not addressing any new bugs. 
- User does not need to set an environment variable
- Faster: no new processes need to be launched in order to evaluate the functions

This adopts the solution in https://github.com/pytorch/pytorch/pull/84879 for Lightning when running with PyTorch < 1.13. 
A minor follow-up is still pending: https://github.com/pytorch/pytorch/pull/85024

Validated with nightly pytorch 1.13 locally, using this simple script:

```py
import torch
import torch.multiprocessing as mp
from lightning_lite.utilities.imports import _TORCH_GREATER_EQUAL_1_13
from lightning_lite.utilities.device_parser import num_cuda_devices, is_cuda_available


def worker(rank):
    print("successfully forked", rank)
    torch.cuda.set_device(rank)


def run():
    print("torch version", torch.__version__)
    print("greater than 1.13?", _TORCH_GREATER_EQUAL_1_13)

    # old function
    torch.cuda.device_count()
    # torch.cuda.is_available()

    # new function
    # print("num_cuda_devices:", num_cuda_devices())
    # print("available:", is_cuda_available())

    mp.start_processes(wor
[... cut ...]
```

This fix changes 13 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/pytorch_lightning/CHANGELOG.md`: `- The `MLFlowLogger.finalize()` now sets the status to `FAILED` when an exception occurred in `Trainer`, and sets the status to `FINISHED` on successful completion ([#12292](https://github.com/Lightning-AI/lightning/pull/12292))`

Patch of `src/pytorch_lightning/CHANGELOG.md` in this fix:

```diff
@@ -81,8 +81,10 @@ The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).
 - Removed fall-back to `LightningEnvironment` when number of SLURM tasks does not correspond to number of processes in Trainer ([#14300](https://github.com/Lightning-AI/lightning/pull/14300))
 
 
-- The `MLFlowLogger.finalize()` now sets the status to `FAILED` when an exception occurred in `Trainer`, and sets the status to `FINISHED` on successful completion ([#12292](https://github.com/Lightning-AI/lightning/pull/12292))
+- Trainer queries the CUDA devices through NVML if available to avoid initializing CUDA before forking, which eliminates the need for the `PL_DISABLE_FORK` environment variable introduced in v1.7.4 ([#14631](https://github.com/Lightning-AI/lightning/issues/14631))
+
 
+- The `MLFlowLogger.finalize()` now sets the status to `FAILED` when an exception occurred in `Trainer`, and sets the status to `FINISHED` on successful completion ([#12292](https://github.com/Lightning-AI/lightning/pull/12292))
 
 
 ### Deprecated
```

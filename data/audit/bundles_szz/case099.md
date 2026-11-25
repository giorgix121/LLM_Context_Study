# case099: Lightning-AI/lightning 47f0d336f14c

Sampled file (the only file the models saw): `src/lightning_lite/strategies/ddp_spawn.py` · committed 2022-09-16 16:25:27-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Standalone Lite: Update LightningLite (#14726)
```

## Diff of the sampled file

```diff
@@ -114,10 +114,6 @@ class DDPSpawnStrategy(ParallelStrategy):
         return DistributedDataParallel(module=module, device_ids=self._determine_ddp_device_ids(), **self._ddp_kwargs)
 
     def module_to_device(self, module: Module) -> None:
-        if self.root_device.type == "cuda":
-            # TODO(lite): This should be handled outside module_to_device, by a call to accelerator.setup_device()
-            # set the device on the spawned subprocesses
-            torch.cuda.set_device(self.root_device)
         module.to(self.root_device)
 
     def reduce(
@@ -200,8 +196,7 @@ class DDPSpawnStrategy(ParallelStrategy):
     def _get_process_group_backend(self) -> str:
         return self._process_group_backend or get_default_process_group_backend_for_device(self.root_device)
 
-    def _set_world_ranks(self, process_idx: int = 0) -> None:
-        self._local_rank = process_idx
+    def _set_world_ranks(self) -> None:
         if self.cluster_environment is None:
             return
         self.cluster_environment.set_global_rank(self.node_rank * self.num_processes + self.local_rank)
```

## Other files changed by this commit (13)

- `src/lightning_lite/__init__.py` (+7 −2)
- `src/lightning_lite/connector.py` (+2 −1)
- `src/lightning_lite/lite.py` (+0 −3)
- `src/lightning_lite/utilities/distributed.py` (+57 −1)
- `src/pytorch_lightning/lite/lite.py` (+31 −86)
- `src/pytorch_lightning/lite/wrappers.py` (+7 −12)
- `src/pytorch_lightning/overrides/distributed.py` (+2 −56)
- `src/pytorch_lightning/trainer/connectors/data_connector.py` (+2 −1)
- `tests/tests_lite/test_lite.py` (+0 −12)
- `tests/tests_pytorch/lite/test_lite.py` (+15 −27)
- `tests/tests_pytorch/lite/test_parity.py` (+4 −2)
- `tests/tests_pytorch/lite/test_wrappers.py` (+15 −5)
- `tests/tests_pytorch/trainer/connectors/test_data_connector.py` (+1 −1)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 3b75c52869ba (2022-10-05) · pull request #14984: Support ddp_fork strategy with native AMP by attempting NVML-based CUDA availability assessment

Pull-request labels: ready to be merged, precision: amp, accelerator: cuda, community, pl

Commit message:

```
Support ddp_fork strategy with native AMP by attempting NVML-based CUDA availability assessment (#14984)

Co-authored-by: Carlos Mocholí <carlossmocholi@gmail.com>
Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
Co-authored-by: Jirka Borovec <Borda@users.noreply.github.com>
```

Pull-request description:

```
## What does this PR do?
Fixes #14981 

`ddp_fork` (and associated alias strategies) cannot currently be used along with native AMP due to the invocation of the CUDA Runtime API within the call to `GradScaler` in the `NativeMixedPrecisionPlugin`:

https://github.com/Lightning-AI/lightning/blob/c059db446e7bfea03fba91e598ad503f0d1c6581/src/pytorch_lightning/plugins/precision/native_amp.py#L53

which in turn initializes CUDA and poisons subsequent forks.

It may be possible with a future version of PyTorch to alter the default behavior of `torch.cuda.is_available()` to use an NVML-based CUDA assessment throughout Lightning. In the meantime, patching  `torch.cuda.is_available()` with Lightning's implementation of the upstream NVML-based assessment can unlock this functionality.

This PR patches `torch.cuda.is_available()` within `NativeMixedPrecisionPlugin` (both Lite and PL versions) and adds a standalone test for the `ddp_fork` strategy in a CUDA and native AMP context (adding a standalone test only for PL given how expensive the standalone multi-gpu tests can be).

The use of `ddp_fork` (and its associated alias strategies) with native AMP in context (e.g. in the context of  Jupyter
[... cut ...]
```

This fix changes 8 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/lightning_lite/lite.py`: `from lightning_lite.plugins import Precision`

Patch of `src/lightning_lite/lite.py` in this fix:

```diff
@@ -26,9 +26,9 @@
 from torch.optim import Optimizer
 from torch.utils.data import BatchSampler, DataLoader, DistributedSampler
 
+from lightning_lite.plugins import Precision  # avoid circular imports: # isort: split
 from lightning_lite.accelerators.accelerator import Accelerator
 from lightning_lite.connector import _Connector, _PLUGIN_INPUT, _PRECISION_INPUT
-from lightning_lite.plugins import Precision
 from lightning_lite.strategies import DeepSpeedStrategy, Strategy, XLAStrategy
 from lightning_lite.strategies.strategy import TBroadcast
 from lightning_lite.utilities import move_data_to_device
```

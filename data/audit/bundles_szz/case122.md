# case122: Lightning-AI/lightning d013bcc5bf23

Sampled file (the only file the models saw): `src/pytorch_lightning/accelerators/cpu.py` · committed 2022-09-12 15:00:14-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Standalone Lite: Accelerators (#14578)

Co-authored-by: Carlos Mocholí <carlossmocholi@gmail.com>
Co-authored-by: Jirka Borovec <Borda@users.noreply.github.com>
```

## Diff of the sampled file

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

## Other files changed by this commit (33)

- `src/lightning_lite/accelerators/__init__.py` (+22 −0)
- `src/lightning_lite/accelerators/accelerator.py` (+56 −0)
- `src/lightning_lite/accelerators/cpu.py` (+65 −0)
- `src/lightning_lite/accelerators/cuda.py` (+64 −0)
- `src/lightning_lite/accelerators/mps.py` (+74 −0)
- `src/lightning_lite/accelerators/registry.py` (+4 −7)
- `src/lightning_lite/accelerators/tpu.py` (+59 −0)
- `src/lightning_lite/utilities/device_parser.py` (+3 −3)
- `src/lightning_lite/utilities/imports.py` (+0 −1)
- `src/pytorch_lightning/accelerators/__init__.py` (+3 −3)
- `src/pytorch_lightning/accelerators/accelerator.py` (+17 −43)
- `src/pytorch_lightning/accelerators/cuda.py` (+8 −9)
- `src/pytorch_lightning/accelerators/hpu.py` (+8 −5)
- `src/pytorch_lightning/accelerators/ipu.py` (+9 −2)
- `src/pytorch_lightning/accelerators/mps.py` (+9 −13)
- `src/pytorch_lightning/accelerators/tpu.py` (+11 −5)
- `src/pytorch_lightning/lite/lite.py` (+1 −1)
- `src/pytorch_lightning/strategies/strategy.py` (+1 −1)
- `src/pytorch_lightning/trainer/connectors/accelerator_connector.py` (+1 −1)
- `tests/tests_lite/accelerators/__init__.py` (+0 −0)
- `tests/tests_lite/accelerators/test_cpu.py` (+43 −0)
- `tests/tests_lite/accelerators/test_cuda.py` (+53 −0)
- `tests/tests_lite/accelerators/test_mps.py` (+49 −0)
- `tests/tests_lite/accelerators/test_registry.py` (+73 −0)
- `tests/tests_lite/accelerators/test_tpu.py` (+40 −0)
- `tests/tests_lite/helpers/runif.py` (+13 −7)
- `tests/tests_lite/utilities/test_device_parser.py` (+7 −0)
- `tests/tests_pytorch/accelerators/test_common.py` (+12 −0)
- `tests/tests_pytorch/accelerators/test_cpu.py` (+11 −0)
- `tests/tests_pytorch/accelerators/test_registry.py` (+1 −49)
- `tests/tests_pytorch/deprecated_api/test_remove_1-10.py` (+6 −0)
- `tests/tests_pytorch/helpers/runif.py` (+3 −3)
- `tests/tests_pytorch/trainer/connectors/test_accelerator_connector.py` (+12 −3)

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
- in `src/lightning_lite/accelerators/cuda.py`: `from typing import Dict, List, Optional, Union`
- in `tests/tests_lite/accelerators/test_cpu.py`: `from lightning_lite.accelerators.cpu import CPUAccelerator`
- in `tests/tests_lite/accelerators/test_cuda.py`: `from lightning_lite.accelerators.cuda import CUDAAccelerator`
- in `tests/tests_lite/utilities/test_device_parser.py`: `@pytest.mark.parametrize("devices", ([3], -1))`; `def test_invalid_devices_with_cpu_accelerator(devices):`

Patch of `src/lightning_lite/accelerators/cuda.py` in this fix:

```diff
@@ -11,13 +11,15 @@
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.
-import multiprocessing
-from typing import Dict, List, Optional, Union
+import os
+import warnings
+from functools import lru_cache
+from typing import Dict, List, Optional, Set, Union
 
 import torch
 
 from lightning_lite.accelerators.accelerator import Accelerator
-from lightning_lite.strategies.launchers.multiprocessing import _is_forking_disabled
+from lightning_lite.utilities.imports import _TORCH_GREATER_EQUAL_1_13
 
 
 class CUDAAccelerator(Accelerator):
@@ -75,16 +77,20 @@ def _get_all_available_cuda_gpus() -> List[int]:
     return list(range(num_cuda_devices()))
 
 
+@lru_cache(1)
 def num_cuda_devices() -> int:
-    """Returns the number of GPUs available.
+    """Returns the number of available CUDA devices.
 
     Unlike :func:`torch.cuda.device_count`, this function does its best not to create a CUDA context for fork support,
     if the platform allows it.
     """
-    if "fork" not in torch.multiprocessing.get_all_start_methods() or _is_forking_disabled():
+    if _TORCH_GREATER_EQUAL_1_13:
         return torch.cuda.device_count()
-    with multiprocessing.get_context("fork").Pool(1) as pool:
-        return pool.apply(torch.cuda.device_count)
+
+    # Implementation copied from upstream: https://github.com/pytorch/pytorch/pull/84879
+    # TODO: Remove once minimum supported PyTorch version is 1.13
+    nvml_count = _device_count_nvml()
+    return torch.cuda.device_count() if nvml_count < 0 else nvml_count
 
 
 def is_cuda_available() -> bool:
@@ -93,7 +99,60 @@ def is_cuda_available() -> bool:
     Unlike :func:`torch.cuda.is_available`, this function does its best not to create a CUDA context for fork support,
     if the platform allows it.
     """
-    if "fork" not in torch.multiprocessing.get_all_start_methods() or _is_forking_disabled():
-        return torch.cuda.is_available()
-    with multiprocessing.get_context("fork").Pool(1) as pool:
-        return pool.apply(torch.cuda.is_available)
+    return num_cuda_devices() > 0
+
+
+def
[... cut ...]
```

Patch of `tests/tests_lite/accelerators/test_cpu.py` in this fix:

```diff
@@ -15,7 +15,7 @@
 import pytest
 import torch
 
-from lightning_lite.accelerators.cpu import CPUAccelerator
+from lightning_lite.accelerators.cpu import CPUAccelerator, parse_cpu_cores
 
 
 def test_auto_device_count():
@@ -41,3 +41,10 @@ def test_init_device_with_wrong_device_type():
 )
 def test_get_parallel_devices(devices, expected):
     assert CPUAccelerator.get_parallel_devices(devices) == expected
+
+
+@pytest.mark.parametrize("devices", ([3], -1))
+def test_invalid_devices_with_cpu_accelerator(devices):
+    """Test invalid device flag raises MisconfigurationException."""
+    with pytest.raises(TypeError, match="should be an int > 0"):
+        parse_cpu_cores(devices)
```

Patch of `tests/tests_lite/accelerators/test_cuda.py` in this fix:

```diff
@@ -17,7 +17,7 @@
 import torch
 from tests_lite.helpers.runif import RunIf
 
-from lightning_lite.accelerators.cuda import CUDAAccelerator
+from lightning_lite.accelerators.cuda import CUDAAccelerator, is_cuda_available, num_cuda_devices
 
 
 @mock.patch("lightning_lite.accelerators.cuda.num_cuda_devices", return_value=2)
@@ -51,3 +51,12 @@ def test_get_parallel_devices(devices, expected):
 def test_set_cuda_device(set_device_mock):
     CUDAAccelerator().setup_device(torch.device("cuda", 1))
     set_device_mock.assert_called_once_with(torch.device("cuda", 1))
+
+
+@mock.patch("lightning_lite.accelerators.cuda._device_count_nvml", return_value=-1)
+@mock.patch("torch.cuda.device_count", return_value=100)
+def test_num_cuda_devices_without_nvml(*_):
+    """Test that if NVML can't be loaded, our helper functions fall back to the default implementation for
+    determining CUDA availability."""
+    assert is_cuda_available()
+    assert num_cuda_devices() == 100
```

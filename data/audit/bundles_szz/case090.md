# case090: ultralytics/yolov5 ca9c993d6c3c

Sampled file (the only file the models saw): `utils/autobatch.py` · committed 2022-09-18 17:15:25-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Standardize warnings with `WARNING  ⚠️ ...` (#9467)

* Standardize warnings

* [pre-commit.ci] auto fixes from pre-commit.com hooks

for more information, see https://pre-commit.ci

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
```

## Diff of the sampled file

```diff
@@ -65,7 +65,7 @@ def autobatch(model, imgsz=640, fraction=0.8, batch_size=16):
             b = batch_sizes[max(i - 1, 0)]  # select prior safe point
     if b < 1 or b > 1024:  # b outside of safe range
         b = batch_size
-        LOGGER.warning(f'{prefix}WARNING: ⚠️ CUDA anomaly detected, recommend restart environment and retry command.')
+        LOGGER.warning(f'{prefix}WARNING ⚠️ CUDA anomaly detected, recommend restart environment and retry command.')
 
     fraction = np.polyval(p, b) / t  # actual fraction predicted
     LOGGER.info(f'{prefix}Using batch-size {b} for {d} {t * fraction:.2f}G/{t:.2f}G ({fraction * 100:.0f}%) ✅')
```

## Other files changed by this commit (16)

- `benchmarks.py` (+1 −1)
- `classify/train.py` (+1 −1)
- `export.py` (+1 −1)
- `hubconf.py` (+1 −1)
- `segment/train.py` (+1 −1)
- `segment/val.py` (+3 −3)
- `train.py` (+1 −1)
- `utils/__init__.py` (+8 −2)
- `utils/autoanchor.py` (+2 −2)
- `utils/dataloaders.py` (+9 −9)
- `utils/general.py` (+8 −13)
- `utils/loggers/__init__.py` (+2 −2)
- `utils/metrics.py` (+1 −1)
- `utils/segment/dataloaders.py` (+1 −1)
- `utils/torch_utils.py` (+1 −1)
- `val.py` (+3 −3)

## Fix commits that the dataset links to this commit (2)

### Fix 1: e3ff78067694 (2022-10-17) · pull request #9825: Allow PyTorch Hub results to display in notebooks

Commit message:

```
Allow PyTorch Hub results to display in notebooks (#9825)

* Allow PyTorch Hub results to display in notebooks

* fix CI

* fix CI

* [pre-commit.ci] auto fixes from pre-commit.com hooks

for more information, see https://pre-commit.ci

* fix CI

* fix CI

* [pre-commit.ci] auto fixes from pre-commit.com hooks

for more information, see https://pre-commit.ci

* fix CI

* [pre-commit.ci] auto fixes from pre-commit.com hooks

for more information, see https://pre-commit.ci

* fix CI

* fix CI

* fix CI

* fix CI

* [pre-commit.ci] auto fixes from pre-commit.com hooks

for more information, see https://pre-commit.ci

* fix CI

* fix CI

* fix CI

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
```

Pull-request description:

```
<!--
Thank you for submitting a YOLOv5 🚀 Pull Request! We want to make contributing to YOLOv5 as easy and transparent as possible. A few tips to get you started:

- Search existing YOLOv5 [PRs](https://github.com/ultralytics/yolov5/pull) to see if a similar PR already exists.
- Link this PR to a YOLOv5 [issue](https://github.com/ultralytics/yolov5/issues) to help us understand what bug fix or feature is being implemented.
- Provide before and after profiling/inference/training results to help us quantify the improvement your PR provides (if applicable).

Please see our ✅ [Contributing Guide](https://github.com/ultralytics/yolov5/blob/master/CONTRIBUTING.md) for more details.
-->


## 🛠️ PR Summary

<sub>Made with ❤️ by [Ultralytics Actions](https://github.com/ultralytics/actions)<sub>

### 🌟 Summary
Enhancements for image display checks and error handling in various environments.

### 📊 Key Changes
- Added `warn=True` argument to `check_imshow` calls when initializing webcam in `classify/predict.py`, `detect.py`, and `segment/predict.py`.
- Introduced `CHECK_IMSHOW` global variable in `models/common.py` and conditional display methods based on environment compatibility.
- Implement
[... cut ...]
```

This fix changes 8 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `utils/__init__.py`: `print(emojis(f'{self.msg}{value}'))`
- in `utils/general.py`: `LOGGER.warning(f'WARNING ⚠️ Environment does not support cv2.imshow() or PIL Image.show() image displays\n{e}')`
- in `utils/metrics.py`: `@TryExcept('WARNING ⚠️ ConfusionMatrix plot failure: ')`

Patch of `utils/__init__.py` in this fix:

```diff
@@ -23,7 +23,7 @@ def __enter__(self):
 
     def __exit__(self, exc_type, value, traceback):
         if value:
-            print(emojis(f'{self.msg}{value}'))
+            print(emojis(f"{self.msg}{': ' if self.msg else ''}{value}"))
         return True
```

Patch of `utils/general.py` in this fix:

```diff
@@ -27,6 +27,7 @@
 from zipfile import ZipFile
 
 import cv2
+import IPython
 import numpy as np
 import pandas as pd
 import pkg_resources as pkg
@@ -73,6 +74,12 @@ def is_colab():
     return 'COLAB_GPU' in os.environ
 
 
+def is_notebook():
+    # Is environment a Jupyter notebook? Verified on Colab, Jupyterlab, Kaggle, Paperspace
+    ipython_type = str(type(IPython.get_ipython()))
+    return 'colab' in ipython_type or 'zmqshell' in ipython_type
+
+
 def is_kaggle():
     # Is environment a Kaggle Notebook?
     return os.environ.get('PWD') == '/kaggle/working' and os.environ.get('KAGGLE_URL_BASE') == 'https://www.kaggle.com'
@@ -383,18 +390,20 @@ def check_img_size(imgsz, s=32, floor=0):
     return new_size
 
 
-def check_imshow():
+def check_imshow(warn=False):
     # Check if environment supports image displays
     try:
-        assert not is_docker(), 'cv2.imshow() is disabled in Docker environments'
-        assert not is_colab(), 'cv2.imshow() is disabled in Google Colab environments'
+        assert not is_notebook()
+        assert not is_docker()
+        assert 'NoneType' not in str(type(IPython.get_ipython()))  # SSH terminals, GitHub CI
         cv2.imshow('test', np.zeros((1, 1, 3)))
         cv2.waitKey(1)
         cv2.destroyAllWindows()
         cv2.waitKey(1)
         return True
     except Exception as e:
-        LOGGER.warning(f'WARNING ⚠️ Environment does not support cv2.imshow() or PIL Image.show() image displays\n{e}')
+        if warn:
+            LOGGER.warning(f'WARNING ⚠️ Environment does not support cv2.imshow() or PIL Image.show()\n{e}')
         return False
```

Patch of `utils/metrics.py` in this fix:

```diff
@@ -186,7 +186,7 @@ def tp_fp(self):
         # fn = self.matrix.sum(0) - tp  # false negatives (missed detections)
         return tp[:-1], fp[:-1]  # remove background class
 
-    @TryExcept('WARNING ⚠️ ConfusionMatrix plot failure: ')
+    @TryExcept('WARNING ⚠️ ConfusionMatrix plot failure')
     def plot(self, normalize=True, save_dir='', names=()):
         import seaborn as sn
```

### Fix 2: e4398cf17960 (2022-10-04) · pull request #9691: TensorRT `--dynamic` fix

Commit message:

```
TensorRT `--dynamic` fix (#9691)

* Update export.py

Signed-off-by: Glenn Jocher <glenn.jocher@ultralytics.com>

* Update export.py

Signed-off-by: Glenn Jocher <glenn.jocher@ultralytics.com>

Signed-off-by: Glenn Jocher <glenn.jocher@ultralytics.com>
```

Pull-request description:

```
May resolve #9688 

Signed-off-by: Glenn Jocher <glenn.jocher@ultralytics.com>

<!--
Thank you for submitting a YOLOv5 🚀 Pull Request! We want to make contributing to YOLOv5 as easy and transparent as possible. A few tips to get you started:

- Search existing YOLOv5 [PRs](https://github.com/ultralytics/yolov5/pull) to see if a similar PR already exists.
- Link this PR to a YOLOv5 [issue](https://github.com/ultralytics/yolov5/issues) to help us understand what bug fix or feature is being implemented.
- Provide before and after profiling/inference/training results to help us quantify the improvement your PR provides (if applicable).

Please see our ✅ [Contributing Guide](https://github.com/ultralytics/yolov5/blob/master/CONTRIBUTING.md) for more details.
-->


## 🛠️ PR Summary

<sub>Made with ❤️ by [Ultralytics Actions](https://github.com/ultralytics/actions)<sub>

### 🌟 Summary
Improved ONNX export compatibility with TensorRT versions 7 and 8.

### 📊 Key Changes
- Removed `False` in the call to `export_onnx` function, now passing `dynamic` directly.
- Fixed indentation and formatting in the `dynamic` flag handling block.

### 🎯 Purpose & Impact
- 🛠 The update ensures better complia
[... cut ...]
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `export.py`: `LOGGER.warning(f"{prefix}WARNING ⚠️ --dynamic model requires maximum --batch-size argument")`

Patch of `export.py` in this fix:

```diff
@@ -251,11 +251,11 @@ def export_engine(model, im, file, half, dynamic, simplify, workspace=4, verbose
     if trt.__version__[0] == '7':  # TensorRT 7 handling https://github.com/ultralytics/yolov5/issues/6012
         grid = model.model[-1].anchor_grid
         model.model[-1].anchor_grid = [a[..., :1, :1, :] for a in grid]
-        export_onnx(model, im, file, 12, False, dynamic, simplify)  # opset 12
+        export_onnx(model, im, file, 12, dynamic, simplify)  # opset 12
         model.model[-1].anchor_grid = grid
     else:  # TensorRT >= 8
         check_version(trt.__version__, '8.0.0', hard=True)  # require tensorrt>=8.0.0
-        export_onnx(model, im, file, 12, False, dynamic, simplify)  # opset 12
+        export_onnx(model, im, file, 12, dynamic, simplify)  # opset 12
     onnx = file.with_suffix('.onnx')
 
     LOGGER.info(f'\n{prefix} starting export with TensorRT {trt.__version__}...')
@@ -285,7 +285,7 @@ def export_engine(model, im, file, half, dynamic, simplify, workspace=4, verbose
 
     if dynamic:
         if im.shape[0] <= 1:
-            LOGGER.warning(f"{prefix}WARNING ⚠️ --dynamic model requires maximum --batch-size argument")
+            LOGGER.warning(f"{prefix} WARNING ⚠️ --dynamic model requires maximum --batch-size argument")
         profile = builder.create_optimization_profile()
         for inp in inputs:
             profile.set_shape(inp.name, (1, *im.shape[1:]), (max(1, im.shape[0] // 2), *im.shape[1:]), im.shape)
```

# case145: ultralytics/yolov5 b25d5a75f2c8

Sampled file (the only file the models saw): `classify/predict.py` · committed 2022-09-23 00:23:40-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Refactor dataset batch-size (#9551)
```

## Diff of the sampled file

```diff
@@ -91,10 +91,9 @@ def run(
     if webcam:
         view_img = check_imshow()
         dataset = LoadStreams(source, img_size=imgsz, transforms=classify_transforms(imgsz[0]), vid_stride=vid_stride)
-        bs = len(dataset)  # batch_size
     else:
         dataset = LoadImages(source, img_size=imgsz, transforms=classify_transforms(imgsz[0]), vid_stride=vid_stride)
-        bs = 1  # batch_size
+    bs = len(dataset)  # batch_size
     vid_path, vid_writer = [None] * bs, [None] * bs
 
     # Run inference
```

## Other files changed by this commit (2)

- `detect.py` (+1 −2)
- `segment/predict.py` (+1 −2)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 966b0e09f0a5 (2022-09-25) · pull request #9581: TensorRT detect.py inference fix

Pull-request labels: bug

Commit message:

```
TensorRT detect.py inference fix (#9581)

* Update

* Update ci-testing.yml

Signed-off-by: Glenn Jocher <glenn.jocher@ultralytics.com>

* Update ci-testing.yml

Signed-off-by: Glenn Jocher <glenn.jocher@ultralytics.com>

* Segment fix

* Segment fix

Signed-off-by: Glenn Jocher <glenn.jocher@ultralytics.com>
```

Pull-request description:

```
May resolve https://github.com/ultralytics/yolov5/issues/9578
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
Enhanced testing procedures and visualization improvements for various models in Ultralytics' YOLOv5 repository.

### 📊 Key Changes
- **Extended Continuous Integration Tests:** Added tests for exporting `.onnx` models and subsequent predictions for classification, detection, and segmentation tasks.
- **Batch Size Standardizat
[... cut ...]
```

This fix changes 4 files. Lines it removes that the commit above had added:

- in the sampled file: `bs = len(dataset)  # batch_size`
- in `detect.py`: `bs = len(dataset)  # batch_size`
- in `segment/predict.py`: `bs = len(dataset)  # batch_size`

Patch of the sampled file in this fix:

```diff
@@ -89,14 +89,15 @@ def run(
     imgsz = check_img_size(imgsz, s=stride)  # check image size
 
     # Dataloader
+    bs = 1  # batch_size
     if webcam:
         view_img = check_imshow()
         dataset = LoadStreams(source, img_size=imgsz, transforms=classify_transforms(imgsz[0]), vid_stride=vid_stride)
+        bs = len(dataset)
     elif screenshot:
         dataset = LoadScreenshots(source, img_size=imgsz, stride=stride, auto=pt)
     else:
         dataset = LoadImages(source, img_size=imgsz, transforms=classify_transforms(imgsz[0]), vid_stride=vid_stride)
-    bs = len(dataset)  # batch_size
     vid_path, vid_writer = [None] * bs, [None] * bs
 
     # Run inference
```

Patch of `detect.py` in this fix:

```diff
@@ -97,14 +97,15 @@ def run(
     imgsz = check_img_size(imgsz, s=stride)  # check image size
 
     # Dataloader
+    bs = 1  # batch_size
     if webcam:
         view_img = check_imshow()
         dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
+        bs = len(dataset)
     elif screenshot:
         dataset = LoadScreenshots(source, img_size=imgsz, stride=stride, auto=pt)
     else:
         dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
-    bs = len(dataset)  # batch_size
     vid_path, vid_writer = [None] * bs, [None] * bs
 
     # Run inference
```

Patch of `segment/predict.py` in this fix:

```diff
@@ -100,14 +100,15 @@ def run(
     imgsz = check_img_size(imgsz, s=stride)  # check image size
 
     # Dataloader
+    bs = 1  # batch_size
     if webcam:
         view_img = check_imshow()
         dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
+        bs = len(dataset)
     elif screenshot:
         dataset = LoadScreenshots(source, img_size=imgsz, stride=stride, auto=pt)
     else:
         dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
-    bs = len(dataset)  # batch_size
     vid_path, vid_writer = [None] * bs, [None] * bs
 
     # Run inference
@@ -179,7 +180,7 @@ def run(
                         c = int(cls)  # integer class
                         label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                         annotator.box_label(xyxy, label, color=colors(c, True))
-                        annotator.draw.polygon(segments[j], outline=colors(c, True), width=3)
+                        # annotator.draw.polygon(segments[j], outline=colors(c, True), width=3)
                     if save_crop:
                         save_one_box(xyxy, imc, file=save_dir / 'crops' / names[c] / f'{p.stem}.jpg', BGR=True)
```

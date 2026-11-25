# case145: ultralytics/yolov5 b25d5a75f2c8

File: `classify/predict.py` · committed 2022-09-23 00:23:40-01:00 · SZZ label: RISKY

## Commit message

```
Refactor dataset batch-size (#9551)
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
   96      bs = len(dataset)  # batch_size
```

## Candidate fixes (1 later commits to this file remove a blamed line; 10 later commits up to 2023-06-30 checked)

### Candidate 1: 966b0e09f0a5 (2022-09-25)

Message:

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

Removed blamed lines: `bs = len(dataset)  # batch_size`

Patch of this file:

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

# case090: ultralytics/yolov5 ca9c993d6c3c

File: `utils/autobatch.py` · committed 2022-09-18 17:15:25-01:00 · SZZ label: RISKY

## Commit message

```
Standardize warnings with `WARNING  ⚠️ ...` (#9467)

* Standardize warnings

* [pre-commit.ci] auto fixes from pre-commit.com hooks

for more information, see https://pre-commit.ci

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
   68          LOGGER.warning(f'{prefix}WARNING ⚠️ CUDA anomaly detected, recommend restart environment and retry command.')
```

## Candidate fixes (0 later commits to this file remove a blamed line; 2 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

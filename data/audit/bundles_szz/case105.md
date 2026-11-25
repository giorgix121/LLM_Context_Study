# case105: ray-project/ray 081ce2fe4e88

Sampled file (the only file the models saw): `python/ray/data/_internal/shuffle_and_partition.py` · committed 2022-10-06 13:41:22-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Revert "[Datasets] Arrow 7.0.0+ Support: Use Arrow IPC format for pickling Arrow data to circumvent slice view buffer truncation bug. (#29055)" (#29138)

This reverts commit c1d62d4.

This is breaking the Windows build: https://buildkite.com/ray-project/oss-ci-build-branch/builds/365#0183ada0-8558-4502-9298-7e0bed873e23
```

## Diff of the sampled file

```diff
@@ -56,7 +56,7 @@ class _ShufflePartitionOp(ShuffleOp):
         slice_sz = max(1, math.ceil(block.num_rows() / output_num_blocks))
         slices = []
         for i in range(output_num_blocks):
-            slices.append(block.slice(i * slice_sz, (i + 1) * slice_sz))
+            slices.append(block.slice(i * slice_sz, (i + 1) * slice_sz, copy=True))
 
         # Randomize the distribution order of the blocks (this prevents empty
         # outputs when input blocks are very small).
```

## Other files changed by this commit (23)

- `python/ray/air/util/transform_pyarrow.py` (+6 −5)
- `python/ray/data/__init__.py` (+14 −0)
- `python/ray/data/_internal/arrow_block.py` (+9 −8)
- `python/ray/data/_internal/arrow_ops/transform_polars.py` (+1 −1)
- `python/ray/data/_internal/arrow_ops/transform_pyarrow.py` (+1 −1)
- `python/ray/data/_internal/arrow_serialization.py` (+27 −204)
- `python/ray/data/_internal/delegating_block_builder.py` (+0 −1)
- `python/ray/data/_internal/pandas_block.py` (+1 −1)
- `python/ray/data/_internal/simple_block.py` (+2 −2)
- `python/ray/data/_internal/split.py` (+1 −1)
- `python/ray/data/dataset.py` (+5 −42)
- `python/ray/data/datasource/file_based_datasource.py` (+28 −1)
- `python/ray/data/grouped_dataset.py` (+1 −1)
- `python/ray/data/random_access_dataset.py` (+2 −2)
- `python/ray/data/read_api.py` (+2 −2)
- `python/ray/data/tests/conftest.py` (+1 −15)
- `python/ray/data/tests/test_arrow_serialization.py` (+0 −288)
- `python/ray/data/tests/test_batch_mapper.py` (+0 −30)
- `python/ray/data/tests/test_dataset.py` (+0 −28)
- `python/ray/util/serialization.py` (+0 −3)
- `python/ray/util/serialization_addons.py` (+0 −6)
- `python/requirements.txt` (+2 −2)
- `python/setup.py` (+1 −1)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 1c82427c2e27 (2022-10-21) · pull request #29479: [AIR - Datasets] [Hotfix] Tensor extension column concatenation fixes.

Commit message:

```
[AIR - Datasets] [Hotfix] Tensor extension column concatenation fixes. (#29479)

Fixes the concatenation of tensor columns (and extension types in general). Previously, concatenating tensor columns may produce a variable-shaped tensor but would be represented with a broken homogeneous-shaped tensor. This PR ensures that the correct tensor extension type is produced post-concatenation.

Issue Details:

The core issue is that we weren’t accounting for homogeneous-shaped tensor column concatenation resulting in a heterogeneous-shaped tensor column. In master, this currently fails silently until accessing the data fails somewhere downstream of the concatenation.

E.g., if you have 5 images of shape (32, 32) in one block, and 5 images of shape (64, 64) in another block, the image column in each individual block is homogeneous-shaped. But if you concatenate those blocks, you have 10 images, half with shape (32, 32) and half with shape (64, 64), which needs our heterogeneous-shaped (variable-shaped) tensor column representation.
```

Pull-request description:

```
Fixes the concatenation of tensor columns (and extension types in general). Previously, concatenating tensor columns may produce a variable-shaped tensor but would be represented with a broken homogeneous-shaped tensor. This PR ensures that the correct tensor extension type is produced post-concatenation.

## Issue Details

The core issue is that we weren’t accounting for homogeneous-shaped tensor column concatenation resulting in a heterogeneous-shaped tensor column. In master, this currently fails silently until accessing the data fails somewhere downstream of the concatenation.

E.g., if you have 5 images of shape (32, 32) in one block, and 5 images of shape (64, 64) in another block, the image column in each individual block is homogeneous-shaped. But if you concatenate those blocks, you have 10 images, half with shape (32, 32) and half with shape (64, 64), which needs our heterogeneous-shaped (variable-shaped) tensor column representation.

## Issue

Closes https://github.com/ray-project/ray/issues/29489

## Checks

- [ ] I've signed off every commit(by using the -s flag, i.e., `git commit -s`) in this PR.
- [x] I've run `scripts/format.sh` to lint the changes in this PR.
- [x
[... cut ...]
```

This fix changes 8 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `python/ray/air/util/transform_pyarrow.py`: `)`; `chunk = ca.chunk(0)`; `chunk.type, pyarrow.concat_arrays([c.storage for c in ca.chunks])`; `return ca`; `return type(chunk).from_storage(`

Patch of `python/ray/air/util/transform_pyarrow.py` in this fix:

```diff
@@ -18,14 +18,21 @@ def _concatenate_extension_column(ca: "pyarrow.ChunkedArray") -> "pyarrow.Array"
     extension arrays.
     See https://issues.apache.org/jira/browse/ARROW-16503.
     """
+    from ray.air.util.tensor_extensions.arrow import (
+        ArrowTensorArray,
+        ArrowTensorType,
+        ArrowVariableShapedTensorType,
+    )
+
     if not _is_column_extension_type(ca):
         raise ValueError("Chunked array isn't an extension array: {ca}")
 
     if ca.num_chunks == 0:
-        # No-op for no-chunk chunked arrays, since there's nothing to concatenate.
-        return ca
+        # Create empty storage array.
+        storage = pyarrow.array([], type=ca.type.storage_type)
+    elif isinstance(ca.type, (ArrowTensorType, ArrowVariableShapedTensorType)):
+        return ArrowTensorArray._concat_same_type(ca.chunks)
+    else:
+        storage = pyarrow.concat_arrays([c.storage for c in ca.chunks])
 
-    chunk = ca.chunk(0)
-    return type(chunk).from_storage(
-        chunk.type, pyarrow.concat_arrays([c.storage for c in ca.chunks])
-    )
+    return ca.type.__arrow_ext_class__().from_storage(ca.type, storage)
```

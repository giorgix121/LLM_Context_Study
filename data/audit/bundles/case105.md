# case105: ray-project/ray 081ce2fe4e88

File: `python/ray/data/_internal/shuffle_and_partition.py` · committed 2022-10-06 13:41:22-01:00 · SZZ label: RISKY

## Commit message

```
Revert "[Datasets] Arrow 7.0.0+ Support: Use Arrow IPC format for pickling Arrow data to circumvent slice view buffer truncation bug. (#29055)" (#29138)

This reverts commit c1d62d4.

This is breaking the Windows build: https://buildkite.com/ray-project/oss-ci-build-branch/builds/365#0183ada0-8558-4502-9298-7e0bed873e23
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
   59              slices.append(block.slice(i * slice_sz, (i + 1) * slice_sz, copy=True))
```

## Candidate fixes (1 later commits to this file remove a blamed line; 3 later commits up to 2023-06-30 checked)

### Candidate 1: 75b206e419f8 (2022-11-08)

Message:

```
[Datasets] [Arrow 7+ Support] [2/N] Add support for Arrow 7 by fixing Arrow serialization bug. (#29993)

This PR adds support for Arrow 7 in Ray, and is the second PR in a set of stacked PRs making up this mono-PR for Arrow 7+ support: #29161, and is stacked on top of a PR fixing task cancellation in Ray Core: #29984.

This PR:
- fixes a serialization bug in Arrow with a custom serializer for Arrow data ([Datasets] Arrow data buffers aren't truncated when pickling zero-copy slice views, leading to huge serialization bloat #29814)
- removes a bunch of defensive copying of Arrow data, which was a workaround for the aforementioned Arrow serialization bug
- adds a CI job for Arrow 7
- bumps the pyarrow upper bound to 8.0.0
```

Removed blamed lines: `slices.append(block.slice(i * slice_sz, (i + 1) * slice_sz, copy=True))`

Patch of this file:

```diff
@@ -56,7 +56,7 @@ def map(
         slice_sz = max(1, math.ceil(block.num_rows() / output_num_blocks))
         slices = []
         for i in range(output_num_blocks):
-            slices.append(block.slice(i * slice_sz, (i + 1) * slice_sz, copy=True))
+            slices.append(block.slice(i * slice_sz, (i + 1) * slice_sz))
 
         # Randomize the distribution order of the blocks (this prevents empty
         # outputs when input blocks are very small).
```

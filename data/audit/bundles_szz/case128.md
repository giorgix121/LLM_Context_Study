# case128: getsentry/sentry cd22be4bbbe3

Sampled file (the only file the models saw): `src/sentry/profiles/utils.py` · committed 2022-10-05 13:54:55-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
fix(profiling): Tune compression params to lower CPU (#39672)
```

## Diff of the sampled file

```diff
@@ -81,7 +81,9 @@ def get_from_profiling_service(
                 "Content-Type": "application/json",
             }
         )
-        kwargs["body"] = brotli.compress(json.dumps(json_data).encode("utf-8"))
+        kwargs["body"] = brotli.compress(
+            json.dumps(json_data).encode("utf-8"), quality=6, mode=brotli.BrotliEncoderMode.TEXT
+        )
     return _profiling_pool.urlopen(  # type: ignore
         method,
         path,
```

## Other files changed by this commit (0)

(none)

## Fix commits that the dataset links to this commit (1)

### Fix 1: bc218e712b26 (2022-10-05) · pull request #39676: fix(profiling): Fix attribute name for brotli compression

Commit message:

```
fix(profiling): Fix attribute name for brotli compression (#39676)

This is what I should have been looking at
https://github.com/google/brotli/blob/9801a2c5d6c67c467ffad676ac301379bb877fc3/python/brotli.py#L25
```

Pull-request description:

```
This is what I should have been looking at https://github.com/google/brotli/blob/9801a2c5d6c67c467ffad676ac301379bb877fc3/python/brotli.py#L25
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: `json.dumps(json_data).encode("utf-8"), quality=6, mode=brotli.BrotliEncoderMode.TEXT`
- in other files of the commit: none

Patch of the sampled file in this fix:

```diff
@@ -82,7 +82,7 @@ def get_from_profiling_service(
             }
         )
         kwargs["body"] = brotli.compress(
-            json.dumps(json_data).encode("utf-8"), quality=6, mode=brotli.BrotliEncoderMode.TEXT
+            json.dumps(json_data).encode("utf-8"), quality=6, mode=brotli.MODE_TEXT
         )
     return _profiling_pool.urlopen(  # type: ignore
         method,
```

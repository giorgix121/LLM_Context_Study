# case128: getsentry/sentry cd22be4bbbe3

File: `src/sentry/profiles/utils.py` · committed 2022-10-05 13:54:55-01:00 · SZZ label: RISKY

## Commit message

```
fix(profiling): Tune compression params to lower CPU (#39672)
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
   84          kwargs["body"] = brotli.compress(
   85              json.dumps(json_data).encode("utf-8"), quality=6, mode=brotli.BrotliEncoderMode.TEXT
   86          )
```

## Candidate fixes (2 later commits to this file remove a blamed line; 11 later commits up to 2023-06-30 checked)

### Candidate 1: bc218e712b26 (2022-10-05)

Message:

```
fix(profiling): Fix attribute name for brotli compression (#39676)

This is what I should have been looking at
https://github.com/google/brotli/blob/9801a2c5d6c67c467ffad676ac301379bb877fc3/python/brotli.py#L25
```

Removed blamed lines: `json.dumps(json_data).encode("utf-8"), quality=6, mode=brotli.BrotliEncoderMode.TEXT`

Patch of this file:

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

### Candidate 2: f04afe044a9b (2023-03-23)

Message:

```
chore(profiling): Add profile payload size (#46254)

Having the payload size is handy to help us understand the size of the
data we're dealing with for the various platforms.
```

Removed blamed lines: `kwargs["body"] = brotli.compress(`

Patch of this file:

```diff
@@ -13,6 +13,7 @@
 from sentry.exceptions import InvalidSearchQuery
 from sentry.net.http import connection_from_url
 from sentry.utils import json, metrics
+from sentry.utils.sdk import set_measurement
 
 
 class RetrySkipTimeout(urllib3.Retry):
@@ -98,9 +99,9 @@ def get_from_profiling_service(
                 "Content-Type": "application/json",
             }
         )
-        kwargs["body"] = brotli.compress(
-            json.dumps(json_data).encode("utf-8"), quality=6, mode=brotli.MODE_TEXT
-        )
+        data = json.dumps(json_data).encode("utf-8")
+        set_measurement("payload.size", len(data), unit="byte")
+        kwargs["body"] = brotli.compress(data, quality=6, mode=brotli.MODE_TEXT)
     return _profiling_pool.urlopen(  # type: ignore
         method,
         path,
```

# case082: getsentry/sentry 2f6716c264bb

Sampled file (the only file the models saw): `src/sentry/services/base.py` · committed 2022-09-12 04:44:38-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
ref: type devserver startup (#38598)

I noticed `sentry devserver 127.0.0.1` produced this error and decided
to prevent it using typing:

```console
$ sentry devserver 127.0.0.1
INFO:The Sentry runner will report development issues to Sentry.io. Use SENTRY_DEVENV_NO_REPORT to avoid reporting issues.
16:33:40 [WARNING] sentry.utils.geo: settings.GEOIP_PATH_MMDB not configured.
/Users/armenzg/code/sentry/src/sentry/runner/initializer.py:571: DeprecatedSettingWarning: The SENTRY_URL_PREFIX setting is deprecated. Please use SENTRY_OPTIONS['system.url-prefix'] instead.
  warnings.warn(DeprecatedSettingWarning(old, "SENTRY_OPTIONS['%s']" % new))
16:33:41 [INFO] sentry.plugins.github: apps-not-configured
16:33:41 [INFO] sentry.runner: We have reported the error below to Sentry
/Users/armenzg/code/sentry/.venv/lib/python3.8/site-packages/sentry_sdk/worker.py:123: ResourceWarning: unclosed <ssl.SSLSocket fd=6, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('192.168.0.14', 58764), raddr=('34.120.195.249', 443)>
  callback = self._queue.get()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
Traceback (most recent call last):
  File "/Users
[... cut ...]
```

## Diff of the sampled file

```diff
@@ -1,5 +1,5 @@
 class Service:
     name = ""
 
-    def __init__(self, debug=False):
+    def __init__(self, debug: bool = False) -> None:
         self.debug = debug
```

## Other files changed by this commit (8)

- `mypy.ini` (+9 −0)
- `requirements-dev-frozen.txt` (+1 −0)
- `requirements-dev-only-frozen.txt` (+1 −0)
- `requirements-dev.txt` (+1 −0)
- `src/sentry/runner/commands/devserver.py` (+24 −22)
- `src/sentry/runner/initializer.py` (+32 −24)
- `src/sentry/services/http.py` (+16 −6)
- `src/sentry/utils/yaml.py` (+7 −7)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 0bb56c8219da (2022-09-16) · pull request #38806: fix(metrics): Re-initialize global tags in subprocesses of the parallel indexer

Pull-request labels: Scope: Backend

Commit message:

```
fix(metrics): Re-initialize global tags in subprocesses of the parallel indexer (#38806)
```

Pull-request description:

```
This fixes tagging in subprocesses, and we already have a smoke test
that the indexer doesn't crash in principle (though I verified locally
that the indexer comes up fine on an empty topic)
```

This fix changes 6 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/sentry/runner/initializer.py`: `def configure_arroyo() -> None:`

Patch of `src/sentry/runner/initializer.py` in this fix:

```diff
@@ -381,8 +381,6 @@ def initialize_app(config: dict[str, Any], skip_service_validation: bool = False
 
     setup_services(validate=not skip_service_validation)
 
-    configure_arroyo()
-
     from django.utils import timezone
 
     from sentry.app import env
@@ -392,20 +390,6 @@ def initialize_app(config: dict[str, Any], skip_service_validation: bool = False
     env.data["start_date"] = timezone.now()
 
 
-def configure_arroyo() -> None:
-    # Arroyo is configured in such a central place because
-    #
-    # 1) it doesn't harm any process that doesn't use arroyo
-    # 2) we want arroyo to be fully configured in subprocesses of the multiprocessing consumer
-    from arroyo import configure_metrics
-
-    from sentry.sentry_metrics.metrics_wrapper import MetricsWrapper
-    from sentry.utils.metrics import backend
-
-    metrics_wrapper = MetricsWrapper(backend, "sentry_metrics.indexer")
-    configure_metrics(metrics_wrapper)
-
-
 def setup_services(validate: bool = True) -> None:
     from sentry import (
         analytics,
```

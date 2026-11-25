# case082: getsentry/sentry 2f6716c264bb

File: `src/sentry/services/base.py` · committed 2022-09-12 04:44:38-01:00 · SZZ label: RISKY

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
  File "/Users/armenzg/code/sentry/.venv/bin/sentry", line 33, in <module>
    sys.exit(load_entry_point('sentry', 'console_scripts', 'sentry')())
  File "/Users/armenzg/code/sentry/src/sentry/runner/__init__.py", line 186, in main
    raise e
  File "/Users/armenzg/code/sentry/src/sentry/runner/__init__.py", line 178, in main
    func(**kwargs)
  File "/Users/armenzg/code/sentry/.venv/lib/python3.8/site-packages/click/core.py", line 1128, in __call__
    return self.main(*args, **kwargs)
  File "/Users/armenzg/code/sentry/.venv/lib/python3.8/site-packages/click/core.py", line 1053, in main
    rv = self.invoke(ctx)
  File "/Users/armenzg/code/sentry/.venv/lib/python3.8/site-packages/click/core.py", line 1659, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/Users/armenzg/code/sentry/.venv/lib/python3.8/site-packages/click/core.py", line 1395, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/Users/armenzg/code/sentry/.venv/lib/python3.8/site-packages/click/core.py", line 754, in invoke
    return __callback(*args, **kwargs)
  File "/Users/armenzg/code/sentry/.venv/lib/python3.8/site-packages/click/decorators.py", line 26, in new_func
    return f(get_current_context(), *args, **kwargs)
  File "/Users/armenzg/code/sentry/src/sentry/runner/decorators.py", line 69, in inner
    return ctx.invoke(f, *args, **kwargs)
  File "/Users/armenzg/code/sentry/.venv/lib/python3.8/site-packages/click/core.py", line 754, in invoke
    return __callback(*args, **kwargs)
  File "/Users/armenzg/code/sentry/.venv/lib/python3.8/site-packages/click/decorators.py", line 26, in new_func
    return f(get_current_context(), *args, **kwargs)
  File "/Users/armenzg/code/sentry/src/sentry/runner/decorators.py", line 29, in inner
    return ctx.invoke(f, *args, **kwargs)
  File "/Users/armenzg/code/sentry/.venv/lib/python3.8/site-packages/click/core.py", line 754, in invoke
    return __callback(*args, **kwargs)
  File "/Users/armenzg/code/sentry/src/sentry/runner/commands/devserver.py", line 215, in devserver
    port = port + 1
TypeError: unsupported operand type(s) for +: 'NoneType' and 'int
```
```

## Diff of the target file

```diff
@@ -1,5 +1,5 @@
 class Service:
     name = ""
 
-    def __init__(self, debug=False):
+    def __init__(self, debug: bool = False) -> None:
         self.debug = debug
```

## Lines SZZ blamed (line numbers in the new version)

```
    4      def __init__(self, debug: bool = False) -> None:
```

## Candidate fixes (0 later commits to this file remove a blamed line; 0 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

# case130: getsentry/sentry c48fda09e252

File: `src/sentry/utils/hashlib.py` · committed 2022-09-12 01:49:00-01:00 · SZZ label: RISKY

## Commit message

```
feat(metrics): Add  cardinality limiter to indexer [sns-1651] (#38428)

Reopen of https://github.com/getsentry/sentry/pull/38302 to avoid
notification spam

See #38257 and
https://www.notion.so/sentry/Metrics-Dimensionality-Limiting-df010a6a6d4e467ca3c5c19230db862b#4966fb9c07fc4394b720ad161c99a096.
This is just the glue code and configuration options for using the
cardinality limiter in the indexer. The actual implementation is TBD.
This is safe to merge because the stub implementation does not actually
limit anything at all, so it should be fast enough to do synchronously
for now

## rollout plan

- [x] https://github.com/getsentry/sentry/pull/38446
- [x] set options to nothing in prod
- [ ] merge + deploy this PR
- [ ] check prod metrics: redis should not be used
- [ ] https://github.com/getsentry/sentry/pull/38445
- [ ] check prod metrics: redis should still not be used
- [ ] run qe tests?
- [ ] get a redis cluster and configure it
- [ ] run use_quota on a separate thread
- [ ] set a quota
- [ ] get rid of writes limiter?
- [ ] stop indexing tag values

Co-authored-by: getsantry[bot] <66042841+getsantry[bot]@users.noreply.github.com>
Co-authored-by: Nikhar Saxena <nikhar.saxena@sentry.io>
```

## Diff of the target file

```diff
@@ -38,7 +38,7 @@ def hash_value(h: hashlib._Hash, value: Any) -> None:
             hash_value(h, item)
     elif isinstance(value, dict):
         h.update(b"\x05" + str(len(value)).encode("utf-8"))
-        for k, v in value.items():
+        for k, v in sorted(value.items()):
             hash_value(h, k)
             hash_value(h, v)
     elif isinstance(value, bytes):
```

## Lines SZZ blamed (line numbers in the new version)

```
   41          for k, v in sorted(value.items()):
```

## Candidate fixes (0 later commits to this file remove a blamed line; 1 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

# case130: getsentry/sentry c48fda09e252

Sampled file (the only file the models saw): `src/sentry/utils/hashlib.py` · committed 2022-09-12 01:49:00-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

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
Co-authored-by: Nikhar Saxena <nikhar.saxena@
[... cut ...]
```

## Diff of the sampled file

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

## Other files changed by this commit (14)

- `src/sentry/ratelimits/cardinality.py` (+8 −4)
- `src/sentry/sentry_metrics/configuration.py` (+12 −0)
- `src/sentry/sentry_metrics/consumers/indexer/batch.py` (+63 −6)
- `src/sentry/sentry_metrics/consumers/indexer/processing.py` (+14 −0)
- `src/sentry/sentry_metrics/indexer/cloudspanner/cloudspanner.py` (+1 −1)
- `src/sentry/sentry_metrics/indexer/limiters/__init__.py` (+0 −0)
- `src/sentry/sentry_metrics/indexer/limiters/cardinality.py` (+152 −0)
- `src/sentry/sentry_metrics/indexer/limiters/writes.py` (+0 −0)
- `src/sentry/sentry_metrics/indexer/postgres/postgres_v2.py` (+1 −1)
- `tests/sentry/sentry_metrics/limiters/test_cardinality_limiter.py` (+111 −0)
- `tests/sentry/sentry_metrics/limiters/test_writes_limiter.py` (+1 −1)
- `tests/sentry/sentry_metrics/test_batch.py` (+92 −1)
- `tests/sentry/sentry_metrics/test_multiprocess_steps.py` (+44 −0)
- `tests/sentry/sentry_metrics/test_parallel_indexer.py` (+3 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 017a7f2bac5b (2022-09-14) · pull request #38794: fix(metrics): Ability to configure releasehealth cluster [sns-1651]

Pull-request labels: Scope: Backend

Commit message:

```
fix(metrics): Ability to configure releasehealth cluster [sns-1651] (#38794)
```

Pull-request description:

```
We are not going to configure any releasehealth quotas, but still need
to be able to connect to a valid redis cluster if we wanted to do so.

We probably don't want to get rid of all the limiting code related to
releasehealth because that's the only way we can test things in the QE
environment.
```

This fix changes 2 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/sentry/sentry_metrics/configuration.py`: `cardinality_limiter_cluster_options={},`

Patch of `src/sentry/sentry_metrics/configuration.py` in this fix:

```diff
@@ -62,7 +62,7 @@ def get_ingest_config(
                 internal_metrics_tag="release-health",
                 writes_limiter_cluster_options=settings.SENTRY_METRICS_INDEXER_WRITES_LIMITER_OPTIONS,
                 writes_limiter_namespace=RELEASE_HEALTH_PG_NAMESPACE,
-                cardinality_limiter_cluster_options={},
+                cardinality_limiter_cluster_options=settings.SENTRY_METRICS_INDEXER_CARDINALITY_LIMITER_OPTIONS,
                 cardinality_limiter_namespace=RELEASE_HEALTH_PG_NAMESPACE,
             )
         )
```

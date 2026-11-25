# case140: getsentry/sentry dba4bbf6a63a

Sampled file (the only file the models saw): `src/sentry/dynamic_sampling/feature_multiplexer.py` · committed 2022-10-25 22:55:34-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
feat(ds): Send boosted releases to relay as part of ProjectConfig [TET-497] (#40415)

Sends boosted release ids as dynamic sampling with start and end time
ranges to relay as part of the project config
Continuation of #40403

Co-authored-by: getsantry[bot] <66042841+getsantry[bot]@users.noreply.github.com>
```

## Diff of the sampled file

```diff
@@ -60,13 +60,11 @@ class DynamicSamplingFeatureMultiplexer:
                 returned_biases.append(bias)
         return returned_biases
 
+    @classmethod
+    def get_enabled_user_biases(cls, user_set_biases: Optional[List[Bias]]) -> Set[str]:
+        users_biases = cls.get_user_biases(user_set_biases)
+        return {bias["id"] for bias in users_biases if bias["active"]}
+
     @staticmethod
     def get_supported_biases_ids() -> Set[str]:
         return {bias["id"] for bias in DEFAULT_BIASES}
-
-    @classmethod
-    def get_user_bias_by_id(cls, bias_id: str, user_set_biases: Optional[List[Bias]]) -> Bias:
-        for bias in cls.get_user_biases(user_set_biases):
-            if bias["id"] == bias_id:
-                return bias
-        raise ValueError(f"{bias_id} is not in supported biases")
```

## Other files changed by this commit (10)

- `mypy.ini` (+1 −0)
- `src/sentry/dynamic_sampling/__init__.py` (+0 −32)
- `src/sentry/dynamic_sampling/latest_release_booster.py` (+9 −8)
- `src/sentry/dynamic_sampling/rules_generator.py` (+135 −0)
- `src/sentry/dynamic_sampling/utils.py` (+26 −35)
- `src/sentry/event_manager.py` (+1 −1)
- `src/sentry/relay/config/__init__.py` (+1 −1)
- `tests/sentry/dynamic_sampling/test_generate_rules.py` (+149 −15)
- `tests/sentry/dynamic_sampling/test_utils.py` (+3 −3)
- `tests/sentry/relay/test_config.py` (+160 −6)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 221709610f25 (2022-11-02) · pull request #40890: fix(ds): reorder dyn-sampling rules

Pull-request labels: Scope: Backend

Commit message:

```
fix(ds): reorder dyn-sampling rules (#40890)

This PR reorders dyn sampling final list of rules so:
1. prioritise dev environments
2. ignore health check 
3. prioritise latest release
```

Pull-request description:

```
This PR reorders dyn sampling final list of rules so:
1. prioritise dev environments
2. ignore health check 
3. prioritise latest release
```

This fix changes 2 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/sentry/dynamic_sampling/rules_generator.py`: `if RuleType.BOOST_LATEST_RELEASES_RULE.value in enabled_biases:`; `rules += generate_boost_release_rules(project.id, sample_rate)`
- in `tests/sentry/relay/test_config.py`: `"active": True,`; `"condition": {`; `"id": 1001,`; `"inner": [`; `"name": "trace.environment",`; `"op": "glob",`

Patch of `src/sentry/dynamic_sampling/rules_generator.py` in this fix:

```diff
@@ -148,9 +148,6 @@ def generate_rules(project: Project) -> List[Union[BaseRule, ReleaseRule]]:
             enabled_biases = DynamicSamplingFeatureMultiplexer.get_enabled_user_biases(
                 project.get_option("sentry:dynamic_sampling_biases", None)
             )
-            # Latest releases
-            if RuleType.BOOST_LATEST_RELEASES_RULE.value in enabled_biases:
-                rules += generate_boost_release_rules(project.id, sample_rate)
 
             # Environments boost
             if RuleType.BOOST_ENVIRONMENTS_RULE.value in enabled_biases:
@@ -159,6 +156,11 @@ def generate_rules(project: Project) -> List[Union[BaseRule, ReleaseRule]]:
             # Add Ignore health check rule
             if RuleType.IGNORE_HEALTHCHECKS_RULE.value in enabled_biases:
                 rules.append(generate_healthcheck_rule(sample_rate))
+
+            # Latest releases
+            if RuleType.BOOST_LATEST_RELEASES_RULE.value in enabled_biases:
+                rules += generate_boost_release_rules(project.id, sample_rate)
+
         rules.append(generate_uniform_rule(sample_rate))
 
     return rules
```

Patch of `tests/sentry/relay/test_config.py` in this fix:

```diff
@@ -420,6 +420,40 @@ def test_project_config_with_boosted_latest_releases_boost_in_dynamic_sampling_r
     dynamic_sampling = get_path(cfg, "config", "dynamicSampling")
     assert dynamic_sampling == {
         "rules": [
+            {
+                "sampleRate": 1,
+                "type": "trace",
+                "condition": {
+                    "op": "or",
+                    "inner": [
+                        {
+                            "op": "glob",
+                            "name": "trace.environment",
+                            "value": ["*dev*", "*test*"],
+                            "options": {"ignoreCase": True},
+                        }
+                    ],
+                },
+                "active": True,
+                "id": 1001,
+            },
+            {
+                "sampleRate": 0.02,
+                "type": "transaction",
+                "condition": {
+                    "op": "or",
+                    "inner": [
+                        {
+                            "op": "glob",
+                            "name": "event.transaction",
+                            "value": HEALTH_CHECK_GLOBS,
+                            "options": {"ignoreCase": True},
+                        }
+                    ],
+                },
+                "active": True,
+                "id": 1002,
+            },
             {
                 "sampleRate": 0.5,
                 "type": "trace",
@@ -490,40 +524,6 @@ def test_project_config_with_boosted_latest_releases_boost_in_dynamic_sampling_r
                     "end": "2022-10-21 19:50:25+00:00",
                 },
             },
-            {
-                "sampleRate": 1,
-                "type": "trace",
-                "condition": {
-                    "op": "or",
-                    "inner": [
-                        {
-                            "op": "glob",
-                            "name": "trace.environment",
-                            "value": ["*dev*", "*test*"],
-                            "options": {"ignoreCase": True},
-                        }
-                    ],
-                },
-                "active": True,
[... cut ...]
```

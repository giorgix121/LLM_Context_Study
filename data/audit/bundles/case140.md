# case140: getsentry/sentry dba4bbf6a63a

File: `src/sentry/dynamic_sampling/feature_multiplexer.py` · committed 2022-10-25 22:55:34-01:00 · SZZ label: RISKY

## Commit message

```
feat(ds): Send boosted releases to relay as part of ProjectConfig [TET-497] (#40415)

Sends boosted release ids as dynamic sampling with start and end time
ranges to relay as part of the project config
Continuation of #40403

Co-authored-by: getsantry[bot] <66042841+getsantry[bot]@users.noreply.github.com>
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
   63      @classmethod
   64      def get_enabled_user_biases(cls, user_set_biases: Optional[List[Bias]]) -> Set[str]:
   65          users_biases = cls.get_user_biases(user_set_biases)
   66          return {bias["id"] for bias in users_biases if bias["active"]}
   67  
```

## Candidate fixes (1 later commits to this file remove a blamed line; 3 later commits up to 2023-06-30 checked)

### Candidate 1: 01b1c6512c15 (2023-01-10)

Message:

```
ref(dynamic-sampling): Remove multiplexer (#42938)
```

Removed blamed lines: `@classmethod`; `def get_enabled_user_biases(cls, user_set_biases: Optional[List[Bias]]) -> Set[str]:`; `return {bias["id"] for bias in users_biases if bias["active"]}`; `users_biases = cls.get_user_biases(user_set_biases)`

Patch of this file:

```diff
@@ -1,41 +0,0 @@
-from typing import TYPE_CHECKING, List, Optional, Set
-
-from sentry import features, options
-from sentry.dynamic_sampling.utils import DEFAULT_BIASES, Bias
-
-if TYPE_CHECKING:
-    from sentry.models import Project
-
-
-class DynamicSamplingFeatureMultiplexer:
-    def __init__(self, project: "Project"):
-        # Feature flag that informs us that the org is on the new AM2 plan and thereby have adaptive
-        # sampling enabled
-        self.dynamic_sampling = features.has("organizations:dynamic-sampling", project.organization)
-
-    @property
-    def is_on_dynamic_sampling(self) -> bool:
-        return self.dynamic_sampling and options.get("dynamic-sampling:enabled-biases")
-
-    @staticmethod
-    def get_user_biases(user_set_biases: Optional[List[Bias]]) -> List[Bias]:
-        if user_set_biases is None:
-            return DEFAULT_BIASES
-
-        id_to_user_bias = {bias["id"]: bias for bias in user_set_biases}
-        returned_biases = []
-        for bias in DEFAULT_BIASES:
-            if bias["id"] in id_to_user_bias:
-                returned_biases.append(id_to_user_bias[bias["id"]])
-            else:
-                returned_biases.append(bias)
-        return returned_biases
-
-    @classmethod
-    def get_enabled_user_biases(cls, user_set_biases: Optional[List[Bias]]) -> Set[str]:
-        users_biases = cls.get_user_biases(user_set_biases)
-        return {bias["id"] for bias in users_biases if bias["active"]}
-
-    @staticmethod
-    def get_supported_biases_ids() -> Set[str]:
-        return {bias["id"] for bias in DEFAULT_BIASES}
```

# case116: Lightning-AI/lightning c81a71c90807

Sampled file (the only file the models saw): `src/lightning_app/cli/commands/connection.py` · committed 2022-09-13 06:43:15-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Lightning App Fixes from Training Studio App dev (#14532)

* update

* update

* update

* update

* update

* update

* update

* update

* update

* update

* update

* update

* update

* update

* update

* update

* update
```

## Diff of the sampled file

```diff
@@ -33,7 +33,8 @@ def connect(app_name_or_id: str, yes: bool = False):
             else:
                 click.echo(f"You are already connected to the cloud Lightning App: {app_name_or_id}.")
         else:
-            click.echo("You are already connected to a Lightning App. Please, use `lightning disconnect`.")
+            disconnect()
+            connect(app_name_or_id, yes)
 
     elif app_name_or_id.startswith("localhost"):
```

## Other files changed by this commit (13)

- `.lightningignore` (+17 −0)
- `src/lightning_app/CHANGELOG.md` (+6 −5)
- `src/lightning_app/cli/lightning_cli.py` (+15 −4)
- `src/lightning_app/core/api.py` (+4 −1)
- `src/lightning_app/core/app.py` (+10 −3)
- `src/lightning_app/core/constants.py` (+1 −0)
- `src/lightning_app/runners/runtime.py` (+0 −5)
- `src/lightning_app/testing/testing.py` (+10 −6)
- `src/lightning_app/utilities/cli_helpers.py` (+3 −1)
- `src/lightning_app/utilities/commands/base.py` (+4 −2)
- `src/lightning_app/utilities/proxies.py` (+23 −1)
- `tests/tests_app/cli/test_cmd_show_logs.py` (+2 −2)
- `tests/tests_app/components/python/test_python.py` (+2 −2)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 969a323345be (2022-10-21) · pull request #15235: [App] Optimise Queues Calls

Pull-request labels: bug, ready to be merged, app (removed)

Commit message:

```
[App] Optimise Queues Calls (#15235)
```

Pull-request description:

```
## What does this PR do?

<!--
Please include a summary of the change and which issue is fixed.
Please also include relevant motivation and context.
List any dependencies that are required for this change.

If we didn't discuss your PR in Github issues there's a high chance it will not be merged.

The following links the related issue to the PR (https://docs.github.com/en/free-pro-team@latest/github/managing-your-work-on-github/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword)
-->

Currently, the Boring App makes 1.2k queue calls per minute. This PR reduces this by some factors.

Here is the current repartition.

```python
ORCHESTRATOR_COPY_RESPONSE_root.dict.dst_w: 54
ORCHESTRATOR_COPY_REQUEST_root.dict.src_w: 182
API_RESPONSE_QUEUE: 131
ORCHESTRATOR_COPY_RESPONSE_root.dict.src_w: 54
ORCHESTRATOR_REQUEST_root.dict.dst_w: 54
API_DELTA_QUEUE: 57
DELTA_QUEUE: 57
ORCHESTRATOR_COPY_REQUEST_root.dict.dst_w: 182
API_STATE_PUBLISH_QUEUE: 131
ERROR_QUEUE: 58
ORCHESTRATOR_REQUEST_root.dict.src_w: 53
CALLER_QUEUE_root.dict.src_w: 183
```

Here is the new repartition:

TODO @hhsecond 

Fixes #\<issue_number>

### Does your PR introduce any breaking changes
[... cut ...]
```

This fix changes 9 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/lightning_app/core/app.py`: `deltas.append(new_work_delta)`; `logger.error(f"The component {component_output.id} couldn't be accessed. Exception: {e}")`; `new_work_delta = _delta_to_app_state_delta(self.root, work, deepcopy(component_output.delta))`; `work = self.get_component_by_name(component_output.id)`

Patch of `src/lightning_app/core/app.py` in this fix:

```diff
@@ -298,44 +298,35 @@ def _collect_deltas_from_ui_and_work_queues(self) -> List[Union[Delta, APIReques
         # during the `state_accumulate_wait` time.
         # The while loop can exit sooner if both queues are empty.
 
-        should_get_delta_from_api = True
-        should_get_component_output = True
         deltas = []
+        api_or_command_request_deltas = []
         t0 = time()
 
         while (time() - t0) < self.state_accumulate_wait:
 
-            if self.api_delta_queue and should_get_delta_from_api:
-                delta_from_api: Union[DeltaRequest, APIRequest, CommandRequest] = self.get_state_changed_from_queue(
-                    self.api_delta_queue
-                )  # TODO: rename
-                if delta_from_api:
-                    if isinstance(delta_from_api, DeltaRequest):
-                        delta_from_api = delta_from_api.delta
-                    deltas.append(delta_from_api)
-                else:
-                    should_get_delta_from_api = False
-
-            if self.delta_queue and should_get_component_output:
-                component_output: Optional[ComponentDelta] = self.get_state_changed_from_queue(self.delta_queue)
-                if component_output:
-                    logger.debug(f"Received from {component_output.id} : {component_output.delta.to_dict()}")
-
+            # TODO: Fetch all available deltas at once to reduce queue calls.
+            delta: Optional[
+                Union[DeltaRequest, APIRequest, CommandRequest, ComponentDelta]
+            ] = self.get_state_changed_from_queue(self.delta_queue)
+            if delta:
+                if isinstance(delta, DeltaRequest):
+                    deltas.append(delta.delta)
+                elif isinstance(delta, ComponentDelta):
+                    logger.debug(f"Received from {delta.id} : {delta.delta.to_dict()}")
                     work = None
                     try:
-                        work = self.get_component_by_name(component_output.id)
+                        work = self.get_component_by_name(delta.id)
                     except (KeyError, AttributeError) as e:
-                        logger.error(f"The componen
[... cut ...]
```

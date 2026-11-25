# case063: Lightning-AI/lightning d579733b081e

Sampled file (the only file the models saw): `src/lightning_app/utilities/cli_helpers.py` · committed 2022-09-14 09:44:59-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Lightning cloud client call with key word arguments (#14685)
```

## Diff of the sampled file

```diff
@@ -103,7 +103,9 @@ def _retrieve_application_url_and_available_commands(app_id_or_name_or_url: Opti
     else:
         client = LightningClient()
         project = _get_project(client)
-        list_lightningapps = client.lightningapp_instance_service_list_lightningapp_instances(project.project_id)
+        list_lightningapps = client.lightningapp_instance_service_list_lightningapp_instances(
+            project_id=project.project_id
+        )
 
         lightningapp_names = [lightningapp.name for lightningapp in list_lightningapps.lightningapps]
```

## Other files changed by this commit (11)

- `src/lightning_app/CHANGELOG.md` (+1 −0)
- `src/lightning_app/cli/cmd_apps.py` (+5 −5)
- `src/lightning_app/cli/commands/connection.py` (+3 −1)
- `src/lightning_app/cli/lightning_cli.py` (+3 −1)
- `src/lightning_app/runners/cloud.py` (+9 −9)
- `src/lightning_app/testing/testing.py` (+2 −2)
- `src/lightning_app/utilities/cluster_logs.py` (+2 −3)
- `src/lightning_app/utilities/commands/base.py` (+3 −1)
- `tests/tests_app/cli/test_cloud_cli.py` (+1 −1)
- `tests/tests_app/runners/test_cloud.py` (+17 −16)
- `tests/tests_app_examples/conftest.py` (+0 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 75e6c9109c7f (2022-09-15) · pull request #14458: [CLI] Fix cluster logs with over 5000 entries

Pull-request labels: bug, ready to be merged, app (removed)

Commit message:

```
[CLI] Fix cluster logs with over 5000 entries (#14458)
```

Pull-request description:

```
## What does this PR do?

Fixes https://linear.app/lightning-ai/issue/GRID-10410/very-large-limits-say-10000-dont-work-error-400 partially. 

Today if you try to fetch gridv1.Cluster logs in the CLI and want more than 5000 lines it'll brake due to internal limitations. This PR implements batching, thus we're fetching 5000 by 5000 log lines from the API server. 


### Does your PR introduce any breaking changes? If yes, please list them.

No

## Before submitting

- [x] Was this **discussed/approved** via a GitHub issue? (not for typos and docs)
- [x] Did you read the [contributor guideline](https://github.com/Lightning-AI/lightning/blob/master/.github/CONTRIBUTING.md), **Pull Request** section?
- [x] Did you make sure your **PR does only one thing**, instead of bundling different changes together?
- [x] Did you make sure to **update the documentation** with your changes? (if necessary)
- [x] Did you write any **new necessary tests**? (not for typos and docs)
- [x] Did you verify new and **existing tests pass** locally with your changes?
- [x] Did you list all the **breaking changes** introduced by this pull request?
- [x] Did you **update the CHANGELOG**? (not for typos, docs, test
[... cut ...]
```

This fix changes 9 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/lightning_app/utilities/cluster_logs.py`: `end: int,`; `start: int,`

Patch of `src/lightning_app/utilities/cluster_logs.py` in this fix:

```diff
@@ -1,100 +1,127 @@
 import json
 import queue
 from dataclasses import dataclass
+from datetime import timedelta
 from threading import Thread
-from typing import Callable, Iterator, Optional
+from typing import Callable, Iterator, List, Optional
 
 import dateutil.parser
 from websocket import WebSocketApp
 
-from lightning_app.utilities.log_helpers import _error_callback, _OrderedLogEntry
+from lightning_app.utilities.data_structures import AttributeDict
+from lightning_app.utilities.exceptions import LogLinesLimitExceeded
+from lightning_app.utilities.log_helpers import _OrderedLogEntry
 from lightning_app.utilities.logs_socket_api import _ClusterLogsSocketAPI
-from lightning_app.utilities.network import LightningClient
 
 
-@dataclass
-class _ClusterLogEventLabels:
+class _ClusterLogEventLabels(AttributeDict):
     cluster_id: str
     grid_url: str
     hostname: str
     level: str
     logger: str
-    path: Optional[str] = None
-    workspace: Optional[str] = None
-    identifier: Optional[str] = None
-    issuer: Optional[str] = None
-    error: Optional[str] = None
-    errorVerbose: Optional[str] = None
-    dir: Optional[str] = None
-    bucket: Optional[str] = None
-    prefix: Optional[str] = None
-    loki_s3: Optional[str] = None
 
 
 @dataclass
 class _ClusterLogEvent(_OrderedLogEntry):
     labels: _ClusterLogEventLabels
 
 
-def _push_log_events_to_read_queue_callback(read_queue: queue.PriorityQueue):
+def _push_log_events_to_read_queue_callback(read_queue: queue.Queue):
     """Pushes _LogEvents from websocket to read_queue.
 
     Returns callback function used with `on_message_callback` of websocket.WebSocketApp.
     """
 
-    def callback(ws_app: WebSocketApp, msg: str):
-        # We strongly trust that the contract on API will hold atm :D
-        event_dict = json.loads(msg)
-        labels = _ClusterLogEventLabels(**event_dict["labels"])
-
-        if "message" in event_dict:
-            message = event_dict["message"]
-            timestamp = dateutil.parser.isoparse(event_dict["timestamp"])
-            event = _ClusterLogEvent(
-                message=message,
-                timestamp=timestamp,
-                labels=labels
[... cut ...]
```

# case089: Lightning-AI/lightning b936fd4380ce

Sampled file (the only file the models saw): `src/lightning_app/utilities/packaging/lightning_utils.py` · committed 2022-10-04 18:46:44-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
[app] Add CloudCompute ID serializable within the flow and works state  (#14819)
```

## Diff of the sampled file

```diff
@@ -110,7 +110,7 @@ def _prepare_lightning_wheels_and_requirements(root: Path) -> Optional[Callable]
     download_frontend(_PROJECT_ROOT)
     _prepare_wheel(_PROJECT_ROOT)
 
-    logger.info("Packaged Lightning with your application.")
+    logger.info(f"Packaged Lightning with your application. Version: {version}")
 
     tar_name = _copy_tar(_PROJECT_ROOT, root)
 
@@ -121,7 +121,9 @@ def _prepare_lightning_wheels_and_requirements(root: Path) -> Optional[Callable]
         # building and copying launcher wheel if installed in editable mode
         launcher_project_path = get_dist_path_if_editable_install("lightning_launcher")
         if launcher_project_path:
-            logger.info("Packaged Lightning Launcher with your application.")
+            from lightning_launcher.__version__ import __version__ as launcher_version
+
+            logger.info(f"Packaged Lightning Launcher with your application. Version: {launcher_version}")
             _prepare_wheel(launcher_project_path)
             tar_name = _copy_tar(launcher_project_path, root)
             tar_files.append(os.path.join(root, tar_name))
@@ -129,7 +131,9 @@ def _prepare_lightning_wheels_and_requirements(root: Path) -> Optional[Callable]
         # building and copying lightning-cloud wheel if installed in editable mode
         lightning_cloud_project_path = get_dist_path_if_editable_install("lightning_cloud")
         if lightning_cloud_project_path:
-            logger.info("Packaged Lightning Cloud with your application.")
+            from lightning_cloud.__version__ import __version__ as cloud_version
+
+            logger.info(f"Packaged Lightning Cloud with your application. Version: {cloud_version}")
             _prepare_wheel(lightning_cloud_project_path)
             tar_name = _copy_tar(lightning_cloud_project_path, root)
             tar_files.append(os.path.join(root, tar_name))
```

## Other files changed by this commit (22)

- `.gitignore` (+2 −1)
- `examples/app_layout/requirements.txt` (+1 −0)
- `examples/app_works_on_default_machine/.lightning` (+1 −0)
- `examples/app_works_on_default_machine/app_v2.py` (+53 −0)
- `examples/app_works_on_default_machine/requirements.txt` (+1 −0)
- `requirements/app/base.txt` (+1 −1)
- `src/lightning_app/CHANGELOG.md` (+2 −0)
- `src/lightning_app/core/constants.py` (+9 −1)
- `src/lightning_app/core/flow.py` (+9 −0)
- `src/lightning_app/core/work.py` (+23 −3)
- `src/lightning_app/runners/backends/mp_process.py` (+2 −2)
- `src/lightning_app/runners/cloud.py` (+30 −1)
- `src/lightning_app/utilities/component.py` (+5 −0)
- `src/lightning_app/utilities/layout.py` (+2 −0)
- `src/lightning_app/utilities/network.py` (+2 −2)
- `src/lightning_app/utilities/packaging/cloud_compute.py` (+66 −3)
- `tests/tests_app/conftest.py` (+2 −0)
- `tests/tests_app/core/test_lightning_app.py` (+75 −7)
- `tests/tests_app/core/test_lightning_flow.py` (+44 −0)
- `tests/tests_app/structures/test_structures.py` (+66 −0)
- `tests/tests_app/utilities/packaging/test_lightning_utils.py` (+3 −2)
- `tests/tests_app/utilities/test_load_app.py` (+3 −3)

## Fix commits that the dataset links to this commit (4)

### Fix 1: 8ec7ddf317ad (2022-10-20) · pull request #15215: [App] Pass LightningWork to LightningApp

Pull-request labels: bug, ready to be merged, priority: 0, app (removed)

Commit message:

```
[App] Pass LightningWork to LightningApp (#15215)

* update

* update

* update

* Apply suggestions from code review

* Apply suggestions from code review

* Apply suggestions from code review

* ll

Co-authored-by: Jirka Borovec <Borda@users.noreply.github.com>
Co-authored-by: Jirka <jirka.borovec@seznam.cz>
Co-authored-by: Luca Antiga <luca.antiga@gmail.com>
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

This feature was requested by @williamFalcon and enables passing work to the LightningApp as well as a flow.

This meant mainly removing boilerplate from documentation examples.

### Does your PR introduce any breaking changes? If yes, please list them.

<!-- FILL IN or None -->

## Before submitting

- [x] Was this **discussed/approved** via a GitHub issue? (not for typos and docs)
- [x] Did you read the [contributor guideline](https://github.com/Lightning-AI/lightning/blob/master/.github/CONTRIBUTING.md), **Pull Request** section?
- [x] Did you make sure your **PR does only one thing**, instead of bundling different changes together?
- [ ] Did you make sure to **upd
[... cut ...]
```

This fix changes 5 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `tests/tests_app/conftest.py`: `cloud_compute._CLOUD_COMPUTE_STORE.clear()`

Patch of `tests/tests_app/conftest.py` in this fix:

```diff
@@ -75,7 +75,8 @@ def clear_app_state_state_variables():
     lightning_app.utilities.state._STATE = None
     lightning_app.utilities.state._LAST_STATE = None
     AppState._MY_AFFILIATION = ()
-    cloud_compute._CLOUD_COMPUTE_STORE.clear()
+    if hasattr(cloud_compute, "_CLOUD_COMPUTE_STORE"):
+        cloud_compute._CLOUD_COMPUTE_STORE.clear()
 
 
 @pytest.fixture
```

### Fix 2: 921dc1cd9afb (2022-11-03) · pull request #15466: [App] Resolve inconsistency where the `flow.flows` property isn't recursive leading to flow overrides

Pull-request labels: bug, ready to be merged, app (removed)

Commit message:

```
[App] Resolve inconsistency where the `flow.flows` property isn't recursive leading to flow overrides (#15466)

* update

* update

* update

* update

* update

* resolve attachment

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

The main issues was the flow.flows call that collected the flows using their attribute name. If 2 flows had the same attribute name, they would ended up overriding themselves.

Fixes #\<issue_number>

### Does your PR introduce any breaking changes? If yes, please list them.

<!-- FILL IN or None -->

## Before submitting

- [x] Was this **discussed/approved** via a GitHub issue? (not for typos and docs)
- [x] Did you read the [contributor guideline](https://github.com/Lightning-AI/lightning/blob/master/.github/CONTRIBUTING.md), **Pull Request** section?
- [x] Did you make sure your **PR does only one thing**, instead of bundling different changes together?
- [x] Did
[... cut ...]
```

This fix changes 13 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `tests/tests_app/utilities/test_load_app.py`: `"cloud_compute": ANY,`

Patch of `tests/tests_app/utilities/test_load_app.py` in this fix:

```diff
@@ -30,12 +30,6 @@ def test_extract_metadata_from_component():
     app = load_app_from_file(os.path.join(test_script_dir, "app_metadata.py"))
     metadata = extract_metadata_from_app(app)
     assert metadata == [
-        {
-            "affiliation": ["root"],
-            "cls_name": "RootFlow",
-            "module": "__main__",
-            "docstring": "RootFlow.",
-        },
         {
             "affiliation": ["root", "flow_a_1"],
             "cls_name": "FlowA",
@@ -48,8 +42,16 @@ def test_extract_metadata_from_component():
             "module": "__main__",
             "docstring": "WorkA.",
             "local_build_config": {"__build_config__": ANY},
-            "cloud_build_config": {"__build_config__": ANY},
-            "cloud_compute": ANY,
+            "cloud_build_config": {"__build_config__": {"requirements": [], "dockerfile": [], "image": None}},
+            "cloud_compute": {
+                "type": "__cloud_compute__",
+                "name": "default",
+                "disk_size": 0,
+                "idle_timeout": None,
+                "shm_size": 0,
+                "mounts": None,
+                "_internal_id": "default",
+            },
         },
         {
             "affiliation": ["root", "flow_a_2"],
@@ -62,23 +64,34 @@ def test_extract_metadata_from_component():
             "cls_name": "WorkA",
             "module": "__main__",
             "docstring": "WorkA.",
-            "local_build_config": {"__build_config__": ANY},
-            "cloud_build_config": {"__build_config__": ANY},
-            "cloud_compute": ANY,
-        },
-        {
-            "affiliation": ["root", "flow_b"],
-            "cls_name": "FlowB",
-            "module": "__main__",
-            "docstring": "FlowB.",
+            "local_build_config": {"__build_config__": {"requirements": [], "dockerfile": [], "image": None}},
+            "cloud_build_config": {"__build_config__": {"requirements": [], "dockerfile": [], "image": None}},
+            "cloud_compute": {
+                "type": "__cloud_compute__",
+                "name": "default",
+                "disk_size": 0,
+                "idle_timeout": None,
+
[... cut ...]
```

### Fix 3: bbf7848a5f3f (2022-10-28) · pull request #15383: [App] Fix cluster logic

Pull-request labels: bug, ready to be merged, app (removed)

Commit message:

```
[App] Fix cluster logic (#15383)
```

Pull-request description:

```
## What does this PR do?

Fixes cluster logic with the following:
- if the provided cluster is `None` and there is no cluster in the `.lightning` file and the app doesn't already exist, we run the app then retrieve the cluster that it ran on and save it in the `.lightning` file
- if the provided cluster is `None` and there is no cluster in the `.lightning` file and the app already exists, we run the app on the existing cluster and save it in the `.lightning` file
- if the provided cluster is `None` and there is a cluster in the `.lightning` file, we run the app on that cluster
- if the provided cluster is not `None` and the app already exists on a different cluster, you get an error
- if the cluster doesn't exist, a confirmation dialog checks if you want to run on lightning cloud instead

### Does your PR introduce any breaking changes? If yes, please list them.

<!-- FILL IN or None -->

## Before submitting

- [x] Was this **discussed/approved** via a GitHub issue? (not for typos and docs)
- [x] Did you read the [contributor guideline](https://github.com/Lightning-AI/lightning/blob/master/.github/CONTRIBUTING.md), **Pull Request** section?
- [x] Did you make sure your **PR does o
[... cut ...]
```

This fix changes 19 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `examples/app_works_on_default_machine/.lightning`: `name: app_works_on_default_machine`
- in `src/lightning_app/runners/cloud.py`: `network_configs: List[V1NetworkConfig] = []`; `release_body.network_config = network_configs`

Patch of `examples/app_works_on_default_machine/.lightning` in this fix:

```diff
@@ -1 +0,0 @@
-name: app_works_on_default_machine
```

Patch of `src/lightning_app/runners/cloud.py` in this fix:

```diff
@@ -8,6 +8,7 @@
 from pathlib import Path
 from typing import Any, Callable, List, Optional, Union
 
+import click
 from lightning_cloud.openapi import (
     Body3,
     Body4,
@@ -106,7 +107,9 @@ def dispatch(
             # Override the name if provided by the CLI
             app_config.name = name
 
-        app_config.save_to_dir(root)
+        if cluster_id:
+            # Override the cluster ID if provided by the CLI
+            app_config.cluster_id = cluster_id
 
         print(f"The name of the app is: {app_config.name}")
 
@@ -195,7 +198,6 @@ def dispatch(
                 random_name = "".join(random.choice(string.ascii_lowercase) for _ in range(5))
                 spec = V1LightningworkSpec(
                     build_spec=build_spec,
-                    cluster_id=cluster_id,
                     drives=drive_specs,
                     user_requested_compute_config=user_compute_config,
                     network_config=[V1NetworkConfig(name=random_name, port=work.port)],
@@ -247,21 +249,9 @@ def dispatch(
                     project_id=project.project_id, body=app_body
                 )
 
-            release_body = Body8(
-                app_entrypoint_file=app_spec.app_entrypoint_file,
-                enable_app_server=app_spec.enable_app_server,
-                flow_servers=app_spec.flow_servers,
-                image_spec=app_spec.image_spec,
-                cluster_id=cluster_id,
-                works=[V1Work(name=work_req.name, spec=work_req.spec) for work_req in work_reqs],
-                local_source=True,
-                dependency_cache_key=app_spec.dependency_cache_key,
-                user_requested_flow_compute_config=app_spec.user_requested_flow_compute_config,
-            )
-
+            network_configs: Optional[List[V1NetworkConfig]] = None
             if ENABLE_MULTIPLE_WORKS_IN_DEFAULT_CONTAINER:
-                network_configs: List[V1NetworkConfig] = []
-
+                network_configs = []
                 initial_port = 8080 + 1 + len(frontend_specs)
                 for _ in range(DEFAULT_NUMBER_OF_EXPOSED_PORTS):
                     network_configs.append(
@@ -272,11 +262,6 @@ def dispatch(
[... cut ...]
```

### Fix 4: bd658441bd01 (2022-10-25) · pull request #15286: [App] testing `lightning` in `lightning-app` package

Pull-request labels: bug, ready to be merged, app (removed)

Commit message:

```
[App] testing `lightning` in `lightning-app` package (#15286)

* hot fix

* update

* update

* update

* cmd

* pkg

* update

* Apply suggestions from code review

* update

* update

* Apply suggestions from code review

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

* cleaning

* Apply suggestions from code review

* update

* update

Co-authored-by: Jirka <jirka.borovec@seznam.cz>
Co-authored-by: Jirka Borovec <Borda@users.noreply.github.com>
```

Pull-request description:

```
## What does this PR do?


In the e2e CI, we are installing lightning in editable mode.
When `get_dist_path_if_editable_install("lightning")`  was changed to `get_dist_path_if_editable_install("lightning-app")` , the code started to exit early there as we get the followings:

```python
(Pdb) get_dist_path_if_editable_install("lightning")
'/Users/thomas/Documents/GitHub/lightning/src'
(Pdb) get_dist_path_if_editable_install("lightning-app")
''
(Pdb) 
```

Therefore, the lightning wheels aren’t generated and the code isn’t uploaded with the app code.
So, we weren’t testing the PR code but latest release on PiPy.

closes #15294

## Before submitting

- [ ] Was this **discussed/approved** via a GitHub issue? (not for typos and docs)
- [x] Did you read the [contributor guideline](https://github.com/Lightning-AI/lightning/blob/master/.github/CONTRIBUTING.md), **Pull Request** section?
- [x] Did you make sure your **PR does only one thing**, instead of bundling different changes together?
- [ ] Did you make sure to **update the documentation** with your changes? (if necessary)
- [ ] Did you write any **new necessary tests**? (not for typos and docs)
- [ ] Did you verify new and **existing
[... cut ...]
```

This fix changes 10 files. Lines it removes that the commit above had added:

- in the sampled file: `logger.info(f"Packaged Lightning Cloud with your application. Version: {cloud_version}")`; `logger.info(f"Packaged Lightning Launcher with your application. Version: {launcher_version}")`; `logger.info(f"Packaged Lightning with your application. Version: {version}")`
- in other files of the commit: none

Patch of the sampled file in this fix:

```diff
@@ -56,6 +56,7 @@ def _prepare_wheel(path):
             ["rm", "-r", "dist"], stdout=logfile, stderr=logfile, bufsize=0, close_fds=True, cwd=path
         ) as proc:
             proc.wait()
+
         with subprocess.Popen(
             ["python", "setup.py", "sdist"],
             stdout=logfile,
@@ -85,34 +86,39 @@ def get_dist_path_if_editable_install(project_name) -> str:
     for path_item in sys.path:
         if not os.path.isdir(path_item):
             continue
+
         egg_info = os.path.join(path_item, project_name + ".egg-info")
         if os.path.isdir(egg_info):
             return path_item
     return ""
 
 
-def _prepare_lightning_wheels_and_requirements(root: Path) -> Optional[Callable]:
+def _prepare_lightning_wheels_and_requirements(root: Path, package_name: str = "lightning") -> Optional[Callable]:
     """This function determines if lightning is installed in editable mode (for developers) and packages the
     current lightning source along with the app.
 
     For normal users who install via PyPi or Conda, then this function does not do anything.
     """
-
-    if not get_dist_path_if_editable_install("lightning-app"):
+    if not get_dist_path_if_editable_install(package_name):
         return
 
+    # this is patch for installing `lightning-app` as standalone package
+    if package_name == "lightning_app":
+        os.environ["PACKAGE_NAME"] = "app"
+
     # Packaging the Lightning codebase happens only inside the `lightning` repo.
     git_dir_name = get_dir_name() if check_github_repository() else None
 
-    is_lightning = git_dir_name and git_dir_name == "lightning_app"
+    is_lightning = git_dir_name and git_dir_name == package_name
 
     if (PACKAGE_LIGHTNING is None and not is_lightning) or PACKAGE_LIGHTNING == "0":
         return
 
     download_frontend(_PROJECT_ROOT)
     _prepare_wheel(_PROJECT_ROOT)
 
-    logger.info(f"Packaged Lightning with your application. Version: {version}")
+    # todo: check why logging.info is missing in outputs
+    print(f"Packaged Lightning with your application. Version: {version}")
 
     tar_name = _copy_tar(_PROJECT_ROOT, root)
 
@@ -125,7 +131,8 @@ def _prepare_lightning_wheels_and_requirements(root: Path) -> Optional[Callable]
         if launcher_project_path:
             from lightning_launcher.__version__ import __version__ as launcher_version
 
-            logger.info(f"Packaged Lightning Launcher with your application. Version: {launcher_version}")
+            # todo: check why logging.info is missing in outputs
+            print(f"Packaged Lightning Launcher with your application. Version: {launcher_version}")
             _prepare_wheel(launcher_project_path)
             tar_name = _copy_tar(launcher_project_path, root)
             tar_files.append(os.path.join(root, tar_name))
@@ -135,7 +142,8 @@ def _prepare_lightning_wheels_and_requirements(root: Path) -> Optional[Callable]
         if lightning_cloud_project_path:
             from lightning_cloud.__version__ import __version__ as cloud_version
 
-            logger.info(f"Packaged Lightning Cloud with your application. Version: {cloud_version}")
+            # todo: check why logging.info is missing in outputs
+            print(f"Packaged Lightning Cloud with your application. Version: {cloud_version}")
             _prepare_wheel(lightning_cloud_project_path)
             tar_name = _copy_tar(lightning_cloud_project_path, root)
             tar_files.append(os.path.join(root, tar_name))
```

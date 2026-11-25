# case124: Lightning-AI/lightning be1eb5e86d07

Sampled file (the only file the models saw): `src/lightning_app/utilities/packaging/lightning_utils.py` · committed 2022-10-22 14:20:49-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
CI: apps (#15242)

* CI: apps
* fix imports
* req
* doctest
* SQLModel
* fsspec
* azure
* docs
* falek8

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
```

## Diff of the sampled file

```diff
@@ -83,6 +83,8 @@ def get_dist_path_if_editable_install(project_name) -> str:
     """Is distribution an editable install - modified version from pip that
     fetches egg-info instead of egg-link"""
     for path_item in sys.path:
+        if not os.path.isdir(path_item):
+            continue
         egg_info = os.path.join(path_item, project_name + ".egg-info")
         if os.path.isdir(egg_info):
             return path_item
@@ -96,13 +98,13 @@ def _prepare_lightning_wheels_and_requirements(root: Path) -> Optional[Callable]
     For normal users who install via PyPi or Conda, then this function does not do anything.
     """
 
-    if not get_dist_path_if_editable_install("lightning"):
+    if not get_dist_path_if_editable_install("lightning-app"):
         return
 
     # Packaging the Lightning codebase happens only inside the `lightning` repo.
     git_dir_name = get_dir_name() if check_github_repository() else None
 
-    is_lightning = git_dir_name and git_dir_name == "lightning"
+    is_lightning = git_dir_name and git_dir_name == "lightning_app"
 
     if (PACKAGE_LIGHTNING is None and not is_lightning) or PACKAGE_LIGHTNING == "0":
         return
```

## Other files changed by this commit (16)

- `.azure/app-cloud-e2e.yml` (+3 −6)
- `.github/workflows/ci-app-examples.yml` (+11 −11)
- `.github/workflows/ci-app-tests.yml` (+22 −11)
- `.github/workflows/code-checks.yml` (+7 −1)
- `.github/workflows/docs-checks.yml` (+15 −3)
- `requirements/app/devel.txt` (+0 −3)
- `requirements/app/test.txt` (+3 −0)
- `requirements/lite/base.txt` (+1 −1)
- `requirements/pytorch/base.txt` (+1 −1)
- `src/lightning_app/components/database/server.py` (+2 −2)
- `src/lightning_app/components/database/utilities.py` (+6 −6)
- `src/lightning_app/components/training.py` (+2 −3)
- `src/lightning_app/core/app.py` (+1 −1)
- `src/lightning_app/core/flow.py` (+1 −1)
- `tests/tests_app/utilities/packaging/test_lightning_utils.py` (+11 −12)
- `tests/tests_app/utilities/test_commands.py` (+1 −2)

## Fix commits that the dataset links to this commit (3)

### Fix 1: 48993cb5ed96 (2022-10-25) · pull request #15302: Resolve App e2es

Pull-request labels: bug, priority: 0, ci, app (removed)

Commit message:

```
Resolve App e2es (#15302)

* update

* prune

* examples

* [pre-commit.ci] auto fixes from pre-commit.com hooks

for more information, see https://pre-commit.ci

Co-authored-by: Jirka Borovec <Borda@users.noreply.github.com>
Co-authored-by: Jirka <jirka.borovec@seznam.cz>
Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>
```

Pull-request description:

```
## What does this PR do?

Closes #15303

## Before submitting

- [x] Was this **discussed/approved** via a GitHub issue? (not for typos and docs)
- [x] Did you read the [contributor guideline](https://github.com/Lightning-AI/lightning/blob/master/.github/CONTRIBUTING.md), **Pull Request** section?
- [x] Did you make sure your **PR does only one thing**, instead of bundling different changes together?
- [ ] Did you make sure to **update the documentation** with your changes? (if necessary)
- [ ] Did you write any **new necessary tests**? (not for typos and docs)
- [x] Did you verify new and **existing tests pass** locally with your changes?
- [ ] Did you list all the **breaking changes** introduced by this pull request?
- [ ] Did you **update the CHANGELOG**? (not for typos, docs, test updates, or minor internal changes/refactors)

<!-- In the CHANGELOG, separate each item in the unreleased section by a blank line to reduce collisions -->

## PR review

Anyone in the community is welcome to review the PR.
Before you start reviewing, make sure you have read the [review guidelines](https://github.com/Lightning-AI/lightning/wiki/Review-guidelines). In short, see the following bullet-li
[... cut ...]
```

This fix changes 4 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `requirements/app/test.txt`: `pytorch-lightning @ https://github.com/Lightning-AI/lightning/archive/refs/heads/master.zip`

Patch of `requirements/app/test.txt` in this fix:

```diff
@@ -12,6 +12,3 @@ psutil
 setuptools<=59.5.0
 sqlmodel
 requests-mock
-
-# TODO: as the package is assumed to be independent we shall be using already released versions
-pytorch-lightning @ https://github.com/Lightning-AI/lightning/archive/refs/heads/master.zip
```

### Fix 2: bd658441bd01 (2022-10-25) · pull request #15286: [App] testing `lightning` in `lightning-app` package

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

- in the sampled file: `if not get_dist_path_if_editable_install("lightning-app"):`; `is_lightning = git_dir_name and git_dir_name == "lightning_app"`
- in `.azure/app-cloud-e2e.yml`: `- bash: git restore . && python -m pip install -e .[ui] --find-links https://download.pytorch.org/whl/cpu/torch_stable.html`; `displayName: 'Install lightning app'`

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

Patch of `.azure/app-cloud-e2e.yml` in this fix:

```diff
@@ -58,8 +58,8 @@ jobs:
           name: "template_streamlit_ui"
         'App: template_react_ui':
           name: "template_react_ui"
-        'App: template_jupyterlab':  # TODO: clarify where these files lives
-          name: "template_jupyterlab"
+        # 'App: template_jupyterlab':  # TODO: clarify where these files lives
+        #   name: "template_jupyterlab"
         'App: idle_timeout':
           name: "idle_timeout"
         'App: collect_failures':
@@ -70,10 +70,10 @@ jobs:
           name: "drive"
         'App: payload':
           name: "payload"
-        # 'App: commands_and_api':
-        #   name: "commands_and_api"
-        'App: quick_start':
-          name: "quick_start"
+        'App: commands_and_api':
+          name: "commands_and_api"
+        # 'App: quick_start':  # TODO: Failed during installation
+        #   name: "quick_start"
     timeoutInMinutes: "30"
     cancelTimeoutInMinutes: "2"
     # values: https://docs.microsoft.com/en-us/azure/devops/pipelines/process/phases?view=azure-devops&tabs=yaml#workspace
@@ -101,12 +101,10 @@ jobs:
         path: $(pip_cache_dir)
       displayName: Cache pip
 
-    - bash: git restore . && python -m pip install -e .[ui] --find-links https://download.pytorch.org/whl/cpu/torch_stable.html
-      env:
-        PACKAGE_NAME: app
-      displayName: 'Install lightning app'
+    - bash: git restore . && python -m pip install -e . --find-links https://download.pytorch.org/whl/cpu/torch_stable.html
+      displayName: 'Install Lightning'
 
-    - bash: python -m pip install -r requirements/app/test.txt --find-links https://download.pytorch.org/whl/cpu/torch_stable.html
+    - bash: python -m pip install -r requirements/app/test.txt -r requirements/app/ui.txt --find-links https://download.pytorch.org/whl/cpu/torch_stable.html
       env:
         PACKAGE_NAME: pytorch
       displayName: 'Install dependencies'
@@ -116,14 +114,14 @@ jobs:
         python -m playwright install  # --with-deps
       displayName: 'Install Playwright system dependencies'
 
-    - bash: |
-        rm -rf examples/app_template_jupyterlab || true
-        git clone https://github.com/Lightning-AI/LAI-lightning-template
[... cut ...]
```

### Fix 3: f98de623fddc (2022-10-24) · pull request #15241: Add support for local connect terminal context

Pull-request labels: bug, ready to be merged, app (removed)

Commit message:

```
Add support for local connect terminal context (#15241)

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

* Update .azure/app-cloud-e2e.yml

Co-authored-by: Carlos Mocholí <carlossmocholi@gmail.com>

* update

Co-authored-by: Carlos Mocholí <carlossmocholi@gmail.com>
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

This PR adds support for having a terminal-based context for the LightningCLI. This works by adding the paren pid in the connection folder.

Furthermore, every time a command runs, it will clean out the dead connections.

Fixes #\<issue_number>

### Does your PR introduce any breaking changes? If yes, please list them.

<!-- FILL IN or None -->

## Before submitting

- [x] Was this **discussed/approved** via a GitHub issue? (not for typos and docs)
- [x] Did you read the [contributor guideline](https://github.com/Lightning-AI/lightning/blob/master/.github/CONTRIBUTING.md), **Pull Request** section?
- [x] Did you make sure your **PR does only one thing**, instead of bu
[... cut ...]
```

This fix changes 9 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `.azure/app-cloud-e2e.yml`: `- bash: python -m pip install -r requirements/app/test.txt`

Patch of `.azure/app-cloud-e2e.yml` in this fix:

```diff
@@ -106,7 +106,7 @@ jobs:
         PACKAGE_NAME: app
       displayName: 'Install lightning app'
 
-    - bash: python -m pip install -r requirements/app/test.txt
+    - bash: python -m pip install -r requirements/app/test.txt --find-links https://download.pytorch.org/whl/cpu/torch_stable.html
       env:
         PACKAGE_NAME: pytorch
       displayName: 'Install dependencies'
```

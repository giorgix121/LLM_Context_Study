# case095: Lightning-AI/lightning bd658441bd01

Sampled file (the only file the models saw): `src/lightning_app/utilities/packaging/cloud_compute.py` · committed 2022-10-25 04:24:20-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

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

## Diff of the sampled file

```diff
@@ -84,6 +84,9 @@ class CloudCompute:
         if self._internal_id is None:
             self._internal_id = "default" if self.name == "default" else uuid4().hex[:7]
 
+        # Internal arguments for now.
+        self.preemptible = False
+
     def to_dict(self) -> dict:
         _verify_mount_root_dirs_are_unique(self.mounts)
         return {"type": __CLOUD_COMPUTE_IDENTIFIER__, **asdict(self)}
```

## Other files changed by this commit (9)

- `.azure/app-cloud-e2e.yml` (+16 −18)
- `examples/app_drive/app.py` (+1 −1)
- `src/lightning_app/testing/testing.py` (+35 −23)
- `src/lightning_app/utilities/app_logs.py` (+2 −1)
- `src/lightning_app/utilities/packaging/lightning_utils.py` (+15 −7)
- `tests/tests_app/utilities/packaging/test_lightning_utils.py` (+23 −11)
- `tests/tests_app_examples/test_boring_app.py` (+2 −2)
- `tests/tests_app_examples/test_commands_and_api.py` (+8 −13)
- `tests/tests_app_examples/test_drive.py` (+1 −1)

## Fix commits that the dataset links to this commit (2)

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
- in `.azure/app-cloud-e2e.yml`: `- bash: git restore . && python -m pip install -e . --find-links https://download.pytorch.org/whl/cpu/torch_stable.html`; `- bash: python -m pip install -r requirements/app/test.txt -r requirements/app/ui.txt --find-links https://download.pytorch.org/whl/cpu/torch_stable.html`; `displayName: 'Install Lightning'`

Patch of `.azure/app-cloud-e2e.yml` in this fix:

```diff
@@ -101,13 +101,8 @@ jobs:
         path: $(pip_cache_dir)
       displayName: Cache pip
 
-    - bash: git restore . && python -m pip install -e . --find-links https://download.pytorch.org/whl/cpu/torch_stable.html
-      displayName: 'Install Lightning'
-
-    - bash: python -m pip install -r requirements/app/test.txt -r requirements/app/ui.txt --find-links https://download.pytorch.org/whl/cpu/torch_stable.html
-      env:
-        PACKAGE_NAME: pytorch
-      displayName: 'Install dependencies'
+    - bash: git restore . && python -m pip install -e . -r requirements/app/test.txt -r requirements/app/ui.txt --find-links https://download.pytorch.org/whl/cpu/torch_stable.html
+      displayName: 'Install Lightning & dependencies'
 
     - bash: |
         python -m pip install playwright
```

### Fix 2: d1263f5d7476 (2022-10-26) · pull request #15324: Resolve Boring App Race Condition

Pull-request labels: bug, ready to be merged, app (removed)

Commit message:

```
Resolve Boring App Race Condition (#15324)
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

The port `1111` is used by the Server work. However, it seems there is a race condition to get in within the logs and the check. Reverting back to 8000 to remove flakyness for now.

Fixes #\<issue_number>

### Does your PR introduce any breaking changes? If yes, please list them.

<!-- FILL IN or None -->

## Before submitting

- [ ] Was this **discussed/approved** via a GitHub issue? (not for typos and docs)
- [x] Did you read the [contributor guideline](https://github.com/Lightning-AI/lightning/blob/master/.github/CONTRIBUTING.md), **Pull Request** section?
- [x] Did you make sure your **PR does only one thing**, instead of bundling different changes together?
- [ ]
[... cut ...]
```

This fix changes 2 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `tests/tests_app_examples/test_boring_app.py`: `assert any("http://0.0.0.0:1111" in line for line in lines)`

Patch of `tests/tests_app_examples/test_boring_app.py` in this fix:

```diff
@@ -34,5 +34,5 @@ def check_hello_there(*_, **__):
 
         assert result.exit_code == 0
         assert result.exception is None
-        assert any("http://0.0.0.0:1111" in line for line in lines)
+        assert any("--filepath=/content/.storage/boring_file.txt" in line for line in lines)
         print("Succeeded App!")
```

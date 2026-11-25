# case040: localstack/localstack a954ecac44a3

Sampled file (the only file the models saw): `localstack/services/es/plugins.py` · committed 2022-09-21 09:05:18-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
refactor kinesis installers (#6879)
```

## Diff of the sampled file

```diff
@@ -1,7 +1,7 @@
 from localstack.packages import Package, packages
 
 
-@packages(service="es")
+@packages()
 def elasticsearch_package() -> Package:
     from localstack.services.opensearch.packages import elasticsearch_package
```

## Other files changed by this commit (10)

- `localstack/packages/__init__.py` (+9 −3)
- `localstack/packages/api.py` (+295 −0)
- `localstack/packages/core.py` (+66 −260)
- `localstack/services/dynamodb/plugins.py` (+1 −1)
- `localstack/services/install.py` (+5 −108)
- `localstack/services/kinesis/kinesalite_server.py` (+16 −5)
- `localstack/services/kinesis/kinesis_mock_server.py` (+3 −4)
- `localstack/services/kinesis/packages.py` (+93 −0)
- `localstack/services/kinesis/plugins.py` (+14 −0)
- `localstack/services/opensearch/plugins.py` (+1 −1)

## Fix commits that the dataset links to this commit (1)

### Fix 1: d07b7b32f1a6 (2022-10-11) · pull request #7006: fix offline GitHub package presence check

Commit message:

```
fix offline GitHub package presence check (#7006)
```

Pull-request description:

```
This PR fixes the GitHub package installer's (and in particular the KinesisMock installer's) presence check for offline startups of LocalStack.
Previously, the path which is checked to test if the package is already installed was created by using the filename in the download URL. However, for GitHub assets, the download URL needs to be fetched from the release / tag data.
In order to allow offline startups, the GitHub installer has been slightly refactored such that it now uses the GitHub asset name (which can not use the release data anymore, but this wasn't needed in the first place).

This might cause minor conflicts with https://github.com/localstack/localstack/pull/6916.
Fixes https://github.com/localstack/localstack/issues/7000.
```

This fix changes 3 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `localstack/packages/core.py`: `:param github_release: GitHub Release JSON data`; `asset_name = self._get_github_asset_name(github_release)`; `def _get_github_asset_name(self, github_release: Dict) -> str:`; `from typing import Callable, Dict, List`
- in `localstack/services/kinesis/packages.py`: `def _get_github_asset_name(self, _):`

Patch of `localstack/packages/core.py` in this fix:

```diff
@@ -3,7 +3,7 @@
 import threading
 from abc import ABC
 from functools import lru_cache
-from typing import Callable, Dict, List
+from typing import Callable, List
 
 import requests
 
@@ -203,13 +203,13 @@ def __init__(self, name: str, tag: str, github_slug: str):
 
     @lru_cache()
     def _get_download_url(self) -> str:
+        asset_name = self._get_github_asset_name()
         response = requests.get(self.github_tag_url)
         if not response.ok:
             raise PackageException(
                 f"Could not get list of releases from {self.github_tag_url}: {response.text}"
             )
         github_release = response.json()
-        asset_name = self._get_github_asset_name(github_release)
         download_url = None
         for asset in github_release.get("assets", []):
             # find the correct binary in the release
@@ -222,11 +222,16 @@ def _get_download_url(self) -> str:
             )
         return download_url
 
-    def _get_github_asset_name(self, github_release: Dict) -> str:
+    def _get_install_marker_path(self, install_dir: str) -> str:
+        # Use the GitHub asset name instead of the download URL (since the download URL needs to be fetched online).
+        return os.path.join(install_dir, self._get_github_asset_name())
+
+    def _get_github_asset_name(self) -> str:
         """
         Determines the name of the asset to download.
+        The asset name must be determinable without having any online data (because it is used in offline scenarios to
+        determine if the package is already installed).
 
-        :param github_release: GitHub Release JSON data
         :return: name of the asset to download from the GitHub project's tag / version
         """
         raise NotImplementedError()
```

Patch of `localstack/services/kinesis/packages.py` in this fix:

```diff
@@ -27,7 +27,7 @@ class KinesisMockPackageInstaller(GitHubReleaseInstaller):
     def __init__(self, version: str):
         super().__init__("kinesis-mock", version, "etspaceman/kinesis-mock")
 
-    def _get_github_asset_name(self, _):
+    def _get_github_asset_name(self):
         arch = get_arch()
         operating_system = get_os()
         if config.is_env_true("KINESIS_MOCK_FORCE_JAVA"):
```

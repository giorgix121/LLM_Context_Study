# case096: python-poetry/poetry 1215ba8f339a

Sampled file (the only file the models saw): `src/poetry/mixology/solutions/solutions/python_requirement_solution.py` · committed 2022-10-06 02:12:59-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
chore: update poetry-core to 1.3 and fix deprecations
```

## Diff of the sampled file

```diff
@@ -12,7 +12,7 @@ if TYPE_CHECKING:
 
 class PythonRequirementSolution(Solution):  # type: ignore[misc]
     def __init__(self, exception: SolverProblemError) -> None:
-        from poetry.core.semver.helpers import parse_constraint
+        from poetry.core.constraints.version import parse_constraint
 
         from poetry.mixology.incompatibility_cause import PythonCause
```

## Other files changed by this commit (42)

- `poetry.lock` (+7 −11)
- `pyproject.toml` (+1 −3)
- `src/poetry/console/commands/add.py` (+1 −1)
- `src/poetry/console/commands/self/add.py` (+1 −1)
- `src/poetry/console/commands/show.py` (+1 −1)
- `src/poetry/console/commands/version.py` (+2 −2)
- `src/poetry/installation/chooser.py` (+1 −1)
- `src/poetry/installation/pip_installer.py` (+1 −1)
- `src/poetry/masonry/builders/editable.py` (+1 −1)
- `src/poetry/mixology/failure.py` (+1 −1)
- `src/poetry/mixology/term.py` (+1 −1)
- `src/poetry/packages/locker.py` (+2 −2)
- `src/poetry/publishing/uploader.py` (+5 −3)
- `src/poetry/puzzle/provider.py` (+3 −3)
- `src/poetry/repositories/cached.py` (+2 −2)
- `src/poetry/repositories/http.py` (+1 −1)
- `src/poetry/repositories/legacy_repository.py` (+2 −2)
- `src/poetry/repositories/link_sources/base.py` (+1 −1)
- `src/poetry/repositories/pool.py` (+1 −1)
- `src/poetry/repositories/pypi_repository.py` (+2 −2)
- `src/poetry/repositories/repository.py` (+3 −3)
- `src/poetry/utils/env.py` (+2 −2)
- `src/poetry/utils/setup_reader.py` (+1 −1)
- `src/poetry/version/version_selector.py` (+1 −1)
- `tests/console/commands/env/helpers.py` (+1 −1)
- `tests/console/commands/env/test_remove.py` (+1 −1)
- `tests/console/commands/env/test_use.py` (+1 −1)
- `tests/console/commands/self/test_update.py` (+1 −1)
- `tests/console/commands/test_add.py` (+1 −1)
- `tests/console/commands/test_publish.py` (+2 −2)
- `tests/fixtures/simple_project/dist/simple_project-1.2.3.tar.gz` (+0 −0)
- `tests/helpers.py` (+3 −3)
- `tests/masonry/builders/test_editable_builder.py` (+1 −1)
- `tests/packages/test_locker.py` (+1 −1)
- `tests/repositories/link_sources/test_base.py` (+1 −1)
- `tests/repositories/link_sources/test_html.py` (+1 −1)
- `tests/repositories/test_legacy_repository.py` (+1 −1)
- `tests/repositories/test_pool.py` (+1 −1)
- `tests/repositories/test_pypi_repository.py` (+1 −1)
- `tests/repositories/test_repository.py` (+1 −1)
- ... and 2 more

## Fix commits that the dataset links to this commit (1)

### Fix 1: 8e8aa44ce79e (2022-09-25) · pull request #6621: normalized sdist names

Pull-request labels: kind/bug, area/build-system, area/publishing, impact/backport, impact/changelog

Commit message:

```
normalized name when registering package at upload
```

Pull-request description:

```
See https://github.com/python-poetry/poetry-core/pull/484
```

This fix changes 2 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `src/poetry/publishing/uploader.py`: `)`; `dist.glob(f"{distribution_name(self._package.name)}-{version}-*.whl")`; `dist.glob(f"{distribution_name(self._package.name)}-{version}.tar.gz")`; `tars = list(`
- in `tests/helpers.py`: `f"https://foo.bar/files/{distribution_name(package.name)}"`; `from poetry.core.masonry.utils.helpers import distribution_name`

Patch of `src/poetry/publishing/uploader.py` in this fix:

```diff
@@ -77,13 +77,10 @@ def adapter(self) -> adapters.HTTPAdapter:
     def files(self) -> list[Path]:
         dist = self._poetry.file.parent / "dist"
         version = self._package.version.to_string()
+        escaped_name = distribution_name(self._package.name)
 
-        wheels = list(
-            dist.glob(f"{distribution_name(self._package.name)}-{version}-*.whl")
-        )
-        tars = list(
-            dist.glob(f"{distribution_name(self._package.name)}-{version}.tar.gz")
-        )
+        wheels = list(dist.glob(f"{escaped_name}-{version}-*.whl"))
+        tars = list(dist.glob(f"{escaped_name}-{version}.tar.gz"))
 
         return sorted(wheels + tars)
 
@@ -303,7 +300,8 @@ def _register(self, session: requests.Session, url: str) -> requests.Response:
         Register a package to a repository.
         """
         dist = self._poetry.file.parent / "dist"
-        file = dist / f"{self._package.name}-{self._package.version.to_string()}.tar.gz"
+        escaped_name = distribution_name(self._package.name)
+        file = dist / f"{escaped_name}-{self._package.version.to_string()}.tar.gz"
 
         if not file.exists():
             raise RuntimeError(f'"{file.name}" does not exist.')
```

Patch of `tests/helpers.py` in this fix:

```diff
@@ -11,7 +11,6 @@
 from typing import TYPE_CHECKING
 from typing import Any
 
-from poetry.core.masonry.utils.helpers import distribution_name
 from poetry.core.packages.package import Package
 from poetry.core.packages.utils.link import Link
 from poetry.core.toml.file import TOMLFile
@@ -235,7 +234,7 @@ def find_packages(self, dependency: Dependency) -> list[Package]:
     def find_links_for_package(self, package: Package) -> list[Link]:
         return [
             Link(
-                f"https://foo.bar/files/{distribution_name(package.name)}"
+                f"https://foo.bar/files/{package.name.replace('-', '_')}"
                 f"-{package.version.to_string()}-py2.py3-none-any.whl"
             )
         ]
```

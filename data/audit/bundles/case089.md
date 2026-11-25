# case089: Lightning-AI/lightning b936fd4380ce

File: `src/lightning_app/utilities/packaging/lightning_utils.py` · committed 2022-10-04 18:46:44-01:00 · SZZ label: RISKY

## Commit message

```
[app] Add CloudCompute ID serializable within the flow and works state  (#14819)
```

## Diff of the target file

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

## Lines SZZ blamed (line numbers in the new version)

```
  113      logger.info(f"Packaged Lightning with your application. Version: {version}")
  124              from lightning_launcher.__version__ import __version__ as launcher_version
  125  
  126              logger.info(f"Packaged Lightning Launcher with your application. Version: {launcher_version}")
  134              from lightning_cloud.__version__ import __version__ as cloud_version
  135  
  136              logger.info(f"Packaged Lightning Cloud with your application. Version: {cloud_version}")
```

## Candidate fixes (1 later commits to this file remove a blamed line; 6 later commits up to 2023-06-30 checked)

### Candidate 1: bd658441bd01 (2022-10-25)

Message:

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

Removed blamed lines: `logger.info(f"Packaged Lightning Cloud with your application. Version: {cloud_version}")`; `logger.info(f"Packaged Lightning Launcher with your application. Version: {launcher_version}")`; `logger.info(f"Packaged Lightning with your application. Version: {version}")`

Patch of this file:

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

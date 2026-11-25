# case111: Lightning-AI/lightning 6855f653bb82

File: `src/pytorch_lightning/loggers/csv_logs.py` · committed 2022-09-20 02:43:32-01:00 · SZZ label: RISKY

## Commit message

```
Set `MLFlowLogger` status to FAILED when training raises an error (#12292)

Co-authored-by: Ritsuki Yamada <ritsuki.yamada@uzabase.com>
Co-authored-by: Adrian Wälchli <aedu.waelchli@gmail.com>
Co-authored-by: Jirka <jirka.borovec@seznam.cz>
Co-authored-by: Carlos Mocholí <carlossmocholi@gmail.com>
```

## Diff of the target file

```diff
@@ -208,6 +208,10 @@ class CSVLogger(Logger):
 
     @rank_zero_only
     def finalize(self, status: str) -> None:
+        if self._experiment is None:
+            # When using multiprocessing, finalize() should be a no-op on the main process, as no experiment has been
+            # initialized there
+            return
         self.save()
 
     @property
```

## Lines SZZ blamed (line numbers in the new version)

```
  211          if self._experiment is None:
  212              # When using multiprocessing, finalize() should be a no-op on the main process, as no experiment has been
  213              # initialized there
  214              return
```

## Candidate fixes (1 later commits to this file remove a blamed line; 7 later commits up to 2023-06-30 checked)

### Candidate 1: 8f1269283f3a (2023-01-13)

Message:

```
Add CSVLogger for Lightning Lite (#16346)

Co-authored-by: Jirka Borovec <6035284+Borda@users.noreply.github.com>
```

Removed blamed lines: `# When using multiprocessing, finalize() should be a no-op on the main process, as no experiment has been`; `# initialized there`; `if self._experiment is None:`; `return`

Patch of this file:

```diff
@@ -18,24 +18,24 @@
 CSV logger for basic experiment logging that does not require opening ports
 
 """
-import csv
 import logging
 import os
 from argparse import Namespace
-from typing import Any, Dict, List, Optional, Union
+from typing import Any, Dict, Optional, Union
 
-from torch import Tensor
-
-from lightning_fabric.utilities.logger import _add_prefix, _convert_params
+from lightning_fabric.loggers.csv_logs import _ExperimentWriter as _FabricExperimentWriter
+from lightning_fabric.loggers.csv_logs import CSVLogger as FabricCSVLogger
+from lightning_fabric.loggers.logger import rank_zero_experiment
+from lightning_fabric.utilities.logger import _convert_params
 from lightning_fabric.utilities.types import _PATH
 from pytorch_lightning.core.saving import save_hparams_to_yaml
-from pytorch_lightning.loggers.logger import Logger, rank_zero_experiment
-from pytorch_lightning.utilities.rank_zero import rank_zero_only, rank_zero_warn
+from pytorch_lightning.loggers.logger import Logger
+from pytorch_lightning.utilities.rank_zero import rank_zero_only
 
 log = logging.getLogger(__name__)
 
 
-class ExperimentWriter:
+class ExperimentWriter(_FabricExperimentWriter):
     r"""
     Experiment writer for CSVLogger.
 
@@ -47,61 +47,23 @@ class ExperimentWriter:
     """
 
     NAME_HPARAMS_FILE = "hparams.yaml"
-    NAME_METRICS_FILE = "metrics.csv"
 
     def __init__(self, log_dir: str) -> None:
+        super().__init__(log_dir=log_dir)
         self.hparams: Dict[str, Any] = {}
-        self.metrics: List[Dict[str, float]] = []
-
-        self.log_dir = log_dir
-        if os.path.exists(self.log_dir) and os.listdir(self.log_dir):
-            rank_zero_warn(
-                f"Experiment logs directory {self.log_dir} exists and is not empty."
-                " Previous log files in this directory will be deleted when the new ones are saved!"
-            )
-        os.makedirs(self.log_dir, exist_ok=True)
-
-        self.metrics_file_path = os.path.join(self.log_dir, self.NAME_METRICS_FILE)
 
     def log_hparams(self, params: Dict[str, Any]) -> None:
         """Record hparams."""
         self.hparams.update(params)
 
-    def log_metrics(self, metrics_dict: Dict[str, float], step: Optional[int] = None) -> None:
-        """Record metrics."""
-
-        def _handle_value(value: Union[Tensor, Any]) -> Any:
-            if isinstance(value, Tensor):
-                return value.item()
-            return value
-
-        if step is None:
-            step = len(self.metrics)
-
-        metrics = {k: _handle_value(v) for k, v in metrics_dict.items()}
-        metrics["step"] = step
-        self.metrics.append(metrics)
-
     def save(self) -> None:
         """Save recorded hparams and metrics into files."""
         hparams_file = os.path.join(self.log_dir, self.NAME_HPARAMS_FILE)
         save_hparams_to_yaml(hparams_file, self.hparams)
+        return super().save()
 
-        if not self.metrics:
-            return
-
-        last_m = {}
-        for m in self.metrics:
-            last_m.update(m)
-        metrics_keys = list(last_m.keys())
-
-        with open(self.metrics_file_path, "w", newline="") as f:
-            writer = csv.DictWriter(f, fieldnames=metrics_keys)
-            writer.writeheader()
-            writer.writerows(self.metrics)
 
-
-class CSVLogger(Logger):
+class CSVLogger(Logger, FabricCSVLogger):
     r"""
     Log to local file system in yaml and CSV format.
 
@@ -115,7 +77,7 @@ class CSVLogger(Logger):
 
     Args:
         save_dir: Save directory
-        name: Experiment name. Defaults to ``'default'``.
+        name: Experiment name. Defaults to ``'lightning_logs'``.
         version: Experiment version. If version is not specified the logger inspects the save
             directory for existing versions, then automatically assigns the next available version.
         prefix: A string to put at the beginning of metric keys.
@@ -132,13 +94,14 @@ def __init__(
         prefix: str = "",
         flush_logs_every_n_steps: int = 100,
     ):
-        super().__init__()
+        super().__init__(
+            root_dir=save_dir,
+            name=name,
+            version=version,
+            prefix=prefix,
+            flush_logs_every_n_steps=flush_logs_every_n_steps,
+        )
         self._save_dir = os.fspath(save_dir)
-        self._name = name or ""
-        self._version = version
-        self._prefix = prefix
-        self._experiment: Optional[ExperimentWriter] = None
-        self._flush_logs_every_n_steps = flush_logs_every_n_steps
 
     @property
     def root_dir(self) -> str:
@@ -170,12 +133,17 @@ def save_dir(self) -> str:
         """
         return self._save_dir
 
+    @rank_zero_only
+    def log_hyperparams(self, params: Union[Dict[str, Any], Namespace]) -> None:
+        params = _convert_params(params)
+        self.experiment.log_hparams(params)
+
     @property
     @rank_zero_experiment
-    def experiment(self) -> ExperimentWriter:
+    def experiment(self) -> _FabricExperimentWriter:
         r"""
 
-        Actual ExperimentWriter object. To use ExperimentWriter features in your
+        Actual _ExperimentWriter object. To use _ExperimentWriter features in your
         :class:`~pytorch_lightning.core.module.LightningModule` do the following.
 
         Example::
@@ -189,65 +157,3 @@ def experiment(self) -> ExperimentWriter:
         os.makedirs(self.root_dir, exist_ok=True)
         self._experiment = ExperimentWriter(log_dir=self.log_dir)
         return self._experiment
-
-    @rank_zero_only
-    def log_hyperparams(self, params: Union[Dict[str, Any], Namespace]) -> None:
-        params = _convert_params(params)
-        self.experiment.log_hparams(params)
-
-    @rank_zero_only
-    def log_metrics(self, metrics: Dict[str, Union[Tensor, float]], step: Optional[int] = None) -> None:
-        metrics = _add_prefix(metrics, self._prefix, self.LOGGER_JOIN_CHAR)
-        self.experiment.log_metrics(metrics, step)
-
```

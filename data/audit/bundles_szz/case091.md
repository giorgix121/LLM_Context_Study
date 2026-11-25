# case091: ray-project/ray 27511adbcaf9

Sampled file (the only file the models saw): `python/ray/data/datasource/csv_datasource.py` · committed 2022-09-07 18:49:21-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
[data] Re-init CSV invalid row handler to solve serialization issue  (#28327)

This re-sets `pyarrow.csv.ParseOptions.invalid_row_handler` to deal with a deserizalization issue in pyarrow (https://issues.apache.org/jira/browse/ARROW-17641).

See #28326 for details.

Signed-off-by: Kai Fricke <kai@anyscale.com>
```

## Diff of the sampled file

```diff
@@ -35,7 +35,14 @@ class CSVDatasource(FileBasedDatasource):
         read_options = reader_args.pop(
             "read_options", csv.ReadOptions(use_threads=False)
         )
-        reader = csv.open_csv(f, read_options=read_options, **reader_args)
+        parse_options = reader_args.pop("parse_options", csv.ParseOptions())
+        # Re-init invalid row handler: https://issues.apache.org/jira/browse/ARROW-17641
+        if hasattr(parse_options, "invalid_row_handler"):
+            parse_options.invalid_row_handler = parse_options.invalid_row_handler
+
+        reader = csv.open_csv(
+            f, read_options=read_options, parse_options=parse_options, **reader_args
+        )
         schema = None
         while True:
             try:
```

## Other files changed by this commit (1)

- `python/ray/data/tests/test_dataset_formats.py` (+22 −1)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 92df1c10173a (2022-10-07) · pull request #29032: [Datasets] read_csv not filter out files by default

Commit message:

```
[Datasets] read_csv not filter out files by default (#29032)

Currently read_csv filters out files without .csv extension when reading. This behavior seems to be surprising to users, and reported to be bad user experience in 3+ user reports (#26605). We should change to NOT filter files by default.

Verified Arrow (https://arrow.apache.org/docs/python/csv.html) and Spark (https://spark.apache.org/docs/latest/sql-data-sources-csv.html) does not filter out CSV files by default. I don't see a strong reason why we want to do it in a different way in Ray.

Added documentation in case users want to use partition_filter to filter out files, and gave an example to filter out files with .csv extension.

Also improve the error message when reading CSV file
```

Pull-request description:

```
Signed-off-by: Cheng Su <scnju13@gmail.com>

<!-- Thank you for your contribution! Please review https://github.com/ray-project/ray/blob/master/CONTRIBUTING.rst before opening a pull request. -->

<!-- Please add a reviewer to the assignee section when you create a PR. If you don't have the access to it, we will shortly find a reviewer and assign them to your PR. -->

## Why are these changes needed?

<!-- Please give a short summary of the change and the problem this solves. -->
Currently `read_csv` filters out files without `.csv` extension when reading. This behavior seems to be surprising to users, and reported to be bad user experience in 3+ user reports (https://github.com/ray-project/ray/issues/26605). We should change to NOT filter files by default.

Verified Arrow (https://arrow.apache.org/docs/python/csv.html) and Spark (https://spark.apache.org/docs/latest/sql-data-sources-csv.html) does not filter out CSV files by default. I don't see a strong reason why we want to do it in a different way in Ray.

Added documentation in case users want to use `partition_filter` to filter out files, and gave an example to filter out files with `.csv` extension.

Also improve the error m
[... cut ...]
```

This fix changes 3 files. Lines it removes that the commit above had added:

- in the sampled file: `)`; `f, read_options=read_options, parse_options=parse_options, **reader_args`; `reader = csv.open_csv(`
- in other files of the commit: none

Patch of the sampled file in this fix:

```diff
@@ -29,7 +29,7 @@ class CSVDatasource(FileBasedDatasource):
     def _read_stream(
         self, f: "pyarrow.NativeFile", path: str, **reader_args
     ) -> Iterator[Block]:
-        import pyarrow
+        import pyarrow as pa
         from pyarrow import csv
 
         read_options = reader_args.pop(
@@ -40,19 +40,27 @@ def _read_stream(
         if hasattr(parse_options, "invalid_row_handler"):
             parse_options.invalid_row_handler = parse_options.invalid_row_handler
 
-        reader = csv.open_csv(
-            f, read_options=read_options, parse_options=parse_options, **reader_args
-        )
-        schema = None
-        while True:
-            try:
-                batch = reader.read_next_batch()
-                table = pyarrow.Table.from_batches([batch], schema=schema)
-                if schema is None:
-                    schema = table.schema
-                yield table
-            except StopIteration:
-                return
+        try:
+            reader = csv.open_csv(
+                f, read_options=read_options, parse_options=parse_options, **reader_args
+            )
+            schema = None
+            while True:
+                try:
+                    batch = reader.read_next_batch()
+                    table = pa.Table.from_batches([batch], schema=schema)
+                    if schema is None:
+                        schema = table.schema
+                    yield table
+                except StopIteration:
+                    return
+        except pa.lib.ArrowInvalid as e:
+            raise ValueError(
+                f"Failed to read CSV file: {path}. "
+                "Please check the CSV file has correct format, or filter out non-CSV "
+                "file with 'partition_filter' field. See read_csv() documentation for "
+                "more details."
+            ) from e
 
     def _write_block(
         self,
```

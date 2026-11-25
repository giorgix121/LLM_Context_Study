# case040: localstack/localstack a954ecac44a3

File: `localstack/services/es/plugins.py` · committed 2022-09-21 09:05:18-01:00 · SZZ label: RISKY

## Commit message

```
refactor kinesis installers (#6879)
```

## Diff of the target file

```diff
@@ -1,7 +1,7 @@
 from localstack.packages import Package, packages
 
 
-@packages(service="es")
+@packages()
 def elasticsearch_package() -> Package:
     from localstack.services.opensearch.packages import elasticsearch_package
```

## Lines SZZ blamed (line numbers in the new version)

```
    4  @packages()
```

## Candidate fixes (1 later commits to this file remove a blamed line; 1 later commits up to 2023-06-30 checked)

### Candidate 1: d0a0770808c7 (2022-10-27)

Message:

```
refactor lpm plugin mechanism (#7063)
```

Removed blamed lines: `@packages()`

Patch of this file:

```diff
@@ -1,7 +1,7 @@
-from localstack.packages import Package, packages
+from localstack.packages import Package, package
 
 
-@packages()
+@package(name="elasticsearch")
 def elasticsearch_package() -> Package:
     from localstack.services.opensearch.packages import elasticsearch_package
```

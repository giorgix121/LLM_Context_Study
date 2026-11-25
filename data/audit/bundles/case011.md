# case011: localstack/localstack 033177254070

File: `localstack/services/dynamodb/utils.py` · committed 2022-09-19 18:18:48-01:00 · SZZ label: RISKY

## Commit message

```
Mark DynamoDB tests and add snapshots (#6878)
```

## Diff of the target file

```diff
@@ -101,9 +101,7 @@ class ItemFinder:
                     key_value = put_item["Item"].get(key_name)
                     if not key_value:
                         raise ValidationException(
-                            "An error occurred (ValidationException) when calling the "
-                            "BatchWriteItem operation: The provided key element does not match "
-                            "the schema"
+                            "The provided key element does not match the schema"
                         )
                     search_key[key_name] = key_value
             if not search_key:
```

## Lines SZZ blamed (line numbers in the new version)

```
  104                              "The provided key element does not match the schema"
```

## Candidate fixes (0 later commits to this file remove a blamed line; 7 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

# case011: localstack/localstack 033177254070

Sampled file (the only file the models saw): `localstack/services/dynamodb/utils.py` · committed 2022-09-19 18:18:48-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

## Commit message

```
Mark DynamoDB tests and add snapshots (#6878)
```

## Diff of the sampled file

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

## Other files changed by this commit (4)

- `localstack/services/dynamodb/provider.py` (+4 −2)
- `localstack/testing/snapshots/transformer_utility.py` (+11 −0)
- `tests/integration/test_dynamodb.py` (+119 −126)
- `tests/integration/test_dynamodb.snapshot.json` (+331 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 04e1f02a5816 (2022-10-05) · pull request #6918: Fix DynamodbStreams binary data consistency

Commit message:

```
Fix DynamodbStreams binary data consistency (#6918)
```

Pull-request description:

```
### Summary
This PR solves an issue where `GetItem` of DynamoDB returns a differently encoded value than `GetRecords` of DynamoDBStreams. This is especially obvious when using binary data (a test case of `b"\x90"` already reveals the issue).

Adds test case `test_data_encoding_consistency`

### Related
Fixes: #6786, Fixes: #6700 

### Note
The test case is currently flaky, therefore I draft the PR for now. 
However, since a similary structured test case [here](https://github.com/localstack/localstack/blob/master/tests/integration/test_dynamodb.py#L1188) is also flaky, I highly suspect that the flakiness is not because of my solution, but because of the client.
```

This fix changes 5 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `tests/integration/test_dynamodb.snapshot.json`: `}`

Patch of `tests/integration/test_dynamodb.snapshot.json` in this fix:

```diff
@@ -327,5 +327,37 @@
     "recorded-content": {
       "ValidationException": "An error occurred (ValidationException) when calling the BatchWriteItem operation: The provided key element does not match the schema"
     }
+  },
+  "tests/integration/test_dynamodb.py::TestDynamoDB::test_data_encoding_consistency": {
+    "recorded-date": "23-09-2022, 13:03:42",
+    "recorded-content": {
+      "GetItem": {
+        "data": {
+          "B": "b'\\x90'"
+        },
+        "id": {
+          "S": "id1"
+        }
+      },
+      "GetRecords": {
+        "ApproximateCreationDateTime": "datetime",
+        "Keys": {
+          "id": {
+            "S": "id1"
+          }
+        },
+        "NewImage": {
+          "data": {
+            "B": "b'\\x90'"
+          },
+          "id": {
+            "S": "id1"
+          }
+        },
+        "SequenceNumber": "100000000023871950156",
+        "SizeBytes": 15,
+        "StreamViewType": "NEW_AND_OLD_IMAGES"
+      }
+    }
   }
-}
+}
\ No newline at end of file
```

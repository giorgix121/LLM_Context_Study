# case134: commaai/openpilot f6119603912e

File: `selfdrive/manager/manager.py` · committed 2022-10-01 06:47:06-01:00 · SZZ label: RISKY

## Commit message

```
networking: add unmetered cellular toggle (#25902)

* add metered toggle to UI

* add GsmMetered param

* add NMMetered constants

* change LTE connection settings: connection.metered

* change to GsmUnmetered override

* update translations

* debug ui

* remove comment

* Revert "debug ui"

This reverts commit 2ad9e65ea229b814782be9f30cc7664125d7e908.

* 'Force Unmetered Cellular' toggle

* update translations

* remove description

* update translations

* change unmetered to metered
```

## Diff of the target file

```diff
@@ -39,6 +39,7 @@ def manager_init() -> None:
   default_params: List[Tuple[str, Union[str, bytes]]] = [
     ("CompletedTrainingVersion", "0"),
     ("DisengageOnAccelerator", "1"),
+    ("GsmMetered", "1"),
     ("HasAcceptedTerms", "0"),
     ("LanguageSetting", "main_en"),
     ("OpenpilotEnabledToggle", "1"),
```

## Lines SZZ blamed (line numbers in the new version)

```
   42      ("GsmMetered", "1"),
```

## Candidate fixes (0 later commits to this file remove a blamed line; 11 later commits up to 2023-06-30 checked)

(none found: the fix may have touched a renamed file, come after the cut-off, or rewritten the line with different whitespace)

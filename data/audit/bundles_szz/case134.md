# case134: commaai/openpilot f6119603912e

Sampled file (the only file the models saw): `selfdrive/manager/manager.py` · committed 2022-10-01 06:47:06-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

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

## Diff of the sampled file

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

## Other files changed by this commit (11)

- `common/params.cc` (+1 −0)
- `selfdrive/athena/tests/helpers.py` (+1 −1)
- `selfdrive/ui/qt/offroad/networking.cc` (+13 −5)
- `selfdrive/ui/qt/offroad/networkmanager.h` (+7 −0)
- `selfdrive/ui/qt/offroad/wifiManager.cc` (+8 −1)
- `selfdrive/ui/qt/offroad/wifiManager.h` (+1 −1)
- `selfdrive/ui/translations/main_ja.ts` (+8 −0)
- `selfdrive/ui/translations/main_ko.ts` (+8 −0)
- `selfdrive/ui/translations/main_pt-BR.ts` (+8 −0)
- `selfdrive/ui/translations/main_zh-CHS.ts` (+8 −0)
- `selfdrive/ui/translations/main_zh-CHT.ts` (+8 −0)

## Fix commits that the dataset links to this commit (1)

### Fix 1: c6b8a253e68f (2022-10-17) · pull request #26113: networking: fix metered setting

Pull-request labels: bugfix

Commit message:

```
networking: fix metered setting (#26113)

when metered set unknown, when unmetered set no
```

Pull-request description:

```
- When the metered toggle is enabled (default) set the `connection.metered` setting to `NM_METERED_UNKNOWN` (allow network manager to decide?)
- When the toggle is disabled, set to `NM_METERED_NO`

Bug introduced in #25902
```

This fix changes 1 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `selfdrive/ui/qt/offroad/wifiManager.cc`: `int meteredInt = metered ? NM_METERED_NO : NM_METERED_UNKNOWN;`

Patch of `selfdrive/ui/qt/offroad/wifiManager.cc` in this fix:

```diff
@@ -368,7 +368,7 @@ void WifiManager::updateGsmSettings(bool roaming, QString apn, bool metered) {
       changes = true;
     }
 
-    int meteredInt = metered ? NM_METERED_NO : NM_METERED_UNKNOWN;
+    int meteredInt = metered ? NM_METERED_UNKNOWN : NM_METERED_NO;
     if (settings.value("connection").value("metered").toInt() != meteredInt) {
       qWarning() << "Changing connection.metered to" << meteredInt;
       settings["connection"]["metered"] = meteredInt;
```

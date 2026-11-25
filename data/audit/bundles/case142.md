# case142: commaai/openpilot 01d05f66fe5a

File: `selfdrive/sensord/pigeond.py` · committed 2022-10-06 08:46:15-01:00 · SZZ label: RISKY

## Commit message

```
auto-detect pigeon or quectel (#25991)

* auto-detect pigeon or quectel

* persistent

* fix sim

* fix process replay

* fix locationd unit tests

* fix that

Co-authored-by: Comma Device <device@comma.ai>
```

## Diff of the target file

```diff
@@ -116,7 +116,7 @@ class TTYPigeon():
       time.sleep(0.001)
 
 
-def initialize_pigeon(pigeon: TTYPigeon) -> None:
+def initialize_pigeon(pigeon: TTYPigeon) -> bool:
   # try initializing a few times
   for _ in range(10):
     try:
@@ -198,6 +198,10 @@ def initialize_pigeon(pigeon: TTYPigeon) -> None:
       break
     except TimeoutError:
       cloudlog.warning("Initialization failed, trying again!")
+  else:
+    cloudlog.warning("Failed to initialize pigeon")
+    return False
+  return True
 
 def deinitialize_and_exit(pigeon: Optional[TTYPigeon]):
   cloudlog.warning("Storing almanac in ublox flash")
@@ -236,7 +240,8 @@ def main():
   time.sleep(0.5)
 
   pigeon = TTYPigeon()
-  initialize_pigeon(pigeon)
+  r = initialize_pigeon(pigeon)
+  Params().put_bool("UbloxAvailable", r)
 
   # start receiving data
   while True:
```

## Lines SZZ blamed (line numbers in the new version)

```
  119  def initialize_pigeon(pigeon: TTYPigeon) -> bool:
  201    else:
  202      cloudlog.warning("Failed to initialize pigeon")
  203      return False
  204    return True
  243    r = initialize_pigeon(pigeon)
  244    Params().put_bool("UbloxAvailable", r)
```

## Candidate fixes (2 later commits to this file remove a blamed line; 5 later commits up to 2023-06-30 checked)

### Candidate 1: 76f9a1487c2b (2022-10-12)

Message:

```
GPS test station first unittests (#25950)

* init gps test

* gps test v1

* add static signal gen script

* update readme

* remove LD_PRELOAD by using rpath, update values after testing

* remove LD_PRELOAD

* update fuzzy testing

* address comments

* cleanup

Co-authored-by: Kurt Nistelberger <kurt.nistelberger@gmail.com>
old-commit-hash: 54d667aa155a795ff3ee4953ce508d64945fdac3
```

Removed blamed lines: `Params().put_bool("UbloxAvailable", r)`; `r = initialize_pigeon(pigeon)`

Patch of this file:

```diff
@@ -7,7 +7,7 @@
 import requests
 import urllib.parse
 from datetime import datetime
-from typing import List, Optional
+from typing import List, Optional, Tuple
 
 from cereal import messaging
 from common.params import Params
@@ -34,7 +34,6 @@ def set_power(enabled: bool) -> None:
   gpio_set(GPIO.UBLOX_PWR_EN, enabled)
   gpio_set(GPIO.UBLOX_RST_N, enabled)
 
-
 def add_ubx_checksum(msg: bytes) -> bytes:
   A = B = 0
   for b in msg[2:]:
@@ -115,35 +114,70 @@ def wait_for_backup_restore_status(self, timeout: float = 1.) -> int:
         raise TimeoutError('No response from ublox')
       time.sleep(0.001)
 
+  def reset_device(self) -> bool:
+    # deleting the backup does not always work on first try (mostly on second try)
+    for _ in range(5):
+      # device cold start
+      self.send(b"\xb5\x62\x06\x04\x04\x00\xff\xff\x00\x00\x0c\x5d")
+      time.sleep(1) # wait for cold start
+      init_baudrate(self)
+
+      # clear configuration
+      self.send_with_ack(b"\xb5\x62\x06\x09\x0d\x00\x00\x00\x1f\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x17\x71\x5b")
+
+      # clear flash memory (almanac backup)
+      self.send_with_ack(b"\xB5\x62\x09\x14\x04\x00\x01\x00\x00\x00\x22\xf0")
+
+      # try restoring backup to verify it got deleted
+      self.send(b"\xB5\x62\x09\x14\x00\x00\x1D\x60")
+      # 1: failed to restore, 2: could restore, 3: no backup
+      status = self.wait_for_backup_restore_status()
+      if status == 1 or status == 3:
+        return True
+    return False
+
+def init_baudrate(pigeon: TTYPigeon):
+  # ublox default setting on startup is 9600 baudrate
+  pigeon.set_baud(9600)
+
+  # $PUBX,41,1,0007,0003,460800,0*15\r\n
+  pigeon.send(b"\x24\x50\x55\x42\x58\x2C\x34\x31\x2C\x31\x2C\x30\x30\x30\x37\x2C\x30\x30\x30\x33\x2C\x34\x36\x30\x38\x30\x30\x2C\x30\x2A\x31\x35\x0D\x0A")
+  time.sleep(0.1)
+  pigeon.set_baud(460800)
+
 
 def initialize_pigeon(pigeon: TTYPigeon) -> bool:
   # try initializing a few times
   for _ in range(10):
     try:
-      pigeon.set_baud(9600)
-
-      # up baud rate
-      pigeon.send(b"\x24\x50\x55\x42\x58\x2C\x34\x31\x2C\x31\x2C\x30\x30\x30\x37\x2C\x30\x30\x30\x33\x2C\x34\x36\x30\x38\x30\x30\x2C\x30\x2A\x31\x35\x0D\x0A")
-      time.sleep(0.1)
-      pigeon.set_baud(460800)
-
-      # other configuration messages
-      pigeon.send_with_ack(b"\xB5\x62\x06\x00\x14\x00\x03\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x1E\x7F")
-      pigeon.send_with_ack(b"\xB5\x62\x06\x00\x14\x00\x00\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x19\x35")
-      pigeon.send_with_ack(b"\xB5\x62\x06\x00\x14\x00\x01\x00\x00\x00\xC0\x08\x00\x00\x00\x08\x07\x00\x01\x00\x01\x00\x00\x00\x00\x00\xF4\x80")
-      pigeon.send_with_ack(b"\xB5\x62\x06\x00\x14\x00\x04\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1D\x85")
-      pigeon.send_with_ack(b"\xB5\x62\x06\x00\x00\x00\x06\x18")
-      pigeon.send_with_ack(b"\xB5\x62\x06\x00\x01\x00\x01\x08\x22")
-      pigeon.send_with_ack(b"\xB5\x62\x06\x00\x01\x00\x03\x0A\x24")
+
+      # setup port config
+      pigeon.send_with_ack(b"\xb5\x62\x06\x00\x14\x00\x03\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x1E\x7F")
+      pigeon.send_with_ack(b"\xb5\x62\x06\x00\x14\x00\x00\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x19\x35")
+      pigeon.send_with_ack(b"\xb5\x62\x06\x00\x14\x00\x01\x00\x00\x00\xC0\x08\x00\x00\x00\x08\x07\x00\x01\x00\x01\x00\x00\x00\x00\x00\xF4\x80")
+      pigeon.send_with_ack(b"\xb5\x62\x06\x00\x14\x00\x04\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1D\x85")
+      pigeon.send_with_ack(b"\xb5\x62\x06\x00\x00\x00\x06\x18")
+      pigeon.send_with_ack(b"\xb5\x62\x06\x00\x01\x00\x01\x08\x22")
+      pigeon.send_with_ack(b"\xb5\x62\x06\x00\x01\x00\x03\x0A\x24")
+
+      # UBX-CFG-RATE (0x06 0x08)
       pigeon.send_with_ack(b"\xB5\x62\x06\x08\x06\x00\x64\x00\x01\x00\x00\x00\x79\x10")
+
+      # UBX-CFG-NAV5 (0x06 0x24)
       pigeon.send_with_ack(b"\xB5\x62\x06\x24\x24\x00\x05\x00\x04\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x5A\x63")
+
+      # UBX-CFG-ODO (0x06 0x1E)
       pigeon.send_with_ack(b"\xB5\x62\x06\x1E\x14\x00\x00\x00\x00\x00\x01\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3C\x37")
       pigeon.send_with_ack(b"\xB5\x62\x06\x39\x08\x00\xFF\xAD\x62\xAD\x1E\x63\x00\x00\x83\x0C")
       pigeon.send_with_ack(b"\xB5\x62\x06\x23\x28\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x56\x24")
+
+      # UBX-CFG-NAV5 (0x06 0x24)
       pigeon.send_with_ack(b"\xB5\x62\x06\x24\x00\x00\x2A\x84")
       pigeon.send_with_ack(b"\xB5\x62\x06\x23\x00\x00\x29\x81")
       pigeon.send_with_ack(b"\xB5\x62\x06\x1E\x00\x00\x24\x72")
       pigeon.send_with_ack(b"\xB5\x62\x06\x39\x00\x00\x3F\xC3")
+
+      # UBX-CFG-MSG (set message rate)
       pigeon.send_with_ack(b"\xB5\x62\x06\x01\x03\x00\x01\x07\x01\x13\x51")
       pigeon.send_with_ack(b"\xB5\x62\x06\x01\x03\x00\x02\x15\x01\x22\x70")
       pigeon.send_with_ack(b"\xB5\x62\x06\x01\x03\x00\x02\x13\x01\x20\x6C")
@@ -224,13 +258,11 @@ def deinitialize_and_exit(pigeon: Optional[TTYPigeon]):
   set_power(False)
   sys.exit(0)
 
-def main():
-  assert TICI, "unsupported hardware for pigeond"
+def create_pigeon() -> Tuple[TTYPigeon, messaging.PubMaster]:
+  pigeon = None
 
   # register exit handler
-  pigeon = None
   signal.signal(signal.SIGINT, lambda sig, frame: deinitialize_and_exit(pigeon))
-
   pm = messaging.PubMaster(['ubloxRaw'])
 
   # power cycle ublox
@@ -240,15 +272,20 @@ def main():
   time.sleep(0.5)
 
   pigeon = TTYPigeon()
-  r = initialize_pigeon(pigeon)
-  Params().put_bool("UbloxAvailable", r)
+  return pigeon, pm
 
-  # start receiving data
-  wh
```

### Candidate 2: cd2756da2345 (2023-01-15)

Message:

```
don't run ublox procs without ublox (#26965)

* pigeond: don't run if ublox missing

* same for ubloxd

Co-authored-by: Comma Device <device@comma.ai>
old-commit-hash: 6861c9999195a9791bdb31675a4ed07dbd562b9c
```

Removed blamed lines: `Params().put_bool("UbloxAvailable", r)`; `r = initialize_pigeon(pigeon)`

Patch of this file:

```diff
@@ -303,8 +303,7 @@ def main():
 
   pigeon, pm = create_pigeon()
   init_baudrate(pigeon)
-  r = initialize_pigeon(pigeon)
-  Params().put_bool("UbloxAvailable", r)
+  initialize_pigeon(pigeon)
 
   # start receiving data
   run_receiving(pigeon, pm)
```

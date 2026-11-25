# case142: commaai/openpilot 01d05f66fe5a

Sampled file (the only file the models saw): `selfdrive/sensord/pigeond.py` · committed 2022-10-06 08:46:15-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

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

## Diff of the sampled file

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

## Other files changed by this commit (8)

- `common/params.cc` (+1 −0)
- `common/params.h` (+2 −2)
- `common/params_pyx.pyx` (+3 −3)
- `selfdrive/locationd/laikad.py` (+1 −1)
- `selfdrive/locationd/locationd.cc` (+3 −3)
- `selfdrive/locationd/test/test_locationd.py` (+1 −0)
- `selfdrive/test/process_replay/process_replay.py` (+1 −0)
- `tools/sim/bridge.py` (+5 −2)

## Fix commits that the dataset links to this commit (1)

### Fix 1: aebb08e10542 (2022-11-04) · pull request #26352: locationd: add gps sanity check for quectel gps

Pull-request labels: bugfix

Commit message:

```
locationd: add gps sanity check for quectel gps (#26352)

* update check

* .

* .

* remove gps kf time check for gps ok

* upsi

* dont use gps_mode

* update refs

* Update selfdrive/locationd/locationd.cc

Co-authored-by: Shane Smiskol <shane@smiskol.com>

Co-authored-by: Kurt Nistelberger <kurt.nistelberger@gmail.com>
Co-authored-by: Cameron Clough <cameronjclough@gmail.com>
Co-authored-by: Shane Smiskol <shane@smiskol.com>
```

Pull-request description:

```
quectel gps verticalAccuracy is clipped to 500, and flags is always 1, so invalid values would pass, causing location
jumps

also the quectel gps returns values in a 1hz rate which causes gpsOK flickering due to the time limit of 1s,
as was seen in: `be13974ffe78aa72|2022-11-02--19-02-26--18`
```

This fix changes 3 files. Lines it removes that the commit above had added:

- in the sampled file: none (the fix does not change this file)
- in `selfdrive/locationd/locationd.cc`: `if (Params().getBool("UbloxAvailable", true)) {`

Patch of `selfdrive/locationd/locationd.cc` in this fix:

```diff
@@ -270,15 +270,22 @@ void Localizer::handle_gps(double current_time, const cereal::GpsLocationData::R
   bool gps_lat_lng_alt_insane = ((std::abs(log.getLatitude()) > 90) || (std::abs(log.getLongitude()) > 180) || (std::abs(log.getAltitude()) > ALTITUDE_SANITY_CHECK));
   bool gps_vel_insane = (floatlist2vector(log.getVNED()).norm() > TRANS_SANITY_CHECK);
 
-  if (gps_invalid_flag || gps_unreasonable || gps_accuracy_insane || gps_lat_lng_alt_insane || gps_vel_insane) {
+  // quectel gps verticalAccuracy is clipped to 500
+  bool gps_accuracy_insane_quectel = false;
+  if (!ublox_available) {
+    gps_accuracy_insane_quectel = log.getVerticalAccuracy() == 500;
+  }
+
+  if (gps_invalid_flag || gps_unreasonable || gps_accuracy_insane || gps_lat_lng_alt_insane || gps_vel_insane || gps_accuracy_insane_quectel) {
+    this->gps_valid = false;
     this->determine_gps_mode(current_time);
     return;
   }
-  
+
   double sensor_time = current_time - sensor_time_offset;
 
   // Process message
-  this->last_gps_fix = sensor_time;
+  this->gps_valid = true;
   this->gps_mode = true;
   Geodetic geodetic = { log.getLatitude(), log.getLongitude(), log.getAltitude() };
   this->converter = std::make_unique<LocalCoord>(geodetic);
@@ -476,9 +483,8 @@ kj::ArrayPtr<capnp::byte> Localizer::get_message_bytes(MessageBuilder& msg_build
   return msg_builder.toBytes();
 }
 
-
 bool Localizer::isGpsOK() {
-  return this->kf->get_filter_time() - this->last_gps_fix < 1.0;
+  return this->gps_valid;
 }
 
 void Localizer::determine_gps_mode(double current_time) {
@@ -498,8 +504,10 @@ void Localizer::determine_gps_mode(double current_time) {
 }
 
 int Localizer::locationd_thread() {
+  ublox_available = Params().getBool("UbloxAvailable", true);
+
   const char* gps_location_socket;
-  if (Params().getBool("UbloxAvailable", true)) {
+  if (ublox_available) {
     gps_location_socket = "gpsLocationExternal";
   } else {
     gps_location_socket = "gpsLocation";
```

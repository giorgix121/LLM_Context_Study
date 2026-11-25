# case135: commaai/openpilot 0f94d81b7adf

File: `selfdrive/car/gm/carcontroller.py` · committed 2022-10-11 14:33:37-01:00 · SZZ label: RISKY

## Commit message

```
GM camera ACC: reduce LKAS faults on startup (#26039)

* GM camera ACC: no faults on start up 2.0

And by 2.0 I mean we don't need to wait for blocked msg support to be merged first to merge this without regressing accidental single blocked msg count handling.

* Send the camera counter + 1

* Keep updating the first counter until we get a message on the bus

* Only update right before sending so sent_lka_steering_cmd is updated first

* Update ref_commit
```

## Diff of the target file

```diff
@@ -21,7 +21,8 @@ class CarController:
     self.frame = 0
     self.last_button_frame = 0
 
-    self.lka_steering_cmd_counter_last = -1
+    self.lka_steering_cmd_counter = 0
+    self.sent_lka_steering_cmd = False
     self.lka_icon_status_last = (False, False)
 
     self.params = CarControllerParams()
@@ -44,9 +45,14 @@ class CarController:
     # Steering (50Hz)
     # Avoid GM EPS faults when transmitting messages too close together: skip this transmit if we just received the
     # next Panda loopback confirmation in the current CS frame.
-    if CS.lka_steering_cmd_counter != self.lka_steering_cmd_counter_last:
-      self.lka_steering_cmd_counter_last = CS.lka_steering_cmd_counter
+    if CS.loopback_lka_steering_cmd_updated:
+      self.lka_steering_cmd_counter += 1
+      self.sent_lka_steering_cmd = True
     elif (self.frame % self.params.STEER_STEP) == 0:
+      # Initialize ASCMLKASteeringCmd counter using the camera
+      if not self.sent_lka_steering_cmd and self.CP.networkLocation == NetworkLocation.fwdCamera:
+        self.lka_steering_cmd_counter = CS.camera_lka_steering_cmd_counter + 1
+
       if CC.latActive:
         new_steer = int(round(actuators.steer * self.params.STEER_MAX))
         apply_steer = apply_std_steer_torque_limits(new_steer, self.apply_steer_last, CS.out.steeringTorque, self.params)
@@ -54,10 +60,7 @@ class CarController:
         apply_steer = 0
 
       self.apply_steer_last = apply_steer
-      # GM EPS faults on any gap in received message counters. To handle transient OP/Panda safety sync issues at the
-      # moment of disengaging, increment the counter based on the last message known to pass Panda safety checks.
-      idx = (CS.lka_steering_cmd_counter + 1) % 4
-
+      idx = self.lka_steering_cmd_counter % 4
       can_sends.append(gmcan.create_steering_control(self.packer_pt, CanBus.POWERTRAIN, apply_steer, idx, CC.latActive))
 
     if self.CP.openpilotLongitudinalControl:
```

## Lines SZZ blamed (line numbers in the new version)

```
   24      self.lka_steering_cmd_counter = 0
   25      self.sent_lka_steering_cmd = False
   48      if CS.loopback_lka_steering_cmd_updated:
   49        self.lka_steering_cmd_counter += 1
   50        self.sent_lka_steering_cmd = True
   52        # Initialize ASCMLKASteeringCmd counter using the camera
   53        if not self.sent_lka_steering_cmd and self.CP.networkLocation == NetworkLocation.fwdCamera:
   54          self.lka_steering_cmd_counter = CS.camera_lka_steering_cmd_counter + 1
   55  
   63        idx = self.lka_steering_cmd_counter % 4
```

## Candidate fixes (3 later commits to this file remove a blamed line; 17 later commits up to 2023-06-30 checked)

### Candidate 1: ed9c040be9c4 (2022-10-25)

Message:

```
GM: reduce LKAS faults while inactive (#26196)

* send at 10hz when inactive

* try to make it fine to switch rates

* fix rate

* todododo

* fine if we skip, we usually send too early

* clean up

* this may be required, 50Hz is not really needed to sync/initialize

* preserves previous behavior (not sure if this makes sense)

* Revert "preserves previous behavior (not sure if this makes sense)"

This reverts commit 3b297bca72307b5cba09bec4e2cd8e0f2761af42.

* Revert "this may be required, 50Hz is not really needed to sync/initialize"

This reverts commit a6b4693814214d3f508db922f3b371c402a13995.

* rm com

* Update ref_commit

* gate behind GM Cam

* common logic

* bet

* update refs
old-commit-hash: 27e315e58f5273da79803ad95737fc15483fef21
```

Removed blamed lines: `# Initialize ASCMLKASteeringCmd counter using the camera`; `if not self.sent_lka_steering_cmd and self.CP.networkLocation == NetworkLocation.fwdCamera:`

Patch of this file:

```diff
@@ -22,6 +22,7 @@ def __init__(self, dbc_name, CP, VM):
     self.apply_gas = 0
     self.apply_brake = 0
     self.frame = 0
+    self.last_steer_frame = 0
     self.last_button_frame = 0
     self.cancel_counter = 0
 
@@ -46,15 +47,21 @@ def update(self, CC, CS):
     # Send CAN commands.
     can_sends = []
 
-    # Steering (50Hz)
+    # Steering (Active: 50Hz, inactive: 10Hz)
+    # Attempt to sync with camera on startup at 50Hz, first few msgs are blocked
+    init_lka_counter = not self.sent_lka_steering_cmd and self.CP.networkLocation == NetworkLocation.fwdCamera
+    steer_step = self.params.INACTIVE_STEER_STEP
+    if CC.latActive or init_lka_counter:
+      steer_step = self.params.ACTIVE_STEER_STEP
+
     # Avoid GM EPS faults when transmitting messages too close together: skip this transmit if we just received the
     # next Panda loopback confirmation in the current CS frame.
     if CS.loopback_lka_steering_cmd_updated:
       self.lka_steering_cmd_counter += 1
       self.sent_lka_steering_cmd = True
-    elif (self.frame % self.params.STEER_STEP) == 0:
-      # Initialize ASCMLKASteeringCmd counter using the camera
-      if not self.sent_lka_steering_cmd and self.CP.networkLocation == NetworkLocation.fwdCamera:
+    elif (self.frame - self.last_steer_frame) >= steer_step:
+      # Initialize ASCMLKASteeringCmd counter using the camera until we get a msg on the bus
+      if init_lka_counter:
         self.lka_steering_cmd_counter = CS.camera_lka_steering_cmd_counter + 1
 
       if CC.latActive:
@@ -63,6 +70,7 @@ def update(self, CC, CS):
       else:
         apply_steer = 0
 
+      self.last_steer_frame = self.frame
       self.apply_steer_last = apply_steer
       idx = self.lka_steering_cmd_counter % 4
       can_sends.append(gmcan.create_steering_control(self.packer_pt, CanBus.POWERTRAIN, apply_steer, idx, CC.latActive))
```

### Candidate 2: 2e954e7473be (2023-01-31)

Message:

```
GM camera ACC: reliable relay open init (#27163)

Reliable relay open
old-commit-hash: 09cd0b4900d8aff1c9484c8848c9b5f7ff269594
```

Removed blamed lines: `self.lka_steering_cmd_counter = CS.camera_lka_steering_cmd_counter + 1`

Patch of this file:

```diff
@@ -63,7 +63,7 @@ def update(self, CC, CS):
     elif (self.frame - self.last_steer_frame) >= steer_step:
       # Initialize ASCMLKASteeringCmd counter using the camera until we get a msg on the bus
       if init_lka_counter:
-        self.lka_steering_cmd_counter = CS.camera_lka_steering_cmd_counter + 1
+        self.lka_steering_cmd_counter = CS.pt_lka_steering_cmd_counter + 1
 
       if CC.latActive:
         new_steer = int(round(actuators.steer * self.params.STEER_MAX))
```

### Candidate 3: 8d0277a2edde (2023-02-20)

Message:

```
GM: remove redundant CarController class variable (#27280)

* clean up

* fix check

* only set ts_nanos on update
old-commit-hash: 14d44e444418e1b6bd23afe5a371db886e8273e2
```

Removed blamed lines: `if CS.loopback_lka_steering_cmd_updated:`; `self.lka_steering_cmd_counter += 1`; `self.sent_lka_steering_cmd = False`; `self.sent_lka_steering_cmd = True`

Patch of this file:

```diff
@@ -30,7 +30,6 @@ def __init__(self, dbc_name, CP, VM):
     self.cancel_counter = 0
 
     self.lka_steering_cmd_counter = 0
-    self.sent_lka_steering_cmd = False
     self.lka_icon_status_last = (False, False)
 
     self.params = CarControllerParams(self.CP)
@@ -59,19 +58,17 @@ def update(self, CC, CS, now_nanos):
       # - until we're in sync with camera so counters align when relay closes, preventing a fault.
       #   openpilot can subtly drift, so this is activated throughout a drive to stay synced
       out_of_sync = self.lka_steering_cmd_counter % 4 != (CS.cam_lka_steering_cmd_counter + 1) % 4
-      if not self.sent_lka_steering_cmd or out_of_sync:
+      if CS.loopback_lka_steering_cmd_ts_nanos == 0 or out_of_sync:
         steer_step = self.params.STEER_STEP
 
-    if CS.loopback_lka_steering_cmd_updated:
-      self.lka_steering_cmd_counter += 1
-      self.sent_lka_steering_cmd = True
+    self.lka_steering_cmd_counter += 1 if CS.loopback_lka_steering_cmd_updated else 0
 
     # Avoid GM EPS faults when transmitting messages too close together: skip this transmit if we
     # received the ASCMLKASteeringCmd loopback confirmation too recently
     last_lka_steer_msg_ms = (now_nanos - CS.loopback_lka_steering_cmd_ts_nanos) * 1e-6
     if (self.frame - self.last_steer_frame) >= steer_step and last_lka_steer_msg_ms > MIN_STEER_MSG_INTERVAL_MS:
       # Initialize ASCMLKASteeringCmd counter using the camera until we get a msg on the bus
-      if not self.sent_lka_steering_cmd:
+      if CS.loopback_lka_steering_cmd_ts_nanos == 0:
         self.lka_steering_cmd_counter = CS.pt_lka_steering_cmd_counter + 1
 
       if CC.latActive:
```

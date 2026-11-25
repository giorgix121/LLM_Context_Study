# case135: commaai/openpilot 0f94d81b7adf

Sampled file (the only file the models saw): `selfdrive/car/gm/carcontroller.py` · committed 2022-10-11 14:33:37-01:00

The dataset labels this whole commit as bug-inducing, through the fix commits listed below.

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

## Diff of the sampled file

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

## Other files changed by this commit (2)

- `selfdrive/car/gm/carstate.py` (+15 −4)
- `selfdrive/test/process_replay/ref_commit` (+1 −1)

## Fix commits that the dataset links to this commit (1)

### Fix 1: 27e315e58f52 (2022-10-25) · pull request #26196: GM: reduce LKAS faults while inactive

Pull-request labels: bugfix, car, gm

Commit message:

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
```

Pull-request description:

```
This sends at the inactive rate when not actuating torque, as the stock camera/ASCM does. Sending at 10Hz when not active means we decrease our chances a lag will cause an LKAS fault under these circumstances

- [x] Make sure we don't send too close together when switching rates

We can also fix a fault when the relay closes on camera cars, but that will require some extra work to delay sending on occasion while inactive to sync up with the camera, so doing that in the next PR
```

This fix changes 3 files. Lines it removes that the commit above had added:

- in the sampled file: `if not self.sent_lka_steering_cmd and self.CP.networkLocation == NetworkLocation.fwdCamera:`
- in other files of the commit: none

Patch of the sampled file in this fix:

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

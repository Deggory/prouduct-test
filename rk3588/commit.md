# RK3588 Port Analysis

## Authoritative Version

### Repository: sunnypilot-pc

### Branch: master-rk3588

---

# Purpose of This Document

This document explains exactly what the `master-rk3588` branch does, why each major commit exists, and how the author modified Sunnypilot/OpenPilot to run on an Orange Pi 5 (RK3588).

This document is intended to be the authoritative engineering reference for future development.

The goal is not to describe OpenPilot in general.

The goal is to explain:

* What was changed
* Why it was changed
* What problem it solves
* What breaks if removed
* How it affects RK3588
* How it affects OpenPilot architecture

---

# Executive Summary

Many developers assume this branch is:

```text
OpenPilot
↓
RKNN
↓
RK3588 NPU
```

This is not what the branch primarily does.

After analyzing the commits, the actual purpose is:

```text
OpenPilot
↓
Remove Comma Hardware Dependencies
↓
Add Webcam / V4L2 Support
↓
Allow No IMU
↓
Allow No Driver Camera
↓
Adapt Camera Geometry
↓
Adapt UI Resolution
↓
Run on Orange Pi 5
```

The branch is primarily a Linux SBC adaptation branch.

The RK3588-specific work focuses on making OpenPilot boot and run on Orange Pi hardware.

---

# Architectural Overview

Original OpenPilot assumes:

```text
Comma Device
├── Road Camera
├── Driver Camera
├── IMU
├── GPS
├── Panda
├── CAN
└── Touch Display
```

Orange Pi 5 provides:

```text
Orange Pi 5
├── IMX415
├── V4L2
├── Linux
└── Generic Display
```

Most expected hardware does not exist.

Therefore OpenPilot fails.

The entire branch exists to solve that problem.

---

# Commit Analysis

---

# Commit: b51be4e

Title:

```text
feat(selfdrive): Make op run
```

This is the most important commit in the branch.

Without this commit:

```text
Manager Starts
↓
Required Hardware Missing
↓
Process Failures
↓
OpenPilot Exits
```

The author modified multiple subsystems.

---

## selfdrive/locationd/locationd.py

Purpose:

```text
Allow operation without standard Comma sensors.
```

Normal OpenPilot expects:

```text
IMU
GPS
Vehicle Signals
```

to be present.

On Orange Pi:

```text
none are guaranteed.
```

The modifications relax startup requirements.

Without this change:

```text
locationd refuses to initialize.
```

---

## selfdrive/modeld

Files:

```text
modeld.py
dmonitoringmodeld.py
SConscript
```

Purpose:

```text
Allow modeld to run without Comma camera hardware.
```

Normally:

```text
Road Camera
Driver Camera
```

must exist.

The port allows:

```text
single camera
webcam
IMX415
```

operation.

Without these changes:

```text
modeld startup fails.
```

---

## tools/webcam/camera.py

Purpose:

```text
Create a webcam abstraction layer.
```

Instead of:

```text
Comma Camera
```

the system can use:

```text
/dev/video0
/dev/video1
/dev/video11
```

through OpenCV.

This is one of the most important files in the entire branch.

It becomes the camera bridge between Linux V4L2 devices and OpenPilot.

---

## tools/webcam/camerad.py

Purpose:

```text
Create a Linux replacement for camerad.
```

The original camerad assumes Comma hardware.

This version allows:

```text
USB Webcam
IMX415
Any V4L2 Camera
```

to feed frames into VisionIPC.

---

## selfdrive/selfdrived/selfdrived.py

Purpose:

```text
Relax startup validation.
```

Normal OpenPilot checks:

```text
Driver Monitoring
Sensors
Vehicle State
```

Many do not exist on Orange Pi.

The author removes blocking conditions.

---

## system/manager/process_config.py

Purpose:

```text
Change process startup behavior.
```

The manager normally launches:

```text
camerad
sensord
hardwared
```

The port disables unsupported services and introduces webcam-based alternatives.

---

# Why This Commit Exists

Without it:

```text
Orange Pi
↓
Manager Starts
↓
Missing Hardware
↓
Failure
```

With it:

```text
Orange Pi
↓
Webcam
↓
Modeld
↓
UI
↓
Running System
```

---

# Commit: 6e91b9c

Title:

```text
feat(tools): Support old local route
```

Purpose:

```text
Improve offline replay support.
```

Files:

```text
tools/lib/route.py
tools/plotjuggler/juggle.py
tools/car_porting/auto_fingerprint.py
selfdrive/debug/uiview.py
```

The modifications allow:

```text
Local Route Logs
```

to be replayed without relying on Comma cloud infrastructure.

This is important because most Orange Pi development occurs offline.

Without this change:

```text
Testing becomes significantly harder.
```

---

# Commit: cab810f

Title:

```text
fix(tools): Fix tools
```

Purpose:

```text
Reduce process requirements for development.
```

Driver monitoring components are removed from some workflows.

The process list focuses on:

```text
webcamerad
ui
calibrationd
plannerd
```

instead of:

```text
Driver Monitoring Stack
```

Why?

Because bench testing generally has:

```text
No Driver Camera
```

and therefore driver monitoring is unnecessary.

---

# Commit: f39cc16

Title:

```text
feat(more): Adapter to rk3588
```

This is the true RK3588 adaptation commit.

---

## cereal/messaging/**init**.py

Purpose:

```text
Increase communication tolerance.
```

Timeout values are relaxed.

Reason:

```text
Orange Pi startup timing differs from Comma hardware.
```

Without this:

```text
False timeout warnings occur.
```

---

## cereal/services.py

Purpose:

```text
Adjust service timing expectations.
```

OpenPilot assumes:

```text
Comma Device Timing
```

The author adapts those assumptions to Linux SBC behavior.

---

## common/realtime.py

Purpose:

```text
Adjust realtime scheduling.
```

Reason:

```text
RK3588 Linux scheduling differs from TICI scheduling.
```

This prevents:

```text
Process starvation
Watchdog failures
Timing instability
```

---

## calibrationd.py

Purpose:

```text
Relax calibration assumptions.
```

Because:

```text
IMX415 mounting geometry differs.
```

and factory Comma calibration data does not exist.

---

## modeld.py

Purpose:

```text
Improve inference loop stability.
```

Changes focus on:

```text
Timing
Service Integration
Linux Compatibility
```

rather than NPU acceleration.

---

## selfdrived.py

Purpose:

```text
Further reduce hardware assumptions.
```

This allows OpenPilot to continue operating even when expected Comma services are absent.

---

# Why This Commit Exists

This commit effectively tells OpenPilot:

```text
You are running on Orange Pi,
not on a Comma device.
```

and adjusts system behavior accordingly.

---

# Commit: 95af03c

Title:

```text
feat(camera): Change camera focal
```

This commit changes camera geometry.

Original values:

```text
1928x1208
2648 focal length
```

New values:

```text
1280x720
1095 focal length
```

Reason:

```text
The camera is no longer the original Comma camera.
```

OpenPilot heavily depends on accurate camera calibration.

If focal length is incorrect:

```text
Lane Detection Errors
Path Estimation Errors
Calibration Errors
```

occur.

---

# Commit: 712bcb2

Title:

```text
feat(camera): Change camera focal to imx415
```

This is the second camera correction commit.

Focal length:

```text
1095
↓
900
```

This strongly suggests:

```text
The first calibration was still inaccurate.
```

The author tuned specifically for:

```text
IMX415 optics.
```

This is one of the strongest pieces of evidence that the branch targets IMX415 hardware.

---

# Commit: bf3f07e

Title:

```text
feat(ui): Adapter ui size to 800x400
```

Largest patch in the branch.

More than 60 files modified.

Purpose:

```text
Adapt OpenPilot UI to small displays.
```

Original OpenPilot assumes:

```text
1080p class displays.
```

Orange Pi deployments often use:

```text
800x400 LCD panels.
```

Without this patch:

```text
Buttons overlap
Text becomes unreadable
Settings screens break
UI becomes unusable
```

Affected systems:

```text
Sidebar
Onroad UI
Offroad UI
Settings
Networking
Widgets
Translations
```

This patch makes the system practical on embedded displays.

---

# Commit: 306a880

Title:

```text
feat(locationd): Allow no imu
```

Purpose:

```text
Allow operation without IMU.
```

Adds support for:

```bash
NO_IMU=1
```

Many Orange Pi installations have:

```text
No IMU
No Yaw Sensor
```

Without this patch:

```text
locationd may fail
Localization becomes invalid
```

The patch allows development systems to continue functioning.

---

# Does This Branch Use RK3588 NPU?

Most likely:

```text
No.
```

There is no evidence in these commits of:

```text
RKNN Toolkit
librknnrt.so
model.rknn
RKNN Inference Pipeline
```

Instead the branch focuses on:

```text
Hardware Adaptation
Camera Integration
Startup Relaxation
UI Scaling
Timing Adjustments
```

Therefore:

```text
master-rk3588
```

should be viewed as:

```text
RK3588 Linux Adaptation Branch
```

rather than:

```text
RK3588 NPU Branch
```

---

# Final Conclusion

The branch accomplishes five major goals:

1. Make OpenPilot run without Comma hardware.
2. Allow webcam and V4L2 camera operation.
3. Adapt camera geometry for IMX415.
4. Adapt UI for 800×400 displays.
5. Allow operation without IMU and other unavailable sensors.

The result is:

```text
Orange Pi 5
↓
IMX415 Camera
↓
Linux V4L2
↓
OpenPilot/Sunnypilot
↓
Working Development Environment
```

This is the true purpose of the `master-rk3588` branch.

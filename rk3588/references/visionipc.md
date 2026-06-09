# VISIONIPC.MD

# VisionIPC Reference for RK3588 / Orange Pi 5 OpenPilot Ports

Version: 1.0

Purpose:

Define how VisionIPC should be understood, preserved, validated, and debugged when porting openpilot-derived forks to:

* RK3588
* RK3588S
* Orange Pi 5
* Orange Pi 5 Plus
* IMX415
* RKISP
* RKNN

Target Repositories:

* openpilot
* sunnypilot
* frogpilot
* OPKR
* KisaPilot
* custom forks

---

# 1. What VisionIPC Is

VisionIPC is the shared-memory transport layer used to move camera frames between camera-producing processes and camera-consuming processes.

In the openpilot pipeline, VisionIPC normally sits between:

Camera Daemon

and

modeld / ui / other consumers

It is not a neural network input format.

It is not a camera driver.

It is not the RKNN input tensor.

It is a frame transport mechanism.

---

# 2. VisionIPC Position in the Pipeline

Recommended RK3588 pipeline:

IMX415

↓

MIPI CSI-2

↓

RKISP

↓

NV12 Frame

↓

Camera Daemon

↓

VisionIPC

↓

modeld

↓

loadyuv.cl

↓

transform.cl

↓

DrivingModelFrame.prepare()

↓

Model Input Tensor

↓

RKNN

This means VisionIPC carries frames before model preprocessing.

---

# 3. Critical Rule

Do not feed VisionIPC frames directly into RKNN.

VisionIPC frames are usually:

* NV12
* image-sized
* camera-space
* unwarped

RKNN driving models expect:

* model tensors
* warped
* resized
* packed
* temporally prepared
* layout-specific

Example:

VisionIPC frame:

1280x720 NV12

Model tensor:

1x12x128x256

or

1x128x256x12

depending on layout.

---

# 4. VisionIPC Responsibilities

VisionIPC is responsible for:

* Frame transport
* Shared memory ownership
* Camera stream identification
* Frame timestamps
* Frame IDs
* Synchronization between producers and consumers

VisionIPC is not responsible for:

* Image warping
* Model tensor creation
* RKNN inference
* Path prediction
* Planner behavior

---

# 5. Common Vision Streams

Common streams include:

* roadCameraState
* wideRoadCameraState
* driverCameraState

Common VisionIPC stream types include:

* VISION_STREAM_ROAD
* VISION_STREAM_WIDE_ROAD
* VISION_STREAM_DRIVER

For RK3588 IMX415 first-stage deployment, the required stream is:

roadCameraState

Only one road camera should be used until the single-camera path is validated.

---

# 6. Single-Camera Policy

For first RK3588 bring-up:

Use:

Road Camera only

Disable or omit:

* Wide Camera
* Driver Camera

Reason:

Single-camera validation is simpler and prevents stream synchronization errors.

After road camera validation passes, additional streams may be added.

---

# 7. Frame Format Policy

Preferred VisionIPC frame format:

NV12

Avoid:

* BGR
* RGB
* MJPEG
* YUYV

in production paths.

Debugging may use RGB/BGR screenshots, but not the runtime model path.

---

# 8. Why NV12 Matters

Openpilot preprocessing is built around NV12 frame handling.

NV12 allows:

Camera

↓

VisionIPC

↓

OpenCL preprocessing

without unnecessary RGB conversions.

Wrong format handling causes:

* color corruption
* invalid tensors
* broken overlays
* unstable model outputs

---

# 9. Tight vs Padded NV12

VisionIPC may carry frames produced from different sources:

* Qualcomm camera stack
* USB webcam
* RKISP
* Replay
* Custom camera daemon

Each source may have different memory layout.

Do not assume the same NV12 layout across sources.

---

# 10. Tight NV12

Tight NV12 has:

Y plane size:

width × height

UV plane size:

width × height / 2

Total size:

width × height × 1.5

Example:

1280 × 720 × 1.5 = 1,382,400 bytes

---

# 11. Padded NV12

Padded NV12 may have:

stride larger than width

aligned height

extra padding rows

larger buffer size

Common symptoms of wrong padded handling:

* green/purple image
* repeated lower image regions
* distorted tensor reconstructions
* modeld crashes after a few frames

---

# 12. VisionIPC Frame Validation

For each stream, record:

* stream name
* width
* height
* stride
* pixel format
* frame size
* frame ID
* timestamp
* producer process
* consumer process

Generate:

visionipc_report.json

---

# 13. Timestamp Validation

Every frame should have a valid timestamp.

Record:

Camera capture timestamp

VisionIPC publish timestamp

modeld receive timestamp

Calculate:

camera-to-modeld latency

Large timestamp drift must be investigated.

---

# 14. Frame ID Validation

Frame IDs must:

* increment monotonically
* not repeat
* not jump unexpectedly

Frame ID problems indicate:

* camera restart
* dropped frames
* synchronization failure

---

# 15. Stream Discovery

AI agents must discover available streams dynamically.

Do not assume:

road stream exists

wide stream exists

driver stream exists

Search for:

* VisionIpcClient
* VisionIpcServer
* VisionStreamType
* roadCameraState
* wideRoadCameraState
* driverCameraState

Generate:

visionipc_stream_inventory.json

---

# 16. Producer Discovery

Find which process publishes frames.

Common producers:

* system/camerad
* tools/webcam/camerad.py
* custom camerad_rk
* replay tools

Record producer path.

---

# 17. Consumer Discovery

Find consumers:

* modeld
* ui
* dmonitoringmodeld
* loggerd
* calibrationd

Record which streams each consumer uses.

---

# 18. RK3588 Recommended Producer

For production RK3588 IMX415:

Preferred producer:

custom RK camera daemon

or

RKISP V4L2 camera daemon

Acceptable for testing:

tools/webcam/camerad.py

Avoid for production:

OpenCV BGR conversion path

unless performance and correctness are validated.

---

# 19. Webcam Compatibility

When using webcam mode:

Environment variables may include:

USE_WEBCAM=1

ROAD_CAM=0

WEBCAM_WIDTH=1280

WEBCAM_HEIGHT=720

WEBCAM_FPS=20

WEBCAM_FOCAL=910.0

Webcam mode is useful for:

* debugging
* replay
* bench testing

It is not final IMX415 production mode.

---

# 20. RKISP Compatibility

For RKISP:

Preferred output:

NV12

Validate:

v4l2 pixel format

bytesperline

sizeimage

frame interval

Do not assume tight layout.

---

# 21. VisionIPC and modeld

modeld should consume VisionIPC frames and then call:

DrivingModelFrame.prepare()

or equivalent fork-specific preprocessing.

The model input tensor must be created after VisionIPC.

---

# 22. VisionIPC and UI

UI may consume the same camera stream.

UI correctness does not guarantee model correctness.

A camera preview can look correct while model tensors are wrong.

Always validate tensors separately.

---

# 23. VisionIPC and Calibration

Calibration depends on correct camera stream geometry.

Wrong VisionIPC resolution or timestamps can cause:

* calibration failure
* unstable overlay
* bad path alignment

---

# 24. VisionIPC and Logger

loggerd may record frames.

Ensure logging does not starve:

* modeld
* camera daemon
* UI

Record logger impact during performance validation.

---

# 25. VisionIPC Failure Modes

Common failures:

No frames

Wrong stream name

Wrong resolution

Wrong pixel format

Dropped frames

Timestamp drift

Buffer layout mismatch

Consumer timeout

Producer crash

---

# 26. Debugging No Frames

Check:

* camera daemon alive
* VisionIPC server created
* stream name correct
* modeld subscribed to correct stream
* camera device opened

Generate:

no_frame_debug_report.md

---

# 27. Debugging Wrong Colors

Likely causes:

* NV12 interpreted as RGB
* UV offset wrong
* padded NV12 read as tight NV12
* wrong bytesperline

Validate NV12 layout.

---

# 28. Debugging Repeated Image Regions

Likely causes:

* wrong stride
* wrong aligned height
* wrong UV plane offset
* wrong buffer size

This is common when Qualcomm/VENUS assumptions are applied to RKISP/webcam frames.

---

# 29. Debugging Overlay Misalignment

VisionIPC may be correct while calibration is wrong.

Check:

* camera intrinsics
* focal length
* principal point
* warp file
* camera resolution

---

# 30. Debugging modeld Crashes

If modeld crashes after receiving frames:

Check:

* frame size
* expected NV12 size
* preprocessing buffer assumptions
* reshape operations
* metadata shape mismatch

---

# 31. VisionIPC Validation Script

Recommended tool:

tools/rk3588/check_visionipc.py

Responsibilities:

* connect to stream
* read frames
* print metadata
* validate frame IDs
* validate timestamps
* validate dimensions
* dump sample frame

---

# 32. Required Report

Generate:

visionipc_validation.json

Include:

stream name

frame count

drop count

average latency

max latency

format

resolution

status

---

# 33. Pass Criteria

VisionIPC passes only if:

* frames received
* IDs monotonic
* timestamps valid
* dimensions correct
* format expected
* no corruption
* modeld consumes stream successfully

---

# 34. Fail Criteria

Any of:

* no frames
* repeated IDs
* invalid timestamps
* wrong resolution
* wrong format
* frame corruption
* modeld timeout

results in FAIL.

---

# 35. AI Agent Rules

When modifying a fork:

1. Discover VisionIPC streams
2. Discover producers
3. Discover consumers
4. Validate frame format
5. Validate dimensions
6. Validate timestamps
7. Validate modeld consumption
8. Generate report

Do not modify RKNN code until VisionIPC passes.

---

# 36. Final Reference Pipeline

Production RK3588 VisionIPC path:

IMX415

↓

RKISP

↓

NV12

↓

VisionIPC

↓

modeld

↓

OpenCL preprocessing

↓

RKNN

This is the required reference pipeline.

---

# 37. VisionIPC Checklist

Stream Inventory

[ ] Complete

Producer Found

[ ] PASS

Consumer Found

[ ] PASS

Frame Format

[ ] PASS

Resolution

[ ] PASS

Timestamps

[ ] PASS

Frame IDs

[ ] PASS

Modeld Consumption

[ ] PASS

UI Preview

[ ] PASS

Overlay Validation

[ ] PASS

Result:

PASS / FAIL

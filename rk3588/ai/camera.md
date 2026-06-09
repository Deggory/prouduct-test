# CAMERA.MD (Authoritative Version)

## Section A — Engineering Specification

### 1. Objective

* Camera subsystem goals
* Scope boundaries
* Non-goals

### 2. Reference Architecture

IMX415
↓
RKISP
↓
NV12
↓
VisionIPC
↓
loadyuv.cl
↓
transform.cl
↓
DrivingModelFrame.prepare()
↓
modeld

### 3. Design Principles

* Preserve model inputs
* Preserve NV12
* Preserve preprocessing
* Preserve training assumptions

### 4. Repository Discovery

* Camera discovery
* Process discovery
* Warp discovery
* Intrinsics discovery

### 5. Sensor Architecture

* IMX415
* IMX335
* IMX477
* Sensor ownership

### 6. RKISP Architecture

* CSI
* ISP
* Exposure
* Gain
* White Balance
* Noise Reduction

### 7. Camera Formats

* NV12
* YUV420
* MJPG
* RGB
* BGR

### 8. NV12 Architecture

* Tight NV12
* Padded NV12
* Memory ownership
* Validation rules

### 9. VisionIPC Integration

* Producer
* Consumer
* Synchronization
* Buffer ownership

### 10. Camera Buffer Ownership

RKISP
↓
VisionIPC
↓
modeld

### 11. OpenCV Rules

Allowed:

* Debugging
* Screenshots
* Validation

Forbidden:

* Production preprocessing

### 12. Camera Configuration

* RK_CAMERA_WIDTH
* RK_CAMERA_HEIGHT
* RK_CAMERA_FPS
* RK_CAMERA_FOCAL

### 13. Intrinsics Policy

* fx
* fy
* cx
* cy

### 14. Extrinsics Policy

* Pitch
* Yaw
* Roll

### 15. Warp Architecture

Camera
↓
Intrinsics
↓
Extrinsics
↓
Warp Matrix
↓
transform.cl

### 16. Warp Ownership

Owned by:
camera.md

Not:

* modeld.md
* rknn.md

### 17. Resolution Policy

* 1280x720
* 1920x1080
* Warp generation

### 18. Webcam Compatibility Layer

* USE_WEBCAM
* Replay
* MP4
* USB Cameras

### 19. Multi-Camera Architecture

* Road Camera
* Driver Camera
* Wide Camera

---

## Section B — Validation Specification

### 20. NV12 Validation

* Size validation
* Layout validation
* Stride validation

### 21. VisionIPC Validation

* Latency
* Queue depth
* Frame drops

### 22. Warp Validation

* Alignment
* Scaling
* Overlay position

### 23. Overlay Validation

* Lane lines
* Path
* Lead vehicle
* Camera preview

### 24. Calibration Validation

* Focal length
* Principal point
* Extrinsics

### 25. RKISP Validation

* Exposure
* Gain
* White balance
* Noise reduction

### 26. Color Validation

* Daylight
* Night
* Rain
* Tunnel
* Cloudy

### 27. Dynamic Range Validation

* Bright sky
* Dark road
* Sunset
* Night

### 28. Camera Timing Validation

Capture
↓
Publish
↓
Receive

### 29. Latency Validation

* Capture latency
* VisionIPC latency
* Total latency

### 30. Stress Testing

30 min
1 hr
4 hr

### 31. Recovery Testing

* Camera restart
* USB reset
* Frame timeout
* Process restart

### 32. Metadata Validation

camera_metadata.json

### 33. Acceptance Test Suite

* NV12
* VisionIPC
* Overlay
* Calibration
* Stress
* Recovery

---

## Section C — AI Agent Operating Manual

### 34. Repository Discovery Workflow

Generate:
camera_analysis.json

Discover:

* camera processes
* VisionIPC streams
* intrinsics
* warp generation
* camera configuration

### 35. Fork Adaptation Rules

Generate:
fork_camera_report.json

Never assume:

* paths
* camera names
* processes
* stream names

### 36. Camera Patch Strategy

Allowed:

* camera.py
* webcamerad
* camerad
* helpers.py
* warp generation

Avoid:

* planner
* controls
* vehicle interface

### 37. AI Agent Validation Workflow

Discover
↓
Validate NV12
↓
Validate VisionIPC
↓
Validate Warp
↓
Validate Overlay
↓
Validate Calibration
↓
Generate Reports

### 38. AI Agent Reporting

Generate:

* camera_analysis.json
* visionipc_report.json
* warp_validation.json
* camera_metadata.json
* fork_camera_report.json

### 39. Failure Modes

* Wrong NV12
* Wrong stride
* Wrong focal
* Wrong principal point
* Wrong warp
* Wrong overlay
* Frame drops
* Latency spikes

### 40. Production Readiness

Required:

* Stable camera
* Stable NV12
* Stable VisionIPC
* Stable overlays
* Stable calibration
* Stable latency
* Stable recovery

### 41. Production Gate

All validations PASS

before deployment.

### 42. Final Checklist

Discovery
[ ]

NV12
[ ]

VisionIPC
[ ]

Warp
[ ]

Calibration
[ ]

Overlay
[ ]

Stress
[ ]

Recovery
[ ]

Documentation
[ ]

Result:
PASS / FAIL

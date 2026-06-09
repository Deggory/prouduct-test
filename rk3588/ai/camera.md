# CAMERA.MD (Authoritative Version)

# Engineering Specification + Validation Specification + AI Agent Operating Manual

Version: 3.0

Target Hardware:

* RK3588
* RK3588S
* Orange Pi 5
* Orange Pi 5 Plus

Target Sensor:

* Sony IMX415

Target Pipeline:

IMX415
↓
MIPI CSI-2
↓
RKISP
↓
V4L2
↓
NV12 DMA-BUF
├──────────────┬────────────────┐
│              │                │
▼              ▼                ▼
VisionIPC    EGLImage        loggerd
↓              ↓
OpenCL       Mali GPU
↓              ↓
RKNN         UI Preview
↓
modelV2/msgq
↓
Planner

Target Forks:

* openpilot
* sunnypilot
* frogpilot
* OPKR
* KisaPilot

---

# Section A — Engineering Specification

## 1. Objective

This document defines:

* IMX415 integration
* RKISP integration
* V4L2 integration
* NV12 transport
* DMA-BUF architecture
* EGLImage camera preview
* VisionIPC interaction
* Validation rules
* AI-agent modification rules

Goal:

Production-quality IMX415 support for RK3588.

---

## 2. Camera Philosophy

Camera correctness is the foundation.

Bad camera data results in:

Wrong tensors
↓
Wrong model outputs
↓
Wrong planner outputs

Camera correctness has higher priority than FPS.

---

## 3. Production Architecture

Target architecture:

IMX415
↓
MIPI CSI-2
↓
RKISP
↓
V4L2
↓
NV12 DMA-BUF
├──────────────┬────────────────┐
│              │                │
▼              ▼                ▼
VisionIPC    EGLImage        loggerd
↓              ↓
OpenCL       Mali GPU
↓              ↓
RKNN         UI
↓
modelV2
↓
Planner

---

## 4. Camera Ownership

camera.md owns:

* Sensor
* MIPI
* RKISP
* V4L2
* NV12
* DMA-BUF
* Intrinsics
* Warp generation
* Capture timing

visionipc.md owns:

* Transport

modeld.md owns:

* Tensor generation

rknn.md owns:

* Inference

---

## 5. IMX415 Overview

Sensor:

Sony IMX415

Resolution:

3840×2160

4K capable

MIPI CSI-2 output

Automotive-friendly image quality

---

## 6. IMX415 Production Mode

Recommended:

1280×720

or

1920×1080

for OpenPilot-style deployment.

Avoid 4K runtime inference.

---

## 7. MIPI CSI Architecture

IMX415
↓
MIPI CSI-2
↓
RK3588 CSI Receiver
↓
RKISP

Validate:

Lane count

Link stability

Clock stability

---

## 8. RKISP Architecture

RKISP performs:

Sensor ingest

Exposure

Gain

Demosaic

Noise reduction

Color processing

NV12 output

---

## 9. RKISP Rule

RKISP output is authoritative.

Avoid:

Sensor RAW
↓
Custom userspace processing

unless explicitly required.

---

## 10. V4L2 Architecture

RKISP
↓
V4L2 Device
↓
Userspace

Common devices:

/dev/video*

Do not hardcode device numbers.

---

## 11. Camera Discovery

Discover:

Resolution

Format

FPS

Buffer Type

Generate:

camera_inventory.json

---

## 12. Supported Formats

Preferred:

NV12

Allowed for debugging:

RGB

BGR

MJPEG

Production:

NV12 only.

---

## 13. Forbidden Production Path

Avoid:

IMX415
↓
OpenCV BGR
↓
bgr_to_nv12()
↓
numpy copies
↓
RKNN

Reason:

High latency

High CPU usage

---

## 14. Preferred Production Path

IMX415
↓
RKISP
↓
V4L2
↓
NV12
↓
VisionIPC
↓
OpenCL
↓
RKNN

---

## 15. DMA-BUF Production Path

IMX415
↓
RKISP
↓
V4L2
↓
NV12 DMA-BUF
↓
VisionIPC
↓
OpenCL
↓
RKNN

Expected gain:

1–4 ms

---

## 16. DMA-BUF + GPU Preview Path

IMX415
↓
RKISP
↓
NV12 DMA-BUF
├→ VisionIPC → OpenCL → RKNN
└→ EGLImage → Mali GPU → UI

Expected UI gain:

3–8 ms

---

## 17. NV12 Architecture

Y Plane

UV Plane

Total:

Width × Height × 1.5

Example:

1280×720

1,382,400 bytes

---

## 18. Tight NV12

Example:

1280×720

Stride = Width

Size = W×H×1.5

---

## 19. Padded NV12

Stride > Width

or

Aligned Height > Visible Height

Must be detected.

Never assume tight layout.

---

## 20. Camera Intrinsics

Required:

Width

Height

Focal Length

Principal Point

Distortion

Generate:

intrinsics.json

---

## 21. Webcam Override Architecture

For PC/Webcam validation:

USE_WEBCAM=1

Override:

Resolution

Focal Length

Warp

Camera Model

---

## 22. Warp Architecture

Intrinsics
↓
Warp Generation
↓
Driving Model Input

Warp must match actual camera geometry.

---

## 23. Overlay Alignment

Overlay accuracy depends on:

Correct Intrinsics

Correct Warp

Correct Calibration

---

## 24. Camera Timing Architecture

Capture
↓
Publish
↓
Receive
↓
Process

All timestamps must be recorded.

---

## 25. Camera Buffer Ownership

Capture
↓
Publish
↓
Consume
↓
Release
↓
Reuse

Required for DMA-BUF safety.

---

## 26. Multi-Camera Policy

Road Camera

Wide Camera

Driver Camera

Start with:

Road Camera only.

---

## 27. Replay Compatibility

Replay must preserve:

Frames

Timestamps

Ordering

Metadata

---

## 28. Logging Compatibility

Logger must not block:

Camera

VisionIPC

Modeld

---

## 29. Camera Failure Modes

No Camera

Wrong Resolution

Wrong Format

Wrong Stride

Wrong Intrinsics

Wrong Warp

Frame Corruption

DMA-BUF Failure

---

## 30. Expected Performance

Current:

18–30 ms

camera → modelV2

DMA-BUF:

15–27 ms

camera → modelV2

DMA-BUF + EGL:

20–35 ms

camera → visible UI

---

# Section B — Validation Specification

## 31. Discovery Validation

Discover:

Sensor

ISP

Formats

FPS

Buffers

Generate:

camera_inventory.json

---

## 32. IMX415 Validation

Validate:

Detected

Streaming

Stable

Correct Resolution

---

## 33. RKISP Validation

Validate:

ISP Running

Frames Produced

No Errors

---

## 34. V4L2 Validation

Validate:

Device Exists

Format Correct

Buffers Working

---

## 35. NV12 Validation

Validate:

Width

Height

Stride

Size

Offsets

Generate:

nv12_validation.json

---

## 36. Tight vs Padded Validation

Record:

Actual Layout

Never assume.

---

## 37. DMA-BUF Validation

Validate:

FD Valid

Import Success

No Corruption

Lifetime Correct

Generate:

dmabuf_validation.json

---

## 38. EGLImage Validation

Validate:

Import

Texture

Preview

Generate:

egl_validation.json

---

## 39. Intrinsics Validation

Validate:

Focal Length

Principal Point

Resolution

---

## 40. Warp Validation

Validate:

Matrix

Crop

Scale

Alignment

Generate:

warp_validation.json

---

## 41. Replay Validation

Replay Route

Consume Frames

Compare Behavior

Generate:

replay_validation.json

---

## 42. Overlay Validation

Validate:

Path

Lane

Road Edge

Lead Vehicle

---

## 43. Timing Validation

Measure:

Capture

Publish

Receive

Display

Generate:

camera_timing.json

---

## 44. Stress Validation

1 Hour Minimum

4 Hours Preferred

Monitor:

Drops

Latency

Memory

Temperature

---

## 45. Recovery Validation

Validate:

Camera Restart

Replay Restart

DMA-BUF Reconnect

Recovery Success

---

## 46. Acceptance Criteria

Camera PASS when:

Frames Correct

Intrinsics Correct

Warp Correct

Timing Correct

No Corruption

---

# Section C — AI Agent Operating Manual

## 47. Discovery Workflow

Discover:

Sensor

RKISP

V4L2

Formats

DMA-BUF

Intrinsics

Warp

Generate:

camera_analysis.json

---

## 48. Fork Adaptation Rules

Never assume:

Video Device

Resolution

Format

Intrinsics

Warp Files

Discover dynamically.

---

## 49. Patch Strategy

Allowed:

Sensor Integration

V4L2 Integration

DMA-BUF Export

Warp Generation

Validation Hooks

Avoid:

Planner Changes

Controls Changes

Model Semantics Changes

---

## 50. IMX415 Bring-Up Workflow

Sensor
↓
RKISP
↓
V4L2
↓
NV12
↓
VisionIPC
↓
Validation
↓
DMA-BUF
↓
Validation
↓
Production

---

## 51. Reporting Requirements

Generate:

camera_inventory.json

camera_analysis.json

nv12_validation.json

dmabuf_validation.json

warp_validation.json

camera_timing.json

---

## 52. Troubleshooting

Green Image

Purple Image

Repeated Bottom Region

Wrong Overlay

Wrong Warp

Wrong Intrinsics

DMA-BUF Failure

No Frames

Document root cause and fix.

---

## 53. Production Modes

Mode 1

Baseline

RKISP
↓
VisionIPC
↓
OpenCL

Mode 2

DMA-BUF

RKISP
↓
DMA-BUF
↓
VisionIPC

Mode 3

DMA-BUF + EGLImage

RKISP
↓
DMA-BUF
├→ VisionIPC
└→ EGLImage

Recommended:

Mode 3

---

## 54. Production Readiness

Required:

IMX415 PASS

RKISP PASS

NV12 PASS

DMA-BUF PASS

Warp PASS

Replay PASS

Stress PASS

Recovery PASS

---

## 55. Final Checklist

IMX415
[ ]

RKISP
[ ]

V4L2
[ ]

NV12
[ ]

DMA-BUF
[ ]

EGLImage
[ ]

Intrinsics
[ ]

Warp
[ ]

Replay
[ ]

Stress
[ ]

Recovery
[ ]

Result:

PASS / FAIL

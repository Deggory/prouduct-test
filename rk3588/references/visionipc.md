# VISIONIPC.MD (Authoritative Version)

## Section A — Engineering Specification

### 1. Objective

Define VisionIPC architecture, ownership, transport, synchronization, DMA-BUF integration, EGLImage integration, replay integration, and AI-agent modification rules.

Target:

IMX415
↓
RKISP
↓
NV12
↓
VisionIPC
↓
modeld

Target Production:

IMX415
↓
RKISP
↓
NV12 DMA-BUF
├──────────────┬───────────────┐
│              │               │
▼              ▼               ▼
VisionIPC    EGLImage       loggerd
↓              ↓
modeld      Mali GPU
↓              ↓
RKNN         UI
↓
planner

---

### 2. VisionIPC Philosophy

VisionIPC exists to transport frames.

VisionIPC does not:

* run inference
* create tensors
* perform planning
* control the vehicle

VisionIPC must preserve:

* frame integrity
* timestamps
* stream identity
* buffer ownership

---

### 3. VisionIPC Position in OpenPilot

Camera
↓
VisionIPC
↓
modeld
↓
modelV2
↓
planner

UI Path:

VisionIPC
↓
UI
↓
GPU
↓
Display

---

### 4. Stream Architecture

Supported streams:

Road Camera

Wide Camera

Driver Camera

Road camera is the primary bring-up target.

---

### 5. VisionIPC Components

VisionIpcServer

VisionIpcClient

VisionBuf

VisionStreamType

Frame Queues

Synchronization

Buffer Management

---

### 6. Producer Architecture

Typical producer:

RKISP
↓
V4L2
↓
VisionIpcServer

Responsibilities:

Capture

Timestamp

Publish

Buffer Ownership

---

### 7. Consumer Architecture

Typical consumers:

modeld

ui

loggerd

calibrationd

Responsibilities:

Subscribe

Validate

Consume

Release

---

### 8. Buffer Lifecycle

Capture
↓
Publish
↓
Consumer Access
↓
Release
↓
Reuse

Ownership must always be documented.

---

### 9. Memory Architecture

Camera Memory

DMA-BUF Memory

VisionIPC Buffers

OpenCL Buffers

GPU Texture Buffers

RKNN Buffers

Ownership transitions must be tracked.

---

### 10. NV12 Architecture

Supported:

Tight NV12

Padded NV12

Never assume layout.

Validate explicitly.

---

### 11. Timestamp Architecture

Capture Timestamp

Publish Timestamp

Receive Timestamp

Display Timestamp

Planner Timestamp

All timestamps must be monotonic.

---

### 12. Synchronization Architecture

Frame IDs

Timestamps

Buffer State

Producer/Consumer Coordination

---

### 13. DMA-BUF Architecture

RKISP
↓
DMA-BUF
↓
VisionIPC

Goal:

Reduce copies

Reduce CPU usage

Reduce latency

---

### 14. DMA-BUF Ownership Rules

Producer allocates

Consumer imports

Producer reuses only after release

Never reuse active buffers.

---

### 15. EGLImage Architecture

DMA-BUF
↓
EGLImage
↓
Mali GPU Texture
↓
OpenGL Rendering

No CPU RGB conversion.

---

### 16. GPU Camera Preview Path

Preferred:

NV12 DMA-BUF
↓
EGLImage
↓
Mali Texture
↓
UI Overlay
↓
Display

Avoid:

NV12
↓
CPU RGB
↓
GPU Upload

---

### 17. Replay Architecture

Recorded Route
↓
Replay
↓
VisionIPC
↓
modeld

Replay must preserve:

Timestamps

Frame Ordering

Metadata

---

### 18. Logger Integration

loggerd may subscribe.

loggerd must never block:

camera

VisionIPC

modeld

---

### 19. Calibration Integration

Calibration depends on:

Timestamps

Frame Integrity

Camera Geometry

VisionIPC failures can invalidate calibration.

---

### 20. Multi-Camera Architecture

Road

Wide

Driver

Synchronization rules required.

---

## Section B — Validation Specification

### 21. Discovery Validation

Discover:

Streams

Producers

Consumers

Buffer Types

Generate:

visionipc_analysis.json

---

### 22. Stream Validation

Validate:

Exists

Alive

Frames Arriving

Correct Format

---

### 23. Frame Validation

Validate:

Width

Height

Stride

Sizeimage

Frame IDs

Timestamps

---

### 24. NV12 Validation

Validate:

Plane Offsets

Buffer Size

Layout

Generate:

nv12_validation.json

---

### 25. Timestamp Validation

Capture

Publish

Receive

Display

Monotonicity required.

---

### 26. Synchronization Validation

Validate:

Frame IDs

Ordering

No Missing Frames

---

### 27. DMA-BUF Validation

Validate:

FD Valid

Import Success

Lifetime Correct

No Corruption

Generate:

dmabuf_validation.json

---

### 28. EGLImage Validation

Validate:

Import

Texture Creation

Color Accuracy

Scaling

Generate:

egl_validation.json

---

### 29. UI Validation

Validate:

Camera Preview

Path Overlay

Lane Overlay

No Artifacts

---

### 30. Replay Validation

Replay Route

Consume Frames

Compare Outputs

Generate:

replay_validation.json

---

### 31. Logger Validation

Validate:

Logging Active

No Frame Loss

No Producer Blocking

---

### 32. Calibration Validation

Validate:

Stable Calibration

No Timestamp Drift

No Frame Corruption

---

### 33. Latency Validation

Measure:

Camera → VisionIPC

VisionIPC → modeld

VisionIPC → UI

Camera → modelV2

Camera → Display

Generate:

latency_report.json

---

### 34. Copy Count Validation

Measure:

Camera Copies

VisionIPC Copies

UI Copies

Goal:

Minimum Copies

---

### 35. Stress Validation

30 Minutes

1 Hour

4 Hours

Validate:

Memory

Latency

Stability

---

### 36. Recovery Validation

Camera Restart

Process Restart

Replay Restart

DMA-BUF Reconnect

---

### 37. Acceptance Criteria

Frames Valid

Timestamps Valid

DMA-BUF Stable

Replay Stable

UI Stable

Modeld Stable

PASS

---

## Section C — AI Agent Operating Manual

### 38. Repository Discovery Workflow

Discover:

VisionIpcServer

VisionIpcClient

VisionBuf

Streams

Consumers

Replay

DMA-BUF Support

EGL Support

Generate:

visionipc_inventory.json

---

### 39. Fork Adaptation Rules

Never assume:

Paths

Stream Names

Enums

Consumer Names

Discover dynamically.

---

### 40. Patch Strategy

Allowed:

VisionIPC

DMA-BUF Export

DMA-BUF Import

UI EGL Path

Validation Hooks

Avoid:

Planner

Controls

Vehicle Interface

---

### 41. DMA-BUF Upgrade Workflow

Baseline
↓
Validate
↓
DMA-BUF
↓
Validate
↓
EGLImage
↓
Validate

Never skip steps.

---

### 42. Reporting Requirements

Generate:

visionipc_analysis.json

visionipc_validation.json

dmabuf_validation.json

egl_validation.json

latency_report.json

copy_count_report.json

---

### 43. Troubleshooting

Green Preview

Purple Preview

Frame Corruption

Stale DMA-BUF

Dropped Frames

Timestamp Drift

EGL Import Failure

Overlay Lag

Replay Desync

Document root causes and fixes.

---

### 44. Failure Modes

Wrong Format

Wrong Stride

Wrong Buffer Size

Invalid Timestamp

DMA-BUF Reuse

GPU Import Failure

Replay Failure

Frame Starvation

---

### 45. Production Deployment Modes

Mode 1

RKISP
↓
VisionIPC
↓
OpenCL
↓
RKNN

Mode 2

RKISP
↓
DMA-BUF
↓
VisionIPC
↓
OpenCL
↓
RKNN

Mode 3

RKISP
↓
DMA-BUF
├→ VisionIPC → RKNN
└→ EGLImage → Mali GPU → UI

Recommended:

Mode 3

---

### 46. Performance Targets

Mode 1

Camera → modelV2

18–30 ms

Mode 2

15–27 ms

Mode 3

15–27 ms

Camera → UI

20–35 ms

---

### 47. Production Readiness

Required:

VisionIPC PASS

Replay PASS

DMA-BUF PASS

EGL PASS

Latency PASS

Stress PASS

Recovery PASS

---

### 48. Final Checklist

Streams
[ ]

NV12
[ ]

Timestamps
[ ]

Replay
[ ]

DMA-BUF
[ ]

EGLImage
[ ]

UI
[ ]

Latency
[ ]

Stress
[ ]

Recovery
[ ]

Result:

PASS / FAIL

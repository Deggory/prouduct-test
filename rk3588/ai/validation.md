# VALIDATION.MD (Authoritative Version)

# Engineering Specification + Validation Specification + AI Agent Operating Manual

Version: 2.0

Target Hardware:

* RK3588
* RK3588S
* Orange Pi 5
* Orange Pi 5 Plus

Target Camera:

* IMX415
* RKISP
* V4L2
* NV12
* DMA-BUF

Target Runtime:

* RKNN Vision Core 0
* RKNN Policy Core 1
* OpenCL
* Mali GPU
* EGLImage

Target Forks:

* openpilot
* sunnypilot
* frogpilot
* OPKR
* KisaPilot

---

# Section A — Engineering Specification

## 1. Objective

Validation exists to prove:

Camera Correct
↓
VisionIPC Correct
↓
Preprocessing Correct
↓
Metadata Correct
↓
Vision Model Correct
↓
Policy Model Correct
↓
Planner Correct
↓
System Stable

Validation is proof.

UI appearance alone is not validation.

---

## 2. Validation Philosophy

Every layer must pass independently.

Failure at any layer invalidates all higher layers.

Validation order:

Camera
↓
VisionIPC
↓
Preprocessing
↓
Metadata
↓
Vision
↓
Policy
↓
Planner
↓
System

---

## 3. Golden Reference Philosophy

Reference implementation:

Tinygrad

or

Official OpenPilot implementation

All comparisons must use:

Identical Inputs

---

## 4. Validation Architecture

Discovery
↓
Artifact Collection
↓
Metric Generation
↓
Comparison
↓
Acceptance
↓
PASS / FAIL

---

## 5. Validation Ownership

camera.md

owns:

Camera Correctness

visionipc.md

owns:

Frame Correctness

modeld.md

owns:

Tensor Correctness

rknn.md

owns:

Inference Correctness

validation.md

owns:

Proof

---

## 6. Production Pipeline

IMX415
↓
RKISP
↓
NV12 DMA-BUF
├──────────────┬──────────────┐
│              │              │
▼              ▼              ▼
VisionIPC    EGLImage       loggerd
↓              ↓
OpenCL       Mali GPU
↓              ↓
RKNN         UI
↓
modelV2
↓
Planner

Every stage must be validated.

---

## 7. Validation Artifacts

Generate:

camera_validation.json

visionipc_validation.json

metadata_validation.json

tensor_validation.json

vision_validation.json

policy_validation.json

planner_validation.json

system_validation.json

validation_inventory.json

---

## 8. Dataset Requirements

Minimum:

1000 Frames

Preferred:

10000+ Frames

Production:

Multiple Routes

---

## 9. Validation Environments

Replay

Recorded Video

Live Camera

Bench Testing

Vehicle Testing

All should be documented.

---

## 10. Acceptance Philosophy

PASS

means:

Measured

Validated

Documented

Repeatable

---

# Section B — Camera Validation

## 11. Camera Discovery Validation

Validate:

Device

Resolution

FPS

Format

Sensor

Generate:

camera_inventory.json

---

## 12. IMX415 Validation

Validate:

Sensor Detected

Resolution Correct

FPS Stable

No Frame Corruption

---

## 13. RKISP Validation

Validate:

ISP Active

Frames Delivered

No ISP Errors

---

## 14. V4L2 Validation

Validate:

Device Node

Format

Buffer Mode

Frame Timing

---

## 15. NV12 Validation

Validate:

Width

Height

Stride

Plane Offsets

Buffer Size

Layout

Never assume.

---

## 16. Tight vs Padded Validation

Detect:

Tight NV12

or

Padded NV12

Record actual layout.

---

## 17. DMA-BUF Validation

Validate:

FD Valid

Import Success

Lifetime Correct

No Corruption

Generate:

dmabuf_validation.json

---

## 18. Camera Timing Validation

Measure:

Capture

Publish

Receive

Latency

Generate:

camera_timing.json

---

## 19. Overlay Validation

Validate:

Preview

Path

Lane

Road Edge

Lead Vehicle

---

## 20. Camera Acceptance Criteria

Camera PASS

when:

Frames Correct

Timing Correct

No Corruption

---

# Section C — VisionIPC Validation

## 21. Stream Validation

Validate:

Producer

Consumers

Frames Arriving

Generate:

visionipc_inventory.json

---

## 22. Timestamp Validation

Validate:

Capture

Publish

Receive

Display

Monotonicity required.

---

## 23. Frame ID Validation

Validate:

Monotonic IDs

No Duplicates

No Unexpected Jumps

---

## 24. Synchronization Validation

Validate:

Ordering

Timing

Consumer Alignment

---

## 25. Replay Validation

Replay Route
↓
VisionIPC
↓
Modeld

Must match reference behavior.

---

## 26. EGLImage Validation

Validate:

Import

Texture Creation

Preview

Generate:

egl_validation.json

---

## 27. UI Validation

Validate:

Preview

Overlay

Latency

No Artifacts

---

# Section D — Preprocessing Validation

## 28. OpenCL Validation

Validate:

loadyuv.cl

transform.cl

Execution Success

Generate:

opencl_validation.json

---

## 29. Tensor Validation

Dump:

img

big_img

feature tensors

Generate:

tensor_validation.json

---

## 30. Tensor Layout Validation

Validate:

NCHW

or

NHWC

Record actual layout.

---

## 31. Tensor Statistics Validation

Record:

Min

Max

Mean

Std

Compare with reference.

---

## 32. Tensor Reconstruction Validation

Tensor
↓
Image Reconstruction

Inspect:

Crop

Warp

Color

Artifacts

---

## 33. Warp Validation

Validate:

Transform Matrix

Crop Region

Scale

Alignment

Generate:

warp_validation.json

---

# Section E — Metadata Validation

## 34. Metadata Discovery

Locate:

Metadata Files

Version

Hashes

Generate:

metadata_inventory.json

---

## 35. Metadata Validation

Validate:

Inputs

Outputs

Shapes

Dtypes

Slices

Names

---

## 36. Slice Validation

Validate:

Start

End

Ownership

Semantic Meaning

---

## 37. Metadata Acceptance

Metadata must match:

Model

Runtime

Outputs

Exactly.

---

# Section F — Vision Model Validation

## 38. Vision Input Validation

Validate:

Input Count

Shape

Layout

Dtype

---

## 39. Vision Output Validation

Validate:

Output Count

Shape

Layout

Dtype

---

## 40. Tinygrad vs RKNN Validation

Tinygrad
↓
Reference

RKNN
↓
Candidate

Same Input

Compare Outputs

---

## 41. Vision Metrics

Calculate:

MAE

Relative MAE

Correlation

Cosine Similarity

---

## 42. Vision Acceptance Targets

Minimum:

Correlation > 0.995

Preferred:

Correlation > 0.999

---

# Section G — Policy Validation

## 43. Policy Input Validation

Validate:

Features

Desire

Traffic Convention

Curvature Inputs

---

## 44. Policy Output Validation

Validate:

Trajectory

Curvature

Decision Outputs

---

## 45. Tinygrad vs RKNN Policy Validation

Same Features

Compare Outputs

---

## 46. Policy Metrics

MAE

Relative MAE

Correlation

Cosine Similarity

---

## 47. Policy Acceptance Targets

Minimum:

Correlation > 0.995

Preferred:

Correlation > 0.999

---

# Section H — Planner Validation

## 48. Planner Health Validation

Validate:

Alive

Stable

Responsive

---

## 49. Planner Output Validation

Compare:

Trajectory

Curvature

Path

Against Reference

---

## 50. Message Validation

Validate:

modelV2

cameraOdometry

Units

Schemas

Frequency

---

## 51. Overlay Validation

Validate:

Overlay Stability

Alignment

Road Tracking

No Clipping

---

# Section I — System Validation

## 52. Latency Validation

Measure:

Camera

VisionIPC

OpenCL

Vision

Policy

Publish

Planner

UI

Generate:

latency_report.json

---

## 53. FPS Validation

Measure:

Average FPS

Minimum FPS

Maximum FPS

95%

99%

---

## 54. Memory Validation

Measure:

RSS

Virtual Memory

Allocation Count

Leaks

Generate:

memory_validation.json

---

## 55. Thermal Validation

Measure:

CPU

GPU

NPU

Board

Generate:

thermal_validation.json

---

## 56. Stress Validation

Minimum:

1 Hour

Preferred:

4 Hours

Monitor:

Latency

Memory

Temperature

FPS

---

## 57. Recovery Validation

Validate:

Camera Restart

Replay Restart

Runtime Restart

Model Reload

Recovery Success

---

## 58. Failure Injection

Simulate:

Corrupt Metadata

Corrupt Model

Invalid Tensor

DMA-BUF Failure

Runtime Failure

Validate safe behavior.

---

# Section J — AI Agent Operating Manual

## 59. Discovery Workflow

Discover:

Camera

VisionIPC

OpenCL

Metadata

Modeld

RKNN

Planner

UI

Generate:

validation_inventory.json

---

## 60. Validation Workflow

Discovery
↓
Camera
↓
VisionIPC
↓
Preprocessing
↓
Metadata
↓
Vision
↓
Policy
↓
Planner
↓
System

---

## 61. Fork Adaptation Rules

Never assume:

Paths

Model Names

Metadata Locations

Runtime Layout

Environment Variables

Discover dynamically.

---

## 62. Reporting Requirements

Generate:

camera_validation.json

visionipc_validation.json

tensor_validation.json

metadata_validation.json

vision_validation.json

policy_validation.json

planner_validation.json

system_validation.json

latency_report.json

validation_inventory.json

---

## 63. Troubleshooting

Wrong Overlay

Tensor Mismatch

Metadata Mismatch

Replay Failure

DMA-BUF Failure

EGL Failure

Planner Instability

Memory Leak

Thermal Issues

Document root cause and fix.

---

## 64. Failure Modes

Camera Failure

VisionIPC Failure

Tensor Failure

Metadata Failure

Vision Failure

Policy Failure

Planner Failure

System Failure

---

## 65. Production Readiness

Required:

Camera PASS

VisionIPC PASS

OpenCL PASS

Metadata PASS

Vision PASS

Policy PASS

Planner PASS

Latency PASS

Memory PASS

Thermals PASS

Recovery PASS

---

## 66. Production Gate

Deployment prohibited until:

All validation sections PASS.

No exceptions.

---

## 67. Final Checklist

Camera
[ ]

VisionIPC
[ ]

DMA-BUF
[ ]

EGLImage
[ ]

OpenCL
[ ]

Metadata
[ ]

Vision
[ ]

Policy
[ ]

Planner
[ ]

Latency
[ ]

FPS
[ ]

Memory
[ ]

Thermals
[ ]

Recovery
[ ]

Result:

PASS / FAIL

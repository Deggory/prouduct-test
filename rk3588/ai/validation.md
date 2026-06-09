# VALIDATION.MD (Authoritative Version)

## Section A — Engineering Specification

### 1. Objective

Validation exists to prove:

Camera Integration Correct
↓
Preprocessing Correct
↓
Model Outputs Correct
↓
Planner Behavior Preserved
↓
Deployment Safe

Validation is not:

"The UI looks correct"

Validation is:

"The tensors, outputs, and planner behavior match the reference implementation."

---

### 2. Validation Philosophy

Every layer must be validated independently.

Failure at any layer invalidates all subsequent layers.

Validation order:

Camera
↓
VisionIPC
↓
Preprocessing
↓
Metadata
↓
Vision Model
↓
Policy Model
↓
Planner
↓
System

---

### 3. Golden Reference Philosophy

Reference implementation:

Tinygrad

or

Official OpenPilot model pipeline

All comparisons must use identical inputs.

---

### 4. Validation Architecture

Validation System

↓

Data Collection

↓

Artifact Generation

↓

Metric Generation

↓

Acceptance Analysis

↓

Pass / Fail

---

### 5. Validation Ownership

camera.md owns:

* Camera correctness
* NV12 correctness
* Warp correctness

modeld.md owns:

* Tensor correctness
* State correctness

rknn.md owns:

* Runtime correctness
* RKNN correctness

validation.md owns:

* Proof

---

### 6. Artifact Architecture

Required artifacts:

camera_validation.json

visionipc_validation.json

tensor_validation.json

metadata_validation.json

vision_validation.json

policy_validation.json

runtime_validation.json

planner_validation.json

system_validation.json

---

### 7. Dataset Architecture

Required scenarios:

Day

Night

Highway

City

Curves

Shadows

Rain

Tunnel

Construction Zones

---

### 8. Dataset Requirements

Minimum:

1000 Frames

Preferred:

10000+ Frames

Production:

Multiple Routes

---

### 9. Validation Environment

Replay

Recorded Video

Live Camera

Bench Testing

Vehicle Testing

Each environment must be documented.

---

### 10. Validation Layer Ownership

Layer 1

Camera

Layer 2

Preprocessing

Layer 3

Metadata

Layer 4

Vision

Layer 5

Policy

Layer 6

Planner

Layer 7

System

---

## Section B — Camera Validation

### 11. Camera Discovery Validation

Validate:

Resolution

FPS

Format

Sensor

Generate:

camera_inventory.json

---

### 12. Resolution Validation

Record:

Width

Height

FPS

Configured

Actual

---

### 13. NV12 Validation

Validate:

bytesperline

sizeimage

stride

layout

tight vs padded

Never assume.

---

### 14. VisionIPC Validation

Validate:

Frame Arrival

Frame Integrity

Frame IDs

Timestamps

No Corruption

Generate:

visionipc_validation.json

---

### 15. Camera Timing Validation

Record:

Capture

Publish

Receive

Latency

---

### 16. Warp Validation

Validate:

Crop

Scale

Alignment

Output Geometry

Generate:

warp_validation.json

---

### 17. Overlay Validation

Validate:

Path Overlay

Lane Overlay

Road Edge Overlay

Lead Vehicle Overlay

---

### 18. Overlay Acceptance Criteria

Overlay must:

Remain Centered

Follow Road Geometry

Remain Stable

No Clipping

No Offset

---

## Section C — Preprocessing Validation

### 19. OpenCL Validation

Validate:

loadyuv.cl

transform.cl

Execution correctness

---

### 20. Tensor Dump Validation

Dump:

img

big_img

Record:

Shape

Layout

Dtype

Statistics

---

### 21. Tensor Layout Validation

Validate:

NCHW

or

NHWC

Record actual layout.

---

### 22. Tensor Statistics Validation

Record:

Min

Max

Mean

Standard Deviation

Compare with reference.

---

### 23. Visual Reconstruction Validation

Tensor
↓
Reconstructed Image

Inspect:

Cropping

Distortion

Artifacts

Color Shifts

---

## Section D — Metadata Validation

### 24. Metadata Discovery

Locate:

Metadata Files

Version

Hashes

Generate:

metadata_inventory.json

---

### 25. Metadata Validation

Validate:

Input Count

Output Count

Shapes

Dtypes

Names

Slices

---

### 26. Slice Validation

Validate:

Start Index

End Index

Output Ownership

Semantic Meaning

---

## Section E — Vision Model Validation

### 27. Vision Input Validation

Validate:

Input Count

Shapes

Layouts

Dtypes

---

### 28. Vision Output Validation

Validate:

Output Count

Shapes

Layouts

Dtypes

---

### 29. Vision Comparison

Tinygrad
↓
RKNN

Same Inputs

Compare Outputs

---

### 30. Vision Metrics

Calculate:

MAE

Relative MAE

Correlation

Cosine Similarity

---

### 31. Vision Acceptance Targets

Minimum:

Correlation > 0.995

Preferred:

Correlation > 0.999

---

## Section F — Policy Validation

### 32. Policy Input Validation

Validate:

Features

Desire

Traffic Convention

Curvature Inputs

---

### 33. Policy Output Validation

Validate:

Trajectory

Curvature

Decisions

---

### 34. Policy Comparison

Tinygrad
↓
RKNN

Same Features

Compare Outputs

---

### 35. Policy Metrics

MAE

Relative MAE

Correlation

Cosine Similarity

---

### 36. Policy Acceptance Targets

Minimum:

Correlation > 0.995

Preferred:

Correlation > 0.999

---

## Section G — Temporal Validation

### 37. Hidden State Validation

Validate:

hidden_state

feature_memory

transformer cache

Persistence

---

### 38. Multi-Frame Validation

Minimum:

100 Consecutive Frames

Single frame testing prohibited.

---

### 39. Feature Buffer Validation

Validate:

Reuse

Persistence

Update Logic

---

## Section H — Runtime Validation

### 40. Runtime Validation

Verify:

RKNN Runtime

Toolkit

NPU Availability

Core Assignment

---

### 41. NPU Validation

Validate:

Core 0

Core 1

Core 2

Assignments

Behavior

---

### 42. Runtime API Validation

Validate:

inference()

or

inputs_set()

run()

outputs_get()

---

## Section I — Planner Validation

### 43. Planner Health Validation

Planner Alive

Planner Stable

Planner Responsive

No Crashes

---

### 44. Planner Output Validation

Compare:

Trajectory

Curvature

Path

Against Reference

---

### 45. Message Validation

Validate:

modelV2

cameraOdometry

Related Outputs

Schemas

Units

---

## Section J — System Validation

### 46. Latency Validation

Record:

Camera

Preprocessing

Inference

Parsing

Publishing

Total

---

### 47. FPS Validation

Measure:

Input FPS

Inference FPS

Published FPS

---

### 48. Memory Validation

Run:

30 Minutes Minimum

Record:

RSS

Virtual Memory

Tensor Allocation Count

---

### 49. Thermal Validation

Record:

CPU Temperature

GPU Temperature

NPU Temperature

No throttling permitted.

---

### 50. Long Duration Validation

Minimum:

1 Hour

Preferred:

4+ Hours

---

### 51. Recovery Validation

Camera Disconnect

Runtime Restart

Process Restart

Model Reload

System must recover.

---

### 52. Failure Injection

Simulate:

Corrupt Model

Missing Metadata

Invalid Tensor

Runtime Failure

Validate safe failure.

---

## Section K — AI Agent Operating Manual

### 53. Repository Discovery Workflow

Discover:

Camera

VisionIPC

Metadata

Runtime

Planner

Generate:

validation_analysis.json

---

### 54. Fork Adaptation Rules

Never assume:

Paths

Model Names

Metadata Locations

Environment Variables

Discover dynamically.

---

### 55. Validation Workflow

Discover
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

### 56. Reporting Requirements

Generate:

camera_validation.json

vision_validation.json

policy_validation.json

runtime_validation.json

latency_validation.json

planner_validation.json

system_validation.json

validation_analysis.json

---

### 57. Failure Modes

Overlay Failure

Tensor Failure

Metadata Failure

Runtime Failure

Planner Failure

Memory Leak

Thermal Throttling

Recovery Failure

---

### 58. Production Readiness

Required:

Camera PASS

Metadata PASS

Vision PASS

Policy PASS

Planner PASS

Runtime PASS

Latency PASS

Memory PASS

Thermals PASS

Recovery PASS

---

### 59. Production Validation Gate

Deployment prohibited until:

All validation sections PASS.

No exceptions.

---

### 60. Final Checklist

Camera
[ ]

NV12
[ ]

VisionIPC
[ ]

Warp
[ ]

Metadata
[ ]

Vision
[ ]

Policy
[ ]

Runtime
[ ]

Planner
[ ]

Latency
[ ]

Memory
[ ]

Thermals
[ ]

Recovery
[ ]

Result:

PASS / FAIL

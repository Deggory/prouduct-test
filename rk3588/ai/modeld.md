# MODELD.MD (Authoritative Version)

# Engineering Specification + Validation Specification + AI Agent Operating Manual

Version: 3.0

Target Hardware:

* RK3588
* RK3588S
* Orange Pi 5
* Orange Pi 5 Plus

Target Runtime:

* RKNN Vision Core 0
* RKNN Policy Core 1
* OpenCL Preprocessing
* DMA-BUF
* VisionIPC

Target Camera:

* IMX415
* RKISP
* NV12

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

* modeld architecture
* preprocessing pipeline
* tensor generation
* metadata handling
* RKNN integration
* model output publishing
* planner interaction
* validation requirements

Goal:

Production-quality RK3588 modeld implementation.

---

## 2. What modeld Is

modeld is the perception runtime.

It is responsible for:

Camera Frames
↓
Preprocessing
↓
Tensor Generation
↓
Vision Model
↓
Policy Model
↓
Output Parsing
↓
modelV2
↓
Planner

modeld is not:

* camera driver
* VisionIPC transport
* planner
* controls system

---

## 3. Production Pipeline

IMX415
↓
RKISP
↓
NV12 DMA-BUF
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
Vision Tensor
↓
RKNN Vision Core 0
↓
Hidden State
↓
RKNN Policy Core 1
↓
Output Parsing
↓
modelV2/msgq
↓
Planner

---

## 4. Modeld Ownership

camera.md

owns:

Camera Correctness

visionipc.md

owns:

Frame Transport

modeld.md

owns:

Preprocessing

Tensor Generation

Model Orchestration

Output Parsing

rknn.md

owns:

RKNN Runtime

validation.md

owns:

Correctness Verification

---

## 5. Modeld Philosophy

Do not rewrite working preprocessing.

The safest architecture is:

NV12
↓
loadyuv.cl
↓
transform.cl
↓
Tensor
↓
RKNN

Only inference changes.

---

## 6. Tinygrad Replacement Rule

Replace:

tinygrad inference

Do not replace:

camera pipeline

warp generation

preprocessing

metadata semantics

planner outputs

---

## 7. Vision Model Ownership

Vision model generates:

* scene understanding
* feature vectors
* hidden state

Vision model executes first.

---

## 8. Policy Model Ownership

Policy model consumes:

features

desire

hidden state

driving context

Policy executes second.

---

## 9. Production RKNN Assignment

Vision

↓

Core 0

Policy

↓

Core 1

Core 2

↓

Reserved

---

## 10. Hidden State Architecture

Vision
↓
hidden_state
↓
Policy

Hidden state must persist across frames.

---

## 11. Temporal Architecture

Single-frame validation is insufficient.

Validate:

100+

Consecutive Frames

Minimum.

---

## 12. OpenCL Architecture

Production preprocessing:

loadyuv.cl
↓
transform.cl

Do not bypass unless validated.

---

## 13. Why OpenCL Remains

OpenCL already produces:

Correct tensors

Correct geometry

Correct warps

Changing it increases risk.

---

## 14. Tensor Architecture

Typical outputs:

img

big_img

feature tensors

hidden state

---

## 15. Tensor Layout Policy

Supported:

NCHW

NHWC

Layout must be discovered.

Never assumed.

---

## 16. Metadata Architecture

Metadata defines:

Inputs

Outputs

Shapes

Dtypes

Slices

Semantics

Metadata is authoritative.

---

## 17. Metadata Rule

Never hardcode:

Output indices

Slice locations

Output ownership

Read metadata.

---

## 18. Output Parsing Architecture

Vision Output
↓
Metadata
↓
Parsed Structures
↓
modelV2

---

## 19. Message Publishing

Publish:

modelV2

cameraOdometry

related messages

through msgq/cereal

---

## 20. Planner Interface

Planner consumes:

modelV2

Modeld must preserve:

schema

units

frequency

semantics

---

## 21. CPU Architecture

Prefer:

A76 cores

CPU4–CPU7

for modeld.

---

## 22. Scheduler Policy

Optional:

SCHED_FIFO

Priority:

50–60

Only after validation.

---

## 23. Performance Targets

Current:

18–30 ms

Camera → modelV2

Target:

<30 ms

---

## 24. DMA-BUF Interaction

DMA-BUF affects:

Frame transport

Not:

Tensor semantics

Not:

Model outputs

---

## 25. VisionIPC Interaction

Modeld consumes:

VisionIPC frames

Modeld must validate:

format

timestamps

layout

before preprocessing.

---

## 26. Replay Compatibility

Replay must generate identical:

tensors

outputs

planner behavior

when compared to live input.

---

## 27. Failure Modes

Wrong Tensor

Wrong Layout

Wrong Metadata

Wrong Hidden State

Wrong Outputs

Planner Instability

Must be detected.

---

## 28. Production Rule

Never optimize:

Before validation.

Never deploy:

Before validation.

---

# Section B — Validation Specification

## 29. Discovery Validation

Discover:

modeld path

metadata

runtime

inputs

outputs

Generate:

modeld_inventory.json

---

## 30. Input Validation

Validate:

Frame Shape

Frame Layout

Frame Timing

Frame Integrity

---

## 31. VisionIPC Validation

Validate:

Frames Arrive

Timestamps Valid

No Corruption

---

## 32. OpenCL Validation

Validate:

loadyuv.cl

transform.cl

Execution Success

Generate:

opencl_validation.json

---

## 33. Tensor Dump Validation

Dump:

img

big_img

hidden state

Generate:

tensor_validation.json

---

## 34. Tensor Statistics Validation

Record:

Min

Max

Mean

Std

Compare with reference.

---

## 35. Tensor Reconstruction Validation

Tensor
↓
Image

Validate:

crop

warp

color

alignment

---

## 36. Metadata Validation

Validate:

Input Count

Output Count

Shapes

Dtypes

Slices

Generate:

metadata_validation.json

---

## 37. Vision Validation

Tinygrad
↓
Reference

RKNN
↓
Candidate

Same Input

Compare Outputs

---

## 38. Vision Metrics

MAE

Relative MAE

Correlation

Cosine Similarity

---

## 39. Vision Acceptance

Minimum:

Correlation > 0.995

Preferred:

Correlation > 0.999

---

## 40. Policy Validation

Same Features

Compare Outputs

Generate:

policy_validation.json

---

## 41. Policy Metrics

MAE

Relative MAE

Correlation

Cosine Similarity

---

## 42. Policy Acceptance

Minimum:

Correlation > 0.995

Preferred:

Correlation > 0.999

---

## 43. Hidden State Validation

Validate:

Persistence

Reuse

Temporal Consistency

---

## 44. Multi-Frame Validation

Minimum:

100 Frames

Preferred:

1000+

---

## 45. Output Validation

Validate:

modelV2

cameraOdometry

Units

Schemas

Frequency

---

## 46. Planner Validation

Validate:

Planner Alive

Planner Stable

Planner Outputs Reasonable

---

## 47. Replay Validation

Replay Route

Compare Outputs

Generate:

replay_validation.json

---

## 48. Latency Validation

Measure:

Preprocessing

Vision

Policy

Publishing

Generate:

latency_report.json

---

## 49. Stress Validation

1 Hour Minimum

4 Hours Preferred

Validate:

Memory

Latency

Temperature

---

## 50. Recovery Validation

Validate:

Runtime Restart

Model Reload

Replay Restart

Recovery Success

---

## 51. Acceptance Criteria

Modeld PASS when:

Tensor PASS

Metadata PASS

Vision PASS

Policy PASS

Planner PASS

Latency PASS

---

# Section C — AI Agent Operating Manual

## 52. Repository Discovery Workflow

Discover:

modeld

metadata

runtime

inputs

outputs

planner interface

Generate:

modeld_analysis.json

---

## 53. Fork Adaptation Rules

Never assume:

model names

metadata paths

runtime names

output ordering

Discover dynamically.

---

## 54. RKNN Port Workflow

Discover
↓
Tensor Validation
↓
Metadata Validation
↓
Vision Validation
↓
Policy Validation
↓
Planner Validation
↓
Performance Validation
↓
Deployment

---

## 55. Allowed Modifications

Inference Runtime

Metadata Reader

Validation Hooks

Performance Tools

Output Verification

---

## 56. Avoid Modifications

Planner Logic

Controls Logic

Message Semantics

Camera Geometry

Warp Logic

Unless explicitly required.

---

## 57. Reporting Requirements

Generate:

modeld_inventory.json

modeld_analysis.json

tensor_validation.json

metadata_validation.json

vision_validation.json

policy_validation.json

latency_report.json

---

## 58. Troubleshooting

Wrong Overlay

Wrong Tensor

Wrong Metadata

Wrong Hidden State

Wrong Planner Output

Runtime Failure

Document root cause and fix.

---

## 59. Production Modes

Mode 1

Tinygrad

Mode 2

RKNN Vision Only

Mode 3

RKNN Vision + Policy

Recommended:

Mode 3

---

## 60. Production Readiness

Required:

Tensor PASS

Metadata PASS

Vision PASS

Policy PASS

Planner PASS

Latency PASS

Replay PASS

Recovery PASS

---

## 61. Final Checklist

VisionIPC
[ ]

OpenCL
[ ]

Tensor
[ ]

Metadata
[ ]

Vision
[ ]

Policy
[ ]

Hidden State
[ ]

Planner
[ ]

Latency
[ ]

Replay
[ ]

Recovery
[ ]

Result:

PASS / FAIL

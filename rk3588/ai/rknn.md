# RKNN.MD (Authoritative Version)

## Section A — Engineering Specification

### 1. Objective

Preserve:

* Model outputs
* Planner behavior
* Tensor semantics
* Metadata semantics

Replace only:

Tinygrad
↓
RKNN

No planner modifications.

No controls modifications.

No vehicle interface modifications.

---

### 2. RKNN Integration Philosophy

Required behavior:

Same Inputs
↓
Same Tensors
↓
Same Metadata
↓
Same Outputs

Only execution backend changes.

---

### 3. RK3588 NPU Architecture

NPU Core 0

NPU Core 1

NPU Core 2

Approximate capability:

6 TOPS INT8

Validate actual runtime.

---

### 4. NPU Ownership

Vision Model

↓

Core 0

Policy Model

↓

Core 1

Core 2

↓

Reserved

Ownership documented.

---

### 5. Core Assignment Rules

Never share:

Vision

and

Policy

on the same core.

Avoid:

RKNNLite.NPU_CORE_AUTO

for production.

---

### 6. Runtime Architecture

Application

↓

ModelRunner

↓

RKNNRunner

↓

RKNN Runtime

↓

NPU

Modeld must never directly call RKNN APIs.

---

### 7. Runtime Discovery

Validate:

/dev/rknpu0

Runtime library

Toolkit version

Kernel support

Generate:

runtime_report.json

---

### 8. Model Discovery

Discover:

driving_vision.rknn

driving_policy.rknn

Generate:

model_inventory.json

Record:

* size
* hash
* version
* timestamp

---

### 9. Runtime API Architecture

Support:

inference()

or

inputs_set()
run()
outputs_get()

Detect automatically.

---

### 10. Runtime Abstraction Layer

ModelRunner

Required interface:

initialize()

validate()

infer()

shutdown()

---

### 11. RKNNRunner Architecture

Responsibilities:

* load model
* validate metadata
* validate inputs
* execute inference
* validate outputs

Non-responsibilities:

* camera
* preprocessing
* planner
* metadata parsing

---

### 12. Model Loading

Load:

Vision Model

and

Policy Model

separately.

Never merge.

---

### 13. Backend Selection

Supported:

OPENPILOT_MODELD_BACKEND=tinygrad

OPENPILOT_MODELD_BACKEND=rknn

OPENPILOT_MODELD_BACKEND=auto

---

### 14. Tinygrad Fallback

Tinygrad remains mandatory.

Purposes:

* validation
* debugging
* unsupported hardware
* recovery

Never remove Tinygrad.

---

### 15. Tensor Architecture

Image Tensors

State Tensors

Feature Tensors

Policy Tensors

Ownership belongs to modeld.

---

### 16. Tensor Layout Architecture

Possible:

NCHW

NHWC

Never assume.

Validate.

---

### 17. NCHW Specification

Example:

[1,12,128,256]

Batch

Channels

Height

Width

---

### 18. NHWC Specification

Example:

[1,128,256,12]

Batch

Height

Width

Channels

---

### 19. Layout Conversion Strategy

Convert only at:

Inference Boundary

Never modify:

VisionIPC

loadyuv.cl

transform.cl

DrivingModelFrame.prepare()

---

### 20. NHWC RKNN Integration

Recommended:

Camera
↓
Preprocessing
↓
NCHW Tensor
↓
Transpose
↓
NHWC RKNN Input

Inference

---

### 21. Vision Model Architecture

Consumes:

img

big_img

Optional calibration inputs

Produces:

path

lanes

road edges

features

hidden state

---

### 22. Policy Model Architecture

Consumes:

features_buffer

desire

traffic_convention

lateral_control_params

prev_desired_curv

Produces:

trajectory

curvature

policy decisions

---

### 23. Hidden State Architecture

Examples:

LSTM

GRU

Transformer Cache

Feature Buffer

History Tensor

Must persist.

---

### 24. Feature Buffer Lifecycle

Frame N
↓
Inference
↓
Update Buffer
↓
Frame N+1
↓
Reuse Buffer

---

### 25. Metadata Ownership

Metadata owns:

* input names
* output names
* shapes
* slices
* semantics

RKNN does not own metadata.

---

## Section B — Validation Specification

### 26. Runtime Validation

Verify:

Runtime Available

NPU Available

API Detected

Version Recorded

---

### 27. Model Validation

Verify:

File Exists

Readable

Correct Version

Correct Hash

---

### 28. Metadata Validation

Validate:

Input Count

Output Count

Input Shapes

Output Shapes

Dtypes

Generate:

metadata_report.json

---

### 29. Tensor Validation

Validate:

Shape

Layout

Dtype

Batch

Generate:

tensor_validation.json

---

### 30. Layout Validation

Validate:

NCHW

or

NHWC

Never infer.

---

### 31. Vision Validation

Generate:

vision_validation.json

Record:

Inputs

Outputs

Shapes

Layouts

Dtypes

---

### 32. Policy Validation

Generate:

policy_validation.json

Record:

Inputs

Outputs

Shapes

Layouts

Dtypes

---

### 33. Hidden State Validation

Generate:

hidden_state_report.json

Validate:

Persistence

Shape

Dtype

Consistency

---

### 34. Feature Buffer Validation

Validate:

Buffer Size

Reuse

Persistence

Update Logic

---

### 35. ONNX Reference Validation

ONNX becomes reference implementation.

Compare:

ONNX

↓

RKNN

---

### 36. Validation Dataset

Use:

Replay Routes

Driving Clips

Recorded Datasets

Webcam Testing

Generate:

validation_dataset.json

---

### 37. Comparison Metrics

Required:

MAE

Relative MAE

Correlation

Cosine Similarity

---

### 38. Acceptance Targets

Vision:

Correlation > 0.995

Policy:

Correlation > 0.995

---

### 39. Multi-Frame Validation

Minimum:

100 consecutive frames

Single-frame validation is insufficient.

---

### 40. Timing Validation

Record:

Inference Start

Inference End

Latency

FPS

Generate:

timing_report.json

---

### 41. Queue Validation

Input Queue

Inference Queue

Dropped Frames

Generate:

queue_report.json

---

### 42. Memory Validation

RSS

Virtual Memory

Tensor Allocations

30-minute test minimum.

---

### 43. Threading Validation

Camera Thread

Preprocess Thread

Inference Thread

Publish Thread

Validate no starvation.

---

### 44. Stress Testing

30 Minutes

1 Hour

4 Hours

Generate:

stress_report.json

---

### 45. Recovery Testing

Reload Runtime

Reload Model

Restart Runner

Revalidate Outputs

---

### 46. Acceptance Test Suite

Runtime Test

Metadata Test

Tensor Test

Vision Test

Policy Test

State Test

Timing Test

Recovery Test

Stress Test

---

## Section C — AI Agent Operating Manual

### 47. Repository Discovery Workflow

Discover:

* runtime layer
* runner layer
* model locations
* metadata locations
* backend selection

Generate:

rknn_analysis.json

---

### 48. Fork Adaptation Rules

Never assume:

* paths
* model names
* metadata names
* environment variables

Discover dynamically.

---

### 49. Patch Strategy

Allowed:

RKNNRunner

Backend Selection

Runtime Detection

Layout Conversion

Validation Layer

Avoid:

Planner

Controls

Vehicle Interface

---

### 50. AI Agent Validation Workflow

Discover
↓
Runtime Validation
↓
Model Validation
↓
Metadata Validation
↓
Tensor Validation
↓
ONNX Comparison
↓
Stress Test
↓
Recovery Test

---

### 51. Reporting Requirements

Generate:

runtime_report.json

metadata_report.json

vision_validation.json

policy_validation.json

hidden_state_report.json

queue_report.json

performance_report.json

rknn_analysis.json

---

### 52. Failure Modes

Wrong Layout

Wrong Shape

Metadata Mismatch

Hidden State Reset

Runtime Crash

NPU Timeout

Memory Leak

Output Mismatch

---

### 53. Error Handling Policy

Fail Fast

Generate Report

Preserve Logs

Do Not Publish Invalid Outputs

---

### 54. Recovery Policy

Allowed:

Reload Model

Reload Runtime

Restart RKNNRunner

Not Allowed:

Silent Failure

Publishing Invalid Outputs

---

### 55. Production Readiness

Required:

Runtime Stable

Metadata Validated

Layout Validated

Outputs Validated

Hidden State Validated

ONNX Comparison Passed

Memory Stable

Recovery Tested

---

### 56. Production Gate

Deployment prohibited until:

All validation sections PASS.

---

### 57. Final Checklist

Runtime
[ ]

Models
[ ]

Metadata
[ ]

Layout
[ ]

Vision
[ ]

Policy
[ ]

Hidden State
[ ]

ONNX Comparison
[ ]

Performance
[ ]

Recovery
[ ]

Result:

PASS / FAIL

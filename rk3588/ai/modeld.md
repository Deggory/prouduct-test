# MODELD.MD (Authoritative Version)

## Section A — Engineering Specification

### 1. Objective

* Purpose of modeld
* Scope boundaries
* Supported runtimes
* Supported forks

### 2. What modeld Actually Is

Modeld is:

Camera Input
↓
Preprocessing
↓
Tensor Generation
↓
Model Execution
↓
Output Parsing
↓
Message Publishing

Modeld is not a neural network.

### 3. Architectural Position

Camera
↓
VisionIPC
↓
modeld
↓
plannerd
↓
controlsd

### 4. System Responsibilities

camera.md owns:

* Camera
* Intrinsics
* Warp
* VisionIPC production

modeld.md owns:

* Tensor preparation
* State management
* Inference orchestration
* Metadata parsing
* Message publishing

rknn.md owns:

* RKNN backend

### 5. Repository Discovery

Discover:

* modeld.py
* helpers.py
* model runners
* metadata
* tinygrad
* RKNN integration points

Generate:

modeld_analysis.json

### 6. Camera Input Layer

VisionIPC
↓
Frame Acquisition
↓
Synchronization

### 7. Preprocessing Layer

loadyuv.cl

transform.cl

DrivingModelFrame.prepare()

### 8. Tensor Generation Layer

Image tensors

State tensors

Feature tensors

Control tensors

### 9. Tensor Ownership

img

big_img

desire

traffic_convention

lateral_control_params

prev_desired_curv

features_buffer

hidden_state

### 10. Tensor Documentation System

Generate:

tensor_report.json

Record:

* shape
* dtype
* layout
* producer
* consumer

### 11. Memory Architecture

Persistent Buffers

Buffer Reuse

Allocation Strategy

### 12. Temporal Architecture

Feature Buffers

Hidden State

Transformer Cache

History Tensors

### 13. State Lifecycle

Frame N
↓
Inference
↓
State Update
↓
Frame N+1

### 14. Model Lifecycle

Initialize
↓
Validate
↓
Infer
↓
Update State
↓
Publish

### 15. Message Publishing

modelV2

cameraOdometry

Associated messages

### 16. Planner Contract

Planner compatibility rules

Message schema ownership

Unit ownership

Field ownership

### 17. Runtime Abstraction Layer

ModelRunner

initialize()

validate()

infer()

shutdown()

### 18. TinygradRunner

Reference implementation

Fallback backend

Regression backend

### 19. RKNNRunner

Production backend

NPU backend

Validation backend

### 20. Backend Selection

tinygrad

rknn

auto

### 21. Threading Architecture

Camera Thread

Inference Thread

Publishing Thread

### 22. Queue Architecture

Input Queue

Inference Queue

Publish Queue

### 23. Memory Policy

Avoid per-frame allocation

Reuse buffers

Track ownership

### 24. Performance Architecture

Latency budgets

Timing budgets

FPS budgets

---

## Section B — Validation Specification

### 25. Discovery Validation

Verify discovery completed

### 26. Tensor Validation

Shape

Dtype

Layout

Producer

Consumer

### 27. Image Tensor Validation

img

big_img

Validation

### 28. Non-Image Tensor Validation

desire

traffic_convention

lateral_control_params

prev_desired_curv

### 29. Metadata Validation

Input Count

Output Count

Input Shapes

Output Shapes

Generate:

metadata_report.json

### 30. Vision Model Validation

Input Validation

Output Validation

Generate:

vision_validation.json

### 31. Policy Model Validation

Input Validation

Output Validation

Generate:

policy_validation.json

### 32. Hidden State Validation

Persistence

Consistency

Memory

### 33. Feature Buffer Validation

Update correctness

Reuse correctness

### 34. Timing Validation

Capture

Tensor Ready

Inference Start

Inference End

Publish

Generate:

modeld_timing.json

### 35. Latency Validation

Camera

Preprocess

Inference

Parsing

Publishing

### 36. Memory Validation

RSS

Virtual Memory

Tensor Allocations

### 37. Queue Validation

Queue Depth

Dropped Frames

Latency

### 38. Planner Validation

Planner alive

Planner compatibility

Planner correctness

### 39. Message Validation

modelV2

cameraOdometry

Schema verification

### 40. Replay Validation

Replay routes

Compare outputs

### 41. Regression Validation

Tinygrad

vs

RKNN

Comparison

### 42. Stress Testing

30 minutes

1 hour

4 hours

### 43. Recovery Testing

Backend restart

Model reload

Runtime restart

### 44. Acceptance Test Suite

Metadata Test

Tensor Test

State Test

Timing Test

Replay Test

Planner Test

Stress Test

Recovery Test

---

## Section C — AI Agent Operating Manual

### 45. Repository Analysis Workflow

Analyze:

* modeld architecture
* runtime architecture
* metadata architecture
* message architecture

Generate:

fork_modeld_report.json

### 46. Fork Adaptation Rules

Never assume:

* file paths
* metadata locations
* model names
* environment variables

Discover dynamically.

### 47. Patch Strategy

Allowed:

* modeld.py
* helpers.py
* runner abstraction
* backend selection
* tensor validation

Avoid:

* planner
* controls
* vehicle interface

unless explicitly required.

### 48. AI Agent Discovery Workflow

Repository
↓
Discovery
↓
Tensor Inventory
↓
Metadata Inventory
↓
Runner Inventory
↓
Validation

### 49. AI Agent Reporting

Generate:

modeld_analysis.json

tensor_report.json

metadata_report.json

backend_report.json

performance_report.json

fork_modeld_report.json

### 50. Failure Modes

Metadata mismatch

Tensor mismatch

Hidden state reset

Wrong layout

Wrong shape

Backend crash

Planner incompatibility

Memory leak

### 51. Error Handling Policy

Fail Fast

Generate Report

Preserve Logs

Do Not Publish Invalid Outputs

### 52. Recovery Policy

Reload Backend

Reload Model

Restart Runner

Revalidate State

### 53. Production Readiness

Required:

Metadata Validated

Tensors Validated

State Validated

Planner Compatible

Performance Measured

Recovery Tested

### 54. Production Gate

Deployment prohibited until:

All tests PASS

### 55. Final Checklist

Discovery
[ ]

Tensor Inventory
[ ]

Metadata
[ ]

Vision
[ ]

Policy
[ ]

State
[ ]

Backend
[ ]

Planner
[ ]

Performance
[ ]

Recovery
[ ]

Result:

PASS / FAIL

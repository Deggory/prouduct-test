# MODEL_METADATA.MD (Authoritative Version)

# Engineering Specification + Validation Specification + AI Agent Operating Manual

Version: 3.0

Target Runtime:

* Tinygrad
* ONNX Runtime
* RKNN
* OpenPilot Modeld

Target Models:

* Driving Vision Model
* Driving Policy Model
* Driver Monitoring Models
* Future OpenPilot Models

Target Platform:

* RK3588
* Orange Pi 5
* OpenPilot Derived Forks

---

# Section A — Engineering Specification

## 1. Objective

This document defines:

* model metadata architecture
* metadata ownership
* tensor definitions
* input definitions
* output definitions
* slice definitions
* runtime compatibility
* AI-agent integration

Goal:

Metadata-driven model execution without hardcoded tensor assumptions.

---

## 2. What Metadata Is

Metadata is the contract between:

Model
↓
Runtime
↓
Parser
↓
Planner

Metadata describes:

Inputs

Outputs

Shapes

Layouts

Slices

Semantics

Units

Meaning

---

## 3. Metadata Philosophy

The model file contains weights.

Metadata contains meaning.

Without metadata:

Model outputs become anonymous arrays.

---

## 4. Why Metadata Matters

Example:

Output tensor:

```text
[0.15, -0.22, 0.04, ...]
```

Without metadata:

Unknown.

With metadata:

```text
path
lane
road edge
lead vehicle
curvature
hidden state
```

---

## 5. OpenPilot Metadata Architecture

Model
↓
Metadata
↓
Parser
↓
modelV2
↓
Planner

Metadata is authoritative.

---

## 6. Metadata Ownership

camera.md

owns:

Camera Geometry

visionipc.md

owns:

Frame Transport

modeld.md

owns:

Tensor Generation

model_metadata.md

owns:

Tensor Meaning

rknn.md

owns:

Runtime Execution

---

## 7. Metadata Components

Metadata defines:

Inputs

Outputs

Slices

Shapes

Dtypes

Layouts

Semantic Meaning

Units

---

## 8. Input Metadata

Defines:

Input Names

Input Shapes

Input Layout

Input Dtype

Input Purpose

---

## 9. Output Metadata

Defines:

Output Names

Output Shapes

Output Layout

Output Dtype

Output Meaning

---

## 10. Slice Metadata

Defines:

Output Start

Output End

Output Ownership

Output Semantics

---

## 11. Metadata Rule

Never hardcode:

Tensor Indices

Output Positions

Slice Locations

Read metadata.

Always.

---

## 12. Metadata Evolution

Models change.

Metadata allows:

Parser compatibility

without rewriting runtime code.

---

## 13. Layout Metadata

Possible layouts:

NCHW

NHWC

Metadata defines which layout is valid.

Never assume.

---

## 14. Dtype Metadata

Examples:

float32

float16

int8

uint8

Metadata defines valid dtype.

---

## 15. Shape Metadata

Examples:

1×12×128×256

1×128×256×12

Metadata defines shape.

---

## 16. Input Ownership

Typical inputs:

Image Tensor

Big Image Tensor

Desire

Traffic Convention

Feature History

Hidden State

---

## 17. Output Ownership

Typical outputs:

Path

Lane

Road Edge

Lead Vehicle

Pose

Hidden State

Policy Outputs

---

## 18. Hidden State Metadata

Hidden state requires:

Shape

Dtype

Persistence Rules

Ownership

---

## 19. Temporal Metadata

Some outputs depend on:

Previous Frame

Previous Hidden State

Previous Features

Metadata must define temporal ownership.

---

## 20. Semantic Metadata

Each slice must define:

Meaning

Units

Expected Range

Consumer

---

## 21. Planner Interface

Planner consumes:

Parsed Metadata Outputs

Not raw tensors.

---

## 22. Metadata Discovery

AI agents must discover:

Metadata Location

Metadata Version

Metadata Format

Before modifying runtime.

---

## 23. Runtime Independence

Metadata must work with:

Tinygrad

ONNX

RKNN

Future runtimes

---

## 24. RKNN Compatibility

RKNN execution changes.

Metadata does not.

Meaning must remain identical.

---

## 25. Metadata Versioning

Every metadata file must include:

Version

Timestamp

Model Compatibility

---

## 26. Metadata Hashing

Generate:

metadata_hash.json

Track:

SHA256

Version

Timestamp

---

## 27. Production Rule

Metadata is authoritative.

Runtime must adapt to metadata.

Never the opposite.

---

# Section B — OpenPilot Metadata Architecture

## 28. Vision Model Metadata

Defines:

Image Inputs

Feature Outputs

Path Outputs

Lane Outputs

Road Edge Outputs

Pose Outputs

Hidden State Outputs

---

## 29. Policy Model Metadata

Defines:

Feature Inputs

Desire Inputs

Hidden State Inputs

Trajectory Outputs

Curvature Outputs

Policy Decisions

---

## 30. Hidden State Metadata

Defines:

State Size

State Shape

State Ownership

Persistence

---

## 31. Slice Architecture

Output Tensor
↓
Slice Definitions
↓
Semantic Outputs

---

## 32. Example Slice Definition

Example:

```text
path:
start = 0
end = 385

lane_left:
start = 386
end = 771
```

Illustrative only.

Always read metadata.

---

## 33. Consumer Architecture

Metadata Consumers:

modeld

parser

planner

UI

loggerd

---

## 34. Metadata Migration

When model updates:

Metadata must update first.

Parser updates second.

---

## 35. Replay Compatibility

Replay validation must use:

Correct metadata version.

---

## 36. Future Compatibility

Metadata should support:

New outputs

New models

New runtimes

Without parser rewrites.

---

# Section C — Validation Specification

## 37. Metadata Discovery Validation

Locate:

Metadata Files

Version

Hashes

Generate:

metadata_inventory.json

---

## 38. Input Validation

Validate:

Input Count

Input Names

Shapes

Layouts

Dtypes

Generate:

input_validation.json

---

## 39. Output Validation

Validate:

Output Count

Output Names

Shapes

Layouts

Dtypes

Generate:

output_validation.json

---

## 40. Slice Validation

Validate:

Start

End

Overlap

Ownership

Generate:

slice_validation.json

---

## 41. Shape Validation

Validate:

Runtime Shape

Metadata Shape

Match Exactly

---

## 42. Layout Validation

Validate:

NCHW

or

NHWC

Match metadata.

---

## 43. Dtype Validation

Validate:

Runtime dtype

Metadata dtype

Match exactly.

---

## 44. Hidden State Validation

Validate:

Shape

Persistence

Reuse

Ownership

Generate:

hidden_state_validation.json

---

## 45. Parser Validation

Validate:

Every metadata output

maps correctly

to parser outputs.

---

## 46. Planner Validation

Validate:

Planner consumes:

correct metadata outputs.

---

## 47. Tinygrad Validation

Reference:

Tinygrad

Metadata must match.

---

## 48. RKNN Validation

Validate:

RKNN outputs

map correctly

through metadata.

---

## 49. Cross-Runtime Validation

Tinygrad
ONNX
RKNN

Must produce:

metadata-compatible outputs.

---

## 50. Replay Validation

Replay Route
↓
Metadata Parser
↓
Planner

Must remain stable.

---

## 51. Metadata Integrity Validation

Verify:

Hash

Version

Compatibility

Generate:

metadata_integrity.json

---

## 52. Acceptance Criteria

Metadata PASS when:

Inputs PASS

Outputs PASS

Slices PASS

Shapes PASS

Layouts PASS

Hidden State PASS

Planner PASS

---

# Section D — AI Agent Operating Manual

## 53. Discovery Workflow

Discover:

Metadata Files

Versions

Hashes

Inputs

Outputs

Slices

Generate:

metadata_analysis.json

---

## 54. Runtime Port Workflow

Discover Metadata
↓
Validate Shapes
↓
Validate Layouts
↓
Validate Outputs
↓
Validate Hidden State
↓
Validate Planner
↓
Deploy

---

## 55. Fork Adaptation Rules

Never assume:

Output Indices

Slice Positions

Tensor Shapes

Layouts

Metadata Paths

Discover dynamically.

---

## 56. RKNN Porting Workflow

Metadata Discovery
↓
Vision Validation
↓
Policy Validation
↓
Parser Validation
↓
Planner Validation

---

## 57. Allowed Modifications

Metadata Readers

Validation Tools

Parser Adapters

Reporting Tools

---

## 58. Avoid Modifications

Metadata Semantics

Planner Semantics

Output Meanings

Unless metadata version changes.

---

## 59. Reporting Requirements

Generate:

metadata_inventory.json

metadata_analysis.json

input_validation.json

output_validation.json

slice_validation.json

hidden_state_validation.json

metadata_integrity.json

---

## 60. Troubleshooting

Wrong Path Output

Wrong Lane Output

Wrong Hidden State

Shape Mismatch

Layout Mismatch

Metadata Version Mismatch

Parser Failure

Planner Failure

Document root cause and fix.

---

## 61. Failure Modes

Missing Metadata

Wrong Shape

Wrong Layout

Wrong Slice

Wrong Hidden State

Wrong Parser Mapping

Planner Instability

---

## 62. Production Readiness

Required:

Metadata PASS

Parser PASS

Planner PASS

Replay PASS

Integrity PASS

Cross-Runtime PASS

---

## 63. Final Checklist

Metadata Located
[ ]

Version Verified
[ ]

Hash Verified
[ ]

Inputs Valid
[ ]

Outputs Valid
[ ]

Slices Valid
[ ]

Hidden State Valid
[ ]

Parser Valid
[ ]

Planner Valid
[ ]

Replay Valid
[ ]

Result:

PASS / FAIL

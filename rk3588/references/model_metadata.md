# MODEL_METADATA.MD

# OpenPilot Model Metadata Reference

Version: 1.0

Purpose:

Define how model metadata should be discovered, validated, interpreted, and preserved when integrating:

* RKNN
* Tinygrad
* ONNX
* Future runtimes

Target Platforms:

* RK3588
* RK3588S
* Orange Pi 5
* Orange Pi 5 Plus

Target Software:

* openpilot
* sunnypilot
* frogpilot
* OPKR
* KisaPilot

---

# 1. What Metadata Is

Metadata is the contract between:

Model

and

Modeld

Metadata defines:

* Inputs
* Outputs
* Shapes
* Tensor layouts
* Output slices
* Hidden states
* Feature buffers

The model is not authoritative.

Metadata is authoritative.

---

# 2. Critical Rule

Never hardcode:

```python
outputs[0]
outputs[1]
outputs[2]
```

Never assume output ordering.

Always validate against metadata.

Many fork failures originate from output assumptions.

---

# 3. Metadata Responsibilities

Metadata owns:

Input Definitions

Output Definitions

Output Names

Output Shapes

Output Interpretation

Hidden State Definitions

Feature Buffer Definitions

---

# 4. Runtime Responsibilities

Runtime owns:

Loading Model

Executing Model

Returning Tensors

Runtime does NOT own:

Tensor meaning

Output interpretation

Path extraction

Lane extraction

Those belong to metadata.

---

# 5. Common Metadata Files

Examples:

driving_vision_metadata.pkl

driving_policy_metadata.pkl

Some forks may use:

json

yaml

protobuf

pickle

The format is less important than the information.

---

# 6. Metadata Discovery

Before integration:

Locate:

Metadata Files

Record:

Path

Size

Hash

Version

Generate:

metadata_inventory.json

---

# 7. Input Definitions

Every input should define:

Name

Shape

Dtype

Layout

Purpose

Example:

img

big_img

desire

traffic_convention

---

# 8. Output Definitions

Every output should define:

Name

Shape

Dtype

Purpose

Consumer

Generate:

output_inventory.json

---

# 9. Input Ownership

Examples:

img

Owned by:

Camera Pipeline

↓

modeld

big_img

Owned by:

Camera Pipeline

↓

modeld

---

# 10. Non-Image Inputs

Examples:

desire

traffic_convention

lateral_control_params

prev_desired_curv

These must be documented.

Never assume shape.

---

# 11. Hidden State Ownership

Examples:

hidden_state

features_buffer

transformer cache

history tensors

Metadata must define them.

---

# 12. Hidden State Rules

Never:

Discard

Reset

Reinitialize

per frame.

Hidden state must persist.

---

# 13. Feature Buffer Rules

Typical flow:

Frame N

↓

Inference

↓

Feature Buffer Update

↓

Frame N+1

↓

Reuse

Metadata should document:

Shape

Purpose

Persistence

---

# 14. Shape Validation

Record:

Rank

Dimensions

Layout

Dtype

Examples:

1x12x128x256

1x128x256x12

1x512

1x8

Never assume.

---

# 15. Layout Validation

Possible:

NCHW

NHWC

Metadata should specify expected layout.

Do not infer from model name.

---

# 16. Dtype Validation

Examples:

float32

float16

int8

uint8

Validate against runtime.

---

# 17. Output Ownership

Output ownership belongs to metadata.

Not:

RKNN

Tinygrad

ONNX

Backends produce tensors only.

Metadata gives meaning.

---

# 18. Output Slices

Many outputs are packed tensors.

Example:

Single Output Tensor

↓

Path

Lane Lines

Road Edges

Lead Vehicles

Metadata defines slice boundaries.

---

# 19. Slice Validation

Record:

Start Index

End Index

Shape

Meaning

Generate:

slice_inventory.json

---

# 20. Path Output

Typical metadata fields:

Path

Trajectory

Future Position

Curvature

Validate location using metadata.

---

# 21. Lane Output

Metadata may define:

Left Lane

Right Lane

Lane Confidence

Lane Probability

Never assume ordering.

---

# 22. Road Edge Output

Metadata may define:

Left Edge

Right Edge

Confidence

Validate slices.

---

# 23. Lead Vehicle Output

Metadata may define:

Distance

Velocity

Acceleration

Probability

Interpret using metadata only.

---

# 24. Desire Output

Metadata may define:

Lane Change

Keep Lane

Turn

Merge

Validate mapping.

---

# 25. Policy Output

Policy metadata may define:

Trajectory

Curvature

Desired Path

Control Features

Always validate.

---

# 26. Metadata Extraction Tool

Recommended:

tools/rk3588/extract_metadata.py

Responsibilities:

Read metadata

Print shapes

Print slices

Generate reports

---

# 27. Metadata Report

Generate:

metadata_report.json

Include:

Inputs

Outputs

Slices

Layouts

Dtypes

Version

---

# 28. RKNN Validation

Before deployment:

Compare:

RKNN Inputs

Metadata Inputs

RKNN Outputs

Metadata Outputs

All must match.

---

# 29. Tinygrad Validation

Compare:

Tinygrad Runtime

Metadata

Ensure:

Shape consistency

Output consistency

---

# 30. ONNX Validation

Compare:

ONNX

Metadata

Validate:

Input count

Output count

Shapes

---

# 31. Runtime-Agnostic Design

Metadata must remain valid regardless of runtime.

Supported runtimes:

Tinygrad

RKNN

ONNX

Future runtimes

should all use the same metadata.

---

# 32. Fork Compatibility

Different forks may:

Rename outputs

Add outputs

Remove outputs

Change metadata locations

Always rediscover metadata.

Never hardcode paths.

---

# 33. Metadata Versioning

Record:

Version

Commit

Hash

Date

Store alongside deployment reports.

---

# 34. Metadata Regression Testing

Repeat validation after:

Model changes

Runtime changes

Metadata changes

Fork updates

---

# 35. Metadata Failure Modes

Common failures:

Wrong Shape

Wrong Layout

Missing Output

Wrong Slice

Corrupt Metadata

Version Mismatch

All must be detected.

---

# 36. AI Agent Rules

When modifying a repository:

1. Discover metadata
2. Inventory inputs
3. Inventory outputs
4. Inventory slices
5. Validate runtime compatibility
6. Generate report
7. Only then modify modeld

Never skip metadata validation.

---

# 37. Pass Criteria

Metadata passes if:

Inputs Validated

Outputs Validated

Slices Validated

Layouts Validated

Dtypes Validated

Version Recorded

---

# 38. Fail Criteria

Any of:

Unknown Output

Unknown Input

Missing Slice

Shape Mismatch

Layout Mismatch

Metadata Corruption

results in FAIL.

---

# 39. Production Checklist

Metadata Located

[ ] PASS

Inputs Documented

[ ] PASS

Outputs Documented

[ ] PASS

Slices Documented

[ ] PASS

Layouts Validated

[ ] PASS

Dtypes Validated

[ ] PASS

---

# 40. Final Reference

Correct Architecture:

Camera

↓

VisionIPC

↓

Preprocessing

↓

Model Input

↓

Runtime (Tinygrad / RKNN)

↓

Raw Output Tensors

↓

Metadata Parser

↓

Path

Lane

Road Edge

Lead

Policy Outputs

↓

Planner

Metadata is the bridge between raw tensors and planner behavior.

Treat it as a first-class component.

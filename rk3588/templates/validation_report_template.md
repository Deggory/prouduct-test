# VALIDATION_REPORT_TEMPLATE.MD (Authoritative Version)

# Engineering Specification + Validation Reporting Specification + Production Acceptance Specification + AI Agent Operating Manual

Version: 3.0

Target Platforms:

* OpenPilot
* Sunnypilot
* FrogPilot
* OPKR
* KisaPilot

Target Hardware:

* RK3588
* RK3588S
* Orange Pi 5
* Orange Pi 5 Plus

Target Runtime:

* Tinygrad
* ONNX Runtime
* RKNN

Target Camera:

* IMX415
* RKISP
* DMA-BUF
* VisionIPC

---

# Section A — Validation Report Engineering Specification

## 1. Objective

This template defines:

* validation report structure
* validation metrics
* acceptance criteria
* failure reporting
* AI-agent reporting requirements

Goal:

Produce repeatable validation reports across all OpenPilot-derived repositories.

---

## 2. Validation Philosophy

Validation is proof.

Not:

UI screenshots

Not:

Subjective judgement

Validation requires:

Measured Evidence
↓
Documented Results
↓
Acceptance Criteria
↓
PASS / FAIL

---

## 3. Validation Ownership

camera.md

owns camera validation

visionipc.md

owns transport validation

modeld.md

owns preprocessing validation

model_metadata.md

owns metadata validation

rknn.md

owns runtime validation

validation.md

owns validation methodology

validation_report_template.md

owns reporting format

---

## 4. Report Metadata

Repository:

Fork:

Branch:

Commit:

Date:

Operator:

Hardware:

Runtime:

Camera:

Models:

Metadata Version:

---

## 5. Validation Scope

Select:

[ ]

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

Modeld

[ ]

Metadata

[ ]

Vision Model

[ ]

Policy Model

[ ]

Planner

[ ]

Replay

[ ]

Performance

[ ]

Deployment

---

# Section B — Discovery Results

## 6. Repository Discovery

Generate:

architecture_inventory.json

Status:

PASS / FAIL

Notes:

---

## 7. Camera Discovery

Generate:

camera_inventory.json

Status:

PASS / FAIL

Notes:

---

## 8. Runtime Discovery

Generate:

runtime_inventory.json

Status:

PASS / FAIL

Notes:

---

## 9. Metadata Discovery

Generate:

metadata_inventory.json

Status:

PASS / FAIL

Notes:

---

## 10. Planner Discovery

Generate:

planner_inventory.json

Status:

PASS / FAIL

Notes:

---

# Section C — Camera Validation Report

## 11. Sensor Validation

Sensor:

Resolution:

FPS:

Status:

PASS / FAIL

---

## 12. RKISP Validation

Frames Generated:

Errors:

Status:

PASS / FAIL

---

## 13. V4L2 Validation

Format:

Buffer Type:

Status:

PASS / FAIL

---

## 14. NV12 Validation

Width:

Height:

Stride:

Buffer Size:

Status:

PASS / FAIL

---

## 15. DMA-BUF Validation

FD Import:

Lifetime:

Corruption:

Status:

PASS / FAIL

---

## 16. Intrinsics Validation

Focal Length:

Principal Point:

Resolution:

Status:

PASS / FAIL

---

## 17. Warp Validation

Transform Matrix:

Overlay Alignment:

Status:

PASS / FAIL

---

## 18. Camera Acceptance

Result:

PASS / FAIL

---

# Section D — VisionIPC Validation Report

## 19. Stream Validation

Road Camera:

Wide Camera:

Driver Camera:

Status:

PASS / FAIL

---

## 20. Timestamp Validation

Monotonic:

Latency:

Status:

PASS / FAIL

---

## 21. Frame Ordering Validation

Drops:

Duplicates:

Status:

PASS / FAIL

---

## 22. Replay Validation

Route:

Frames:

Result:

PASS / FAIL

---

## 23. VisionIPC Acceptance

Result:

PASS / FAIL

---

# Section E — Modeld Validation Report

## 24. Tensor Validation

Input Shape:

Layout:

Dtype:

Status:

PASS / FAIL

---

## 25. Tensor Statistics

Min:

Max:

Mean:

Std:

Status:

PASS / FAIL

---

## 26. Tensor Reconstruction

Crop:

Warp:

Alignment:

Status:

PASS / FAIL

---

## 27. Metadata Validation

Inputs:

Outputs:

Slices:

Status:

PASS / FAIL

---

## 28. Hidden State Validation

Shape:

Persistence:

Status:

PASS / FAIL

---

## 29. Modeld Acceptance

Result:

PASS / FAIL

---

# Section F — RKNN Validation Report

## 30. Vision Validation

Reference Runtime:

Candidate Runtime:

Correlation:

Cosine Similarity:

Relative MAE:

Status:

PASS / FAIL

---

## 31. Policy Validation

Reference Runtime:

Candidate Runtime:

Correlation:

Cosine Similarity:

Relative MAE:

Status:

PASS / FAIL

---

## 32. Core Assignment Validation

Vision Core:

Policy Core:

Status:

PASS / FAIL

---

## 33. Runtime Stability

Crashes:

Inference Errors:

Status:

PASS / FAIL

---

## 34. RKNN Acceptance

Result:

PASS / FAIL

---

# Section G — Planner Validation Report

## 35. modelV2 Validation

Schema:

Frequency:

Units:

Status:

PASS / FAIL

---

## 36. Planner Health

Alive:

Stable:

Responsive:

Status:

PASS / FAIL

---

## 37. Overlay Validation

Path:

Lane:

Road Edge:

Lead Vehicle:

Status:

PASS / FAIL

---

## 38. Planner Acceptance

Result:

PASS / FAIL

---

# Section H — System Validation Report

## 39. Latency Validation

Camera:

VisionIPC:

OpenCL:

Vision:

Policy:

Planner:

UI:

Total:

Status:

PASS / FAIL

---

## 40. FPS Validation

Average:

Minimum:

Maximum:

95%:

99%:

Status:

PASS / FAIL

---

## 41. Memory Validation

RSS:

Peak RSS:

Leaks:

Status:

PASS / FAIL

---

## 42. Thermal Validation

CPU:

GPU:

NPU:

Status:

PASS / FAIL

---

## 43. Stress Validation

Duration:

Crashes:

Drops:

Status:

PASS / FAIL

---

## 44. Recovery Validation

Camera Restart:

Runtime Restart:

Replay Restart:

Status:

PASS / FAIL

---

## 45. System Acceptance

Result:

PASS / FAIL

---

# Section I — Failure Analysis

## 46. Failure Summary

Failures:

Root Cause:

Impact:

Severity:

Low / Medium / High / Critical

---

## 47. Recommended Fixes

Fix 1:

Fix 2:

Fix 3:

---

## 48. Revalidation Requirements

Required Tests:

Expected Outcome:

---

# Section J — AI Agent Operating Manual

## 49. Report Generation Workflow

Discovery
↓
Camera Validation
↓
VisionIPC Validation
↓
Modeld Validation
↓
Metadata Validation
↓
RKNN Validation
↓
Planner Validation
↓
System Validation
↓
Report Generation

---

## 50. Reporting Rules

Never report:

PASS

without evidence.

Every section requires:

Metrics

Logs

Artifacts

Validation outputs.

---

## 51. Artifact Requirements

Attach:

camera_inventory.json

visionipc_inventory.json

metadata_inventory.json

tensor_validation.json

vision_validation.json

policy_validation.json

latency_report.json

thermal_report.json

---

## 52. Production Gate

Validation report cannot PASS unless:

Camera PASS

VisionIPC PASS

Modeld PASS

Metadata PASS

Vision PASS

Policy PASS

Planner PASS

System PASS

---

## 53. Final Validation Status

Repository:

Branch:

Commit:

Validation Result:

PASS / FAIL

Production Ready:

YES / NO

Reviewer:

Date:

Notes:

---

## 54. Final Acceptance Checklist

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

Modeld
[ ]

Vision RKNN
[ ]

Policy RKNN
[ ]

Planner
[ ]

Replay
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

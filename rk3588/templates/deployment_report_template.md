# DEPLOYMENT_REPORT_TEMPLATE.MD (Authoritative Version)

# Engineering Specification + Deployment Reporting Specification + Release Certification Specification + Production Acceptance Specification + AI Agent Operating Manual

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
* EGLImage

Deployment Target:

Production Release

---

# Section A — Deployment Report Engineering Specification

## 1. Objective

This document defines:

* deployment reporting
* release certification
* production readiness evaluation
* rollback certification
* operational acceptance

Goal:

Provide a standardized deployment certification report for all RK3588 OpenPilot-derived ports.

---

## 2. Deployment Philosophy

Deployment is not:

Successful Compilation

Deployment is:

Validated System
↓
Verified Performance
↓
Stable Runtime
↓
Safe Production Release

---

## 3. Deployment Ownership

camera.md

owns camera readiness

visionipc.md

owns transport readiness

modeld.md

owns perception readiness

rknn.md

owns runtime readiness

validation.md

owns correctness readiness

performance.md

owns benchmark readiness

deployment.md

owns deployment methodology

deployment_report_template.md

owns deployment certification

---

## 4. Release Metadata

Repository:

Fork:

Branch:

Commit:

Release Version:

Release Candidate:

Date:

Operator:

Reviewer:

Deployment Environment:

---

## 5. Hardware Metadata

Board:

CPU:

GPU:

NPU:

RAM:

Storage:

Camera:

Kernel:

OS:

---

## 6. Runtime Metadata

Runtime:

Vision Runtime:

Policy Runtime:

Vision Core:

Policy Core:

DMA-BUF:

EGLImage:

RGA:

---

# Section B — Repository Certification

## 7. Repository Verification

Repository Exists:

YES / NO

Branch Correct:

YES / NO

Commit Recorded:

YES / NO

Working Tree Clean:

YES / NO

Status:

PASS / FAIL

---

## 8. Artifact Inventory

Generate:

artifact_inventory.json

Contents:

Models

Metadata

Configs

Reports

Checksums

---

## 9. Artifact Integrity

Verify:

SHA256

Version

Timestamp

Status:

PASS / FAIL

---

## 10. Release Package Verification

Release Bundle Exists:

YES / NO

Rollback Package Exists:

YES / NO

Documentation Complete:

YES / NO

Status:

PASS / FAIL

---

# Section C — Camera Deployment Certification

## 11. Sensor Certification

Sensor:

Resolution:

FPS:

Status:

PASS / FAIL

---

## 12. RKISP Certification

Frames Generated:

Errors:

Status:

PASS / FAIL

---

## 13. V4L2 Certification

Format:

Buffers:

Status:

PASS / FAIL

---

## 14. NV12 Certification

Width:

Height:

Stride:

Status:

PASS / FAIL

---

## 15. DMA-BUF Certification

Enabled:

YES / NO

Validation Result:

PASS / FAIL

---

## 16. Camera Readiness

Camera Production Ready:

YES / NO

Status:

PASS / FAIL

---

# Section D — VisionIPC Deployment Certification

## 17. Stream Certification

Road Camera:

Wide Camera:

Driver Camera:

Status:

PASS / FAIL

---

## 18. Timestamp Certification

Monotonic:

Latency:

Status:

PASS / FAIL

---

## 19. Replay Certification

Route Tested:

Replay Stable:

Status:

PASS / FAIL

---

## 20. VisionIPC Readiness

Production Ready:

YES / NO

Status:

PASS / FAIL

---

# Section E — Model Runtime Certification

## 21. Metadata Certification

Version:

Hash:

Validation Result:

PASS / FAIL

---

## 22. Vision Model Certification

Runtime:

Correlation:

Latency:

Status:

PASS / FAIL

---

## 23. Policy Model Certification

Runtime:

Correlation:

Latency:

Status:

PASS / FAIL

---

## 24. Hidden State Certification

Persistence:

Validation:

Status:

PASS / FAIL

---

## 25. Model Runtime Readiness

Production Ready:

YES / NO

Status:

PASS / FAIL

---

# Section F — Planner Certification

## 26. modelV2 Certification

Schema:

Frequency:

Units:

Status:

PASS / FAIL

---

## 27. Planner Health Certification

Alive:

Stable:

Responsive:

Status:

PASS / FAIL

---

## 28. Overlay Certification

Path:

Lane:

Road Edge:

Lead Vehicle:

Status:

PASS / FAIL

---

## 29. Planner Readiness

Production Ready:

YES / NO

Status:

PASS / FAIL

---

# Section G — Performance Certification

## 30. Camera → modelV2

Average:

95%:

Maximum:

Target:

15–27 ms

Status:

PASS / FAIL

---

## 31. Camera → UI

Average:

95%:

Maximum:

Target:

20–35 ms

Status:

PASS / FAIL

---

## 32. FPS Certification

Average:

Minimum:

95%:

Status:

PASS / FAIL

---

## 33. CPU Certification

Average:

Peak:

Migration:

Status:

PASS / FAIL

---

## 34. GPU Certification

Average:

Peak:

Status:

PASS / FAIL

---

## 35. NPU Certification

Core 0:

Core 1:

Core 2:

Status:

PASS / FAIL

---

## 36. Memory Certification

Average:

Peak:

Leaks:

Status:

PASS / FAIL

---

## 37. Thermal Certification

CPU:

GPU:

NPU:

Throttling:

Status:

PASS / FAIL

---

## 38. Performance Readiness

Production Ready:

YES / NO

Status:

PASS / FAIL

---

# Section H — Stress Certification

## 39. Test Duration

Duration:

Environment:

---

## 40. Runtime Stability

Crashes:

Inference Failures:

Restarts:

Status:

PASS / FAIL

---

## 41. Camera Stability

Frame Drops:

ISP Errors:

DMA-BUF Errors:

Status:

PASS / FAIL

---

## 42. Memory Stability

Leaks:

Growth:

Status:

PASS / FAIL

---

## 43. Latency Stability

Average:

95%:

Drift:

Status:

PASS / FAIL

---

## 44. Stress Readiness

Production Ready:

YES / NO

Status:

PASS / FAIL

---

# Section I — Recovery Certification

## 45. Camera Restart

Recovery Time:

Status:

PASS / FAIL

---

## 46. Runtime Restart

Recovery Time:

Status:

PASS / FAIL

---

## 47. Replay Restart

Recovery Time:

Status:

PASS / FAIL

---

## 48. Model Reload

Recovery Time:

Status:

PASS / FAIL

---

## 49. Recovery Readiness

Production Ready:

YES / NO

Status:

PASS / FAIL

---

# Section J — Rollback Certification

## 50. Rollback Package

Exists:

YES / NO

Status:

PASS / FAIL

---

## 51. Rollback Procedure

Documented:

YES / NO

Verified:

YES / NO

Status:

PASS / FAIL

---

## 52. Known Good Configuration

Stored:

YES / NO

Versioned:

YES / NO

Status:

PASS / FAIL

---

## 53. Rollback Readiness

Production Ready:

YES / NO

Status:

PASS / FAIL

---

# Section K — Deployment Acceptance

## 54. Validation Summary

Validation Report:

PASS / FAIL

---

## 55. Performance Summary

Performance Report:

PASS / FAIL

---

## 56. Stress Summary

Stress Report:

PASS / FAIL

---

## 57. Recovery Summary

Recovery Report:

PASS / FAIL

---

## 58. Rollback Summary

Rollback Report:

PASS / FAIL

---

## 59. Overall Readiness

Camera Ready:

YES / NO

Runtime Ready:

YES / NO

Planner Ready:

YES / NO

Performance Ready:

YES / NO

Recovery Ready:

YES / NO

Rollback Ready:

YES / NO

---

## 60. Deployment Recommendation

NOT READY

READY FOR TESTING

READY FOR RC

READY FOR PRODUCTION

Select one.

---

# Section L — AI Agent Operating Manual

## 61. Deployment Workflow

Discovery
↓
Validation
↓
Performance
↓
Stress
↓
Recovery
↓
Rollback
↓
Certification
↓
Production

---

## 62. Reporting Rules

Never certify:

Production Ready

without:

Validation PASS

Performance PASS

Stress PASS

Recovery PASS

Rollback PASS

---

## 63. Required Artifacts

Attach:

validation_report.json

performance_report.json

deployment_inventory.json

latency_report.json

thermal_report.json

rollback_report.json

artifact_inventory.json

---

## 64. Production Gate

Deployment prohibited unless:

Camera PASS

VisionIPC PASS

Metadata PASS

Vision PASS

Policy PASS

Planner PASS

Performance PASS

Stress PASS

Recovery PASS

Rollback PASS

---

## 65. Release Classification

Development

Testing

Release Candidate

Production

Mark one.

---

## 66. Final Deployment Status

Repository:

Branch:

Commit:

Release Version:

Deployment Result:

PASS / FAIL

Production Certified:

YES / NO

Reviewer:

Date:

Notes:

---

## 67. Final Acceptance Checklist

Repository
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

Metadata
[ ]

Vision RKNN
[ ]

Policy RKNN
[ ]

Planner
[ ]

Performance
[ ]

Stress
[ ]

Recovery
[ ]

Rollback
[ ]

Documentation
[ ]

Release Package
[ ]

Result:

PASS / FAIL

---

## 68. Production Certification Record

Certification ID:

Repository:

Release:

Commit:

Hardware:

Runtime:

Certification Result:

PASS / FAIL

Production Approved:

YES / NO

Approval Date:

Reviewer:

Signature:

Only PASS certifications may be considered production-ready releases.

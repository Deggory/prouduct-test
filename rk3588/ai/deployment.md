# DEPLOYMENT.MD (Authoritative Version)

# Engineering Specification + Deployment Verification Specification + AI Agent Operating Manual

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

Target Runtime:

* RKNN Vision Core 0
* RKNN Policy Core 1
* DMA-BUF
* EGLImage
* Mali-G610 GPU

Target Forks:

* openpilot
* sunnypilot
* frogpilot
* OPKR
* KisaPilot

---

# Section A — Engineering Specification

## 1. Objective

Deployment exists to move a validated RK3588 AI stack into production.

Required order:

camera.md
↓
visionipc.md
↓
modeld.md
↓
rknn.md
↓
validation.md
↓
performance.md
↓
deployment.md

Deployment is the final gate.

---

## 2. Deployment Philosophy

Deployment is not:

Successful Build

Deployment is:

Validated System
↓
Stable Runtime
↓
Stable Planner
↓
Safe Vehicle Behavior

---

## 3. Production Architecture

Target architecture:

IMX415
↓
RKISP
↓
V4L2
↓
NV12 DMA-BUF
├──────────────┬─────────────────┐
│              │                 │
▼              ▼                 ▼
VisionIPC    EGLImage         loggerd
↓              ↓
OpenCL       Mali GPU
↓              ↓
RKNN Vision  UI Preview
↓              ↓
RKNN Policy  Overlay
↓
modelV2/msgq
↓
planner
↓
controls

---

## 4. Deployment Ownership

camera.md

owns:

Camera Readiness

visionipc.md

owns:

Transport Readiness

modeld.md

owns:

Model Pipeline Readiness

rknn.md

owns:

NPU Runtime Readiness

validation.md

owns:

Correctness Verification

performance.md

owns:

Performance Verification

deployment.md

owns:

Release Process

---

## 5. Deployment Modes

Mode 1

Baseline

RKISP
↓
VisionIPC
↓
OpenCL
↓
RKNN

Mode 2

DMA-BUF

RKISP
↓
DMA-BUF
↓
VisionIPC
↓
RKNN

Mode 3

DMA-BUF + EGLImage

RKISP
↓
DMA-BUF
├→ VisionIPC → RKNN
└→ EGLImage → Mali GPU → UI

Production recommendation:

Mode 3

---

## 6. Release Philosophy

Validation
↓
Performance
↓
Road Testing
↓
Release Candidate
↓
Production

Never skip stages.

---

## 7. Repository Tracking

Record:

Repository

Fork

Branch

Commit

Date

Operator

Generate:

deployment_metadata.json

---

## 8. Branch Strategy

Recommended:

main
↓
rk3588-validation
↓
rk3588-production

Never deploy from development branches.

---

## 9. Artifact Architecture

Required:

Vision Model

Policy Model

Metadata

Warp Files

Configuration Files

Validation Reports

Performance Reports

Deployment Reports

---

## 10. Artifact Inventory

Generate:

artifact_inventory.json

Record:

Path

Size

Hash

Version

Timestamp

---

## 11. Checksum Policy

Generate SHA256 for:

Models

Metadata

Configs

Reports

Store permanently.

---

## 12. Version Tracking

Track:

Repository Commit

Model Version

Metadata Version

Runtime Version

Kernel Version

Deployment Version

---

## 13. Configuration Ownership

Document:

Runtime Selection

Camera Settings

DMA-BUF Settings

EGL Settings

Model Paths

Metadata Paths

---

## 14. Runtime Architecture

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

## 15. CPU Architecture

Preferred:

A76 cores

CPU4–CPU7

Avoid A55 execution.

---

## 16. Scheduler Policy

Optional:

SCHED_FIFO

Priority:

50–60

Only after validation.

---

## 17. Logging Policy

Deployment must record:

Errors

Warnings

Inference Times

Planner State

Camera State

NPU State

---

## 18. Monitoring Philosophy

Every deployment must be observable.

Unmonitored deployments are unsupported.

---

## 19. Health Monitoring

Track:

CPU

GPU

NPU

Memory

Temperature

Planner

Generate:

health_report.json

---

## 20. Deployment Artifacts

Store:

Validation Reports

Performance Reports

Deployment Reports

Logs

Checksums

Rollback Package

---

# Section B — Deployment Verification Specification

## 21. Pre-Deployment Gate

Required:

Camera PASS

VisionIPC PASS

Modeld PASS

RKNN PASS

Validation PASS

Performance PASS

---

## 22. Repository Verification

Verify:

Repository Exists

Branch Correct

Commit Recorded

Working Tree Clean

---

## 23. Artifact Verification

Verify:

Exists

Readable

Correct Hash

Correct Version

Generate:

artifact_verification.json

---

## 24. Camera Verification

Verify:

IMX415 Detected

Resolution Correct

FPS Correct

NV12 Correct

DMA-BUF Working

Generate:

camera_verification.json

---

## 25. VisionIPC Verification

Verify:

Streams Exist

Timestamps Valid

Consumers Alive

Generate:

visionipc_verification.json

---

## 26. DMA-BUF Verification

Verify:

FD Valid

Import Success

No Corruption

Generate:

dmabuf_verification.json

---

## 27. EGL Verification

Verify:

EGLImage Import

Texture Creation

Camera Preview

Generate:

egl_verification.json

---

## 28. OpenCL Verification

Verify:

loadyuv.cl

transform.cl

Execution Success

Generate:

opencl_verification.json

---

## 29. RKNN Verification

Verify:

Runtime Available

Vision Model Loads

Policy Model Loads

Core Assignment Correct

Generate:

rknn_verification.json

---

## 30. Metadata Verification

Verify:

Metadata Exists

Matches Model

Version Recorded

Generate:

metadata_verification.json

---

## 31. Startup Verification

Verify:

Camera Starts

VisionIPC Starts

Modeld Starts

Planner Starts

UI Starts

All remain alive.

---

## 32. Runtime Verification

Validate:

Inference Success

No Crashes

Stable Outputs

---

## 33. Validation Report Verification

Required:

Camera Validation

VisionIPC Validation

Model Validation

Planner Validation

System Validation

---

## 34. Performance Report Verification

Required:

Latency PASS

FPS PASS

Memory PASS

Thermals PASS

Recovery PASS

---

## 35. Production Performance Targets

Mode 3 Target:

Camera → modelV2

15–27 ms

Camera → UI

20–35 ms

---

## 36. Memory Verification

Verify:

No Leaks

Stable Allocation Count

Stable Buffer Usage

---

## 37. Thermal Verification

Verify:

CPU < 80°C

NPU < 85°C

GPU Stable

No Throttling

---

## 38. Recovery Verification

Verify:

Camera Restart

Runtime Restart

Model Reload

Recovery Success

---

## 39. Stress Verification

Minimum:

1 Hour

Preferred:

4 Hours

No Crashes

No Leaks

No Performance Collapse

---

## 40. Acceptance Criteria

All verification sections PASS.

---

# Section C — Road Test Specification

## 41. Road Test Philosophy

Bench success is insufficient.

Road validation is mandatory.

---

## 42. Phase 1

Low-Speed Testing

Validate:

Overlay

Planner

Inference

Camera Stability

---

## 43. Phase 2

Mixed Traffic

Validate:

Curves

Intersections

Traffic

Planner Stability

---

## 44. Phase 3

Extended Operation

1–4 Hours

Monitor:

Latency

Memory

Temperature

Planner

---

## 45. Overlay Validation

Validate:

Path

Lane

Road Edge

Lead Vehicle

Overlay must remain stable.

---

## 46. Planner Validation

Validate:

Planner Alive

Planner Stable

No Timing Drift

No Unexpected Behavior

---

## 47. UI Validation

Validate:

Camera Preview

Overlay Rendering

DMA-BUF Path

EGLImage Path

---

## 48. Runtime Recovery Validation

Validate:

Camera Restart

Runtime Restart

Replay Restart

Model Reload

Recovery Success

---

# Section D — Release Engineering

## 49. Release Candidate Process

RC1
↓
Validation
↓
RC2
↓
Validation
↓
Production

---

## 50. Regression Policy

Repeat validation after:

Model Updates

Runtime Updates

Camera Updates

Repository Updates

---

## 51. Long-Term Maintenance

Store:

Validation Reports

Performance Reports

Deployment Reports

For every release.

---

## 52. Security Policy

Verify:

Model Integrity

Metadata Integrity

Artifact Integrity

Prevent corrupted deployments.

---

## 53. Rollback Philosophy

Rollback must be immediate.

Never deploy without rollback.

---

## 54. Rollback Assets

Known Good Branch

Known Good Models

Known Good Metadata

Known Good Runtime

Known Good Configurations

---

## 55. Rollback Triggers

Planner Instability

Runtime Crashes

Thermal Instability

Memory Leak

Unexpected Outputs

Immediate rollback required.

---

## 56. Release Package Structure

release_bundle/

models/

metadata/

configs/

reports/

logs/

checksums/

rollback/

---

# Section E — AI Agent Operating Manual

## 57. Repository Discovery Workflow

Discover:

Camera

VisionIPC

DMA-BUF

EGL

OpenCL

Modeld

RKNN

Planner

UI

Generate:

deployment_inventory.json

---

## 58. Fork Adaptation Rules

Never assume:

Paths

Runtime Layout

Metadata Location

Environment Variables

Discover dynamically.

---

## 59. Deployment Workflow

Discovery
↓
Verification
↓
Validation
↓
Performance
↓
Road Testing
↓
Release Candidate
↓
Production

---

## 60. AI Agent Responsibilities

Analyze Repository

Generate Validation Plan

Generate Performance Plan

Generate Rollback Plan

Generate Deployment Plan

Generate Reports

---

## 61. Reporting Requirements

Generate:

deployment_metadata.json

artifact_inventory.json

camera_verification.json

visionipc_verification.json

rknn_verification.json

deployment_report.json

deployment_inventory.json

---

## 62. Troubleshooting

Model Load Failure

DMA-BUF Failure

EGL Import Failure

Thermal Throttling

Planner Failure

Overlay Failure

Memory Leak

Deployment Rollback

Document root cause and resolution.

---

## 63. Failure Modes

Runtime Failure

Planner Failure

Thermal Failure

Memory Leak

DMA-BUF Failure

GPU Import Failure

Artifact Corruption

Rollback Failure

---

## 64. Production Readiness

Required:

Camera PASS

VisionIPC PASS

DMA-BUF PASS

EGL PASS

Modeld PASS

RKNN PASS

Validation PASS

Performance PASS

Road Testing PASS

---

## 65. Production Gate

Deployment prohibited until:

All acceptance criteria PASS.

No exceptions.

---

## 66. Final Checklist

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

Modeld
[ ]

RKNN
[ ]

Validation
[ ]

Performance
[ ]

Road Testing
[ ]

Rollback Package
[ ]

Documentation
[ ]

Result:

PASS / FAIL

---

## 67. Final Deployment Record

Status:

PASS / FAIL

Repository:

Branch:

Commit:

Hardware:

Runtime:

Date:

Operator:

Notes:

Only PASS deployments may be considered production-ready.

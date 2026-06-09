# PRODUCTION_CHECKLIST.MD (Authoritative Version)

# Engineering Checklist + Production Certification Checklist + Release Readiness Checklist + Deployment Approval Checklist + AI Agent Operating Checklist

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

* RKNN
* Tinygrad
* ONNX Runtime

Target Camera:

* IMX415
* RKISP
* DMA-BUF
* VisionIPC
* EGLImage

Production Goal:

Certified Production Deployment

---

# Section A — Production Certification Philosophy

## Certification Rule

Production deployment requires:

Architecture PASS
↓
Validation PASS
↓
Performance PASS
↓
Stress PASS
↓
Recovery PASS
↓
Deployment PASS

Failure at any stage blocks deployment.

---

## Certification Principle

Production Ready means:

Correct

Stable

Measurable

Recoverable

Documented

Repeatable

---

## Forbidden Assumptions

Never certify production because:

Build succeeds

UI renders

Camera displays

Model runs

Certification requires full validation.

---

# Section B — Repository Certification

## Repository Verification

Repository Located

[ ]

Repository Inventory Generated

[ ]

Architecture Inventory Generated

[ ]

Runtime Inventory Generated

[ ]

Metadata Inventory Generated

[ ]

---

## Source Integrity

Git Repository Clean

[ ]

Branch Recorded

[ ]

Commit Recorded

[ ]

Version Recorded

[ ]

---

## Release Integrity

Release Tag Created

[ ]

Release Notes Created

[ ]

Artifacts Versioned

[ ]

---

## Repository Certification

PASS

[ ]

---

# Section C — Hardware Certification

## RK3588 Verification

CPU Available

[ ]

GPU Available

[ ]

NPU Available

[ ]

ISP Available

[ ]

RGA Available

[ ]

DMA-BUF Available

[ ]

---

## Camera Hardware

IMX415 Connected

[ ]

Sensor Detected

[ ]

No Hardware Errors

[ ]

---

## Storage

Storage Healthy

[ ]

Sufficient Free Space

[ ]

No Filesystem Errors

[ ]

---

## Hardware Certification

PASS

[ ]

---

# Section D — Camera Production Certification

## Sensor Validation

Sensor PASS

[ ]

---

## MIPI Validation

MIPI PASS

[ ]

---

## RKISP Validation

RKISP PASS

[ ]

---

## V4L2 Validation

V4L2 PASS

[ ]

---

## NV12 Validation

NV12 PASS

[ ]

---

## DMA-BUF Validation

DMA-BUF PASS

[ ]

---

## EGLImage Validation

EGLImage PASS

[ ]

---

## Intrinsics Validation

PASS

[ ]

---

## Warp Validation

PASS

[ ]

---

## Replay Validation

PASS

[ ]

---

## Camera Certification

PASS

[ ]

---

# Section E — VisionIPC Certification

## Stream Validation

Road Camera Stream PASS

[ ]

Frames Arrive Correctly

[ ]

No Corruption

[ ]

No Drops

[ ]

---

## Timestamp Validation

Monotonic

[ ]

Stable

[ ]

---

## Replay Validation

Replay PASS

[ ]

---

## VisionIPC Certification

PASS

[ ]

---

# Section F — Runtime Certification

## OpenCL

loadyuv.cl PASS

[ ]

transform.cl PASS

[ ]

Tensor Generation PASS

[ ]

---

## Metadata

Metadata Located

[ ]

Metadata Validated

[ ]

Metadata Hash Verified

[ ]

Metadata PASS

[ ]

---

## Vision Runtime

Vision Model PASS

[ ]

Correlation > 0.995

[ ]

---

## Policy Runtime

Policy Model PASS

[ ]

Correlation > 0.995

[ ]

---

## Hidden State

Persistence Verified

[ ]

Temporal Stability Verified

[ ]

---

## Runtime Certification

PASS

[ ]

---

# Section G — modeld Certification

## Runtime Startup

modeld Starts

[ ]

No Runtime Errors

[ ]

No Crashes

[ ]

---

## Publishing

modelV2 Published

[ ]

cameraOdometry Published

[ ]

Planner Receives Messages

[ ]

---

## Stability

100 Frame Validation PASS

[ ]

1000 Frame Validation PASS

[ ]

---

## modeld Certification

PASS

[ ]

---

# Section H — Planner Certification

## Planner Health

Planner Alive

[ ]

Planner Stable

[ ]

---

## modelV2 Validation

Schema Correct

[ ]

Units Correct

[ ]

Frequency Correct

[ ]

---

## Overlay Validation

Path Correct

[ ]

Lane Correct

[ ]

Road Edge Correct

[ ]

Lead Vehicle Correct

[ ]

---

## Replay Validation

Replay PASS

[ ]

---

## Planner Certification

PASS

[ ]

---

# Section I — Performance Certification

## Camera → modelV2

Measured

[ ]

Target < 30 ms

[ ]

Preferred < 25 ms

[ ]

---

## Camera → UI

Measured

[ ]

Target < 35 ms

[ ]

---

## Vision Runtime

Average < 12 ms

[ ]

95% Stable

[ ]

---

## Policy Runtime

Average < 5 ms

[ ]

95% Stable

[ ]

---

## FPS

Measured

[ ]

Target Achieved

[ ]

---

## Performance Certification

PASS

[ ]

---

# Section J — Resource Certification

## CPU

Utilization Recorded

[ ]

Affinity Verified

[ ]

No Unexpected Migration

[ ]

---

## GPU

Utilization Recorded

[ ]

GPU Preview Path Verified

[ ]

---

## NPU

Vision Core 0

[ ]

Policy Core 1

[ ]

Core Assignment Verified

[ ]

---

## Memory

Peak Recorded

[ ]

No Leak Detected

[ ]

---

## Resource Certification

PASS

[ ]

---

# Section K — Thermal Certification

## CPU

Temperature Recorded

[ ]

No Throttling

[ ]

---

## GPU

Temperature Recorded

[ ]

No Throttling

[ ]

---

## NPU

Temperature Recorded

[ ]

No Throttling

[ ]

---

## Thermal Certification

PASS

[ ]

---

# Section L — Stress Certification

## Runtime Stability

1 Hour PASS

[ ]

4 Hour PASS

[ ]

---

## Camera Stability

No Disconnects

[ ]

No ISP Failures

[ ]

No DMA-BUF Failures

[ ]

---

## Runtime Stability

No RKNN Failures

[ ]

No modeld Failures

[ ]

No Planner Failures

[ ]

---

## Latency Stability

No Significant Drift

[ ]

No Queue Growth

[ ]

---

## Stress Certification

PASS

[ ]

---

# Section M — Recovery Certification

## Camera Recovery

Camera Restart PASS

[ ]

---

## Runtime Recovery

RKNN Restart PASS

[ ]

modeld Restart PASS

[ ]

---

## Replay Recovery

Replay Restart PASS

[ ]

---

## Recovery Certification

PASS

[ ]

---

# Section N — Rollback Certification

## Rollback Package

Exists

[ ]

---

## Known Good Build

Stored

[ ]

Verified

[ ]

---

## Rollback Procedure

Documented

[ ]

Tested

[ ]

---

## Rollback Certification

PASS

[ ]

---

# Section O — Documentation Certification

## Required Documents

camera.md

[ ]

visionipc.md

[ ]

modeld.md

[ ]

rknn.md

[ ]

validation.md

[ ]

performance.md

[ ]

deployment.md

[ ]

---

## Required Reports

Validation Report

[ ]

Performance Report

[ ]

Deployment Report

[ ]

---

## Required Checklists

camera_checklist.md

[ ]

rknn_checklist.md

[ ]

validation_checklist.md

[ ]

production_checklist.md

[ ]

---

## Documentation Certification

PASS

[ ]

---

# Section P — AI Agent Certification

## Discovery

Architecture Inventory Generated

[ ]

Runtime Inventory Generated

[ ]

Metadata Inventory Generated

[ ]

---

## Validation

All Metrics Generated

[ ]

Evidence Stored

[ ]

Acceptance Criteria Evaluated

[ ]

---

## Reporting

validation_report.json

[ ]

performance_report.json

[ ]

deployment_report.json

[ ]

---

## AI Agent Certification

PASS

[ ]

---

# Section Q — Production Approval Matrix

## Core Systems

Camera PASS

[ ]

VisionIPC PASS

[ ]

OpenCL PASS

[ ]

Metadata PASS

[ ]

Vision PASS

[ ]

Policy PASS

[ ]

modeld PASS

[ ]

Planner PASS

[ ]

Replay PASS

[ ]

---

## Operational Systems

Performance PASS

[ ]

Resources PASS

[ ]

Thermals PASS

[ ]

Stress PASS

[ ]

Recovery PASS

[ ]

Rollback PASS

[ ]

Documentation PASS

[ ]

---

## Production Approval

READY FOR TESTING

[ ]

READY FOR RC

[ ]

READY FOR PRODUCTION

[ ]

---

# Final Production Certification

Repository:

---

Branch:

---

Commit:

---

Hardware:

---

Camera:

---

Runtime:

---

Validation Date:

---

Reviewer:

---

Architecture PASS

[ ]

Validation PASS

[ ]

Performance PASS

[ ]

Stress PASS

[ ]

Recovery PASS

[ ]

Rollback PASS

[ ]

Documentation PASS

[ ]

Production Ready:

YES / NO

Final Result:

PASS / FAIL

Certification ID:

---

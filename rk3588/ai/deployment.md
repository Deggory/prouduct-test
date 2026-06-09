# DEPLOYMENT.MD (Authoritative Version)

## Section A — Engineering Specification

### 1. Objective

Deployment exists to move a validated RK3588 system into production.

Required sequence:

camera.md
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

Deployment is the final stage.

---

### 2. Deployment Philosophy

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

Never deploy before validation.

Never deploy before performance verification.

---

### 3. Deployment Ownership

camera.md owns:

Camera Deployment Readiness

modeld.md owns:

Model Pipeline Readiness

rknn.md owns:

Runtime Readiness

validation.md owns:

Proof of Correctness

performance.md owns:

Proof of Stability

deployment.md owns:

Release Process

---

### 4. Supported Architecture

IMX415
↓
RKISP
↓
NV12
↓
VisionIPC
↓
loadyuv.cl
↓
transform.cl
↓
DrivingModelFrame.prepare()
↓
RKNN Vision
↓
RKNN Policy
↓
Planner
↓
Controls
↓
Vehicle

This is the deployment target architecture.

---

### 5. Deployment Modes

Development

Validation

Release Candidate

Production

Always pass through validation.

---

### 6. Repository Preparation

Record:

Repository

Branch

Commit

Date

Operator

Generate:

deployment_metadata.json

---

### 7. Branch Strategy

Recommended:

main

↓

rk3588-rknn-validation

↓

rk3588-rknn-production

Never deploy directly from development branches.

---

### 8. Backup Strategy

Create:

backup/

Store:

Original Models

Original Metadata

Original Configurations

Original Patches

Rollback must always be possible.

---

### 9. Artifact Architecture

Required:

driving_vision.rknn

driving_policy.rknn

metadata

warp files

configuration files

validation reports

performance reports

Generate:

artifact_inventory.json

---

### 10. Artifact Ownership

Models

Metadata

Configuration

Reports

Checksums

Ownership must be documented.

---

### 11. Release Bundle Architecture

release_bundle/

models/

metadata/

configs/

reports/

logs/

checksums/

---

### 12. Checksum Policy

Generate:

SHA256

for:

Models

Metadata

Configurations

Reports

Store permanently.

---

### 13. Version Control Policy

Track:

Repository

Branch

Commit

Model Version

Metadata Version

Runtime Version

Kernel Version

---

### 14. Configuration Ownership

Environment Variables

Runtime Selection

Camera Configuration

Model Paths

Metadata Paths

Must be documented.

---

### 15. Runtime Architecture

Vision

↓

NPU Core 0

Policy

↓

NPU Core 1

Core 2

↓

Reserved

Production configuration.

---

### 16. CPU Architecture

modeld

↓

A76 Cores Only

Avoid A55 execution when possible.

---

### 17. Scheduler Policy

Optional:

SCHED_FIFO

Only after validation is complete.

---

### 18. Health Monitoring Architecture

Monitor:

CPU

Memory

NPU

Temperature

Planner Status

Generate:

health_report.json

---

### 19. Logging Architecture

Record:

Startup Events

Warnings

Errors

Inference Times

Camera Status

Planner Status

Logs are deployment artifacts.

---

### 20. Monitoring Philosophy

Every deployment must remain observable.

Unmonitored deployments are unsupported.

---

## Section B — Verification Specification

### 21. Pre-Deployment Checklist

Camera PASS

Modeld PASS

RKNN PASS

Validation PASS

Performance PASS

Required before deployment.

---

### 22. Repository Verification

Verify:

Repository Exists

Branch Correct

Commit Recorded

Clean Working Tree

---

### 23. Artifact Verification

Verify:

Exists

Readable

Correct Hash

Correct Version

Generate:

artifact_verification.json

---

### 24. Model Verification

Verify:

Vision Model

Policy Model

Hashes

Versions

Generate:

model_verification.json

---

### 25. Metadata Verification

Verify:

Metadata Exists

Metadata Matches Model

Version Recorded

Generate:

metadata_verification.json

---

### 26. Runtime Verification

Verify:

RKNN Runtime Installed

NPU Available

Core Assignment Valid

Generate:

runtime_verification.json

---

### 27. Camera Verification

Verify:

IMX415 Detected

Resolution Correct

FPS Correct

NV12 Correct

Generate:

camera_verification.json

---

### 28. Warp Verification

Verify:

Warp Exists

Resolution Matches

Intrinsics Match

Generate:

warp_verification.json

---

### 29. Configuration Verification

Verify:

Environment Variables

Paths

Runtime Selection

Generate:

config_verification.json

---

### 30. Startup Verification

Verify:

Camera Starts

VisionIPC Starts

modeld Starts

Planner Starts

Processes Remain Alive

---

### 31. Health Verification

Monitor:

CPU

Memory

NPU

Temperature

Process Health

---

### 32. Runtime Verification

Validate:

Inference Success

No Crashes

Stable Output

---

### 33. Validation Report Verification

Required:

Camera Validation

Model Validation

RKNN Validation

Planner Validation

System Validation

---

### 34. Performance Report Verification

Required:

Latency PASS

FPS PASS

Memory PASS

Thermals PASS

Recovery PASS

---

## Section C — Road Test Specification

### 35. Road Test Philosophy

Bench success is insufficient.

Road validation is mandatory.

---

### 36. Phase 1

Low-Speed Testing

Objectives:

Overlay Validation

Planner Validation

Runtime Validation

---

### 37. Phase 2

Mixed Traffic Testing

Objectives:

Curves

Intersections

Traffic

Planner Stability

---

### 38. Phase 3

Extended Duration Testing

1–4 Hours

Continuous Operation

Monitor:

Latency

Memory

Temperature

Planner

---

### 39. Thermal Validation

Monitor:

CPU

GPU

NPU

No thermal throttling permitted.

---

### 40. Memory Validation

Monitor:

RSS

Virtual Memory

Leak Growth

No leaks permitted.

---

### 41. Planner Validation

Planner Alive

Planner Stable

No Timing Drift

No Unexpected Behavior

---

### 42. Runtime Recovery Validation

Validate:

Camera Restart

Runtime Restart

Model Reload

Recovery Success

Generate:

recovery_report.json

---

## Section D — Release Engineering

### 43. Release Candidate Process

RC1
↓
Validation
↓
RC2
↓
Validation
↓
Production

Recommended workflow.

---

### 44. Regression Policy

Repeat validation after:

Model Updates

Runtime Updates

Camera Updates

Repository Updates

---

### 45. Long-Term Maintenance

Store:

Validation Reports

Performance Reports

Deployment Reports

For every release.

---

### 46. Security Policy

Verify:

Model Integrity

Metadata Integrity

Artifact Integrity

Prevent accidental deployment of modified artifacts.

---

### 47. Rollback Philosophy

Rollback must be immediate.

Never deploy without rollback capability.

---

### 48. Rollback Assets

Known-Good Branch

Known-Good Models

Known-Good Metadata

Known-Good Runtime

---

### 49. Rollback Triggers

Planner Instability

Runtime Crashes

Memory Leak

Thermal Instability

Unexpected Outputs

Immediate rollback required.

---

## Section E — AI Agent Operating Manual

### 50. Repository Discovery Workflow

Discover:

Camera Architecture

VisionIPC

modeld

Metadata

RKNN Runtime

Planner

Generate:

deployment_analysis.json

---

### 51. Fork Adaptation Rules

Never assume:

Paths

Metadata Locations

Environment Variables

Runtime Layout

Generate:

fork_deployment_report.json

---

### 52. Deployment Workflow

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

### 53. AI Agent Responsibilities

Analyze Repository

Detect Camera Pipeline

Detect modeld Architecture

Detect Runtime

Detect Metadata

Generate Patch Plan

Generate Validation Plan

Generate Rollback Plan

Generate Deployment Report

These responsibilities come directly from the deployment specification.

---

### 54. Reporting Requirements

Generate:

deployment_metadata.json

artifact_inventory.json

model_verification.json

runtime_verification.json

camera_verification.json

deployment_report.json

deployment_analysis.json

---

### 55. Failure Modes

Runtime Instability

Planner Instability

Thermal Throttling

Memory Leak

Validation Failure

Artifact Corruption

Rollback Failure

---

### 56. Production Readiness

Required:

Camera PASS

Modeld PASS

RKNN PASS

Validation PASS

Performance PASS

Road Testing PASS

---

### 57. Production Gate

Deployment prohibited until:

All acceptance criteria PASS.

No exceptions.

---

### 58. Final Release Checklist

Repository
[ ]

Camera
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

Documentation
[ ]

Release Bundle
[ ]

Checksums
[ ]

Rollback Plan
[ ]

Result:

PASS / FAIL

---

### 59. Final Deployment Record

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

Only deployments achieving PASS may be considered production-ready.

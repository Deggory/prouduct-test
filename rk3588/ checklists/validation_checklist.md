# VALIDATION_CHECKLIST.MD (Authoritative Version)

# Engineering Checklist + Validation Checklist + Verification Checklist + Production Certification Checklist + AI Agent Operating Checklist

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

Purpose:

Production certification of the complete perception pipeline.

---

# Section A — Repository Discovery Checklist

## Architecture Discovery

Repository Located

[ ]

Architecture Inventory Generated

[ ]

Process Inventory Generated

[ ]

Message Inventory Generated

[ ]

Model Inventory Generated

[ ]

Metadata Inventory Generated

[ ]

---

## Runtime Discovery

Tinygrad Runtime Located

[ ]

RKNN Runtime Located

[ ]

Fallback Runtime Verified

[ ]

Environment Variables Recorded

[ ]

---

## Deployment Discovery

Validation Reports Located

[ ]

Performance Reports Located

[ ]

Deployment Reports Located

[ ]

Rollback Package Located

[ ]

---

# Section B — Camera Validation Checklist

## Sensor Validation

Sensor Detected

[ ]

Sensor Stable

[ ]

Resolution Verified

[ ]

FPS Verified

[ ]

No Probe Errors

[ ]

---

## MIPI Validation

MIPI Link Stable

[ ]

No CRC Errors

[ ]

No Packet Loss

[ ]

No Link Resets

[ ]

---

## RKISP Validation

ISP Running

[ ]

Frames Generated

[ ]

No ISP Errors

[ ]

No Frame Corruption

[ ]

---

## V4L2 Validation

Device Present

[ ]

Streaming Works

[ ]

Buffers Valid

[ ]

NV12 Verified

[ ]

---

## NV12 Validation

Width Verified

[ ]

Height Verified

[ ]

Stride Verified

[ ]

Offsets Verified

[ ]

No Corruption

[ ]

---

## DMA-BUF Validation

Export Works

[ ]

Import Works

[ ]

No FD Leaks

[ ]

No Corruption

[ ]

---

## Camera Acceptance

Camera PASS

[ ]

---

# Section C — VisionIPC Validation Checklist

## Stream Validation

Road Stream Present

[ ]

Frames Arrive

[ ]

No Drops

[ ]

No Corruption

[ ]

---

## Timestamp Validation

Monotonic

[ ]

Correct Ordering

[ ]

Latency Recorded

[ ]

---

## Replay Validation

Replay Loads

[ ]

Frames Match Live Input

[ ]

Replay Stable

[ ]

---

## VisionIPC Acceptance

VisionIPC PASS

[ ]

---

# Section D — OpenCL Validation Checklist

## loadyuv.cl

Kernel Compiles

[ ]

Kernel Executes

[ ]

Output Valid

[ ]

---

## transform.cl

Kernel Compiles

[ ]

Kernel Executes

[ ]

Output Valid

[ ]

---

## Tensor Validation

Tensor Shape Correct

[ ]

Tensor Layout Correct

[ ]

Tensor Dtype Correct

[ ]

Tensor Statistics Verified

[ ]

---

## OpenCL Acceptance

OpenCL PASS

[ ]

---

# Section E — Metadata Validation Checklist

## Metadata Discovery

Metadata Located

[ ]

Version Recorded

[ ]

Hash Recorded

[ ]

---

## Input Validation

Input Count Correct

[ ]

Input Shapes Correct

[ ]

Input Layout Correct

[ ]

Input Dtype Correct

[ ]

---

## Output Validation

Output Count Correct

[ ]

Output Shapes Correct

[ ]

Output Layout Correct

[ ]

Output Dtype Correct

[ ]

---

## Slice Validation

Slices Located

[ ]

No Overlap

[ ]

Parser Compatible

[ ]

---

## Hidden State Validation

Shape Verified

[ ]

Persistence Verified

[ ]

Ownership Verified

[ ]

---

## Metadata Acceptance

Metadata PASS

[ ]

---

# Section F — Vision Model Validation Checklist

## Reference Runtime

Tinygrad Outputs Saved

[ ]

Reference Route Recorded

[ ]

Reference Metrics Generated

[ ]

---

## RKNN Validation

Model Loads

[ ]

Inference Runs

[ ]

Outputs Generated

[ ]

No Runtime Errors

[ ]

---

## Accuracy Validation

Same Input Used

[ ]

Output Comparison Generated

[ ]

Correlation Calculated

[ ]

Cosine Similarity Calculated

[ ]

Relative MAE Calculated

[ ]

---

## Acceptance Criteria

Correlation > 0.995

[ ]

Correlation > 0.999 Preferred

[ ]

No Semantic Differences

[ ]

---

## Vision Acceptance

Vision PASS

[ ]

---

# Section G — Policy Model Validation Checklist

## Input Validation

Features Correct

[ ]

Hidden State Correct

[ ]

Desire Input Correct

[ ]

Traffic Convention Correct

[ ]

---

## Output Validation

Trajectory Valid

[ ]

Curvature Valid

[ ]

Policy Outputs Valid

[ ]

---

## Accuracy Validation

Same Input Used

[ ]

Metrics Generated

[ ]

Reference Comparison Completed

[ ]

---

## Acceptance Criteria

Correlation > 0.995

[ ]

Correlation > 0.999 Preferred

[ ]

No Semantic Differences

[ ]

---

## Policy Acceptance

Policy PASS

[ ]

---

# Section H — modeld Validation Checklist

## Runtime Validation

modeld Starts

[ ]

No Runtime Errors

[ ]

RKNN Backend Loads

[ ]

Fallback Backend Preserved

[ ]

---

## Tensor Validation

Tensor Generated

[ ]

Tensor Shape Valid

[ ]

Tensor Statistics Valid

[ ]

---

## Publishing Validation

modelV2 Published

[ ]

cameraOdometry Published

[ ]

Planner Receives Messages

[ ]

---

## modeld Acceptance

modeld PASS

[ ]

---

# Section I — Planner Validation Checklist

## modelV2 Validation

Schema Correct

[ ]

Units Correct

[ ]

Frequency Correct

[ ]

---

## Planner Validation

Planner Alive

[ ]

Planner Stable

[ ]

No Oscillation

[ ]

No Invalid Trajectories

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

## Planner Acceptance

Planner PASS

[ ]

---

# Section J — Replay Validation Checklist

## Route Validation

Replay Route Loads

[ ]

Replay Completes

[ ]

No Crashes

[ ]

---

## Runtime Validation

Vision Stable

[ ]

Policy Stable

[ ]

Planner Stable

[ ]

---

## Output Validation

Outputs Match Reference

[ ]

No Significant Drift

[ ]

---

## Replay Acceptance

Replay PASS

[ ]

---

# Section K — Performance Validation Checklist

## Camera → modelV2

Latency Measured

[ ]

Target < 30 ms

[ ]

Preferred < 25 ms

[ ]

---

## Camera → UI

Latency Measured

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

## Performance Acceptance

Performance PASS

[ ]

---

# Section L — Resource Validation Checklist

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

EGL Path Verified

[ ]

---

## NPU

Core 0 Active

[ ]

Core 1 Active

[ ]

Core Assignment Verified

[ ]

---

## Memory

Usage Recorded

[ ]

Peak Recorded

[ ]

No Leak Detected

[ ]

---

## Resource Acceptance

Resources PASS

[ ]

---

# Section M — Thermal Validation Checklist

## CPU Thermal

Temperature Recorded

[ ]

No Throttling

[ ]

---

## GPU Thermal

Temperature Recorded

[ ]

No Throttling

[ ]

---

## NPU Thermal

Temperature Recorded

[ ]

No Throttling

[ ]

---

## Thermal Acceptance

Thermals PASS

[ ]

---

# Section N — Stress Validation Checklist

## Duration

1 Hour Pass

[ ]

4 Hour Preferred

[ ]

---

## Stability

No Crashes

[ ]

No Runtime Failures

[ ]

No Camera Failures

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

## Stress Acceptance

Stress PASS

[ ]

---

# Section O — Recovery Validation Checklist

## Camera Recovery

Camera Restart Passes

[ ]

---

## Runtime Recovery

RKNN Restart Passes

[ ]

modeld Restart Passes

[ ]

---

## Replay Recovery

Replay Restart Passes

[ ]

---

## Recovery Acceptance

Recovery PASS

[ ]

---

# Section P — Production Certification Checklist

## Core Validation

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

## Operational Validation

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

---

## Documentation

Validation Report Complete

[ ]

Performance Report Complete

[ ]

Deployment Report Complete

[ ]

Rollback Plan Complete

[ ]

---

# Section Q — AI Agent Verification Checklist

## Discovery

All Inventories Generated

[ ]

Architecture Verified

[ ]

Dependencies Verified

[ ]

---

## Validation

All Metrics Generated

[ ]

Acceptance Criteria Evaluated

[ ]

Evidence Stored

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

# Final Validation Certification

Repository:

---

Branch:

---

Commit:

---

Runtime:

---

Camera:

---

Validation Date:

---

Reviewer:

---

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

Production Ready:

YES / NO

Final Result:

PASS / FAIL

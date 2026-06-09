# RKNN_CHECKLIST.MD (Authoritative Version)

# Engineering Checklist + Validation Checklist + Performance Checklist + Production Checklist + AI Agent Operating Checklist

Version: 3.0

Target Hardware:

* RK3588
* RK3588S
* Orange Pi 5
* Orange Pi 5 Plus

Target Runtime:

* RKNN Toolkit 2
* RKNN Toolkit Lite 2
* RKNNLite

Target Models:

* Vision Model
* Policy Model

Target Pipeline:

IMX415
↓
RKISP
↓
NV12 DMA-BUF
↓
VisionIPC
↓
OpenCL
↓
RKNN Vision Core 0
↓
RKNN Policy Core 1
↓
modelV2/msgq
↓
Planner

---

# Section A — Pre-Port Checklist

## Hardware Validation

RK3588 Detected

[ ]

CPU Available

[ ]

GPU Available

[ ]

NPU Available

[ ]

Memory Sufficient

[ ]

Storage Sufficient

[ ]

---

## Runtime Validation

RKNN Toolkit Installed

[ ]

RKNNLite Installed

[ ]

Runtime Loads

[ ]

No Dependency Errors

[ ]

No Missing Libraries

[ ]

---

## Repository Discovery

modeld Located

[ ]

Metadata Located

[ ]

Vision Model Located

[ ]

Policy Model Located

[ ]

Runtime Inventory Generated

[ ]

---

# Section B — Model Inventory Checklist

## Vision Model

Model File Located

[ ]

Version Recorded

[ ]

Hash Recorded

[ ]

Metadata Located

[ ]

---

## Policy Model

Model File Located

[ ]

Version Recorded

[ ]

Hash Recorded

[ ]

Metadata Located

[ ]

---

## Inventory Artifacts

model_inventory.json

[ ]

metadata_inventory.json

[ ]

runtime_inventory.json

[ ]

---

# Section C — Metadata Checklist

## Metadata Discovery

Metadata File Exists

[ ]

Version Recorded

[ ]

Hash Recorded

[ ]

Compatible With Model

[ ]

---

## Input Validation

Input Names Valid

[ ]

Input Shapes Valid

[ ]

Input Dtypes Valid

[ ]

Input Layout Valid

[ ]

---

## Output Validation

Output Names Valid

[ ]

Output Shapes Valid

[ ]

Output Dtypes Valid

[ ]

Output Layout Valid

[ ]

---

## Slice Validation

Slices Located

[ ]

Slices Documented

[ ]

No Overlap

[ ]

Parser Compatible

[ ]

---

# Section D — Model Conversion Checklist

## ONNX Validation

ONNX Loads

[ ]

ONNX Runs

[ ]

Reference Outputs Saved

[ ]

---

## RKNN Conversion

Conversion Successful

[ ]

No Warnings

[ ]

No Unsupported Ops

[ ]

No Accuracy Warnings

[ ]

---

## RKNN Artifacts

vision_model.rknn

[ ]

policy_model.rknn

[ ]

conversion_report.json

[ ]

---

# Section E — RKNN Runtime Checklist

## Runtime Initialization

RKNN Runtime Loads

[ ]

Context Created

[ ]

Models Loaded

[ ]

No Errors

[ ]

---

## Runtime Configuration

Vision Core = 0

[ ]

Policy Core = 1

[ ]

Core Assignment Recorded

[ ]

---

## Runtime Stability

100 Inferences Pass

[ ]

1000 Inferences Pass

[ ]

No Runtime Crashes

[ ]

No Memory Growth

[ ]

---

# Section F — Vision Model Validation Checklist

## Input Validation

Input Shape Correct

[ ]

Input Layout Correct

[ ]

Input Dtype Correct

[ ]

Input Tensor Valid

[ ]

---

## Output Validation

Output Shape Correct

[ ]

Output Layout Correct

[ ]

Output Dtype Correct

[ ]

Output Count Correct

[ ]

---

## Accuracy Validation

Tinygrad Reference Exists

[ ]

Same Input Used

[ ]

Output Compared

[ ]

Metrics Generated

[ ]

---

## Metrics

Correlation > 0.995

[ ]

Correlation > 0.999 Preferred

[ ]

Cosine Similarity Valid

[ ]

Relative MAE Acceptable

[ ]

---

# Section G — Policy Model Validation Checklist

## Input Validation

Feature Tensor Correct

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

Output Count Correct

[ ]

Output Shape Correct

[ ]

---

## Accuracy Validation

Tinygrad Reference Exists

[ ]

Same Input Used

[ ]

Metrics Generated

[ ]

---

## Metrics

Correlation > 0.995

[ ]

Correlation > 0.999 Preferred

[ ]

Cosine Similarity Valid

[ ]

Relative MAE Acceptable

[ ]

---

# Section H — Hidden State Checklist

## State Discovery

State Shape Recorded

[ ]

State Dtype Recorded

[ ]

Metadata Verified

[ ]

---

## State Persistence

State Reused

[ ]

No Reset Between Frames

[ ]

Temporal Consistency Verified

[ ]

---

## Multi-Frame Validation

100 Frames Pass

[ ]

1000 Frames Preferred

[ ]

No Drift Detected

[ ]

---

# Section I — modeld Integration Checklist

## Runtime Integration

RKNN Backend Loads

[ ]

Fallback Runtime Preserved

[ ]

No Startup Errors

[ ]

---

## Tensor Validation

OpenCL Pipeline Preserved

[ ]

Tensor Generation Valid

[ ]

Tensor Statistics Valid

[ ]

---

## Publishing Validation

modelV2 Published

[ ]

cameraOdometry Published

[ ]

Planner Receives Data

[ ]

---

# Section J — Planner Compatibility Checklist

## modelV2 Validation

Schema Correct

[ ]

Frequency Correct

[ ]

Units Correct

[ ]

---

## Planner Validation

Planner Alive

[ ]

Planner Stable

[ ]

Trajectory Valid

[ ]

Overlay Correct

[ ]

---

## Replay Validation

Replay Route Passes

[ ]

Planner Matches Reference

[ ]

---

# Section K — Performance Checklist

## Vision Runtime

Average < 12 ms

[ ]

95% Stable

[ ]

No Queue Growth

[ ]

---

## Policy Runtime

Average < 5 ms

[ ]

95% Stable

[ ]

No Queue Growth

[ ]

---

## Combined Runtime

Vision + Policy < 20 ms

[ ]

Target Achieved

[ ]

---

## Pipeline Runtime

Camera → modelV2 < 30 ms

[ ]

Preferred < 25 ms

[ ]

---

# Section L — NPU Utilization Checklist

## Core Assignment

Vision Core 0

[ ]

Policy Core 1

[ ]

Core 2 Reserved

[ ]

---

## Utilization

Core 0 Active

[ ]

Core 1 Active

[ ]

No Unexpected Migration

[ ]

---

## Thermal Validation

No Thermal Throttling

[ ]

Stable During Stress Test

[ ]

---

# Section M — Memory Checklist

## Runtime Memory

Memory Recorded

[ ]

Peak Recorded

[ ]

No Leak Detected

[ ]

---

## Long Duration Test

1 Hour Pass

[ ]

4 Hour Preferred

[ ]

No Growth Detected

[ ]

---

# Section N — Recovery Checklist

## Runtime Recovery

Runtime Restart Passes

[ ]

Model Reload Passes

[ ]

Inference Resumes

[ ]

---

## Replay Recovery

Replay Restart Passes

[ ]

Replay Remains Stable

[ ]

---

# Section O — Production Readiness Checklist

## Validation

Metadata PASS

[ ]

Vision PASS

[ ]

Policy PASS

[ ]

Hidden State PASS

[ ]

Planner PASS

[ ]

Replay PASS

[ ]

---

## Performance

Latency PASS

[ ]

FPS PASS

[ ]

Memory PASS

[ ]

Thermal PASS

[ ]

Stress PASS

[ ]

---

## Deployment

Validation Report Exists

[ ]

Performance Report Exists

[ ]

Deployment Report Exists

[ ]

Rollback Plan Exists

[ ]

---

# Section P — AI Agent Verification Checklist

## Discovery

Repository Inventory Generated

[ ]

Runtime Inventory Generated

[ ]

Metadata Inventory Generated

[ ]

---

## Validation

Reference Runtime Compared

[ ]

Metrics Generated

[ ]

Acceptance Criteria Checked

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

# Final RKNN Certification

Hardware:

---

Vision Model:

---

Policy Model:

---

Vision Core:

---

Policy Core:

---

Average Vision Latency:

---

Average Policy Latency:

---

Combined Runtime:

---

Production Ready:

YES / NO

Reviewer:

---

Date:

---

Result:

PASS / FAIL

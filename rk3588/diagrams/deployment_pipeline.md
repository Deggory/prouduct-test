# DEPLOYMENT_PIPELINE.MD (Authoritative Version)

# Architecture Diagram + Deployment Diagram + Production Certification Diagram + AI Agent Operating Diagram

Version: 3.0

Target Platform:

* OpenPilot
* Sunnypilot
* FrogPilot
* OPKR

Target Hardware:

* RK3588
* Orange Pi 5

Target Runtime:

* RKNN Vision
* RKNN Policy
* Tinygrad Fallback

Deployment Type:

Production Deployment

---

# Section A — Complete Production Deployment Pipeline

```text
Repository
    ↓
Architecture Discovery
    ↓
Camera Validation
    ↓
VisionIPC Validation
    ↓
Metadata Validation
    ↓
RKNN Validation
    ↓
Planner Validation
    ↓
Performance Validation
    ↓
Stress Validation
    ↓
Recovery Validation
    ↓
Rollback Validation
    ↓
Deployment Certification
    ↓
Production Release
```

Rule:

```text
Every stage must PASS before deployment.
```

---

# Section B — Production Runtime Architecture

```text
IMX415
   ↓
RKISP
   ↓
NV12 DMA-BUF
   ├───────────────────────┬───────────────────────┐
   │                       │                       │
   ▼                       ▼                       ▼
VisionIPC              EGLImage                loggerd
   ↓                       ↓
modeld                 Mali GPU
   ↓                       ↓
OpenCL                 Camera Preview
   ↓                       ↓
RKNN Vision Core 0     Overlay Rendering
   ↓
RKNN Policy Core 1
   ↓
modelV2/msgq
   ↓
Planner
   ↓
Controls
```

---

# Section C — Deployment Preparation Flow

```text
Clone Repository
   ↓
Verify Branch
   ↓
Verify Commit
   ↓
Generate Inventory
   ↓
Generate Validation Plan
   ↓
Generate Performance Plan
   ↓
Generate Deployment Plan
```

Artifacts:

```text
architecture_inventory.json
runtime_inventory.json
metadata_inventory.json
deployment_inventory.json
```

---

# Section D — Build Pipeline

```text
Source Code
   ↓
Patch Application
   ↓
Code Validation
   ↓
Build System
   ↓
Compile
   ↓
Link
   ↓
Generate Artifacts
```

Outputs:

```text
vision.rknn
policy.rknn
metadata.json
validation_report.json
performance_report.json
deployment_report.json
```

---

# Section E — Camera Deployment Validation

```text
IMX415 Detected
   ↓
MIPI Stable
   ↓
RKISP Streaming
   ↓
V4L2 NV12 Valid
   ↓
DMA-BUF Valid
   ↓
VisionIPC Valid
   ↓
PASS
```

Required:

```text
No frame corruption
No frame drops
No ISP failures
```

---

# Section F — Runtime Deployment Validation

```text
Metadata Located
   ↓
Metadata Validated
   ↓
Vision RKNN Loaded
   ↓
Policy RKNN Loaded
   ↓
Core Assignment Verified
   ↓
Inference Verified
   ↓
PASS
```

Core Assignment:

```text
Vision → Core 0
Policy → Core 1
Core 2 Reserved
```

---

# Section G — Model Validation Flow

```text
Tinygrad Reference
         │
         ▼
Reference Outputs
         │
         ▼
      Compare
         ▲
         │
RKNN Outputs
```

Metrics:

```text
MAE
Relative MAE
Cosine Similarity
Correlation
```

Acceptance:

```text
Correlation > 0.995
Preferred > 0.999
```

---

# Section H — modelV2 Deployment Validation

```text
Vision Output
    ↓
Metadata Parser
    ↓
modelV2
    ↓
msgq Publish
    ↓
Planner Receive
    ↓
Planner Stable
```

Required:

```text
No schema changes
No planner modifications
```

---

# Section I — Performance Certification Flow

```text
Camera Capture
      ↓
VisionIPC
      ↓
OpenCL
      ↓
Vision RKNN
      ↓
Policy RKNN
      ↓
modelV2 Publish
```

Targets:

```text
Vision:
8–12 ms

Policy:
2–5 ms

Camera → modelV2:
< 30 ms

Preferred:
< 25 ms
```

---

# Section J — UI Certification Flow

```text
NV12 DMA-BUF
      ↓
EGLImage
      ↓
Mali GPU Texture
      ↓
Camera Preview
      ↓
Overlay Render
      ↓
Display
```

Target:

```text
Camera → UI
< 35 ms
```

---

# Section K — Stress Certification Flow

```text
Start Runtime
      ↓
1 Hour Test
      ↓
4 Hour Test
      ↓
Memory Monitoring
      ↓
Latency Monitoring
      ↓
Thermal Monitoring
      ↓
PASS
```

Required:

```text
No crashes
No memory leaks
No NPU failures
No planner failures
```

---

# Section L — Recovery Certification Flow

```text
Camera Restart
      ↓
Recovery Verified

RKNN Restart
      ↓
Recovery Verified

modeld Restart
      ↓
Recovery Verified

Replay Restart
      ↓
Recovery Verified
```

Result:

```text
Recovery PASS
```

---

# Section M — Rollback Certification Flow

```text
Production Release
      ↓
Rollback Package Exists
      ↓
Known Good Build Stored
      ↓
Rollback Tested
      ↓
PASS
```

Rollback Methods:

```text
git revert
known-good release tag
release bundle restore
```

---

# Section N — Production Approval Matrix

```text
Camera PASS
      ↓
VisionIPC PASS
      ↓
Metadata PASS
      ↓
Vision PASS
      ↓
Policy PASS
      ↓
modeld PASS
      ↓
Planner PASS
      ↓
Performance PASS
      ↓
Stress PASS
      ↓
Recovery PASS
      ↓
Rollback PASS
      ↓
Production Approved
```

---

# Section O — AI Agent Deployment Workflow

```text
Discover Repository
      ↓
Discover Metadata
      ↓
Discover Runtime
      ↓
Generate Validation Plan
      ↓
Generate Performance Plan
      ↓
Run Validation
      ↓
Run Benchmarks
      ↓
Run Stress Tests
      ↓
Generate Reports
      ↓
Generate Certification
      ↓
Approve Deployment
```

---

# Section P — Required Deployment Artifacts

```text
architecture_inventory.json

camera_inventory.json

runtime_inventory.json

metadata_inventory.json

validation_report.json

performance_report.json

deployment_report.json

rollback_report.json
```

All required before production approval.

---

# Section Q — Forbidden Deployment Paths

Forbidden:

```text
Deploy without validation

Deploy without metadata verification

Deploy without Tinygrad comparison

Deploy without rollback plan

Deploy with failing metrics

Deploy with unknown tensor layout
```

Also forbidden:

```text
Planner modifications to fix runtime issues

Controlsd modifications to fix perception issues

Hardcoded metadata indices
```

---

# Section R — Final Production Deployment Diagram

```text
Repository
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
Production Release
    ↓
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
modelV2
    ↓
Planner
    ↓
Controls
```

Final Production Targets:

```text
Camera → modelV2: < 30 ms

Preferred:
< 25 ms

Camera → UI:
< 35 ms

Vision:
8–12 ms

Policy:
2–5 ms

Production Status:
APPROVED
```

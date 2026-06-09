# DEPLOYMENT_EXAMPLE.MD (Authoritative Version)

# Engineering Example + Deployment Example + Production Certification Example + AI Agent Operating Example

Version: 3.0

Target Platform:

* OpenPilot
* Sunnypilot
* FrogPilot
* OPKR

Target Hardware:

* Orange Pi 5
* RK3588
* RK3588S

Target Camera:

* IMX415

Target Runtime:

* RKNN Vision
* RKNN Policy

Deployment Type:

Production Release

---

# Section A — Objective

## 1. Purpose

This document demonstrates a complete production deployment of:

```text
IMX415
+
RKISP
+
VisionIPC
+
OpenCL
+
RKNN
+
OpenPilot
```

running on:

```text
Orange Pi 5
RK3588
```

---

## 2. Production Definition

Production deployment means:

```text
Validation PASS
Performance PASS
Stress PASS
Recovery PASS
Deployment PASS
```

All must pass.

---

## 3. Final Production Pipeline

```text
IMX415
↓
RKISP
↓
NV12 DMA-BUF
├──────────────┬─────────────┐
│              │             │
▼              ▼             ▼
VisionIPC    EGLImage      loggerd
↓              ↓
OpenCL       Mali GPU
↓              ↓
RKNN         UI
↓
modelV2
↓
Planner
↓
Controls
```

---

# Section B — Hardware Deployment Example

## 4. Hardware Inventory

Board:

```text
Orange Pi 5
```

CPU:

```text
4 × Cortex A76
4 × Cortex A55
```

GPU:

```text
Mali G610 MP4
```

NPU:

```text
6 TOPS
3 Core NPU
```

RAM:

```text
16 GB LPDDR4X
```

---

## 5. Camera Inventory

Camera:

```text
Sony IMX415
```

Interface:

```text
MIPI CSI-2
```

Output:

```text
NV12
```

Resolution:

```text
1280×720
```

FPS:

```text
20–30
```

---

## 6. Runtime Inventory

Vision Runtime:

```text
RKNN
```

Policy Runtime:

```text
RKNN
```

Vision Core:

```text
0
```

Policy Core:

```text
1
```

Reserved:

```text
Core 2
```

---

# Section C — Pre-Deployment Validation

## 7. Camera Validation

Results:

```text
Sensor:
PASS

MIPI:
PASS

RKISP:
PASS

V4L2:
PASS

NV12:
PASS

DMA-BUF:
PASS
```

---

## 8. VisionIPC Validation

Results:

```text
Frame Transport:
PASS

Timestamp Validation:
PASS

Replay Validation:
PASS
```

---

## 9. Metadata Validation

Results:

```text
Metadata Located:
PASS

Metadata Version:
PASS

Metadata Hash:
PASS

Slice Validation:
PASS
```

---

## 10. RKNN Validation

Vision:

```text
Correlation:
0.9997
```

Policy:

```text
Correlation:
0.9995
```

Status:

```text
PASS
```

---

# Section D — Production Configuration Example

## 11. Environment Variables

```bash
export OPENPILOT_MODELD_BACKEND=rknn

export RKNN_VISION_CORE=0

export RKNN_POLICY_CORE=1

export RK_USE_DMABUF=1

export RK_USE_EGLIMAGE=1
```

---

## 12. Runtime Configuration

Vision:

```text
RKNN Core 0
```

Policy:

```text
RKNN Core 1
```

Fallback:

```text
Tinygrad Available
```

---

## 13. Camera Configuration

```text
Sensor:
IMX415

Format:
NV12

Transport:
DMA-BUF

Preview:
EGLImage
```

---

# Section E — Build Example

## 14. Build Environment

Repository:

```text
sunnypilot-rk3588
```

Branch:

```text
rk3588-production
```

Commit:

```text
abcdef123456
```

---

## 15. Build Command

Example:

```bash
scons -j$(nproc)
```

Expected:

```text
BUILD SUCCESS
```

---

## 16. Artifact Generation

Expected:

```text
vision.rknn

policy.rknn

metadata.json

validation_report.json

performance_report.json

deployment_report.json
```

---

# Section F — Runtime Startup Example

## 17. Start Pipeline

```bash
./launch_openpilot.sh
```

---

## 18. Startup Sequence

Expected:

```text
manager
↓
camerad
↓
VisionIPC
↓
modeld
↓
RKNN
↓
Planner
↓
UI
```

---

## 19. Runtime Verification

Verify:

```text
No crashes

No missing models

No metadata errors

No camera errors
```

---

# Section G — Performance Example

## 20. Camera Timing

Capture:

```text
4 ms
```

VisionIPC:

```text
1 ms
```

OpenCL:

```text
5 ms
```

---

## 21. RKNN Timing

Vision:

```text
10 ms
```

Policy:

```text
3 ms
```

---

## 22. End-to-End Timing

Camera → modelV2

```text
23 ms
```

Status:

```text
PASS
```

---

## 23. UI Timing

Camera → UI

```text
28 ms
```

Status:

```text
PASS
```

---

# Section H — Resource Example

## 24. CPU Usage

Average:

```text
32%
```

Peak:

```text
54%
```

Status:

```text
PASS
```

---

## 25. GPU Usage

Average:

```text
18%
```

Peak:

```text
34%
```

Status:

```text
PASS
```

---

## 26. NPU Usage

Vision Core 0:

```text
72%
```

Policy Core 1:

```text
31%
```

Core 2:

```text
Idle
```

Status:

```text
PASS
```

---

## 27. Memory Usage

Average:

```text
1.8 GB
```

Peak:

```text
2.4 GB
```

Status:

```text
PASS
```

---

# Section I — Thermal Example

## 28. CPU Temperature

Average:

```text
61°C
```

Peak:

```text
72°C
```

---

## 29. GPU Temperature

Average:

```text
58°C
```

Peak:

```text
67°C
```

---

## 30. NPU Temperature

Average:

```text
63°C
```

Peak:

```text
74°C
```

---

## 31. Thermal Status

```text
No throttling
```

Result:

```text
PASS
```

---

# Section J — Stress Example

## 32. Test Duration

```text
4 Hours
```

---

## 33. Runtime Stability

Results:

```text
No crashes

No camera failures

No RKNN failures

No planner failures
```

---

## 34. Memory Stability

Results:

```text
No memory leak

No abnormal growth
```

---

## 35. Stress Result

```text
PASS
```

---

# Section K — Recovery Example

## 36. Camera Restart

Result:

```text
Automatic Recovery
PASS
```

---

## 37. RKNN Restart

Result:

```text
Context Recreated
PASS
```

---

## 38. modeld Restart

Result:

```text
Recovery Successful
PASS
```

---

## 39. Replay Restart

Result:

```text
Replay Continues
PASS
```

---

# Section L — Deployment Certification Example

## 40. Validation Summary

```text
Camera:
PASS

VisionIPC:
PASS

Metadata:
PASS

Vision:
PASS

Policy:
PASS

Planner:
PASS
```

---

## 41. Performance Summary

```text
Latency:
PASS

FPS:
PASS

Memory:
PASS

Thermals:
PASS
```

---

## 42. Operational Summary

```text
Stress:
PASS

Recovery:
PASS

Rollback:
PASS
```

---

# Section M — Rollback Example

## 43. Rollback Package

Exists:

```text
YES
```

---

## 44. Rollback Command

Example:

```bash
git revert <deployment_commit>
```

or

```bash
git checkout known_good_release
```

---

## 45. Rollback Validation

Result:

```text
PASS
```

---

# Section N — Production Approval Example

## 46. Approval Matrix

Camera

```text
PASS
```

VisionIPC

```text
PASS
```

Metadata

```text
PASS
```

Vision

```text
PASS
```

Policy

```text
PASS
```

Planner

```text
PASS
```

Performance

```text
PASS
```

Stress

```text
PASS
```

Recovery

```text
PASS
```

Rollback

```text
PASS
```

---

## 47. Deployment Status

```text
READY FOR PRODUCTION
```

---

# Section O — AI Agent Operating Example

## 48. Deployment Workflow

```text
Repository Discovery
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
Production Deployment
```

---

## 49. Required Deliverables

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

---

## 50. Agent Rules

Always:

* validate before deployment
* benchmark before deployment
* verify rollback
* preserve planner semantics
* preserve metadata semantics

Never:

* deploy without validation
* deploy without rollback
* deploy with failing metrics
* deploy with unknown metadata

---

# Final Production Example

Platform:

```text
Orange Pi 5
```

Camera:

```text
IMX415
```

Runtime:

```text
RKNN
```

Vision Core:

```text
0
```

Policy Core:

```text
1
```

Camera → modelV2:

```text
23 ms
```

Camera → UI:

```text
28 ms
```

Stress:

```text
4 Hours PASS
```

Recovery:

```text
PASS
```

Production Certification:

```text
APPROVED
```

Final Result:

```text
PASS
```

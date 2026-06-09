# PERFORMANCE.MD (Authoritative Version)

# Engineering Specification + Validation Specification + AI Agent Operating Manual

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
* Mali-G610 GPU
* OpenCL preprocessing
* DMA-BUF
* EGLImage

Target Forks:

* openpilot
* sunnypilot
* frogpilot
* OPKR
* KisaPilot

---

# Section A — Engineering Specification

## 1. Objective

Performance exists to ensure:

Correctness
↓
Stability
↓
Low Latency
↓
High Throughput

Correctness always has higher priority than FPS.

---

## 2. Performance Philosophy

Never optimize:

Before Validation

Never optimize:

Before Stability

Optimization order:

Correctness
↓
Validation
↓
Stability
↓
Performance

---

## 3. Production Architecture

Target architecture:

IMX415
↓
RKISP
↓
NV12 DMA-BUF
├──────────────┬───────────────┐
│              │               │
▼              ▼               ▼
VisionIPC    EGLImage       loggerd
↓              ↓
OpenCL       Mali GPU
↓              ↓
RKNN         UI
↓
modelV2/msgq
↓
planner
↓
controls

---

## 4. Performance Ownership

camera.md

owns:

* camera timing
* capture latency

visionipc.md

owns:

* transport latency
* DMA-BUF transport

modeld.md

owns:

* preprocessing timing
* tensor timing

rknn.md

owns:

* inference timing
* NPU utilization

performance.md

owns:

* measurement
* benchmarking
* optimization
* acceptance

---

## 5. Performance Layers

Layer 1

Camera

Layer 2

VisionIPC

Layer 3

Preprocessing

Layer 4

Inference

Layer 5

Publishing

Layer 6

Planner

Layer 7

UI

Each layer must be measured independently.

---

## 6. Latency Philosophy

Measure:

Average

Median

95%

99%

Maximum

Average latency alone is insufficient.

---

## 7. Throughput Philosophy

Measure:

FPS

Frame Drops

Queue Depth

Processing Rate

---

## 8. Jitter Philosophy

Low jitter is often more important than high FPS.

Target:

<5 ms

Preferred:

<2 ms

---

## 9. Orange Pi 5 Performance Targets

Current Baseline:

Camera → modelV2

18–30 ms

Current UI:

30–45 ms

---

## 10. DMA-BUF Targets

Expected:

Camera → modelV2

15–27 ms

Gain:

1–4 ms

---

## 11. DMA-BUF + EGL Targets

Expected:

Camera → modelV2

15–27 ms

Camera → UI

20–35 ms

Gain:

3–8 ms

---

## 12. FPS Targets

Minimum:

20 FPS

Target:

30 FPS

Preferred:

40+ FPS

without violating latency targets.

---

## 13. End-to-End Budget

Target:

<30 ms

Acceptable:

<40 ms

Maximum:

50 ms

---

## 14. Camera Budget

Capture:

3–5 ms

Target.

---

## 15. VisionIPC Budget

Transport:

1–2 ms

Target.

---

## 16. OpenCL Budget

loadyuv.cl

transform.cl

Combined:

3–6 ms

Target.

---

## 17. Vision RKNN Budget

Vision Core 0

Target:

8–12 ms

---

## 18. Policy RKNN Budget

Policy Core 1

Target:

2–5 ms

---

## 19. Publish Budget

modelV2/msgq

Target:

1–2 ms

---

## 20. UI Budget

GPU Render

Target:

3–12 ms

---

## 21. CPU Architecture

RK3588:

4× Cortex-A76

4× Cortex-A55

Production:

Prefer A76

---

## 22. CPU Affinity

Recommended:

modeld

↓

CPU4-CPU7

Avoid A55 migration.

---

## 23. Scheduler Policy

Optional:

SCHED_FIFO

Priority:

50–60

Only after validation.

---

## 24. NPU Architecture

Core 0

Vision

Core 1

Policy

Core 2

Reserved

---

## 25. NPU Assignment Rule

Never share:

Vision

and

Policy

on same core.

---

## 26. GPU Architecture

Mali-G610

Responsibilities:

UI Rendering

Texture Rendering

OpenGL

Not:

RKNN Inference

---

## 27. EGLImage Architecture

DMA-BUF
↓
EGLImage
↓
GPU Texture

Purpose:

Zero-copy camera preview

---

## 28. Memory Architecture

Track:

Camera Buffers

VisionIPC Buffers

DMA-BUF Buffers

GPU Textures

RKNN Buffers

Feature Buffers

Hidden State Buffers

---

## 29. Buffer Reuse Policy

Avoid:

Per-frame allocation

Prefer:

Persistent buffers

---

## 30. Logging Policy

Performance tests must record:

CPU

GPU

NPU

Memory

Latency

Temperature

---

# Section B — Validation Specification

## 31. Camera Performance Validation

Measure:

Capture Latency

Frame Rate

Frame Drops

Generate:

camera_performance.json

---

## 32. VisionIPC Validation

Measure:

Transport Latency

Queue Depth

Drops

Generate:

visionipc_performance.json

---

## 33. DMA-BUF Validation

Measure:

Copy Reduction

CPU Usage Reduction

Latency Improvement

Generate:

dmabuf_performance.json

---

## 34. OpenCL Validation

Measure:

loadyuv.cl

transform.cl

Execution Time

Generate:

opencl_performance.json

---

## 35. Tensor Validation

Measure:

Tensor Preparation Time

Allocation Count

Buffer Reuse

---

## 36. Vision Performance Validation

Measure:

Inference Time

Queue Delay

Core Utilization

Generate:

vision_performance.json

---

## 37. Policy Performance Validation

Measure:

Inference Time

Queue Delay

Core Utilization

Generate:

policy_performance.json

---

## 38. Combined Inference Validation

Measure:

Vision + Policy

Target:

<20 ms

---

## 39. Planner Validation

Measure:

Planner Frequency

Planner Latency

Planner Jitter

Generate:

planner_performance.json

---

## 40. UI Validation

Measure:

Render Time

Display Latency

Overlay Latency

Generate:

ui_performance.json

---

## 41. EGL Validation

Measure:

Import Time

Texture Creation

Render Time

Generate:

egl_performance.json

---

## 42. FPS Validation

Record:

Average FPS

Minimum FPS

Maximum FPS

95%

99%

---

## 43. Latency Validation

Record:

Average

Median

95%

99%

Maximum

---

## 44. Copy Count Validation

Measure:

Camera Copies

VisionIPC Copies

UI Copies

Goal:

Minimum Copies

---

## 45. CPU Validation

Measure:

A76 Usage

A55 Usage

Migration

Scheduler Behavior

---

## 46. GPU Validation

Measure:

GPU Utilization

Texture Throughput

UI Load

---

## 47. NPU Validation

Measure:

Core 0 Utilization

Core 1 Utilization

Core 2 Utilization

---

## 48. Memory Validation

Measure:

RSS

Virtual Memory

Allocation Count

Leaks

---

## 49. Thermal Validation

Measure:

CPU Temperature

GPU Temperature

NPU Temperature

---

## 50. Long Duration Validation

Minimum:

1 Hour

Preferred:

4 Hours

Record:

Latency

Memory

Temperature

FPS

---

## 51. Recovery Validation

Measure:

Camera Restart

Runtime Restart

Model Reload

Recovery Time

---

## 52. Acceptance Criteria

Camera PASS

VisionIPC PASS

OpenCL PASS

RKNN PASS

Planner PASS

UI PASS

Latency PASS

Thermals PASS

Memory PASS

Recovery PASS

---

# Section C — AI Agent Operating Manual

## 53. Discovery Workflow

Discover:

Camera

VisionIPC

DMA-BUF

OpenCL

RKNN

Planner

UI

Generate:

performance_inventory.json

---

## 54. Benchmark Workflow

Discovery
↓
Camera
↓
VisionIPC
↓
DMA-BUF
↓
OpenCL
↓
Vision
↓
Policy
↓
Planner
↓
UI

Generate Reports

---

## 55. Optimization Workflow

Baseline
↓
Validate
↓
DMA-BUF
↓
Validate
↓
EGLImage
↓
Validate
↓
CPU Affinity
↓
Validate

Never skip validation.

---

## 56. Fork Adaptation Rules

Never assume:

CPU numbering

Runtime names

Model paths

Environment variables

Discover dynamically.

---

## 57. Reporting Requirements

Generate:

camera_performance.json

visionipc_performance.json

dmabuf_performance.json

opencl_performance.json

vision_performance.json

policy_performance.json

planner_performance.json

ui_performance.json

thermal_report.json

latency_report.json

performance_inventory.json

---

## 58. Troubleshooting

Low FPS

High Latency

Thermal Throttling

DMA-BUF Fallback

NPU Contention

CPU Migration

Planner Jitter

UI Lag

Memory Leak

Document root cause and fix.

---

## 59. Failure Modes

Thermal Throttling

Memory Leak

NPU Contention

DMA-BUF Failure

GPU Import Failure

Planner Starvation

Queue Saturation

Latency Spike

---

## 60. Production Modes

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

Recommended:

Mode 3

---

## 61. Expected Performance

Mode 1

Camera → modelV2

18–30 ms

Camera → UI

30–45 ms

Mode 2

15–27 ms

27–42 ms

Mode 3

15–27 ms

20–35 ms

---

## 62. Production Readiness

Required:

Latency PASS

FPS PASS

Memory PASS

Thermals PASS

DMA-BUF PASS

EGL PASS

Planner PASS

Recovery PASS

---

## 63. Final Checklist

Camera
[ ]

VisionIPC
[ ]

DMA-BUF
[ ]

OpenCL
[ ]

Vision RKNN
[ ]

Policy RKNN
[ ]

Planner
[ ]

UI
[ ]

Latency
[ ]

FPS
[ ]

Memory
[ ]

Thermals
[ ]

Recovery
[ ]

Result:

PASS / FAIL

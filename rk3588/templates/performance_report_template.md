# PERFORMANCE_REPORT_TEMPLATE.MD (Authoritative Version)

# Engineering Specification + Performance Reporting Specification + Benchmarking Specification + Production Acceptance Specification + AI Agent Operating Manual

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

---

# Section A — Performance Report Engineering Specification

## 1. Objective

This document defines:

* performance reporting
* latency measurement
* FPS measurement
* CPU measurement
* GPU measurement
* NPU measurement
* thermal measurement
* production acceptance criteria

Goal:

Provide a repeatable performance benchmark format across all OpenPilot-derived repositories.

---

## 2. Performance Philosophy

Performance is measured.

Not guessed.

Every reported number must originate from:

Instrumentation
↓
Measurement
↓
Documentation

---

## 3. Benchmark Hierarchy

Camera
↓
VisionIPC
↓
OpenCL
↓
Vision Model
↓
Policy Model
↓
Planner
↓
UI
↓
System

Each stage measured independently.

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

Model Version:

Metadata Version:

Kernel Version:

---

## 5. Benchmark Scope

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

Vision RKNN

[ ]

Policy RKNN

[ ]

Planner

[ ]

UI

[ ]

Thermals

[ ]

Memory

[ ]

Stress

---

# Section B — Hardware Benchmark Report

## 6. CPU Information

CPU:

Core Count:

A76 Count:

A55 Count:

Governor:

Affinity:

Scheduler:

---

## 7. GPU Information

GPU:

Driver:

OpenGL Version:

OpenCL Version:

---

## 8. NPU Information

Runtime:

RKNN Version:

Vision Core:

Policy Core:

Reserved Core:

---

## 9. Memory Information

RAM:

Available RAM:

Swap:

DMA-BUF Enabled:

---

## 10. System Information

OS:

Kernel:

Board:

Storage:

---

# Section C — Camera Performance Report

## 11. Sensor Benchmark

Sensor:

Resolution:

FPS:

Status:

PASS / FAIL

---

## 12. Capture Latency

Average:

Median:

95%:

99%:

Maximum:

---

## 13. Frame Drop Analysis

Frames Captured:

Frames Dropped:

Drop Rate:

---

## 14. V4L2 Performance

Buffer Type:

Buffer Count:

Average Capture Time:

---

## 15. DMA-BUF Performance

Enabled:

YES / NO

Average Gain:

Copy Reduction:

CPU Reduction:

---

## 16. Camera Summary

Result:

PASS / FAIL

---

# Section D — VisionIPC Performance Report

## 17. Stream Throughput

Road Stream FPS:

Wide Stream FPS:

Driver Stream FPS:

---

## 18. Transport Latency

Average:

Median:

95%:

99%:

Maximum:

---

## 19. Queue Analysis

Average Queue Depth:

Peak Queue Depth:

Drops:

---

## 20. VisionIPC Summary

Result:

PASS / FAIL

---

# Section E — OpenCL Performance Report

## 21. loadyuv.cl Benchmark

Average:

Median:

95%:

Maximum:

---

## 22. transform.cl Benchmark

Average:

Median:

95%:

Maximum:

---

## 23. Combined OpenCL Time

Average:

Target:

3–6 ms

Status:

PASS / FAIL

---

# Section F — Vision RKNN Performance Report

## 24. Vision Runtime

Runtime:

Core:

Threads:

---

## 25. Vision Inference

Average:

Median:

95%:

99%:

Maximum:

---

## 26. Vision Throughput

FPS:

Queue Delay:

Utilization:

---

## 27. Vision Acceptance

Target:

8–12 ms

Status:

PASS / FAIL

---

# Section G — Policy RKNN Performance Report

## 28. Policy Runtime

Runtime:

Core:

Threads:

---

## 29. Policy Inference

Average:

Median:

95%:

99%:

Maximum:

---

## 30. Policy Throughput

FPS:

Queue Delay:

Utilization:

---

## 31. Policy Acceptance

Target:

2–5 ms

Status:

PASS / FAIL

---

# Section H — Planner Performance Report

## 32. modelV2 Publish

Frequency:

Latency:

Drops:

---

## 33. Planner Frequency

Average:

Minimum:

Maximum:

---

## 34. Planner Latency

Average:

Median:

95%:

Maximum:

---

## 35. Planner Acceptance

Result:

PASS / FAIL

---

# Section I — UI Performance Report

## 36. UI Rendering Path

Mode:

CPU

GPU

DMA-BUF

EGLImage

---

## 37. Camera Preview Latency

Average:

Median:

95%:

Maximum:

---

## 38. Overlay Latency

Path Overlay:

Lane Overlay:

Road Edge Overlay:

---

## 39. GPU Utilization

Average:

Peak:

---

## 40. UI Acceptance

Result:

PASS / FAIL

---

# Section J — System Latency Report

## 41. Pipeline Latency

Camera:

VisionIPC:

OpenCL:

Vision:

Policy:

Planner:

UI:

---

## 42. End-to-End Latency

Camera → modelV2

Average:

95%:

Maximum:

---

## 43. Display Latency

Camera → UI

Average:

95%:

Maximum:

---

## 44. Production Targets

Mode 1

Baseline

18–30 ms

Camera → modelV2

Mode 2

DMA-BUF

15–27 ms

Mode 3

DMA-BUF + EGLImage

15–27 ms

Camera → modelV2

20–35 ms

Camera → UI

---

## 45. Latency Acceptance

PASS / FAIL

---

# Section K — Resource Utilization Report

## 46. CPU Utilization

Average:

Peak:

A76 Usage:

A55 Usage:

---

## 47. GPU Utilization

Average:

Peak:

---

## 48. NPU Utilization

Core 0:

Core 1:

Core 2:

---

## 49. Memory Usage

Average:

Peak:

Leaks:

---

## 50. Resource Acceptance

PASS / FAIL

---

# Section L — Thermal Report

## 51. CPU Temperature

Average:

Peak:

---

## 52. GPU Temperature

Average:

Peak:

---

## 53. NPU Temperature

Average:

Peak:

---

## 54. Thermal Throttling

Observed:

YES / NO

---

## 55. Thermal Acceptance

PASS / FAIL

---

# Section M — Stress Report

## 56. Test Duration

Duration:

Environment:

---

## 57. Stability Metrics

Crashes:

Frame Drops:

Inference Failures:

Restarts:

---

## 58. Memory Stability

Leaks:

Growth Rate:

---

## 59. Latency Stability

Average:

95%:

Drift:

---

## 60. Stress Acceptance

PASS / FAIL

---

# Section N — Comparative Benchmark Report

## 61. Baseline Runtime

Tinygrad:

Average:

---

## 62. Candidate Runtime

RKNN:

Average:

---

## 63. Improvement

Latency Gain:

FPS Gain:

CPU Reduction:

---

## 64. DMA-BUF Impact

Before:

After:

Gain:

---

## 65. EGLImage Impact

Before:

After:

Gain:

---

## 66. RGA Impact

Before:

After:

Gain:

---

# Section O — AI Agent Operating Manual

## 67. Benchmark Workflow

Discovery
↓
Camera Benchmark
↓
VisionIPC Benchmark
↓
OpenCL Benchmark
↓
Vision Benchmark
↓
Policy Benchmark
↓
Planner Benchmark
↓
UI Benchmark
↓
Thermal Benchmark
↓
Report Generation

---

## 68. Reporting Rules

Never report:

Performance Improvement

without measured baseline.

Every claim requires:

Metric

Method

Evidence

---

## 69. Artifact Requirements

Attach:

camera_performance.json

visionipc_performance.json

opencl_performance.json

vision_performance.json

policy_performance.json

planner_performance.json

ui_performance.json

thermal_report.json

latency_report.json

---

## 70. Production Acceptance

Required:

Camera PASS

VisionIPC PASS

Vision PASS

Policy PASS

Planner PASS

Latency PASS

Thermals PASS

Stress PASS

---

## 71. Final Performance Status

Repository:

Branch:

Commit:

Performance Result:

PASS / FAIL

Production Performance:

YES / NO

Reviewer:

Date:

---

## 72. Final Acceptance Checklist

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

CPU
[ ]

GPU
[ ]

NPU
[ ]

Memory
[ ]

Thermals
[ ]

Stress
[ ]

Result:

PASS / FAIL

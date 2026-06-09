# PERFORMANCE.MD (Authoritative Version)

## Section A — Engineering Specification

### 1. Objective

Performance exists to ensure:

Stable Camera Timing
↓
Stable Inference Timing
↓
Stable Planner Timing
↓
Predictable Vehicle Behavior

Performance is not:

Maximum FPS

Performance is:

Consistency

---

### 2. Performance Philosophy

Priority Order:

Correctness
↓
Stability
↓
Latency
↓
FPS

Never sacrifice correctness for benchmark numbers.

---

### 3. Reference Pipeline

IMX415
↓
RKISP
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

Every stage contributes latency.

---

### 4. Performance Ownership

camera.md owns:

Camera Performance

modeld.md owns:

Tensor Performance

rknn.md owns:

Inference Performance

performance.md owns:

Measurement

Optimization

Benchmarking

Acceptance

---

### 5. Benchmark Philosophy

All benchmarks must be:

Repeatable

Comparable

Versioned

Reproducible

---

### 6. Benchmark Artifacts

Generate:

timing_report.json

throughput_report.json

latency_report.json

memory_report.json

thermal_report.json

npu_report.json

performance_analysis.json

---

### 7. Benchmark Dataset Requirements

Replay Route

Recorded Video

Live Camera

Minimum:

1000 Frames

Preferred:

10000+ Frames

---

### 8. Performance Environment

Record:

Repository

Commit

Runtime

Kernel

CPU Governor

NPU Version

Temperature

Power Source

---

### 9. Orange Pi 5 Reference Targets

Expected:

Camera

3–5 ms

OpenCL

3–6 ms

Vision RKNN

8–12 ms

Policy RKNN

2–5 ms

Publishing

1–2 ms

Total

17–30 ms

Expected FPS

20–30 FPS

These targets come directly from the RK3588 performance baseline.

---

### 10. Latency Architecture

Camera
↓
Preprocess
↓
Inference
↓
Parsing
↓
Publishing

Every stage must be measured.

---

### 11. End-to-End Budget

Target:

<35 ms

Acceptable:

<50 ms

Preferred:

<30 ms

---

### 12. Frame Timing Architecture

Capture Start

Capture End

Preprocess Start

Preprocess End

Inference Start

Inference End

Publish Time

Every frame should record timestamps.

---

### 13. Throughput Architecture

Measure:

Average FPS

Minimum FPS

Maximum FPS

95th Percentile FPS

99th Percentile FPS

---

### 14. Jitter Architecture

Measure:

Frame-to-frame variation

Target:

<5 ms

Preferred:

<2 ms

Large jitter is often more damaging than low FPS.

---

### 15. CPU Architecture

RK3588:

4× Cortex-A76

4× Cortex-A55

A76 cluster preferred.

---

### 16. CPU Affinity Strategy

modeld

↓

CPU4-CPU7

Only

Avoid migration to A55 cores.

---

### 17. CPU Pinning

Recommended:

sched_setaffinity()

Benefits:

Reduced Migration

Lower Jitter

More Predictable Timing

---

### 18. Scheduler Architecture

Default

SCHED_RR

SCHED_FIFO

Real-time scheduling allowed only after validation.

---

### 19. Real-Time Policy

Priority Range:

50–60

Validate carefully.

Incorrect priorities can destabilize systems.

---

### 20. Memory Architecture

Persistent Buffers

Buffer Reuse

Avoid Per-Frame Allocation

Minimize Fragmentation

---

### 21. Buffer Ownership

Image Buffers

Feature Buffers

Hidden State Buffers

Inference Buffers

Ownership documented.

---

### 22. NPU Architecture

Core 0

Core 1

Core 2

Independent execution units.

---

### 23. NPU Assignment

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

### 24. Core Sharing Policy

Forbidden:

Vision + Policy sharing the same NPU core.

Reason:

Latency spikes

Queue contention

---

### 25. OpenCL Architecture

loadyuv.cl

transform.cl

Remain unchanged.

OpenCL still performs preprocessing.

---

## Section B — Performance Validation

### 26. Camera Performance Validation

Measure:

Capture Latency

ISP Latency

Frame Delivery Latency

Generate:

camera_performance.json

---

### 27. VisionIPC Performance Validation

Measure:

Queue Depth

Dropped Frames

Latency

Generate:

visionipc_performance.json

---

### 28. OpenCL Validation

Measure:

loadyuv.cl

transform.cl

Execution Time

Generate:

opencl_report.json

---

### 29. Tensor Performance Validation

Measure:

Tensor Preparation Time

Buffer Reuse

Allocation Count

---

### 30. Vision Model Performance Validation

Measure:

Vision Inference

NPU Utilization

Queue Delay

---

### 31. Vision Acceptance Targets

Target:

8–15 ms

per frame

---

### 32. Policy Performance Validation

Measure:

Policy Inference

NPU Utilization

Queue Delay

---

### 33. Policy Acceptance Targets

Target:

2–8 ms

per frame

---

### 34. Combined Inference Validation

Vision
+
Policy

Target:

<20 ms

combined

---

### 35. Tinygrad Baseline Validation

Measure:

Tinygrad Vision

Tinygrad Policy

Use as regression baseline.

---

### 36. Latency Validation

Record:

Average

Median

95th Percentile

99th Percentile

Maximum

---

### 37. FPS Validation

Record:

Average FPS

Min FPS

Max FPS

95th Percentile FPS

99th Percentile FPS

---

### 38. Planner Timing Validation

Validate:

Planner Alive

Planner Frequency

Planner Jitter

Planner Latency

---

### 39. Publish Timing Validation

Validate:

modelV2 publish rate

cameraOdometry publish rate

No timing drift.

---

## Section C — Thermal & Reliability Validation

### 40. Thermal Philosophy

Performance without thermal stability is invalid.

---

### 41. Thermal Limits

CPU

<80°C

NPU

<85°C

Board

<75°C

---

### 42. Thermal Validation

30 Minutes Minimum

1 Hour Preferred

Generate:

thermal_report.json

---

### 43. Thermal Throttling Validation

Record:

Clock Reductions

Frequency Changes

Performance Drops

---

### 44. Power Validation

Measure:

Voltage

Current

Power Consumption

When available.

---

### 45. Long Duration Validation

1 Hour Minimum

4 Hours Preferred

Validate:

Latency

Memory

Temperature

FPS

---

### 46. Memory Validation

RSS

Virtual Memory

Tensor Buffers

Allocation Count

No leaks permitted.

---

### 47. Recovery Performance Validation

Runtime Restart

Camera Restart

Model Reload

Measure recovery times.

---

## Section D — AI Agent Operating Manual

### 48. Repository Discovery Workflow

Discover:

Camera

VisionIPC

OpenCL

Modeld

RKNN

Planner

Generate:

performance_analysis.json

---

### 49. Fork Adaptation Rules

Never assume:

CPU Mapping

Runtime Paths

Model Paths

Environment Variables

Discover dynamically.

---

### 50. Benchmark Workflow

Discovery
↓
Camera Benchmark
↓
OpenCL Benchmark
↓
Vision Benchmark
↓
Policy Benchmark
↓
Planner Benchmark
↓
Thermal Benchmark
↓
Reliability Benchmark

---

### 51. Optimization Workflow

Correctness
↓
Stability
↓
Latency
↓
FPS

Optimization in any other order is prohibited.

---

### 52. Reporting Requirements

Generate:

timing_report.json

latency_report.json

throughput_report.json

memory_report.json

thermal_report.json

npu_report.json

performance_analysis.json

---

### 53. Failure Modes

FPS Collapse

Thermal Throttling

NPU Contention

CPU Migration

Memory Leak

Queue Saturation

Planner Jitter

Publish Drift

---

### 54. Optimization Boundaries

Allowed:

CPU Affinity

NPU Assignment

Buffer Reuse

Scheduler Configuration

Validation Tools

Avoid:

Changing Planner Logic

Changing Controls Logic

Changing Metadata Semantics

---

### 55. Production Readiness

Required:

Latency PASS

FPS PASS

Memory PASS

Thermals PASS

Planner PASS

Recovery PASS

---

### 56. Production Gate

Deployment prohibited until:

All performance sections PASS.

---

### 57. Final Checklist

CPU Affinity
[ ]

NPU Assignment
[ ]

Camera
[ ]

VisionIPC
[ ]

OpenCL
[ ]

Vision
[ ]

Policy
[ ]

Latency
[ ]

FPS
[ ]

Memory
[ ]

Thermals
[ ]

Planner
[ ]

Recovery
[ ]

Result:

PASS / FAIL

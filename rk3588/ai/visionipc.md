# VISIONIPC.MD (Authoritative Version)

# Engineering Specification + Validation Specification + Production Specification + AI Agent Operating Manual

Version: 3.0

Target Hardware:

* RK3588
* Orange Pi 5
* Orange Pi 5 Plus

Target Camera:

* IMX415

Target Runtime:

* VisionIPC
* DMA-BUF
* EGLImage
* OpenCL
* RKNN

---

# Section A — What VisionIPC Is

## 1. Purpose

VisionIPC is the transport layer used by OpenPilot.

Its job is:

```text
Move camera frames
from producer
to consumer
```

Example:

```text
camerad
    ↓
VisionIPC
    ↓
modeld
```

VisionIPC does NOT:

```text
Run inference
Parse metadata
Control vehicle
Plan trajectory
```

It only transports frames.

---

## 2. Why VisionIPC Exists

Without VisionIPC:

```text
Camera
  ↓
Shared Memory
  ↓
Manual Synchronization
  ↓
Multiple Copies
```

Problems:

```text
high latency
frame corruption
ownership confusion
```

VisionIPC solves this.

---

## 3. Production Goal

VisionIPC must provide:

```text
Low latency
Frame ordering
Timestamp consistency
Buffer ownership
Replay compatibility
```

---

# Section B — Production Architecture

## 4. Complete Flow

```text
IMX415
   ↓
RKISP
   ↓
NV12 DMA-BUF
   ↓
VisionIPC Server
   ↓
VisionIPC Client
   ↓
modeld
```

---

## 5. UI Flow

```text
NV12 DMA-BUF
   ↓
VisionIPC
   ↓
EGLImage
   ↓
GPU Texture
   ↓
UI Preview
```

---

## 6. Logging Flow

```text
VisionIPC
   ↓
loggerd
   ↓
route logs
```

---

# Section C — Ownership Model

## 7. Producer

Usually:

```text
camerad
```

owns:

```text
capture
buffer creation
timestamp generation
```

---

## 8. Consumer

Usually:

```text
modeld
```

owns:

```text
frame consumption
tensor generation
```

---

## 9. Ownership Rule

```text
One producer

Many consumers
```

Allowed.

---

## 10. Forbidden Ownership

```text
Multiple producers
same stream
```

Forbidden.

---

# Section D — Stream Architecture

## 11. Road Camera Stream

Example:

```text
VISION_STREAM_ROAD
```

Contains:

```text
road-facing frames
```

---

## 12. Driver Stream

Example:

```text
VISION_STREAM_DRIVER
```

Contains:

```text
driver monitoring frames
```

---

## 13. Wide Stream

Example:

```text
VISION_STREAM_WIDE
```

Contains:

```text
wide camera frames
```

---

## 14. Single Camera Deployment

For IMX415-only deployment:

```text
ROAD stream enabled

DRIVER disabled

WIDE disabled
```

Preferred.

---

# Section E — Buffer Lifecycle

## 15. Standard Lifecycle

```text
Camera Capture
    ↓
Buffer Allocation
    ↓
VisionIPC Publish
    ↓
Consumer Receive
    ↓
Processing
    ↓
Release
```

---

## 16. DMA-BUF Lifecycle

```text
RKISP
   ↓
DMA-BUF FD
   ↓
VisionIPC
   ↓
modeld
```

No CPU copy.

---

## 17. CPU Copy Lifecycle

```text
RKISP
   ↓
NV12
   ↓
CPU memcpy
   ↓
VisionIPC
```

Allowed.

Not preferred.

---

# Section F — Timestamp System

## 18. Purpose

Every frame needs:

```text
capture timestamp
```

---

## 19. Timestamp Flow

```text
Camera
   ↓
timestamp generated
   ↓
VisionIPC publish
   ↓
modeld receive
```

---

## 20. Rule

Timestamps must be:

```text
monotonic
```

Never:

```text
decreasing
```

---

## 21. Validation

Verify:

```text
Frame N+1 > Frame N
```

Always.

---

# Section G — DMA-BUF Integration

## 22. Why DMA-BUF

Normal path:

```text
Camera
 ↓
Copy
 ↓
VisionIPC
```

DMA-BUF:

```text
Camera
 ↓
Shared FD
 ↓
VisionIPC
```

---

## 23. Benefits

```text
Lower latency
Lower CPU usage
Less memory traffic
```

---

## 24. Production Target

Preferred:

```text
DMA-BUF enabled
```

---

# Section H — EGLImage Integration

## 25. Purpose

Display camera preview without:

```text
RGB conversion
```

---

## 26. Flow

```text
DMA-BUF
   ↓
EGLImage
   ↓
GPU Texture
   ↓
OpenGL
   ↓
UI
```

---

## 27. Benefit

Reduces:

```text
CPU usage
preview latency
```

---

# Section I — modeld Integration

## 28. Receive Path

```text
VisionIPC
   ↓
recv()
   ↓
NV12 frame
```

---

## 29. Tensor Flow

```text
NV12
   ↓
loadyuv.cl
   ↓
transform.cl
   ↓
tensor
```

---

## 30. Rule

VisionIPC transports frames.

VisionIPC never generates tensors.

---

# Section J — Replay Integration

## 31. Replay Flow

```text
route log
   ↓
replay
   ↓
VisionIPC
   ↓
modeld
```

---

## 32. Requirement

Replay must behave like:

```text
live camera
```

---

## 33. Validation

Replay output:

```text
must match
live pipeline
```

---

# Section K — Performance Targets

## 34. Standard Path

```text
RKISP
 ↓
VisionIPC
 ↓
modeld
```

Target:

```text
1–3 ms
```

---

## 35. DMA-BUF Path

Target:

```text
<1 ms
```

Typical:

```text
0.3–0.8 ms
```

---

## 36. End-to-End Target

```text
Camera → modelV2

<30 ms
```

Preferred:

```text
<25 ms
```

---

# Section L — Validation Specification

## 37. Stream Validation

Verify:

```text
frames arrive
```

---

## 38. Timestamp Validation

Verify:

```text
timestamps increase
```

---

## 39. Ordering Validation

Verify:

```text
no reordering
```

---

## 40. Drop Validation

Verify:

```text
no excessive drops
```

---

## 41. Replay Validation

Verify:

```text
replay works
```

---

# Section M — Failure Modes

## 42. Buffer Corruption

Symptoms:

```text
green image
purple image
split frame
```

---

## 43. Timestamp Corruption

Symptoms:

```text
negative latency
out-of-order frames
```

---

## 44. Ownership Bugs

Symptoms:

```text
random crashes
stale frames
```

---

# Section N — AI Agent Rules

## 45. Must Understand

Before modifying:

```text
stream types
timestamps
buffer ownership
DMA-BUF
EGLImage
```

---

## 46. Must Not

Never:

```text
change stream semantics

change timestamp semantics

change ownership semantics
```

---

## 47. Always Validate

After modification:

```text
stream validation

timestamp validation

replay validation

performance validation
```

---

# Section O — Production Deployment

## 48. Recommended Pipeline

```text
IMX415
 ↓
RKISP
 ↓
NV12 DMA-BUF
 ↓
VisionIPC
 ├── modeld
 └── EGLImage Preview
```

---

## 49. Expected Timing

```text
VisionIPC:
0.3–1.0 ms

Camera → modelV2:
15–30 ms

Camera → UI:
20–35 ms
```

---

## 50. Final Production Certification

VisionIPC PASS when:

```text
Frames Valid
Timestamps Valid
Ordering Valid
Replay Valid
Performance Valid
DMA-BUF Valid
```

Result:

```text
PRODUCTION READY
```

# CAMERA_PIPELINE.MD (Authoritative Version)

# Architecture Diagram + Validation Diagram + Production Diagram + AI Agent Operating Diagram

Version: 3.0

Target Hardware:

* RK3588
* Orange Pi 5

Target Camera:

* IMX415

Target Pipeline:

* RKISP
* V4L2
* NV12
* DMA-BUF
* VisionIPC
* EGLImage
* OpenCL
* RKNN
* modelV2
* Planner

---

# Section A — Production Camera Pipeline

## 1. Full Production Pipeline

```text
IMX415
  ↓
MIPI CSI-2
  ↓
RK3588 CSI Receiver
  ↓
RKISP
  ↓
V4L2
  ↓
NV12 DMA-BUF
  ├──────────────────────────────┬──────────────────────────────┐
  │                              │                              │
  ▼                              ▼                              ▼
VisionIPC                     EGLImage                       loggerd
  ↓                              ↓
modeld                         Mali GPU Texture               route logs
  ↓                              ↓
loadyuv.cl                     UI camera preview
  ↓                              ↓
transform.cl                   OpenGL overlay
  ↓                              ↓
model tensor                   display
  ↓
RKNN Vision Core 0
  ↓
RKNN Policy Core 1
  ↓
modelV2 / msgq
  ↓
planner
  ↓
controlsd
```

---

# Section B — Baseline Pipeline

## 2. Safe Baseline Path

```text
IMX415
  ↓
RKISP / V4L2
  ↓
NV12
  ↓
VisionIPC
  ↓
loadyuv.cl + transform.cl
  ↓
model tensor
  ↓
RKNN Vision Core 0
  ↓
RKNN Policy Core 1
  ↓
modelV2
  ↓
planner
```

Expected:

```text
Camera → modelV2: 18–30 ms
Camera → UI:      30–45 ms
```

---

# Section C — DMA-BUF Optimized Pipeline

## 3. DMA-BUF Path

```text
IMX415
  ↓
RKISP / V4L2
  ↓
NV12 DMA-BUF
  ↓
VisionIPC zero-copy
  ↓
OpenCL preprocessing
  ↓
RKNN
  ↓
modelV2
```

Expected:

```text
Camera → modelV2: 15–27 ms
```

---

# Section D — GPU Zero-Copy UI Pipeline

## 4. EGLImage Preview Path

```text
NV12 DMA-BUF
  ↓
EGLImage
  ↓
Mali GPU Texture
  ↓
OpenGL Camera Preview
  ↓
Path / Lane Overlay
  ↓
Display
```

Expected:

```text
Camera → visible UI: 20–35 ms
```

---

# Section E — Forbidden Slow Pipeline

## 5. Avoid This Path

```text
IMX415
  ↓
OpenCV
  ↓
BGR
  ↓
BGR → NV12
  ↓
numpy copy
  ↓
RKNN
```

Reason:

```text
High CPU load
Extra memory copies
Higher latency
Possible 50+ ms pipeline
```

---

# Section F — Ownership Diagram

```text
camera.md
  owns:
    IMX415
    RKISP
    V4L2
    NV12
    DMA-BUF export
    intrinsics
    warp

visionipc.md
  owns:
    frame transport
    stream identity
    timestamps
    buffer ownership

modeld.md
  owns:
    loadyuv.cl
    transform.cl
    tensor generation
    model orchestration

rknn.md
  owns:
    RKNN runtime
    NPU core assignment

performance.md
  owns:
    timing
    latency
    FPS
    resource measurement

deployment.md
  owns:
    production release
```

---

# Section G — Validation Flow Diagram

```text
Sensor detected
  ↓
MIPI stable
  ↓
RKISP streaming
  ↓
V4L2 NV12 valid
  ↓
DMA-BUF valid
  ↓
VisionIPC valid
  ↓
OpenCL tensor valid
  ↓
RKNN output valid
  ↓
modelV2 valid
  ↓
planner valid
  ↓
production ready
```

---

# Section H — AI Agent Workflow Diagram

```text
Discover camera
  ↓
Detect V4L2 format
  ↓
Validate NV12 layout
  ↓
Validate DMA-BUF
  ↓
Validate VisionIPC
  ↓
Validate tensor
  ↓
Validate RKNN
  ↓
Validate planner
  ↓
Generate reports
```

---

# Section I — Final Production Target

```text
IMX415
  ↓
RKISP
  ↓
NV12 DMA-BUF
  ├→ VisionIPC → OpenCL → RKNN Vision Core 0 → RKNN Policy Core 1 → modelV2 → planner
  └→ EGLImage → Mali GPU → UI preview + overlay
```

Result target:

```text
Camera → modelV2: <30 ms
Camera → UI:      <35 ms
```

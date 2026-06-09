# RKNN_PIPELINE.MD (Authoritative Version)

# Architecture Diagram + Runtime Diagram + Validation Diagram + Production Diagram + AI Agent Operating Diagram

Version: 3.0

Target Hardware:

* RK3588
* Orange Pi 5

Target Runtime:

* RKNN Vision Core 0
* RKNN Policy Core 1
* Tinygrad fallback
* OpenCL preprocessing
* msgq / cereal

---

# Section A — RKNN Production Pipeline

```text
IMX415
  ↓
RKISP / V4L2
  ↓
NV12 DMA-BUF
  ↓
VisionIPC
  ↓
modeld
  ↓
loadyuv.cl + transform.cl
  ↓
model tensor
  ↓
layout validation
  ↓
optional NCHW → NHWC
  ↓
RKNN Vision Model
  ↓
NPU Core 0
  ↓
vision outputs
  ↓
feature buffer / hidden state
  ↓
policy input preparation
  ↓
RKNN Policy Model
  ↓
NPU Core 1
  ↓
policy outputs
  ↓
metadata parser
  ↓
modelV2 / msgq
  ↓
plannerd
```

---

# Section B — NPU Core Assignment

```text
RK3588 NPU
  ├── Core 0
  │     └── driving_vision.rknn
  │
  ├── Core 1
  │     └── driving_policy.rknn
  │
  └── Core 2
        └── reserved / future models
```

Rule:

```text
Do not use AUTO core assignment for production.
Do not run vision and policy on the same NPU core.
```

---

# Section C — Runtime Abstraction

```text
modeld
  ↓
ModelRunner interface
  ↓
RKNNRunner
  ↓
RKNNLite / RKNN Runtime
  ↓
NPU Core
```

Fallback:

```text
modeld
  ↓
ModelRunner interface
  ↓
TinygradRunner
  ↓
Mali/OpenCL or CPU backend
```

---

# Section D — Vision Model Path

```text
image tensor
  ↓
input validation
  ↓
layout conversion if required
  ↓
RKNN Vision Core 0
  ↓
raw outputs
  ↓
metadata output map
  ↓
features
hidden state
path-related outputs
```

Expected latency:

```text
8–12 ms
```

---

# Section E — Policy Model Path

```text
features / hidden state
  ↓
desire
  ↓
traffic convention
  ↓
lateral context
  ↓
input validation
  ↓
RKNN Policy Core 1
  ↓
raw outputs
  ↓
metadata output map
  ↓
trajectory / policy outputs
```

Expected latency:

```text
2–5 ms
```

---

# Section F — Layout Handling

Tinygrad common layout:

```text
NCHW
1×12×128×256
```

RKNN possible layout:

```text
NHWC
1×128×256×12
```

Conversion boundary:

```text
OpenCL tensor
  ↓
layout validation
  ↓
transpose only if RKNN requires NHWC
  ↓
RKNN input
```

Rule:

```text
Never assume layout.
Validate from metadata and RKNN input details.
```

---

# Section G — Metadata Flow

```text
RKNN raw outputs
  ↓
metadata definitions
  ↓
output names
  ↓
slice definitions
  ↓
semantic outputs
  ↓
modelV2
```

Rule:

```text
Never hardcode outputs[0], outputs[1], outputs[2].
```

---

# Section H — Hidden State Flow

```text
Frame N
  ↓
Vision inference
  ↓
hidden state / feature buffer update
  ↓
Policy inference
  ↓
store updated state
  ↓
Frame N+1
  ↓
reuse previous state
```

Rule:

```text
Do not reset hidden state every frame.
```

---

# Section I — Validation Pipeline

```text
same input tensor
  ├── Tinygrad reference
  │       ↓
  │   reference outputs
  │
  └── RKNN candidate
          ↓
      RKNN outputs

compare:
  MAE
  Relative MAE
  Correlation
  Cosine Similarity
```

Acceptance:

```text
Correlation > 0.995
Preferred > 0.999
```

---

# Section J — Performance Timing Diagram

```text
T0 camera capture
  ↓
T1 VisionIPC receive
  ↓
T2 OpenCL done
  ↓
T3 RKNN vision done
  ↓
T4 RKNN policy done
  ↓
T5 modelV2 published
```

Target:

```text
T5 - T0 < 30 ms
```

Expected:

```text
Baseline: 18–30 ms
DMA-BUF: 15–27 ms
```

---

# Section K — Failure Diagram

```text
wrong layout
  ↓
bad RKNN tensor
  ↓
wrong vision output
  ↓
wrong modelV2
  ↓
bad planner behavior
```

or:

```text
hidden state reset
  ↓
unstable temporal output
  ↓
planner jitter
```

---

# Section L — AI Agent Workflow

```text
discover models
  ↓
discover metadata
  ↓
discover RKNN input layout
  ↓
validate tensors
  ↓
load RKNN vision on Core 0
  ↓
load RKNN policy on Core 1
  ↓
compare Tinygrad vs RKNN
  ↓
validate modelV2
  ↓
validate planner
  ↓
generate reports
```

---

# Section M — Forbidden Flow

```text
VisionIPC NV12 frame
  ↓
RKNN directly
```

Forbidden because:

```text
RKNN expects model tensor, not camera frame.
```

Also forbidden:

```text
Removing Tinygrad fallback
Hardcoding output indices
Changing planner semantics
Changing controls semantics
Ignoring metadata
Skipping multi-frame validation
```

---

# Section N — Final Production Target

```text
NV12 DMA-BUF
  ↓
VisionIPC
  ↓
OpenCL preprocessing
  ↓
RKNN Vision Core 0
  ↓
RKNN Policy Core 1
  ↓
modelV2/msgq
  ↓
planner
```

Production target:

```text
Camera → modelV2: <30 ms
Vision RKNN:       8–12 ms
Policy RKNN:       2–5 ms
Planner stable:    PASS
```

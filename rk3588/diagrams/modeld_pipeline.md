# MODELD_PIPELINE.MD (Authoritative Version)

# Architecture Diagram + Runtime Diagram + Validation Diagram + AI Agent Operating Diagram

Version: 3.0

Target Hardware:

* RK3588
* Orange Pi 5

Target Runtime:

* OpenCL preprocessing
* RKNN Vision Core 0
* RKNN Policy Core 1
* msgq / cereal

---

# Section A — Full modeld Pipeline

```text
VisionIPC road camera frame
  ↓
modeld frame receive
  ↓
timestamp validation
  ↓
NV12 layout validation
  ↓
loadyuv.cl
  ↓
transform.cl
  ↓
DrivingModelFrame.prepare()
  ↓
image tensors
  ↓
metadata input validation
  ↓
RKNN Vision Core 0
  ↓
vision outputs
  ↓
feature buffer / hidden state update
  ↓
policy input preparation
  ↓
RKNN Policy Core 1
  ↓
policy outputs
  ↓
metadata output parsing
  ↓
modelV2 construction
  ↓
msgq / cereal publish
  ↓
plannerd
```

---

# Section B — Baseline Runtime Path

```text
NV12 frame
  ↓
OpenCL preprocessing
  ↓
NCHW tensor
  ↓
Tinygrad Vision
  ↓
Tinygrad Policy
  ↓
modelV2
```

Used for:

```text
reference
debugging
fallback
regression comparison
```

---

# Section C — RKNN Runtime Path

```text
NV12 frame
  ↓
OpenCL preprocessing
  ↓
NCHW tensor
  ↓
optional NCHW → NHWC conversion
  ↓
RKNN Vision Core 0
  ↓
features / hidden state
  ↓
RKNN Policy Core 1
  ↓
modelV2
```

Target:

```text
Camera → modelV2: 18–30 ms
With DMA-BUF:     15–27 ms
```

---

# Section D — Tensor Ownership Diagram

```text
camera.md
  owns:
    camera geometry
    intrinsics
    warp source

visionipc.md
  owns:
    frame transport
    timestamp
    frame identity

modeld.md
  owns:
    preprocessing
    tensor generation
    state update
    output parsing
    modelV2 publish

model_metadata.md
  owns:
    input names
    output names
    shapes
    slices
    semantics

rknn.md
  owns:
    NPU execution
    runtime validation
```

---

# Section E — Hidden State Flow

```text
Frame N
  ↓
Vision inference
  ↓
hidden state / features update
  ↓
Policy inference
  ↓
Store state
  ↓
Frame N+1 reuses state
```

Rule:

```text
Never reset hidden state every frame.
```

---

# Section F — Metadata Parsing Flow

```text
RKNN raw outputs
  ↓
metadata output map
  ↓
slice definitions
  ↓
path
lane lines
road edges
lead vehicles
pose
policy trajectory
  ↓
modelV2 fields
```

Rule:

```text
Never hardcode output indices.
```

---

# Section G — msgq Publish Flow

```text
modeld
  ↓
modelV2
  ↓
cereal serialization
  ↓
msgq publish
  ↓
plannerd subscribe
  ↓
planner update
```

---

# Section H — Validation Flow

```text
Frame received
  ↓
tensor dumped
  ↓
tensor stats validated
  ↓
Tinygrad output generated
  ↓
RKNN output generated
  ↓
outputs compared
  ↓
modelV2 validated
  ↓
planner validated
```

Metrics:

```text
MAE
Relative MAE
Correlation
Cosine similarity
```

Acceptance:

```text
Correlation > 0.995
Preferred > 0.999
```

---

# Section I — Performance Flow

```text
T0 camera timestamp
  ↓
T1 modeld receive
  ↓
T2 OpenCL done
  ↓
T3 vision RKNN done
  ↓
T4 policy RKNN done
  ↓
T5 modelV2 published
```

Target:

```text
T5 - T0 < 30 ms
```

---

# Section J — AI Agent Workflow

```text
Discover modeld
  ↓
Discover metadata
  ↓
Discover tensor shapes
  ↓
Preserve OpenCL preprocessing
  ↓
Add RKNN runner
  ↓
Validate Tinygrad vs RKNN
  ↓
Validate modelV2
  ↓
Validate planner
  ↓
Generate reports
```

---

# Section K — Forbidden Flow

```text
VisionIPC frame
  ↓
direct RKNN input
```

Forbidden because:

```text
VisionIPC frame is not model tensor.
```

Also forbidden:

```text
hardcoded outputs[0]
hardcoded NHWC/NCHW
planner modification for runtime bug
controlsd modification for perception bug
```

---

# Section L — Final Production Target

```text
IMX415
  ↓
RKISP
  ↓
NV12 DMA-BUF
  ↓
VisionIPC
  ↓
modeld
  ↓
loadyuv.cl + transform.cl
  ↓
RKNN Vision Core 0
  ↓
RKNN Policy Core 1
  ↓
modelV2/msgq
  ↓
planner
```

Result target:

```text
Camera → modelV2: <30 ms
Planner receives stable modelV2 at target rate
```

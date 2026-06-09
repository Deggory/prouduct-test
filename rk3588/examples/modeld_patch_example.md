# MODELD_PATCH_EXAMPLE.MD (Authoritative Version)

# Engineering Example + Patch Example + Validation Example + Production Example + AI Agent Operating Example

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

* Tinygrad
* RKNN

Purpose:

Demonstrate a complete production-quality modeld migration from Tinygrad inference to RKNN inference while preserving:

* VisionIPC
* OpenCL preprocessing
* metadata semantics
* planner interface
* modelV2 schema

---

# Section A — Original Architecture

## 1. Baseline OpenPilot modeld

Pipeline:

```text
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
Tensor
↓
Tinygrad Vision
↓
Tinygrad Policy
↓
modelV2
↓
Planner
```

---

## 2. Baseline Responsibilities

modeld owns:

* frame acquisition
* preprocessing
* tensor generation
* inference
* metadata parsing
* message publication

Planner owns:

* trajectory generation

Controls own:

* vehicle commands

---

## 3. Migration Goal

Replace:

```text
Tinygrad inference
```

with:

```text
RKNN inference
```

while keeping:

```text
VisionIPC
OpenCL
Tensor generation
Metadata parser
Planner interface
```

unchanged.

---

# Section B — Discovery Example

## 4. Repository Discovery

AI agent discovers:

```text
selfdrive/modeld/modeld.py

selfdrive/modeld/
models/
metadata/
transforms/

msgq/
cereal/
```

---

## 5. Runtime Discovery

Detect:

```python
USE_RKNN = os.getenv(
    "OPENPILOT_MODELD_BACKEND",
    "auto"
)
```

---

## 6. Metadata Discovery

Locate:

```text
driving_vision_metadata.json
driving_policy_metadata.json
```

Generate:

```text
metadata_inventory.json
```

---

# Section C — Backend Selection Patch

## 7. Original

Example:

```python
vision_model = TinygradVisionModel(...)
policy_model = TinygradPolicyModel(...)
```

---

## 8. New Design

Introduce:

```python
ModelRunner
```

abstraction.

---

## 9. Patch Example

```diff
- vision_model = TinygradVisionModel(...)
- policy_model = TinygradPolicyModel(...)

+ backend = select_backend()
+
+ if backend == "rknn":
+   vision_model = RKNNVisionRunner(...)
+   policy_model = RKNNPolicyRunner(...)
+ else:
+   vision_model = TinygradVisionModel(...)
+   policy_model = TinygradPolicyModel(...)
```

---

## 10. Validation

Verify:

```text
Tinygrad path still works
RKNN path loads
```

---

# Section D — RKNN Runner Integration

## 11. Add Runner

New file:

```text
selfdrive/modeld/runners/rknn_runner.py
```

---

## 12. Vision Core Assignment

```python
vision_runner = RKNNRunner(
    model_path=VISION_MODEL,
    core_id=0
)
```

---

## 13. Policy Core Assignment

```python
policy_runner = RKNNRunner(
    model_path=POLICY_MODEL,
    core_id=1
)
```

---

## 14. Production Rule

Never place both models on same NPU core.

Preferred:

```text
Vision → Core 0
Policy → Core 1
```

---

# Section E — Tensor Preservation Example

## 15. Original Tensor Path

```text
NV12
↓
loadyuv.cl
↓
transform.cl
↓
Tensor
```

---

## 16. Patch Rule

Do not modify:

```text
loadyuv.cl
transform.cl
warp generation
```

---

## 17. Validation

Verify:

```python
tensor.shape
tensor.dtype
tensor.mean()
tensor.std()
```

Before and after patch.

---

# Section F — NHWC Migration Example

## 18. Tinygrad Format

Example:

```text
NCHW

1×12×128×256
```

---

## 19. RKNN Format

Example:

```text
NHWC

1×128×256×12
```

---

## 20. Conversion Patch

```python
vision_tensor = np.transpose(
    vision_tensor,
    (0,2,3,1)
)
```

---

## 21. Validation

Verify:

```text
Shape
Layout
Statistics
```

Match reference.

---

# Section G — Inference Patch Example

## 22. Original

```python
vision_output = vision_model.run(
    vision_tensor
)
```

---

## 23. RKNN

```python
vision_output = vision_runner.infer({
    "img": vision_tensor
})
```

---

## 24. Policy

```python
policy_output = policy_runner.infer({
    "features_buffer": features,
    "desire": desire
})
```

---

## 25. Validation

Verify:

```text
Output count
Output shape
Output dtype
```

---

# Section H — Metadata Patch Example

## 26. Original

Hardcoded indices:

```python
path = outputs[0]
lane = outputs[1]
```

---

## 27. Correct Patch

```python
path = metadata.get_output(
    outputs,
    "path"
)

lane = metadata.get_output(
    outputs,
    "lane"
)
```

---

## 28. Production Rule

Never hardcode output indices.

---

# Section I — modelV2 Preservation Example

## 29. Original

```python
msg.modelV2.path = path
msg.modelV2.laneLines = lane_lines
```

---

## 30. Patch Rule

No schema changes.

No message changes.

No planner changes.

---

## 31. Validation

Verify:

```text
modelV2 schema identical
```

---

# Section J — Error Handling Patch

## 32. Runtime Failure

```python
try:
    outputs = runner.infer(...)
except Exception:
    ...
```

---

## 33. Recovery

Allowed:

```text
Reload RKNN model
Restart RKNN runtime
Fallback Tinygrad
```

---

## 34. Forbidden

Never:

```text
Publish invalid outputs
```

---

# Section K — Validation Example

## 35. Tensor Validation

Generate:

```text
tensor_validation.json
```

---

## 36. Vision Validation

Compare:

```text
Tinygrad
RKNN
```

Metrics:

```text
Correlation
Cosine Similarity
MAE
```

---

## 37. Acceptance

```text
Correlation > 0.995

Preferred > 0.999
```

---

## 38. Policy Validation

Generate:

```text
policy_validation.json
```

---

## 39. Multi-Frame Validation

Minimum:

```text
100 frames
```

Preferred:

```text
1000 frames
```

---

# Section L — Performance Example

## 40. Baseline

Tinygrad:

```text
Vision:
50–150 ms

Policy:
20–40 ms
```

---

## 41. RKNN

Vision:

```text
8–12 ms
```

Policy:

```text
2–5 ms
```

---

## 42. Pipeline

Camera → modelV2

```text
18–30 ms
```

With DMA-BUF:

```text
15–27 ms
```

---

# Section M — Patch Report Example

## 43. Generated Report

```text
Patch:
RKNN modeld integration

Files Modified:
modeld.py

Files Added:
rknn_runner.py

Planner Modified:
NO

Schema Modified:
NO

Runtime:
RKNN

Status:
PASS
```

---

# Section N — Deployment Example

## 44. Production Configuration

Environment:

```bash
OPENPILOT_MODELD_BACKEND=rknn

RKNN_VISION_CORE=0

RKNN_POLICY_CORE=1

RK_USE_DMABUF=1

RK_USE_EGLIMAGE=1
```

---

## 45. Validation Artifacts

Required:

```text
tensor_validation.json

vision_validation.json

policy_validation.json

latency_report.json

deployment_report.json
```

---

## 46. Production Checklist

Vision PASS

[ ]

Policy PASS

[ ]

Metadata PASS

[ ]

Planner PASS

[ ]

Replay PASS

[ ]

Performance PASS

[ ]

Recovery PASS

[ ]

---

# Section O — AI Agent Operating Example

## 47. Discovery Workflow

```text
Discover modeld
↓
Discover Metadata
↓
Discover Runtime
↓
Generate Patch
↓
Generate Validation
↓
Generate Performance Report
↓
Deploy
```

---

## 48. Patch Workflow

```text
Tinygrad
↓
RKNN Runner
↓
Validation
↓
Production
```

---

## 49. Agent Rules

Always:

* preserve OpenCL
* preserve metadata
* preserve planner interface
* preserve modelV2

Never:

* modify planner semantics
* modify controls semantics
* hardcode tensor indices
* remove Tinygrad fallback

---

# Final Example Result

Platform:

Orange Pi 5

Camera:

IMX415

Runtime:

RKNN

Vision Core:

0

Policy Core:

1

Camera → modelV2:

22 ms

Camera → UI:

28 ms

Planner Compatibility:

PASS

Replay Compatibility:

PASS

Production Ready:

YES

Result:

PASS

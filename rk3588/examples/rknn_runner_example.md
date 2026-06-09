# RKNN_RUNNER_EXAMPLE.MD (Authoritative Version)

# Engineering Example + Runtime Example + Validation Example + Production Example + AI Agent Operating Example

Version: 3.0

Target Hardware:

* RK3588
* RK3588S
* Orange Pi 5
* Orange Pi 5 Plus

Target Runtime:

* RKNNLite
* RKNN Toolkit Lite2

Target Models:

* Vision Model
* Policy Model

Target Pipeline:

IMX415
↓
RKISP
↓
NV12 DMA-BUF
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
modelV2/msgq
↓
Planner

---

# Section A — Objective

## 1. Purpose

This document provides an example RKNNRunner design for OpenPilot-derived forks.

The example demonstrates:

* safe RKNN loading
* runtime discovery
* metadata validation
* input validation
* output validation
* NPU core binding
* Tinygrad fallback compatibility
* production error handling
* AI-agent patch guidance

---

## 2. Design Rule

modeld must not call RKNN directly.

Correct:

```text
modeld
↓
ModelRunner
↓
RKNNRunner
↓
RKNNLite
```

Incorrect:

```text
modeld
↓
RKNNLite directly
```

---

# Section B — Runtime Architecture

## 3. Runner Interface

Recommended interface:

```python
class ModelRunner:
    def initialize(self) -> None:
        raise NotImplementedError

    def validate(self) -> None:
        raise NotImplementedError

    def infer(self, inputs: dict[str, object]) -> dict[str, object]:
        raise NotImplementedError

    def shutdown(self) -> None:
        raise NotImplementedError
```

---

## 4. RKNNRunner Lifecycle

Lifecycle:

```text
Construct
↓
Discover Runtime
↓
Load Model
↓
Initialize Runtime
↓
Validate Metadata
↓
Infer
↓
Shutdown
```

---

## 5. Runtime Ownership

RKNNRunner owns:

* RKNNLite object
* model path
* NPU core selection
* runtime initialization
* input validation
* output validation
* inference timing

RKNNRunner does not own:

* camera frames
* VisionIPC
* OpenCL preprocessing
* metadata semantics
* planner messages

---

# Section C — Example RKNNRunner

## 6. Python Example

```python
from __future__ import annotations

import os
import time
import json
import hashlib
from pathlib import Path
from typing import Any

import numpy as np


class RKNNRunnerError(RuntimeError):
    pass


class RKNNRunner:
    def __init__(
        self,
        model_path: str | Path,
        model_name: str,
        core_id: int,
        expected_inputs: dict[str, tuple[int, ...]] | None = None,
        expected_outputs: dict[str, tuple[int, ...]] | None = None,
        nhwc_inputs: set[str] | None = None,
    ) -> None:
        self.model_path = Path(model_path)
        self.model_name = model_name
        self.core_id = core_id
        self.expected_inputs = expected_inputs or {}
        self.expected_outputs = expected_outputs or {}
        self.nhwc_inputs = nhwc_inputs or set()
        self.rknn = None
        self.initialized = False
        self.last_latency_ms: float | None = None

    def initialize(self) -> None:
        self._validate_model_file()
        RKNNLite = self._import_runtime()
        self.rknn = RKNNLite()

        ret = self.rknn.load_rknn(str(self.model_path))
        if ret != 0:
            raise RKNNRunnerError(f"{self.model_name}: failed to load RKNN model: {ret}")

        core_mask = self._core_mask(RKNNLite, self.core_id)
        ret = self.rknn.init_runtime(core_mask=core_mask)
        if ret != 0:
            raise RKNNRunnerError(f"{self.model_name}: failed to init runtime: {ret}")

        self.initialized = True

    def validate(self) -> None:
        if not self.initialized:
            raise RKNNRunnerError(f"{self.model_name}: runtime not initialized")

        self._write_runtime_report()

    def infer(self, inputs: dict[str, np.ndarray]) -> list[np.ndarray]:
        if not self.initialized or self.rknn is None:
            raise RKNNRunnerError(f"{self.model_name}: infer called before initialize")

        ordered_inputs = self._prepare_inputs(inputs)

        start = time.monotonic()
        outputs = self.rknn.inference(inputs=ordered_inputs)
        end = time.monotonic()

        self.last_latency_ms = (end - start) * 1000.0

        if outputs is None:
            raise RKNNRunnerError(f"{self.model_name}: RKNN inference returned None")

        validated = self._validate_outputs(outputs)
        return validated

    def shutdown(self) -> None:
        if self.rknn is not None:
            self.rknn.release()
        self.rknn = None
        self.initialized = False

    def _validate_model_file(self) -> None:
        if not self.model_path.exists():
            raise RKNNRunnerError(f"{self.model_name}: missing model {self.model_path}")

        if not self.model_path.is_file():
            raise RKNNRunnerError(f"{self.model_name}: not a file {self.model_path}")

        if self.model_path.stat().st_size <= 0:
            raise RKNNRunnerError(f"{self.model_name}: empty model {self.model_path}")

    def _import_runtime(self) -> Any:
        try:
            from rknnlite.api import RKNNLite
        except Exception as e:
            raise RKNNRunnerError(f"{self.model_name}: cannot import RKNNLite: {e}") from e
        return RKNNLite

    def _core_mask(self, RKNNLite: Any, core_id: int) -> int:
        if core_id == 0:
            return RKNNLite.NPU_CORE_0
        if core_id == 1:
            return RKNNLite.NPU_CORE_1
        if core_id == 2:
            return RKNNLite.NPU_CORE_2
        raise RKNNRunnerError(f"{self.model_name}: invalid NPU core {core_id}")

    def _prepare_inputs(self, inputs: dict[str, np.ndarray]) -> list[np.ndarray]:
        ordered: list[np.ndarray] = []

        for name, expected_shape in self.expected_inputs.items():
            if name not in inputs:
                raise RKNNRunnerError(f"{self.model_name}: missing input {name}")

            arr = inputs[name]

            if not isinstance(arr, np.ndarray):
                raise RKNNRunnerError(f"{self.model_name}: input {name} is not ndarray")

            if tuple(arr.shape) != tuple(expected_shape):
                raise RKNNRunnerError(
                    f"{self.model_name}: input {name} shape mismatch: "
                    f"got {arr.shape}, expected {expected_shape}"
                )

            if name in self.nhwc_inputs:
                arr = self._nchw_to_nhwc(arr, name)

            ordered.append(np.ascontiguousarray(arr))

        return ordered

    def _nchw_to_nhwc(self, arr: np.ndarray, name: str) -> np.ndarray:
        if arr.ndim != 4:
            raise RKNNRunnerError(f"{self.model_name}: cannot convert {name}, rank != 4")

        return np.transpose(arr, (0, 2, 3, 1))

    def _validate_outputs(self, outputs: list[np.ndarray]) -> list[np.ndarray]:
        if not isinstance(outputs, list):
            raise RKNNRunnerError(f"{self.model_name}: outputs not list")

        if self.expected_outputs and len(outputs) != len(self.expected_outputs):
            raise RKNNRunnerError(
                f"{self.model_name}: output count mismatch: "
                f"got {len(outputs)}, expected {len(self.expected_outputs)}"
            )

        for i, output in enumerate(outputs):
            if not isinstance(output, np.ndarray):
                raise RKNNRunnerError(f"{self.model_name}: output {i} is not ndarray")

            if not np.all(np.isfinite(output)):
                raise RKNNRunnerError(f"{self.model_name}: output {i} contains non-finite values")

        return outputs

    def _write_runtime_report(self) -> None:
        report = {
            "model_name": self.model_name,
            "model_path": str(self.model_path),
            "sha256": self._sha256(self.model_path),
            "core_id": self.core_id,
            "initialized": self.initialized,
        }

        out = Path("/tmp") / f"{self.model_name}_rknn_runtime_report.json"
        out.write_text(json.dumps(report, indent=2))

    def _sha256(self, path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
```

---

# Section D — Vision Runner Example

## 7. Vision Model Setup

```python
vision_runner = RKNNRunner(
    model_path="selfdrive/modeld/models/driving_vision.rknn",
    model_name="driving_vision",
    core_id=0,
    expected_inputs={
        "img": (1, 12, 128, 256),
        "big_img": (1, 12, 128, 256),
    },
    nhwc_inputs={"img", "big_img"},
)
```

---

## 8. Vision Initialization

```python
vision_runner.initialize()
vision_runner.validate()
```

---

## 9. Vision Inference

```python
vision_outputs = vision_runner.infer({
    "img": img_tensor,
    "big_img": big_img_tensor,
})
```

---

## 10. Vision Rule

Vision model must run on:

```text
NPU Core 0
```

---

# Section E — Policy Runner Example

## 11. Policy Model Setup

```python
policy_runner = RKNNRunner(
    model_path="selfdrive/modeld/models/driving_policy.rknn",
    model_name="driving_policy",
    core_id=1,
    expected_inputs={
        "features_buffer": (1, 512),
        "desire": (1, 8),
        "traffic_convention": (1, 2),
    },
)
```

---

## 12. Policy Initialization

```python
policy_runner.initialize()
policy_runner.validate()
```

---

## 13. Policy Inference

```python
policy_outputs = policy_runner.infer({
    "features_buffer": features_buffer,
    "desire": desire,
    "traffic_convention": traffic_convention,
})
```

---

## 14. Policy Rule

Policy model must run on:

```text
NPU Core 1
```

---

# Section F — Backend Selection Example

## 15. Environment Variable

```bash
OPENPILOT_MODELD_BACKEND=rknn
```

Fallback:

```bash
OPENPILOT_MODELD_BACKEND=tinygrad
```

Auto:

```bash
OPENPILOT_MODELD_BACKEND=auto
```

---

## 16. Backend Selection Logic

```python
def select_backend() -> str:
    backend = os.environ.get("OPENPILOT_MODELD_BACKEND", "auto")

    if backend in ("rknn", "tinygrad"):
        return backend

    vision = Path("selfdrive/modeld/models/driving_vision.rknn")
    policy = Path("selfdrive/modeld/models/driving_policy.rknn")

    if vision.exists() and policy.exists():
        return "rknn"

    return "tinygrad"
```

---

# Section G — Integration Example

## 17. modeld Integration Sketch

```python
backend = select_backend()

if backend == "rknn":
    vision_runner.initialize()
    policy_runner.initialize()

    vision_outputs = vision_runner.infer(vision_inputs)
    policy_outputs = policy_runner.infer(policy_inputs)
else:
    vision_outputs = tinygrad_vision_runner.infer(vision_inputs)
    policy_outputs = tinygrad_policy_runner.infer(policy_inputs)
```

---

## 18. Integration Rule

Only replace inference execution.

Do not replace:

* VisionIPC
* loadyuv.cl
* transform.cl
* warp generation
* metadata parser
* planner interface

---

# Section H — Validation Example

## 19. Runtime Validation

Generate:

```text
driving_vision_rknn_runtime_report.json
driving_policy_rknn_runtime_report.json
```

---

## 20. Output Comparison

Compare:

```text
Tinygrad output
RKNN output
```

Metrics:

```text
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

## 21. Multi-Frame Validation

Minimum:

```text
100 frames
```

Preferred:

```text
1000 frames
```

---

# Section I — Performance Example

## 22. Expected Latency

Vision RKNN:

```text
8–12 ms
```

Policy RKNN:

```text
2–5 ms
```

Combined:

```text
10–17 ms
```

---

## 23. Pipeline Target

Camera → modelV2:

```text
18–30 ms
```

With DMA-BUF:

```text
15–27 ms
```

---

# Section J — Error Handling Example

## 24. Fail-Fast Policy

If RKNN output is invalid:

```text
Do not publish invalid modelV2.
```

Instead:

```text
Log error
Generate report
Fallback or restart runner
```

---

## 25. Recovery Policy

Allowed:

```text
Reload model
Reinitialize runtime
Restart RKNNRunner
Fallback to Tinygrad
```

Not allowed:

```text
Silent invalid output
```

---

# Section K — Production Checklist

Runtime loads

[ ]

Vision core 0

[ ]

Policy core 1

[ ]

Input shapes validated

[ ]

NHWC conversion validated

[ ]

Output shapes validated

[ ]

Tinygrad comparison passed

[ ]

Multi-frame validation passed

[ ]

Latency target passed

[ ]

Recovery tested

[ ]

---

# Section L — AI Agent Notes

## 26. Agent Rules

AI agent must:

1. Discover metadata first
2. Discover model input shapes
3. Discover model output shapes
4. Detect NCHW/NHWC requirement
5. Validate RKNN outputs against Tinygrad
6. Preserve Tinygrad fallback
7. Avoid planner/control changes

---

## 27. Agent Must Not

AI agent must not:

* hardcode output indices
* assume tensor layout
* remove fallback backend
* modify planner semantics
* publish invalid outputs
* skip multi-frame validation

---

# Final Example Result

Expected production configuration:

```text
Vision:
RKNN Core 0

Policy:
RKNN Core 1

Camera → modelV2:
18–30 ms

With DMA-BUF:
15–27 ms

Result:
PASS
```

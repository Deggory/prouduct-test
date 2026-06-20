# BRAIN.MD — The Omniscient RK3588 OpenPilot Brain

> **Version:** 4.0 — Absolute Master Reference  
> **Classification:** Single Source of Truth  
> **Target:** Orange Pi 5 / RK3588 / Sony IMX415 — Single Camera  
> **Mission:** Map the complete neural, physical, and software architecture of Sunnypilot/OpenPilot on RK3588, providing exact file-by-file patching instructions for any fork.

---

## Table of Contents

1. [Prime Directive](#prime-directive)
2. [Section 1 — File-by-File Patch Map](#section-1--file-by-file-patch-map)
3. [Section 2 — The 7-Milestone Porting Roadmap](#section-2--the-7-milestone-porting-roadmap)
4. [Section 3 — Camera & Preprocessing Secrets](#section-3--camera--preprocessing-secrets)
5. [Section 4 — RKNN Model Conversion Master Guide](#section-4--rknn-model-conversion-master-guide)
6. [Section 5 — RKNN Integration Architecture](#section-5--rknn-integration-architecture)
7. [Section 6 — System Configuration & Environment Variables](#section-6--system-configuration--environment-variables)
8. [Section 7 — Known Quirks & Drift Log](#section-7--known-quirks--drift-log)
9. [Section 8 — Architectural Flow Diagram](#section-8--architectural-flow-diagram)
10. [Final Declaration](#final-declaration)

---

## Prime Directive

This document is the complete engineering reference for running OpenPilot/Sunnypilot on Rockchip RK3588.

### The Absolute Rules

1. **Producer-side changes only.**  
   You may change how frames are captured (`camerad`) and how inference is run (`modeld`). You must **never** alter message schemas (`cereal/log.capnp`), planner math, control semantics, `loadyuv.cl`, or `transform.cl`.

2. **Metadata-driven execution.**  
   Never hardcode tensor indices such as `outputs[0]`. Always read input shapes and output slices from `.pkl` metadata files.

3. **Fail-fast and fallback.**  
   Always validate `np.isfinite()` on NPU outputs. If RKNN fails, fall back to ONNX/Tinygrad. Never silently publish garbage data to the planner.

4. **Strict NPU core assignment.**  
   Vision RKNN runs on **Core 0**. Policy RKNN runs on **Core 1**. Never use `NPU_CORE_AUTO` or `NPU_CORE_ALL` in production.

---

## Section 1 — File-by-File Patch Map

When forking any OpenPilot repo to RK3588, apply these exact modifications file-by-file.

### 1.1 Hardware Abstraction Layer

#### `system/hardware/__init__.py`

**Change:** Inject RK3588 device-tree detection and map the hardware class.

```python
RK3588 = "rk3588" in open("/proc/device-tree/compatible").read()
```

Then map:

```python
HARDWARE = RK3588Hardware(detected=True)
```

#### `common/hardware/rk3588/hardware.py`

Create this new file.

**Action:** Add an `RK3588Hardware(HardwareBase)` class.

**Critical rule:** `get_device_type()` must return `"pc"`.

OpenPilot's `DEVICE_CAMERAS` dictionary only has keys for `("pc", ...)`. Returning `"rk3588"` can cause a `KeyError` crash in:

```text
common/transformations/camera.py
```

**Also implement:**

- Thermal zones:
  - `soc-thermal`
  - `gpu-thermal`
  - `npu-thermal`
- CPU governors:
  - A76 cluster at approximately `2.256 GHz`
  - A55 cluster at approximately `1.8 GHz`
- NPU frequency:
  - `1 GHz`

---

### 1.2 Process Management

#### `system/manager/process_config.py`

**Change:** Gate `camerad` versus `webcamerad` with the `USE_WEBCAM` environment variable.

**Change:** Gate `dmonitoringmodeld` with the `NO_DM` environment variable.

**Warning:** If `NO_DM=0` and no driver camera is connected, `dmonitoringmodeld` can spin-wait forever on a blocking `vipc_client.connect()`. For a single-camera Orange Pi 5 build, default to:

```bash
export NO_DM=1
```

#### `common/realtime.py`

**Change:** Pin `camerad` to A76 Core 6 with `SCHED_FIFO` priority 53.

**Change:** Pin `modeld` to A76 Cores 4-7 with `SCHED_FIFO` priority 54.

---

### 1.3 Camera & VisionIPC

#### `tools/webcam/camera.py`

Development path.

**Change:** `CameraMJPG` should target:

```text
1280x720 @ 20 FPS
MJPG fourcc
```

**Change:** Add `get_modeld_nv12_info()` returning tight NV12 layout:

```text
1280 * 720 * 1.5 = 1,382,400 bytes
```

If this is missing, the UV plane offset can shift and corrupt the model input.

#### `common/transformations/camera.py`

**Change:** Override `DEVICE_CAMERAS[("pc", "unknown")]` with IMX415 intrinsics:

```text
width  = 1280
height = 720
focal  = 900.0
```

#### `common/hardware/rk3588/camera/v4l2.py` and `csi.py`

Production path.

**Action:** Implement V4L2 MPLANE with `VIDIOC_EXPBUF` to export DMA-BUF file descriptors.

**Action:** Pass the DMA-BUF fd to VisionIPC.

**Goal:** Zero CPU copies.

---

### 1.4 Model Inference — `modeld`

#### `sunnypilot/modeld_v2/modeld.py`

Or, depending on the fork:

```text
selfdrive/modeld/modeld.py
```

**Change:** Read the backend from:

```bash
OPENPILOT_MODELD_BACKEND
```

**Behavior:**

- If `OPENPILOT_MODELD_BACKEND=rknn`, initialize `RKNNRunner` for vision and policy.
- Otherwise, fall back to `TinygradRunner` or `ONNXRunner`.

#### `sunnypilot/modeld_v2/model_runner.py`

**Action:** Add an `RKNNRunner` class.

**Action:** Load `.rknn` models.

**Action:** Assign NPU cores:

```text
Vision -> NPU Core 0
Policy -> NPU Core 1
```

**Action:** Transpose NCHW to NHWC before inference.

**Action:** Parse outputs via `output_slices` from `.pkl` metadata.

**Never do this in production:**

```python
outputs[0]
```

as a hardcoded semantic assumption.

#### `selfdrive/modeld/models/`

Place these files here:

```text
selfdrive/modeld/models/
├── driving_vision.rknn
├── driving_policy.rknn
├── driving_vision_metadata.pkl
└── driving_policy_metadata.pkl
```

---

### 1.5 Location & Sensors

#### `selfdrive/locationd/locationd.py`

**Change:** Add:

```python
NO_IMU = os.getenv("NO_IMU") is not None
```

**Drift note:** The physical IMU socket drain is fully commented out in this design. The Kalman filter runs purely on:

- `cameraOdometry`
- `carState`
- `liveCalibration`

This is intentional for Orange Pi 5 single-camera bring-up.

---

## Section 2 — The 7-Milestone Porting Roadmap

Follow this exact sequence when porting a new repo. Do not skip steps.

1. **PC-mode bootstrapping**  
   Get UI to boot using:

   ```bash
   export USE_WEBCAM=1
   export NO_DM=1
   export NO_IMU=1
   ```

2. **IMX415 kernel setup**  
   Install the device-tree overlay and verify:

   ```bash
   dmesg | grep imx415
   ```

3. **DMA-BUF zero-copy camera**  
   Bypass OpenCV. Use:

   ```text
   V4L2 MPLANE -> NV12 DMA-BUF -> VisionIPC
   ```

4. **UI EGLImage rendering**  
   Bind the DMA-BUF fd to an OpenGL texture through:

   ```text
   eglCreateImageKHR
   ```

5. **Model conversion**  
   Convert ONNX to RKNN and fix:

   - GELU
   - UINT8 inputs
   - ReduceL2 FP16 overflow
   - GatherND negative indexing

6. **RKNN NPU inference**  
   Wire `RKNNRunner` into `modeld`.

   ```text
   Vision -> Core 0
   Policy -> Core 1
   ```

7. **Real-time scheduling**  
   Apply `os.sched_setaffinity` and `SCHED_FIFO` priorities.

---

## Section 3 — Camera & Preprocessing Secrets

### 3.1 The NV12 Layout Bug

This is fatal if missed.

Webcams send tight NV12:

```text
1280 * 720 * 1.5 = 1,382,400 bytes
```

OpenPilot expects padded Qualcomm VENUS-style NV12:

```text
stride   = 1280
y_height = 736
```

**Fix:** Add `get_modeld_nv12_info()` that returns tight NV12 layout when:

```bash
USE_WEBCAM=1
```

Otherwise, the UV plane offset can shift, corrupting the model input image.

---

### 3.2 The Forbidden CPU Path

Never use this path in production:

```text
IMX415 -> OpenCV BGR -> bgr_to_nv12() -> numpy copies -> RKNN
```

**Reason:** It destroys latency by adding approximately 8-10 ms of CPU overhead.

This path is acceptable only for Milestone 1 development bring-up.

---

### 3.3 The Target Zero-Copy Path

```text
IMX415 (MIPI CSI-2)
  -> RKISP (/dev/video0)
  -> V4L2 MPLANE (NV12 DMA-BUF)
       ├──> VisionIPC fd passing -> modeld -> NPU reads fd directly
       └──> EGLImage fd passing  -> Mali GPU renders texture directly
```

---

## Section 4 — RKNN Model Conversion Master Guide

Converting Supercombo/driving ONNX models to RKNN has known failure points. Use this matrix.

### 4.1 The 4-Step Conversion Pipeline

1. **Simplify**  
   Use `onnxsim simplify()` to remove redundant `Identity` and `Cast` ops.

2. **Opset downgrade**  
   RKNN Toolkit 2.3.2 requires opset `<= 19`.

3. **Graph rewrites for vision**  
   Convert UINT8 inputs to FLOAT16 and remove Cast nodes.

4. **Build**  
   Quantize to INT8 using KL divergence and export `.rknn`.

---

### 4.2 The 5 Fatal RKNN Conversion Bugs & Fixes

#### 1. `Gelu(approximate="tanh")`

**Issue:** RKNN has no native mapping for tanh-approximate GELU.

**Fix:** Rewrite the ONNX graph into primitive:

```text
Mul / Add / Tanh
```

operations before conversion.

#### 2. UINT8 Input Rejection — Vision Model

**Issue:** `driving_vision.onnx` uses UINT8. RKNN can fail with:

```text
Not Support Dtype: 2
```

**Fix:** Change graph inputs to FLOAT16 and remove the two direct input `Cast` nodes.

#### 3. ReduceL2 FP16 Overflow — Vision Model

**Issue:** Hidden-state L2 normalization square-sum can exceed FP16 max.

Example:

```text
FP16 max ~= 65,504
norm     ~= 440
square   ~= 193,600
```

**Fix:** Prescale the input in the ONNX graph:

```text
ReduceL2(x) -> ReduceL2(x / 32) * 32
```

#### 4. GatherND Negative Index — Policy Model

**Issue:** The policy model crops feature tokens using:

```text
GatherND(indices=-9..-1)
```

RKNN can mishandle negative indices and produce `inf`.

**Fix:** Rewrite the ONNX graph to:

```text
Slice(features_buffer, axis=1, starts=16, ends=25)
```

#### 5. NCHW vs NHWC Data Layout

**Issue:** RKNNLite defaults to NCHW, but NPU hardware expects NHWC. Without transpose, `hidden_state` can become all zeros.

**Fix:** Set:

```text
data_format="nhwc"
```

Then transpose tensors in Python:

```python
np.transpose(tensor, (0, 2, 3, 1))
```

---

## Section 5 — RKNN Integration Architecture

### 5.1 The `RKNNRunner` Class Blueprint

This is the authoritative wrapper for NPU inference.

```python
import pickle
import numpy as np
from rknnlite.api import RKNNLite


class RKNNRunner:
    def __init__(self, model_path, metadata_path, core_id=0):
        self.rknn = RKNNLite()
        self.rknn.load_rknn(model_path)

        # Strict core assignment:
        # 0 = Vision
        # 1 = Policy
        # 2 = Reserved
        core_mask = {
            0: RKNNLite.NPU_CORE_0,
            1: RKNNLite.NPU_CORE_1,
            2: RKNNLite.NPU_CORE_2,
        }[core_id]

        self.rknn.init_runtime(core_mask=core_mask)

        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)

        self.output_slices = self.metadata["output_slices"]

    def infer(self, inputs: dict) -> dict:
        # 1. Prepare inputs: NCHW -> NHWC when required.
        ordered_inputs = [self._prepare(inputs[k]) for k in sorted(inputs.keys())]

        # 2. Run NPU inference.
        outputs = self.rknn.inference(inputs=ordered_inputs)

        # 3. Fail-fast validation.
        for output in outputs:
            if not np.all(np.isfinite(output)):
                raise ValueError("RKNN output contains NaN or Inf")

        # 4. Metadata-driven slicing.
        # Do not hardcode tensor semantics from outputs[0].
        flat_output = outputs[0].flatten()
        return {
            name: flat_output[slice_range]
            for name, slice_range in self.output_slices.items()
        }
```

---

### 5.2 Model File Structure

```text
selfdrive/modeld/models/
├── driving_vision.rknn             # INT8 NPU model
├── driving_policy.rknn             # INT8 NPU model
├── driving_vision_metadata.pkl     # input_shapes, output_slices
└── driving_policy_metadata.pkl
```

---

### 5.3 Expected Performance

INT8 on RK3588 NPU:

| Component | Expected Time |
|---|---:|
| Vision inference | ~8-12 ms |
| Policy inference | ~2-5 ms |
| Total NPU time | <17 ms |

This fits within a 50 ms frame budget for 20 Hz operation.

---

## Section 6 — System Configuration & Environment Variables

### 6.1 Orange Pi 5 V4L2 Device Mapping

```text
/dev/video0  -> RKISP main path, IMX415 road camera
/dev/video11 -> RKISP self path, preview/config
/dev/video31 -> RGA, hardware resize/convert accelerator
```

---

### 6.2 Master Environment Variables

```bash
# Camera
export USE_WEBCAM=1
export ROAD_CAM=0
export WEBCAM_WIDTH=1280
export WEBCAM_HEIGHT=720
export WEBCAM_FPS=20
export WEBCAM_FOURCC=MJPG
export WEBCAM_FOCAL=900.0

# Hardware gates
export NO_DM=1
export NO_IMU=1

# Model backend
export OPENPILOT_MODELD_BACKEND=rknn
export MODELD_VISION_RKNN_INPUT_LAYOUT=nhwc
export MODELD_WARP_OUTPUT_LAYOUT=nhwc
export DISABLE_JIT_ALIAS_COPY=1
```

---

### 6.3 UI Adaptations

OpenPilot often assumes a 2160x1080 display.

Orange Pi 5 HDMI may use:

- 800x400
- 1280x720
- 1920x1080

Patch the Qt UI scaling in:

```text
selfdrive/ui/qt/
```

so the UI renders correctly on the target display.

---

### 6.4 Build System — SCons

Build command:

```bash
QCOM=1 scons -j"$(nproc)"
```

`QCOM=1` is used here to enable the ARM64/tinygrad-style path expected by the fork.

Initialize submodules:

```bash
git submodule update --init --recursive
```

Required submodules commonly include:

- `cereal`
- `msgq`
- `opendbc`
- `tinygrad`

---

## Section 7 — Known Quirks & Drift Log

### IMU Drain Commented Out

In `locationd.py`, the physical IMU socket drain is fully commented out.

The Kalman filter runs on:

- `cameraOdometry`
- `carState`
- `liveCalibration`

This is intentional for the Orange Pi 5 single-camera setup.

---

### `dmonitoringmodeld` Spin-Wait

If `NO_DM=0` and no driver camera is connected, `dmonitoringmodeld` can spin-wait forever on a blocking `vipc_client.connect()`.

For single-camera builds, use:

```bash
export NO_DM=1
```

---

### Panfrost OpenCL Limitations

The Mali-G610 GPU via Rusticl can compile vision preprocessing, but the policy model may fail with:

```text
InvalidBitWidth: Invalid bit width in input: 128
```

CPU/LLVM is the stable fallback for preprocessing until RGA is fully wired.

---

### FLOAT16 ONNXRuntime Is Not a Reference

Do not use FP16 ONNXRuntime CPU as the validation baseline for RKNN correlation.

Grouped convolutions such as `conv2d_11` can produce wrong results in FP16 on CPU.

Use FP32-promoted ONNX as the reference for correlation validation.

---

### `GOD.md` HEAD Drift

The documented `HEAD` in `GOD.md` can become stale.

Always verify the actual commit history with:

```bash
git log --oneline -5
```

before relying on commit hashes in docs.

---

## Section 8 — Architectural Flow Diagram

```text
[IMX415 Sensor] -> (MIPI) -> [RKISP] -> (V4L2) -> [DMA-BUF NV12]
                                                      |
                                    +-----------------+-----------------+
                                    |                                   |
                              [VisionIPC]                           [EGLImage]
                                    |                                   |
                              [modeld.py]                           [UI/Qt]
                                    |                                   |
                    +---------------+---------------+                 |
                    |                               |                 |
          [RKNN Vision Core 0]            [RKNN Policy Core 1]        |
          (8-12ms inference)              (2-5ms inference)           |
                    |                               |                 |
                    +---------------+---------------+                 |
                                    |                                 |
                              [Metadata Slicing]                      |
                                    |                                 |
                              [modelV2 message]                       |
                                    |                                 |
                 +------------------+------------------+             |
                 |                  |                  |             |
           [plannerd]         [controlsd]          [selfdrived]      |
                 |                  |                  |             |
           [longitudinalPlan]    [carControl]      [selfdriveState]  |
                 |                  |                  |             |
                 +------------------+------------------+             |
                                    |                                 |
                              [card / CAN bus]                        |
                                    |                                 |
                              [Vehicle Actuators] <-------------------+
```

---

## Final Declaration

This document represents the complete engineering truth for the Orange Pi 5 / RK3588 OpenPilot ecosystem.

If you are an AI agent or engineer tasked with porting a new repository:

1. Read this document fully.
2. Apply the File-by-File Patch Map in Section 1.
3. Obey the metadata and fail-fast rules.
4. Consult Section 4 when model conversion fails.
5. Do not deviate from this architecture.

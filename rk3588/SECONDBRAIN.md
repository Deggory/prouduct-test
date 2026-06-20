# SECONDBRAIN.md — RK3588 / Orange Pi 5 / IMX415 OpenPilot Porting Brain

**Version:** 1.0  
**Source basis:** BRAIN.md v8-style RK3588 master notes supplied by the user  
**Target hardware:** Orange Pi 5 / RK3588 / Sony IMX415 single road camera  
**Target software family:** openpilot / sunnypilot / sunnypilot-pc / enhancedopenpilot-style forks  
**Mission:** Give any human engineer or AI coding agent one practical file that explains how to fork, patch, validate, and debug an OpenPilot-style repo so it can run on RK3588 with RKNN NPU acceleration and a single IMX415 camera.

---

## 0. How to Use This File

Place this file in the repo root or inside an `ai/` or `docs/` folder:

```text
repo/
├── SECONDBRAIN.md
├── selfdrive/
├── system/
├── common/
└── tools/
```

When using VS Code, Claude Code, Cursor, Copilot, or any AI coding agent, tell it:

```text
Read SECONDBRAIN.md first.
Do not modify planner/control logic.
Only patch hardware, camera, model runner, build/env, and validation paths.
Follow the RK3588 rules exactly.
```

This document is not just a README. It is the porting memory. It should tell the AI what is allowed, what is forbidden, what files matter, and how to validate the result.

---

# 1. Prime Directive

This project is about running OpenPilot/Sunnypilot on **Rockchip RK3588**, especially **Orange Pi 5**, using a **single Sony IMX415 road camera** and **RKNN NPU models**.

The goal is not to rewrite OpenPilot.  
The goal is to change the producer side:

```text
camera input  -> camerad / VisionIPC
model input   -> modeld / RKNN runner
hardware HAL  -> RK3588 detection, thermal, frequency, CAN, fan
```

The downstream OpenPilot brain must remain stable:

```text
modelV2 schema
planner
controlsd
carState
carControl
cereal messages
loadyuv.cl
transform.cl
```

## Absolute Rules

### Rule 1 — Producer-Side Changes Only

Allowed:

- `camerad`
- `webcamerad`
- V4L2 camera HAL
- RK3588 hardware HAL
- `modeld`
- model runner wrapper
- RKNN conversion tools
- launch/env scripts
- validation tools
- UI display scaling and camera texture import

Forbidden:

- Changing `modelV2` schema just to fit RKNN
- Changing planner math to hide bad model output
- Changing control semantics
- Changing `loadyuv.cl` or `transform.cl` unless there is a documented separate optimization task
- Publishing fake or reshaped model outputs without metadata verification

### Rule 2 — Metadata-Driven Execution

Never hardcode output indexes like this:

```python
plan = outputs[0]
```

Use metadata:

```python
with open(metadata_path, "rb") as f:
    metadata = pickle.load(f)

output_slices = metadata["output_slices"]
flat = outputs[0].reshape(-1)

parsed = {
    name: flat[slice_info]
    for name, slice_info in output_slices.items()
}
```

### Rule 3 — Fail Fast, Then Fallback

Before publishing any RKNN output:

```python
if not np.all(np.isfinite(output)):
    raise RuntimeError("RKNN output contains NaN or Inf")
```

If RKNN fails at runtime:

1. Log the failure.
2. Drop the bad frame or fallback to Tinygrad/ONNX.
3. Never publish NaN/Inf to planner.

### Rule 4 — Strict NPU Core Assignment

Production should not use automatic NPU core selection.

Correct target:

```text
Vision RKNN -> NPU Core 0
Policy RKNN -> NPU Core 1
Core 2      -> spare / future / debug
```

Forbidden in production:

```python
RKNNLite.NPU_CORE_AUTO
RKNNLite.NPU_CORE_ALL
```

### Rule 5 — OpenCV Path Is Development Only

Allowed for first boot/debug:

```text
IMX415 / USB camera -> OpenCV -> numpy -> modeld
```

Production target:

```text
IMX415 -> RKISP -> V4L2 NV12 DMA-BUF -> VisionIPC -> modeld/RKNN
```

OpenCV BGR conversion adds avoidable CPU latency and breaks the zero-copy goal.

---

# 2. Target Hardware Brain

## 2.1 RK3588 Topology

```text
SoC:       Rockchip RK3588
Board:     Orange Pi 5
CPU:       4x Cortex-A76 big cores + 4x Cortex-A55 little cores
GPU:       Mali-G610
NPU:       3-core Rockchip NPU, up to ~6 TOPS advertised
ISP:       RKISP
Camera:    Sony IMX415 over MIPI CSI-2
OS target: Ubuntu 24.04-style RK3588 Linux image
```

## 2.2 Recommended Core Roles

```text
A55 cores 0-3:
  background tasks, UI helper, logging

A76 cores 4-7:
  modeld, camerad, critical runtime work

Recommended:
  camerad -> core 6, SCHED_FIFO priority 53
  modeld  -> cores 4,5,6,7, SCHED_FIFO priority 54
  ui      -> normal priority, GPU-bound
```

Example environment:

```bash
export CAMERAD_CORE_POOL=6
export MODELD_CORE_POOL=4,5,6,7
```

## 2.3 Critical IMX415 Assumptions

For single road camera builds:

```text
Resolution: 1280 x 720
FPS:        20
Format:     NV12 target for production
Focal:      around 900.0 px for initial intrinsics
```

Important: these values must match the model path and camera intrinsics used by the fork.

---

# 3. Repository Porting Strategy

## 3.1 The 7 Milestones

Do not jump directly to RKNN. Port in this order.

### Milestone 1 — PC-Mode Boot

Goal:

```text
UI boots.
No comma hardware crash.
One camera feed appears.
```

Use:

```bash
export USE_WEBCAM=1
export NO_DM=1
export NO_IMU=1
```

Expected dev path:

```text
webcamerad -> VisionIPC -> modeld -> UI
```

### Milestone 2 — RK3588 Hardware Detection

Goal:

```text
Repo knows it is running on RK3588.
It does not crash because it is not TICI/comma hardware.
```

Patch:

```text
system/hardware/__init__.py
common/hardware/rk3588/
```

### Milestone 3 — IMX415 Kernel / V4L2

Goal:

```text
Linux sees the IMX415 through RKISP.
```

Verify:

```bash
dmesg | grep -i imx415
v4l2-ctl --list-devices
media-ctl -p
```

Expected camera path:

```text
imx415 -> csi2 dphy -> rkcif/rkisp -> rkisp_mainpath -> /dev/video*
```

### Milestone 4 — Zero-Copy Camera

Goal:

```text
No OpenCV BGR path.
No numpy camera copies.
Frames are NV12 DMA-BUF.
```

Target:

```text
V4L2 MPLANE
VIDIOC_REQBUFS
VIDIOC_EXPBUF
DMA-BUF fd
VisionIPC fd passing
```

### Milestone 5 — RKNN Model Conversion

Goal:

```text
driving_vision.rknn
driving_policy.rknn
matching metadata .pkl files
```

Must solve:

- UINT8 input issue
- GELU tanh approximation
- ReduceL2 FP16 overflow
- GatherND negative index issue
- NCHW/NHWC layout issue

### Milestone 6 — RKNN Runtime in modeld

Goal:

```text
modeld can select backend:
  rknn
  tinygrad
  onnx
```

`rknn` path must:

- Load `.rknn`
- Load metadata `.pkl`
- Assign NPU core strictly
- Validate output finite values
- Parse outputs using metadata
- Fallback on failure

### Milestone 7 — Validation and Deployment

Goal:

```text
100+ frame output correlation passes.
1 hour stress run passes.
Camera and modeld restart correctly.
No NaN/Inf reaches modelV2.
Thermals stay safe.
```

---

# 4. File-by-File Patch Map

This section tells an AI agent exactly where to look.

## 4.1 Hardware Abstraction Layer

### `system/hardware/__init__.py`

Purpose:

```text
Detect RK3588 and select RK3588Hardware.
```

Pattern:

```python
def _is_rk3588() -> bool:
    try:
        with open("/proc/device-tree/compatible", "rb") as f:
            data = f.read().lower()
        return b"rk3588" in data
    except Exception:
        return False

RK3588 = _is_rk3588()

if TICI:
    HARDWARE = Tici()
elif RK3588:
    from common.hardware.rk3588.hardware import RK3588Hardware
    HARDWARE = RK3588Hardware(detected=True)
else:
    HARDWARE = Pc()
```

Important:

```text
Do not make RK3588 behave like TICI unless every TICI dependency is present.
```

### `common/hardware/rk3588/hardware.py`

Create this if missing.

Responsibilities:

- `RK3588Hardware(HardwareBase)`
- thermal readings
- CPU governor control
- NPU frequency helper
- fan PWM helper
- CAN / SocketCAN helper if used
- safe device type mapping

Critical:

```python
def get_device_type(self):
    return "pc"
```

Reason:

```text
Many OpenPilot camera/intrinsics maps only know "pc", "tici", etc.
Returning "rk3588" may cause DEVICE_CAMERAS KeyError unless the repo has a proper RK3588 camera entry.
```

## 4.2 Process Management

### `system/manager/process_config.py`

Required gates:

```python
USE_WEBCAM = os.getenv("USE_WEBCAM") is not None
NO_DM = os.getenv("NO_DM") is not None
NO_IMU = os.getenv("NO_IMU") is not None
```

Single camera target:

```text
road camera only
driver camera disabled
wide camera disabled
IMU optional/disabled first
```

Gate driver monitoring:

```text
dmonitoringmodeld enabled only when NO_DM is false and driver cam exists
```

Warning:

```text
If NO_DM=0 but no driver camera exists, dmonitoringmodeld can block/spin waiting for VisionIPC.
```

## 4.3 Realtime Scheduling

### `common/realtime.py`

Add RK3588-aware core pinning:

```python
# recommended
camerad: core 6, priority 53
modeld: cores 4-7, priority 54
```

Example helper:

```python
def rk3588_realtime_process(cores, priority):
    os.sched_setaffinity(0, set(cores))
    param = os.sched_param(priority)
    os.sched_setscheduler(0, os.SCHED_FIFO, param)
```

Keep fallback if permission is missing.

## 4.4 Camera Development Path

### `tools/webcam/camera.py`

Development only.

Set defaults:

```text
width  = 1280
height = 720
fps    = 20
focal  = 900.0
```

For USB webcam:

```bash
export USE_WEBCAM=1
export ROAD_CAM=0
export WEBCAM_WIDTH=1280
export WEBCAM_HEIGHT=720
export WEBCAM_FPS=20
```

For IMX415, prefer NV12 if possible.

## 4.5 Production Camera HAL

Suggested new files:

```text
common/hardware/rk3588/camera/v4l2.py
common/hardware/rk3588/camera/csi.py
common/hardware/rk3588/visionbuf_dma.cc
common/hardware/rk3588/rga.py
```

### `common/hardware/rk3588/camera/v4l2.py`

Responsibilities:

- open `/dev/video*`
- query capabilities
- detect single-plane vs multi-plane
- set NV12 format
- request buffers
- mmap buffers
- export DMA-BUF fds with `VIDIOC_EXPBUF`
- queue/dequeue frames
- pass fd and metadata onward

Target capture:

```text
V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE
V4L2_PIX_FMT_NV12
V4L2_MEMORY_MMAP
VIDIOC_EXPBUF -> dmabuf_fd
```

### `common/hardware/rk3588/camera/csi.py`

Responsibilities:

- IMX415 defaults
- media graph sanity checks
- device selection
- configure road camera only

Recommended class:

```python
class IMX415Camera:
    width = 1280
    height = 720
    fps = 20
    pix_fmt = "NV12"
```

### `common/hardware/rk3588/visionbuf_dma.cc`

Responsibilities:

```text
C++ DMA-BUF VisionIPC buffer handling.
```

Goal:

```text
VisionIPC passes fd directly instead of copying bytes.
```

## 4.6 Camera Intrinsics

### `common/transformations/camera.py`

For early RK3588 compatibility, override PC unknown camera entry:

```python
DEVICE_CAMERAS[("pc", "unknown")] = CameraConfig(
    width=1280,
    height=720,
    focal_length=900.0,
    ...
)
```

Better long-term:

```text
Add explicit RK3588/IMX415 entry if the repo supports custom device types cleanly.
```

## 4.7 UI Rendering

### `system/ui/lib/egl.py` or equivalent UI GL backend

Target:

```text
DMA-BUF fd -> EGLImage -> OpenGL texture
```

Use:

```c
eglCreateImageKHR(... EGL_LINUX_DMA_BUF_EXT ...)
glEGLImageTargetTexture2DOES(GL_TEXTURE_EXTERNAL_OES, image)
```

Needed attributes:

```text
DRM_FORMAT_NV12
plane 0 fd, offset, pitch
plane 1 fd, offset, pitch
```

The UI should not force CPU conversion just to show the camera.

## 4.8 Model Runtime

Common possible files:

```text
selfdrive/modeld/modeld.py
selfdrive/modeld/runners/*
sunnypilot/modeld_v2/modeld.py
sunnypilot/modeld_v2/model_runner.py
selfdrive/modeld/models/
```

Runtime selection:

```bash
export OPENPILOT_MODELD_BACKEND=rknn
```

Accepted backends:

```text
rknn
tinygrad
onnx
```

Expected model files:

```text
selfdrive/modeld/models/
├── driving_vision.rknn
├── driving_policy.rknn
├── driving_vision_metadata.pkl
└── driving_policy_metadata.pkl
```

## 4.9 Location and IMU

### `selfdrive/locationd/locationd.py`

Single camera first boot:

```bash
export NO_IMU=1
```

If physical IMU is not ready:

```text
locationd should still run using cameraOdometry, carState, liveCalibration if fork supports that path.
```

Do not fake IMU values unless explicitly documented for a simulator.

---

# 5. Camera Pipeline Brain

## 5.1 Bad Development Pipeline

This is acceptable only for bring-up:

```text
IMX415 or USB cam
  -> OpenCV VideoCapture
  -> BGR frame
  -> resize / convert
  -> numpy buffer
  -> VisionIPC
  -> modeld
```

Problems:

- CPU copy
- BGR conversion cost
- extra latency
- breaks true zero-copy design
- not production-safe for low latency

## 5.2 Correct Production Pipeline

```text
Sony IMX415
  -> MIPI CSI-2
  -> Rockchip CSI2 DPHY
  -> RKCIF / RKISP
  -> rkisp_mainpath
  -> V4L2 NV12 MPLANE buffer
  -> DMA-BUF fd export
  -> VisionIPC fd passing
  -> modeld
  -> RKNN NPU
```

UI path:

```text
same DMA-BUF fd
  -> EGLImage
  -> Mali GPU
  -> onroad UI overlay
```

## 5.3 V4L2 Sequence

Pseudo-flow:

```c
fd = open("/dev/video0", O_RDWR);

ioctl(fd, VIDIOC_QUERYCAP, &cap);

fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
fmt.fmt.pix_mp.width = 1280;
fmt.fmt.pix_mp.height = 720;
fmt.fmt.pix_mp.pixelformat = V4L2_PIX_FMT_NV12;
ioctl(fd, VIDIOC_S_FMT, &fmt);

req.count = 4;
req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
req.memory = V4L2_MEMORY_MMAP;
ioctl(fd, VIDIOC_REQBUFS, &req);

for each buffer:
  VIDIOC_QUERYBUF
  mmap
  VIDIOC_EXPBUF -> dmabuf_fd
  VIDIOC_QBUF

VIDIOC_STREAMON

loop:
  VIDIOC_DQBUF
  send dmabuf_fd + timestamp + frame id
  VIDIOC_QBUF
```

## 5.4 NV12 Layout Bug

OpenPilot often assumes Qualcomm VENUS-style padded NV12.

IMX415 / V4L2 may provide tight NV12:

```text
Y plane:  width * height
UV plane: width * height / 2
Total:    width * height * 1.5
1280x720: 1,382,400 bytes
```

If OpenPilot expects padded height/stride, UV offset will be wrong. This corrupts color and model input.

Required helper:

```python
def get_modeld_nv12_info(width, height, tight=True):
    if tight:
        y_stride = width
        y_height = height
        uv_offset = width * height
        total_size = width * height * 3 // 2
    else:
        # existing device-specific padded layout
        ...
    return y_stride, y_height, uv_offset, total_size
```

Use tight layout for:

```text
USE_WEBCAM=1
RK3588 V4L2 native path
IMX415 NV12 path unless proven padded
```

---

# 6. RGA Brain

RGA is the Rockchip hardware accelerator for resize/convert/copy.

Use RGA for:

- NV12 resize
- format conversion
- crop
- scaling camera frames before model input

Do not use RGA with numpy arrays in production.

Correct:

```text
DMA-BUF fd -> RGA -> DMA-BUF fd
```

Incorrect:

```text
DMA-BUF -> CPU numpy -> RGA -> CPU numpy
```

Suggested API:

```python
class RGA:
    def resize_nv12(self, src_fd, src_w, src_h, dst_fd, dst_w, dst_h):
        ...
```

Expected performance target:

```text
preprocess resize/convert: <1-2 ms
```

---

# 7. RKNN Conversion Brain

## 7.1 Conversion Target

Output files:

```text
driving_vision.rknn
driving_policy.rknn
driving_vision_metadata.pkl
driving_policy_metadata.pkl
```

Target platform:

```text
rk3588
```

Quantization:

```text
INT8 where safe
FP16 fallback for unsupported/non-quantized ops
```

## 7.2 RKNN Toolkit Config

Use this as starting config:

```python
rknn.config(
    mean_values=[[0, 0, 0]],
    std_values=[[1, 1, 1]],
    target_platform="rk3588",
    quantized_dtype="asymmetric_quantized-8",
    quantized_method="channel",
    float_dtype="float16",
    optimization_level=3,
    quantized_algorithm="normal",
    compress_weight=True,
)
```

Try `kl_divergence` if accuracy is poor:

```python
quantized_algorithm="kl_divergence"
```

## 7.3 Required ONNX Fixes

### Fix 1 — GELU Approximation

Problem:

```text
Gelu(approximate="tanh") may not map cleanly to RKNN.
```

Fix:

```text
Rewrite GELU into primitive Mul/Add/Tanh nodes before conversion.
```

### Fix 2 — UINT8 Vision Inputs

Problem:

```text
Vision model may use UINT8 inputs.
RKNN conversion may reject or mishandle them.
```

Fix:

```text
Change model graph inputs to FLOAT16/FLOAT32.
Remove direct input Cast nodes.
Move normalization/preprocess outside or into supported graph form.
```

### Fix 3 — ReduceL2 FP16 Overflow

Problem:

```text
FP16 max finite value is 65504.
ReduceL2 square-sum can overflow.
```

Fix:

```text
ReduceL2(x) -> ReduceL2(x / 32) * 32
```

### Fix 4 — GatherND Negative Index

Problem:

```text
Policy model may use GatherND with negative indices.
RKNN can produce invalid outputs.
```

Fix:

```text
Replace negative GatherND crop with positive Slice.
Example:
Slice(features_buffer, axis=1, starts=16, ends=25)
```

### Fix 5 — NCHW vs NHWC

Problem:

```text
OpenPilot/tinygrad often uses NCHW.
RKNN/NPU path may expect NHWC.
```

Fix:

```python
nhwc = np.transpose(nchw, (0, 2, 3, 1))
```

Set RKNN config/layout accordingly and validate against metadata.

## 7.4 Calibration Dataset

Store calibration samples:

```text
tools/rknn/dataset/
```

Vision samples:

```text
input_imgs_*.npy
big_input_imgs_*.npy
shape examples: (1, 12, 128, 256)
```

Policy samples:

```text
features_buffer_*.npy
desire_*.npy
traffic_convention_*.npy
lateral_control_params_*.npy
prev_desired_curv_*.npy
```

Use real representative driving frames where possible.

Minimum dev count:

```text
11 samples
```

Better validation count:

```text
100+ frames
```

---

# 8. RKNN Runtime Brain

## 8.1 RKNNRunner Requirements

A correct runner must do all of this:

- Load `.rknn`
- Load matching `.pkl` metadata
- Validate expected inputs
- Convert layout if needed
- Assign strict NPU core
- Run inference
- Validate finite outputs
- Parse using metadata
- Return named tensors to existing modeld logic
- Fallback on runtime failure

## 8.2 Safe RKNNRunner Skeleton

```python
import os
import pickle
import numpy as np
from rknnlite.api import RKNNLite


class RKNNRunner:
    CORE_MAP = {
        0: RKNNLite.NPU_CORE_0,
        1: RKNNLite.NPU_CORE_1,
        2: RKNNLite.NPU_CORE_2,
    }

    def __init__(self, model_path, metadata_path, core_id, input_layout="nchw"):
        if core_id not in self.CORE_MAP:
            raise ValueError(f"Invalid RKNN core_id={core_id}. Use 0, 1, or 2.")

        self.model_path = model_path
        self.metadata_path = metadata_path
        self.core_id = core_id
        self.input_layout = input_layout

        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)

        self.input_shapes = self.metadata.get("input_shapes", {})
        self.output_slices = self.metadata.get("output_slices", None)
        if not self.output_slices:
            raise ValueError(f"{metadata_path} missing output_slices")

        self.rknn = RKNNLite()

        ret = self.rknn.load_rknn(model_path)
        if ret != 0:
            raise RuntimeError(f"Failed to load RKNN model: {model_path}")

        ret = self.rknn.init_runtime(core_mask=self.CORE_MAP[core_id])
        if ret != 0:
            raise RuntimeError(f"Failed to init RKNN runtime on core {core_id}")

    def _prepare_array(self, arr):
        arr = np.asarray(arr)

        if not np.all(np.isfinite(arr)):
            raise ValueError("RKNN input contains NaN or Inf")

        if self.input_layout.lower() == "nhwc" and arr.ndim == 4:
            # Convert NCHW -> NHWC only if the source is NCHW.
            # In production, validate this against metadata.
            arr = np.transpose(arr, (0, 2, 3, 1)).copy()

        return arr

    def infer(self, inputs):
        ordered = []
        for name in self.input_shapes.keys():
            if name not in inputs:
                raise KeyError(f"Missing RKNN input: {name}")
            ordered.append(self._prepare_array(inputs[name]))

        outputs = self.rknn.inference(inputs=ordered)
        if outputs is None:
            raise RuntimeError("RKNN inference returned None")

        for i, out in enumerate(outputs):
            if not np.all(np.isfinite(out)):
                raise RuntimeError(f"RKNN output {i} contains NaN or Inf")

        # Many converted models return one flat output, but do not assume
        # semantic meaning without metadata.
        flat = np.concatenate([np.asarray(o).reshape(-1) for o in outputs])

        parsed = {}
        for name, sl in self.output_slices.items():
            parsed[name] = flat[sl]

        return parsed
```

## 8.3 Correct Core Assignment

Example:

```python
vision_runner = RKNNRunner(
    "selfdrive/modeld/models/driving_vision.rknn",
    "selfdrive/modeld/models/driving_vision_metadata.pkl",
    core_id=int(os.getenv("RKNN_VISION_CORE", "0")),
    input_layout=os.getenv("MODELD_VISION_RKNN_INPUT_LAYOUT", "nhwc"),
)

policy_runner = RKNNRunner(
    "selfdrive/modeld/models/driving_policy.rknn",
    "selfdrive/modeld/models/driving_policy_metadata.pkl",
    core_id=int(os.getenv("RKNN_POLICY_CORE", "1")),
    input_layout=os.getenv("MODELD_POLICY_RKNN_INPUT_LAYOUT", "nhwc"),
)
```

Reject:

```text
missing core env -> fallback to all cores
invalid core -> auto mode
runtime error -> publish bad data
```

## 8.4 Fallback Logic

Pseudo-flow:

```python
try:
    out = rknn_runner.infer(inputs)
except Exception as e:
    cloudlog.exception("RKNN failed, falling back")
    out = fallback_runner.infer(inputs)
```

Fallback can be:

```text
TinygradRunner
ONNXRunner
CPU debug runner
```

---

# 9. Environment Brain

## 9.1 Dev Boot Environment

```bash
export USE_WEBCAM=1
export ROAD_CAM=0
export NO_DM=1
export NO_IMU=1
export WEBCAM_WIDTH=1280
export WEBCAM_HEIGHT=720
export WEBCAM_FPS=20
export WEBCAM_FOCAL=900.0
```

## 9.2 RKNN Environment

```bash
export OPENPILOT_MODELD_BACKEND=rknn
export RKNN_VISION_CORE=0
export RKNN_POLICY_CORE=1
export MODELD_VISION_RKNN_INPUT_LAYOUT=nhwc
export MODELD_POLICY_RKNN_INPUT_LAYOUT=nhwc
export MODELD_WARP_OUTPUT_LAYOUT=nhwc
```

## 9.3 RK3588 Stability Environment

```bash
export DISABLE_JIT_ALIAS_COPY=1
export CAMERAD_CORE_POOL=6
export MODELD_CORE_POOL=4,5,6,7
```

## 9.4 Example Launch Script

```bash
#!/usr/bin/env bash
set -e

export USE_WEBCAM=1
export ROAD_CAM=${ROAD_CAM:-0}
export NO_DM=1
export NO_IMU=1

export WEBCAM_WIDTH=1280
export WEBCAM_HEIGHT=720
export WEBCAM_FPS=20
export WEBCAM_FOCAL=900.0

export OPENPILOT_MODELD_BACKEND=rknn
export RKNN_VISION_CORE=0
export RKNN_POLICY_CORE=1
export MODELD_VISION_RKNN_INPUT_LAYOUT=nhwc
export MODELD_POLICY_RKNN_INPUT_LAYOUT=nhwc
export MODELD_WARP_OUTPUT_LAYOUT=nhwc

export DISABLE_JIT_ALIAS_COPY=1
export CAMERAD_CORE_POOL=6
export MODELD_CORE_POOL=4,5,6,7

./launch_openpilot.sh
```

---

# 10. Sysfs / Thermal / Frequency Brain

## 10.1 CPU Governor

Target sysfs:

```text
/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

Set:

```bash
echo userspace | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

Common target:

```text
A76 big cores: around 2.2-2.4 GHz if cooling allows
A55 little cores: around 1.8 GHz
```

## 10.2 NPU Frequency

Possible path:

```text
/sys/class/devfreq/fdab0000.npu/cur_freq
```

Target:

```text
1,000,000,000 Hz
```

Also inspect:

```bash
ls /sys/class/devfreq/
cat /sys/class/devfreq/*npu*/available_frequencies
cat /sys/class/devfreq/*npu*/cur_freq
```

## 10.3 Thermal Zones

Possible zones:

```text
/sys/class/thermal/thermal_zone0/temp  # SoC
/sys/class/thermal/thermal_zone1/temp  # GPU
/sys/class/thermal/thermal_zone2/temp  # NPU
```

Do not assume numbering blindly. Identify names:

```bash
for z in /sys/class/thermal/thermal_zone*; do
  echo "$z: $(cat $z/type 2>/dev/null) $(cat $z/temp 2>/dev/null)"
done
```

## 10.4 Fan PWM

Possible path:

```text
/sys/class/hwmon/hwmon2/pwm1
```

But `hwmon2` can change. Search:

```bash
find /sys/class/hwmon -name "pwm*"
```

Thermal policy:

```text
<65°C: low fan
65-75°C: medium fan
75-85°C: high fan
>85°C: critical, reduce load or warn
```

---

# 11. Build Brain

## 11.1 Submodules

Always initialize:

```bash
git submodule update --init --recursive
```

Important submodules may include:

```text
cereal
msgq
opendbc
tinygrad
```

## 11.2 SCons

Common build:

```bash
scons -j$(nproc)
```

Some RK3588 forks may need:

```bash
QCOM=1 scons -j$(nproc)
```

Note:

```text
Only use QCOM=1 if the fork expects it for larch64/tinygrad/platform paths.
Do not blindly enable QCOM behavior if it turns on TICI-only services.
```

---

# 12. Validation Brain

## 12.1 Minimum Validation Before Calling RKNN “Working”

Do not trust “it runs” alone.

Required:

```text
1. modeld starts
2. RKNN models load
3. NPU cores assigned correctly
4. output values finite
5. output shapes match metadata
6. modelV2 publishes
7. planner receives sane modelV2
8. UI shows path/lane/road edge
9. fallback works when RKNN is disabled
10. no crash after restart
```

## 12.2 Cross-Runtime Correlation

Procedure:

```text
Run same 100+ frames through Tinygrad/ONNX.
Save reference outputs.
Run same frames through RKNN.
Compare outputs by named metadata slices.
```

Pass target:

```text
correlation > 0.995 for major vision/policy outputs
no NaN
no Inf
hidden state persists
```

Do not compare against FP16 ONNXRuntime CPU if known wrong for the fork. Use FP32 reference.

## 12.3 Stress Test

Minimum:

```text
1 hour continuous run
```

Monitor:

```bash
top
htop
watch -n 1 cat /sys/class/thermal/thermal_zone*/temp
watch -n 1 cat /sys/class/devfreq/*npu*/cur_freq
```

Watch for:

- camera frame drops
- modeld restart loop
- NPU errors
- memory leak
- CPU thermal throttling
- UI freeze
- VisionIPC disconnects

## 12.4 Recovery Test

Test manager recovery:

```bash
pkill -f modeld
pkill -f camerad
pkill -f webcamerad
```

Expected:

```text
manager restarts process
VisionIPC reconnects
modelV2 resumes
no permanent UI crash
```

## 12.5 CAN Test

If using SocketCAN:

```bash
ip link show
ip -details link show can0
candump can0
```

Set bitrate example:

```bash
sudo ip link set can0 down
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up
```

---

# 13. Known Quirks and Failure Modes

## 13.1 `get_device_type()` Returning `rk3588`

Symptom:

```text
KeyError in camera intrinsics / DEVICE_CAMERAS
```

Fix:

```python
get_device_type() -> "pc"
```

Or add a real RK3588 camera config everywhere needed.

## 13.2 Driver Monitoring Enabled Without Driver Cam

Symptom:

```text
dmonitoringmodeld waits forever or spins on VisionIPC
```

Fix:

```bash
export NO_DM=1
```

## 13.3 IMU Not Present

Symptom:

```text
location/sensord errors
```

Fix first boot:

```bash
export NO_IMU=1
```

Later add real IMU support.

## 13.4 RKNN Outputs NaN/Inf

Causes:

- bad conversion
- wrong input layout
- negative GatherND
- ReduceL2 overflow
- wrong calibration
- wrong metadata slicing

Fix:

```text
stop publishing output
fallback
inspect conversion
compare by slices
```

## 13.5 Hidden State All Zeros

Likely cause:

```text
NCHW/NHWC mismatch
```

Fix:

```python
np.transpose(x, (0, 2, 3, 1))
```

Then validate shapes.

## 13.6 Color / Model Looks Wrong

Likely cause:

```text
NV12 UV offset wrong
stride/padding mismatch
RGB/BGR/YUV mismatch
```

Fix:

```text
validate NV12 layout
dump test frame
compare CPU decoded image
check tight vs padded NV12
```

## 13.7 Panfrost / Rusticl OpenCL Problems

Possible issue:

```text
InvalidBitWidth: Invalid bit width in input: 128
```

Fix:

```text
Use CPU/LLVM fallback for that path.
Use RGA for preprocessing where possible.
Do not block RKNN integration on GPU OpenCL policy path.
```

## 13.8 FLOAT16 ONNXRuntime Is Not Always a Good Reference

If grouped convolution or specific ops are wrong in FP16 CPU reference, use FP32 ONNX reference.

---

# 14. Architecture Diagrams

## 14.1 Whole System Flow

```text
[IMX415 Sensor]
      |
      v
[MIPI CSI-2]
      |
      v
[Rockchip CSI2 DPHY]
      |
      v
[RKCIF / RKISP]
      |
      v
[V4L2 NV12 DMA-BUF]
      |
      +------------------------------+
      |                              |
      v                              v
[VisionIPC fd passing]          [EGLImage import]
      |                              |
      v                              v
[modeld]                       [Mali GPU / UI]
      |
      v
[RKNN Vision Core 0]
      |
      v
[RKNN Policy Core 1]
      |
      v
[metadata slicing]
      |
      v
[modelV2]
      |
      +-------------+--------------+
      |             |              |
      v             v              v
[plannerd]     [controlsd]     [selfdrived]
      |             |
      v             v
[plan]        [carControl]
                    |
                    v
              [CAN / Panda / SocketCAN]
                    |
                    v
              [Vehicle actuators]
```

## 14.2 Development Path

```text
USB camera or IMX415
  -> OpenCV
  -> numpy
  -> webcamerad
  -> VisionIPC
  -> modeld
  -> Tinygrad/ONNX/RKNN
  -> modelV2
```

Use only to make the repo boot.

## 14.3 Production Path

```text
IMX415
  -> RKISP
  -> V4L2 NV12 DMA-BUF
  -> VisionIPC fd
  -> modeld
  -> RKNN
  -> modelV2
```

---

# 15. AI Agent Work Instructions

When an AI agent works on this repo, it must follow this sequence.

## 15.1 First Read

Read:

```text
SECONDBRAIN.md
README.md
GOD.md
GOD2.md
audit.md
commit.md
```

If documents conflict:

```text
audit.md and latest SECONDBRAIN.md win for RK3588 production issues.
```

## 15.2 Before Editing

Find actual files:

```bash
find . -path "*modeld*" -maxdepth 5
find . -path "*hardware*" -maxdepth 5
find . -path "*camera*" -maxdepth 5
grep -R "OPENPILOT_MODELD_BACKEND" -n .
grep -R "RKNN" -n .
grep -R "USE_WEBCAM" -n .
grep -R "NO_DM" -n .
```

## 15.3 Forbidden AI Behavior

Do not:

- invent files without checking repo structure
- patch planner to hide model issues
- remove Tinygrad/ONNX fallback
- use `NPU_CORE_ALL` to “make it work”
- hardcode output slices
- remove validation because it fails
- claim zero-copy while still using OpenCV/numpy
- claim production-ready without validation artifacts

## 15.4 Required AI Output After Patching

Every patch should produce:

```text
1. What files changed
2. Why each file changed
3. How to run
4. How to validate
5. Fallback path still works or not
6. Known remaining gaps
```

---

# 16. Final Checklists

## 16.1 Boot Checklist

```text
[ ] Repo builds
[ ] Manager starts
[ ] UI starts
[ ] No TICI/comma hardware crash
[ ] USE_WEBCAM path works
[ ] NO_DM disables driver monitoring
[ ] NO_IMU disables IMU dependency
[ ] Camera feed visible
```

## 16.2 Camera Checklist

```text
[ ] IMX415 detected in dmesg
[ ] media-ctl graph correct
[ ] v4l2-ctl shows NV12 support
[ ] 1280x720 @ 20fps configured
[ ] tight NV12 layout handled
[ ] no OpenCV in production path
[ ] DMA-BUF fds exported
[ ] VisionIPC receives frames
```

## 16.3 RKNN Checklist

```text
[ ] driving_vision.rknn present
[ ] driving_policy.rknn present
[ ] metadata .pkl files present
[ ] metadata has input_shapes
[ ] metadata has output_slices
[ ] vision uses NPU core 0
[ ] policy uses NPU core 1
[ ] no NPU_CORE_AUTO
[ ] no NPU_CORE_ALL
[ ] np.isfinite checks active
[ ] runtime fallback active
[ ] no hardcoded semantic outputs[0]
```

## 16.4 Validation Checklist

```text
[ ] 100+ frame reference outputs saved
[ ] 100+ frame RKNN outputs saved
[ ] output correlation checked
[ ] hidden state persistence checked
[ ] modelV2 schema unchanged
[ ] planner receives sane model
[ ] UI path/lane visible
[ ] one-hour stress test passed
[ ] thermal log saved
[ ] restart/recovery test passed
```

## 16.5 Production Checklist

```text
[ ] IMX415 native V4L2 path
[ ] DMA-BUF zero-copy
[ ] RGA or GPU preprocess target documented
[ ] RKNN core assignment strict
[ ] fallback available
[ ] CPU load acceptable
[ ] NPU frequency locked or monitored
[ ] fan/thermal control working
[ ] CAN path verified
[ ] no schema/control hacks
```

---

# 17. Final Declaration

This file is the working second brain for RK3588 OpenPilot porting.

A correct RK3588 fork should:

```text
boot safely,
read one IMX415 road camera,
avoid driver-camera blocking,
run modeld with RKNN when selected,
preserve Tinygrad/ONNX fallback,
publish valid modelV2,
avoid planner/control hacks,
and move toward true DMA-BUF zero-copy production camera input.
```

If something fails, debug in this order:

```text
1. Boot/env gates
2. Camera detection
3. NV12 layout
4. VisionIPC frame delivery
5. RKNN model loading
6. Input layout
7. Output finite validation
8. Metadata slicing
9. modelV2 publishing
10. planner/control downstream
```

Do not call the port complete until validation artifacts exist.

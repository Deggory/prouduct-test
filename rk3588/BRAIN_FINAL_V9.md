# BRAIN.MD — The Omniscient RK3588 OpenPilot Brain

**Version:** 9.0 — Authoritative Final Master Reference  
**Classification:** Single Source of Truth  
**Target:** Orange Pi 5 / RK3588 / Sony IMX415 single road camera  
**Mission:** Map the complete neural, physical, and software architecture of Sunnypilot/OpenPilot on RK3588. This document defines the C++ RKNN runner architecture, strict sysfs frequency locking, and exact file-by-file patching instructions for any fork.

---

## PRIME DIRECTIVE

This document is the engineering reference for running OpenPilot/Sunnypilot on Rockchip RK3588.

### Absolute Rules

1. **Producer-side changes only.**  
   You may change how frames are captured by `camerad` and how inference is run by `modeld`.  
   You must **not** alter:
   - `cereal/log.capnp`
   - `modelV2` schema
   - planner math
   - control semantics
   - `controlsd`
   - `plannerd`
   - `loadyuv.cl`
   - `transform.cl`

2. **Metadata-driven execution only.**  
   Never hardcode tensor indices such as `outputs[0]`. Always read input shapes and output slices from `.pkl` metadata files.

3. **Fail-fast and fallback.**  
   Always validate NPU outputs with finite checks before publishing. If RKNN fails, fall back to ONNX/Tinygrad. Never silently publish garbage model data to the planner.

4. **Strict NPU core assignment.**  
   - Vision RKNN → NPU Core 0
   - Policy RKNN → NPU Core 1
   - Core 2 → optional / reserved

   Do **not** use `RKNN_NPU_CORE_0_1`, `RKNN_NPU_CORE_ALL`, or `NPU_CORE_AUTO` in production.

5. **C++ NPU runner.**  
   NPU inference should use a compiled C++ RKNN runner, `rknnmodel.cc`, wrapped with Cython, `rknnmodel_pyx.pyx`. Do not depend on pure Python `RKNNLite` for the production path.

6. **Hardware frequency locking.**  
   NPU and DDR/DMC frequencies must be locked at runtime through sysfs to avoid latency spikes.

---

## SECTION 1 — FILE-BY-FILE PATCH MAP

When forking any OpenPilot/Sunnypilot repo to RK3588, apply these changes file by file.

---

### 1.1 Hardware Abstraction Layer and Sysfs Frequency Locking

#### `system/hardware/__init__.py`

Add RK3588 detection.

```python
def _is_rk3588() -> bool:
    try:
        with open("/proc/device-tree/compatible", "r", encoding="utf-8", errors="ignore") as f:
            return "rk3588" in f.read().lower()
    except FileNotFoundError:
        return False

RK3588 = _is_rk3588()
PC = not TICI and not RK3588

if TICI:
    HARDWARE = Tici()
elif RK3588:
    HARDWARE = RK3588Hardware(detected=True)
else:
    HARDWARE = Pc()
```

#### `common/hardware/rk3588/hardware.py` or `system/hardware/rk3588/hardware.py`

Create a new `RK3588Hardware(HardwareBase)` class.

Critical rule:

```python
def get_device_type(self):
    return "pc"
```

This is required because many OpenPilot camera tables only have `"pc"` keys. Returning `"rk3588"` may cause `DEVICE_CAMERAS` lookup crashes.

Add safe sysfs helpers:

```python
def sudo_write(value: str, path: str) -> None:
    try:
        with open(path, "w") as f:
            f.write(str(value))
    except PermissionError:
        os.system(f"sudo sh -c 'echo {value} > {path}'")
    except FileNotFoundError:
        pass
```

Lock NPU and DDR/DMC frequency inside `initialize_hardware()`:

```python
def initialize_hardware(self):
    # Lock NPU to 1 GHz
    sudo_write("userspace", "/sys/class/devfreq/fdab0000.npu/governor")
    sudo_write("1000000000", "/sys/class/devfreq/fdab0000.npu/userspace/set_freq")

    # Lock DDR/DMC to 2.112 GHz
    sudo_write("userspace", "/sys/class/devfreq/dmc/governor")
    sudo_write("2112000000", "/sys/class/devfreq/dmc/userspace/set_freq")
```

Thermal and fan monitoring should include:

```text
/sys/class/thermal/thermal_zone0/temp
/sys/class/thermal/thermal_zone1/temp
/sys/class/thermal/thermal_zone2/temp
/sys/class/hwmon/hwmon2/pwm1
```

NPU load monitoring:

```text
/sys/kernel/debug/rknpu/load
```

---

### 1.2 Process Management and Core Pinning

#### `system/manager/process_config.py` or `selfdrive/manager/process_config.py`

Add environment gates:

```python
WEBCAM = os.getenv("USE_WEBCAM") is not None
NO_DM = os.getenv("NO_DM") is not None
NO_IMU = os.getenv("NO_IMU") is not None
```

Required behavior:

- `USE_WEBCAM=1` may use `webcamerad` for dev bring-up.
- `NO_DM=1` disables driver monitoring camera/model processes.
- `NO_IMU=1` prevents IMU/sensor startup from blocking a single-camera Orange Pi 5 boot.
- On production RK3588 camera path, use native `camerad` with V4L2 DMA-BUF.

#### `common/realtime.py`

Recommended process pinning:

```text
camerad → Core 6, SCHED_FIFO priority 53
modeld  → Cores 4,5,6,7, SCHED_FIFO priority 54
ui      → A55 / normal priority, GPU-bound
```

RK3588 core map:

```text
CPU 0-3 → Cortex-A55 little cores
CPU 4-7 → Cortex-A76 big cores
```

---

### 1.3 Camera and VisionIPC Zero-Copy HAL

#### `common/hardware/rk3588/camera/v4l2.py`

Implement V4L2 capture with DMA-BUF export.

Required operations:

1. Open the RKISP main path, usually `/dev/video0`.
2. Configure `V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE`.
3. Use `V4L2_PIX_FMT_NV12`.
4. Request MMAP buffers.
5. Export each buffer with `VIDIOC_EXPBUF`.
6. Pass the exported DMA-BUF fd to VisionIPC.

Production path:

```text
IMX415 → MIPI CSI-2 → RKISP → V4L2 MPLANE → NV12 DMA-BUF → VisionIPC
```

#### `common/hardware/rk3588/camera/csi.py`

Create an `IMX415Camera` class.

Recommended defaults:

```text
width  = 1280
height = 720
fps    = 20
format = NV12
```

#### `common/transformations/camera.py`

Set IMX415 intrinsics for PC/RK3588 compatibility:

```text
width  = 1280
height = 720
focal  = 900.0
```

Do not return `"rk3588"` from `get_device_type()` unless all camera tables are updated.

---

### 1.4 Model Inference: C++ RKNN Runner

#### New files

```text
selfdrive/modeld/runners/rknnmodel.cc
selfdrive/modeld/runners/rknnmodel.h
selfdrive/modeld/runners/rknnmodel_pyx.pyx
```

#### `rknnmodel.cc`

The C++ runner must:

1. Read the `.rknn` model file.
2. Call `rknn_init`.
3. Set strict core mask:
   - Vision: `RKNN_NPU_CORE_0`
   - Policy: `RKNN_NPU_CORE_1`
4. Query input/output counts dynamically.
5. Query input/output tensor attributes dynamically.
6. Set inputs with `rknn_inputs_set`.
7. Run inference with `rknn_run`.
8. Get outputs with `rknn_outputs_get`.
9. Copy every output into output buffers.
10. Release outputs with `rknn_outputs_release`.
11. Never assume only one output.
12. Never hardcode `outputs[0]` as the whole model result.

Skeleton:

```cpp
#include "selfdrive/modeld/runners/rknnmodel.h"

RKNNModel::RKNNModel(const std::string &model_path, int core_id) {
  std::string model_data = util::read_file(model_path);
  RKNN_CHECK(rknn_init(&ctx, (void*)model_data.data(), model_data.size(), 0, nullptr));

  if (core_id == 0) {
    RKNN_CHECK(rknn_set_core_mask(ctx, RKNN_NPU_CORE_0));
  } else if (core_id == 1) {
    RKNN_CHECK(rknn_set_core_mask(ctx, RKNN_NPU_CORE_1));
  } else if (core_id == 2) {
    RKNN_CHECK(rknn_set_core_mask(ctx, RKNN_NPU_CORE_2));
  } else {
    throw std::runtime_error("Invalid RKNN NPU core id");
  }

  RKNN_CHECK(rknn_query(ctx, RKNN_QUERY_IN_OUT_NUM, &io_num, sizeof(io_num)));
  query_input_attrs();
  query_output_attrs();
}
```

#### `rknnmodel_pyx.pyx`

Expose the C++ runner to Python/modeld. It should:

- Accept model path.
- Accept core id.
- Accept ordered numpy inputs.
- Return one or more numpy outputs.
- Avoid Python-side RKNNLite for production.

#### `selfdrive/modeld/runners/__init__.py`

Add RKNN backend selection without letting THNEED silently override RKNN when RKNN is explicitly requested.

Recommended backend priority:

```text
OPENPILOT_MODELD_BACKEND=rknn → RKNN
OPENPILOT_MODELD_BACKEND=onnx → ONNX
OPENPILOT_MODELD_BACKEND=tinygrad/thneed → THNEED
unset → existing repo default
```

#### `selfdrive/modeld/SConscript`

Add RKNN build/linking:

```python
rknn_lib = []

if device == "RK3588" or arch in ("aarch64", "larch64"):
    rknn_lib += ["rknnrt"]
    common_src += ["runners/rknnmodel.cc"]

# Build Cython wrapper
lenvCython.Program(
    "runners/rknnmodel_pyx.so",
    "runners/rknnmodel_pyx.pyx",
    LIBS=[rknnmodel_lib, rknn_lib, *cython_libs],
    RPATH=f"{Dir('#').abspath}/third_party/rknpu/aarch64",
)
```

#### `selfdrive/modeld/modeld.py` or `sunnypilot/modeld_v2/modeld.py`

Modeld must:

- Read `OPENPILOT_MODELD_BACKEND`.
- Load `driving_vision.rknn` and `driving_policy.rknn`.
- Load `.pkl` metadata.
- Use metadata for input ordering, shapes, and output slices.
- Validate finite outputs.
- Fall back to Tinygrad/ONNX if RKNN fails.
- Preserve hidden-state behavior.
- Preserve `modelV2` schema.

---

### 1.5 Model Files

Recommended layout:

```text
selfdrive/modeld/models/
├── driving_vision.rknn
├── driving_policy.rknn
├── driving_vision_metadata.pkl
├── driving_policy_metadata.pkl
├── driving_vision.onnx
└── driving_policy.onnx
```

Do not depend on a monolithic `supercombo.rknn` unless the repo already uses monolithic supercombo and metadata matches it.

---

### 1.6 Location and Sensors

#### `selfdrive/locationd/locationd.py`

Add:

```python
NO_IMU = os.getenv("NO_IMU") is not None
```

For a single-camera Orange Pi 5 dev bring-up, the Kalman filter can run from:

```text
cameraOdometry
carState
liveCalibration
```

Do not let missing IMU block the whole system during early bring-up.

---

## SECTION 2 — C++ RKNN RUNNER ARCHITECTURE: THE BUKAPILOT METHOD

Bukapilot’s KA2 branch is the reference idea:

```text
repo:   kommuai/bukapilot
branch: release_ka2
target: KA2 / RK3588
runner: selfdrive/modeld/runners/rknnmodel.cc
freq:   system/hardware/ka2/hardware.py
```

Useful concepts to copy:

```text
KA2 hardware abstraction idea
RKNN C++ runner structure
Cython wrapper pattern
SCons rknnrt linking
NPU/DMC sysfs frequency locking
NPU load reading from /sys/kernel/debug/rknpu/load
modeld runner selection pattern
```

Unsafe parts to avoid:

```text
single-output assert
hardcoded outputs[0]
RKNN_NPU_CORE_0_1 for production
hardcoded input shapes
THNEED silently taking priority when RKNN is requested
monolithic supercombo assumption if your repo uses split vision/policy models
```

---

### 2.1 C++ RKNN Runner Flow

```text
.rknn file
  ↓
read into memory
  ↓
rknn_init()
  ↓
rknn_set_core_mask()
  ↓
rknn_query(input/output count)
  ↓
rknn_query(input/output tensor attrs)
  ↓
rknn_inputs_set()
  ↓
rknn_run()
  ↓
rknn_outputs_get()
  ↓
copy outputs
  ↓
finite validation
  ↓
metadata slicing
  ↓
modelV2 publish
```

---

### 2.2 Strict Core Assignment

Use explicit core selection:

```cpp
switch (core_id) {
  case 0:
    RKNN_CHECK(rknn_set_core_mask(ctx, RKNN_NPU_CORE_0));
    break;
  case 1:
    RKNN_CHECK(rknn_set_core_mask(ctx, RKNN_NPU_CORE_1));
    break;
  case 2:
    RKNN_CHECK(rknn_set_core_mask(ctx, RKNN_NPU_CORE_2));
    break;
  default:
    throw std::runtime_error("Invalid NPU core id");
}
```

Do not use:

```cpp
RKNN_NPU_CORE_0_1
RKNN_NPU_CORE_0_1_2
RKNN_NPU_CORE_ALL
```

for production driving inference.

---

### 2.3 Multi-Output Handling

Wrong:

```cpp
assert(io_num.n_output == 1);
memcpy(output, (float *)rknn_outputs[0].buf, rknn_outputs[0].size);
```

Correct:

```cpp
for (uint32_t i = 0; i < io_num.n_output; ++i) {
    outputs[i].want_float = 1;
    outputs[i].index = i;
    outputs[i].is_prealloc = 0;
}

RKNN_CHECK(rknn_outputs_get(ctx, io_num.n_output, outputs.data(), nullptr));

for (uint32_t i = 0; i < io_num.n_output; ++i) {
    copy_output(i, outputs[i].buf, outputs[i].size);
}

RKNN_CHECK(rknn_outputs_release(ctx, io_num.n_output, outputs.data()));
```

---

## SECTION 3 — HARDWARE-LEVEL IMPLEMENTATION DETAILS

### 3.1 V4L2 Media Graph and DMA-BUF Camera Pipeline

Target route:

```text
imx415
  → rockchip-csi2-dphy
  → rkcif
  → rkisp_mainpath
  → /dev/video0
```

Native capture sequence:

```text
open("/dev/video0", O_RDWR)
VIDIOC_S_FMT with V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE
V4L2_PIX_FMT_NV12
VIDIOC_REQBUFS
VIDIOC_QUERYBUF
mmap
VIDIOC_EXPBUF
VIDIOC_QBUF
VIDIOC_STREAMON
loop:
  VIDIOC_DQBUF
  pass dmabuf_fd to VisionIPC
  VIDIOC_QBUF
```

Production target:

```text
IMX415 NV12 DMA-BUF
  ├── VisionIPC → modeld → RKNN
  └── EGLImage  → UI
```

---

### 3.2 Thermal and Power Management

Recommended sysfs paths:

```text
CPU governor:
  /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

NPU governor:
  /sys/class/devfreq/fdab0000.npu/governor

NPU target frequency:
  /sys/class/devfreq/fdab0000.npu/userspace/set_freq

NPU current frequency:
  /sys/class/devfreq/fdab0000.npu/cur_freq

DDR/DMC governor:
  /sys/class/devfreq/dmc/governor

DDR/DMC target frequency:
  /sys/class/devfreq/dmc/userspace/set_freq

DDR/DMC current frequency:
  /sys/class/devfreq/dmc/cur_freq

NPU load:
  /sys/kernel/debug/rknpu/load

Thermals:
  /sys/class/thermal/thermal_zone0/temp
  /sys/class/thermal/thermal_zone1/temp
  /sys/class/thermal/thermal_zone2/temp

Fan PWM:
  /sys/class/hwmon/hwmon2/pwm1
```

Recommended values:

```text
NPU: 1000000000 Hz
DMC: 2112000000 Hz
```

Thermal policy:

```text
Below 65°C: normal
65–75°C: increase fan
75–85°C: full fan, warning
85°C+: critical, expect throttling
```

---

### 3.3 EGLImage GPU Rendering

To render the camera feed without CPU copy:

```cpp
EGLImageKHR image = eglCreateImageKHR(
    display,
    EGL_NO_CONTEXT,
    EGL_LINUX_DMA_BUF_EXT,
    nullptr,
    attributes
);

glEGLImageTargetTexture2DOES(GL_TEXTURE_EXTERNAL_OES, image);
```

Attributes must include:

```text
EGL_LINUX_DRM_FOURCC_EXT = DRM_FORMAT_NV12
EGL_DMA_BUF_PLANE0_FD_EXT = dmabuf_fd
EGL_DMA_BUF_PLANE0_OFFSET_EXT = 0
EGL_DMA_BUF_PLANE0_PITCH_EXT = stride
EGL_DMA_BUF_PLANE1_FD_EXT = dmabuf_fd
EGL_DMA_BUF_PLANE1_OFFSET_EXT = uv_offset
EGL_DMA_BUF_PLANE1_PITCH_EXT = stride
```

---

## SECTION 4 — RKNN MODEL CONVERSION MASTER GUIDE

### 4.1 Conversion Pipeline

```text
ONNX
  ↓
onnxsim simplify
  ↓
opset check / downgrade to supported RKNN Toolkit version
  ↓
graph rewrites
  ↓
calibration dataset
  ↓
INT8 RKNN build
  ↓
.rknn export
  ↓
validation against FP32 ONNX/Tinygrad reference
```

---

### 4.2 Fatal RKNN Conversion Bugs and Fixes

#### 1. `Gelu(approximate="tanh")`

Problem:

```text
RKNN may not map tanh-approximate GELU correctly.
```

Fix:

```text
Rewrite GELU into primitive Mul/Add/Tanh operations before RKNN conversion.
```

#### 2. UINT8 Input Rejection

Problem:

```text
Vision ONNX may use UINT8 inputs.
RKNN conversion can reject unsupported dtype.
```

Fix:

```text
Change graph inputs to FLOAT16/FLOAT32.
Remove direct input Cast nodes.
```

#### 3. ReduceL2 FP16 Overflow

Problem:

```text
Hidden-state L2 normalization may overflow FP16 intermediate range.
```

Fix:

```text
ReduceL2(x) → ReduceL2(x / 32) * 32
```

#### 4. GatherND Negative Index

Problem:

```text
Policy model may use GatherND with negative indices.
RKNN can mishandle negative indexing and produce invalid outputs.
```

Fix:

```text
Rewrite to Slice(features_buffer, axis=1, starts=16, ends=25)
```

#### 5. NCHW vs NHWC Layout

Problem:

```text
RKNN hardware usually prefers NHWC.
Wrong layout can produce zero or corrupted hidden_state.
```

Fix:

```text
Set RKNN config data_format to NHWC where needed.
Transpose tensors before inference only when metadata says so.
```

Example:

```python
x_nhwc = np.transpose(x_nchw, (0, 2, 3, 1))
```

---

### 4.3 RKNN Toolkit Config

Recommended starting config:

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

Use `kl_divergence` if validation shows better accuracy with your dataset.

---

### 4.4 Calibration Dataset

Place calibration samples under:

```text
tools/rknn/dataset/
```

Vision examples:

```text
input_imgs_000.npy
big_input_imgs_000.npy
...
```

Policy examples:

```text
features_buffer_000.npy
desire_000.npy
traffic_convention_000.npy
lateral_control_params_000.npy
prev_desired_curv_000.npy
...
```

Use real frames from the same preprocessing path you will use at runtime.

---

## SECTION 5 — CAMERA AND PREPROCESSING SECRETS

### 5.1 NV12 Layout Bug

Webcam / standard V4L2 tight NV12:

```text
1280 × 720 × 1.5 = 1,382,400 bytes
```

Qualcomm/OpenPilot padded NV12 may expect:

```text
stride = 1280
y_height = 736
```

If UV offset is wrong, the model receives corrupted image data.

Required fix:

```text
Add get_modeld_nv12_info() that returns tight NV12 layout when:
- USE_WEBCAM=1
- native V4L2 RK3588 path is active
```

---

### 5.2 Forbidden CPU Production Path

Do not use this in production:

```text
IMX415
  → OpenCV BGR
  → bgr_to_nv12()
  → numpy copies
  → RKNN
```

Reason:

```text
This adds CPU conversion/copy overhead and destroys the latency target.
```

Allowed only for early boot/testing:

```text
USE_WEBCAM=1 dev bring-up
```

---

### 5.3 Target Production Path

```text
IMX415
  → MIPI CSI-2
  → RKISP
  → V4L2 MPLANE
  → NV12 DMA-BUF
  ├── VisionIPC → modeld → C++ RKNN runner
  └── EGLImage  → UI
```

Optional optimization:

```text
RGA resize/convert using DMA-BUF fd
```

RGA must work on DMA-BUF fds, not numpy arrays.

---

## SECTION 6 — SYSTEM CONFIGURATION AND ENVIRONMENT VARIABLES

### 6.1 Orange Pi 5 Device Mapping

Common mapping:

```text
/dev/video0  → RKISP main path / IMX415 road camera
/dev/video11 → RKISP self path / preview or alternate path
/dev/video31 → RGA hardware accelerator
```

Always verify on your board:

```bash
v4l2-ctl --list-devices
media-ctl -p
```

---

### 6.2 Master Environment Variables

Development bring-up:

```bash
export USE_WEBCAM=1
export ROAD_CAM=0
export WEBCAM_WIDTH=1280
export WEBCAM_HEIGHT=720
export WEBCAM_FPS=20
export WEBCAM_FOCAL=900.0
export NO_DM=1
export NO_IMU=1
```

RKNN backend:

```bash
export OPENPILOT_MODELD_BACKEND=rknn
export RKNN_VISION_CORE=0
export RKNN_POLICY_CORE=1
export MODELD_VISION_RKNN_INPUT_LAYOUT=nhwc
export MODELD_WARP_OUTPUT_LAYOUT=nhwc
```

Mali/OpenCL stability:

```bash
export DISABLE_JIT_ALIAS_COPY=1
```

Force fallback for debugging:

```bash
export OPENPILOT_MODELD_BACKEND=onnx
```

---

### 6.3 UI Adaptations

OpenPilot UI may assume comma-style resolutions. Orange Pi 5 HDMI may use:

```text
800×400
1280×720
1920×1080
```

Patch UI scaling only if required. Do not change model/planner logic for UI layout issues.

---

### 6.4 Build System

Typical commands:

```bash
git submodule update --init --recursive
scons -j$(nproc)
```

If the repo expects larch64/QCOM flags:

```bash
QCOM=1 scons -j$(nproc)
```

For RKNN C++ runner, make sure the runtime library is available:

```text
third_party/rknpu/aarch64/librknnrt.so
```

or installed system-wide where the dynamic linker can find it.

---

## SECTION 7 — VALIDATION AND DEPLOYMENT PROTOCOLS

### 7.1 Cross-Runtime Validation

Before merging RKNN:

1. Run 100+ frames with ONNX/Tinygrad.
2. Save raw model outputs.
3. Run the exact same frames with RKNN.
4. Compare per-output correlation.
5. Verify hidden state persistence.
6. Verify `modelV2` schema remains identical.
7. Verify no `NaN` or `Inf`.

Pass criteria:

```text
vision output correlation > 0.995
policy output correlation > 0.995
zero invalid outputs
no modelV2 schema drift
```

---

### 7.2 Runtime Stress Test

Minimum test:

```text
1 hour continuous run
```

Monitor:

```text
modeld FPS / frame time
RKNN vision latency
RKNN policy latency
camera frame drops
CPU usage
NPU load
DMC frequency
temperature
memory growth
manager restarts
```

Recovery tests:

```text
kill modeld
kill camerad / webcamerad
disconnect/reconnect camera if possible
restart manager
```

The system should recover without publishing invalid model output.

---

### 7.3 CAN and Vehicle Bring-Up

For your current single-camera/lateral-first setup:

```text
Start with lateral-only.
Keep longitudinal/radar disabled unless the car path is validated.
Use Panda or SocketCAN only after modeld/camera are stable.
```

Required car signals before safe lateral testing:

```text
vehicle speed
steering angle
steering torque / driver torque
brake pressed
gas pressed
gear / drive state
cruise or MADS state if used
```

---

### 7.4 Known Quirks and Drift Log

#### IMU drain commented out

Some RK3588 ports intentionally run without physical IMU at first. The filter can rely on:

```text
cameraOdometry
carState
liveCalibration
```

#### Driver monitoring spin-wait

If `NO_DM=0` and no driver camera exists, `dmonitoringmodeld` may wait forever. Use:

```bash
export NO_DM=1
```

#### Mali/Panfrost OpenCL limitations

Mali-G610 via Panfrost/Rusticl may work for some preprocessing but fail on some policy graph patterns. Keep ONNX/Tinygrad fallback until RGA/RKNN path is stable.

#### FP16 ONNXRuntime is not a reference

Use FP32 ONNX/Tinygrad as validation baseline. FP16 CPU execution can be wrong for some grouped convolutions.

#### Git/doc drift

Never trust old docs or commit names blindly. Always inspect the current repo files.

---

## SECTION 8 — ARCHITECTURAL FLOW DIAGRAM

```text
[IMX415 Sensor]
      ↓ MIPI CSI-2
[RKISP]
      ↓ V4L2
[NV12 DMA-BUF]
      ├──────────────────────────────┐
      ↓                              ↓
[VisionIPC]                      [EGLImage]
      ↓                              ↓
[modeld.py]                       [UI/Qt]
      ↓
┌──────────────────────────────┬──────────────────────────────┐
│ C++ RKNN Vision Runner        │ C++ RKNN Policy Runner        │
│ driving_vision.rknn           │ driving_policy.rknn           │
│ NPU Core 0                    │ NPU Core 1                    │
│ ~8–12 ms                      │ ~2–5 ms                       │
└──────────────────────────────┴──────────────────────────────┘
      ↓
[Metadata Slicing]
      ↓
[Finite Output Validation]
      ↓
[modelV2 message]
      ↓
┌─────────────┬──────────────┬──────────────┐
│ plannerd    │ controlsd    │ selfdrived   │
└─────────────┴──────────────┴──────────────┘
      ↓
[Panda / SocketCAN]
      ↓
[Vehicle Actuators]
```

---

## SECTION 9 — STEP-BY-STEP PORTING ORDER

Do not ask an AI agent to port everything at once.

Use this order:

```text
1. Boot repo on Orange Pi 5 in PC/webcam mode.
2. Disable driver monitoring and IMU blockers.
3. Add RK3588 hardware HAL and frequency locking.
4. Set IMX415 single-camera defaults and intrinsics.
5. Confirm VisionIPC receives one road camera stream.
6. Add model backend selector.
7. Add ONNX/Tinygrad fallback.
8. Add C++ RKNN runner skeleton.
9. Link librknnrt in SCons.
10. Run driving_vision.rknn on NPU Core 0.
11. Run driving_policy.rknn on NPU Core 1.
12. Validate outputs against ONNX/Tinygrad.
13. Add finite checks and runtime fallback.
14. Replace dev OpenCV path with V4L2 DMA-BUF.
15. Add RGA/EGL zero-copy only after modeld is correct.
```

---

## SECTION 10 — VS CODE / AI AGENT PROMPT

Paste this into VS Code AI/Claude Code/Copilot when starting the port:

```text
Read ai/BRAIN.md fully before editing anything.

Goal:
Port this current Sunnypilot/OpenPilot repo to Orange Pi 5 / RK3588 with one Sony IMX415 road camera and split RKNN models.

Target:
- Orange Pi 5
- RK3588
- single IMX415 road camera
- no driver monitoring camera
- optional NO_IMU bring-up mode
- driving_vision.rknn on NPU Core 0
- driving_policy.rknn on NPU Core 1
- C++ RKNN runner wrapped by Cython
- ONNX/Tinygrad fallback if RKNN fails

Hard rules:
- Do not modify cereal/log.capnp.
- Do not modify modelV2 schema.
- Do not modify plannerd.
- Do not modify controlsd.
- Do not modify loadyuv.cl.
- Do not modify transform.cl.
- Do not hardcode outputs[0].
- Do not assume one output.
- Do not use RKNN_NPU_CORE_ALL, RKNN_NPU_CORE_0_1, or NPU_CORE_AUTO in production.
- Read model metadata .pkl for shapes and output slices.
- Validate all model outputs with finite checks.

First task:
Inspect the repo and create ai/RK3588_PORT_PLAN.md.

The plan must include:
1. current modeld path
2. current camerad/webcamerad path
3. current hardware detection path
4. current process_config path
5. current model file layout
6. current fallback runners
7. files that must be patched
8. risks
9. exact milestone order
10. test commands for each milestone

Do not edit source code until the plan is approved.
```

---

## FINAL DECLARATION

This document is the final engineering guide for the Orange Pi 5 / RK3588 OpenPilot/Sunnypilot port.

Any AI agent or engineer must:

```text
1. Read this document fully.
2. Apply only producer-side changes first.
3. Keep planner/control/schema untouched.
4. Use strict RKNN core assignment.
5. Use C++ RKNN runner for production.
6. Lock NPU and DMC frequencies.
7. Validate against ONNX/Tinygrad.
8. Publish modelV2 only after finite output validation.
9. Preserve fallback paths.
10. Avoid unsafe Bukapilot assumptions while reusing its useful KA2/RK3588 ideas.
```

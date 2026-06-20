# BRAIN.MD — The Omniscient RK3588 OpenPilot Brain

**Version:** 10.4 — Final Repo-Ready Master Reference  
**Classification:** Single Source of Truth  
**Target:** Orange Pi 5 / RK3588 / Sony IMX415 single road camera  
**Mission:** Map the complete neural, physical, and software architecture of Sunnypilot/OpenPilot on RK3588. This document defines the C++ RKNN runner architecture, strict sysfs frequency locking, V4L2 plane auto-detection, VisionIPC-safe camera bring-up, RKNN validation, and exact file-by-file patching instructions for any fork.

---

# PRIME DIRECTIVE

This document is the engineering reference for running OpenPilot/Sunnypilot on Rockchip RK3588 with one IMX415 road camera.

The goal is not to rewrite OpenPilot. The goal is to replace only the hardware producer side:

```text
camera capture path
model inference backend
hardware/frequency setup
```

The following must remain semantically compatible with upstream OpenPilot/Sunnypilot:

```text
VisionIPC stream contracts
roadCameraState timing
DrivingModelFrame.prepare()
modelV2 schema
planner inputs/outputs
controlsd behavior
Panda / safety behavior
```

---

# ABSOLUTE RULES

## 1. Producer-side changes only

You may change how frames are captured by `camerad` / `webcamerad` / `v4l2d`, and how inference is run by `modeld`.

You must **not** alter:

```text
cereal/log.capnp
modelV2 schema
planner math
control semantics
controlsd
plannerd
loadyuv.cl
transform.cl
DrivingModelFrame.prepare() semantics
```

## 2. Metadata-driven execution only

Never hardcode tensor indices such as:

```text
outputs[0]
```

Always read:

```text
input names
input shapes
input dtype
output names
output slices
hidden-state layout
```

from the model metadata `.pkl` files.

Outputs must be mapped by metadata name/order, not by guesses.

## 3. Fail-fast and fallback

Always validate model outputs before publishing:

```text
C++ runner: std::isfinite()
Python/modeld: np.isfinite()
```

If RKNN fails:

```text
1. stop publishing RKNN result immediately
2. switch to ONNX/Tinygrad fallback
3. reset hidden state safely
4. log the failure reason to cloudlog
5. keep modelV2 schema unchanged
```

Never silently publish garbage data to planner/controlsd.

## 4. Strict RKNN NPU core assignment

Production assignment:

```text
driving_vision.rknn  → RKNN_NPU_CORE_0
driving_policy.rknn  → RKNN_NPU_CORE_1
NPU Core 2           → optional/reserved
```

Never use these for production driving inference:

```text
RKNN_NPU_CORE_0_1
RKNN_NPU_CORE_0_1_2
RKNN_NPU_CORE_ALL
NPU_CORE_AUTO
```

Optional testing environment variables may exist:

```bash
export RKNN_VISION_CORE=0
export RKNN_POLICY_CORE=1
```

But the code must reject invalid values:

```text
AUTO
ALL
0_1
0_1_2
```

## 5. C++ RKNN runner for production

Production NPU inference must use:

```text
selfdrive/modeld/runners/rknnmodel.cc
selfdrive/modeld/runners/rknnmodel.h
selfdrive/modeld/runners/rknnmodel_pyx.pyx
```

Do not depend on pure Python `RKNNLite` for the production path.

Python RKNNLite is acceptable only for early testing/debug.

## 6. Hardware frequency locking

NPU and DDR/DMC frequencies must be locked through a root-owned boot mechanism:

```text
systemd service
udev rule
boot script
root-launched manager setup
```

Do not depend on interactive `sudo` from `managerd` or `modeld`.

## 7. Camera device detection

Never assume `/dev/video0`.

Always detect road camera from:

```text
ROAD_CAM environment variable
media-ctl -p
v4l2-ctl --list-devices
v4l2-ctl --list-formats-ext
```

For Deggory Orange Pi 5 IMX415 setup, default road camera is:

```text
/dev/video11
```

Always verify whether the selected node is mainpath/selfpath with:

```bash
media-ctl -p
```

---

# SECTION 1 — FILE-BY-FILE PATCH MAP

## 1.1 Hardware abstraction layer and frequency locking

### `system/hardware/__init__.py`

Add RK3588 detection using device tree.

Example:

```python
def _is_rk3588() -> bool:
    try:
        with open("/proc/device-tree/compatible", "r", encoding="utf-8", errors="ignore") as f:
            return "rk3588" in f.read().lower()
    except FileNotFoundError:
        return False

RK3588 = _is_rk3588()
```

Then map:

```python
if TICI:
    HARDWARE = Tici()
elif RK3588:
    HARDWARE = RK3588Hardware(detected=True)
else:
    HARDWARE = Pc()
```

### `common/hardware/rk3588/hardware.py` or `system/hardware/rk3588/hardware.py`

Create:

```python
class RK3588Hardware(HardwareBase):
    ...
```

Critical compatibility rule:

```python
def get_device_type(self):
    return "pc"
```

This is a temporary compatibility hack because many OpenPilot camera tables use `"pc"` keys.

Cleaner long-term fix:

```text
1. publish roadCameraState.sensor = "imx415"
2. add DEVICE_CAMERAS[("pc", "imx415")]
3. later add DEVICE_CAMERAS[("rk3588", "imx415")]
4. only then return "rk3588" from get_device_type()
```

### Dynamic sysfs detection

Do not hardcode one sysfs path. Search dynamically.

NPU paths may look like:

```text
/sys/class/devfreq/fdab0000.npu/
```

DMC/DDR paths may look like:

```text
/sys/class/devfreq/dmc/
```

Search patterns:

```text
/sys/class/devfreq/*npu*
/sys/class/devfreq/*dmc*
/sys/class/devfreq/*ddr*
```

Recommended locked values:

```text
NPU: 1000000000 Hz
DMC: 2112000000 Hz
```

Thermal/fan detection:

```text
/sys/class/thermal/thermal_zone*/temp
/sys/class/hwmon/hwmon*/name
/sys/class/hwmon/hwmon*/pwm*
```

Do not hardcode:

```text
/sys/class/hwmon/hwmon2/pwm1
```

Thermal policy:

```text
below 65°C  → normal
65–75°C     → increase fan
75–85°C     → full fan / warning
85°C+       → critical / expect throttling
```

NPU load:

```text
/sys/kernel/debug/rknpu/load
```

---

## 1.2 Process management and core pinning

### `system/manager/process_config.py` or `selfdrive/manager/process_config.py`

Required environment gates:

```python
WEBCAM = os.getenv("USE_WEBCAM") is not None
NO_DM = os.getenv("NO_DM") is not None
NO_IMU = os.getenv("NO_IMU") is not None
```

Required behavior:

```text
USE_WEBCAM=1 → may use tools/webcam/webcamerad for bring-up
NO_DM=1      → disables driver monitoring camera/model processes
NO_IMU=1     → prevents missing IMU from blocking Orange Pi 5 bring-up
```

Production RK3588 camera path should use native V4L2 capture, not PyAV/OpenCV.

### `common/realtime.py`

Recommended RK3588 process pinning:

```text
CPU 0-3 → Cortex-A55 little cores
CPU 4-7 → Cortex-A76 big cores
```

Recommended assignment:

```text
camerad → Core 6, SCHED_FIFO priority 53
modeld  → Cores 4,5,6,7, SCHED_FIFO priority 54
ui      → A55/normal priority, GPU-bound
```

---

## 1.3 Camera and VisionIPC

### Current development path

Your current working path may be:

```text
IMX415
→ RKISP kernel driver
→ /dev/video11
→ tools/webcam/camera.py
→ PyAV/OpenCV
→ BGR/RGB conversion
→ NV12 conversion
→ VisionIPC
→ modeld
→ UI/model output
```

This path is allowed only for initial bring-up.

Production must replace:

```text
tools/webcam/camera.py
PyAV/OpenCV
BGR/RGB conversion
BGR/RGB → NV12 conversion
```

with native V4L2 capture.

### `common/hardware/rk3588/camera/v4l2.py`

Implement native V4L2 capture.

Required auto-detection:

```text
If camera reports single-plane NV12:
  use V4L2_BUF_TYPE_VIDEO_CAPTURE
  use V4L2_PIX_FMT_NV12

If camera reports multi-plane NV12M:
  use V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE
  use V4L2_PIX_FMT_NV12M
```

For every buffer, read:

```text
bytesperline
sizeimage
data_offset
plane count
stride
offset
fd
```

### Buffer ownership rule

First milestone:

```text
V4L2 frame
→ copy into VisionIPC-owned buffer
→ modeld consumes normal VisionIPC buffer
```

Second milestone:

```text
V4L2 DMA-BUF fd
→ VisionIPC fd passing/import
→ EGLImage / RKNN memory APIs
```

Never requeue a V4L2 buffer with `VIDIOC_QBUF` until the consumer has finished or the data has been copied.

Do not assume current VisionIPC already supports external V4L2 DMA-BUF lifetime tracking.

### `common/hardware/rk3588/camera/csi.py`

Create:

```text
IMX415Camera
```

Recommended bring-up defaults:

```text
width  = 1280
height = 720
fps    = 20
format = NV12 or NV12M detected at runtime
```

### `common/transformations/camera.py`

Temporary bring-up:

```text
Override DEVICE_CAMERAS[("pc", "unknown")] only when IMX415/RK3588 env is active.
```

Better:

```text
roadCameraState.sensor = "imx415"
DEVICE_CAMERAS[("pc", "imx415")]
```

Future clean version:

```text
DEVICE_CAMERAS[("rk3588", "imx415")]
```

Recommended initial intrinsics:

```text
width  = 1280
height = 720
focal  = 900.0
```

These must later be calibrated for the real lens.

### `selfdrive/modeld/models/commonmodel.cc`

Usually related files:

```text
selfdrive/modeld/models/commonmodel.cc
selfdrive/modeld/models/commonmodel_pyx.pyx
selfdrive/modeld/models/commonmodel_pyx.py
```

`DrivingModelFrame.prepare()` must remain semantically identical.

Preserve:

```text
temporal frame buffer
warp matrix behavior
YUV layout
frame stacking
stride
uv_offset
frame order
OpenCL transform/loadyuv behavior
```

Do not replace OpenPilot model preprocessing with letterbox.

---

## 1.4 Model inference with C++ RKNN runner

### New files

```text
selfdrive/modeld/runners/rknnmodel.cc
selfdrive/modeld/runners/rknnmodel.h
selfdrive/modeld/runners/rknnmodel_pyx.pyx
```

### `rknnmodel.cc`

Must do:

```text
1. read .rknn model into memory
2. rknn_init(&ctx, model_data, model_size, 0, nullptr)
3. rknn_set_core_mask(ctx, strict_core)
4. rknn_query input/output count
5. rknn_query input/output tensor attributes
6. validate input count/name/dtype/layout/size
7. rknn_inputs_set()
8. rknn_run()
9. rknn_outputs_get()
10. validate every output buffer size
11. validate finite float outputs with std::isfinite()
12. copy every output
13. rknn_outputs_release()
14. rknn_destroy()
```

Never assume one output.

Wrong:

```cpp
assert(io_num.n_output == 1);
memcpy(output, outputs[0].buf, outputs[0].size);
```

Correct:

```cpp
for (uint32_t i = 0; i < io_num.n_output; ++i) {
  outputs[i].index = i;
  outputs[i].want_float = 1;
}
```

### `rknnmodel_pyx.pyx`

Expose C++ runner to Python/modeld.

Must verify before inference:

```text
input count
input order
input name
dtype
layout
byte size
contiguous memory
finite float inputs
```

Must verify after inference:

```text
output count
output byte size
finite outputs
metadata mapping
```

### `selfdrive/modeld/SConscript`

Add:

```text
rknnmodel.cc
rknnmodel_pyx.pyx
librknnrt.so
rknn_api.h include path
runtime RPATH or LD_LIBRARY_PATH support
```

### `selfdrive/modeld/modeld.py`

Backend selection:

```text
OPENPILOT_MODELD_BACKEND=rknn      → RKNN
OPENPILOT_MODELD_BACKEND=onnx      → ONNX
OPENPILOT_MODELD_BACKEND=tinygrad  → Tinygrad
unset                              → repo default
```

If RKNN is explicitly requested, do not allow THNEED/Tinygrad to silently override it.

Modeld must:

```text
load driving_vision.rknn
load driving_policy.rknn
load .pkl metadata
preserve hidden state behavior
validate finite outputs
fallback to ONNX/Tinygrad on failure
publish unchanged modelV2 schema
```

---

## 1.5 Model files and layout

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

Do not mix:

```text
monolithic supercombo.rknn
```

with split:

```text
driving_vision.rknn
driving_policy.rknn
```

unless metadata and parser match exactly.

---

## 1.6 RKNN runtime dependency

Required on Orange Pi 5:

```text
rknn_api.h
librknnrt.so
correct rknpu2 runtime version
/dev/rknpu accessible
LD_LIBRARY_PATH includes librknnrt.so path
```

Test:

```bash
ls -l /dev/rknpu*
ldconfig -p | grep rknn
find / -name "librknnrt.so" 2>/dev/null
find / -name "rknn_api.h" 2>/dev/null
```

---

## 1.7 Location and sensors

### `selfdrive/locationd/locationd.py`

Gate IMU/sensor usage with:

```python
NO_IMU = os.getenv("NO_IMU") is not None
```

Do not permanently comment out sensor drain globally.

Only bypass IMU blocking during Orange Pi 5 single-camera bring-up.

---

# SECTION 2 — C++ RKNN RUNNER ARCHITECTURE

## 2.1 RKNN runner flow

```text
.rknn file
  ↓
read into memory
  ↓
rknn_init(&ctx, model_data, model_size, 0, nullptr)
  ↓
rknn_set_core_mask()
  ↓
rknn_query(input/output count)
  ↓
rknn_query(input/output tensor attrs)
  ↓
validate input metadata
  ↓
rknn_inputs_set()
  ↓
rknn_run()
  ↓
rknn_outputs_get()
  ↓
copy all outputs
  ↓
finite validation
  ↓
rknn_outputs_release()
  ↓
metadata slicing
  ↓
modelV2 publish
```

## 2.2 Zero-copy NPU input warning

GPU/UI can import DMA-BUF through EGLImage.

RKNN zero-copy input requires explicit RKNN memory APIs where supported:

```text
rknn_create_mem
rknn_set_io_mem
```

Do not assume:

```text
rknn_inputs_set()
```

imports DMA-BUF fds directly.

Safest first production version:

```text
V4L2 mmap/DMA-BUF
→ copy into VisionIPC/OpenCL model buffer
→ existing DrivingModelFrame.prepare()
→ RKNN input tensor
```

Later optimization:

```text
V4L2 DMA-BUF
→ VisionIPC fd passing
→ EGLImage for UI
→ RKNN memory API for NPU input
```

## 2.3 Runtime fallback strategy

If RKNN inference fails:

```text
NaN
Inf
wrong output size
NPU crash
rknn_run error
rknn_outputs_get error
metadata mismatch
```

Then:

```text
1. stop publishing RKNN result immediately
2. switch to ONNX/Tinygrad fallback
3. reset hidden state safely
4. log failure reason to cloudlog
5. keep manager alive if possible
```

---

# SECTION 3 — HARDWARE-LEVEL IMPLEMENTATION DETAILS

## 3.1 V4L2 media graph and DMA-BUF camera pipeline

Target route:

```text
imx415
→ rockchip-csi2-dphy
→ rkcif
→ rkisp
→ selected ROAD_CAM node
```

Open device:

```c
open(ROAD_CAM, O_RDWR)
```

Default for Deggory setup:

```text
/dev/video11
```

Verify with:

```bash
media-ctl -p
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video11 --list-formats-ext
```

Native capture sequence:

```text
open()
VIDIOC_QUERYCAP
VIDIOC_ENUM_FMT
VIDIOC_S_FMT
VIDIOC_REQBUFS
VIDIOC_QUERYBUF
mmap
VIDIOC_EXPBUF
VIDIOC_QBUF
VIDIOC_STREAMON
loop:
  VIDIOC_DQBUF
  copy to VisionIPC buffer for first milestone
  VIDIOC_QBUF
```

## 3.2 Camera timestamps and frame IDs

The published cereal Event must have:

```text
logMonoTime
```

The `roadCameraState` payload must preserve:

```text
frameId
timestampSof
timestampEof
```

Internal variables may be snake_case, but published fields must match capnp exactly.

Frame IDs must be monotonic.

Timestamps must use monotonic clock domain compatible with OpenPilot.

## 3.3 EGLImage GPU rendering

To render the camera feed without CPU copies:

```c
EGLImageKHR image = eglCreateImageKHR(
    display,
    EGL_NO_CONTEXT,
    EGL_LINUX_DMA_BUF_EXT,
    NULL,
    attributes
);

glEGLImageTargetTexture2DOES(GL_TEXTURE_EXTERNAL_OES, image);
```

Attributes must include correct DMA-BUF information:

```text
EGL_LINUX_DRM_FOURCC_EXT
EGL_DMA_BUF_PLANE0_FD_EXT
EGL_DMA_BUF_PLANE0_OFFSET_EXT
EGL_DMA_BUF_PLANE0_PITCH_EXT
EGL_DMA_BUF_PLANE1_FD_EXT
EGL_DMA_BUF_PLANE1_OFFSET_EXT
EGL_DMA_BUF_PLANE1_PITCH_EXT
```

For NV12/NV12M, verify whether plane 0 and plane 1 use the same fd or separate fds.

## 3.4 Color-format validation

Even when the frame displays correctly, model input can be wrong.

Validate:

```text
NV12 vs NV21
UV order
full-range vs limited-range YUV
stride
UV offset
image rotation
image mirror
exposure brightness
black level
white balance stability
frame crop
horizon position
```

---

# SECTION 4 — RKNN MODEL CONVERSION MASTER GUIDE

## 4.1 Conversion pipeline

```text
ONNX
→ onnxsim simplify
→ opset check/downgrade
→ graph rewrites
→ FP16/non-quant RKNN build
→ validation against FP32 ONNX/Tinygrad
→ optional INT8 RKNN build
→ second validation
```

First target:

```text
FP16 / non-quant RKNN for correctness
```

Second target:

```text
INT8 RKNN only after ONNX/Tinygrad correlation passes
```

Do not make INT8 mandatory first.

## 4.2 Fatal RKNN conversion bugs and fixes

### 1. GELU approximate tanh

Problem:

```text
Gelu(approximate="tanh") may not map correctly.
```

Fix:

```text
Rewrite into primitive Mul/Add/Tanh operations.
```

### 2. UINT8 input rejection

Problem:

```text
Vision ONNX may use UINT8 inputs.
RKNN conversion may reject unsupported dtype.
```

Fix:

```text
Change graph inputs to FLOAT16/FLOAT32.
Remove direct input Cast nodes.
```

### 3. ReduceL2 FP16 overflow

Problem:

```text
Hidden-state L2 normalization may overflow FP16 intermediate range.
```

Fix:

```text
ReduceL2(x) → ReduceL2(x / 32) * 32
```

### 4. GatherND negative index

Problem:

```text
Policy model may use GatherND with negative indices.
RKNN can mishandle negative indexing.
```

Fix:

```text
Rewrite to Slice(features_buffer, axis=1, starts=16, ends=25)
```

### 5. NCHW vs NHWC layout

Problem:

```text
Wrong layout can produce zero/corrupted hidden state.
```

Fix:

```text
Set RKNN config data_format="nhwc" only where metadata/runtime expects it.
Transpose tensors only when metadata says so.
```

Example:

```python
x_nhwc = np.transpose(x_nchw, (0, 2, 3, 1))
```

---

# SECTION 5 — CAMERA AND PREPROCESSING SECRETS

## 5.1 NV12 layout bug

Webcam / standard V4L2 tight NV12:

```text
1280 × 720 × 1.5 = 1,382,400 bytes
```

Qualcomm/OpenPilot padded NV12 may expect:

```text
stride = 1280
y_height = 736
```

If UV offset is wrong, model receives corrupted image data.

Required fix:

```text
Add get_modeld_nv12_info() that returns tight NV12 layout when:
- USE_WEBCAM=1
- native V4L2 RK3588 path is active
```

## 5.2 Forbidden CPU production path

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
adds CPU conversion/copy overhead
destroys latency target
can change color range/order
```

Allowed only for early boot/testing:

```text
USE_WEBCAM=1 dev bring-up
```

## 5.3 Correct road model preprocessing

Do not use letterbox for OpenPilot driving model.

Wrong:

```text
NV12 camera frame
→ RGB/BGR
→ letterbox
→ RKNN
```

Correct:

```text
NV12 camera frame
→ OpenPilot warp / transform
→ YUV temporal input
→ RKNN
```

Preserve:

```text
calibration matrix
warp matrix
loadyuv.cl semantics
transform.cl semantics
temporal frame stack
hidden state
```

---

# SECTION 6 — SYSTEM CONFIGURATION AND ENVIRONMENT VARIABLES

## 6.1 Orange Pi 5 V4L2 device mapping

Common mapping:

```text
/dev/video0  → RKISP main path or alternate camera node
/dev/video11 → Deggory IMX415 road camera node
/dev/video31 → RGA hardware accelerator
```

Always verify:

```bash
v4l2-ctl --list-devices
media-ctl -p
```

## 6.2 Master environment variables

Development bring-up:

```bash
export NOBOARD=1
export NOSENSOR=1
export FORCE_IGNITION_ON=1
export USE_WEBCAM=1
export ROAD_CAM=11
export NO_DM=1
export NO_IMU=1
```

Production:

```bash
unset USE_WEBCAM
export ROAD_CAM=/dev/video11
export OPENPILOT_MODELD_BACKEND=rknn
export RKNN_VISION_CORE=0
export RKNN_POLICY_CORE=1
export MODELD_VISION_RKNN_INPUT_LAYOUT=nhwc
export MODELD_WARP_OUTPUT_LAYOUT=nhwc
export DISABLE_JIT_ALIAS_COPY=1
```

Force fallback for debugging:

```bash
export OPENPILOT_MODELD_BACKEND=onnx
```

## 6.3 UI adaptations

OpenPilot UI may assume comma-style resolution:

```text
2160×1080
```

Orange Pi 5 HDMI may use:

```text
800×400
1280×720
1920×1080
```

Patch only UI scaling/layout when required.

Do not change model/planner logic for UI issues.

---

# SECTION 7 — VALIDATION AND DEPLOYMENT PROTOCOLS

## 7.1 Hardware validation commands

Before launching OpenPilot:

```bash
v4l2-ctl --list-devices
media-ctl -p
v4l2-ctl -d /dev/video11 --list-formats-ext
v4l2-ctl -d /dev/video11 --get-fmt-video
v4l2-ctl -d /dev/video11 --stream-mmap --stream-count=100 --stream-to=/tmp/imx415.raw
```

NV12 preview test:

```bash
gst-launch-1.0 v4l2src device=/dev/video11 ! \
  video/x-raw,format=NV12,width=1920,height=1080,framerate=60/1 ! \
  xvimagesink
```

RKNN runtime checks:

```bash
ls -l /dev/rknpu*
ldconfig -p | grep rknn
find / -name "librknnrt.so" 2>/dev/null
find / -name "rknn_api.h" 2>/dev/null
```

## 7.2 Cross-runtime validation

Required before merging RKNN:

```text
1. run 100+ frames with FP32 ONNX/Tinygrad
2. save raw model outputs
3. run same frames with RKNN
4. compare per-output correlation
5. verify hidden state persistence
6. verify modelV2 schema remains identical
7. verify zero NaN/Inf
```

Pass criteria:

```text
vision output correlation > 0.995
policy output correlation > 0.995
zero invalid outputs
no modelV2 schema drift
```

## 7.3 Latency logging

Log every 100 frames:

```text
camera VIDIOC_DQBUF ms
camera copy-to-VisionIPC ms
VisionIPC send ms
modeld receive wait ms
DrivingModelFrame.prepare ms
RKNN vision ms
RKNN policy ms
modelV2 publish ms
total camera → modelV2 ms
CPU usage
NPU load
DMC frequency
temperature
```

This proves the system has moved away from the PyAV/OpenCV slow path.

## 7.4 Runtime stress test

Minimum:

```text
1 hour continuous run
```

Monitor:

```text
modeld FPS
camera frame drops
manager restarts
memory growth
temperature
NPU load
DMC frequency
RKNN latency spikes
```

Recovery tests:

```text
kill modeld
kill camerad/webcamerad
restart manager
disconnect/reconnect camera if possible
```

## 7.5 Road testing safety rules

Never test steering control on road until:

```text
camera/modeld stable for 1 hour
modelV2 output verified sane
controls disabled or passive mode verified
Panda safety active
driver can override
emergency disengage tested
brake/gas override verified
steering torque limit verified
```

Start with:

```text
passive mode
replay/demo mode
bench CAN
lateral-only
low-speed closed/private area
```

---

# SECTION 8 — ARCHITECTURAL FLOW DIAGRAM

```text
[IMX415 Sensor]
      ↓ MIPI CSI-2
[RKISP]
      ↓ V4L2
[DMA-BUF NV12/NV12M]
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
[Panda / CAN bus]
      ↓
[Vehicle Actuators]
```

---

# SECTION 9 — STEP-BY-STEP PORTING ORDER

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
14. Replace dev OpenCV path with V4L2 native capture.
15. Add DMA-BUF fd passing only after copy-path modeld is correct.
16. Add EGL/RGA optimization only after model accuracy is validated.
```

---

# SECTION 10 — VS CODE / AI AGENT PROMPT

Paste this into VS Code AI/Claude Code/Copilot when starting the port:

```text
Read ai/BRAIN.md fully before editing anything.

Goal:
Port this current Sunnypilot/OpenPilot repo to Orange Pi 5 / RK3588 with one Sony IMX415 road camera and split RKNN models.

Target:
- Orange Pi 5
- RK3588
- single IMX415 road camera
- road camera defaults to /dev/video11 unless ROAD_CAM overrides it
- no driver monitoring camera
- optional NO_IMU bring-up mode
- driving_vision.rknn on RKNN_NPU_CORE_0
- driving_policy.rknn on RKNN_NPU_CORE_1
- C++ RKNN runner wrapped by Cython
- ONNX/Tinygrad fallback if RKNN fails

Hard rules:
- Do not modify cereal/log.capnp.
- Do not modify modelV2 schema.
- Do not modify plannerd.
- Do not modify controlsd.
- Do not modify loadyuv.cl.
- Do not modify transform.cl.
- Do not modify DrivingModelFrame.prepare() semantics.
- Do not hardcode outputs[0].
- Do not assume one output.
- Do not use RKNN_NPU_CORE_ALL, RKNN_NPU_CORE_0_1, RKNN_NPU_CORE_0_1_2, or NPU_CORE_AUTO in production.
- Read model metadata .pkl for shapes and output slices.
- Validate all model outputs with finite checks.
- Do not use letterbox for the OpenPilot driving model.
- Do not use OpenCV BGR path in production.

First task:
Inspect the repo and create ai/RK3588_PORT_PLAN.md.

The plan must include:
1. current modeld path
2. current camerad/webcamerad/v4l2d path
3. current hardware detection path
4. current process_config path
5. current model file layout
6. current fallback runners
7. current VisionIPC stream names
8. current cameraState fields
9. files that must be patched
10. risks
11. exact milestone order
12. test commands for each milestone

Do not edit source code until the plan is approved.
```

---

# FINAL DECLARATION

This document is the final repo-ready engineering guide for the Orange Pi 5 / RK3588 OpenPilot/Sunnypilot port.

Any AI agent or engineer must:

```text
1. Read this document fully.
2. Create RK3588_PORT_PLAN.md before editing source.
3. Apply producer-side changes first.
4. Keep planner/control/schema untouched.
5. Use strict RKNN core assignment.
6. Use C++ RKNN runner for production.
7. Lock NPU and DMC frequencies.
8. Validate against ONNX/Tinygrad.
9. Publish modelV2 only after finite output validation.
10. Preserve fallback paths.
11. Replace PyAV/OpenCV only after baseline modeld is correct.
12. Add true zero-copy only after copy-path correctness is proven.
```

**Do not deviate from this architecture.**

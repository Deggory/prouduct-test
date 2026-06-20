# RK3588_PORT_PLAN.md

**Status:** Pending Approval
**Target Repo:** sunnypilot-pc
**Master Reference:** `ai/BRAIN.md` (V10.3)

## 1. Objective
Port the Sunnypilot-PC repository to run natively on Orange Pi 5 (RK3588) with a single Sony IMX415 camera. The ultimate goal is C++ RKNN NPU inference for the driving model, replacing the CPU ONNX/Tinygrad backend, while strictly preserving producer-side semantics and planner/controls safety.

## 2. Current State vs. Target State

| Component | Current State (sunnypilot-pc) | Target State (RK3588 Native) |
|---|---|---|
| **Hardware** | `PC=True`, `TICI=False`. No RK3588 awareness. | `RK3588=True`. Sysfs NPU/DDR freq locking, thermal monitoring. |
| **Camera** | `tools/webcam/camera.py` (OpenCV MJPG -> BGR -> NV12 CPU copy). | Native V4L2 `NV12`/`NV12M` capture from `/dev/video11`. Copy to VisionIPC first, DMA-BUF zero-copy later. |
| **Camera Intrinsics** | TICI defaults (focal=2648). | IMX415 defaults (1280x720, focal=900.0). |
| **Model Inference** | Python ONNX/Tinygrad (CPU). ~300ms latency. | C++ RKNN Runner via Cython. Strict Core 0 (Vision) / Core 1 (Policy). ~17ms latency. |
| **Output Parsing** | Python based. | Metadata `.pkl` driven slicing. `std::isfinite()` validation. Fallback to ONNX on NPU failure. |

## 3. Gaps to Address
1. **Hardware Detection:** `system/hardware/__init__.py` lacks device-tree RK3588 detection.
2. **V4L2 HAL:** Missing `common/hardware/rk3588/` directory with V4L2 and NPU C++ wrappers.
3. **Intrinsics:** `common/transformations/camera.py` will crash if `get_device_type()` returns `"rk3588"` (must return `"pc"` hack).
4. **Build System:** `selfdrive/modeld/SConscript` does not compile `rknnmodel.cc` or link `librknnrt.so`.
5. **Model Runner:** `selfdrive/modeld/modeld.py` lacks `OPENPILOT_MODELD_BACKEND=rknn` gate.

## 4. File-by-File Implementation Plan

### Phase 1: Hardware Abstraction & Bootstrapping
- **`system/hardware/__init__.py`**
  - Add `_is_rk3588()` device tree check.
  - Map `HARDWARE = RK3588Hardware(detected=True)` when true.
- **`common/hardware/rk3588/hardware.py`** (New)
  - Implement `RK3588Hardware(HardwareBase)`.
  - `get_device_type()` returns `"pc"` (with documented warning).
  - `initialize_hardware()` writes NPU (1GHz) and DDR (2.112GHz) sysfs freq locks (to be run via systemd).
- **`system/manager/process_config.py`**
  - Ensure `NO_DM=1` and `NO_IMU=1` defaults are safe for single-cam OPi5.

### Phase 2: Camera & VisionIPC (Fast V4L2 Copy Path)
- **`common/hardware/rk3588/camera/v4l2.py`** (New)
  - Auto-detect `V4L2_BUF_TYPE_VIDEO_CAPTURE` vs `MPLANE` (`NV12` vs `NV12M`).
  - Implement `open`, `set_format`, `request_buffers`, `start_streaming`, `capture_frame`.
- **`common/hardware/rk3588/camera/csi.py`** (New)
  - `IMX415Camera` class wrapping V4L2. Defaults: 1280x720 @ 20fps.
- **`tools/webcam/camerad.py`**
  - Gate camera initialization: if `RK3588=True`, use `IMX415Camera` instead of `CameraMJPG`.
  - Copy V4L2 NV12 frame into VisionIPC buffer. Do NOT attempt zero-copy DMA-BUF fd passing yet.
- **`common/transformations/camera.py`**
  - Override `DEVICE_CAMERAS[("pc", "unknown")]` with `CameraConfig(1280, 720, 900.0)` when `RK3588` env is active.
- **`selfdrive/modeld/models/commonmodel.cc`**
  - Ensure `DrivingModelFrame.prepare()` reads the tight NV12 layout correctly (no padded VENUS stride assumptions).

### Phase 3: C++ RKNN Runner Integration
- **`selfdrive/modeld/runners/rknnmodel.cc` & `rknnmodel.h`** (New)
  - `rknn_init(&ctx, model, size, 0, nullptr)`.
  - Strict `rknn_set_core_mask(ctx, RKNN_NPU_CORE_0)` (Vision) / `RKNN_NPU_CORE_1` (Policy).
  - Verify inputs (dtype, NCHW/NHWC, byte size). `rknn_inputs_set`.
  - `rknn_run(ctx, nullptr)`. `rknn_outputs_get`.
  - C++ `std::isfinite()` validation on all float outputs.
- **`selfdrive/modeld/runners/rknnmodel_pyx.pyx`** (New)
  - Cython wrapper to pass numpy arrays to C++ and return parsed outputs.
- **`selfdrive/modeld/runners/__init__.py`**
  - Export `RKNNModel`.
- **`selfdrive/modeld/SConscript`**
  - Add `rknnmodel.cc` to sources. Link `librknnrt.so`. Build `.pyx` extension.
- **`selfdrive/modeld/modeld.py`**
  - Read `OPENPILOT_MODELD_BACKEND`. If `=rknn`, load `.rknn` models and init `RKNNModel`.
  - Slice outputs via `driving_vision_metadata.pkl`.
  - If NPU inference fails, catch exception, log, reset hidden state, and fall back to ONNX.

## 5. Validation & Test Commands

Before integrating modeld, verify the V4L2 camera pipeline:
```bash
# 1. Verify media graph
media-ctl -p

# 2. Check formats on video11
v4l2-ctl -d /dev/video11 --list-formats-ext
v4l2-ctl -d /dev/video11 --get-fmt-video

# 3. Test raw capture
v4l2-ctl -d /dev/video11 --stream-mmap --stream-count=100 --stream-to=/tmp/imx415.raw

# 4. Test OpenPilot boot (no model)
NOBOARD=1 NOSENSOR=1 FORCE_IGNITION_ON=1 USE_WEBCAM=1 ROAD_CAM=11 NO_DM=1 NO_IMU=1 ./launch_openpilot.sh

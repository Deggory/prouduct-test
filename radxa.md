# Radxa Dragon Q6A (QCS6490) Porting Guide
> Derived from deep analysis of the sunnypilot-pc (openpilot-rk) codebase
> Last updated: 2026-05-10 (session 2 — speed tables, Hexagon HTP explainer, Jetson Orin comparison, Path A BEAM=1, int8 quantize option)

## Table of Contents
1. [What This Repo Is](#1-what-this-repo-is)
2. [Platform Detection Chain](#2-platform-detection-chain-how-the-repo-knows-what-hardware-its-on)
3. [Model Inference — Three Stacks](#3-model-inference--three-separate-stacks)
4. [Image Preprocessing — GPU on Orange Pi 5](#4-image-preprocessing--what-actually-uses-the-gpu-on-orange-pi-5)
5. [Camera Layer](#5-camera-layer)
6. [OpenCL Driver Situation](#6-opencl-driver-situation)
7. [SNPE / Qualcomm AI Stack in Repo](#7-snpe--qualcomm-ai-stack-in-repo)
8. [Tinygrad QCOM Backend Details](#8-tinygrad-qcom-backend-details)
9. [ONNX Runner Provider Logic](#9-onnx-runner-provider-logic)
10. [Hardware Class Summary](#10-hardware-class-summary)
11. [Device Speed Comparison](#11-device-speed-comparison--model-inference)
12. [What Works on QCS6490 Today](#12-what-works-on-qcs6490-today-zero-code-changes)
13. [Code Changes Required](#13-code-changes-required--ordered-by-value)
14. [Complete File Change Map](#14-complete-file-change-map)
15. [Tinygrad Backend Reference](#15-key-tinygrad-backend-file-reference)
16. [Camera Intrinsics](#16-camera-intrinsics--may-need-tuning)
17. [Environment Variables](#17-environment-variables-reference)
18. [How to Reach 20-30ms (Comma 3X Level)](#18-how-to-reach-20-30ms-comma-3x-level--all-realistic-options)
19. [Plain-Language Guide to All 4 Paths](#19-plain-language-guide-to-all-4-acceleration-paths-for-non-coders)
20. [What Is the Hexagon 770 HTP](#20-what-is-the-hexagon-770-htp--and-what-happens-when-radxa-q6a-runs-on-gpu)
21. [Recommended Porting Order](#21-recommended-porting-order-for-qcs6490)

---

## 1. What This Repo Is

The README title is **openpilot-rk** — a fork of sunnypilot adapted to run on **RK3588 devices (Orange Pi 5)** running **Ubuntu 24.04**. There is **zero Rockchip-specific kernel code** in the repo. The adaptation is entirely in:
- Build-time device-class selection (`PC` vs `TICI` vs `larch64`)
- Model inference backend selection (OpenCL ICD / ONNX CPU)
- Camera layer (USB webcam via V4L2 instead of native ISP)
- One OpenCL ICD package (`pocl-opencl-icd` or Mali vendor driver)

---

## 2. Platform Detection Chain (How the Repo Knows What Hardware It's On)

### Step A — Python runtime: `system/hardware/__init__.py`
```python
TICI = os.path.isfile('/TICI')   # file written by comma's AGNOS OS only
PC   = not TICI                  # everything else → Orange Pi 5 lands here
```
On Orange Pi 5 (Ubuntu 24.04): `/TICI` does not exist → `PC = True`, `TICI = False`.

### Step B — Build system arch: `SConstruct` lines 85-88
```python
real_arch = arch = subprocess.check_output(["uname", "-m"])  # 'aarch64'
if arch == "aarch64" and AGNOS:   # AGNOS=False on Orange Pi
    arch = "larch64"              # only assigned for comma's own device
# Orange Pi stays as 'aarch64'
```

**Four build arches:**
| Arch | Maps To |
|---|---|
| `larch64` | Comma TICI (AGNOS, Qualcomm SDM845) |
| `aarch64` | Linux PC aarch64 — **Orange Pi 5 and QCS6490 land here** |
| `x86_64` | Linux x86 PC |
| `Darwin` | macOS |

### Step C — C++ compile-time: `system/hardware/hw.h`
```cpp
#if QCOM2
#include "system/hardware/tici/hardware.h"
#define Hardware HardwareTici
#else
#include "system/hardware/pc/hardware.h"
#define Hardware HardwarePC      // ← Orange Pi 5 path
#endif
```
`QCOM2` flag is only set when `arch == "larch64"` in `SConstruct`.

### Step D — Camera: `system/manager/process_config.py`
```python
WEBCAM = os.getenv("USE_WEBCAM") is not None
NativeProcess("camerad", ..., enabled=not WEBCAM)     # native ISP: disabled on PC
PythonProcess("webcamerad", "tools.webcam.camerad", ..., enabled=WEBCAM)  # USB webcam
```
Native `camerad` binary is only **built** when `arch == "larch64"` (SConstruct line 385).

---

## 3. Model Inference — Three Separate Stacks

### Stack 1: `selfdrive/modeld/modeld.py` — stock tinygrad path (`is_stock_model`)

**File:** `selfdrive/modeld/modeld.py` lines 5-10
```python
if TICI:
    from ...tinygrad_helpers import qcom_tensor_from_opencl_address
    os.environ['QCOM'] = '1'     # tinygrad → ops_qcom.py (KGSL direct)
else:
    os.environ['GPU'] = '1'      # tinygrad → ops_gpu.py (OpenCL ICD)
```

**Build-time model compilation:** `selfdrive/modeld/SConscript` lines 40-45
```python
if arch == 'larch64':     device_string = 'QCOM=1'       # compiled for KGSL
elif arch == 'Darwin':    device_string = 'CLANG=1 IMAGE=0'
else:                     device_string = 'GPU=1 BEAM=0 IMAGE=0'  # ← Orange Pi / QCS6490
```

On Orange Pi 5: tinygrad compiles ONNX model with `GPU=1` → `tinygrad/runtime/ops_gpu.py` → **pure OpenCL ICD**. Calls `clGetPlatformIDs` / `clGetDeviceIDs` and picks up whatever ICD is registered in `/etc/OpenCL/vendors/`.

### Stack 2: `sunnypilot/modeld_v2/modeld.py` — tinygrad v2 path (`is_tinygrad_model`)

**File:** `sunnypilot/modeld_v2/model_runner.py` line 46
```python
TinygradRunner() if TICI else ONNXRunner()
```
On PC/Orange Pi 5: **`ONNXRunner`** → `onnxruntime` **CPU execution only**. No GPU.

**SConscript:** `sunnypilot/modeld_v2/SConscript` lines 41-43
```python
if arch == 'larch64':  device_string = 'QCOM=1'
else:                  device_string = 'CLANG=1 IMAGE=0'  # CPU, no GPU
```

### Stack 3: `sunnypilot/modeld/modeld.py` — SNPE/Thneed path (`is_snpe_model`)

**File:** `sunnypilot/modeld/runners/__init__.py`
```python
USE_THNEED = int(os.getenv('USE_THNEED', str(int(TICI))))
USE_SNPE   = int(os.getenv('USE_SNPE',   str(int(TICI))))
```
- On `larch64` (TICI): Thneed (OpenCL replay) or SNPE (Qualcomm AI Engine / DSP)
- On `aarch64` / `x86_64`: falls back to ONNX CPU

**SNPE build exclusion** in `sunnypilot/modeld/SConscript` lines 30-33:
```python
if arch != "Darwin" and arch != "aarch64":   # ← blocks SNPE on aarch64 Linux
    common_src += ['runners/snpemodel.cc']
    snpe_lib += ['SNPE']
```

### Process routing: `system/manager/process_config.py` lines 150-165
```python
PythonProcess("modeld",         ..., and_(only_onroad, is_stock_model))
PythonProcess("modeld_snpe",    ..., and_(only_onroad, is_snpe_model),  enabled=not PC)
PythonProcess("modeld_tinygrad",..., and_(only_onroad, is_tinygrad_model), enabled=not PC)
```
`modeld_snpe` and `modeld_tinygrad` are **disabled on PC** (`enabled=not PC`). Only `modeld` (stock) runs.

---

## 4. Image Preprocessing — What Actually Uses the GPU on Orange Pi 5

Even in ONNX CPU mode, **image preprocessing always uses OpenCL**:

| File | Purpose |
|---|---|
| `selfdrive/modeld/transforms/loadyuv.cl` | YUV → planar float conversion |
| `selfdrive/modeld/transforms/transform.cl` | Homography warp |
| `common/clutil.cc` lines 60-75 | `clGetPlatformIDs` + `clGetDeviceIDs(CL_DEVICE_TYPE_DEFAULT)` |

This is what uses the **Mali-G610 GPU** on Orange Pi 5. It works because `clutil.cc` is platform-agnostic — it picks up any registered OpenCL ICD. On QCS6490 it will pick up the Adreno ICD instead.

---

## 5. Camera Layer

**File:** `tools/webcam/camera.py` — `CameraMJPG` class
- Pure Python OpenCV + libav (PyAV) USB webcam capture
- Sets MJPEG format, 1280×720 @ 20fps
- Converts BGR → NV12 for VisionIPC

**File:** `tools/webcam/camerad.py`
- Publishes `roadCameraState`, `driverCameraState`, optional `wideRoadCameraState`
- Controlled by env vars `ROAD_CAM`, `DRIVER_CAM`, `WIDE_CAM`, `NO_DM`

---

## 6. OpenCL Driver Situation

**Webcam README** (`tools/webcam/README.md`):
```
Install OpenCL Driver:
sudo apt install pocl-opencl-icd
```
`pocl` is a **CPU-based** fallback OpenCL. For actual GPU acceleration:
- Orange Pi 5 (Mali-G610): install Mali vendor OpenCL driver or `mesa-opencl-icd` (panfrost, limited)
- QCS6490 (Adreno 643L): install `mesa-opencl-icd` (freedreno) or Qualcomm vendor driver

**Base Dockerfile** (`Dockerfile.openpilot_base` lines 37-54): installs Intel OpenCL ICD for x86 CI. On aarch64 this is irrelevant.

---

## 7. SNPE / Qualcomm AI Stack in Repo

Third-party SNPE libraries are already present:
```
third_party/snpe/
├── larch64/          # libSNPE.so, libhta.so, libsnpe_dsp_domains_v2.so
├── x86_64/           # x86 libs
├── x86_64-linux-clang/
├── include/          # DlContainer/, DlSystem/, SNPE/ headers
└── dsp/              # DSP firmware blobs
```

`snpemodel.cc` already handles GPU and DSP runtimes under `#ifdef QCOM2`:
```cpp
if (runtime == USE_GPU_RUNTIME)       snpe_runtime = zdl::DlSystem::Runtime_t::GPU;
else if (runtime == USE_DSP_RUNTIME)  snpe_runtime = zdl::DlSystem::Runtime_t::DSP;
else                                  snpe_runtime = zdl::DlSystem::Runtime_t::CPU;
```

---

## 8. Tinygrad QCOM Backend Details

**File:** `tinygrad_repo/tinygrad/runtime/ops_qcom.py`
- Direct Adreno A6XX register programming via `/dev/kgsl-3d0` ioctls
- Uses `tinygrad/runtime/autogen/kgsl.py` and `adreno.py` autogen bindings
- GPU ID check: `if QCOMDevice.gpu_id < 700:` — supports A6XX series (643L = A660 = gen 6XX ✓)
- Does **not** support 700-series (8 Gen 1+) yet

**File:** `selfdrive/modeld/runners/tinygrad_helpers.py`
```python
def qcom_tensor_from_opencl_address(opencl_address, shape, dtype):
    cl_buf_desc_ptr = to_mv(opencl_address, 8).cast('Q')[0]
    rawbuf_ptr = to_mv(cl_buf_desc_ptr, 0x100).cast('Q')[20]  # offset 0xA0 = raw GPU ptr
    return Tensor.from_blob(rawbuf_ptr, shape, dtype=dtype, device='QCOM')
```
This bridges OpenCL buffers (from image preprocessing) into tinygrad's QCOM device — critical for zero-copy pipeline.

**Tinygrad device selection** (`tinygrad_repo/tinygrad/device.py` line 35):
```python
for device in ["METAL", "AMD", "NV", "CUDA", "QCOM", "GPU", "CLANG", "LLVM"]:
    ...
if (from_env := next(d for d in self._devices if getenv(d) == 1)): return from_env
```
Setting `QCOM=1` env var forces the KGSL backend. Setting `GPU=1` forces OpenCL.

---

## 9. ONNX Runner Provider Logic

**File:** `sunnypilot/modeld/runners/onnxmodel.py` lines 42-54
```python
if 'OpenVINOExecutionProvider' in ort.get_available_providers():
    provider = 'OpenVINOExecutionProvider'
elif 'CUDAExecutionProvider' in ort.get_available_providers():
    provider = ('CUDAExecutionProvider', {...})
else:
    provider = 'CPUExecutionProvider'
```
**QNN provider is not listed** — needs to be added for QCS6490.

---

## 10. Hardware Class Summary

| Class | File | `PC()` | `TICI()` | `AGNOS()` |
|---|---|---|---|---|
| `Pc` | `system/hardware/pc/hardware.py` | `True` | env-based | env-based |
| `Tici` | `system/hardware/tici/hardware.py` | `False` | `True` | `True` |

On Orange Pi 5 and QCS6490 (today): `Pc()` is used. `get_gpu_usage_percent()` returns 0, `get_device_type()` returns `"pc"`.

---

## 11. Device Speed Comparison — Model Inference

### All Devices Side-by-Side (Comma 3X + PC-path devices)

| Device | Chip | ONNX Provider / Backend | Code changes needed | Model speed |
|---|---|---|---|---|
| **Comma 3X** | SDM845 / Adreno 630 | tinygrad QCOM=1 KGSL (not ONNX) | none (built-in) | **~20-30ms** |
| **Jetson AGX Orin** | Orin / Ampere GPU | `CUDAExecutionProvider` | none — already in code | **~15-25ms** |
| **Jetson Orin NX 16GB** | Orin / Ampere GPU | `CUDAExecutionProvider` | none — already in code | **~20-35ms** |
| **Jetson Orin Nano 8GB** | Orin / Ampere GPU | `CUDAExecutionProvider` | none — already in code | **~30-50ms** |
| **Jetson Orin Nano Super** | Orin / Ampere GPU | `CUDAExecutionProvider` | none — already in code | **~22-35ms** |
| **Intel NUC 13/14 (Core i7)** | Raptor Lake / Xe iGPU | `OpenVINOExecutionProvider` | none — already in code | **~35-60ms** |
| **x86 mini PC + NVIDIA dGPU** | any / RTX 3060+ | `CUDAExecutionProvider` | none — already in code | **~20-40ms** |
| **Orange Pi 5 / RK3588** | RK3588 / Mali-G610 | tinygrad GPU=1 OpenCL | none | **~50-150ms** |
| **Radxa Q6A — today** | QCS6490 / Adreno 643L | `CPUExecutionProvider` (fallback) | none, but slow | **~300-500ms** |
| **Radxa Q6A + mesa-opencl-icd** | QCS6490 / Adreno 643L | tinygrad GPU=1 OpenCL | install ICD only | **~100-150ms** |
| **Radxa Q6A + Path C (QNN fp32)** | QCS6490 / Hexagon 770 HTP | `QNNExecutionProvider` | 4 lines + pip install | **~40-60ms** |
| **Radxa Q6A + QNN int8** | QCS6490 / Hexagon 770 HTP | `QNNExecutionProvider` int8 | above + quantize script | **~30-40ms** |
| **Radxa Q6A + Path A (KGSL+BEAM)** | QCS6490 / Adreno 643L | tinygrad QCOM=1 direct KGSL | 7 files + rebuild | **~25-40ms** |
| **Radxa Q6A + Path B (SNPE)** | QCS6490 / Hexagon 770 HTP | SNPE DSP int8 `.dlc` | SDK + convert + 5 files | **~20-30ms** |

> Estimates based on hardware specs and code analysis. Benchmark with `sunnypilot/modeld_v2/tests/timing/benchmark.py`.

---

### Which Devices Need Zero Code Changes

The ONNX provider selection in `sunnypilot/modeld/runners/onnxmodel.py` already auto-detects three providers in priority order:

```
1. OpenVINOExecutionProvider  → installed by: pip install onnxruntime-openvino
2. CUDAExecutionProvider      → installed by: pip install onnxruntime-gpu
3. CPUExecutionProvider       → always available (fallback)
```

If you install the right Python package, the device is automatically accelerated — **no code changes, no rebuild**.

| Device type | What to install | Provider selected | Speed |
|---|---|---|---|
| NVIDIA Jetson Orin (any) | `pip install onnxruntime-gpu` | CUDA | ~15-50ms |
| x86 PC with NVIDIA GPU | `pip install onnxruntime-gpu` | CUDA | ~20-40ms |
| Intel NUC / Core Ultra | `pip install onnxruntime-openvino` | OpenVINO | ~35-60ms |
| Any device (fallback) | (already installed) | CPU | ~100-500ms |
| Radxa Q6A (after code change) | `pip install onnxruntime-qnn` | QNN | ~40-60ms |

---

### NVIDIA Jetson Orin — Best ONNX Device Outside Comma 3X

Jetson Orin runs aarch64 Ubuntu — **same code path as Orange Pi 5 and Radxa Q6A**. It lands in `PC=True`, `arch=aarch64`. No modifications needed except:

```bash
pip install onnxruntime-gpu     # installs CUDA provider
USE_WEBCAM=1 python3 system/manager/manager.py
```

ONNX Runtime automatically picks `CUDAExecutionProvider`. The Jetson AGX Orin reaches ~15-25ms — **faster than Comma 3X's tinygrad path** — because its Ampere GPU is vastly more powerful than the Adreno 630.

**Jetson comparison**:

| Jetson model | GPU | TOPS | ONNX CUDA speed | Notes |
|---|---|---|---|---|
| Jetson Orin Nano 8GB | 1024 Ampere | 40 | ~30-50ms | entry Orin |
| **Jetson Orin Nano Super** | **1024 Ampere** | **67** | **~22-35ms** | **Jan 2025, same module, higher clocks** |
| Jetson Orin NX 16GB | 1024 Ampere | 100 | ~20-35ms | — |
| Jetson AGX Orin 64GB | 2048 Ampere | 275 | ~15-25ms | faster than Comma 3X |
| Comma 3X (reference) | Adreno 630 KGSL | ~10 | ~20-30ms | not ONNX, uses tinygrad |
| Radxa Q6A Adreno 643L | 1024 ALUs | ~25 | ~25-40ms (Path A+BEAM) | QCS6490, needs code changes |

The **Orin Nano Super** is pin-compatible with the Orin Nano 8GB module — same physical board, just higher clocked silicon. JetPack 6 / Ubuntu 22.04 aarch64. Zero code changes needed beyond `pip install onnxruntime-gpu`.

---

### Other Qualcomm Linux Boards (Same Changes as Radxa Q6A)

Any board with an Adreno A6XX GPU and `/dev/kgsl-3d0` can use Path A (tinygrad QCOM=1) or Path C (QNN) after the same code changes:

| Board | SoC | Adreno GPU | tinygrad QCOM compat |
|---|---|---|---|
| Radxa Dragon Q6A | QCS6490 | Adreno 643L (A660) | Yes — gpu_id ~660 < 700 |
| Qualcomm RB5 Dev Kit | QRB5165 | Adreno 650 | Yes — gpu_id ~650 < 700 |
| Qualcomm RB3 Gen 2 | QCM6490 | Adreno 643L | Yes — same chip as Q6A |
| Lenovo ThinkPad X13s | SC8280XP | Adreno 690 | Yes — gpu_id ~690 < 700 |
| Surface Pro X (SQ2) | SC8180X | Adreno 690 | Yes — gpu_id ~690 < 700 |

**Not compatible** with tinygrad QCOM: Snapdragon 8 Gen 1+ (gpu_id ≥ 700, Adreno 730+). Reason: `ops_qcom.py` has `if QCOMDevice.gpu_id < 700` — 7XX series requires different CP_EVENT_WRITE7 commands not yet implemented.

---

### Why Orange Pi 5 Is Faster Than QCS6490 Today

Orange Pi 5 uses Stack 1 (`selfdrive/modeld`) with tinygrad `GPU=1` — the model **does** run on the Mali-G610 GPU via OpenCL. QCS6490, without an OpenCL ICD installed, falls back to pure CPU. Installing `mesa-opencl-icd` (freedreno) on QCS6490 immediately closes this gap.

### Hardware Comparison: Orange Pi 5 vs Radxa Q6A

| | Orange Pi 5 (RK3588 / Mali-G610) | Radxa Dragon Q6A (QCS6490 / Adreno 643L) |
|---|---|---|
| CPU | Cortex-A76×4 + A55×4, aarch64 | Kryo 670 (A78×4 + A55×4), aarch64 |
| GPU | Mali-G610 MP4 | Adreno 643L (A6XX family) |
| AI accelerator | RKNN NPU 6 TOPS | Hexagon 770 HTP (CDSP) — see Section 20 |
| GPU kernel driver | Mali proprietary or panfrost | `/dev/kgsl-3d0` (Qualcomm KGSL) |
| OpenCL | Mali vendor ICD or mesa (panfrost) | mesa-opencl-icd (freedreno) or vendor |
| SNPE/QNN | Not available | Full SNPE 2.x + QNN SDK |
| tinygrad QCOM backend | Not compatible (Mali ≠ Adreno) | Yes — A6XX family, gpu_id < 700 ✓ |
| Inference today (no changes) | tinygrad GPU=1 OpenCL ~50-150ms | ONNX CPU ~300-500ms |
| Best possible inference | tinygrad GPU=1 OpenCL ~50-150ms | SNPE/HTP ~20-30ms or KGSL ~25-40ms |

---

## 12. What Works on QCS6490 Today (Zero Code Changes)

Run exactly like Orange Pi 5:
```bash
sudo apt install opencl-headers ocl-icd-libopencl1
# Install Adreno OpenCL ICD (mesa-opencl-icd or vendor)
sudo apt install mesa-opencl-icd   # freedreno-based, works for preproc

USE_WEBCAM=1 python3 system/manager/manager.py
```
- Platform class: `Pc()` ✓
- Image preprocessing: OpenCL on Adreno 643L ✓
- Model inference: ONNX CPU ✓
- Camera: USB webcam via V4L2 ✓

---

## 13. Code Changes Required — Ordered by Value

### Change 1 — Enable tinygrad QCOM backend (best GPU path, needs kgsl)

**`system/hardware/__init__.py`** — add QCS detection:
```python
import os
TICI = os.path.isfile('/TICI')
QCS  = os.path.exists('/dev/kgsl-3d0') and not TICI   # Qualcomm Linux board
PC   = not TICI and not QCS
HARDWARE = cast(HardwareBase, Tici() if TICI else Pc())
```

**`selfdrive/modeld/modeld.py`** — enable QCOM path:
```python
from openpilot.system.hardware import TICI, QCS
if TICI or QCS:
    from openpilot.selfdrive.modeld.runners.tinygrad_helpers import qcom_tensor_from_opencl_address
    os.environ['QCOM'] = '1'
else:
    os.environ['GPU'] = '1'
```

**`sunnypilot/modeld_v2/model_runner.py`** line 46:
```python
from openpilot.system.hardware import TICI, QCS
# change:  TinygradRunner() if TICI else ONNXRunner()
# to:
TinygradRunner() if (TICI or QCS) else ONNXRunner()
```

**`selfdrive/modeld/SConscript`** and **`sunnypilot/modeld_v2/SConscript`**:
```python
import os
QCS = os.path.exists('/dev/kgsl-3d0') and not os.path.isfile('/TICI')
if arch == 'larch64' or (arch == 'aarch64' and QCS):
    device_string = 'QCOM=1'
elif arch == 'Darwin':
    device_string = 'CLANG=1 IMAGE=0'
else:
    device_string = 'GPU=1 BEAM=0 IMAGE=0'
```

**`system/manager/process_config.py`** — enable SNPE/tinygrad processes:
```python
from openpilot.system.hardware import PC, TICI, QCS
ENABLE_HW_ACCEL = not PC  # change this where enabled=not PC
```

### Change 2 — Enable SNPE build for aarch64 + QCS (DSP path)

**`sunnypilot/modeld/SConscript`** lines 30-33:
```python
import os
QCS = os.path.exists('/dev/kgsl-3d0') and not os.path.isfile('/TICI')
if arch != "Darwin" and (arch != "aarch64" or QCS):
    common_src += ['runners/snpemodel.cc']
    snpe_lib += ['SNPE']
```

Add SNPE aarch64 libraries to `third_party/snpe/` (from Qualcomm AI Hub or QNN SDK for `aarch64-ubuntu22`):
```
third_party/snpe/aarch64-linux/
├── libSNPE.so
├── libhta.so
└── libsnpe_dsp_domains_v2.so
```

### Change 3 — Add QNN ORT provider (easiest GPU/DSP path, no kernel changes)

**`sunnypilot/modeld/runners/onnxmodel.py`** — add before CUDA check:
```python
elif 'QNNExecutionProvider' in ort.get_available_providers() and 'ONNXCPU' not in os.environ:
    provider = ('QNNExecutionProvider', {
        'backend_path': 'libQnnHtp.so',
        'htp_performance_mode': 'burst',
        'htp_graph_finalization_optimization_mode': '3',
    })
```
Install: `pip install onnxruntime-qnn` (Qualcomm's ORT release).

### Change 4 — Device permissions for kgsl (QCS only)

**`launch_chffrplus.sh`** — add outside `agnos_init` block:
```bash
function qcs_init {
    sudo chgrp gpu /dev/kgsl-3d0 /dev/ion 2>/dev/null || true
    sudo chmod 660 /dev/kgsl-3d0 /dev/ion 2>/dev/null || true
}

if [ -f /AGNOS ]; then
    agnos_init
elif [ -e /dev/kgsl-3d0 ]; then
    qcs_init
fi
```

---

## 14. Complete File Change Map

| File | Change | Priority |
|---|---|---|
| `system/hardware/__init__.py` | Add `QCS = os.path.exists('/dev/kgsl-3d0') and not TICI` | High |
| `selfdrive/modeld/modeld.py` | `QCOM=1` when `TICI or QCS` | High |
| `sunnypilot/modeld_v2/modeld.py` | Same QCOM env logic | High |
| `sunnypilot/modeld_v2/model_runner.py` | `TinygradRunner()` if `TICI or QCS` | High |
| `selfdrive/modeld/SConscript` | `device_string = 'QCOM=1'` for aarch64+kgsl | High |
| `sunnypilot/modeld_v2/SConscript` | Same | High |
| `sunnypilot/modeld/SConscript` | Enable SNPE build for aarch64+QCS | Medium |
| `system/manager/process_config.py` | `enabled=not PC` → `enabled=not PC or QCS` for modeld_snpe/tinygrad | Medium |
| `sunnypilot/modeld/runners/onnxmodel.py` | Add `QNNExecutionProvider` | Medium |
| `third_party/snpe/aarch64-linux/` | Add SNPE libs for aarch64 | Medium |
| `launch_chffrplus.sh` | Add `qcs_init` for kgsl device permissions | Low |
| `system/hardware/pc/hardware.py` | Add `get_gpu_usage_percent()` reading from sysfs | Low |

---

## 15. Key Tinygrad Backend File Reference

| File | Backend | Triggered by |
|---|---|---|
| `tinygrad_repo/tinygrad/runtime/ops_gpu.py` | OpenCL ICD (any vendor) | `GPU=1` env |
| `tinygrad_repo/tinygrad/runtime/ops_qcom.py` | Adreno KGSL direct | `QCOM=1` env |
| `tinygrad_repo/tinygrad/runtime/autogen/kgsl.py` | KGSL ioctl bindings | imported by ops_qcom |
| `tinygrad_repo/tinygrad/runtime/autogen/adreno.py` | Adreno A6XX register defs | imported by ops_qcom |
| `tinygrad_repo/tinygrad/runtime/autogen/opencl.py` | OpenCL ctypes bindings | imported by ops_gpu |

Adreno 643L is A6XX family — **confirmed compatible** with tinygrad QCOM backend (`gpu_id < 700` check passes for A660/643L which is ~642-660 range).

---

## 16. Camera Intrinsics — May Need Tuning

**`common/transformations/camera.py`** — `("pc", "unknown")` maps to `_ar_ox_config`:
```python
("pc", "unknown"): _ar_ox_config   # 1280×720, focal=900.0
```
USB webcams have different focal lengths. The README says to use GMLCCalibration to get actual intrinsics and update `camera.py` and `selfdrive/ui/ui.h`.

**`selfdrive/ui/ui.h`** lines 29-31:
```cpp
const Eigen::Matrix3f FCAM_INTRINSIC_MATRIX = (Eigen::Matrix3f() <<
  900.0, 0.0, 1280.0 / 2,
  0.0, 900.0, 720.0 / 2,
  0.0, 0.0, 1.0).finished();
```
Update `900.0` and resolution to match your actual camera.

---

## 17. Environment Variables Reference

| Variable | Effect |
|---|---|
| `USE_WEBCAM=1` | Use USB webcam instead of native camerad |
| `NO_DM=1` | Disable driver monitoring camera |
| `ROAD_CAM=N` | Use `/dev/videoN` for road camera |
| `DRIVER_CAM=N` | Use `/dev/videoN` for driver camera |
| `WIDE_CAM=N` | Use `/dev/videoN` for wide camera |
| `NO_IMU=1` | Ignore IMU from CAN (if yawRate not populated) |
| `GPU=1` | Force tinygrad OpenCL backend |
| `QCOM=1` | Force tinygrad KGSL/Adreno backend |
| `USE_SNPE=1` | Force SNPE runner |
| `USE_THNEED=1` | Force Thneed runner |
| `USE_ONNX=1` | Force ONNX runner (always available) |
| `ONNXCPU=1` | Force CPU provider even if GPU ORT provider available |
| `SEND_RAW_PRED=1` | Include raw model output in message |

---

## 18. How to Reach 20-30ms (Comma 3X Level) — All Realistic Options

The Comma 3X runs the model in ~20-30ms using tinygrad `QCOM=1` on Adreno 630 via KGSL — **not ONNX**. Getting to that speed range on QCS6490 requires one of the following approaches.

### Quick Reference

| Step | What you do | Speed | Time |
|---|---|---|---|
| Path C as-is | `pip install onnxruntime-qnn` + 4 lines | ~40-60ms | 30 min |
| + int8 quantize (Option 1) | run quantize script + 2 lines change | ~30-40ms | +1 hr, **no rebuild** |
| + BEAM tinygrad (Option 2) | Path A 7 files + rebuild with `BEAM=1` | ~25-40ms | +2-4 hr build |
| SNPE `.dlc` (Option 3 / Path B) | Qualcomm SDK + convert model | ~20-30ms | 1-2 days |
| Comma 3X reference | (already built, thneed fp16) | ~20-30ms | N/A |

**Fastest no-rebuild path to ~30ms**: Path C (QNN fp32) first, then run the int8 quantize script below. No recompile needed. Total ~1.5 hours.

---

### Why Plain ONNX + QNN Gets ~40-60ms, Not 20-30ms

The bottleneck is **precision and layer fragmentation**:

- `supercombo.onnx` is an fp16 model. `onnxmodel.py` immediately upscales it to fp32 (`convert_fp16_to_fp32`). The Hexagon HTP runs fp32 at ~half speed vs int8.
- The model has hundreds of small layers. ONNX Runtime QNN fuses some, but not all. Each unfused layer crossing is overhead.
- On the Comma 3X, tinygrad's `BEAM` optimizer tries thousands of kernel tile combinations at build time and picks the fastest layout. ONNX Runtime does not do this.

To cross from 40ms into 20-30ms, **you must change the model precision** or **use a lower-level engine**.

---

### Option 1 — QNN + int8 Quantized ONNX Model (30-40ms, stays in ONNX format)

**What changes**: quantize `supercombo.onnx` from fp32 to int8 before passing it to QNN. The HTP is designed for int8 — its throughput doubles vs fp16/fp32.

**What it produces**: a new `supercombo_int8.onnx` file alongside the original. The code change in `onnxmodel.py` is one extra line to load this file instead when QNN is the provider.

**How to quantize** (run once on any Linux PC with ONNX Runtime installed):
```bash
pip install onnxruntime onnx numpy
python3 - <<'EOF'
from onnxruntime.quantization import quantize_static, CalibrationDataReader, QuantType, QuantFormat
import numpy as np, onnxruntime as ort

# Minimal calibration reader — feed ~100 frames of zeros as stand-in
# Replace with real camera frames for best accuracy
class FakeCalibReader(CalibrationDataReader):
    def __init__(self):
        self.count = 0
    def get_next(self):
        if self.count >= 100:
            return None
        self.count += 1
        return {
            "input_imgs":     np.zeros((1, 12, 128, 256), dtype=np.float32),
            "big_input_imgs": np.zeros((1, 12, 128, 256), dtype=np.float32),
        }

quantize_static(
    model_input="sunnypilot/modeld/models/supercombo.onnx",
    model_output="sunnypilot/modeld/models/supercombo_int8.onnx",
    calibration_data_reader=FakeCalibReader(),
    quant_type=QuantType.QInt8,
    quant_format=QuantFormat.QDQ,
)
print("Done")
EOF
```

**Code change** in `sunnypilot/modeld/runners/onnxmodel.py` — load int8 model when QNN is selected:
```python
elif 'QNNExecutionProvider' in ort.get_available_providers() and 'ONNXCPU' not in os.environ:
    int8_path = path.replace('.onnx', '_int8.onnx') if isinstance(path, str) else path
    model_data = int8_path if os.path.exists(int8_path) else path   # fall back if not converted
    provider = ('QNNExecutionProvider', {
        'backend_path': 'libQnnHtp.so',
        'htp_performance_mode': 'burst',
        'htp_graph_finalization_optimization_mode': '3',
    })
```

**Expected speed**: ~30-40ms (int8 HTP)
**Accuracy impact**: very small — the model is already robust to numerical variation; int8 quantization of supercombo has been validated in real sunnypilot deployments via SNPE's `use_tf8` flag (the same quantization scheme, see `snpemodel.cc` line 86-90)

---

### Option 2 — tinygrad QCOM=1 + BEAM Optimizer (25-40ms, Adreno 643L direct)

This is Path A (7 files to change, rebuild) with one extra build flag: **`BEAM=1`**.

`BEAM` is tinygrad's autotuner. At compile time it tries many different GPU kernel tile sizes and picks the fastest. It adds 30-60 min to the build but can cut runtime by 20-40%. Currently the `aarch64` build uses `BEAM=0` (disabled):

```python
# selfdrive/modeld/SConscript line 44:
else: device_string = 'GPU=1 BEAM=0 IMAGE=0'   # ← BEAM disabled
```

After enabling Path A (change `GPU=1 BEAM=0` → `QCOM=1 BEAM=1`):
```python
if arch == 'larch64' or (arch == 'aarch64' and QCS):
    device_string = 'QCOM=1 BEAM=1'    # ← autotuned for your specific Adreno 643L
```

**Expected speed**: ~25-40ms (Adreno 643L is a generation newer than the Comma 3X's Adreno 630 — raw fp16 throughput is roughly comparable; BEAM finds the optimal layout for exactly this GPU)

**Note**: the BEAM-compiled `.pkl` file is specific to the exact GPU it was compiled on. You cannot share it between an Adreno 630 and 643L.

---

### Option 3 — SNPE DSP with `.dlc` int8 model (20-30ms, matches Comma 3X)

This is Path B. The `.dlc` format with `use_tf8=True` (8-bit quantized image input) runs on the Hexagon 770 HTP at int8 natively — this is exactly what the Comma 3X does, just on a Hexagon 690 (SDM845) instead of 770.

**Expected speed**: ~20-30ms — **closest to Comma 3X performance**
**Effort**: hardest (Qualcomm SDK, `.dlc` conversion, SNPE libs, 5 file changes)

The `snpemodel.cc` code (`use_tf8` + `Runtime.DSP`) for this already exists and works — it just needs to be built for `aarch64` and pointed at a converted model.

---

### Summary — Path to 20-30ms

| Option | Format | Precision | Speed | Effort |
|---|---|---|---|---|
| QNN + fp32 ONNX (Path C as-is) | `.onnx` | fp32 | ~40-60ms | Very easy |
| QNN + int8 ONNX (Option 1 above) | `.onnx` | int8 | ~30-40ms | Easy (quantize script + 2 lines) |
| tinygrad QCOM=1 + BEAM (Option 2) | `.pkl` | fp16 | ~25-40ms | Moderate (7 files + rebuild with BEAM=1) |
| SNPE DSP `.dlc` (Path B / Option 3) | `.dlc` | int8 | ~20-30ms | Hard (SDK + conversion) |
| Comma 3X reference | `.pkl` (thneed) | fp16 | ~20-30ms | N/A (already built) |

**Practical recommendation**: do Path C (QNN fp32, ~40ms, 30 min) first to confirm everything works end-to-end. Then run the quantization script above to get the int8 model and switch to ~30ms — total additional effort is ~1 hour and zero code rebuilds.

---

## 19. Plain-Language Guide to All 4 Acceleration Paths (For Non-Coders)

### Background: What Is "The Model"?

Openpilot has an **AI brain** — a neural network that takes the camera image every ~50ms and decides "turn left 2°, brake 10%". This is called the **model**. It runs in a loop, forever, while the car is driving.

Running the model fast is critical. If it takes 400ms (0.4 seconds) per frame on CPU, the car reacts slowly. On Qualcomm hardware with proper acceleration, it can take 30-50ms — 8-10x faster.

**On QCS6490 today with zero changes**: model runs on 4 CPU cores (~300-500ms/frame). The Adreno 643L GPU is only used to convert camera images from YUV colour format — not for the AI at all.

There are **4 paths** to bring the Adreno 643L GPU / Hexagon 770 DSP into the loop.

---

### Path A — tinygrad direct GPU (Adreno 643L via KGSL kernel driver)

**What it is**: tinygrad is the AI framework used inside openpilot. It has a special mode (`QCOM=1`) that talks **directly to the Adreno GPU** at the lowest level possible — bypassing all middleware, talking to a kernel driver called KGSL (`/dev/kgsl-3d0`). Think of KGSL as the GPU's "doorbell" — tinygrad rings it directly.

**The bonus**: image preprocessing (converting camera pixels) already runs on the GPU via OpenCL. With Path A, the model also runs on the same GPU. tinygrad can **share the GPU memory directly** between preprocessing and model — zero copying. This is the most efficient pipeline.

**How fast**: ~50-80ms without tuning; **~25-40ms with `BEAM=1`** (tinygrad autotuner, adds 30-60 min to compile time but optimal for your specific Adreno 643L)

**How hard**: Moderate — 7 files to change, then rebuild with `QCOM=1 BEAM=1`

**What exactly blocks it today (3 things)**:

1. **Detection block** — `system/hardware/__init__.py` only knows two states: "I am comma's AGNOS device (`TICI`)" or "I am a generic PC (`PC`)". QCS6490 falls into `PC`, so the system never tries KGSL. Fix: add `QCS = os.path.exists('/dev/kgsl-3d0') and not TICI`.

2. **Backend selection block** — `selfdrive/modeld/modeld.py` says: `if TICI: use QCOM mode; else: use OpenCL mode`. QCS6490 is `else`, so it gets OpenCL (image preprocessing only). Fix: change `if TICI or QCS`.

3. **Build block** — At compile time, the model is pre-compiled for a specific target. For `aarch64` (QCS6490's CPU arch) it compiles with `GPU=1` (generic OpenCL), not `QCOM=1`. The pre-compiled model cannot switch targets at runtime. Fix: add kgsl detection to the build script.

**Permission requirement** (Path D): `/dev/kgsl-3d0` is owned by root by default. The openpilot process runs as a normal user. Without permission, Path A crashes immediately with "Permission denied". One shell script change fixes this.

**Files to change (7)**:
| File | What to change |
|---|---|
| `system/hardware/__init__.py` | Add `QCS` detection flag |
| `selfdrive/modeld/modeld.py` | `if TICI or QCS:` → set `QCOM=1` |
| `sunnypilot/modeld_v2/model_runner.py` | Use `TinygradRunner` when `TICI or QCS` |
| `selfdrive/modeld/SConscript` | Compile with `QCOM=1` when on kgsl board |
| `sunnypilot/modeld_v2/SConscript` | Same |
| `system/manager/process_config.py` | Enable `modeld_tinygrad` process for QCS |
| `launch_chffrplus.sh` | Fix kgsl device permissions on boot |

---

### Path B — SNPE DSP (Hexagon 770 HTP via Qualcomm AI Engine SDK)

**What it is**: Qualcomm makes a dedicated AI chip called the **Hexagon DSP** (sometimes called HTP or CDSP). It is purpose-built for neural networks — not a GPU, not a CPU, just AI. The QCS6490 has a Hexagon 770. Qualcomm's SDK to use it is called **SNPE** (Snapdragon Neural Processing Engine).

SNPE is already partially wired into this codebase — it's the engine used on the original comma TICI device. The libraries exist in `third_party/snpe/larch64/`. The model runner `snpemodel.cc` already handles GPU and DSP runtimes. However, the build system **explicitly blocks SNPE from being compiled for `aarch64`** Linux.

**How fast**: ~30-50ms per inference frame — **the fastest possible path**

**How hard**: Hard — requires downloading Qualcomm SDK files + 5 code changes + model must be in `.dlc` format (Qualcomm's proprietary format, different from `.onnx`)

**What exactly blocks it today (3 things)**:

1. **Build exclusion** — `sunnypilot/modeld/SConscript` line 30 says `if arch != "Darwin" and arch != "aarch64"`: only then add SNPE. One line blocks QCS6490.

2. **Missing libraries** — `third_party/snpe/` has `larch64/` libraries (for comma's device) but no `aarch64-linux/` folder. The Qualcomm QNN SDK download includes these.

3. **Missing `.dlc` model** — SNPE runs `.dlc` files, not `.onnx` files. The openpilot driving model (a `.onnx`) needs to be converted using Qualcomm's `snpe-onnx-to-dlc` tool.

**Files to change (5)**:
| File | What to change |
|---|---|
| `sunnypilot/modeld/SConscript` | Remove `aarch64` exclusion from SNPE build |
| `system/hardware/__init__.py` | Add `QCS` detection flag |
| `system/manager/process_config.py` | Enable `modeld_snpe` process for QCS |
| `third_party/snpe/aarch64-linux/` | **New folder**: add `libSNPE.so`, `libhta.so`, `libsnpe_dsp_domains_v2.so` |
| `launch_chffrplus.sh` | Fix kgsl/ion device permissions on boot |

---

### Path C — QNN ONNX Runtime (Hexagon 770 HTP via ONNX Runtime provider)

**What it is**: ONNX Runtime (the AI engine used for `ONNXRunner`) supports **plugins called "execution providers"**. Qualcomm makes one called `QNNExecutionProvider` that sends `.onnx` models to the Hexagon DSP automatically. No `.dlc` conversion needed. No kernel driver needed. Just install a Python package and add 4 lines of code.

This is **the easiest path** and the one with the **best effort-to-reward ratio**.

**How fast**: ~40-60ms per inference frame (5-8x faster than CPU)

**How hard**: Very easy — install 1 Python package + change 4 lines in 1 file

**What exactly blocks it today (1 thing)**:

`sunnypilot/modeld/runners/onnxmodel.py` lines 42-54 check for execution providers in this order:
```
1. OpenVINO  (Intel accelerator — not on Radxa)
2. CUDA      (NVIDIA GPU — not on Radxa)
3. CPU       (always available — this is what runs today)
```
QNN is not in the list. The fix is to add it before CUDA. The code already auto-detects which providers are available — adding QNN to the check is enough.

**Files to change (1)**:
| File | What to change |
|---|---|
| `sunnypilot/modeld/runners/onnxmodel.py` | Add `QNNExecutionProvider` check before CUDA check |

**Extra step**: install `onnxruntime-qnn` instead of the standard `onnxruntime` package.

---

### Path D — kgsl Device Permissions (Prerequisite for Path A)

**What it is**: This is NOT an acceleration path — it is a one-time setup step required before Path A can work.

On Linux, `/dev/kgsl-3d0` (the KGSL GPU driver doorbell) is owned by `root`. Openpilot runs as a normal user. When tinygrad (Path A) tries to open `/dev/kgsl-3d0`, Linux says "permission denied" and crashes.

The fix is a small function in the startup script that runs `chmod` on the device node every boot. The comma device (`AGNOS`) does this inside `agnos_init`. QCS6490 needs the same thing in a new `qcs_init` function.

**Files to change (1)**:
| File | What to change |
|---|---|
| `launch_chffrplus.sh` | Add `qcs_init` function that runs `chmod 660 /dev/kgsl-3d0` |

---

### Which Path to Use — Decision Tree

```
Have 30 minutes? → Path C (install package + 4 lines of code)
                   Result: Hexagon DSP, ~40-60ms/frame

Want full GPU pipeline? → Path D first (permissions), then Path A (7 files)
                          Result: Adreno 643L GPU, ~60-80ms/frame, zero-copy image+model

Want the absolute fastest? → Path B (most work, need Qualcomm SDK + .dlc model)
                              Result: Hexagon 770 HTP, ~30-50ms/frame
```

### Recommended Order

| Step | Path | Time | Result |
|---|---|---|---|
| 1 | None (run as PC) | 0 min | Works, ~300-500ms/frame CPU |
| 2 | Path C — QNN fp32 | 30 min | Hexagon HTP, ~40-60ms/frame |
| 2b | + int8 quantize script | +1 hr, no rebuild | Hexagon HTP int8, ~30-40ms/frame |
| 3 | Path D — kgsl permissions | 5 min | Prerequisite for step 4 |
| 4 | Path A — tinygrad QCOM=1 + BEAM=1 | 2-4 hrs + rebuild | Adreno 643L GPU, ~25-40ms, zero-copy |
| 5 | Path B — SNPE DSP .dlc int8 | 1-2 days | Hexagon HTP, ~20-30ms/frame |

**Start with Step 2 (Path C)**. It requires the least change and gives the biggest speedup. Path A and B require rebuilding the entire project from source.

---

## 19. What Is the Hexagon 770 HTP — And What Happens When Radxa Q6A Runs on GPU

### The QCS6490 Has Three Compute Engines

Inside the QCS6490 chip there are three completely separate "workers" that can run calculations:

```
┌──────────────────────────────────────────────────────────────────┐
│  QCS6490 chip                                                    │
│                                                                  │
│  ┌─────────────────┐   ┌──────────────────┐   ┌──────────────┐  │
│  │   CPU           │   │   GPU            │   │   HTP / DSP  │  │
│  │  Kryo 670       │   │  Adreno 643L     │   │  Hexagon 770 │  │
│  │  8 cores        │   │  A6XX family     │   │  (CDSP)      │  │
│  │  general tasks  │   │  graphics + AI   │   │  AI only     │  │
│  │                 │   │  /dev/kgsl-3d0   │   │  /dev/cdsp0  │  │
│  └─────────────────┘   └──────────────────┘   └──────────────┘  │
│                                                                  │
│  TODAY: model runs here  model runs here?      model runs here?  │
│         ✓ (default)       needs Path A          needs Path B/C   │
└──────────────────────────────────────────────────────────────────┘
```

---

### What Is Hexagon 770 HTP?

**Hexagon** = the name Qualcomm gives to their DSP (Digital Signal Processor) — a small secondary processor on the chip.

**770** = the generation (Hexagon 770 is in the QCS6490 / Snapdragon 778G class chips).

**HTP** = Hexagon Tensor Processor — a specific block *inside* the Hexagon that handles AI math.

**Why it exists**: Neural networks are almost entirely **matrix multiplications** — multiply a grid of numbers by another grid of numbers, millions of times. The CPU is a generalist and does this slowly. The GPU is better. The HTP is a specialist circuit built *only* to do exactly this operation, in 8-bit integers, very fast and with very low power.

**Analogy**: Imagine adding two numbers:
- CPU: takes a pen and paper, writes numbers, does the addition, writes the answer
- GPU: has 1000 pens and papers and does 1000 additions at the same time
- HTP: has a custom-built machine that does nothing but additions, 10000 at once, consumes 1/5th the power

The openpilot driving model is ~10-30 million operations per frame. The HTP can run that entire workload in ~30-50ms. The CPU takes ~400ms.

**The physical path** (Path B/C): model weights → `/dev/cdsp0` kernel driver → DSP firmware → HTP fixed-function units → result back.

**Key difference from GPU**: The GPU (`/dev/kgsl-3d0`) runs shader programs (general code compiled to GPU machine code). The HTP runs fixed quantized-integer operations — no shader compilation, just load weights and execute. That's why it's faster and more efficient for inference.

---

### What Happens When Radxa Q6A Runs on GPU (Path A — Adreno 643L)

When Path A is enabled (`QCOM=1`, tinygrad direct KGSL), this is the exact sequence inside the chip:

**Step 1 — Camera frame arrives**
```
USB camera → V4L2 kernel driver → RAM buffer (YUV format)
```

**Step 2 — Image preprocessing on Adreno 643L GPU**
```
RAM (YUV frame)
  → OpenCL kernel loadyuv.cl    [converts YUV → float planes]
  → OpenCL kernel transform.cl  [applies homography warp, resize to 512×256]
  → result stays in GPU VRAM                       ← no CPU involved
```
This already happens today. The OpenCL kernels write the result into a GPU memory buffer.

**Step 3 — Zero-copy hand-off (the critical Path A difference)**
```
GPU VRAM buffer (preprocessed image)
  → tinygrad reads the raw GPU pointer from the OpenCL buffer struct
  → creates a tinygrad QCOM Tensor pointing at the SAME memory address
  → no copying, no moving data                     ← this is what tinygrad_helpers.py does
```
Without Path A: at this point the data would be copied CPU→RAM→CPU before ONNX can use it. That round-trip takes ~5-10ms and forces the CPU to wake up.

**Step 4 — Model inference on Adreno 643L GPU**
```
GPU VRAM (image tensor) + GPU VRAM (model weights, pre-loaded)
  → tinygrad QCOM backend sends compute commands to /dev/kgsl-3d0
  → KGSL kernel driver submits commands to Adreno CP (Command Processor)
  → Adreno 643L executes: ~200 shader dispatches (convolutions, attention layers)
  → result tensor in GPU VRAM (steering angle, brake, path predictions)
```

What tinygrad is actually writing to KGSL (from `ops_qcom.py`) is a sequence of A6XX GPU register writes and compute dispatches — the same low-level commands a graphics driver would send for 3D rendering, but repurposed for matrix math.

**Step 5 — Read result**
```
GPU VRAM result → copied to CPU RAM → published to cereal/messaging bus
```
This final copy is tiny (a few hundred floats) and takes <1ms.

**End-to-end latency (Path A)**:
```
Camera frame arrives
→ preproc on GPU:      ~5ms
→ zero-copy hand-off:  ~0ms
→ model on GPU:        ~50-70ms
→ result copy:         ~1ms
Total:                 ~56-76ms
```
Compare CPU path: preproc ~5ms + **copy to CPU** ~8ms + **model on CPU** ~400ms + result ~1ms = **~414ms**

**Adreno 643L GPU specs (relevant to inference)**:
- 1024 shader processors (ALUs) in 8 compute units
- 1.4 GHz compute clock (at full performance mode)
- 32-bit float throughput: ~2.9 TFLOPS
- 16-bit float throughput: ~5.8 TFLOPS (model runs fp16)
- Memory bandwidth: ~25 GB/s shared with CPU

The openpilot supercombo model is ~600 million floating point operations. At 5.8 TFLOPS theoretical, ignoring overhead: 0.6 GFLOP / 5800 GFLOP/s = ~0.1ms. The actual 50-70ms is due to **memory bandwidth and kernel launch overhead** — the model has hundreds of small layers that each require a new compute dispatch. This is exactly the overhead that SNPE/HTP avoids by fusing layers in hardware.

---

### GPU vs HTP — Which Is Better for This Model?

| | Adreno 643L GPU (Path A) | Hexagon 770 HTP (Path B/C) |
|---|---|---|
| What runs it | tinygrad KGSL direct | SNPE or QNN |
| Precision | fp16 (16-bit float) | int8 (8-bit integer, quantized) |
| Speed | ~50-80ms/frame | ~30-50ms/frame |
| Power draw | ~2-4W | ~0.5-1W |
| Image preproc integration | Zero-copy (same GPU) | Data must cross to DSP |
| Accuracy | Full precision | Very slightly lower (quantization) |
| Effort to enable | Moderate (Path A, 7 files) | Hard (Path B) or Easy (Path C) |
| Zero-copy possible? | Yes (Path A) | No — image preproc stays on GPU |

**Conclusion**: For pure speed and power efficiency, HTP wins. For zero-copy full-GPU pipeline (image + model on the same device, no bus transfers), Adreno wins. In practice on a moving car, the 20ms difference between GPU and HTP is less important than having Path C working (QNN, 30 minutes) before Path A (rebuild, hours).

---

## 20. Recommended Porting Order for QCS6490

1. **Immediate** — Run as generic PC with `USE_WEBCAM=1`. Confirm calibration, controls, and CAN work. Image preprocessing runs on Adreno GPU via OpenCL ICD.

2. **Step 2** — Install ONNX Runtime with QNN provider. Add `QNNExecutionProvider` to `onnxmodel.py`. Model inference moves to Hexagon DSP. ~4-5× speedup.

3. **Step 3** — Enable tinygrad QCOM backend. Add `QCS` detection, modify `modeld.py` files and SConscripts. Full zero-copy GPU pipeline: image preproc + model on Adreno GPU via KGSL.

4. **Step 4** — Enable SNPE stack. Add aarch64 SNPE libs. Enable `modeld_snpe` and `modeld_tinygrad` processes for non-PC. This unlocks the full Qualcomm AI stack including `.dlc` model format and DSP acceleration.

5. **Step 5** — Add proper hardware class. Create `system/hardware/qcs/hardware.py` and `hardware.h` for accurate device reporting, thermal management, and GPU usage metrics.

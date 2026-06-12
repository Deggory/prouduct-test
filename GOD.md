# GOD.MD (Authoritative Version)

# SuperAI Agent — Complete Omniscient Engineering Reference

Version: 1.0
Classification: Authoritative — SuperAI Agent
Status: Production Reference

Target Repository: sunnypilot-pc
Target Branch: master-rk3588
Target Remote: https://github.com/MM-X/sunnypilot-pc.git
Target Hardware: Orange Pi 5 / RK3588 / IMX415
Authored: 2026-06-10

---

# PRIME DIRECTIVE

This document is the single source of truth for all AI-assisted code changes, reviews, and
generation tasks in this repository.

Before writing any code:

```
Read this document fully.
Understand the architecture.
Understand the rules.
Understand what is forbidden.
Only then: write code.
```

If you are an AI agent (GitHub Copilot, Claude, ChatGPT, Cursor, Windsurf, Continue.dev):

```
You MUST follow every rule in this document.
You MUST NOT skip validation steps.
You MUST NOT modify planner, controls, or message semantics.
You MUST NOT hardcode tensor indices.
You MUST NOT remove Tinygrad fallback.
You MUST preserve ALL existing interfaces.
```

---

# SECTION 1 — REPOSITORY IDENTITY

## 1.1 Repository Facts

```
Repository:   sunnypilot-pc
Remote:       https://github.com/MM-X/sunnypilot-pc.git
Branch:       master-rk3588
HEAD:         3ad69b20b fix(lon): Change LEAD_DANGER_FACTOR
Base fork:    sunnypilot (which forks commaai/openpilot)
Purpose:      Linux SBC adaptation — run Sunnypilot on Orange Pi 5 (RK3588)
```

## 1.2 What This Branch Actually Does

```
NOT primarily: RK3588 NPU acceleration
ACTUALLY:      Linux SBC hardware adaptation

Specifically:
- Remove Comma hardware dependencies
- Add V4L2/webcam camera support
- Allow no IMU / no driver camera
- Adapt camera geometry for IMX415
- Adapt UI to 800×400 display
- Run on Orange Pi 5
```

## 1.3 Key Commits (chronological, oldest first)

```
b51be4e29 feat(selfdrive): Make op run          ← THE foundational commit
f39cc16f7 feat(more): Adapter to rk3588
28b99cc23 feat(lon): Opt lon control
6e91b9c2c feat(tools): Support old local route
cab810f02 fix(tools): Fix tools
bf3f07e7a feat(ui): Adapter ui size to 800x400
95af03c09 feat(camera): Change camera focal
306a880ca feat(locationd): Allow no imu
712bcb2be feat(camera): Change camera focal to imx415
3ad69b20b fix(lon): Change LEAD_DANGER_FACTOR     ← HEAD
```

---

# SECTION 2 — DIRECTORY STRUCTURE

## 2.1 Top-Level Layout

```
sunnypilot-pc/
├── Ai/                          ← AI engineering pack (this document lives here)
│   ├── GOD.md                   ← YOU ARE HERE
│   ├── README.md
│   ├── commit.md
│   ├── ai/                      ← core domain docs
│   │   ├── camera.md
│   │   ├── visionipc.md
│   │   ├── modeld.md
│   │   ├── rknn.md
│   │   ├── validation.md
│   │   ├── performance.md
│   │   └── deployment.md
│   ├── references/              ← deep architecture specs
│   │   ├── openpilot_architecture.md
│   │   ├── rk3588.md
│   │   ├── imx415.md
│   │   ├── model_metadata.md
│   │   └── visionipc.md
│   ├── diagrams/                ← pipeline flow diagrams
│   │   ├── camera_pipeline.md
│   │   ├── modeld_pipeline.md
│   │   ├── rknn_pipeline.md
│   │   └── deployment_pipeline.md
│   ├── examples/                ← concrete code examples
│   │   ├── rknn_runner_example.md
│   │   ├── modeld_patch_example.md
│   │   ├── imx415_rkisp_example.md
│   │   └── deployment_example.md
│   ├── templates/               ← report templates
│   │   ├── patch_template.md
│   │   ├── validation_report_template.md
│   │   ├── performance_report_template.md
│   │   └── deployment_report_template.md
│   ├── checklists/
│   │   ├── camera_checklist.md
│   │   ├── rknn_checklist.md
│   │   ├── validation_checklist.md
│   │   └── production_checklist.md
│
├── cereal/                      ← message schemas (capnp)
├── common/                      ← shared utilities
├── openpilot/                   ← symlink directory (points back to root dirs)
│   ├── common -> ../common
│   ├── selfdrive -> ../selfdrive/
│   ├── sunnypilot -> ../sunnypilot
│   ├── system -> ../system/
│   ├── third_party -> ../third_party
│   └── tools -> ../tools
├── selfdrive/                   ← main driving logic
├── sunnypilot/                  ← sunnypilot extensions
├── system/                      ← system services
├── tools/                       ← developer tools including webcam
├── panda/                       ← CAN interface hardware
├── third_party/                 ← external libraries
├── msgq/                        ← message queue (submodule)
├── opendbc/                     ← CAN database (submodule)
└── tinygrad_repo/               ← tinygrad ML framework (submodule)
```

## 2.2 Import Path Convention

```
All Python imports use the openpilot.* prefix:

from openpilot.selfdrive.modeld.modeld import ...
from openpilot.sunnypilot.modeld_v2.model_runner import ...
from openpilot.common.params import Params
from openpilot.system.manager.process_config import managed_processes

The openpilot/ directory is a collection of symlinks so that
"import openpilot.selfdrive.X" resolves to "selfdrive/X".
```

---

# SECTION 3 — COMPLETE PROCESS ARCHITECTURE

## 3.1 Process Table (system/manager/process_config.py)

```python
# --- KEY ENVIRONMENT VARIABLES ---
WEBCAM = os.getenv("USE_WEBCAM") is not None      # line 12
NO_DM  = os.getenv("NO_DM")   is not None         # line 13

# --- CAMERA PROCESSES ---
NativeProcess("camerad",    "system/camerad",   driverview, enabled=not WEBCAM)
PythonProcess("webcamerad", "tools.webcam.camerad", driverview, enabled=WEBCAM)

# --- MODEL PROCESSES ---
PythonProcess("modeld",     "selfdrive.modeld.modeld",              and_(only_onroad, is_stock_model))
PythonProcess("dmonitoringmodeld", "selfdrive.modeld.dmonitoringmodeld", driverview, enabled=not NO_DM)

# --- SUNNYPILOT MODEL PROCESSES ---
NativeProcess("modeld_snpe",    "sunnypilot/modeld",    and_(only_onroad, is_snpe_model),    enabled=not PC)
NativeProcess("modeld_tinygrad","sunnypilot/modeld_v2", and_(only_onroad, is_tinygrad_model), enabled=not PC)

# --- LOCATION ---
PythonProcess("locationd",  "selfdrive.locationd.locationd",  only_onroad)
PythonProcess("calibrationd","selfdrive.locationd.calibrationd", only_onroad)
PythonProcess("paramsd",    "selfdrive.locationd.paramsd",     only_onroad)
PythonProcess("torqued",    "selfdrive.locationd.torqued",     only_onroad)

# --- CONTROLS ---
PythonProcess("selfdrived", "selfdrive.selfdrived.selfdrived", only_onroad)
PythonProcess("controlsd",  "selfdrive.controls.controlsd",   and_(not_joystick, iscar))
PythonProcess("plannerd",   "selfdrive.controls.plannerd",    not_long_maneuver)
PythonProcess("card",       "selfdrive.car.card",             only_onroad)
PythonProcess("radard",     "selfdrive.controls.radard",      only_onroad)

# --- SYSTEM ---
NativeProcess("loggerd",    "system/loggerd",   logging)
NativeProcess("encoderd",   "system/loggerd",   only_onroad,  enabled=not PC)
NativeProcess("sensord",    "system/sensord",   only_onroad,  enabled=not PC)
PythonProcess("pandad",     "selfdrive.pandad.pandad", always_run)
PythonProcess("hardwared",  "system.hardware.hardwared", always_run)
```

## 3.2 Model Runner Selection

```python
# Model runner selected at runtime based on active bundle:
# sunnypilot/models/helpers.py

get_active_model_runner() → Runner enum:
  Runner.stock     → selfdrive.modeld.modeld (stock OpenPilot modeld)
  Runner.tinygrad  → sunnypilot/modeld_v2 (TinygradRunner / ONNXRunner)
  Runner.snpe      → sunnypilot/modeld (SNPE native binary)

# Active bundle stored in params:
params.get("ModelManager_ActiveBundle")  → ModelBundle capnp object
params.get("ModelRunnerTypeCache")       → cached runner type int
```

---

# SECTION 4 — CAMERA PIPELINE

## 4.1 Current State (Development/RK3588 Bring-Up)

```
Environment: USE_WEBCAM=1

IMX415 / any V4L2 cam
   ↓
tools/webcam/camera.py (CameraMJPG class)
   ↓ cv2.VideoCapture → MJPG format → bgr2nv12
   ↓ target: 1280×720 @ 20fps
tools/webcam/camerad.py (Camerad class)
   ↓ NV12 via CPU copy
VisionIPC (server: "camerad")
   ↓
selfdrive/modeld/modeld.py or sunnypilot/modeld_v2/modeld.py
```

## 4.2 Production Target (IMX415 + RKISP)

```
IMX415 → RKISP → V4L2 → NV12 DMA-BUF
   ├─→ VisionIPC → OpenCL → RKNN/Tinygrad → modelV2 → Planner
   └─→ EGLImage → Mali GPU → UI Preview
```

## 4.3 Camera Files

```
tools/webcam/camera.py          ← Camera (av/PyAV) + CameraMJPG (cv2/MJPG)
tools/webcam/camerad.py         ← Camerad class: VisionIPC server + thread per camera
common/transformations/camera.py ← CameraConfig, DeviceCameraConfig, DEVICE_CAMERAS
```

## 4.4 Camera Env Vars

```bash
USE_WEBCAM=1              # enable webcam mode (disables native camerad)
ROAD_CAM=0                # road camera device index/path (default: "0")
DRIVER_CAM=2              # driver camera device index/path (default: "2")
WIDE_CAM=<path>           # optional wide camera
NO_DM=1                   # disable driver monitoring entirely
```

## 4.5 IMX415 Camera Geometry (camera.py)

```python
# After commit 712bcb2be
# IMX415 focal length applied to DEVICE_CAMERAS lookup
# CameraMJPG targets: 1280×720, MJPG fourcc, 20fps
# NV12 buffer size: 1280×720×1.5 = 1,382,400 bytes
```

## 4.6 FORBIDDEN Camera Path

```
NEVER use: IMX415 → OpenCV BGR → bgr_to_nv12() → numpy copies → RKNN
REASON: high CPU, high latency, acceptable ONLY for development
TARGET: IMX415 → RKISP → V4L2 → NV12 DMA-BUF → VisionIPC (zero-copy)
```

---

# SECTION 5 — MODELD PIPELINE

## 5.1 Stock modeld (selfdrive/modeld/modeld.py)

```python
# Activated when: is_stock_model() → Runner.stock
# Uses: selfdrive/modeld/models/driving_vision.onnx + driving_policy.onnx
# VisionIPC client: "camerad"
# Auto-detects available streams:
available_streams = VisionIpcClient.available_streams("camerad", block=False)
use_extra_client = WIDE_ROAD in available_streams and ROAD in available_streams
main_wide_camera = ROAD not in available_streams  # fallback to wide if no road cam

# Publishes: modelV2, drivingModelData, cameraOdometry
# Subscribes: deviceState, carState, roadCameraState, liveCalibration,
#             driverMonitoringState, carControl
```

## 5.2 Sunnypilot modeld_v2 (sunnypilot/modeld_v2/modeld.py)

```python
# Activated when: is_tinygrad_model() → Runner.tinygrad
# Uses: sunnypilot/modeld_v2/models/supercombo.onnx or custom bundle
# Runner class: ModelRunner (ABC) → TinygradRunner or ONNXRunner
# ModelState picks runner: TinygradRunner if TICI else ONNXRunner

# ModelRunner ABC interface (model_runner.py):
class ModelRunner(ABC):
  def prepare_inputs(imgs_cl, numpy_inputs, frames) -> dict
  def run_model()
  def slice_outputs(model_outputs) -> dict  # reads output_slices from metadata

# Metadata loaded from pickle:
self.model_metadata = pickle.load(open(metadata_path, 'rb'))
self.input_shapes   = self.model_metadata['input_shapes']
self.output_slices  = self.model_metadata['output_slices']
```

## 5.3 RKNN Port (sunnypilot/modeld/ — SNPE binary)

```
Activated when: is_snpe_model() → Runner.snpe
Binary: sunnypilot/modeld/modeld (NativeProcess)
Models: sunnypilot/modeld/models/supercombo.onnx
```

## 5.4 Model Files Present

```
selfdrive/modeld/models/
  driving_vision.onnx
  driving_policy.onnx
  dmonitoring_model.onnx
  dmonitoring_model.current

sunnypilot/modeld/models/
  supercombo.onnx

sunnypilot/modeld_v2/models/
  supercombo.onnx
  dmonitoring_model.onnx
  dmonitoring_model.current
```

## 5.5 Critical Preprocessing Rules

```
DO NOT modify:
  loadyuv.cl         (NV12 → YUV tensor)
  transform.cl       (camera tensor warping)
  DrivingModelFrame.prepare()
  warp generation logic

Only change: inference backend (Tinygrad → RKNN)
```

## 5.6 Hidden State Rule

```
NEVER reset hidden state every frame.
Hidden state persists across frames for temporal consistency.
Reset only on explicit model reset / camera loss.
```

## 5.7 Tensor Layout

```
Tinygrad default: NCHW [1, 12, 128, 256]
RKNN may require: NHWC [1, 128, 256, 12]

Conversion only at inference boundary:
  np.transpose(tensor, (0, 2, 3, 1))

NEVER modify VisionIPC, loadyuv.cl, transform.cl for layout.
```

---

# SECTION 6 — LOCATIOND (IMU/SENSOR HANDLING)

## 6.1 No-IMU Mode

```python
# selfdrive/locationd/locationd.py line 20
NO_IMU = os.getenv("NO_IMU") is not None

# Gyro observation path gated at line 116:
if not NO_IMU:
    # GYRO observation
    ...
```

## 6.2 Current Actual Behavior (Drift from Documentation)

```
IMPORTANT: The direct accelerometer/gyroscope socket drain is FULLY commented out.
Physical IMU data is NEVER read regardless of NO_IMU.
Filter runs on: cameraOdometry + carState + liveCalibration ONLY.
sensors_valid is hardcoded True at get_msg() call site.
Filter initialized via sm.all_checks() (SubMaster liveness only).

# line 273: acc_msgs, gyro_msgs drain is commented out
# line 302: filter_initialized = sm.all_checks()  ← no sensor dependency

Impact: Works fine on Orange Pi 5 (no sensord). If sensord re-enabled,
        its output will be silently ignored.
```

## 6.3 selfdrived Sensor Relaxation

```python
# selfdrive/selfdrived/selfdrived.py
NO_DM = os.getenv("NO_DM") is not None  # line 36

self.camera_packets = ["roadCameraState"]  # line 80
if not NO_DM:
  self.camera_packets.append("driverCameraState")  # line 82

if NO_DM:
  ignore += ['driverMonitoringState']  # line 89
```

---

# SECTION 7 — CONTROLS ARCHITECTURE

## 7.1 controlsd.py

```python
# Subscribes: liveParameters, liveTorqueParameters, modelV2, selfdriveState,
#             liveCalibration, livePose, longitudinalPlan, carState, carOutput,
#             driverMonitoringState, onroadEvents, driverAssistance, selfdriveStateSP
# Publishes:  carControl, controlsState, carControlSP
# Poll:       selfdriveState

# Lateral controllers: LatControlPID, LatControlAngle, LatControlTorque
# Longitudinal:        LongControl

# MADS integration:
ss_sp = self.sm['selfdriveStateSP']
if ss_sp.mads.available:
  _lat_active = ss_sp.mads.active
else:
  _lat_active = self.sm['selfdriveState'].active
```

## 7.2 plannerd.py

```python
# Subscribes: carControl, carState, controlsState, liveParameters, radarState,
#             modelV2, selfdriveState
# Publishes:  longitudinalPlan, driverAssistance, longitudinalPlanSP
# Poll:       modelV2
# Uses: LongitudinalPlanner, LaneDepartureWarning
```

## 7.3 card.py (Car Interface)

```python
# Subscribes: pandaStates, carControl, onroadEvents, carControlSP
# Publishes:  sendcan, carState, carParams, carOutput, liveTracks, carParamsSP
# Handles: CAN RX/TX, car fingerprinting, OBD multiplexing
# Uses: opendbc.car.car_helpers.get_car, interfaces
# Sunnypilot: sunnypilot.mads.helpers.set_alternative_experience
```

## 7.4 selfdrived.py

```python
# State machine: StateMachine (state.py)
# MADS: ModularAssistiveDrivingSystem (sunnypilot/mads/mads.py)
# Events: Events + EventsSP
# Subscriptions include all camera_packets + sensor_packets + gps_packets
# IGNORE_PROCESSES = {"loggerd", "encoderd", "statsd", "ui"}
```

---

# SECTION 8 — SUNNYPILOT EXTENSIONS

## 8.1 MADS (Modular Assistive Driving System)

```python
# sunnypilot/mads/mads.py
# MADS allows lateral control independent of longitudinal engagement

# State machine: disabled → paused → enabled → softDisabling → overriding
# Key params:
#   "Mads"                    → master toggle
#   "MadsMainCruiseAllowed"   → allow on main cruise
#   "MadsSteeringMode"        → steering behavior on brake
#   "MadsUnifiedEngagementMode" → unified engagement

# Custom message: custom.SelfdriveStateSP.mads (ModularAssistiveDrivingSystem)
# Hyundai special: allow_always=True for HAS_LDA_BUTTON or CANFD
```

## 8.2 Model Manager

```python
# sunnypilot/models/manager.py + helpers.py
# Manages downloadable model bundles

# Bundle stored in: params.get("ModelManager_ActiveBundle") → ModelBundle capnp
# Runner determined by: bundle.runner.raw → Runner enum (snpe/tinygrad/stock)
# Cached in: params.get("ModelRunnerTypeCache") → str(int)

# Bundle contains:
#   drive model  → .onnx or _tinygrad.pkl or .dlc (SNPE)
#   metadata     → .pkl (pickle of input_shapes, output_slices)
#   navigation model (optional)

# Model root path: Paths.model_root()
```

## 8.3 Neural Network Lateral Control (NNLC)

```python
# Commit: 309304a35 Controls: Neural Network Lateral Control (NNLC)
# Torque lateral accel extension
# Param: "NeuralNetworkLateralControl"
# Location: sunnypilot/selfdrive/controls/
# Uses: sunnypilot/neural_network_data/neural_network_lateral_control/
```

## 8.4 Automatic Lane Change

```python
# Commit: 34bbdf4d7 Controls: Automatic lane change
# Params: "AutoLaneChangeTimer", "AutoLaneChangeBsmDelay"
```

## 8.5 SunnyLink

```python
# sunnypilot/sunnylink/
# Remote access / settings backup-restore
# Params: controlled by sunnylink_ready(), sunnylink_need_register(), use_sunnylink_uploader()
```

## 8.6 Custom Cereal Messages

```
cereal/custom.capnp defines all sunnypilot-specific messages:

ModularAssistiveDrivingSystem  → MADS state
SelfdriveStateSP               → extends selfdriveState with MADS
ModelManagerSP                 → model bundle management
  Runner enum: snpe / tinygrad / stock
  Type enum: drive / navigation / metadata
  DownloadStatus: notDownloading/downloading/downloaded/cached/failed
CarParamsSP                    → extended car params
OnroadEventSP                  → sunnypilot-specific events
```

---

# SECTION 9 — MESSAGE ARCHITECTURE

## 9.1 Core Message Flow

```
Camera → roadCameraState / driverCameraState / wideRoadCameraState
       → VisionIPC (frames)

modeld → modelV2, drivingModelData, cameraOdometry

plannerd → longitudinalPlan, driverAssistance

controlsd → carControl, controlsState

selfdrived → selfdriveState, onroadEvents

card → carState, carParams, carOutput

locationd → livePose
calibrationd → liveCalibration
paramsd → liveParameters
torqued → liveTorqueParameters
```

## 9.2 Key Service Frequencies (cereal/services.py)

```
carState:          100 Hz
carControl:        100 Hz
controlsState:     100 Hz
selfdriveState:    50 Hz
modelV2:           20 Hz
roadCameraState:   20 Hz
driverCameraState: 20 Hz
longitudinalPlan:  10 Hz
livePose:          10 Hz
liveCalibration:   2 Hz
liveParameters:    10 Hz
```

## 9.3 Important Params Keys

```
CarParams                    → CLEAR_ON_MANAGER_START | CLEAR_ON_ONROAD_TRANSITION
CarParamsSP                  → sunnypilot car params
ModelManager_ActiveBundle    → active model bundle (capnp bytes)
ModelRunnerTypeCache         → cached runner type string
Mads                         → MADS master toggle
MadsMainCruiseAllowed        → MADS on main cruise
NeuralNetworkLateralControl  → NNLC toggle
AutoLaneChangeTimer          → ALC timer
QuietMode                    → quiet mode
LocationFilterInitialState   → Kalman filter seed
LiveTorqueParameters         → PERSISTENT | DONT_LOG
```

---

# SECTION 10 — HARDWARE ABSTRACTION

## 10.1 Hardware Detection

```python
# system/hardware/__init__.py  (merged version — RK3588-aware)
TICI = os.path.isfile('/TICI')
PC   = not TICI

def _is_rk3588():
    """Detect RK3588 via device tree."""
    with open('/proc/device-tree/compatible') as f:
        return 'rk3588' in f.read()

RK3588 = _is_rk3588()

if TICI:
  HARDWARE = Tici()
elif RK3588:
  HARDWARE = RK3588Hardware(detected=True)    # ← links to common/hardware/rk3588/hardware.py
else:
  HARDWARE = Pc()
```

**NOTE: This project targets Orange Pi 5 only. Comma 3/3X (TICI) is NOT used.**
The `TICI` branch and all TICI hardware code (`smbus2`, amplifier, etc.) are irrelevant
and have not been adapted for this platform. The `smbus2` import error is harmless —
it only triggers if `/TICI` file exists, which it does not on Orange Pi 5.

**CRITICAL: `get_device_type()` must return `"pc"`.** RK3588Hardware's `get_device_type()`
returns `"pc"` (not `"rk3588"`) because `DEVICE_CAMERAS` dictionary only has keys for
`("pc", ...)`, `("tici", ...)`, `("neo", ...)`. Without this, modeld crashes at:
`DEVICE_CAMERAS[("rk3588", "unknown")]` → KeyError.
See commit `1109bdba6` for the fix.

On Orange Pi 5:
```
TICI    = False    (no /TICI file)
PC      = True     (PC = not TICI — unchanged from original)
RK3588  = True     (detected via device tree)

HARDWARE = RK3588Hardware    ← NOT Pc anymore
```

The `RK3588Hardware` class lives in `common/hardware/rk3588/hardware.py` and provides:
- CPU governor optimization (A76@2.256GHz, A55@1.8GHz)
- NPU frequency management (1GHz)
- Thermal zone monitoring (CPU, GPU, NPU temperatures)
- CAN interface setup
- PWM fan control
- Device variant detection

**No existing code breaks** because `PC` and `TICI` values stay the same.
Only `HARDWARE` changes from `Pc()` to `RK3588Hardware()` on Orange Pi 5.

# On Orange Pi 5: PC=False, TICI=False
# This means: PC-gated processes disabled, TICI-gated processes disabled
# → sensord disabled (not PC)
# → encoderd disabled (not PC)
# → modeld_snpe/modeld_tinygrad enabled (not PC)
```

## 10.2 Paths

```python
# system/hardware/hw.py  Paths class
Paths.model_root()    → path to custom model directory
Paths.shm_path()      → shared memory path
```

---

# SECTION 11 — BUILD SYSTEM

## 11.1 SCons

```
Build entry: SConstruct (root)
Submodule builds: cereal/SConscript, msgq_repo/SConscript, etc.
Model compilation: selfdrive/modeld/SConscript
  - Compiles tinygrad models from .onnx → _tinygrad.pkl
  - Compiles commonmodel .so for Cython

Build command:
  scons -j$(nproc)

GPU device strings:
  larch64 (Orange Pi 5): QCOM=1
  Darwin:                CLANG=1 IMAGE=0
  x86/other:             GPU=1 BEAM=0 IMAGE=0
```

---

# SECTION 12 — COMPLETE ENVIRONMENT VARIABLES REFERENCE

```bash
# Camera
USE_WEBCAM=1              # use Python webcam pipeline instead of native camerad
ROAD_CAM=0                # road camera device (int index or /dev/videoX path)
DRIVER_CAM=2              # driver camera device
WIDE_CAM=/dev/videoX      # optional wide camera

# Driver Monitoring
NO_DM=1                   # disable dmonitoringmodeld and dmonitoringd

# Sensors
NO_IMU=1                  # skip gyroscope observations in locationd

# Model Backend
OPENPILOT_MODELD_BACKEND=rknn|tinygrad|auto

# RKNN (when backend=rknn)
RKNN_VISION_CORE=0
RKNN_POLICY_CORE=1
RK_USE_DMABUF=1
RK_USE_EGLIMAGE=1

# Debug
REPLAY=1                  # replay mode (relaxes some checks)
SIMULATION=1              # simulation mode
DEBUG=0                   # locationd debug output (0 or 1)
SEND_RAW_PRED=1           # include raw model output in publish
TESTING_CLOSET=1          # testing closet mode

# Runtime
QCOM=1                    # enable Qualcomm path in tinygrad (set for larch64)
```

---

# SECTION 13 — PRODUCTION PIPELINE (TARGET STATE)

## 13.1 Full Production Flow

```
IMX415
   ↓ MIPI CSI-2
RKISP
   ↓ V4L2
NV12 DMA-BUF
   ├─────────────────────────────┬─────────────────────────┐
   │                             │                         │
   ▼                             ▼                         ▼
VisionIPC (zero-copy)        EGLImage                  loggerd
   ↓                             ↓
modeld                        Mali GPU Texture
   ↓                             ↓
loadyuv.cl + transform.cl     UI camera preview
   ↓                             ↓
model tensor                  OpenGL overlay
   ↓
RKNN Vision Core 0
   ↓
RKNN Policy Core 1
   ↓
modelV2/msgq
   ↓
plannerd
   ↓
controlsd
   ↓
card → sendcan → CAN bus → Vehicle
```

## 13.2 Current Development Flow

```
/dev/videoX (USB cam or IMX415 V4L2)
   ↓ cv2.VideoCapture (OpenCV MJPG)
CameraMJPG.read_frames() → bgr2nv12 (CPU)
   ↓
Camerad._send_yuv() → VisionIPC
   ↓
selfdrive/modeld/modeld.py or sunnypilot/modeld_v2/modeld.py
   ↓ (ONNXRunner on PC, TinygradRunner on TICI)
modelV2 → plannerd → controlsd
```

## 13.3 CPU Pinning and Real-Time Scheduling

Consistent latency requires two things: **fast cores** and **no interruptions**.

### A76 Big Core Pinning

The RK3588 has 8 CPU cores: 4× Cortex-A76 at 2.4GHz (cores 4-7) and 4× Cortex-A55 at 1.8GHz (cores 0-3).
The OS can schedule `modeld` on any core randomly. Pinning forces it to the fast A76 cores:

```python
os.sched_setaffinity(0, {4, 5, 6, 7})   # modeld → A76 only
```

Without pinning: A76 ~2.4GHz vs A55 ~1.8GHz = ~25% slower if scheduled on the wrong core.

### SCHED_FIFO Real-Time Priority

Normally the Linux scheduler can pause any process mid-frame to run another task.
This causes latency spikes (e.g. 22ms frame suddenly takes 40ms).

With `SCHED_FIFO priority 54`:
- Once `modeld` starts running a frame, the OS will **not interrupt** it
- The frame runs to completion
- Eliminates random latency spikes

```python
param = sched_param(sched_priority=54)
sched_setscheduler(0, SCHED_FIFO, param)   # no interruptions
```

**Requires root.** Falls back gracefully if unavailable.

### Recommended modeld Configuration

```python
# modeld startup (sunnypilot/modeld_v2/modeld.py)
config_realtime_process(7, 54)             # core 7 + priority 54 (existing)
os.sched_setaffinity(0, {4, 5, 6, 7})     # all A76 cores (RKNN addition)
sched_setscheduler(0, SCHED_FIFO, ...)     # real-time mode (RKNN addition)
```

Together they guarantee: **fast core + no interruptions = consistent 22ms every frame**.

## 13.4 RGA Hardware Accelerator (Future Optimization)

The RK3588 has a dedicated **RGA (Raster Graphics Accelerator)** chip for hardware image
processing, separate from CPU, GPU, and NPU.

### What RGA does
```
Resize:     Any resolution → any resolution in hardware (<1ms)
Crop:       Hardware crop without CPU copy
Rotate:     Hardware rotation (0, 90, 180, 270)
Convert:    NV12 ↔ RGB ↔ YUV ↔ BGR in hardware
```

### Where RGA would help

**Model preprocessing (biggest gain):**
```
Current:    CPU NV12→BGR→resize→YUV         8ms
With RGA:   RGA NV12→resize→YUV             1ms  ← saves 7ms
```
The `rga.py` file exists in `common/hardware/rk3588/` but needs DMA-BUF file
descriptors (not numpy arrays) to operate. Not yet wired.

**UI camera preview (small gain):**
```
Current:    GPU renders full-resolution camera + overlay
With RGA:   RGA pre-resizes camera frame → GPU uploads smaller texture
```
Gain: ~1-2ms on UI. Mali GPU already runs at 60fps — UI is not the bottleneck.

### What RGA CANNOT do
- ❌ Render UI overlays (paths, lanes, alerts) — GPU's job
- ❌ Draw text, shapes, lines — GPU's job
- ❌ Run AI inference — NPU's job
- ❌ Composite layers — GPU's job

### Priority
```
RGA for model preprocessing:   HIGH priority (saves 7ms)
RGA for UI preview:            LOW priority (GPU already fast)
```

## 13.5 Performance Targets

```
Mode 1 (current):   camera → modelV2: 18–30ms, camera → UI: 30–45ms
Mode 2 (+DMA-BUF):  camera → modelV2: 15–27ms
Mode 3 (+EGLImage): camera → modelV2: 15–27ms, camera → UI: 20–35ms

Vision RKNN:   8–12ms
Policy RKNN:   2–5ms
Combined:      <20ms
Total pipeline:<30ms (target), <25ms (preferred)
```

---

# SECTION 14 — AI AGENT RULES (ABSOLUTE)

## 14.1 Before Writing Any Code

```
Step 1: Read GOD.md (this document)
Step 2: Identify the subsystem being modified (camera/modeld/controls/etc.)
Step 3: Read the relevant domain doc in Ai/ai/
Step 4: Check FORBIDDEN list (Section 14.3)
Step 5: Confirm Validation Plan exists
Step 6: Write code
Step 7: Validate
```

## 14.2 What Is Safe To Modify

```
✅ Camera integration (tools/webcam/, system/camerad/)
✅ VisionIPC configuration (stream count, buffer sizes)
✅ RKNN inference backend (add RKNNRunner, swap from Tinygrad)
✅ DMA-BUF export/import path
✅ EGLImage camera preview path
✅ Validation hooks and tooling
✅ Performance measurement tooling
✅ Sunnypilot feature toggles (params)
✅ UI adaptations (resolution, layout)
✅ Environment variable gates for new features
✅ Process manager enable/disable conditions
```

## 14.3 FORBIDDEN — Never Modify These Without Explicit Validation

```
❌ Planner logic (plannerd.py, longitudinal_planner.py)
❌ Controls semantics (controlsd.py output behavior)
❌ Vehicle interface CAN encoding (opendbc)
❌ loadyuv.cl kernel
❌ transform.cl kernel
❌ DrivingModelFrame.prepare() preprocessing
❌ warp generation logic (get_warp_matrix)
❌ Message schema (cereal/log.capnp) — only cereal/custom.capnp for sunnypilot
❌ modelV2 field semantics and units
❌ Metadata output slice positions (read from metadata, never hardcode)
❌ Remove or bypass Tinygrad fallback backend
❌ Hidden state reset pattern (must persist across frames)
❌ Output hardcoding: outputs[0], outputs[1] — always use metadata slices
❌ NCHW/NHWC assumption without validation
❌ Adding sensor validation that requires hardware not present on RK3588
❌ Making NO_IMU=0 the default behavior (IMU hardware doesn't exist)
❌ Hardcoding /dev/videoX device numbers
❌ Force-disabling modeld single-camera fallback
```

## 14.4 Pattern Rules

```python
# CORRECT: backend selection
backend = os.environ.get("OPENPILOT_MODELD_BACKEND", "auto")
if backend == "rknn":
  runner = RKNNRunner(...)
else:
  runner = TinygradRunner(...)

# CORRECT: metadata-driven output parsing
path = metadata.get_output(outputs, "path")   # NOT: outputs[0]

# CORRECT: layout validation
if model_requires_nhwc:
  tensor = np.transpose(tensor, (0, 2, 3, 1))

# CORRECT: NPU core assignment
vision_runner = RKNNRunner(model_path=VISION_MODEL, core_id=0)
policy_runner = RKNNRunner(model_path=POLICY_MODEL, core_id=1)
# NEVER: core_id = RKNNLite.NPU_CORE_AUTO for production

# CORRECT: error handling
try:
  outputs = runner.infer(inputs)
except Exception:
  log_error()
  fallback_to_tinygrad()
  # NEVER silently publish invalid outputs

# CORRECT: camera device
device = os.getenv("ROAD_CAM", "0")   # NOT hardcoded "0" or "/dev/video11"
```

## 14.5 Validation Requirements Before Merging

```
Any modeld/RKNN change requires:
  □ Tinygrad reference outputs generated (100+ frames minimum)
  □ RKNN outputs compared against Tinygrad reference
  □ Correlation > 0.995 on vision model
  □ Correlation > 0.995 on policy model
  □ Hidden state persistence verified across 100+ frames
  □ modelV2 schema unchanged
  □ planner receives correct messages at correct frequency
  □ latency measured and within target

Any camera change requires:
  □ NV12 layout validated (width, height, stride, size)
  □ VisionIPC stream confirmed alive
  □ Timestamps monotonic
  □ Tensor statistics match reference (before/after)
```

---

# SECTION 15 — KNOWN DRIFT FROM DOCUMENTATION

These are confirmed differences between what Ai/commit.md documents and what the code actually does today (as of HEAD 3ad69b20b, 2026-06-10):

## 15.1 IMU Handling (Stronger Than Documented)

```
Document says: "relax startup requirements, allow no IMU"
Reality: IMU socket drain is FULLY commented out
         Physical sensor data is NEVER read
         Filter runs on camera odometry only
         sensors_valid hardcoded to True
File: selfdrive/locationd/locationd.py lines 273, 302
```

## 15.2 dmonitoringmodeld Spin-Wait Risk

```
If started WITHOUT driver camera stream AND NO_DM is not set:
  dmonitoringmodeld will spin-wait forever at line 147
  (blocking connect to VISION_STREAM_DRIVER with no timeout)
Mitigation: always set NO_DM=1 when no driver camera connected
```

## 15.3 Manager Services Not Blanket-Disabled

```
Document says: "manager disables unsupported services"
Reality: Services disabled only via:
  - WEBCAM env var (camerad ↔ webcamerad)
  - NO_DM env var (dmonitoringmodeld/d)
  - PC hardware flag (sensord, encoderd, etc.)
  No RK3588-specific service disable list exists
```

## 15.4 Forbidden Production Path Is Current State

```
The CameraMJPG (OpenCV MJPG → BGR → NV12) path IS the current camera path.
This is explicitly the "forbidden production path" in imx415.md.
It is acceptable for development bring-up.
It MUST be replaced with RKISP → V4L2 → NV12 DMA-BUF for production.
```

---

# SECTION 16 — RKNN INTEGRATION GUIDE

## 16.1 RKNNRunner Design (from Ai/examples/rknn_runner_example.md)

```python
class RKNNRunner:
  def __init__(self, model_path, model_name, core_id,
               expected_inputs=None, expected_outputs=None, nhwc_inputs=None):
    # core_id: 0=vision, 1=policy, 2=reserved
    ...

  def initialize(self):
    self._validate_model_file()   # check exists, readable, non-empty
    rknn = RKNNLite()
    rknn.load_rknn(str(self.model_path))
    core_mask = {0: NPU_CORE_0, 1: NPU_CORE_1, 2: NPU_CORE_2}[core_id]
    rknn.init_runtime(core_mask=core_mask)
    self._write_runtime_report()  # JSON report to /tmp/

  def infer(self, inputs: dict) -> list[np.ndarray]:
    ordered = self._prepare_inputs(inputs)   # validate shapes + NCHW→NHWC
    outputs = self.rknn.inference(inputs=ordered)
    return self._validate_outputs(outputs)   # check finite, check shape
    # NEVER return invalid outputs
```

## 16.2 Vision Model Inputs (known from current onnx models)

```python
# selfdrive/modeld/models/driving_vision.onnx
expected_inputs = {
    "img":     (1, 12, 128, 256),
    "big_img": (1, 12, 128, 256),
}
nhwc_inputs = {"img", "big_img"}   # RKNN likely requires NHWC

# sunnypilot/modeld_v2/models/supercombo.onnx
# input_shapes loaded from metadata pickle
# ALWAYS read from metadata — do not hardcode
```

## 16.3 Policy Model Inputs

```python
expected_inputs = {
    "features_buffer":    (1, 512),    # may vary — read from metadata
    "desire":             (1, 8),
    "traffic_convention": (1, 2),
    "lateral_control_params": (1, 2),
    "prev_desired_curv":  (1, ...),
}
```

## 16.4 Integration Into Existing Pipeline

```python
# In model_runner.py (sunnypilot/modeld_v2/):
# Add RKNNRunner alongside TinygradRunner/ONNXRunner

backend = os.environ.get("OPENPILOT_MODELD_BACKEND", "auto")

if backend == "rknn":
  if not (vision_rknn_path.exists() and policy_rknn_path.exists()):
    backend = "tinygrad"   # graceful fallback

if backend == "rknn":
  self.model_runner = RKNNRunner(...)
elif TICI:
  self.model_runner = TinygradRunner()
else:
  self.model_runner = ONNXRunner()
```

---

# SECTION 17 — UI ADAPTATIONS

## 17.1 Resolution Change

```
Commit: bf3f07e7a feat(ui): Adapter ui size to 800x400
Target display: 800×400 (Orange Pi 5 typical HDMI output)
Original OpenPilot: 2160×1080 (Comma 3X)
File: selfdrive/ui/qt/
```

## 17.2 UI Process

```python
# process_config.py:
NativeProcess("ui", "selfdrive/ui", ["./ui"], always_run,
              watchdog_max_dt=(5 if not PC else None))
PythonProcess("soundd", "selfdrive.ui.soundd", only_onroad, enabled=not PC)
```

---

# SECTION 18 — LONGITUDINAL CONTROL CHANGES

## 18.1 LEAD_DANGER_FACTOR Change

```
Commit: 3ad69b20b fix(lon): Change LEAD_DANGER_FACTOR (HEAD)
File: selfdrive/controls/lib/longitudinal_planner.py
Purpose: Optimize longitudinal control behavior for RK3588 platform
```

## 18.2 Other Lon Changes

```
Commit: ddf8fa492 fix(lon): Opt lon ctrl
Commit: 28b99cc23 feat(lon): Opt lon control
Purpose: Tuning for real-world driving on Orange Pi 5 hardware
```

---

# SECTION 19 — HOW TO USE THIS DOCUMENT IN GITHUB COPILOT

## 19.1 Reference in Chat

```
When asking Copilot to write code, start with:
"Read Ai/GOD.md and follow all rules in it, then..."

Or attach GOD.md as context and say:
"Using the architecture in GOD.md, implement X"
```

## 19.2 Key Context Snippets to Always Include

When asking for modeld changes:
```
"Follow GOD.md Section 5 — preserve loadyuv.cl, transform.cl,
metadata-driven slicing, no hardcoded indices, keep Tinygrad fallback"
```

When asking for camera changes:
```
"Follow GOD.md Section 4 — use env var gating,
target DMA-BUF path, preserve NV12 layout validation"
```

When asking for RKNN integration:
```
"Follow GOD.md Section 16 — use RKNNRunner class,
Vision=Core0, Policy=Core1, never AUTO core, fail-fast on invalid output"
```

When asking for any change:
```
"Follow GOD.md Section 14 — check forbidden list,
add env var gate, preserve all existing interfaces"
```

---

# SECTION 20 — CHECKLISTS

## 20.1 Camera Change Checklist

```
□ Camera device path comes from env var (not hardcoded)
□ NV12 layout detected dynamically (stride != assumed tight)
□ VisionIPC stream name unchanged ("camerad")
□ Timestamps monotonic
□ Tensor stats before/after match reference
□ Works with USE_WEBCAM=1 path unchanged
□ NO_DM guard preserved
□ dmonitoringmodeld spin-wait risk addressed if NO_DM=0
```

## 20.2 Modeld / RKNN Change Checklist

```
□ Tinygrad fallback path still works
□ ONNXRunner still works (PC development)
□ output_slices read from metadata (not hardcoded)
□ input_shapes read from metadata (not hardcoded)
□ NCHW/NHWC validated from model, not assumed
□ Hidden state persists across frames
□ Vision RKNN on Core 0, Policy RKNN on Core 1
□ NPU_CORE_AUTO not used
□ Correlation > 0.995 vs Tinygrad reference
□ 100+ consecutive frames validated
□ modelV2 schema identical
□ planner unmodified
□ controlsd unmodified
□ Error: fail-fast, never publish invalid outputs
```

## 20.3 New Feature Checklist

```
□ Feature gated behind env var or param
□ Default behavior preserved when gate is off
□ Existing tests still pass
□ No planner/controls/message semantic changes
□ All new code follows import path convention (openpilot.*)
□ New params added to params_keys.h with correct flags
□ New cereal messages only in cereal/custom.capnp
□ Fallback to previous behavior if feature fails
```

## 20.4 Production Deployment Checklist

```
□ Camera PASS (frames, timestamps, NV12 layout)
□ VisionIPC PASS (streams alive, no drops)
□ Modeld PASS (tensor stats, output correlation)
□ Planner PASS (stable, correct frequency)
□ Controls PASS (no unsafe behavior)
□ Latency PASS (camera→modelV2 < 30ms)
□ Stress PASS (1hr minimum, 4hr preferred)
□ Recovery PASS (camera/modeld/planner restart)
□ Rollback PASS (known-good build exists)
□ NO_DM, NO_IMU, USE_WEBCAM documented for deployment
□ OPENPILOT_MODELD_BACKEND set explicitly
```

---

# SECTION 21 — QUICK REFERENCE CARD

## 21.1 Key File Locations

```
Camera pipeline:
  tools/webcam/camera.py          ← CameraMJPG / Camera classes
  tools/webcam/camerad.py         ← Camerad + VisionIPC server
  common/transformations/camera.py ← intrinsics, DEVICE_CAMERAS

modeld:
  selfdrive/modeld/modeld.py      ← stock modeld (Runner.stock)
  sunnypilot/modeld_v2/modeld.py  ← sunnypilot modeld (Runner.tinygrad)
  sunnypilot/modeld_v2/model_runner.py ← ModelRunner ABC, TinygradRunner, ONNXRunner
  sunnypilot/models/helpers.py    ← get_active_bundle(), get_active_model_runner()

Controls:
  selfdrive/selfdrived/selfdrived.py  ← state machine, MADS integration
  selfdrive/controls/controlsd.py    ← lat/long actuator control
  selfdrive/controls/plannerd.py     ← trajectory planning
  selfdrive/car/card.py              ← CAN interface

Location:
  selfdrive/locationd/locationd.py   ← Kalman filter, NO_IMU gate

Process management:
  system/manager/process_config.py   ← process table, WEBCAM/NO_DM gates
  system/manager/manager.py          ← process startup, params init

Messages:
  cereal/log.capnp                   ← base OpenPilot messages
  cereal/custom.capnp                ← sunnypilot custom messages

Params:
  common/params_keys.h               ← all param keys + flags

AI Pack:
  Ai/GOD.md                          ← THIS DOCUMENT
  Ai/ai/camera.md                    ← camera spec
  Ai/ai/modeld.md                    ← modeld spec
  Ai/ai/rknn.md                      ← RKNN spec
  Ai/ai/visionipc.md                 ← VisionIPC spec
  Ai/examples/rknn_runner_example.md ← complete RKNNRunner code
```

## 21.2 One-Line Architecture Summary

```
IMX415 → RKISP → V4L2 → NV12 DMA-BUF → VisionIPC →
modeld (OpenCL preproc → RKNN/Tinygrad Vision→Policy) →
modelV2 → plannerd → controlsd → card → CAN → Vehicle
```

## 21.3 Current Departure From Target

```
Target:  IMX415 → RKISP → DMA-BUF → VisionIPC (zero-copy)
Current: /dev/videoX → OpenCV MJPG → BGR→NV12 CPU copy → VisionIPC
Gap:     ~5-8ms latency penalty, higher CPU usage
Fix:     Implement RKISP V4L2 capture with DMA-BUF export
```

---

# SECTION 22 — COMMIT ANALYSIS SUMMARY

This section summarizes the detailed findings in `Ai/commit.md`. Read that file for the full analysis.

## 22.1 Branch Purpose (Critical Understanding)

Many developers assume the branch is about RK3588 NPU acceleration.

The actual purpose is:

```
OpenPilot
↓
Remove Comma Hardware Dependencies
↓
Add Webcam / V4L2 Support
↓
Allow No IMU
↓
Allow No Driver Camera
↓
Adapt Camera Geometry for IMX415
↓
Adapt UI Resolution to 800×400
↓
Run on Orange Pi 5
```

This branch is primarily a **Linux SBC adaptation branch**, not an RKNN NPU branch.

## 22.2 Key Commit Breakdown

| Commit | Purpose | What Breaks If Removed |
|---|---|---|
| b51be4e (Make op run) | Foundation — hardware relaxation, webcam bridge | Everything fails to start |
| f39cc16 (Adapter to rk3588) | Timing adjustments, timeout relaxation, scheduling | False timeouts, starvation |
| 6e91b9c (Old local route) | Offline replay support | No offline testing |
| cab810f (Fix tools) | Reduced process requirements for dev | Bench testing harder |
| 95af03c (Camera focal) | First IMX415 focal length correction | Wrong lane/path overlay |
| 712bcb2 (IMX415 focal) | Second focal length correction (900) | Persistent calibration errors |
| bf3f07e (UI 800×400) | 60+ files — UI adaptation for small display | UI broken on embedded panels |
| 306a880 (No IMU) | NO_IMU=1 support | locationd fails without IMU |
| 28b99cc (Opt lon control) | Longitudinal control tuning | Suboptimal RK3588 behavior |
| ddf8fa4 (Opt lon ctrl) | Further longitudinal optimization | Same |
| 3ad69b20 (LEAD_DANGER) | LEAD_DANGER_FACTOR change | Longitudinal follow distance |

## 22.3 What This Branch Does NOT Do

```
❌ Does NOT use RKNN NPU (no librknnrt.so, no .rknn models)
❌ Does NOT accelerate modeld via NPU
❌ Does NOT add RKNN inference pipeline (prepared for future)
❌ Does NOT implement zero-copy camera path (prepared for future)
❌ Does NOT use Comma hardware

✅ DOES make OpenPilot boot and run on Orange Pi 5
✅ DOES enable camera via V4L2/webcam
✅ DOES adapt geometry for IMX415
✅ DOES adapt UI for small displays
✅ DOES allow operation without IMU/sensors
✅ DOES prepare infrastructure for future RKNN integration
```

## 22.4 Drift Between commit.md and Current Code

Key findings (confirmed at HEAD 3ad69b20b):

```
1. IMU handling is STRONGER than documented
   → IMU drain path commented out entirely (locationd.py:273)
   → Sensors NEVER read regardless of NO_IMU
   → sensors_valid hardcoded to True

2. dmonitoringmodeld has spin-wait risk
   → Blocking connect to driver stream with no timeout
   → Mitigation: always set NO_DM=1 without driver camera

3. Manager does NOT have blanket RK3588 disable list
   → Only env-var gated (WEBCAM, NO_DM, PC flag)
   → sensord/encoderd/etc. still enabled on non-PC builds
```

---

# SECTION 23 — TESTING & VALIDATION WORKFLOW

## 23.1 Validation Philosophy

Before any change is merged, it must pass validation at its level:

```
Cosmetic change  → visual inspection
Config change    → env var test
Camera change    → frame validation + timestamps + NV12 layout
Modeld change    → tensor stats + output correlation (0.995+)
RKNN change      → Tinygrad reference + cross-runtime comparison
Controls change  → planner stability + CAN output validation
Production       → Full checklist (Section 20.4)
```

## 23.2 Replay Testing

Offline replay is the primary validation method:

```bash
# Replay a recorded route (needs route data in local directory)
cd sunnypilot-pc
./tools/replay/replay --data <route_data_dir>

# With specific services enabled
./tools/replay/replay --data <dir> --only modeld,plannerd

# Without driver monitoring
NO_DM=1 ./tools/replay/replay --data <dir>
```

Replay validates:
- Model outputs match expected
- Planner produces stable trajectories
- No crashes or hangs
- Message frequencies correct

## 23.3 Component-Level Testing

```bash
# Test camera capture
python -c "
import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
print('Frame shape:', frame.shape if ret else 'FAIL')
cap.release()
"

# Check V4L2 device capabilities
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video0 --list-formats-ext

# Test VisionIPC stream
# Run webcamerad standalone:
USE_WEBCAM=1 ROAD_CAM=0 python -m tools.webcam.camerad

# Run modeld standalone (needs VisionIPC running):
python -m selfdrive.modeld.modeld
```

## 23.4 End-to-End System Test

```bash
# Minimum viable test (no driver cam, no IMU):
NO_DM=1 NO_IMU=1 USE_WEBCAM=1 ROAD_CAM=0 ./launch_openpilot.sh

# With driver camera:
NO_IMU=1 USE_WEBCAM=1 ROAD_CAM=0 DRIVER_CAM=2 ./launch_openpilot.sh
```

Expected startup sequence:
```
1. manager starts
2. webcamerad connects to /dev/videoX
3. VisionIPC stream goes live
4. modeld connects and starts inference
5. plannerd, controlsd start
6. UI renders camera preview
```

## 23.5 Stress Testing

```
Minimum:  1 hour continuous run
Preferred: 4+ hours

Monitor:
  - CPU utilization per core
  - Memory usage (watch for leaks)
  - FPS stability
  - Temperature (RK3588 throttles at 85°C)
  - Log messages (no repeated errors)
```

## 23.6 Recovery Testing

Test that the system recovers from:

```bash
# Kill webcamerad — manager should restart it
pkill -f webcamerad

# Kill modeld — should restart and re-connect to VisionIPC
pkill -f "python.*modeld"

# Camera cable unplug/replug
# Check VisionIPC reconnection

# Power cycle test
# Verify persistent params survive reboot
```

## 23.7 Cross-Runtime Validation

When changing model backends (Tinygrad ↔ RKNN):

```
1. Run 100+ frames with Tinygrad → save reference outputs
2. Run same frames with RKNN → save test outputs
3. Compare per-output correlation
4. PASS criteria: correlation > 0.995 on vision + policy
5. Verify hidden state persistence across all frames
6. Verify modelV2 schema identical
7. Verify planner receives correct messages
```

---

# SECTION 24 — DEPLOYMENT GUIDE

## 24.1 Build Instructions

```bash
# Clone repository
git clone https://github.com/MM-X/sunnypilot-pc.git
cd sunnypilot-pc

# Initialize submodules
git submodule update --init --recursive

# Build with SCons
scons -j$(nproc)

# For RK3588 (Orange Pi 5), set QCOM=1 for tinygrad larch64:
QCOM=1 scons -j$(nproc)
```

## 24.2 Environment Setup (Orange Pi 5)

Required packages:
```bash
# System dependencies
sudo apt update
sudo apt install -y \
  python3 python3-pip python3-dev \
  libopencv-dev \
  v4l-utils \
  cmake build-essential \
  libssl-dev

# Python dependencies
pip install -r requirements.txt
pip install opencv-python pyav numpy

# For RKNN (when backend=rknn):
# Install RKNN Toolkit Lite 2 from Rockchip SDK
```

## 24.3 Camera Configuration

```bash
# List V4L2 devices
v4l2-ctl --list-devices

# Typical Orange Pi 5 IMX415 mapping:
# /dev/video0  → RKISP main (IMX415 road camera)
# /dev/video11 → RKISP dummy (configuration only)
# /dev/video31 → RGA (hardware accelerator)

# Test camera capture:
USE_WEBCAM=1 ROAD_CAM=0 python -c "
from tools.webcam.camera import CameraMJPG
cam = CameraMJPG('0', 1280, 720, 20)
frame = cam.read_frame()
print('Camera OK' if frame is not None else 'Camera FAIL')
"
```

## 24.4 First-Run Procedure

```bash
# 1. Set environment variables
export USE_WEBCAM=1
export ROAD_CAM=0
export NO_DM=1        # unless driver camera connected
export NO_IMU=1       # Orange Pi 5 has no IMU

# 2. Launch
./launch_openpilot.sh

# 3. Monitor logs
tail -f /tmp/openpilot/log/*.log

# 4. Check processes
ps aux | grep -E "manager|webcam|modeld|ui"

# 5. Verify VisionIPC
python -c "
from openpilot.system.hardware import PC, TICI
print(f'PC={PC}, TICI={TICI}')
print('Hardware detection OK')
"
```

## 24.5 Production Deployment Checklist

See Section 20.4 for full checklist.

Key environment for production:
```bash
export USE_WEBCAM=1
export ROAD_CAM=0                    # or actual /dev/videoX
export NO_DM=1                       # if no driver camera
export NO_IMU=1                      # RK3588 has no IMU
export OPENPILOT_MODELD_BACKEND=auto # or rknn/tinygrad
export RKNN_VISION_CORE=0
export RKNN_POLICY_CORE=1
```

## 24.6 Rollback Procedure

```bash
# Keep last known-good build:
cp -a sunnypilot-pc sunnypilot-pc.bak

# To rollback:
cd sunnypilot-pc && git checkout <last-good-commit>
scons -j$(nproc)
./launch_openpilot.sh

# Or restore backup:
mv sunnypilot-pc.bak sunnypilot-pc
```

---

# SECTION 25 — TROUBLESHOOTING COMMON ISSUES

## 25.1 Camera Issues

| Symptom | Likely Cause | Fix |
|---|---|---|
| No frames | Wrong /dev/videoX | Check v4l2-ctl --list-devices, set ROAD_CAM |
| Green/purple image | Wrong format (BGR vs MJPG) | Check camera.py fourcc setting |
| Camera CV2 error | Device busy or wrong index | `sudo fuser -v /dev/video*` |
| Low FPS | USB bandwidth (USB cam) | Use direct IMX415, not USB |
| Camera not detected | No V4L2 driver | `sudo modprobe rkisp` |
| cv2.VideoCapture(0) fails | Wrong device number | Try 1, 2, or /dev/videoX path |

## 25.2 Startup / Process Issues

| Symptom | Likely Cause | Fix |
|---|---|---|
| manager exits immediately | Missing critical service | Check environment vars are set |
| modeld won't start | VisionIPC not ready | Start webcamerad first |
| dmonitoringmodeld hung | No driver camera, NO_DM not set | Set NO_DM=1 |
| UI blank | No camera frames | Verify webcamerad is publishing |
| Process repeatedly crashing | watchdog timeout | Check timestamps, process timing |
| "No IMU" errors | sensord not available | Set NO_IMU=1 |

## 25.3 Modeld Issues

| Symptom | Likely Cause | Fix |
|---|---|---|
| NaN outputs | Corrupt input tensor | Check NV12 layout, preprocessing |
| Wrong path/lane detection | Wrong focal length | Verify camera.py intrinsics |
| Model load failure | Missing model file | Run scons to compile models |
| Tinygrad error | Missing GPU driver | Set OPENPILOT_MODELD_BACKEND=onnx |
| RKNN inference fails | No RKNN runtime | Install RKNN Toolkit Lite 2 |
| Hidden state reset | Camera restart | Check VisionIPC reconnection |

## 25.4 CAN / Vehicle Issues

| Symptom | Likely Cause | Fix |
|---|---|---|
| No panda found | Panda not connected | `lsusb`, check panda driver |
| CAN timeout | Panda firmware mismatch | Flash panda with correct firmware |
| Car not recognized | No fingerprint data | Drive briefly, check carState |
| Steering not working | Wrong car interface | Check opendbc fingerprint |

## 25.5 Debugging Commands

```bash
# Check process health
ps aux | grep -E "manager|webcam|modeld|ui|panda"

# Check message bus
python -c "
from openpilot.cereal.messaging import SubMaster
sm = SubMaster(['carState', 'modelV2', 'controlsState'])
sm.update(1000)
print(sm.updated_alive)
"

# Check logs
ls -la /tmp/openpilot/log/
tail -f /tmp/openpilot/log/manager.log

# Check shared memory
ls -la /dev/shm/

# Check params
python -c "
from openpilot.common.params import Params
p = Params()
print('Mads:', p.get('Mads'))
print('CarParams:', bool(p.get('CarParams')))
"

# Camera preview test (standalone)
USE_WEBCAM=1 ROAD_CAM=0 python -c "
from tools.webcam.camerad import Camerad
import time
c = Camerad()
c.start()
time.sleep(5)
c.stop()
print('Camera preview OK')
"
```

---

# SECTION 26 — V4L2 & CAMERA CONFIGURATION GUIDE

## 26.1 Orange Pi 5 V4L2 Device Mapping

Typical device mapping on Orange Pi 5 with IMX415:

```
Device              Path              Purpose
─────────────────────────────────────────────────
RKISP main raw      /dev/video0       Main ISP input (IMX415 road)
RKISP self path     /dev/video1       ISP processed output
RKISP dummy         /dev/video11      ISP config interface
RGA                 /dev/video31      Hardware resize/crop
MIPI CSI2           /dev/video4       Raw CSI before ISP
```

The exact mapping depends on kernel configuration and device tree. Always discover dynamically:

```bash
# Discover all video devices and their capabilities:
for dev in /dev/video*; do
  echo "=== $dev ==="
  v4l2-ctl -d $dev --all 2>/dev/null | head -5
done
```

## 26.2 Camera Device Rules

```
ROAD_CAM env var    → /dev/videoX for road camera (default: "0")
DRIVER_CAM env var  → /dev/videoX for driver camera (default: "2")
WIDE_CAM env var    → /dev/videoX for wide camera (optional)

Device numbers MUST come from env vars, NOT hardcoded.
See Section 4.4 for env var reference.
```

## 26.3 Testing V4L2 Capture

```bash
# Test raw capture from RKISP
v4l2-ctl -d /dev/video0 --set-fmt-video=width=1280,height=720,pixelformat=NV12
v4l2-ctl -d /dev/video0 --stream-mmap --stream-to=test.raw --stream-count=30
# This captures 30 NV12 frames to test.raw

# Check format support
v4l2-ctl -d /dev/video0 --list-formats-ext

# Check current format
v4l2-ctl -d /dev/video0 --get-fmt-video
```

## 26.4 IMX415 Specific Configuration

```python
# Camera geometry after commits 95af03c + 712bcb2b:
IMX415_CONFIG = {
    "sensor": "Sony IMX415",
    "resolution": "3840×2160 (native)",
    "runtime_resolution": "1280×720",
    "focal_length": 900,           # pixels (tuned for IMX415)
    "frame_rate": 20,              # FPS target
    "format": "MJPG",              # current webcam mode
    "nv12_size": 1280 * 720 * 3 // 2,  # 1,382,400 bytes
    "production_format": "NV12",   # target mode
    "production_path": "RKISP → V4L2 → NV12 DMA-BUF",
}
```

## 26.5 NV12 Layout Validation

Always validate NV12 layout — stride may not equal width:

```python
# In code, always detect dynamically:
def validate_nv12(width, height, stride, buf_size):
    expected_size = stride * height * 3 // 2
    if buf_size < expected_size:
        raise ValueError(f"NV12 buffer too small: {buf_size} < {expected_size}")
    if stride < width:
        raise ValueError(f"NV12 stride {stride} < width {width}")
    return True
```

## 26.6 Multi-Camera Setup

```python
# tools/webcam/camerad.py — current camera config
CAMERAS = [
    CameraType("roadCameraState", VISION_STREAM_ROAD, os.getenv("ROAD_CAM", "0")),
]
if not NO_DM:
    CAMERAS.append(CameraType("driverCameraState", VISION_STREAM_DRIVER, os.getenv("DRIVER_CAM", "2")))
if WIDE_CAM := os.getenv("WIDE_CAM"):
    CAMERAS.append(CameraType("wideRoadCameraState", VISION_STREAM_WIDE_ROAD, WIDE_CAM))
```

## 26.7 Production Camera Path (Target)

```
Current (dev):     /dev/videoX → cv2 MJPG → BGR→NV12 (CPU) → VisionIPC
Target (prod):     IMX415 → RKISP → V4L2 → NV12 DMA-BUF → VisionIPC (zero-copy)

Fix: Replace CameraMJPG with RKISP V4L2 capture using DMA-BUF export
     See Ai/ai/camera.md and Ai/examples/imx415_rkisp_example.md
```

---

# SECTION 27 — DOCUMENT ARCHITECTURE & MAINTENANCE

## 27.1 Ai/ Pack Document Relationships

The Ai/ documents form a layered knowledge system:

```
Layer 0 (Entry):       Ai/README.md              ← start here, reading order
Layer 1 (Omniscient):  Ai/GOD.md                 ← THIS DOCUMENT (everything at once)
Layer 2 (Analysis):    Ai/commit.md              ← what each commit does and why
Layer 3 (Domain):      Ai/ai/camera.md           ← camera subsystem deep spec
                       Ai/ai/visionipc.md        ← VisionIPC transport spec
                       Ai/ai/modeld.md           ← modeld pipeline spec
                       Ai/ai/rknn.md             ← RKNN integration spec
                       Ai/ai/validation.md       ← validation methodology
                       Ai/ai/performance.md      ← performance measurement
                       Ai/ai/deployment.md       ← deployment procedures
Layer 4 (Reference):   Ai/references/            ← hardware specs, architecture
                       └── rk3588.md             ← RK3588 SoC deep reference
                       └── imx415.md             ← IMX415 sensor deep reference
                       └── openpilot_architecture.md  ← generic OpenPilot arch
                       └── model_metadata.md     ← metadata-driven execution
                       └── visionipc.md          ← VisionIPC deep reference
Layer 5 (Assets):      Ai/examples/              ← concrete code examples
                       Ai/templates/             ← reusable report templates
                       Ai/checklists/            ← validation checklists
                       Ai/diagrams/              ← pipeline flow diagrams
```

## 27.2 When to Update GOD.md

GOD.md must be updated when:

```
1. New commits change subsystem behavior
   → Update Section 1 (key commits list + HEAD)
   → Update Section 15 (drift from documentation)
   → Add entry to Section 22 (commit analysis)

2. New env vars are added
   → Update Section 12 (env vars reference)

3. New processes or messages are added
   → Update Section 3 (process table)
   → Update Section 9 (message architecture)

4. Forbidden rules are identified
   → Update Section 14.3 (FORBIDDEN list)

5. Check-in checklist is completed
   → Mark items in Section 20
```

## 27.3 How to Record Drift

When code behavior diverges from documented behavior:

```
1. Add entry to Section 15 (Known Drift) with:
   - What the document says
   - What the code actually does
   - File and line reference
   - Impact assessment

2. Do NOT change the original document claim
   - The original architecture goal should remain visible
   - Drift records show the gap between goal and reality

3. After fixing the code to match the document:
   - Remove or mark the drift entry as RESOLVED
   - Add date of resolution
```

## 27.4 Frequency of Validation

```
Per commit:     Run relevant checklists from Section 20
Per deployment: Run full production checklist (Section 20.4)
Weekly:         Verify Section 15 (drift) is still accurate
Per release:    Full document review, update version
```

## 27.5 GOD.md Ownership

```
Author:         Generated 2026-06-10
Maintainer:     AI agents modifying the repository
Validation:     Cross-reference against actual code behavior
Authority:     This document is authoritative over AI code generation
               Code is authoritative over this document for drift detection
```

---

# SECTION 28 — CAN / PANDA HARDWARE SETUP

## 28.1 Panda on Orange Pi 5

The panda provides CAN interface between OpenPilot and the vehicle:

```bash
# Check panda detection
lsusb | grep Panda

# panda should appear as USB device
# If not, check USB cable and panda firmware

# Test panda communication
python -c "
from openpilot.selfdrive.pandad.pandad import Panda
panda = Panda()
print(f'Panda type: {panda.get_type()}')
print(f'Panda firmware: {panda.get_version()}')
"
```

## 28.2 CAN Bus Setup

```bash
# Panda creates virtual CAN interfaces:
# panda0 → CAN bus 0 (usually powertrain)
# panda1 → CAN bus 1 (usually auxiliary)
# panda2 → CAN bus 2 (usually camera/radar)

# Test CAN traffic:
candump panda0
```

## 28.3 CAN Debugging

```bash
# Monitor CAN messages
python -c "
from openpilot.selfdrive.car.card import CarInterface
print('CarInterface available')
"

# Check carState (requires active panda + car)
python -c "
from openpilot.cereal.messaging import SubMaster
import time
sm = SubMaster(['carState'])
for _ in range(100):
    sm.update(10)
    if sm.updated['carState']:
        print('CAN messages received')
        break
    time.sleep(0.1)
"
```

## 28.4 Hardware Requirements Summary

```
Minimum:
  Orange Pi 5 (any variant)
  IMX415 camera module (or USB webcam for dev)
  Power supply (5V/4A+ recommended)
  MicroSD or NVMe boot drive

For Vehicle Operation:
  Panda (any version: Panda, Panda Blue, Panda FDCAN)
  OBD-II cable (for CAN connection)
  GPS module (optional, not required for basic operation)

For Development:
  USB keyboard/mouse
  HDMI display (supports 800×400 or higher)
  Ethernet or WiFi for SSH
```

---

# SECTION 29 — MAKING CHANGES REFERENCE

## 29.1 Decision Tree: "I Want to Change the Camera"

```
I want to change the camera
│
├─ Add new camera type?
│   → Read Ai/ai/camera.md, Ai/ai/visionipc.md
│   → Add CameraType in tools/webcam/camerad.py
│   → Add env var gate in process_config.py
│   → CHECK: Section 14.3 FORBIDDEN list
│   → RUN: Section 20.1 Camera Change Checklist
│
├─ Change camera resolution?
│   → Update CameraMJPG target in tools/webcam/camera.py
│   → Update DEVICE_CAMERAS in common/transformations/camera.py
│   → Validate NV12 layout
│   → CHECK: Timestamps, frame rate still stable
│
├─ Switch to RKISP production path?
│   → Read Ai/examples/imx415_rkisp_example.md
│   → Implement V4L2 capture with DMA-BUF
│   → Run DMA-BUF validation
│   → Target: Section 13.3 performance targets
│
└─ Change focal length?
    → Update DEVICE_CAMERAS in common/transformations/camera.py
    → Validate warp generation, overlay accuracy
    → Cross-reference with planner output
```

## 29.2 Decision Tree: "I Want to Change the Model Backend"

```
I want to change model backend
│
├─ Switch from Tinygrad to RKNN?
│   → Read Ai/ai/rknn.md, Ai/examples/rknn_runner_example.md
│   → Implement RKNNRunner (Section 16.1)
│   → Vision Core 0, Policy Core 1 (Section 16.3)
│   → Validate metadata-driven (no hardcoded indices)
│   → Run 100+ frame correlation test
│   → CHECK: Section 14.3 FORBIDDEN list
│   → RUN: Section 20.2 Modeld/RKNN Change Checklist
│
├─ Switch from ONNX to Tinygrad?
│   → Set OPENPILOT_MODELD_BACKEND=tinygrad
│   → Verify models compiled (scons)
│   → Test on TICI hardware
│
└─ Add new model type?
    → Add new Runner class to model_runner.py
    → Add metadata for new model
    → Keep Tinygrad fallback
    → Never modify planner semantics
```

## 29.3 Decision Tree: "I Want to Add a New Feature"

```
I want to add a feature
│
├─ Feature gated behind env var or param?
│   → YES: Add env var to Section 12
│   → YES: Add param to common/params_keys.h
│   → Default behavior preserved when gate is off
│
├─ Does feature modify planner, controls, or messages?
│   → Read Section 14.3 FORBIDDEN list
│   → Get explicit validation before proceeding
│
├─ New cereal message needed?
│   → Add to cereal/custom.capnp ONLY
│   → Never modify cereal/log.capnp base messages
│
├─ New process needed?
│   → Add to system/manager/process_config.py
│   → Follow env var gating pattern (WEBCAM, NO_DM)
│
├─ Fallback when feature fails?
│   → Always have fallback to previous behavior
│   → Fail-fast, never silently publish invalid data
│
└─ Run: Section 20.3 New Feature Checklist
```

## 29.4 Checklist: Before Asking an AI Agent to Write Code

```
□ Read GOD.md first (this document)
□ Identify subsystem being modified
□ Read relevant domain doc in Ai/ai/
□ Check Section 14.3 FORBIDDEN list
□ Confirm validation plan exists
□ Include env var or param gate
□ Preserve default behavior
□ Preserve Tinygrad fallback (for model changes)
□ Include fallback on failure
□ In prompt: "Follow GOD.md Sections X, Y, Z"
```

---

# SECTION 30 — REFERENCE: EnhancedOpenPilot RK3588 HARDWARE MODULES

This section documents findings from the `enhancedopenpilot/common/hardware/rk3588/` module collection
(located at `/home/d/enhancedopenpilot/common/hardware/rk3588/`). These modules provide complete
RK3588 hardware acceleration and can be adapted into this repository.

## 30.1 Module Overview

```
enhancedopenpilot/common/hardware/rk3588/
├── __init__.py              ← Re-exports key classes
├── npu.py                   ← RKNNRuntime (minimal RKNN wrapper)
├── hardware.py              ← RK3588Hardware (HardwareBase subclass)
├── camera/
│   ├── __init__.py          ← Camera HAL exports
│   ├── v4l2.py              ← V4L2 with DMA-BUF zero-copy support
│   ├── csi.py               ← CSICamera, IMX415Camera, OX03C10Camera
│   ├── usb.py               ← USBCamera, UVCCamera
│   ├── exposure.py          ← ExposureController, AutoExposure
│   └── sensors/
│       ├── __init__.py
│       ├── imx415.py        ← IMX415 sensor driver (register-level)
│       └── ox03c10.py       ← OX03C10 sensor driver
├── rga.py                   ← RGA hardware accelerator (librga.so via ctypes)
├── visionbuf_dma.cc         ← C++ DMA-BUF buffer management
├── mpp.py                   ← MPP (Media Process Platform) integration
├── inference_allocation.py  ← NPU core allocation strategy
├── performance_policy.py    ← Performance optimization policy
├── config.py                ← Configuration management
├── core.py                  ← Core infrastructure
├── gpio.py                  ← GPIO control
├── gps.py                   ← GPS integration
├── accel.py                 ← Accelerometer
├── watchdog.py              ← Watchdog timer
├── storage.py               ← Storage management
├── SConscript               ← Build integration
└── hardware.h               ← Hardware constants
```

## 30.2 Gap Analysis — What Each Module Solves

| Module | Gap in Our Project | Impact |
|---|---|---|
| `npu.py` — RKNNRuntime | **#1 gap**: 0% RKNN inference (model runs on CPU at ~300ms) | Enables NPU inference at 8-12ms per frame |
| `camera/v4l2.py` — V4L2+DMA-BUF | **#2 gap**: Current pipeline uses OpenCV MJPG→CPU (forbidden production path) | Enables zero-copy RKISP→V4L2→DMA-BUF→VisionIPC |
| `camera/csi.py` + `sensors/imx415.py` | **#3 gap**: No proper IMX415 sensor initialization | Register-level init, MIPI config, low-light mode |
| `rga.py` — RGA acceleration | Optimization: CPU does resize/convert | Hardware-accelerated resize/format conversion |
| `hardware.py` — RK3588Hardware | `PC=False, TICI=False` leaves no proper HW platform | Full RK3588 platform: CPU gov, NPU freq, thermal, CAN, fan |
| `visionbuf_dma.cc` — DMA-BUF buffers | Needed by zero-copy camera path | C++ DMA-BUF buffer management |

## 30.3 Key Classes — Quick Reference

### RKNNRuntime (npu.py)

```python
from rknnlite.api import RKNNLite

# Core mask: "0"=1, "1"=2, "2"=4, "0,1"=3, "0,1,2"=7, "all"=7
class RKNNRuntime:
    def __init__(self, model_path: str, cores: Optional[str] = "all"):
        # Loads .rknn model, inits runtime with core mask

    def infer(self, inputs: np.ndarray | list[np.ndarray]) -> list[np.ndarray]:
        # Run NPU inference

    def release(self) -> None:
        # Release RKNN resources

    # Supports context manager: with RKNNRuntime(path) as r: ...
```

### V4L2Camera (camera/v4l2.py)

```python
class V4L2Camera:
    # Supports both MMAP and DMA-BUF memory types
    # Auto-detects Single Plane vs MPLANE
    # Full capture lifecycle: open → set_format → request_buffers → setup → start → capture → stop → close

    def capture_frame(self, timeout_ms=1000) -> Optional[V4L2Buffer]:
        # Returns buffer with dmabuf_fd or mmap data

    def get_frame_data(self, buf) -> Optional[np.ndarray]:
        # Get frame data as numpy array

    def capture_loop(self) -> Generator[V4L2Buffer]:
        # Generator for continuous capture
```

### IMX415Camera (camera/csi.py)

```python
class IMX415Camera(CSICamera):
    # Extends CSICamera → V4L2Camera
    # Default: 1280x720, NV12, 20fps, 4-lane MIPI, 1.2GHz (changed from 1920x1080)
    # full_initialize(): sensor init → MIPI setup → RK3588 optimizations → V4L2 format
```

### RK3588Hardware (hardware.py)

```python
class RK3588Hardware(HardwareBase):
    # Extends HardwareBase — drop-in platform for system/hardware/
    # Detects variant: LubanCat-4, RK3588S-Generic, RK3588-Generic, etc.
    # initialize_hardware(): CPU gov, memory, power, device-specific optimizations
    # Thermal: soc-thermal, gpu-thermal, rk806-thermal, npu-thermal auto-detection
    # CAN: configures can0, can1 at specified bitrate
    # Fan: PWM control via sysfs
    # Touchscreen: Goodix GT911 auto-discovery
    # Camera config: multi-camera with env-var overrides
```

### RGA (rga.py)

```python
class RGA:
    # Hardware accelerator — loads librga.so via ctypes
    # Zero-copy resize/convert via DMA-BUF file descriptors

    def resize(src_fd, src_w, src_h, dst_fd, dst_w, dst_h, fmt='nv12') -> bool:
        # Hardware resize (same format)

    def convert(src_fd, src_w, src_h, src_fmt, dst_fd, dst_fmt) -> bool:
        # Hardware format conversion
```

## 30.4 Integration Plan into This Repository

### Phase 1 — RKNN Inference (HIGHEST priority)

```
Files to add:     common/hardware/rk3588/npu.py
Modules to modify: sunnypilot/modeld_v2/model_runner.py
                   sunnypilot/modeld_v2/modeld.py

Steps:
  1. Copy npu.py → common/hardware/rk3588/npu.py
  2. Add RKNNRunner class in model_runner.py (see GOD.md §16)
  3. Wire into modeld.py: if backend=="rknn": runner = RKNNRunner(...)
  4. Convert .onnx → .rknn using RKNN Toolkit 2
  5. Validate: 100+ frames, correlation > 0.995 vs Tinygrad

Import convention:
  from openpilot.common.hardware.rk3588.npu import RKNNRuntime
```

### Phase 2 — DMA-BUF Camera (HIGH priority)

```
Files to add:     common/hardware/rk3588/camera/v4l2.py
                   common/hardware/rk3588/camera/csi.py
                   common/hardware/rk3588/camera/sensors/imx415.py
                   common/hardware/rk3588/visionbuf_dma.cc
Modules to modify: tools/webcam/camerad.py
                   tools/webcam/camera.py

Steps:
  1. Add V4L2 camera HAL (v4l2.py, csi.py, imx415.py)
  2. Create RKISPCamera class that uses V4L2 → DMA-BUF path
  3. Wire into camerad.py replacing CameraMJPG
  4. Export DMA-BUF fds through VisionIPC
  5. Validate: NV12 layout, timestamps, 20fps stable
```

### Phase 3 — RGA + Hardware Platform (MEDIUM priority)

```
Files to add:     common/hardware/rk3588/rga.py
                   common/hardware/rk3588/hardware.py
Modules to modify: system/hardware/hw.py (optionally)
                   system/manager/process_config.py (optionally)

Steps:
  1. Add RGA for camera resize/convert offload
  2. Wire RK3588Hardware as platform when detected
  3. Configure thermal, CAN, fan, touchscreen
```

## 30.5 Import Path Convention for These Modules

```python
# All modules use openpilot prefix:
from openpilot.common.hardware.rk3588.npu import RKNNRuntime
from openpilot.common.hardware.rk3588.camera.v4l2 import V4L2Camera, V4L2Config
from openpilot.common.hardware.rk3588.camera.csi import IMX415Camera
from openpilot.common.hardware.rk3588.rga import RGA
from openpilot.common.hardware.rk3588.hardware import RK3588Hardware
```

## 30.6 Key Differences From EnhancedOpenPilot

```
Our repo:           sunnypilot-pc (fork of sunnypilot, which forks commaai/openpilot)
Their repo:         enhancedopenpilot (separate fork with RK3588 HW layer built in)

Their approach:     Added common/hardware/rk3588/ as a first-class hardware platform
Our approach:       PC=False, TICI=False → processes enabled/disabled via env vars

To adopt their approach, we would:
  1. Add common/hardware/rk3588/ with the modules above
  2. Register RK3588Hardware as a platform in system/hardware/
  3. Use hardware detection to select camera backend automatically
  4. Keep existing env-var gates for backward compatibility
```

## 30.7 Location of Source Files

```
Original: /home/d/enhancedopenpilot/common/hardware/rk3588/
Target:   common/hardware/rk3588/  (relative to repo root)
```

---

# SECTION 31 — RKNN MODEL CONVERSION (ONNX → RKNN)

This section documents the actual RKNN conversion process and bugs found when converting
`driving_vision.onnx` and `driving_policy.onnx` for RK3588 NPU. Source: `docs/rk3588_npu_rknn_plan.md`.

## 31.1 Conversion Flow

```
ONNX model (.onnx)
  │
  ├─ Step 1: Fix ONNX opset (must be ≤19 for RKNN Toolkit 2.3.2)
  ├─ Step 2: Rewrite Gelu(approximate="tanh") → Mul/Add/Tanh primitives
  ├─ Step 3: (Vision only) Change UINT8 inputs → FLOAT16, remove Cast nodes
  ├─ Step 4: (Vision only) ReduceL2 prescale to avoid FP16 overflow
  ├─ Step 5: (Policy only) Rewrite GatherND negative index → Slice
  └─ Final: Build .rknn with RKNN Toolkit 2
```

## 31.2 Critical Bugs Found During Conversion

### Bug 1: Opset Version

RKNN Toolkit 2.3.2 accepts **opset ≤ 19** (not 14 as documented elsewhere).
If conversion fails with opset errors, try 19 first, then 14.

### Bug 2: Gelu(approximate="tanh") — Must Rewrite

The driving model uses `Gelu(approximate="tanh")` which has no direct RKNN mapping.
Must rewrite into primitive `Mul/Add/Tanh` operations before conversion.

### Bug 3: UINT8 Input — RKNN Rejects (Vision Only)

`driving_vision.onnx` uses UINT8 for `img` and `big_img` inputs.
RKNN build fails with `Not Support Dtype: 2` on UINT8.

Fix: Change graph inputs to **FLOAT16** (or FLOAT32), and remove the two direct
input `Cast` nodes from the graph.

### Bug 4: ReduceL2 FP16 Overflow (Vision Only)

The hidden state at the end of the vision model uses `ReduceL2` for L2 normalization.
The internal square-sum exceeds FP16 range (norm is ~440-463, square is ~193,600-214,369,
FP16 max is 65,504).

Fix: Prescale the input:
```
ReduceL2(x) → ReduceL2(x / 32) * 32
```
This keeps intermediate values within FP16 range.

With this fix: hidden_state MAE improves from broken to `0.002299`, corr `0.997651`.

### Bug 5: GatherND Negative Index (Policy Only)

The policy model uses `Transpose(features_buffer) → GatherND(indices=-9..-1) → Transpose`
to crop the feature tokens. RKNN mishandles negative-index `GatherND` — first index
already produces `inf`.

Fix: Rewrite to `Slice(features_buffer, axis=1, starts=16, ends=25)`.

With this fix: policy outputs go from 6/10 invalid → 0/10 invalid, corr `0.998845`.

### Bug 6: NHWC vs NCHW Data Layout

RKNNLite must use **NHWC** input with `data_format="nhwc"`:
- NCHW tensors must be transposed to NHWC before calling RKNN
- Without NHWC, hidden_state becomes all zeros
- Set `MODELD_VISION_RKNN_INPUT_LAYOUT=nhwc` and `MODELD_WARP_OUTPUT_LAYOUT=nhwc`

### Bug 7: FLOAT16 ONNXRuntime is NOT a Safe Reference

When comparing RKNN vs ONNX outputs, FLOAT16 ONNXRuntime CPU produces wrong results
for grouped convolutions (specifically `conv2d_11`: group=64, channels 64→128, kernel 7×7).
Always use FP32-promoted ONNX for reference comparisons.

## 31.3 Model Structure

### driving_vision.onnx

```
Inputs:  img (1, 12, 128, 256), big_img (1, 12, 128, 256)
Output:  outputs (1, 1576)
Slices:
  meta           0:55
  desire_pred    55:87
  pose           87:99
  wide_from_device_euler   99:105
  road_transform         105:117
  lane_lines             117:645
  road_edges             653:917
  lead                   917:1061
  hidden_state          1064:1576
```

### driving_policy.onnx

```
Inputs:  desire_pulse (1, 25, 8), traffic_convention (1, 2), features_buffer (1, 25, 512)
Output:  outputs (1, 1000)
Slices:
  plan           0:990
  desire_state   990:998
```

## 31.4 Achieved Performance

With vision RKNN + policy RKNN, no tinygrad fallback:

```
Raw NPU inference:      vision ~28ms + policy ~4.3ms = ~32ms combined
Live end-to-end:        ~45-50ms (includes preprocessing + tensor copies)
modelExecutionTime:     median ~0.051s
Publish rate:           ~5 FPS (20 FPS target without preprocessing bottleneck)
```

## 31.5 RKNN Validation Results

## 31.5 Current Model Status

The following files are present and validated in `selfdrive/modeld/models/`:

```
driving_vision.rknn             36 MB   INT8 quantized (valid RKNN)
driving_vision.rknn.fp16_backup 36 MB   FP16 fallback
driving_vision_metadata.pkl     407 B   Input shapes + output slices
driving_policy.rknn             8.2 MB  INT8 quantized (valid RKNN)
driving_policy.rknn.fp16_backup 8.2 MB  FP16 fallback
driving_policy_metadata.pkl     277 B   Input shapes + output slices
```

All `.rknn` files confirmed real NPU models (not Git LFS pointers).
Metadata verified against model structure. Unnecessary model files
(YOLO, pothole, license plate, depth, segmentation, etc.) removed.
Only driving vision + driving policy models remain.

After all fixes (NHWC, ReduceL2 prescale, GatherND rewrite, FP32 reference):

| Comparison | Correlation | MAE |
|---|---|---|
| Vision full output | 0.999984 | 0.071963 |
| Vision hidden_state | 0.997651 | 0.002299 |
| Policy output | 0.998845 | 0.291091 |

## 31.6 Environment Variables for RKNN

```bash
OPENPILOT_MODELD_BACKEND=rknn       # Enable RKNN path
MODELD_VISION_RKNN_INPUT_LAYOUT=nhwc  # NHWC layout for vision
MODELD_WARP_OUTPUT_LAYOUT=nhwc        # NHWC layout for warp
MODELD_POLICY_BACKEND=auto            # Auto-fallback to tinygrad on bad output
MODELD_VISION_RKNN_PATH=...           # Override vision .rknn path
MODELD_POLICY_RKNN_PATH=...           # Override policy .rknn path
DISABLE_JIT_ALIAS_COPY=1              # Required for OpenCL warp path
```

## 31.7 Policy Auto-Fallback

Set `MODELD_POLICY_BACKEND=auto`. This runs policy on NPU first, checks if output
is finite, and falls back to tinygrad if RKNN output contains non-finite values.
In testing: 77 outputs, 2 tinygrad fallbacks, 0 non-finite final outputs.

### 31.8 Unused References (harmless)

The RKNN wrapper files (`driving_vision_rknn.py`, `driving_policy_rknn.py`) contain
docstring references to `pp_liteseg_rknn.py` — this is just a coding pattern reference,
not an import. Road segmentation models are not used in this project.

The `_paths.py` helper in `tools/rknn/scripts/` has no shebang — this is normal for
non-executable module files. It's only used by the conversion scripts.

Both are harmless and do not affect functionality.

---

# SECTION 32 — ORANGE PI 5 SETUP & LIVE RUN

This section documents the complete workflow for setting up and running RKNN on
Orange Pi 5. Source: `docs/rk3588_orangepi5_fresh_setup_runbook.md`,
`docs/rk3588_orangepi5_porting_plan.md`.

## 32.1 7-Milestone Porting Roadmap

```
Milestone 0: Repository builds on Orange Pi 5
Milestone 1: PC-mode runtime with webcam (USB webcam, no TICI paths)
Milestone 2: RK3588 hardware abstraction layer (thermal, process gating)
Milestone 3: Camera strategy (USB webcam first, then native RKISP)
Milestone 4: Model acceleration (tinygrad CL, CPU/LLVM, then RKNN)
Milestone 5: RK MPP video encoding (hardware encoding for logging)
Milestone 6: Sensors and time (IMU/GNSS on RK3588)
Milestone 7: Vehicle integration (USB panda first)
```

## 32.2 Applied Patches (from cwal1220/openpilot_rk3588 port)

```
system/hardware/rk3588/hardware.py       → Rk3588(Pc) with thermal zones
system/hardware/__init__.py              → Devicetree detection for RK3588
system/manager/process_config.py         → Prevent Qualcomm camerad on RK3588
tools/webcam/camera.py                   → WEBCAM_WIDTH/HEIGHT/FPS/FLIP env vars
tools/webcam/camerad.py                  → Use WEBCAM_FPS consistently
selfdrive/modeld/SConscript              → OPENPILOT_TINYGRAD_DEV override
SConstruct                               → --minimal skips non-essential tools
```

## 32.3 Build and Run Commands

```bash
# On Orange Pi 5 with Armbian Ubuntu 24.04, Linux 6.1 vendor kernel

# Clone
GIT_LFS_SKIP_SMUDGE=1 git clone -b codex/rk3588-orangepi5-port \
  https://github.com/cwal1220/openpilot_rk3588.git openpilot
cd openpilot

# Submodules
git submodule update --init --recursive

# Python env (using uv)
uv sync --frozen --no-dev --extra tools --extra dev

# Install RKNN Lite runtime
uv pip install --python .venv/bin/python \
  /path/to/rknn_toolkit_lite2-2.3.2-cp312-cp312-manylinux_2_17_aarch64.whl

# Apply tinygrad RK3588 OpenCL patch
cd tinygrad_repo && git apply ../tools/rk3588/tinygrad_rk3588.patch && cd ..

# Build
env -u DEBUG scons -j2

# Run live webcam RKNN smoke test (70 second window)
export XAUTHORITY="$(ls /run/user/1000/.mutter-Xwaylandauth.* | tail -n 1)"
timeout 70s env -u DEBUG \
  PATH="$PWD/.venv/bin:$PATH" \
  DISPLAY=:0 XAUTHORITY="$XAUTHORITY" \
  XDG_RUNTIME_DIR=/run/user/1000 \
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus \
  BIG=1 SCALE=0.875 \
  NOBOARD=1 USE_WEBCAM=1 ROAD_CAM=0 \
  WEBCAM_WIDTH=1280 WEBCAM_HEIGHT=720 WEBCAM_FPS=20 WEBCAM_FOURCC=MJPG WEBCAM_FLIP=none \
  OPENPILOT_MODELD_BACKEND=rknn \
  MODELD_VISION_RKNN_INPUT_LAYOUT=nhwc \
  MODELD_WARP_OUTPUT_LAYOUT=nhwc \
  MODELD_POLICY_BACKEND=auto \
  DISABLE_JIT_ALIAS_COPY=1 \
  .venv/bin/python tools/rk3588/run_live_webcam_rknn.py
```

## 32.4 Success Criteria

Logs show:
```
started webcamerad
started ui
started soundd
started modeld
started calibrationd
started plannerd
loaded RKNN model driving_vision_rk3588.rknn
loaded RKNN model driving_policy_rk3588.rknn
```

Plus: UI window visible on HDMI with camera preview and path overlay.
Use `xdotool search --name UI` to find the window.

## 32.5 Known Benign Warnings

- `ALSA ... underrun occurred` — audio, non-critical
- `W Query dynamic range failed. Ret code: RKNN_ERR_MODEL_INVALID` — expected for static-shape RKNN
- `No LTE connection found` — no cellular on Orange Pi 5
- Occasional `skipping model eval. Dropped ... frames` — normal with USB webcam

## 32.6 OpenCL on Mali-G610 (Panfrost/Rusticl)

The Orange Pi 5 GPU is Mali-G610 with Panfrost driver and Rusticl OpenCL.

```
clinfo reports: Mali-G610 (Panfrost) + pocl CPU platform
Must force Rusticl: OCL_ICD_VENDORS=/etc/OpenCL/vendors/rusticl.icd
```

Known limitations:
- Requires `DISABLE_JIT_ALIAS_COPY=1` for OpenCL queue replay
- Vision model compiles and runs on CL
- **Policy model fails** on Panfrost with `InvalidBitWidth: Invalid bit width in input: 128`
- CPU/LLVM is the stable preprocessing fallback

---

# SECTION 33 — CAMERA PREPROCESSING: NV12 + INTRINSICS

This section documents critical preprocessing fixes discovered during RKNN porting.
Without these, the UI overlay will be wrong or missing even if the model runs correctly.
Source: `docs/rk3588_overlay_preprocess_analysis.md`.

## 33.1 Root Cause of Missing/Wrong Overlay

The RKNN model conversion was NOT the problem (vision corr 0.999984). The problem was
**how camera frames were fed into the model**. Two bugs:

1. NV12 buffer layout: Webcam sends tight NV12, modeld reads padded NV12
2. Camera intrinsics: Wrong focal length for webcam resolution

## 33.2 Bug 1: NV12 Tight vs Padded Layout

Webcam sends **tight NV12** (no padding):
```text
1280 × 720 × 1.5 = 1,382,400 bytes
```

But `get_nv12_info(1280, 720)` returns **padded layout** (Qualcomm VENUS style):
```text
stride=1280, y_height=736, uv_height=368, size=2,220,032 bytes
```

This shifted the UV plane offset, corrupting the model input image and causing
early crashes.

**Fix:** Add `get_modeld_nv12_info()` that uses tight NV12 when `USE_WEBCAM=1`.
Create a separate webcam warp pkl: `driving_warp_1280x720_webcam_tinygrad.pkl`.

## 33.3 Bug 2: Camera Intrinsics Mismatch

`DEVICE_CAMERAS[("pc", "unknown")]` defaults to TICI AR0231 settings:
```text
width=1928, height=1208, focal=2648
```

For 1280×720 webcam input, this produces an extreme warp (zoom 2.9×):
```text
[[2.9098902, 0, 219.06813],
 [0, 2.9098902, 465.48923],
 [0, 0, 1]]
```

**Fix:** Override with webcam intrinsics when `USE_WEBCAM=1`:
```text
WEBCAM_WIDTH=1280, WEBCAM_HEIGHT=720, WEBCAM_FOCAL=900.0
```

Resulting warp:
```text
[[1.0, 0.0, 384.0],
 [0.0, 1.0, 312.4],
 [0.0, 0.0, 1.0]]
```

## 33.4 Env Vars for Webcam Mode

```bash
WEBCAM_WIDTH=1280         # Webcam frame width
WEBCAM_HEIGHT=720          # Webcam frame height
WEBCAM_FPS=20              # Webcam target FPS
WEBCAM_FOURCC=MJPG         # MJPG required for stable 1280×720
WEBCAM_FLIP=none           # Rotation/flip
WEBCAM_FOCAL=900.0         # Focal length (tuned for IMX415, commit 712bcb2be)
```

## 33.5 IMX415Camera Defaults — CRITICAL

The `IMX415Camera` class in `common/hardware/rk3588/camera/csi.py` originally defaulted to
`1920×1080 @ 30fps`. This was **wrong** for this repo — it would break the warp matrix
and overlay (zoomed/clipped road view).

**Your repo is calibrated for `1280×720 @ 20fps, focal=900`:**

```
common/transformations/camera.py:  CameraConfig(1280, 720, 900.0)
selfdrive/ui/ui.h:                 FCAM_INTRINSIC_MATRIX with focal 900, 1280/2, 720/2
Commit 712bcb2be:                  "feat(camera): Change camera focal to imx415"
```

**Fix applied:** Changed `IMX415Camera` defaults to `1280×720 @ 20fps`.
No other file depends on these defaults.

## 33.6 Verification Tools

Two tools exist to debug preprocessing:

1. `dump_model_preprocess_video.py` — Dumps model input tensors from video file
   for visual inspection. Saves original resize, 6ch reconstruction images.
   
2. `run_live_webcam_rknn.py` — Controlled bring-up runner that starts camera,
   modeld, UI without full manager. Injects demo CarParams.

---

# SECTION 34 — ORANGE PI 5 PORTING ROADMAP REFERENCE

Complete 7-milestone plan from `docs/rk3588_orangepi5_porting_plan.md`.

## 34.1 Summary

This is a reference for the order in which RK3588 features should be ported.
The principle: **correctness first, acceleration second, hardware integration third**.

## 34.2 Milestone Descriptions

```
M0: Build Baseline
    - git submodules, Python env, scons --minimal
    - No runtime changes

M1: PC-Mode Runtime
    - USB webcam (USE_WEBCAM=1)
    - NOBOARD=1 for bench
    - No TICI paths, no sensord, no AGNOS
    - webcamerad publishes roadCameraState

M2: RK3588 Hardware Abstraction
    - system/hardware/rk3588/hardware.py (Rk3588 extends Pc)
    - Thermal zone mapping (soc-thermal, gpu-thermal, npu-thermal)
    - Process gating for RK3588-specific behavior

M3: Camera Strategy
    - Phase A: USB webcam stabilization (env vars for WxH/FPS/fourcc)
    - Phase B: Native RK camera (V4L2 or libcamera investigation)

M4: Model Acceleration
    - Path 1: tinygrad OpenCL (Mali-G610 / Rusticl)
    - Path 2: CPU/LLVM fallback (correctness baseline)
    - Path 3: RKNN NPU (this project's ultimate target)

M5: Video Encoding (RK MPP)
    - Replace ffmpeg software encoding with RK hardware encoder

M6: Sensors (IMU/GNSS)
    - External IMU or Linux IIO
    - USB GNSS or UART GNSS

M7: Vehicle Integration
    - USB panda first
    - Safety hooks unchanged
```

## 34.3 Key Design Decision: Rk3588(Pc)

The port uses `Rk3588(Pc)` — a subclass of the PC hardware class, NOT a new platform:
- Keeps `PC=True` for model compatibility (no new DeviceType)
- Adds RK3588 identity via devicetree detection
- Maps Orange Pi 5 thermal zones
- No TICI paths, no AGNOS, no Qualcomm assumptions

This avoids breaking `DEVICE_CAMERAS`, `modeld`, and other code that indexes by device type.

---

# FINAL DECLARATION

This document is authoritative.

Any AI agent modifying code in this repository must consult this document first.

Architecture first. Code second.

Validate everything. Assume nothing. Discover dynamically.

Never modify planner, controls, or message semantics without explicit validation.

The system is:
```
Orange Pi 5
↓
IMX415 Camera (or webcam for development)
↓
Linux V4L2
↓
Sunnypilot / OpenPilot
↓
Working ADAS on RK3588
```

That is the mission. Every line of code serves that mission.

---

# SECTION 35 — IMX415 CAMERA HARDWARE INSTALLATION (Orange Pi 5)

This section covers the kernel-level IMX415 camera installation on Orange Pi 5.
Hardware files are in `tools/imx415/`. The auto-install script handles everything.

## 35.1 What You Need

- Orange Pi 5 board
- Sony IMX415 camera module
- Ubuntu 24.04 (Joshua-Riek image): https://github.com/Joshua-Riek/ubuntu-rockchip
- Connect IMX415 to **CAM1** connector

## 35.2 Auto-Install (1 Command)

```bash
# Copy tools/imx415/ folder to your Orange Pi 5, then:
bash tools/imx415/install_imx415.sh
```

This single script does everything:
```
Step 1: Backup original DTB          → rk3588s-orangepi-5.dtb.bak
Step 2: Install new DTB              → rk3588s-orangepi-5.dtb (with IMX415 support)
Step 3: Install overlay DTB files    → orangepi-5-imx415-c*.dtbo
Step 4: Configure u-boot             → /etc/default/u-boot (auto, no duplicates)
Step 5: Update u-boot                → u-boot-update
Step 6: Reboot                       → IMX415 detected on next boot
```

## 35.3 Verification

After reboot, check the camera is detected:

```bash
sudo dmesg | grep imx415
```

Expected output (key lines):
```
imx415 7-001a: detect imx415 lane 4       ← MIPI lanes OK
imx415 7-001a: Detected imx415 id 0000e0  ← Sensor chip ID verified
rockchip-csi2-dphy csi2-dphy0: dphy0 matches m00_b_imx415  ← CSI PHY connected
imx415 7-001a: set fmt: cur_mode: 3864x2192, hdr: 0, bpp: 10  ← Sensor configured
```

## 35.4 Testing the Camera

```bash
# GStreamer preview (NV12, 1920x1080@60fps)
gst-launch-1.0 v4l2src device=/dev/video11 \
  ! video/x-raw,format=NV12,width=1920,height=1080,framerate=60/1 \
  ! xvimagesink

# OpenCV Python demo
cd tools/imx415 && python3 demo.py
```

## 35.5 Device Mapping

```
/dev/video0    → RKISP main (IMX415 road camera)
/dev/video11   → RKISP dummy/self path (used for preview)
/dev/video31   → RGA (hardware accelerator)
```

## 35.6 Manual Installation (if not using auto-install)

```bash
# 1. Backup
cd /usr/lib/firmware/6.1.0-1025-rockchip/device-tree/rockchip/
sudo cp rk3588s-orangepi-5.dtb rk3588s-orangepi-5.dtb.bak

# 2. Replace DTB
sudo cp ~/imx415/dts/rk3588s-orangepi-5.dtb ./
sudo cp ~/imx415/dts/orangepi-5-imx415-c* ./overlay/

# 3. Configure u-boot
sudo vi /etc/default/u-boot
# Add:
# U_BOOT_FDT="device-tree/rockchip/rk3588s-orangepi-5.dtb"
# U_BOOT_FDT_OVERLAYS="device-tree/rockchip/overlay/orangepi-5-ap6275p.dtbo device-tree/rockchip/overlay/orangepi-5-imx415-c1.dtbo"

# 4. Update and reboot
sudo u-boot-update
sudo reboot
```

## 35.7 Files Structure

```
tools/imx415/
├── install_imx415.sh              ← Auto-install script (run this)
├── readme.md                      ← Full documentation
├── demo.py                        ← OpenCV camera test
├── dts/                           ← Compiled DTB files
│   ├── rk3588s-orangepi-5.dtb
│   └── orangepi-5-imx415-c*.dtbo
├── dts-original/                  ← DTS source (for custom boards)
│   ├── dts.diff
│   └── rockchip/...
└── pic/                           ← Reference images
```

## 35.8 Other RK3588 Boards

For non-Orange Pi 5 boards, modify the DTS source files in `dts-original/` to match
your board's device tree, then compile with:
```bash
dtc -I dts -O dtb -o output.dtbo input.dts
```

---

Document Version: 2.3
Repository: MM-X/sunnypilot-pc
Branch: master-rk3588
Generated: 2026-06-10

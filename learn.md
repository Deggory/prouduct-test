### 🟦 How to Ask the AI for Automation or Porting

You can ask the AI to perform any porting, validation, or automation task by simply describing what you want in plain language. The AI will follow the interactive protocol in this file, guiding you step by step and waiting for your confirmation at each stage.

**Example prompts:**
- "Port this OpenPilot repo to Orange Pi 5 using the learn.md protocol."
- "Validate that my repo only uses the IMX415 front camera and the correct RKNN models."
- "Automate the model cleanup and checklist validation for a new SunnyPilot fork."
- "Check if all required scripts and folders are present for Orange Pi 5."
- "Run the full porting checklist and stop after each step for my review."

**How it works:**
1. The AI will explain the next step and what will change.
2. It will check for required files/folders and help you create them if missing.
3. It will make the change or guide you through it.
4. It will summarize what was done and ask for your confirmation before proceeding.
5. You can ask questions, request more detail, or say "continue" to move to the next step.

**Tip:**
You don’t need to use special commands—just describe your goal or problem, and the AI will handle the rest interactively.
## 🟦 How to Use This Automation System in Your Project

1. **Copy .claude/ and .vscode/**
	- Copy the `.claude/` folder (AI agent rules, checklists, scripts) and `.vscode/` folder (workspace/editor settings) from this repo to the root of your new project.
	- This enables robust AI-driven automation and a consistent development environment.

2. **Copy and Adapt learn.md**
	- Copy this `learn.md` file to your new repo.
	- Update only the car interface, model paths, and any hardware-specific details as needed for your project.

3. **Follow the Interactive Protocol**
	- Use the step-by-step protocol in `learn.md` to port or validate your repo.
	- At each step, the AI (or you) will:
	  - Explain what will change
	  - Check for required files/folders
	  - Make the change
	  - Summarize what was done
	  - Wait for confirmation before proceeding

4. **Let AI Agents Automate Tasks**
	- With `.claude/` present, AI agents (like Copilot or Claude) will follow the rules and checklists for code analysis, file analysis, test running, and parallel work.
	- You can ask the AI to perform porting, validation, or automation tasks, and it will use the protocol and agent rules to guide the process.

5. **Customize as Needed**
	- If your project has unique requirements, you can edit the `.claude/agents/` files or add new checklists/rules.
	- Update `learn.md` to reflect any project-specific steps or hardware.

**Result:**
- You get a fully automated, interactive, and error-resistant porting/validation workflow for any OpenPilot/SunnyPilot-based repo, tailored for Orange Pi 5 or your custom hardware.
## 🟨 Orange Pi 5 Porting: system/ Folder Essentials

The `system/` folder provides the core platform abstraction, process management, and hardware integration for EnhancedOpenPilot. For Orange Pi 5, these are the critical components and patterns you must understand or adapt:

### 1. Hardware Abstraction Layer (HAL)
- **system/hardware/**: Defines the hardware abstraction for all platforms. For Orange Pi 5, this is extended by `common/hardware/rk3588/`.
	- `system/hardware/__init__.py`: Detects RK3588 and instantiates the correct hardware object (`RK3588Hardware`).
	- `system/hardware/base.py`: Base classes for hardware, thermal, and power management.
	- `system/hardware/hardwared.py`: Main hardware daemon. Monitors thermal, power, and device health, and exposes status to the rest of the stack.
	- `system/hardware/power_monitoring.py`: Handles battery, voltage, and auto-shutdown logic. Orange Pi 5 uses EOPDeviceAutoShutdownIn param for safe shutdown.
	- `system/hardware/capabilities.py`: Detects available accelerators (AX-M1, Hailo-8, etc.), enables/disables features accordingly.
	- `system/hardware/storage.py`: Detects and manages external storage (SD card, USB, etc.) for logging and route recording.
	- `system/hardware/hw.py`: Platform paths for logs, persistent storage, and SD card support. Uses RK3588-specific storage manager if available.

### 2. Manager and Process Registry
- **system/manager/**: Orchestrates all daemons and manages their lifecycle.
	- `manager.py`: Main entrypoint. Boots all processes, sets params, and ensures required folders exist (e.g., for msgq IPC).
	- `process_config.py`: The master process registry. Controls which daemons are started, their enable/disable toggles, and platform-specific logic (e.g., only start `camerad` if RK3588 detected and enabled).
	- `process.py`: Launches Python and native daemons, sets process titles, and manages watchdogs.
	- `helpers.py`: Utility functions for bootlog, param management, and stdout handling.
	- `build.py`: SCons build orchestration for all platforms.

### 3. Camera Daemon and Platform Integration
- **system/camerad/**: Platform-agnostic camera daemon. For Orange Pi 5, all camera specifics are handled by `common/hardware/rk3588/camera/` and the RGA/NPU pipeline.
	- `main.cc`: Entry point for the C++ camera daemon. Exits on PC, sets real-time priority and core affinity (big core 6), then launches camera threads.
	- `snapshot.py`: Utility for capturing and converting camera frames (YUV to RGB) for debugging and validation.

### 4. Device Identity and Registration
- **system/device.py**: Ensures a stable device identifier (dongle ID) is stored in params. For Orange Pi 5, uses `rk3588-<serial>` as the unique ID.

### 5. Platform-Specific Hardware (common/hardware/rk3588/)
- All RK3588-specific logic (NPU, RGA, GPIO, core pools, camera, etc.) is implemented in `common/hardware/rk3588/`.
	- `hardware.py`: Main hardware class, exposes device variant, CAN, camera, and sensor configuration.
	- `core.py`: CPU core detection and affinity management (big/little clusters, Lubancat pattern).
	- `npu.py`: Minimal RKNN runtime for NPU inference (load/init/infer/release, core mask mapping).
	- `rga.py`: Zero-copy image processing using hardware RGA (resize, format conversion, DMA-BUF support).

### 6. Validation and Bring-Up Patterns
- Use the process registry (`process_config.py`) to verify which daemons are enabled for Orange Pi 5 (e.g., `camerad`, `modeld`, `stereod`, etc.).
- Validate hardware health and thermal status via `hardwared` and `power_monitoring.py`.
- Use camera and NPU test scripts in `common/hardware/rk3588/` to validate bring-up before running the full stack.

---

### Orange Pi 5 Porting Checklist: system/

- [ ] RK3588 hardware detection and instantiation (`system/hardware/__init__.py`)
- [ ] Hardware daemon (`hardwared`) running and reporting thermal/power status
- [ ] Camera daemon (`camerad`) enabled and using RK3588 camera pipeline
- [ ] NPU and RGA modules present and validated (`common/hardware/rk3588/`)
- [ ] Process registry (`process_config.py`) enables all required daemons for your config
- [ ] Device ID and params set correctly (`system/device.py`)
- [ ] Power monitoring and auto-shutdown logic validated
- [ ] External storage detection and logging tested

---

**Tip:** For new platforms, only `system/hardware/`, `system/manager/`, and `system/camerad/` need to be adapted. All RK3588 specifics should live in `common/hardware/rk3588/` for maximum portability.

# 🧠 EnhancedOpenPilot Orange Pi 5 Porting & Validation Guide

This is your **complete, actionable knowledge base** for porting or validating any OpenPilot-based repo to the Orange Pi 5 (RK3588). It includes code snippets, config examples, and automation patterns for every critical step.



## 🟦 Panda CAN Integration (Orange Pi 5)

**Panda** (comma.ai's original CAN interface) is the required CAN hardware for Orange Pi 5. All CAN communication between OpenPilot and your car is routed through Panda using the pandad process. This replaces all other safety modules and CAN bridges.


### Minimal Daemon/Process List (Orange Pi 5 + Panda)

- `camerad` (IMX415 front camera only)
- `modeld` (driving_vision.rknn, driving_policy.rknn only)
- `controlsd` (main control loop)
- `plannerd` (path/long planner)
- `radard` (lead/radar logic)
- `card` (car interface, CAN parsing/actuation)
- `pandad` (CAN bridge for Panda)


**Do not run:**
- Any ELM327, side radar, or unused car integrations
- Any driver monitoring, Bluetooth, voice, or extra sensors
- Any camera except IMX415 front
- Any model except driving_vision.rknn and driving_policy.rknn


### Panda CAN Integration Steps

1. **Enable `pandad` and `card` daemons:**
	 - `selfdrive/pandad/pandad.py` — CAN bridge daemon. Proxies CAN messages between Orange Pi 5 and Panda via USB.
	 - `selfdrive/car/card.py` — Main car interface. Handles CAN parsing, actuator commands, and communication with Panda.
	 - Only keep your car’s interface and CAN parser in `selfdrive/car/`.

2. **Remove all ELM327, side radar, and unused car integrations.**

3. **Ensure only IMX415 front camera is enabled in `camerad`.**

4. **All safety logic is handled by Panda firmware and OpenPilot safety hooks.**

5. **Messaging:**
	 - Keep all Cap'n Proto messaging (`cereal/`), and `msgq` for IPC.

6. **Process Registry Example:**
	 ```python
	 procs = [
		 PythonProcess("camerad", "selfdrive.camerad.camerad", always_run),
		 PythonProcess("modeld", "selfdrive.modeld.modeld", always_run),
		 PythonProcess("controlsd", "selfdrive.controls.controlsd", always_run),
		 PythonProcess("plannerd", "selfdrive.controls.plannerd", always_run),
		 PythonProcess("radard", "selfdrive.controls.radard", always_run),
		 PythonProcess("card", "selfdrive.car.card", always_run),
		 PythonProcess("pandad", "selfdrive.pandad.pandad", always_run),
	 ]
	 ```

---


### Orange Pi 5 Porting Checklist: Panda CAN

- [ ] `pandad` enabled for CAN bridge to Panda
- [ ] Only your car’s interface and CAN parser present in `selfdrive/car/`
- [ ] All ELM327, side radar, and unused car integrations removed
- [ ] Only IMX415 front camera enabled in `camerad`
- [ ] Only `driving_vision.rknn` and `driving_policy.rknn` models present
- [ ] All safety logic handled by Panda and OpenPilot safety hooks

## 🚗 What is EnhancedOpenPilot?
EnhancedOpenPilot is a fork of OpenPilot, re-architected for the Orange Pi 5 (RK3588) and the BrownPanda Chinese EV framework. It replaces comma.ai hardware with:
- RK3588 (CPU/NPU/RGA)
- Unified Camera HAL
- PCIe accelerator support (optional)
- BrownPanda safety module

---

## 💡 Step 1: Hardware Detection & Factory (Automatable)
**File:** `common/hardware/__init__.py`
**Goal:** Detect RK3588 and return the correct hardware object.

```python
import os
from functools import lru_cache

def _looks_like_rk3588() -> bool:
	try:
		if os.path.exists('/dev/rknpu') or os.path.exists('/dev/rknpu0'):
			return True
		if os.path.exists('/proc/device-tree/compatible'):
			with open('/proc/device-tree/compatible', 'r', encoding='utf-8') as f:
				if 'rk3588' in f.read().lower():
					return True
		if os.path.exists('/proc/cpuinfo'):
			with open('/proc/cpuinfo', 'r', encoding='utf-8') as f:
				if 'rk3588' in f.read().lower():
					return True
		return False
	except Exception:
		return False

@lru_cache()
def get_hardware():
	if _looks_like_rk3588():
		from openpilot.common.hardware.rk3588.hardware import RK3588Hardware
		return RK3588Hardware(detected=True)
	try:
		from openpilot.system.hardware.tici import TICIHardware
		return TICIHardware()
	except Exception:
		from openpilot.system.hardware.base import HardwareBase
		return HardwareBase()
```

**Test:** Add a test in `common/hardware/tests/` that mocks `/proc/cpuinfo` and `/dev/rknpu` to verify detection.

## 🧠 2. The "Brain" Concept: CPU vs. NPU vs. RGA
A normal laptop uses a Central Processing Unit (CPU) for everything. If a CPU had to handle live video and AI driving models simultaneously, it would lag and the car would crash. The Orange Pi 5 (RK3588 chip) works around this by dividing the labor between specialized "brains":

*   **The CPU (The Manager - 8 cores):** The RK3588 has an 8-core CPU. It handles the operating system, moves data around, and runs the basic logic (like deciding how much to turn the steering wheel based on simple math).
*   **The NPU (The Thinker - Neural Processing Unit - 3 INT8 cores):** Instead of a heavy GPU, the RK3588 has a 3-core NPU. This chip is physically hardwired to do one thing: run Artificial Intelligence neural networks. It calculates AI math exponentially faster and uses significantly less battery/electricity than a normal computer. It speaks a specific "language" and relies on highly optimized INT8 (8-bit integer) numbers instead of heavy decimals.
*   **The RGA (The Eye Doctor - Raster Graphics Accelerator):** Video straight from a 4K camera is way too massive for the AI to "read" quickly. The RGA is a dedicated hardware chip that instantly resizes the image (e.g., down to 512x384), rotates it, and changes the color format (from camera YUV to computer RGB) in microseconds, all without bothering the CPU or NPU.
*   **The RKMpp (Media Process Platform):** Another devoted chip responsible exclusively for compressing/decompressing video files to save storage space without taxing the CPU.

---

## 💰 3. The Computing Budget: Understanding "6 TOPS"
Because the Orange Pi 5 is a small board, its NPU has a maximum processing speed limit of **6 TOPS** (Tera Operations Per Second). Think of this as "6 Units of Neural Brainpower." If you ask the NPU to use 7 TOPS, the driving system will lag and fail.

To prevent the board from crashing, EnhancedOpenPilot securely splits this budget algorithmically across different AI tasks:
1.  **Main Vision & Policy (3.5 TOPS @ 20 times a second):** This is the core driving AI model. It looks at the road and outputs a 3D trajectory of exactly where the car should physically drive.
2.  **Object Detection (1.5 TOPS @ 15 times a second):** Runs an AI called *YOLOv8n-seg*. Its entire job is to scan the image for hazard bounding boxes (cars, pedestrians, stop signs).
3.  **Semantic Segmentation (1.0 TOPS @ 15 times a second):** Runs an AI called *PP-LiteSeg*. Its entire job is to color in the pixels on the screen to strictly categorize the road surface versus the lane lines.
4.  **Driver Monitoring (External):** We already spent our entire 6.0 TOPS (3.5 + 1.5 + 1.0) on just looking out the windshield! Looking at the driver's face to make sure they are awake requires another 2 to 3 TOPS. Because the main NPU is completely "maxed out", EnhancedOpenPilot physically offloads this task to a **PCIe Accelerator**, a secondary plug-in chip, to ensure the main driving system is never interrupted.

---

## 🔄 4. Step-by-Step Flow: The 100Hz Control Loop
A self-driving car cannot afford to be late. The software forces the system to calculate steering and gas exactly **100 times every single second (0.01 seconds per cycle, or 100Hz)**. Here is exactly what happens in a comprehensive timeline of that microscopic fraction of a second:

1.  **Boot Up (`system/manager`):** When you turn the car on, a script called `manager.py` reads a master roster (`process_config.py`). It boots up the cameras, the AI, and the steering math, verifying all feature toggles (like `EOPExternalPerceptionEnabled`) are correct.
2.  **Seeing the Road (`camerad`):** Up to 6 cameras plugged into the Orange Pi's CSI ports snap an instant picture of the road.
3.  **Image Adjustments (`rga.py`):** Before the image can even be cached properly, the Orange Pi's RGA shrinks the image to the exact square needed by the AI, and color-corrects it to RGB format instantly.
4.  **NPU Forward Passes (`modeld`):** The fixed image is injected into the NPU. The AI model performs a "forward pass." Within milliseconds, it spits out neural network predictions—a string of numbers translating to "tight curve ahead" or "car braking fast."
5.  **IPC Shouting (`msgq` & Cap'n Proto):** The programs in OpenPilot don't talk to each other like a standard app. Instead, they shout their findings into an Inter-Process Communication (IPC) message queue called `msgq`. The AI shouts "curve ahead!" in a specialized format (Cap'n Proto) and the control system listens.
6.  **Control Math (`controlsd.py`):** The control loop wakes up exactly every 0.01 seconds. It reads the AI's latest message, reads the car's current speed, and uses advanced math controllers (LQR, PID, DEC, TJA) to algorithmically calculate exactly how many degrees to spin the steering wheel.
7.  **Hardware-Gated Safety Check (`BrownPanda`):** Before the steering wheel is actually commanded to move, the data hits a hardware safety module. The BrownPanda logic double-checks the math (e.g., "Is the software trying to jerk the wheel left while going 70mph?"). If it's mathematically dangerous, BrownPanda hardware-blocks the signal from reaching the car's CAN bus. If it's safe, the car physically moves.

---

## 🗺️ 5. Code Map (Where Everything Lives)
If you need to peek into the software files or direct a programmer, you only need to care about a few specific folders. Here is what they do in plain English:

*   **`common/hardware/rk3588/` (The Translation Layer):** This is the holy grail for your Orange Pi 5. Because OpenPilot was originally built for comma.ai hardware, this folder contains all the custom code that acts as a translator. It houses `npu.py` (wakes up the AI chip), `rga.py` (image fixing), and `gpio.py` (talking to car wires). It ensures the rest of the code commands natively translate to the Orange Pi.
*   **`selfdrive/modeld/models/` (The AI Brains):** This is literally where the "brain" files are stored. The Orange Pi 5 NPU only accepts models natively compiled into a special file type ending in **`.rknn`**.
*   **`tools/rknn/` (The Model Conversion Classroom):** If you build a new AI model using Python/PyTorch, the Orange Pi natively won't understand it. This folder contains the tools to convert standard ONNX models into the optimized `.rknn` files. **Crucial Note:** You *cannot* run these conversion tools on the Orange Pi itself; they must be run on a powerful desktop PC (x86 architecture) beforehand because the conversion demands massive compute power to perform INT8 quantization.
*   **`system/manager/process_config.py` (The Master Roster):** A simple Python list of every single program (camera daemon, tracking daemon, UI daemon) that turns on when the car starts, along with their toggles.
*   **`selfdrive/controls/` (The Driver):** The math files containing the 100 times-per-second control loop, ensuring smooth lane centering and braking.

---

## 🎯 6. Actionable Lego Blocks (Next Steps)
When bringing up your Orange Pi 5 setup piece-by-piece, do not attempt to compile and understand the whole steering/AI math at once. Treat it like Lego blocks.

**Block 1. The Cameras (`camerad`)**
Ensure your cameras are properly plugged into the orange Pi's CSI ports. Run only the camera code and verify that the RGA is successfully capturing and resizing video without errors. Don't worry about driving yet.

**Block 2. Model Conversion (`tools/rknn/`)**
Get your desktop computer (x86_64). Take your target AI models and run them through the `convert_detection_models.sh` script to convert them to INT8 `.rknn` models. Prove they convert and quantize precisely without errors.

**Block 3. Loading the NPU Natively (`modeld`)**
Transfer the newly minted `.rknn` files onto the Orange Pi 5. Write a simple Python script using `common/hardware/rk3588/npu.py` to simply load the model natively into the NPU, feed it a picture, and see if it outputs numbers without crashing.

**Block 4. Plugging into IPC Queue (`msgq`)**
Once the AI natively outputs numbers from a picture via the NPU, plug the script into the `manager.py` so it starts shouting its messages into the Cap'n Proto `msgq` queue. At this point, the control systems can finally start reading the data.

---

## 📬 7. The Cereal Folder (The Postal Service)
The `cereal` folder is the **"Postal Service" and "Dictionary"** of your self-driving car.

Earlier, we talked about **IPC Shouting (Inter-Process Communication)**—how the AI brain (`modeld`) shouts "Curve ahead!" and the steering system (`controlsd`) listens. The `cereal` folder is what makes that conversation possible.

Here is what it does and why it is critical for the Orange Pi 5:

### 1. The Cap'n Proto "Dictionary" (`.capnp` files)
If the AI shouted instructions in French, and the steering wheel only spoke English, the car would crash.
Inside the `cereal` folder, there are files ending in `.capnp` (like `log.capnp` and `car.capnp`). These are strict dictionaries. They force every single program in the car to format their data in the exact same way.
*   **Example:** It enforces a rule that says: "Whenever someone reports the car's speed, it *must* be formatted as a tiny decimal number."

### 2. High-Speed Delivery for the Orange Pi 5
The Orange Pi 5 is coordinating three different chips simultaneously: the CPU, the NPU, and the RGA. They are all firing off data 100 times a second. Text files or standard computer data are too "heavy" and would cause a traffic jam.
`cereal` uses a technology incredibly optimized for speed (Cap'n Proto) that allows the NPU and CPU to pass messages back and forth in **microseconds** with almost zero effort. It’s a lightning-fast data highway.

### 3. The "Radio Frequencies" (`services.py`)
Inside this folder is a file called `services.py`. Think of this as the radio dial for the car.
*   It assigns a specific frequency to the camera, a different frequency to the AI, and a different one to the steering wheel.
*   This ensures that when the camera takes a picture, only programs that tuned into the "Camera Frequency" get the message, preventing the system from getting messy.

**In summary:**
The `cereal` folder doesn't contain Orange Pi 5 specific "hardware" code. Instead, it provides the blazing-fast communication network that allows the Orange Pi's scattered chips (CPU, NPU, RGA) to talk to each other seamlessly without slowing down!

---

## 🧩 9. Realtime Helpers: Core affinity and scheduling (reference)
When porting to an Orange Pi 5, it's useful to include safe helpers that attempt to set CPU affinity and realtime scheduling only when the platform supports it. Add these functions to your `common/realtime.py` or keep them as a reference in this file so porting scripts can copy them into new repositories.

```python
def set_core_affinity(cores: list[int]) -> None:
	# Only attempt on non-PC or when RK NPU device nodes exist
	if not PC or os.path.exists('/dev/rknpu0') or os.path.exists('/dev/rknpu'):
		try:
			os.sched_setaffinity(0, cores)
		except Exception:
			pass



## 🟦 Orange Pi 5 Porting: openpilot, release, scripts Folders

### openpilot
**Purpose:** Main process tree (selfdrive, controls, modeld, car, etc.)

**Orange Pi 5 relevance:**
- `selfdrive/modeld/models/` contains `.rknn` models for RK3588 NPU. These must match your NPU budget (see model inventory and NPU_AND_MODELS.md).
- `selfdrive/modeld/README.md` and `docs/NPU_AND_MODELS.md` describe model requirements, NPU utilization, and conversion steps.
- `selfdrive/camerad/` and `common/hardware/rk3588/` handle all camera and hardware specifics (CSI, RGA, NPU, GPIO, PCIe accel).

**Action:**
- Ensure all required `.rknn` models are present in `selfdrive/modeld/models/`.
- Use `tools/rknn/convert_detection_models.sh` on a desktop (x86_64) to convert ONNX models to `.rknn` for RK3588.
- Validate NPU utilization does not exceed 6.0 TOPS (see model inventory table).
- For new models, update the inventory and test with `common/hardware/rk3588/npu.py`.

---

### release
**Purpose:** Build and release scripts for packaging and deployment.

**Orange Pi 5 relevance:**
- Use `build_devel.sh` or `build_release.sh` for packaging the stack for Orange Pi 5.
- No RK3588-specific logic is needed; scripts are platform-agnostic.

**Action:**
- Run `./release/build_devel.sh` for development builds.
- Run `./release/build_release.sh` for production images.
- Validate output images on Orange Pi 5 hardware.

---

### scripts
**Purpose:** Utility scripts for deployment, camera HAL, power management, and validation.

**Orange Pi 5 relevance:**
- **`rk3588_secure_host.sh`**: Secure lockdown, OpenBLT flashing, and SSH lockdown for RK3588 hosts. Use for production deployment and firmware flashing. Example usage:
	```bash
	./scripts/rk3588_secure_host.sh --lock
	./scripts/rk3588_secure_host.sh --unlock
	./scripts/rk3588_secure_host.sh --status
	./scripts/rk3588_secure_host.sh --flash --image firmware.srec
	```
- **`setup_camera_hal_env.sh`**: Sets up environment variables and system settings for the unified Camera HAL. Run before launching camera daemons to ensure zero-copy and high-performance operation.
	```bash
	source ./scripts/setup_camera_hal_env.sh
	```
- **`verify_big_core_allocation.sh`**: Verifies that safety-critical daemons (e.g., `controlsd`, `modeld`, `stereod`) are running on the correct RK3588 big CPU cores with proper priorities. Example output:
	```bash
	./scripts/verify_big_core_allocation.sh
	# Shows which daemons are on big cores (4-7) and their priorities
	```
- **`disable-powersave.py`**: Disables power-saving features on the device to ensure maximum performance. Run at boot or before starting OpenPilot:
	```bash
	python3 ./scripts/disable-powersave.py
	```
- **`reset_eop_params.sh`**: Backs up and wipes `/data/params` after a migration (e.g., EOP_ → EP_ prefix). Use with caution:
	```bash
	./scripts/reset_eop_params.sh
	# Prompts for confirmation, backs up, wipes, and recreates params dir
	```

**Action:**
- Use these scripts for setup, validation, and troubleshooting on Orange Pi 5.
- Automate their invocation in deployment scripts or CI pipelines for consistent bring-up and validation.

---

### Porting/Validation Checklist (for Orange Pi 5)

- [ ] All required `.rknn` models present and validated in `selfdrive/modeld/models/`
- [ ] NPU utilization ≤ 6.0 TOPS (see model inventory)
- [ ] Camera HAL environment configured (`setup_camera_hal_env.sh`)
- [ ] Daemon core affinity and priorities verified (`verify_big_core_allocation.sh`)
- [ ] Power-saving disabled (`disable-powersave.py`)
- [ ] Secure host lockdown and firmware flashing as needed (`rk3588_secure_host.sh`)
- [ ] Params reset after migration (`reset_eop_params.sh`)
- [ ] Build and release scripts tested (`build_devel.sh`, `build_release.sh`)

---

**Tip:** For automation, chain these scripts in your deployment pipeline and validate each step with log output. For new repo ports, copy this checklist and adapt as needed.

## 🟦 Step 2: Camera HAL & Daemon Migration
**Unified interface for all daemons:**

```python
from common.hardware.rk3588.camera import (
	OX03C10Camera, CSICameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
```

**USB Camera Example:**
```python
from common.hardware.rk3588.camera import (
	UVCCamera, USBCameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
camera_config = USBCameraConfig(
	device_path=device_path,
	width=width, height=height, pixel_format=V4L2PixelFormat.YUYV,
	fps=fps, usb_port="auto", uvc_version="1.5",
	---
	# 🧠 Orange Pi 5 Minimal OpenPilot Porting Guide (IMX415, Vision+Policy Only)

	This file is a **maximal, AI-automatable knowledge base** for porting any OpenPilot-based repo to Orange Pi 5 (RK3588) with only a single IMX415 front camera and only the `driving_vision.rknn` and `driving_policy.rknn` models. All other features (driver monitoring, stereo, Bluetooth, voice, grid, ground, track, predict, side cameras, etc.) are disabled or removed. Use this as the only reference for automation or manual porting.

	---

	## 1. Directory Map: What to Keep, What to Remove

	**Keep/Adapt:**
	- `common/hardware/rk3588/` (all files, especially `camera/`, `npu.py`, `rga.py`, `hardware.py`)
	- `selfdrive/camerad/` (only for IMX415 front camera)
	- `selfdrive/modeld/` (only `driving_vision.rknn`, `driving_policy.rknn`, and their wrappers)
	- `selfdrive/controls/` (only `controlsd.py`, `plannerd.py`, `radard.py`)
	- `selfdrive/car/` (only your car's interface and CAN parser)
	- `cereal/` (all, for Cap'n Proto messaging)
	- `system/manager/`, `system/hardware/`, `system/camerad/` (minimal, see below)
	- `scripts/` (only `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`)

	**Remove/Disable:**
	- All `monitoringd`, `stereod`, `externald`, `gridd`, `groundd`, `trackd`, `predictd`, `bluetoothd`, `voice`, `side cameras`, `driver monitoring`, `USB cameras`, `mapd`, `joystickd`, `elm327d`, `webjoystick`, `plated`, `snapd`, `loopd`, `crashd`, `debrisd`, `test/` folders not needed for your car.

	---

	## 2. Hardware Detection: RK3588-Only

	**File:** `system/hardware/__init__.py`

	```python
	from openpilot.common.hardware.rk3588.hardware import RK3588Hardware
	HARDWARE = RK3588Hardware(detected=True)
	RK3588 = True
	PC = False
	```

	**Remove all other hardware detection logic.**

	---

	## 3. Camera HAL: IMX415 Front Camera Only

	**File:** `common/hardware/rk3588/camera/csi.py`

	```python
	from common.hardware.rk3588.camera.v4l2 import V4L2Camera, V4L2Config, V4L2PixelFormat
	from common.hardware.rk3588.camera.sensors import IMX415Driver

	config = V4L2Config(
			device_path="/dev/video0",  # IMX415 front camera
			width=1920, height=1080, pixel_format=V4L2PixelFormat.YUYV,
			fps=30, memory_strategy="default"
	)
	camera = V4L2Camera(config)
	sensor = IMX415Driver(config.device_path)
	sensor.initialize()
	```

	**Remove all OX03C10, OS04C10, USB, and stereo camera logic.**

	---

	## 4. Model Inventory: Only Vision + Policy

	**Directory:** `selfdrive/modeld/models/`

	**Keep only:**
	- `driving_vision.rknn`
	- `driving_policy.rknn`

	**Remove all other models (YOLO, segmentation, headpose, etc.).**

	---

	## 5. Model Loading: Minimal RKNN Wrappers

	**File:** `selfdrive/modeld/vision/driving_vision_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingVisionRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load vision RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init vision RKNN runtime"
			def infer(self, img):
					return self.rknn.inference(inputs=[img])
	```

	**File:** `selfdrive/modeld/vision/driving_policy_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingPolicyRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load policy RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init policy RKNN runtime"
			def infer(self, features):
					return self.rknn.inference(inputs=[features])
	```

	---

	## 6. Minimal modeld: Only Vision + Policy

	**File:** `selfdrive/modeld/modeld.py` (simplified)

	```python
	from selfdrive.modeld.vision.driving_vision_rknn import DrivingVisionRKNN
	from selfdrive.modeld.vision.driving_policy_rknn import DrivingPolicyRKNN

	vision = DrivingVisionRKNN("models/driving_vision.rknn")
	policy = DrivingPolicyRKNN("models/driving_policy.rknn")

	# Main loop: get camera frame, run vision, then policy, publish result
	while True:
			img = get_camera_frame()  # Use IMX415 camera only
			vision_out = vision.infer(img)
			policy_out = policy.infer(vision_out)
			publish(policy_out)
	```

	---

	## 7. Process Registry: Only Required Daemons

	**File:** `system/manager/process_config.py`

	```python
	from openpilot.system.manager.process import PythonProcess, NativeProcess

	procs = [
		PythonProcess("camerad", "selfdrive.camerad.camerad", always_run),
		PythonProcess("modeld", "selfdrive.modeld.modeld", always_run),
		PythonProcess("controlsd", "selfdrive.controls.controlsd", always_run),
		PythonProcess("plannerd", "selfdrive.controls.plannerd", always_run),
		PythonProcess("radard", "selfdrive.controls.radard", always_run),
		PythonProcess("car", "selfdrive.car.card", always_run),
	]
	managed_processes = {p.name: p for p in procs}
	```

	**Remove all other processes (monitoringd, stereod, externald, bluetoothd, etc.).**

	---

	## 8. Controls: Minimal

	**File:** `selfdrive/controls/controlsd.py` (keep only core control loop, remove all references to unused features)

	**File:** `selfdrive/controls/plannerd.py`, `selfdrive/controls/radard.py` (keep only core logic)

	---

	## 9. Car Interface: Minimal

	**File:** `selfdrive/car/<yourcar>/interface.py` (implement only CAN parsing and actuator commands for your car)

	---

	## 10. Messaging: Cereal

	**Keep all Cap'n Proto schemas and messaging code in `cereal/`.**

	---

	## 11. Scripts: Only What You Need

	- `scripts/setup_camera_hal_env.sh` (run before launching)
	- `scripts/disable-powersave.py` (run at boot)
	- `scripts/verify_big_core_allocation.sh` (validate core affinity)

	---

	## 12. Build & Run

	**Build:**
	```bash
	./release/build_devel.sh
	# or
	./release/build_release.sh
	```

	**Run:**
	```bash
	source ./scripts/setup_camera_hal_env.sh
	python3 -m selfdrive.camerad.camerad &
	python3 -m selfdrive.modeld.modeld &
	python3 -m selfdrive.controls.controlsd &
	python3 -m selfdrive.controls.plannerd &
	python3 -m selfdrive.controls.radard &
	python3 -m selfdrive.car.card &
	```

	---

	## 13. Porting/Validation Checklist (AI/Automation Ready)

	- [ ] Only `driving_vision.rknn` and `driving_policy.rknn` present in `selfdrive/modeld/models/`
	- [ ] Only IMX415 front camera enabled (no wide, stereo, USB, or driver monitoring)
	- [ ] Only Orange Pi 5 hardware detection logic present
	- [ ] Only required daemons enabled in process registry
	- [ ] All unused features/processes removed or disabled
	- [ ] Camera HAL and IMX415 driver validated
	- [ ] Controls and car interface minimal and correct
	- [ ] Scripts for camera HAL and power validated
	- [ ] Build and run scripts tested

	---

	## 🟧 Stability & Safety Guard Checklist (AI/Manual Porting)

	**Track and implement these before any road testing or production deployment.**

### Critical Safety/Robustness Fixes
- [ ] Replace all `assert` with `raise RuntimeError` in `rknn_runner.py` (asserts can be disabled, raising is always safe)
- [ ] Add null check on RKNN `outputs_get()` before indexing (raise if None)
- [ ] Add `np.isfinite()` guard on all NPU outputs before parsing (raise if NaN/Inf)
- [ ] Verify policy input key order matches RKNN model input order at startup (log both orders)
- [ ] Ensure `release()` is called on RKNNRunner at shutdown (use `atexit` or `try/finally` in modeld)
- [ ] Add camera reconnect/retry loop in `camera.py` (for CSI/USB disconnect resilience)
- [ ] Verify A76 core numbering: `cat /sys/devices/system/cpu/cpu{4..7}/cpufreq/cpuinfo_max_freq` (should be 2400000 for big cores)
- [ ] Add/verify heatsink + fan for sustained NPU performance (thermal throttling can cause >30ms inference)
- [ ] Broaden `/dev/rknpu0` check to also match `/dev/rknpu` (kernel naming varies)
- [ ] Add `__del__` guard in RKNNRunner to prevent double-release segfaults

### Operational/Deployment Gaps
- [ ] Add `rknn-toolkit-lite2` install instructions to setup scripts (cannot be in pyproject.toml, not on PyPI)
- [ ] Add thermal warning in UI/log if modelExecutionTime > 0.025s (optional, but recommended)
- [ ] Track and log all stability/safety checklist items in CI or deployment pipeline

---

## 🟧 Stability & Safety Guard Reference (Details)

**1. RKNN Error Handling:**
  - Replace all `assert` with `raise RuntimeError` in `rknn_runner.py`.
  - Add null check on `outputs_get()` before indexing.
  - Add `np.isfinite()` guard on all NPU outputs before parsing.

**2. Policy Input Order:**
  - At startup, print/log both the policy input dict key order and the RKNN model's expected input order. Confirm they match.

**3. RKNN Resource Management:**
  - Ensure `release()` is always called on RKNNRunner at shutdown (use `atexit` or `try/finally`).
  - Add `__del__` guard to RKNNRunner to prevent double-release segfaults.

**4. Camera Robustness:**
  - Add a reconnect/retry loop in `camera.py` for CSI/USB disconnects.

**5. Core Affinity & Thermal:**
  - Verify A76 core numbering on your kernel (should be 2400000 kHz for big cores).
  - Add/verify heatsink + fan for sustained NPU performance.
  - Add thermal warning in UI/log if modelExecutionTime > 0.025s.

**6. NPU Device Node Detection:**
  - Broaden `/dev/rknpu0` check to also match `/dev/rknpu`.

**7. RKNN Dependency:**
  - Add `rknn-toolkit-lite2` install instructions to setup scripts (manual pip install from Rockchip wheel).

**8. CI/Automation:**
  - Track and log all stability/safety checklist items in CI or deployment pipeline.

---




## 🟦 Interactive AI-Driven Porting Protocol (Step-by-Step)

### 🟢 Step 0: Ensure .claude/ and .vscode/ Folders Exist

Before starting any porting or automation, check for the presence of the `.claude/` and `.vscode/` folders at the root of your repo:

- **.claude/**: Contains AI agent rules, checklists, and automation scripts. This is essential for AI-driven automation and porting. Reference the structure and contents from this repo if you need to create it.
- **.vscode/**: Contains workspace/editor settings for VS Code. This is optional for runtime, but highly recommended for maximizing AI/VS Code automation. Reference the structure and contents from this repo if you need to create it.

**If either folder is missing:**
1. The AI agent (or user) should create the missing folder(s) at the repo root.
2. Populate them with the standard files from this repo (see `.claude/` and `.vscode/` here for examples).
3. Only proceed to the next step after confirming both folders exist.

**Summary:**
- `.claude/` enables robust, rule-based AI automation.
- `.vscode/` enables consistent workspace/editor settings for AI and human developers.

---

This section defines a **step-by-step, interactive automation workflow** for porting or validating any OpenPilot/SunnyPilot repo to Orange Pi 5. It is designed for use by AI agents (or humans) in VS Code or similar environments, ensuring:
- Each step is explained before changes are made
- The user confirms understanding before proceeding
- All required files/folders are checked and created if missing
- After each step, a summary of what was done is provided
- Only after user confirmation does the process continue

### 🟢 Protocol Overview
1. **Explain the step and what will change**
2. **Check for required files/folders**
	 - If missing, help the user create them (with exact path and content)
3. **Make the change (code/config/script)**
4. **Summarize what was done and why**
5. **Wait for user confirmation to proceed**
6. **Repeat for next step**

---

### 🟩 Example Interactive Step (AI/Automation)

**Step 1: Model Inventory Cleanup**
- *Explain*: "We will remove all models except `driving_vision.rknn` and `driving_policy.rknn` from `selfdrive/modeld/models/`. This ensures only the required INT8 models are present for Orange Pi 5."
- *Check*: "Are both required models present? If not, here is how to add them..."
- *Action*: "Remove all other model files."
- *Summary*: "Now only the required models remain. This reduces NPU load and avoids errors."
- *Confirm*: "Do you understand and want to proceed to the next step? (yes/no)"

---

### 🟦 Checklist-Driven Guidance

- At each step, the agent checks the relevant checklist (in learn.md or a dedicated checklist folder/file).
- If a checklist item or file is missing, the agent:
	- Explains what is missing and why it matters
	- Offers to create the file/folder with the correct structure
	- Waits for user confirmation before proceeding

---

### 🟧 User/AI Interaction Pattern

1. **AI/agent explains the next step and what will change**
2. **User reviews and confirms understanding**
3. **AI/agent checks for all required files/folders**
4. **If missing, AI/agent offers to create them and explains their purpose**
5. **AI/agent makes the change and summarizes the result**
6. **User confirms to proceed**
7. **Repeat until all porting/validation steps are complete**

---

### 🟦 How to Use This Protocol

- Use this section as the master automation script for any AI agent or human following the porting process.
- For each checklist item or porting step, follow the interactive pattern above.
- Never skip user confirmation or summary after each step.
- Always check for missing files/folders and help the user create them.
- This ensures maximum transparency, learning, and error prevention during repo porting.

---

### 1. Model Inventory & Quantization (INT8 Only)

- **Only keep these models in `selfdrive/modeld/models/`:**
	- `driving_vision.rknn` (Vision, INT8 quantized)
	- `driving_policy.rknn` (Policy, INT8 quantized)
- **Remove all other models** (YOLO, segmentation, headpose, etc.) unless explicitly needed for your car.
- **Quantization:**
	- All RKNN models must be INT8 quantized (`do_quantization=True` in conversion scripts) for maximum NPU speed on RK3588/Orange Pi 5.
	- Do not use FP16 or FP32 models for driving vision/policy; they will be slow or unsupported.
- **Reference:** See `inference_registry.yaml` and `README.md` in `selfdrive/modeld/models/` for model paths, input sizes, and NPU core assignments.

### 2. Model Conversion & Validation

- Use `tools/rknn/convert_detection_models.sh` on x86_64 PC to convert ONNX → `.rknn` (INT8 quantized).
- Validate model load and inference with `common/hardware/rk3588/npu.py` before deploying to Orange Pi 5.
- Update `inference_registry.yaml` to reflect only the models you keep.

### 3. Essential Scripts & Automation

- **Setup/validation scripts to automate:**
	- `scripts/setup_camera_hal_env.sh` (Camera HAL env)
	- `scripts/disable-powersave.py` (Disable CPU power save)
	- `scripts/verify_big_core_allocation.sh` (Check core affinity)
	- `scripts/rk3588_secure_host.sh` (Lockdown/firmware)
- **Automate these in your CI/deployment pipeline.**
- **Document any required environment variables or feature flags.**

### 4. Directory/File Map for Automation

- `common/hardware/rk3588/` — All hardware/camera/NPU code
- `selfdrive/modeld/models/` — Only vision/policy `.rknn` models
- `selfdrive/controls/` — Only `controlsd.py`, `plannerd.py`, `radard.py`
- `selfdrive/car/` — Only your car’s interface and CAN parser
- `cereal/` — All Cap'n Proto schemas and messaging
- `system/manager/`, `system/hardware/`, `system/camerad/` — Minimal, as above
- `scripts/` — Only the scripts listed above

### 5. Remove/Disable Everything Else

- All monitoringd, stereod, externald, gridd, groundd, trackd, predictd, bluetoothd, voice, side cameras, USB cameras, mapd, joystickd, elm327d, webjoystick, plated, snapd, loopd, crashd, debrisd, and any test/ folders not needed for your car.

### 6. .claude/ and .vscode/ for AI Automation

- **.claude/**: Keep for AI agent rules, checklists, and porting automation. Not needed for runtime, but essential for AI-driven repo adaptation.
- **.vscode/**: Keep for workspace/editor settings if you want to maximize AI/VS Code automation. Not required for runtime.

### 7. Automation Notes for AI Agents

- Use this learn.md as the single source of truth for porting/validating any OpenPilot/SunnyPilot repo to Orange Pi 5.
- All code/config snippets, directory/file maps, and checklists are AI-automatable.
- For new repo ports, copy this file, update only the car interface and model paths, and follow all checklists.
- For validation, run all scripts and checklists in CI or deployment pipeline.

### 8. Troubleshooting & Validation

- If any model fails to load or is slow, check quantization (must be INT8) and NPU core assignment.
- If camera or NPU fails, validate with test scripts in `common/hardware/rk3588/tests/`.
- If CAN or car interface fails, check `selfdrive/car/` and `selfdrive/socketd/socketd.py`.

### 9. Final Checklist (AI/Automation Ready)

- [ ] Only `driving_vision.rknn` and `driving_policy.rknn` present (INT8, correct paths)
- [ ] All other models removed
- [ ] Only IMX415 front camera enabled
- [ ] Only required daemons/processes enabled
- [ ] All unused features/processes removed
- [ ] All scripts validated and automated
- [ ] All hardware abstraction and platform detection logic correct
- [ ] All safety/stability guard items implemented
- [ ] .claude/ and .vscode/ present for AI automation (optional for runtime)
- [ ] learn.md up to date and used as automation source

- [ ] List all required `.rknn` models and their exact paths (e.g., `selfdrive/modeld/models/driving_vision.rknn`, `driving_policy.rknn`)
- [ ] Document all environment variables and feature flags needed (e.g., `USE_WEBCAM=1`, `NO_DM=1`, `ROAD_CAM` auto-detect)
- [ ] Summarize all process/daemon requirements (minimal list: `camerad`, `modeld`, `controlsd`, `plannerd`, `radard`, `card`, `socketd`)
- [ ] Specify all hardware abstraction and platform detection logic (e.g., RK3588 detection, NPU device node checks)
- [ ] List all scripts and utilities required for setup, validation, and deployment (e.g., `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`, `rk3588_secure_host.sh`)
- [ ] Document all code changes or diffs needed for porting (e.g., RKNN runner, modeld.py changes, SConscript skips, launch_env.sh env vars)
- [ ] Include all stability and safety guard checklist items (as above)
- [ ] Note all files/folders to keep, adapt, or remove (directory map)
- [ ] Summarize all tuning/parameter changes (e.g., camera focal length, DT_MDL, service frequencies)
- [ ] Reference all historical commits or diffs that must be replicated for new ports
- [ ] List all manual install steps (e.g., `rknn-toolkit-lite2` wheel, Mali driver, IMU wiring if used)
- [ ] Add any additional notes for automation, CI, or AI-driven porting

---

## 🟨 Orange Pi 5 Porting: openpilot, release, scripts Folders

### openpilot
**Purpose:** Main process tree (selfdrive, controls, modeld, car, etc.)

**Orange Pi 5 relevance:**
- `selfdrive/modeld/models/` contains `.rknn` models for RK3588 NPU. These must match your NPU budget (see model inventory and NPU_AND_MODELS.md).
- `selfdrive/modeld/README.md` and `docs/NPU_AND_MODELS.md` describe model requirements, NPU utilization, and conversion steps.
- `selfdrive/camerad/` and `common/hardware/rk3588/` handle all camera and hardware specifics (CSI, RGA, NPU, GPIO, PCIe accel).

**Action:**
- Ensure all required `.rknn` models are present in `selfdrive/modeld/models/`.
- Use `tools/rknn/convert_detection_models.sh` on a desktop (x86_64) to convert ONNX models to `.rknn` for RK3588.
- Validate NPU utilization does not exceed 6.0 TOPS (see model inventory table).
- For new models, update the inventory and test with `common/hardware/rk3588/npu.py`.

---

### release
**Purpose:** Build and release scripts for packaging and deployment.

**Orange Pi 5 relevance:**
- Use `build_devel.sh` or `build_release.sh` for packaging the stack for Orange Pi 5.
- No RK3588-specific logic is needed; scripts are platform-agnostic.

**Action:**
- Run `./release/build_devel.sh` for development builds.
- Run `./release/build_release.sh` for production images.
- Validate output images on Orange Pi 5 hardware.

---

### scripts
**Purpose:** Utility scripts for deployment, camera HAL, power management, and validation.

**Orange Pi 5 relevance:**
- **`rk3588_secure_host.sh`**: Secure lockdown, OpenBLT flashing, and SSH lockdown for RK3588 hosts. Use for production deployment and firmware flashing. Example usage:
	```bash
	./scripts/rk3588_secure_host.sh --lock
	./scripts/rk3588_secure_host.sh --unlock
	./scripts/rk3588_secure_host.sh --status
	./scripts/rk3588_secure_host.sh --flash --image firmware.srec
	```
- **`setup_camera_hal_env.sh`**: Sets up environment variables and system settings for the unified Camera HAL. Run before launching camera daemons to ensure zero-copy and high-performance operation.
	```bash
	source ./scripts/setup_camera_hal_env.sh
	```
- **`verify_big_core_allocation.sh`**: Verifies that safety-critical daemons (e.g., `controlsd`, `modeld`, `stereod`) are running on the correct RK3588 big CPU cores with proper priorities. Example output:
	```bash
	./scripts/verify_big_core_allocation.sh
	# Shows which daemons are on big cores (4-7) and their priorities
	```
- **`disable-powersave.py`**: Disables power-saving features on the device to ensure maximum performance. Run at boot or before starting OpenPilot:
	```bash
	python3 ./scripts/disable-powersave.py
	```
- **`reset_eop_params.sh`**: Backs up and wipes `/data/params` after a migration (e.g., EOP_ → EP_ prefix). Use with caution:
	```bash
	./scripts/reset_eop_params.sh
	# Prompts for confirmation, backs up, wipes, and recreates params dir
	```

**Action:**
- Use these scripts for setup, validation, and troubleshooting on Orange Pi 5.
- Automate their invocation in deployment scripts or CI pipelines for consistent bring-up and validation.

---

### Porting/Validation Checklist (for Orange Pi 5)

- [ ] All required `.rknn` models present and validated in `selfdrive/modeld/models/`
- [ ] NPU utilization ≤ 6.0 TOPS (see model inventory)
- [ ] Camera HAL environment configured (`setup_camera_hal_env.sh`)
- [ ] Daemon core affinity and priorities verified (`verify_big_core_allocation.sh`)
- [ ] Power-saving disabled (`disable-powersave.py`)
- [ ] Secure host lockdown and firmware flashing as needed (`rk3588_secure_host.sh`)
- [ ] Params reset after migration (`reset_eop_params.sh`)
- [ ] Build and release scripts tested (`build_devel.sh`, `build_release.sh`)

---

**Tip:** For automation, chain these scripts in your deployment pipeline and validate each step with log output. For new repo ports, copy this checklist and adapt as needed.

## 🟦 Step 2: Camera HAL & Daemon Migration
**Unified interface for all daemons:**

```python
from common.hardware.rk3588.camera import (
	OX03C10Camera, CSICameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
```

**USB Camera Example:**
```python
from common.hardware.rk3588.camera import (
	UVCCamera, USBCameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
camera_config = USBCameraConfig(
	device_path=device_path,
	width=width, height=height, pixel_format=V4L2PixelFormat.YUYV,
	fps=fps, usb_port="auto", uvc_version="1.5",
	---
	# 🧠 Orange Pi 5 Minimal OpenPilot Porting Guide (IMX415, Vision+Policy Only)

	This file is a **maximal, AI-automatable knowledge base** for porting any OpenPilot-based repo to Orange Pi 5 (RK3588) with only a single IMX415 front camera and only the `driving_vision.rknn` and `driving_policy.rknn` models. All other features (driver monitoring, stereo, Bluetooth, voice, grid, ground, track, predict, side cameras, etc.) are disabled or removed. Use this as the only reference for automation or manual porting.

	---

	## 1. Directory Map: What to Keep, What to Remove

	**Keep/Adapt:**
	- `common/hardware/rk3588/` (all files, especially `camera/`, `npu.py`, `rga.py`, `hardware.py`)
	- `selfdrive/camerad/` (only for IMX415 front camera)
	- `selfdrive/modeld/` (only `driving_vision.rknn`, `driving_policy.rknn`, and their wrappers)
	- `selfdrive/controls/` (only `controlsd.py`, `plannerd.py`, `radard.py`)
	- `selfdrive/car/` (only your car's interface and CAN parser)
	- `cereal/` (all, for Cap'n Proto messaging)
	- `system/manager/`, `system/hardware/`, `system/camerad/` (minimal, see below)
	- `scripts/` (only `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`)

	**Remove/Disable:**
	- All `monitoringd`, `stereod`, `externald`, `gridd`, `groundd`, `trackd`, `predictd`, `bluetoothd`, `voice`, `side cameras`, `driver monitoring`, `USB cameras`, `mapd`, `joystickd`, `elm327d`, `webjoystick`, `plated`, `snapd`, `loopd`, `crashd`, `debrisd`, `test/` folders not needed for your car.

	---

	## 2. Hardware Detection: RK3588-Only

	**File:** `system/hardware/__init__.py`

	```python
	from openpilot.common.hardware.rk3588.hardware import RK3588Hardware
	HARDWARE = RK3588Hardware(detected=True)
	RK3588 = True
	PC = False
	```

	**Remove all other hardware detection logic.**

	---

	## 3. Camera HAL: IMX415 Front Camera Only

	**File:** `common/hardware/rk3588/camera/csi.py`

	```python
	from common.hardware.rk3588.camera.v4l2 import V4L2Camera, V4L2Config, V4L2PixelFormat
	from common.hardware.rk3588.camera.sensors import IMX415Driver

	config = V4L2Config(
			device_path="/dev/video0",  # IMX415 front camera
			width=1920, height=1080, pixel_format=V4L2PixelFormat.YUYV,
			fps=30, memory_strategy="default"
	)
	camera = V4L2Camera(config)
	sensor = IMX415Driver(config.device_path)
	sensor.initialize()
	```

	**Remove all OX03C10, OS04C10, USB, and stereo camera logic.**

	---

	## 4. Model Inventory: Only Vision + Policy

	**Directory:** `selfdrive/modeld/models/`

	**Keep only:**
	- `driving_vision.rknn`
	- `driving_policy.rknn`

	**Remove all other models (YOLO, segmentation, headpose, etc.).**

	---

	## 5. Model Loading: Minimal RKNN Wrappers

	**File:** `selfdrive/modeld/vision/driving_vision_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingVisionRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load vision RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init vision RKNN runtime"
			def infer(self, img):
					return self.rknn.inference(inputs=[img])
	```

	**File:** `selfdrive/modeld/vision/driving_policy_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingPolicyRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load policy RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init policy RKNN runtime"
			def infer(self, features):
					return self.rknn.inference(inputs=[features])
	```

	---

	## 6. Minimal modeld: Only Vision + Policy

	**File:** `selfdrive/modeld/modeld.py` (simplified)

	```python
	from selfdrive.modeld.vision.driving_vision_rknn import DrivingVisionRKNN
	from selfdrive.modeld.vision.driving_policy_rknn import DrivingPolicyRKNN

	vision = DrivingVisionRKNN("models/driving_vision.rknn")
	policy = DrivingPolicyRKNN("models/driving_policy.rknn")

	# Main loop: get camera frame, run vision, then policy, publish result
	while True:
			img = get_camera_frame()  # Use IMX415 camera only
			vision_out = vision.infer(img)
			policy_out = policy.infer(vision_out)
			publish(policy_out)
	```

	---

	## 7. Process Registry: Only Required Daemons

	**File:** `system/manager/process_config.py`

	```python
	from openpilot.system.manager.process import PythonProcess, NativeProcess

	procs = [
		PythonProcess("camerad", "selfdrive.camerad.camerad", always_run),
		PythonProcess("modeld", "selfdrive.modeld.modeld", always_run),
		PythonProcess("controlsd", "selfdrive.controls.controlsd", always_run),
		PythonProcess("plannerd", "selfdrive.controls.plannerd", always_run),
		PythonProcess("radard", "selfdrive.controls.radard", always_run),
		PythonProcess("car", "selfdrive.car.card", always_run),
	]
	managed_processes = {p.name: p for p in procs}
	```

	**Remove all other processes (monitoringd, stereod, externald, bluetoothd, etc.).**

	---

	## 8. Controls: Minimal

	**File:** `selfdrive/controls/controlsd.py` (keep only core control loop, remove all references to unused features)

	**File:** `selfdrive/controls/plannerd.py`, `selfdrive/controls/radard.py` (keep only core logic)

	---

	## 9. Car Interface: Minimal

	**File:** `selfdrive/car/<yourcar>/interface.py` (implement only CAN parsing and actuator commands for your car)

	---

	## 10. Messaging: Cereal

	**Keep all Cap'n Proto schemas and messaging code in `cereal/`.**

	---

	## 11. Scripts: Only What You Need

	- `scripts/setup_camera_hal_env.sh` (run before launching)
	- `scripts/disable-powersave.py` (run at boot)
	- `scripts/verify_big_core_allocation.sh` (validate core affinity)

	---

	## 12. Build & Run

	**Build:**
	```bash
	./release/build_devel.sh
	# or
	./release/build_release.sh
	```

	**Run:**
	```bash
	source ./scripts/setup_camera_hal_env.sh
	python3 -m selfdrive.camerad.camerad &
	python3 -m selfdrive.modeld.modeld &
	python3 -m selfdrive.controls.controlsd &
	python3 -m selfdrive.controls.plannerd &
	python3 -m selfdrive.controls.radard &
	python3 -m selfdrive.car.card &
	```

	---

	## 13. Porting/Validation Checklist (AI/Automation Ready)

	- [ ] Only `driving_vision.rknn` and `driving_policy.rknn` present in `selfdrive/modeld/models/`
	- [ ] Only IMX415 front camera enabled (no wide, stereo, USB, or driver monitoring)
	- [ ] Only Orange Pi 5 hardware detection logic present
	- [ ] Only required daemons enabled in process registry
	- [ ] All unused features/processes removed or disabled
	- [ ] Camera HAL and IMX415 driver validated
	- [ ] Controls and car interface minimal and correct
	- [ ] Scripts for camera HAL and power validated
	- [ ] Build and run scripts tested

	---

	## 🟧 Stability & Safety Guard Checklist (AI/Manual Porting)

	**Track and implement these before any road testing or production deployment.**

### Critical Safety/Robustness Fixes
- [ ] Replace all `assert` with `raise RuntimeError` in `rknn_runner.py` (asserts can be disabled, raising is always safe)
- [ ] Add null check on RKNN `outputs_get()` before indexing (raise if None)
- [ ] Add `np.isfinite()` guard on all NPU outputs before parsing (raise if NaN/Inf)
- [ ] Verify policy input key order matches RKNN model input order at startup (log both orders)
- [ ] Ensure `release()` is called on RKNNRunner at shutdown (use `atexit` or `try/finally` in modeld)
- [ ] Add camera reconnect/retry loop in `camera.py` (for CSI/USB disconnect resilience)
- [ ] Verify A76 core numbering: `cat /sys/devices/system/cpu/cpu{4..7}/cpufreq/cpuinfo_max_freq` (should be 2400000 for big cores)
- [ ] Add/verify heatsink + fan for sustained NPU performance (thermal throttling can cause >30ms inference)
- [ ] Broaden `/dev/rknpu0` check to also match `/dev/rknpu` (kernel naming varies)
- [ ] Add `__del__` guard in RKNNRunner to prevent double-release segfaults

### Operational/Deployment Gaps
- [ ] Add `rknn-toolkit-lite2` install instructions to setup scripts (cannot be in pyproject.toml, not on PyPI)
- [ ] Add thermal warning in UI/log if modelExecutionTime > 0.025s (optional, but recommended)
- [ ] Track and log all stability/safety checklist items in CI or deployment pipeline

---

## 🟧 Stability & Safety Guard Reference (Details)

**1. RKNN Error Handling:**
  - Replace all `assert` with `raise RuntimeError` in `rknn_runner.py`.
  - Add null check on `outputs_get()` before indexing.
  - Add `np.isfinite()` guard on all NPU outputs before parsing.

**2. Policy Input Order:**
  - At startup, print/log both the policy input dict key order and the RKNN model's expected input order. Confirm they match.

**3. RKNN Resource Management:**
  - Ensure `release()` is always called on RKNNRunner at shutdown (use `atexit` or `try/finally`).
  - Add `__del__` guard to RKNNRunner to prevent double-release segfaults.

**4. Camera Robustness:**
  - Add a reconnect/retry loop in `camera.py` for CSI/USB disconnects.

**5. Core Affinity & Thermal:**
  - Verify A76 core numbering on your kernel (should be 2400000 kHz for big cores).
  - Add/verify heatsink + fan for sustained NPU performance.
  - Add thermal warning in UI/log if modelExecutionTime > 0.025s.

**6. NPU Device Node Detection:**
  - Broaden `/dev/rknpu0` check to also match `/dev/rknpu`.

**7. RKNN Dependency:**
  - Add `rknn-toolkit-lite2` install instructions to setup scripts (manual pip install from Rockchip wheel).

**8. CI/Automation:**
  - Track and log all stability/safety checklist items in CI or deployment pipeline.

---

## 🟩 Final Checklist: What to Extract and Document in learn.md

- [ ] List all required `.rknn` models and their exact paths (e.g., `selfdrive/modeld/models/driving_vision.rknn`, `driving_policy.rknn`)
- [ ] Document all environment variables and feature flags needed (e.g., `USE_WEBCAM=1`, `NO_DM=1`, `ROAD_CAM` auto-detect)
- [ ] Summarize all process/daemon requirements (minimal list: `camerad`, `modeld`, `controlsd`, `plannerd`, `radard`, `card`, `socketd`)
- [ ] Specify all hardware abstraction and platform detection logic (e.g., RK3588 detection, NPU device node checks)
- [ ] List all scripts and utilities required for setup, validation, and deployment (e.g., `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`, `rk3588_secure_host.sh`)
- [ ] Document all code changes or diffs needed for porting (e.g., RKNN runner, modeld.py changes, SConscript skips, launch_env.sh env vars)
- [ ] Include all stability and safety guard checklist items (as above)
- [ ] Note all files/folders to keep, adapt, or remove (directory map)
- [ ] Summarize all tuning/parameter changes (e.g., camera focal length, DT_MDL, service frequencies)
- [ ] Reference all historical commits or diffs that must be replicated for new ports
- [ ] List all manual install steps (e.g., `rknn-toolkit-lite2` wheel, Mali driver, IMU wiring if used)
- [ ] Add any additional notes for automation, CI, or AI-driven porting

---

## 🟨 Orange Pi 5 Porting: openpilot, release, scripts Folders

### openpilot
**Purpose:** Main process tree (selfdrive, controls, modeld, car, etc.)

**Orange Pi 5 relevance:**
- `selfdrive/modeld/models/` contains `.rknn` models for RK3588 NPU. These must match your NPU budget (see model inventory and NPU_AND_MODELS.md).
- `selfdrive/modeld/README.md` and `docs/NPU_AND_MODELS.md` describe model requirements, NPU utilization, and conversion steps.
- `selfdrive/camerad/` and `common/hardware/rk3588/` handle all camera and hardware specifics (CSI, RGA, NPU, GPIO, PCIe accel).

**Action:**
- Ensure all required `.rknn` models are present in `selfdrive/modeld/models/`.
- Use `tools/rknn/convert_detection_models.sh` on a desktop (x86_64) to convert ONNX models to `.rknn` for RK3588.
- Validate NPU utilization does not exceed 6.0 TOPS (see model inventory table).
- For new models, update the inventory and test with `common/hardware/rk3588/npu.py`.

---

### release
**Purpose:** Build and release scripts for packaging and deployment.

**Orange Pi 5 relevance:**
- Use `build_devel.sh` or `build_release.sh` for packaging the stack for Orange Pi 5.
- No RK3588-specific logic is needed; scripts are platform-agnostic.

**Action:**
- Run `./release/build_devel.sh` for development builds.
- Run `./release/build_release.sh` for production images.
- Validate output images on Orange Pi 5 hardware.

---

### scripts
**Purpose:** Utility scripts for deployment, camera HAL, power management, and validation.

**Orange Pi 5 relevance:**
- **`rk3588_secure_host.sh`**: Secure lockdown, OpenBLT flashing, and SSH lockdown for RK3588 hosts. Use for production deployment and firmware flashing. Example usage:
	```bash
	./scripts/rk3588_secure_host.sh --lock
	./scripts/rk3588_secure_host.sh --unlock
	./scripts/rk3588_secure_host.sh --status
	./scripts/rk3588_secure_host.sh --flash --image firmware.srec
	```
- **`setup_camera_hal_env.sh`**: Sets up environment variables and system settings for the unified Camera HAL. Run before launching camera daemons to ensure zero-copy and high-performance operation.
	```bash
	source ./scripts/setup_camera_hal_env.sh
	```
- **`verify_big_core_allocation.sh`**: Verifies that safety-critical daemons (e.g., `controlsd`, `modeld`, `stereod`) are running on the correct RK3588 big CPU cores with proper priorities. Example output:
	```bash
	./scripts/verify_big_core_allocation.sh
	# Shows which daemons are on big cores (4-7) and their priorities
	```
- **`disable-powersave.py`**: Disables power-saving features on the device to ensure maximum performance. Run at boot or before starting OpenPilot:
	```bash
	python3 ./scripts/disable-powersave.py
	```
- **`reset_eop_params.sh`**: Backs up and wipes `/data/params` after a migration (e.g., EOP_ → EP_ prefix). Use with caution:
	```bash
	./scripts/reset_eop_params.sh
	# Prompts for confirmation, backs up, wipes, and recreates params dir
	```

**Action:**
- Use these scripts for setup, validation, and troubleshooting on Orange Pi 5.
- Automate their invocation in deployment scripts or CI pipelines for consistent bring-up and validation.

---

### Porting/Validation Checklist (for Orange Pi 5)

- [ ] All required `.rknn` models present and validated in `selfdrive/modeld/models/`
- [ ] NPU utilization ≤ 6.0 TOPS (see model inventory)
- [ ] Camera HAL environment configured (`setup_camera_hal_env.sh`)
- [ ] Daemon core affinity and priorities verified (`verify_big_core_allocation.sh`)
- [ ] Power-saving disabled (`disable-powersave.py`)
- [ ] Secure host lockdown and firmware flashing as needed (`rk3588_secure_host.sh`)
- [ ] Params reset after migration (`reset_eop_params.sh`)
- [ ] Build and release scripts tested (`build_devel.sh`, `build_release.sh`)

---

**Tip:** For automation, chain these scripts in your deployment pipeline and validate each step with log output. For new repo ports, copy this checklist and adapt as needed.

## 🟦 Step 2: Camera HAL & Daemon Migration
**Unified interface for all daemons:**

```python
from common.hardware.rk3588.camera import (
	OX03C10Camera, CSICameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
```

**USB Camera Example:**
```python
from common.hardware.rk3588.camera import (
	UVCCamera, USBCameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
camera_config = USBCameraConfig(
	device_path=device_path,
	width=width, height=height, pixel_format=V4L2PixelFormat.YUYV,
	fps=fps, usb_port="auto", uvc_version="1.5",
	---
	# 🧠 Orange Pi 5 Minimal OpenPilot Porting Guide (IMX415, Vision+Policy Only)

	This file is a **maximal, AI-automatable knowledge base** for porting any OpenPilot-based repo to Orange Pi 5 (RK3588) with only a single IMX415 front camera and only the `driving_vision.rknn` and `driving_policy.rknn` models. All other features (driver monitoring, stereo, Bluetooth, voice, grid, ground, track, predict, side cameras, etc.) are disabled or removed. Use this as the only reference for automation or manual porting.

	---

	## 1. Directory Map: What to Keep, What to Remove

	**Keep/Adapt:**
	- `common/hardware/rk3588/` (all files, especially `camera/`, `npu.py`, `rga.py`, `hardware.py`)
	- `selfdrive/camerad/` (only for IMX415 front camera)
	- `selfdrive/modeld/` (only `driving_vision.rknn`, `driving_policy.rknn`, and their wrappers)
	- `selfdrive/controls/` (only `controlsd.py`, `plannerd.py`, `radard.py`)
	- `selfdrive/car/` (only your car's interface and CAN parser)
	- `cereal/` (all, for Cap'n Proto messaging)
	- `system/manager/`, `system/hardware/`, `system/camerad/` (minimal, see below)
	- `scripts/` (only `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`)

	**Remove/Disable:**
	- All `monitoringd`, `stereod`, `externald`, `gridd`, `groundd`, `trackd`, `predictd`, `bluetoothd`, `voice`, `side cameras`, `driver monitoring`, `USB cameras`, `mapd`, `joystickd`, `elm327d`, `webjoystick`, `plated`, `snapd`, `loopd`, `crashd`, `debrisd`, `test/` folders not needed for your car.

	---

	## 2. Hardware Detection: RK3588-Only

	**File:** `system/hardware/__init__.py`

	```python
	from openpilot.common.hardware.rk3588.hardware import RK3588Hardware
	HARDWARE = RK3588Hardware(detected=True)
	RK3588 = True
	PC = False
	```

	**Remove all other hardware detection logic.**

	---

	## 3. Camera HAL: IMX415 Front Camera Only

	**File:** `common/hardware/rk3588/camera/csi.py`

	```python
	from common.hardware.rk3588.camera.v4l2 import V4L2Camera, V4L2Config, V4L2PixelFormat
	from common.hardware.rk3588.camera.sensors import IMX415Driver

	config = V4L2Config(
			device_path="/dev/video0",  # IMX415 front camera
			width=1920, height=1080, pixel_format=V4L2PixelFormat.YUYV,
			fps=30, memory_strategy="default"
	)
	camera = V4L2Camera(config)
	sensor = IMX415Driver(config.device_path)
	sensor.initialize()
	```

	**Remove all OX03C10, OS04C10, USB, and stereo camera logic.**

	---

	## 4. Model Inventory: Only Vision + Policy

	**Directory:** `selfdrive/modeld/models/`

	**Keep only:**
	- `driving_vision.rknn`
	- `driving_policy.rknn`

	**Remove all other models (YOLO, segmentation, headpose, etc.).**

	---

	## 5. Model Loading: Minimal RKNN Wrappers

	**File:** `selfdrive/modeld/vision/driving_vision_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingVisionRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load vision RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init vision RKNN runtime"
			def infer(self, img):
					return self.rknn.inference(inputs=[img])
	```

	**File:** `selfdrive/modeld/vision/driving_policy_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingPolicyRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load policy RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init policy RKNN runtime"
			def infer(self, features):
					return self.rknn.inference(inputs=[features])
	```

	---

	## 6. Minimal modeld: Only Vision + Policy

	**File:** `selfdrive/modeld/modeld.py` (simplified)

	```python
	from selfdrive.modeld.vision.driving_vision_rknn import DrivingVisionRKNN
	from selfdrive.modeld.vision.driving_policy_rknn import DrivingPolicyRKNN

	vision = DrivingVisionRKNN("models/driving_vision.rknn")
	policy = DrivingPolicyRKNN("models/driving_policy.rknn")

	# Main loop: get camera frame, run vision, then policy, publish result
	while True:
			img = get_camera_frame()  # Use IMX415 camera only
			vision_out = vision.infer(img)
			policy_out = policy.infer(vision_out)
			publish(policy_out)
	```

	---

	## 7. Process Registry: Only Required Daemons

	**File:** `system/manager/process_config.py`

	```python
	from openpilot.system.manager.process import PythonProcess, NativeProcess

	procs = [
		PythonProcess("camerad", "selfdrive.camerad.camerad", always_run),
		PythonProcess("modeld", "selfdrive.modeld.modeld", always_run),
		PythonProcess("controlsd", "selfdrive.controls.controlsd", always_run),
		PythonProcess("plannerd", "selfdrive.controls.plannerd", always_run),
		PythonProcess("radard", "selfdrive.controls.radard", always_run),
		PythonProcess("car", "selfdrive.car.card", always_run),
	]
	managed_processes = {p.name: p for p in procs}
	```

	**Remove all other processes (monitoringd, stereod, externald, bluetoothd, etc.).**

	---

	## 8. Controls: Minimal

	**File:** `selfdrive/controls/controlsd.py` (keep only core control loop, remove all references to unused features)

	**File:** `selfdrive/controls/plannerd.py`, `selfdrive/controls/radard.py` (keep only core logic)

	---

	## 9. Car Interface: Minimal

	**File:** `selfdrive/car/<yourcar>/interface.py` (implement only CAN parsing and actuator commands for your car)

	---

	## 10. Messaging: Cereal

	**Keep all Cap'n Proto schemas and messaging code in `cereal/`.**

	---

	## 11. Scripts: Only What You Need

	- `scripts/setup_camera_hal_env.sh` (run before launching)
	- `scripts/disable-powersave.py` (run at boot)
	- `scripts/verify_big_core_allocation.sh` (validate core affinity)

	---

	## 12. Build & Run

	**Build:**
	```bash
	./release/build_devel.sh
	# or
	./release/build_release.sh
	```

	**Run:**
	```bash
	source ./scripts/setup_camera_hal_env.sh
	python3 -m selfdrive.camerad.camerad &
	python3 -m selfdrive.modeld.modeld &
	python3 -m selfdrive.controls.controlsd &
	python3 -m selfdrive.controls.plannerd &
	python3 -m selfdrive.controls.radard &
	python3 -m selfdrive.car.card &
	```

	---

	## 13. Porting/Validation Checklist (AI/Automation Ready)

	- [ ] Only `driving_vision.rknn` and `driving_policy.rknn` present in `selfdrive/modeld/models/`
	- [ ] Only IMX415 front camera enabled (no wide, stereo, USB, or driver monitoring)
	- [ ] Only Orange Pi 5 hardware detection logic present
	- [ ] Only required daemons enabled in process registry
	- [ ] All unused features/processes removed or disabled
	- [ ] Camera HAL and IMX415 driver validated
	- [ ] Controls and car interface minimal and correct
	- [ ] Scripts for camera HAL and power validated
	- [ ] Build and run scripts tested

	---

	## 🟧 Stability & Safety Guard Checklist (AI/Manual Porting)

	**Track and implement these before any road testing or production deployment.**

### Critical Safety/Robustness Fixes
- [ ] Replace all `assert` with `raise RuntimeError` in `rknn_runner.py` (asserts can be disabled, raising is always safe)
- [ ] Add null check on RKNN `outputs_get()` before indexing (raise if None)
- [ ] Add `np.isfinite()` guard on all NPU outputs before parsing (raise if NaN/Inf)
- [ ] Verify policy input key order matches RKNN model input order at startup (log both orders)
- [ ] Ensure `release()` is called on RKNNRunner at shutdown (use `atexit` or `try/finally` in modeld)
- [ ] Add camera reconnect/retry loop in `camera.py` (for CSI/USB disconnect resilience)
- [ ] Verify A76 core numbering: `cat /sys/devices/system/cpu/cpu{4..7}/cpufreq/cpuinfo_max_freq` (should be 2400000 for big cores)
- [ ] Add/verify heatsink + fan for sustained NPU performance (thermal throttling can cause >30ms inference)
- [ ] Broaden `/dev/rknpu0` check to also match `/dev/rknpu` (kernel naming varies)
- [ ] Add `__del__` guard in RKNNRunner to prevent double-release segfaults

### Operational/Deployment Gaps
- [ ] Add `rknn-toolkit-lite2` install instructions to setup scripts (cannot be in pyproject.toml, not on PyPI)
- [ ] Add thermal warning in UI/log if modelExecutionTime > 0.025s (optional, but recommended)
- [ ] Track and log all stability/safety checklist items in CI or deployment pipeline

---

## 🟧 Stability & Safety Guard Reference (Details)

**1. RKNN Error Handling:**
  - Replace all `assert` with `raise RuntimeError` in `rknn_runner.py`.
  - Add null check on `outputs_get()` before indexing.
  - Add `np.isfinite()` guard on all NPU outputs before parsing.

**2. Policy Input Order:**
  - At startup, print/log both the policy input dict key order and the RKNN model's expected input order. Confirm they match.

**3. RKNN Resource Management:**
  - Ensure `release()` is always called on RKNNRunner at shutdown (use `atexit` or `try/finally`).
  - Add `__del__` guard to RKNNRunner to prevent double-release segfaults.

**4. Camera Robustness:**
  - Add a reconnect/retry loop in `camera.py` for CSI/USB disconnects.

**5. Core Affinity & Thermal:**
  - Verify A76 core numbering on your kernel (should be 2400000 kHz for big cores).
  - Add/verify heatsink + fan for sustained NPU performance.
  - Add thermal warning in UI/log if modelExecutionTime > 0.025s.

**6. NPU Device Node Detection:**
  - Broaden `/dev/rknpu0` check to also match `/dev/rknpu`.

**7. RKNN Dependency:**
  - Add `rknn-toolkit-lite2` install instructions to setup scripts (manual pip install from Rockchip wheel).

**8. CI/Automation:**
  - Track and log all stability/safety checklist items in CI or deployment pipeline.

---

## 🟩 Final Checklist: What to Extract and Document in learn.md

- [ ] List all required `.rknn` models and their exact paths (e.g., `selfdrive/modeld/models/driving_vision.rknn`, `driving_policy.rknn`)
- [ ] Document all environment variables and feature flags needed (e.g., `USE_WEBCAM=1`, `NO_DM=1`, `ROAD_CAM` auto-detect)
- [ ] Summarize all process/daemon requirements (minimal list: `camerad`, `modeld`, `controlsd`, `plannerd`, `radard`, `card`, `socketd`)
- [ ] Specify all hardware abstraction and platform detection logic (e.g., RK3588 detection, NPU device node checks)
- [ ] List all scripts and utilities required for setup, validation, and deployment (e.g., `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`, `rk3588_secure_host.sh`)
- [ ] Document all code changes or diffs needed for porting (e.g., RKNN runner, modeld.py changes, SConscript skips, launch_env.sh env vars)
- [ ] Include all stability and safety guard checklist items (as above)
- [ ] Note all files/folders to keep, adapt, or remove (directory map)
- [ ] Summarize all tuning/parameter changes (e.g., camera focal length, DT_MDL, service frequencies)
- [ ] Reference all historical commits or diffs that must be replicated for new ports
- [ ] List all manual install steps (e.g., `rknn-toolkit-lite2` wheel, Mali driver, IMU wiring if used)
- [ ] Add any additional notes for automation, CI, or AI-driven porting

---

## 🟨 Orange Pi 5 Porting: openpilot, release, scripts Folders

### openpilot
**Purpose:** Main process tree (selfdrive, controls, modeld, car, etc.)

**Orange Pi 5 relevance:**
- `selfdrive/modeld/models/` contains `.rknn` models for RK3588 NPU. These must match your NPU budget (see model inventory and NPU_AND_MODELS.md).
- `selfdrive/modeld/README.md` and `docs/NPU_AND_MODELS.md` describe model requirements, NPU utilization, and conversion steps.
- `selfdrive/camerad/` and `common/hardware/rk3588/` handle all camera and hardware specifics (CSI, RGA, NPU, GPIO, PCIe accel).

**Action:**
- Ensure all required `.rknn` models are present in `selfdrive/modeld/models/`.
- Use `tools/rknn/convert_detection_models.sh` on a desktop (x86_64) to convert ONNX models to `.rknn` for RK3588.
- Validate NPU utilization does not exceed 6.0 TOPS (see model inventory table).
- For new models, update the inventory and test with `common/hardware/rk3588/npu.py`.

---

### release
**Purpose:** Build and release scripts for packaging and deployment.

**Orange Pi 5 relevance:**
- Use `build_devel.sh` or `build_release.sh` for packaging the stack for Orange Pi 5.
- No RK3588-specific logic is needed; scripts are platform-agnostic.

**Action:**
- Run `./release/build_devel.sh` for development builds.
- Run `./release/build_release.sh` for production images.
- Validate output images on Orange Pi 5 hardware.

---

### scripts
**Purpose:** Utility scripts for deployment, camera HAL, power management, and validation.

**Orange Pi 5 relevance:**
- **`rk3588_secure_host.sh`**: Secure lockdown, OpenBLT flashing, and SSH lockdown for RK3588 hosts. Use for production deployment and firmware flashing. Example usage:
	```bash
	./scripts/rk3588_secure_host.sh --lock
	./scripts/rk3588_secure_host.sh --unlock
	./scripts/rk3588_secure_host.sh --status
	./scripts/rk3588_secure_host.sh --flash --image firmware.srec
	```
- **`setup_camera_hal_env.sh`**: Sets up environment variables and system settings for the unified Camera HAL. Run before launching camera daemons to ensure zero-copy and high-performance operation.
	```bash
	source ./scripts/setup_camera_hal_env.sh
	```
- **`verify_big_core_allocation.sh`**: Verifies that safety-critical daemons (e.g., `controlsd`, `modeld`, `stereod`) are running on the correct RK3588 big CPU cores with proper priorities. Example output:
	```bash
	./scripts/verify_big_core_allocation.sh
	# Shows which daemons are on big cores (4-7) and their priorities
	```
- **`disable-powersave.py`**: Disables power-saving features on the device to ensure maximum performance. Run at boot or before starting OpenPilot:
	```bash
	python3 ./scripts/disable-powersave.py
	```
- **`reset_eop_params.sh`**: Backs up and wipes `/data/params` after a migration (e.g., EOP_ → EP_ prefix). Use with caution:
	```bash
	./scripts/reset_eop_params.sh
	# Prompts for confirmation, backs up, wipes, and recreates params dir
	```

**Action:**
- Use these scripts for setup, validation, and troubleshooting on Orange Pi 5.
- Automate their invocation in deployment scripts or CI pipelines for consistent bring-up and validation.

---

### Porting/Validation Checklist (for Orange Pi 5)

- [ ] All required `.rknn` models present and validated in `selfdrive/modeld/models/`
- [ ] NPU utilization ≤ 6.0 TOPS (see model inventory)
- [ ] Camera HAL environment configured (`setup_camera_hal_env.sh`)
- [ ] Daemon core affinity and priorities verified (`verify_big_core_allocation.sh`)
- [ ] Power-saving disabled (`disable-powersave.py`)
- [ ] Secure host lockdown and firmware flashing as needed (`rk3588_secure_host.sh`)
- [ ] Params reset after migration (`reset_eop_params.sh`)
- [ ] Build and release scripts tested (`build_devel.sh`, `build_release.sh`)

---

**Tip:** For automation, chain these scripts in your deployment pipeline and validate each step with log output. For new repo ports, copy this checklist and adapt as needed.

## 🟦 Step 2: Camera HAL & Daemon Migration
**Unified interface for all daemons:**

```python
from common.hardware.rk3588.camera import (
	OX03C10Camera, CSICameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
```

**USB Camera Example:**
```python
from common.hardware.rk3588.camera import (
	UVCCamera, USBCameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
camera_config = USBCameraConfig(
	device_path=device_path,
	width=width, height=height, pixel_format=V4L2PixelFormat.YUYV,
	fps=fps, usb_port="auto", uvc_version="1.5",
	---
	# 🧠 Orange Pi 5 Minimal OpenPilot Porting Guide (IMX415, Vision+Policy Only)

	This file is a **maximal, AI-automatable knowledge base** for porting any OpenPilot-based repo to Orange Pi 5 (RK3588) with only a single IMX415 front camera and only the `driving_vision.rknn` and `driving_policy.rknn` models. All other features (driver monitoring, stereo, Bluetooth, voice, grid, ground, track, predict, side cameras, etc.) are disabled or removed. Use this as the only reference for automation or manual porting.

	---

	## 1. Directory Map: What to Keep, What to Remove

	**Keep/Adapt:**
	- `common/hardware/rk3588/` (all files, especially `camera/`, `npu.py`, `rga.py`, `hardware.py`)
	- `selfdrive/camerad/` (only for IMX415 front camera)
	- `selfdrive/modeld/` (only `driving_vision.rknn`, `driving_policy.rknn`, and their wrappers)
	- `selfdrive/controls/` (only `controlsd.py`, `plannerd.py`, `radard.py`)
	- `selfdrive/car/` (only your car's interface and CAN parser)
	- `cereal/` (all, for Cap'n Proto messaging)
	- `system/manager/`, `system/hardware/`, `system/camerad/` (minimal, see below)
	- `scripts/` (only `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`)

	**Remove/Disable:**
	- All `monitoringd`, `stereod`, `externald`, `gridd`, `groundd`, `trackd`, `predictd`, `bluetoothd`, `voice`, `side cameras`, `driver monitoring`, `USB cameras`, `mapd`, `joystickd`, `elm327d`, `webjoystick`, `plated`, `snapd`, `loopd`, `crashd`, `debrisd`, `test/` folders not needed for your car.

	---

	## 2. Hardware Detection: RK3588-Only

	**File:** `system/hardware/__init__.py`

	```python
	from openpilot.common.hardware.rk3588.hardware import RK3588Hardware
	HARDWARE = RK3588Hardware(detected=True)
	RK3588 = True
	PC = False
	```

	**Remove all other hardware detection logic.**

	---

	## 3. Camera HAL: IMX415 Front Camera Only

	**File:** `common/hardware/rk3588/camera/csi.py`

	```python
	from common.hardware.rk3588.camera.v4l2 import V4L2Camera, V4L2Config, V4L2PixelFormat
	from common.hardware.rk3588.camera.sensors import IMX415Driver

	config = V4L2Config(
			device_path="/dev/video0",  # IMX415 front camera
			width=1920, height=1080, pixel_format=V4L2PixelFormat.YUYV,
			fps=30, memory_strategy="default"
	)
	camera = V4L2Camera(config)
	sensor = IMX415Driver(config.device_path)
	sensor.initialize()
	```

	**Remove all OX03C10, OS04C10, USB, and stereo camera logic.**

	---

	## 4. Model Inventory: Only Vision + Policy

	**Directory:** `selfdrive/modeld/models/`

	**Keep only:**
	- `driving_vision.rknn`
	- `driving_policy.rknn`

	**Remove all other models (YOLO, segmentation, headpose, etc.).**

	---

	## 5. Model Loading: Minimal RKNN Wrappers

	**File:** `selfdrive/modeld/vision/driving_vision_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingVisionRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load vision RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init vision RKNN runtime"
			def infer(self, img):
					return self.rknn.inference(inputs=[img])
	```

	**File:** `selfdrive/modeld/vision/driving_policy_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingPolicyRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load policy RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init policy RKNN runtime"
			def infer(self, features):
					return self.rknn.inference(inputs=[features])
	```

	---

	## 6. Minimal modeld: Only Vision + Policy

	**File:** `selfdrive/modeld/modeld.py` (simplified)

	```python
	from selfdrive.modeld.vision.driving_vision_rknn import DrivingVisionRKNN
	from selfdrive.modeld.vision.driving_policy_rknn import DrivingPolicyRKNN

	vision = DrivingVisionRKNN("models/driving_vision.rknn")
	policy = DrivingPolicyRKNN("models/driving_policy.rknn")

	# Main loop: get camera frame, run vision, then policy, publish result
	while True:
			img = get_camera_frame()  # Use IMX415 camera only
			vision_out = vision.infer(img)
			policy_out = policy.infer(vision_out)
			publish(policy_out)
	```

	---

	## 7. Process Registry: Only Required Daemons

	**File:** `system/manager/process_config.py`

	```python
	from openpilot.system.manager.process import PythonProcess, NativeProcess

	procs = [
		PythonProcess("camerad", "selfdrive.camerad.camerad", always_run),
		PythonProcess("modeld", "selfdrive.modeld.modeld", always_run),
		PythonProcess("controlsd", "selfdrive.controls.controlsd", always_run),
		PythonProcess("plannerd", "selfdrive.controls.plannerd", always_run),
		PythonProcess("radard", "selfdrive.controls.radard", always_run),
		PythonProcess("car", "selfdrive.car.card", always_run),
	]
	managed_processes = {p.name: p for p in procs}
	```

	**Remove all other processes (monitoringd, stereod, externald, bluetoothd, etc.).**

	---

	## 8. Controls: Minimal

	**File:** `selfdrive/controls/controlsd.py` (keep only core control loop, remove all references to unused features)

	**File:** `selfdrive/controls/plannerd.py`, `selfdrive/controls/radard.py` (keep only core logic)

	---

	## 9. Car Interface: Minimal

	**File:** `selfdrive/car/<yourcar>/interface.py` (implement only CAN parsing and actuator commands for your car)

	---

	## 10. Messaging: Cereal

	**Keep all Cap'n Proto schemas and messaging code in `cereal/`.**

	---

	## 11. Scripts: Only What You Need

	- `scripts/setup_camera_hal_env.sh` (run before launching)
	- `scripts/disable-powersave.py` (run at boot)
	- `scripts/verify_big_core_allocation.sh` (validate core affinity)

	---

	## 12. Build & Run

	**Build:**
	```bash
	./release/build_devel.sh
	# or
	./release/build_release.sh
	```

	**Run:**
	```bash
	source ./scripts/setup_camera_hal_env.sh
	python3 -m selfdrive.camerad.camerad &
	python3 -m selfdrive.modeld.modeld &
	python3 -m selfdrive.controls.controlsd &
	python3 -m selfdrive.controls.plannerd &
	python3 -m selfdrive.controls.radard &
	python3 -m selfdrive.car.card &
	```

	---

	## 13. Porting/Validation Checklist (AI/Automation Ready)

	- [ ] Only `driving_vision.rknn` and `driving_policy.rknn` present in `selfdrive/modeld/models/`
	- [ ] Only IMX415 front camera enabled (no wide, stereo, USB, or driver monitoring)
	- [ ] Only Orange Pi 5 hardware detection logic present
	- [ ] Only required daemons enabled in process registry
	- [ ] All unused features/processes removed or disabled
	- [ ] Camera HAL and IMX415 driver validated
	- [ ] Controls and car interface minimal and correct
	- [ ] Scripts for camera HAL and power validated
	- [ ] Build and run scripts tested

	---

	## 🟧 Stability & Safety Guard Checklist (AI/Manual Porting)

	**Track and implement these before any road testing or production deployment.**

### Critical Safety/Robustness Fixes
- [ ] Replace all `assert` with `raise RuntimeError` in `rknn_runner.py` (asserts can be disabled, raising is always safe)
- [ ] Add null check on RKNN `outputs_get()` before indexing (raise if None)
- [ ] Add `np.isfinite()` guard on all NPU outputs before parsing (raise if NaN/Inf)
- [ ] Verify policy input key order matches RKNN model input order at startup (log both orders)
- [ ] Ensure `release()` is called on RKNNRunner at shutdown (use `atexit` or `try/finally` in modeld)
- [ ] Add camera reconnect/retry loop in `camera.py` (for CSI/USB disconnect resilience)
- [ ] Verify A76 core numbering: `cat /sys/devices/system/cpu/cpu{4..7}/cpufreq/cpuinfo_max_freq` (should be 2400000 for big cores)
- [ ] Add/verify heatsink + fan for sustained NPU performance (thermal throttling can cause >30ms inference)
- [ ] Broaden `/dev/rknpu0` check to also match `/dev/rknpu` (kernel naming varies)
- [ ] Add `__del__` guard in RKNNRunner to prevent double-release segfaults

### Operational/Deployment Gaps
- [ ] Add `rknn-toolkit-lite2` install instructions to setup scripts (cannot be in pyproject.toml, not on PyPI)
- [ ] Add thermal warning in UI/log if modelExecutionTime > 0.025s (optional, but recommended)
- [ ] Track and log all stability/safety checklist items in CI or deployment pipeline

---

## 🟧 Stability & Safety Guard Reference (Details)

**1. RKNN Error Handling:**
  - Replace all `assert` with `raise RuntimeError` in `rknn_runner.py`.
  - Add null check on `outputs_get()` before indexing.
  - Add `np.isfinite()` guard on all NPU outputs before parsing.

**2. Policy Input Order:**
  - At startup, print/log both the policy input dict key order and the RKNN model's expected input order. Confirm they match.

**3. RKNN Resource Management:**
  - Ensure `release()` is always called on RKNNRunner at shutdown (use `atexit` or `try/finally`).
  - Add `__del__` guard to RKNNRunner to prevent double-release segfaults.

**4. Camera Robustness:**
  - Add a reconnect/retry loop in `camera.py` for CSI/USB disconnects.

**5. Core Affinity & Thermal:**
  - Verify A76 core numbering on your kernel (should be 2400000 kHz for big cores).
  - Add/verify heatsink + fan for sustained NPU performance.
  - Add thermal warning in UI/log if modelExecutionTime > 0.025s.

**6. NPU Device Node Detection:**
  - Broaden `/dev/rknpu0` check to also match `/dev/rknpu`.

**7. RKNN Dependency:**
  - Add `rknn-toolkit-lite2` install instructions to setup scripts (manual pip install from Rockchip wheel).

**8. CI/Automation:**
  - Track and log all stability/safety checklist items in CI or deployment pipeline.

---

## 🟩 Final Checklist: What to Extract and Document in learn.md

- [ ] List all required `.rknn` models and their exact paths (e.g., `selfdrive/modeld/models/driving_vision.rknn`, `driving_policy.rknn`)
- [ ] Document all environment variables and feature flags needed (e.g., `USE_WEBCAM=1`, `NO_DM=1`, `ROAD_CAM` auto-detect)
- [ ] Summarize all process/daemon requirements (minimal list: `camerad`, `modeld`, `controlsd`, `plannerd`, `radard`, `card`, `socketd`)
- [ ] Specify all hardware abstraction and platform detection logic (e.g., RK3588 detection, NPU device node checks)
- [ ] List all scripts and utilities required for setup, validation, and deployment (e.g., `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`, `rk3588_secure_host.sh`)
- [ ] Document all code changes or diffs needed for porting (e.g., RKNN runner, modeld.py changes, SConscript skips, launch_env.sh env vars)
- [ ] Include all stability and safety guard checklist items (as above)
- [ ] Note all files/folders to keep, adapt, or remove (directory map)
- [ ] Summarize all tuning/parameter changes (e.g., camera focal length, DT_MDL, service frequencies)
- [ ] Reference all historical commits or diffs that must be replicated for new ports
- [ ] List all manual install steps (e.g., `rknn-toolkit-lite2` wheel, Mali driver, IMU wiring if used)
- [ ] Add any additional notes for automation, CI, or AI-driven porting

---

## 🟨 Orange Pi 5 Porting: openpilot, release, scripts Folders

### openpilot
**Purpose:** Main process tree (selfdrive, controls, modeld, car, etc.)

**Orange Pi 5 relevance:**
- `selfdrive/modeld/models/` contains `.rknn` models for RK3588 NPU. These must match your NPU budget (see model inventory and NPU_AND_MODELS.md).
- `selfdrive/modeld/README.md` and `docs/NPU_AND_MODELS.md` describe model requirements, NPU utilization, and conversion steps.
- `selfdrive/camerad/` and `common/hardware/rk3588/` handle all camera and hardware specifics (CSI, RGA, NPU, GPIO, PCIe accel).

**Action:**
- Ensure all required `.rknn` models are present in `selfdrive/modeld/models/`.
- Use `tools/rknn/convert_detection_models.sh` on a desktop (x86_64) to convert ONNX models to `.rknn` for RK3588.
- Validate NPU utilization does not exceed 6.0 TOPS (see model inventory table).
- For new models, update the inventory and test with `common/hardware/rk3588/npu.py`.

---

### release
**Purpose:** Build and release scripts for packaging and deployment.

**Orange Pi 5 relevance:**
- Use `build_devel.sh` or `build_release.sh` for packaging the stack for Orange Pi 5.
- No RK3588-specific logic is needed; scripts are platform-agnostic.

**Action:**
- Run `./release/build_devel.sh` for development builds.
- Run `./release/build_release.sh` for production images.
- Validate output images on Orange Pi 5 hardware.

---

### scripts
**Purpose:** Utility scripts for deployment, camera HAL, power management, and validation.

**Orange Pi 5 relevance:**
- **`rk3588_secure_host.sh`**: Secure lockdown, OpenBLT flashing, and SSH lockdown for RK3588 hosts. Use for production deployment and firmware flashing. Example usage:
	```bash
	./scripts/rk3588_secure_host.sh --lock
	./scripts/rk3588_secure_host.sh --unlock
	./scripts/rk3588_secure_host.sh --status
	./scripts/rk3588_secure_host.sh --flash --image firmware.srec
	```
- **`setup_camera_hal_env.sh`**: Sets up environment variables and system settings for the unified Camera HAL. Run before launching camera daemons to ensure zero-copy and high-performance operation.
	```bash
	source ./scripts/setup_camera_hal_env.sh
	```
- **`verify_big_core_allocation.sh`**: Verifies that safety-critical daemons (e.g., `controlsd`, `modeld`, `stereod`) are running on the correct RK3588 big CPU cores with proper priorities. Example output:
	```bash
	./scripts/verify_big_core_allocation.sh
	# Shows which daemons are on big cores (4-7) and their priorities
	```
- **`disable-powersave.py`**: Disables power-saving features on the device to ensure maximum performance. Run at boot or before starting OpenPilot:
	```bash
	python3 ./scripts/disable-powersave.py
	```
- **`reset_eop_params.sh`**: Backs up and wipes `/data/params` after a migration (e.g., EOP_ → EP_ prefix). Use with caution:
	```bash
	./scripts/reset_eop_params.sh
	# Prompts for confirmation, backs up, wipes, and recreates params dir
	```

**Action:**
- Use these scripts for setup, validation, and troubleshooting on Orange Pi 5.
- Automate their invocation in deployment scripts or CI pipelines for consistent bring-up and validation.

---

### Porting/Validation Checklist (for Orange Pi 5)

- [ ] All required `.rknn` models present and validated in `selfdrive/modeld/models/`
- [ ] NPU utilization ≤ 6.0 TOPS (see model inventory)
- [ ] Camera HAL environment configured (`setup_camera_hal_env.sh`)
- [ ] Daemon core affinity and priorities verified (`verify_big_core_allocation.sh`)
- [ ] Power-saving disabled (`disable-powersave.py`)
- [ ] Secure host lockdown and firmware flashing as needed (`rk3588_secure_host.sh`)
- [ ] Params reset after migration (`reset_eop_params.sh`)
- [ ] Build and release scripts tested (`build_devel.sh`, `build_release.sh`)

---

**Tip:** For automation, chain these scripts in your deployment pipeline and validate each step with log output. For new repo ports, copy this checklist and adapt as needed.

## 🟦 Step 2: Camera HAL & Daemon Migration
**Unified interface for all daemons:**

```python
from common.hardware.rk3588.camera import (
	OX03C10Camera, CSICameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
```

**USB Camera Example:**
```python
from common.hardware.rk3588.camera import (
	UVCCamera, USBCameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
camera_config = USBCameraConfig(
	device_path=device_path,
	width=width, height=height, pixel_format=V4L2PixelFormat.YUYV,
	fps=fps, usb_port="auto", uvc_version="1.5",
	---
	# 🧠 Orange Pi 5 Minimal OpenPilot Porting Guide (IMX415, Vision+Policy Only)

	This file is a **maximal, AI-automatable knowledge base** for porting any OpenPilot-based repo to Orange Pi 5 (RK3588) with only a single IMX415 front camera and only the `driving_vision.rknn` and `driving_policy.rknn` models. All other features (driver monitoring, stereo, Bluetooth, voice, grid, ground, track, predict, side cameras, etc.) are disabled or removed. Use this as the only reference for automation or manual porting.

	---

	## 1. Directory Map: What to Keep, What to Remove

	**Keep/Adapt:**
	- `common/hardware/rk3588/` (all files, especially `camera/`, `npu.py`, `rga.py`, `hardware.py`)
	- `selfdrive/camerad/` (only for IMX415 front camera)
	- `selfdrive/modeld/` (only `driving_vision.rknn`, `driving_policy.rknn`, and their wrappers)
	- `selfdrive/controls/` (only `controlsd.py`, `plannerd.py`, `radard.py`)
	- `selfdrive/car/` (only your car's interface and CAN parser)
	- `cereal/` (all, for Cap'n Proto messaging)
	- `system/manager/`, `system/hardware/`, `system/camerad/` (minimal, see below)
	- `scripts/` (only `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`)

	**Remove/Disable:**
	- All `monitoringd`, `stereod`, `externald`, `gridd`, `groundd`, `trackd`, `predictd`, `bluetoothd`, `voice`, `side cameras`, `driver monitoring`, `USB cameras`, `mapd`, `joystickd`, `elm327d`, `webjoystick`, `plated`, `snapd`, `loopd`, `crashd`, `debrisd`, `test/` folders not needed for your car.

	---

	## 2. Hardware Detection: RK3588-Only

	**File:** `system/hardware/__init__.py`

	```python
	from openpilot.common.hardware.rk3588.hardware import RK3588Hardware
	HARDWARE = RK3588Hardware(detected=True)
	RK3588 = True
	PC = False
	```

	**Remove all other hardware detection logic.**

	---

	## 3. Camera HAL: IMX415 Front Camera Only

	**File:** `common/hardware/rk3588/camera/csi.py`

	```python
	from common.hardware.rk3588.camera.v4l2 import V4L2Camera, V4L2Config, V4L2PixelFormat
	from common.hardware.rk3588.camera.sensors import IMX415Driver

	config = V4L2Config(
			device_path="/dev/video0",  # IMX415 front camera
			width=1920, height=1080, pixel_format=V4L2PixelFormat.YUYV,
			fps=30, memory_strategy="default"
	)
	camera = V4L2Camera(config)
	sensor = IMX415Driver(config.device_path)
	sensor.initialize()
	```

	**Remove all OX03C10, OS04C10, USB, and stereo camera logic.**

	---

	## 4. Model Inventory: Only Vision + Policy

	**Directory:** `selfdrive/modeld/models/`

	**Keep only:**
	- `driving_vision.rknn`
	- `driving_policy.rknn`

	**Remove all other models (YOLO, segmentation, headpose, etc.).**

	---

	## 5. Model Loading: Minimal RKNN Wrappers

	**File:** `selfdrive/modeld/vision/driving_vision_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingVisionRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load vision RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init vision RKNN runtime"
			def infer(self, img):
					return self.rknn.inference(inputs=[img])
	```

	**File:** `selfdrive/modeld/vision/driving_policy_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingPolicyRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load policy RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init policy RKNN runtime"
			def infer(self, features):
					return self.rknn.inference(inputs=[features])
	```

	---

	## 6. Minimal modeld: Only Vision + Policy

	**File:** `selfdrive/modeld/modeld.py` (simplified)

	```python
	from selfdrive.modeld.vision.driving_vision_rknn import DrivingVisionRKNN
	from selfdrive.modeld.vision.driving_policy_rknn import DrivingPolicyRKNN

	vision = DrivingVisionRKNN("models/driving_vision.rknn")
	policy = DrivingPolicyRKNN("models/driving_policy.rknn")

	# Main loop: get camera frame, run vision, then policy, publish result
	while True:
			img = get_camera_frame()  # Use IMX415 camera only
			vision_out = vision.infer(img)
			policy_out = policy.infer(vision_out)
			publish(policy_out)
	```

	---

	## 7. Process Registry: Only Required Daemons

	**File:** `system/manager/process_config.py`

	```python
	from openpilot.system.manager.process import PythonProcess, NativeProcess

	procs = [
		PythonProcess("camerad", "selfdrive.camerad.camerad", always_run),
		PythonProcess("modeld", "selfdrive.modeld.modeld", always_run),
		PythonProcess("controlsd", "selfdrive.controls.controlsd", always_run),
		PythonProcess("plannerd", "selfdrive.controls.plannerd", always_run),
		PythonProcess("radard", "selfdrive.controls.radard", always_run),
		PythonProcess("car", "selfdrive.car.card", always_run),
	]
	managed_processes = {p.name: p for p in procs}
	```

	**Remove all other processes (monitoringd, stereod, externald, bluetoothd, etc.).**

	---

	## 8. Controls: Minimal

	**File:** `selfdrive/controls/controlsd.py` (keep only core control loop, remove all references to unused features)

	**File:** `selfdrive/controls/plannerd.py`, `selfdrive/controls/radard.py` (keep only core logic)

	---

	## 9. Car Interface: Minimal

	**File:** `selfdrive/car/<yourcar>/interface.py` (implement only CAN parsing and actuator commands for your car)

	---

	## 10. Messaging: Cereal

	**Keep all Cap'n Proto schemas and messaging code in `cereal/`.**

	---

	## 11. Scripts: Only What You Need

	- `scripts/setup_camera_hal_env.sh` (run before launching)
	- `scripts/disable-powersave.py` (run at boot)
	- `scripts/verify_big_core_allocation.sh` (validate core affinity)

	---

	## 12. Build & Run

	**Build:**
	```bash
	./release/build_devel.sh
	# or
	./release/build_release.sh
	```

	**Run:**
	```bash
	source ./scripts/setup_camera_hal_env.sh
	python3 -m selfdrive.camerad.camerad &
	python3 -m selfdrive.modeld.modeld &
	python3 -m selfdrive.controls.controlsd &
	python3 -m selfdrive.controls.plannerd &
	python3 -m selfdrive.controls.radard &
	python3 -m selfdrive.car.card &
	```

	---

	## 13. Porting/Validation Checklist (AI/Automation Ready)

	- [ ] Only `driving_vision.rknn` and `driving_policy.rknn` present in `selfdrive/modeld/models/`
	- [ ] Only IMX415 front camera enabled (no wide, stereo, USB, or driver monitoring)
	- [ ] Only Orange Pi 5 hardware detection logic present
	- [ ] Only required daemons enabled in process registry
	- [ ] All unused features/processes removed or disabled
	- [ ] Camera HAL and IMX415 driver validated
	- [ ] Controls and car interface minimal and correct
	- [ ] Scripts for camera HAL and power validated
	- [ ] Build and run scripts tested

	---

	## 🟧 Stability & Safety Guard Checklist (AI/Manual Porting)

	**Track and implement these before any road testing or production deployment.**

### Critical Safety/Robustness Fixes
- [ ] Replace all `assert` with `raise RuntimeError` in `rknn_runner.py` (asserts can be disabled, raising is always safe)
- [ ] Add null check on RKNN `outputs_get()` before indexing (raise if None)
- [ ] Add `np.isfinite()` guard on all NPU outputs before parsing (raise if NaN/Inf)
- [ ] Verify policy input key order matches RKNN model input order at startup (log both orders)
- [ ] Ensure `release()` is called on RKNNRunner at shutdown (use `atexit` or `try/finally` in modeld)
- [ ] Add camera reconnect/retry loop in `camera.py` (for CSI/USB disconnect resilience)
- [ ] Verify A76 core numbering: `cat /sys/devices/system/cpu/cpu{4..7}/cpufreq/cpuinfo_max_freq` (should be 2400000 for big cores)
- [ ] Add/verify heatsink + fan for sustained NPU performance (thermal throttling can cause >30ms inference)
- [ ] Broaden `/dev/rknpu0` check to also match `/dev/rknpu` (kernel naming varies)
- [ ] Add `__del__` guard in RKNNRunner to prevent double-release segfaults

### Operational/Deployment Gaps
- [ ] Add `rknn-toolkit-lite2` install instructions to setup scripts (cannot be in pyproject.toml, not on PyPI)
- [ ] Add thermal warning in UI/log if modelExecutionTime > 0.025s (optional, but recommended)
- [ ] Track and log all stability/safety checklist items in CI or deployment pipeline

---

## 🟧 Stability & Safety Guard Reference (Details)

**1. RKNN Error Handling:**
  - Replace all `assert` with `raise RuntimeError` in `rknn_runner.py`.
  - Add null check on `outputs_get()` before indexing.
  - Add `np.isfinite()` guard on all NPU outputs before parsing.

**2. Policy Input Order:**
  - At startup, print/log both the policy input dict key order and the RKNN model's expected input order. Confirm they match.

**3. RKNN Resource Management:**
  - Ensure `release()` is always called on RKNNRunner at shutdown (use `atexit` or `try/finally`).
  - Add `__del__` guard to RKNNRunner to prevent double-release segfaults.

**4. Camera Robustness:**
  - Add a reconnect/retry loop in `camera.py` for CSI/USB disconnects.

**5. Core Affinity & Thermal:**
  - Verify A76 core numbering on your kernel (should be 2400000 kHz for big cores).
  - Add/verify heatsink + fan for sustained NPU performance.
  - Add thermal warning in UI/log if modelExecutionTime > 0.025s.

**6. NPU Device Node Detection:**
  - Broaden `/dev/rknpu0` check to also match `/dev/rknpu`.

**7. RKNN Dependency:**
  - Add `rknn-toolkit-lite2` install instructions to setup scripts (manual pip install from Rockchip wheel).

**8. CI/Automation:**
  - Track and log all stability/safety checklist items in CI or deployment pipeline.

---

## 🟩 Final Checklist: What to Extract and Document in learn.md

- [ ] List all required `.rknn` models and their exact paths (e.g., `selfdrive/modeld/models/driving_vision.rknn`, `driving_policy.rknn`)
- [ ] Document all environment variables and feature flags needed (e.g., `USE_WEBCAM=1`, `NO_DM=1`, `ROAD_CAM` auto-detect)
- [ ] Summarize all process/daemon requirements (minimal list: `camerad`, `modeld`, `controlsd`, `plannerd`, `radard`, `card`, `socketd`)
- [ ] Specify all hardware abstraction and platform detection logic (e.g., RK3588 detection, NPU device node checks)
- [ ] List all scripts and utilities required for setup, validation, and deployment (e.g., `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`, `rk3588_secure_host.sh`)
- [ ] Document all code changes or diffs needed for porting (e.g., RKNN runner, modeld.py changes, SConscript skips, launch_env.sh env vars)
- [ ] Include all stability and safety guard checklist items (as above)
- [ ] Note all files/folders to keep, adapt, or remove (directory map)
- [ ] Summarize all tuning/parameter changes (e.g., camera focal length, DT_MDL, service frequencies)
- [ ] Reference all historical commits or diffs that must be replicated for new ports
- [ ] List all manual install steps (e.g., `rknn-toolkit-lite2` wheel, Mali driver, IMU wiring if used)
- [ ] Add any additional notes for automation, CI, or AI-driven porting

---

## 🟨 Orange Pi 5 Porting: openpilot, release, scripts Folders

### openpilot
**Purpose:** Main process tree (selfdrive, controls, modeld, car, etc.)

**Orange Pi 5 relevance:**
- `selfdrive/modeld/models/` contains `.rknn` models for RK3588 NPU. These must match your NPU budget (see model inventory and NPU_AND_MODELS.md).
- `selfdrive/modeld/README.md` and `docs/NPU_AND_MODELS.md` describe model requirements, NPU utilization, and conversion steps.
- `selfdrive/camerad/` and `common/hardware/rk3588/` handle all camera and hardware specifics (CSI, RGA, NPU, GPIO, PCIe accel).

**Action:**
- Ensure all required `.rknn` models are present in `selfdrive/modeld/models/`.
- Use `tools/rknn/convert_detection_models.sh` on a desktop (x86_64) to convert ONNX models to `.rknn` for RK3588.
- Validate NPU utilization does not exceed 6.0 TOPS (see model inventory table).
- For new models, update the inventory and test with `common/hardware/rk3588/npu.py`.

---

### release
**Purpose:** Build and release scripts for packaging and deployment.

**Orange Pi 5 relevance:**
- Use `build_devel.sh` or `build_release.sh` for packaging the stack for Orange Pi 5.
- No RK3588-specific logic is needed; scripts are platform-agnostic.

**Action:**
- Run `./release/build_devel.sh` for development builds.
- Run `./release/build_release.sh` for production images.
- Validate output images on Orange Pi 5 hardware.

---

### scripts
**Purpose:** Utility scripts for deployment, camera HAL, power management, and validation.

**Orange Pi 5 relevance:**
- **`rk3588_secure_host.sh`**: Secure lockdown, OpenBLT flashing, and SSH lockdown for RK3588 hosts. Use for production deployment and firmware flashing. Example usage:
	```bash
	./scripts/rk3588_secure_host.sh --lock
	./scripts/rk3588_secure_host.sh --unlock
	./scripts/rk3588_secure_host.sh --status
	./scripts/rk3588_secure_host.sh --flash --image firmware.srec
	```
- **`setup_camera_hal_env.sh`**: Sets up environment variables and system settings for the unified Camera HAL. Run before launching camera daemons to ensure zero-copy and high-performance operation.
	```bash
	source ./scripts/setup_camera_hal_env.sh
	```
- **`verify_big_core_allocation.sh`**: Verifies that safety-critical daemons (e.g., `controlsd`, `modeld`, `stereod`) are running on the correct RK3588 big CPU cores with proper priorities. Example output:
	```bash
	./scripts/verify_big_core_allocation.sh
	# Shows which daemons are on big cores (4-7) and their priorities
	```
- **`disable-powersave.py`**: Disables power-saving features on the device to ensure maximum performance. Run at boot or before starting OpenPilot:
	```bash
	python3 ./scripts/disable-powersave.py
	```
- **`reset_eop_params.sh`**: Backs up and wipes `/data/params` after a migration (e.g., EOP_ → EP_ prefix). Use with caution:
	```bash
	./scripts/reset_eop_params.sh
	# Prompts for confirmation, backs up, wipes, and recreates params dir
	```

**Action:**
- Use these scripts for setup, validation, and troubleshooting on Orange Pi 5.
- Automate their invocation in deployment scripts or CI pipelines for consistent bring-up and validation.

---

### Porting/Validation Checklist (for Orange Pi 5)

- [ ] All required `.rknn` models present and validated in `selfdrive/modeld/models/`
- [ ] NPU utilization ≤ 6.0 TOPS (see model inventory)
- [ ] Camera HAL environment configured (`setup_camera_hal_env.sh`)
- [ ] Daemon core affinity and priorities verified (`verify_big_core_allocation.sh`)
- [ ] Power-saving disabled (`disable-powersave.py`)
- [ ] Secure host lockdown and firmware flashing as needed (`rk3588_secure_host.sh`)
- [ ] Params reset after migration (`reset_eop_params.sh`)
- [ ] Build and release scripts tested (`build_devel.sh`, `build_release.sh`)

---

**Tip:** For automation, chain these scripts in your deployment pipeline and validate each step with log output. For new repo ports, copy this checklist and adapt as needed.

## 🟦 Step 2: Camera HAL & Daemon Migration
**Unified interface for all daemons:**

```python
from common.hardware.rk3588.camera import (
	OX03C10Camera, CSICameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
```

**USB Camera Example:**
```python
from common.hardware.rk3588.camera import (
	UVCCamera, USBCameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
camera_config = USBCameraConfig(
	device_path=device_path,
	width=width, height=height, pixel_format=V4L2PixelFormat.YUYV,
	fps=fps, usb_port="auto", uvc_version="1.5",
	---
	# 🧠 Orange Pi 5 Minimal OpenPilot Porting Guide (IMX415, Vision+Policy Only)

	This file is a **maximal, AI-automatable knowledge base** for porting any OpenPilot-based repo to Orange Pi 5 (RK3588) with only a single IMX415 front camera and only the `driving_vision.rknn` and `driving_policy.rknn` models. All other features (driver monitoring, stereo, Bluetooth, voice, grid, ground, track, predict, side cameras, etc.) are disabled or removed. Use this as the only reference for automation or manual porting.

	---

	## 1. Directory Map: What to Keep, What to Remove

	**Keep/Adapt:**
	- `common/hardware/rk3588/` (all files, especially `camera/`, `npu.py`, `rga.py`, `hardware.py`)
	- `selfdrive/camerad/` (only for IMX415 front camera)
	- `selfdrive/modeld/` (only `driving_vision.rknn`, `driving_policy.rknn`, and their wrappers)
	- `selfdrive/controls/` (only `controlsd.py`, `plannerd.py`, `radard.py`)
	- `selfdrive/car/` (only your car's interface and CAN parser)
	- `cereal/` (all, for Cap'n Proto messaging)
	- `system/manager/`, `system/hardware/`, `system/camerad/` (minimal, see below)
	- `scripts/` (only `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`)

	**Remove/Disable:**
	- All `monitoringd`, `stereod`, `externald`, `gridd`, `groundd`, `trackd`, `predictd`, `bluetoothd`, `voice`, `side cameras`, `driver monitoring`, `USB cameras`, `mapd`, `joystickd`, `elm327d`, `webjoystick`, `plated`, `snapd`, `loopd`, `crashd`, `debrisd`, `test/` folders not needed for your car.

	---

	## 2. Hardware Detection: RK3588-Only

	**File:** `system/hardware/__init__.py`

	```python
	from openpilot.common.hardware.rk3588.hardware import RK3588Hardware
	HARDWARE = RK3588Hardware(detected=True)
	RK3588 = True
	PC = False
	```

	**Remove all other hardware detection logic.**

	---

	## 3. Camera HAL: IMX415 Front Camera Only

	**File:** `common/hardware/rk3588/camera/csi.py`

	```python
	from common.hardware.rk3588.camera.v4l2 import V4L2Camera, V4L2Config, V4L2PixelFormat
	from common.hardware.rk3588.camera.sensors import IMX415Driver

	config = V4L2Config(
			device_path="/dev/video0",  # IMX415 front camera
			width=1920, height=1080, pixel_format=V4L2PixelFormat.YUYV,
			fps=30, memory_strategy="default"
	)
	camera = V4L2Camera(config)
	sensor = IMX415Driver(config.device_path)
	sensor.initialize()
	```

	**Remove all OX03C10, OS04C10, USB, and stereo camera logic.**

	---

	## 4. Model Inventory: Only Vision + Policy

	**Directory:** `selfdrive/modeld/models/`

	**Keep only:**
	- `driving_vision.rknn`
	- `driving_policy.rknn`

	**Remove all other models (YOLO, segmentation, headpose, etc.).**

	---

	## 5. Model Loading: Minimal RKNN Wrappers

	**File:** `selfdrive/modeld/vision/driving_vision_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingVisionRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load vision RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init vision RKNN runtime"
			def infer(self, img):
					return self.rknn.inference(inputs=[img])
	```

	**File:** `selfdrive/modeld/vision/driving_policy_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingPolicyRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load policy RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init policy RKNN runtime"
			def infer(self, features):
					return self.rknn.inference(inputs=[features])
	```

	---

	## 6. Minimal modeld: Only Vision + Policy

	**File:** `selfdrive/modeld/modeld.py` (simplified)

	```python
	from selfdrive.modeld.vision.driving_vision_rknn import DrivingVisionRKNN
	from selfdrive.modeld.vision.driving_policy_rknn import DrivingPolicyRKNN

	vision = DrivingVisionRKNN("models/driving_vision.rknn")
	policy = DrivingPolicyRKNN("models/driving_policy.rknn")

	# Main loop: get camera frame, run vision, then policy, publish result
	while True:
			img = get_camera_frame()  # Use IMX415 camera only
			vision_out = vision.infer(img)
			policy_out = policy.infer(vision_out)
			publish(policy_out)
	```

	---

	## 7. Process Registry: Only Required Daemons

	**File:** `system/manager/process_config.py`

	```python
	from openpilot.system.manager.process import PythonProcess, NativeProcess

	procs = [
		PythonProcess("camerad", "selfdrive.camerad.camerad", always_run),
		PythonProcess("modeld", "selfdrive.modeld.modeld", always_run),
		PythonProcess("controlsd", "selfdrive.controls.controlsd", always_run),
		PythonProcess("plannerd", "selfdrive.controls.plannerd", always_run),
		PythonProcess("radard", "selfdrive.controls.radard", always_run),
		PythonProcess("car", "selfdrive.car.card", always_run),
	]
	managed_processes = {p.name: p for p in procs}
	```

	**Remove all other processes (monitoringd, stereod, externald, bluetoothd, etc.).**

	---

	## 8. Controls: Minimal

	**File:** `selfdrive/controls/controlsd.py` (keep only core control loop, remove all references to unused features)

	**File:** `selfdrive/controls/plannerd.py`, `selfdrive/controls/radard.py` (keep only core logic)

	---

	## 9. Car Interface: Minimal

	**File:** `selfdrive/car/<yourcar>/interface.py` (implement only CAN parsing and actuator commands for your car)

	---

	## 10. Messaging: Cereal

	**Keep all Cap'n Proto schemas and messaging code in `cereal/`.**

	---

	## 11. Scripts: Only What You Need

	- `scripts/setup_camera_hal_env.sh` (run before launching)
	- `scripts/disable-powersave.py` (run at boot)
	- `scripts/verify_big_core_allocation.sh` (validate core affinity)

	---

	## 12. Build & Run

	**Build:**
	```bash
	./release/build_devel.sh
	# or
	./release/build_release.sh
	```

	**Run:**
	```bash
	source ./scripts/setup_camera_hal_env.sh
	python3 -m selfdrive.camerad.camerad &
	python3 -m selfdrive.modeld.modeld &
	python3 -m selfdrive.controls.controlsd &
	python3 -m selfdrive.controls.plannerd &
	python3 -m selfdrive.controls.radard &
	python3 -m selfdrive.car.card &
	```

	---

	## 13. Porting/Validation Checklist (AI/Automation Ready)

	- [ ] Only `driving_vision.rknn` and `driving_policy.rknn` present in `selfdrive/modeld/models/`
	- [ ] Only IMX415 front camera enabled (no wide, stereo, USB, or driver monitoring)
	- [ ] Only Orange Pi 5 hardware detection logic present
	- [ ] Only required daemons enabled in process registry
	- [ ] All unused features/processes removed or disabled
	- [ ] Camera HAL and IMX415 driver validated
	- [ ] Controls and car interface minimal and correct
	- [ ] Scripts for camera HAL and power validated
	- [ ] Build and run scripts tested

	---

	## 🟧 Stability & Safety Guard Checklist (AI/Manual Porting)

	**Track and implement these before any road testing or production deployment.**

### Critical Safety/Robustness Fixes
- [ ] Replace all `assert` with `raise RuntimeError` in `rknn_runner.py` (asserts can be disabled, raising is always safe)
- [ ] Add null check on RKNN `outputs_get()` before indexing (raise if None)
- [ ] Add `np.isfinite()` guard on all NPU outputs before parsing (raise if NaN/Inf)
- [ ] Verify policy input key order matches RKNN model input order at startup (log both orders)
- [ ] Ensure `release()` is called on RKNNRunner at shutdown (use `atexit` or `try/finally` in modeld)
- [ ] Add camera reconnect/retry loop in `camera.py` (for CSI/USB disconnect resilience)
- [ ] Verify A76 core numbering: `cat /sys/devices/system/cpu/cpu{4..7}/cpufreq/cpuinfo_max_freq` (should be 2400000 for big cores)
- [ ] Add/verify heatsink + fan for sustained NPU performance (thermal throttling can cause >30ms inference)
- [ ] Broaden `/dev/rknpu0` check to also match `/dev/rknpu` (kernel naming varies)
- [ ] Add `__del__` guard in RKNNRunner to prevent double-release segfaults

### Operational/Deployment Gaps
- [ ] Add `rknn-toolkit-lite2` install instructions to setup scripts (cannot be in pyproject.toml, not on PyPI)
- [ ] Add thermal warning in UI/log if modelExecutionTime > 0.025s (optional, but recommended)
- [ ] Track and log all stability/safety checklist items in CI or deployment pipeline

---

## 🟧 Stability & Safety Guard Reference (Details)

**1. RKNN Error Handling:**
  - Replace all `assert` with `raise RuntimeError` in `rknn_runner.py`.
  - Add null check on `outputs_get()` before indexing.
  - Add `np.isfinite()` guard on all NPU outputs before parsing.

**2. Policy Input Order:**
  - At startup, print/log both the policy input dict key order and the RKNN model's expected input order. Confirm they match.

**3. RKNN Resource Management:**
  - Ensure `release()` is always called on RKNNRunner at shutdown (use `atexit` or `try/finally`).
  - Add `__del__` guard to RKNNRunner to prevent double-release segfaults.

**4. Camera Robustness:**
  - Add a reconnect/retry loop in `camera.py` for CSI/USB disconnects.

**5. Core Affinity & Thermal:**
  - Verify A76 core numbering on your kernel (should be 2400000 kHz for big cores).
  - Add/verify heatsink + fan for sustained NPU performance.
  - Add thermal warning in UI/log if modelExecutionTime > 0.025s.

**6. NPU Device Node Detection:**
  - Broaden `/dev/rknpu0` check to also match `/dev/rknpu`.

**7. RKNN Dependency:**
  - Add `rknn-toolkit-lite2` install instructions to setup scripts (manual pip install from Rockchip wheel).

**8. CI/Automation:**
  - Track and log all stability/safety checklist items in CI or deployment pipeline.

---

## 🟩 Final Checklist: What to Extract and Document in learn.md

- [ ] List all required `.rknn` models and their exact paths (e.g., `selfdrive/modeld/models/driving_vision.rknn`, `driving_policy.rknn`)
- [ ] Document all environment variables and feature flags needed (e.g., `USE_WEBCAM=1`, `NO_DM=1`, `ROAD_CAM` auto-detect)
- [ ] Summarize all process/daemon requirements (minimal list: `camerad`, `modeld`, `controlsd`, `plannerd`, `radard`, `card`, `socketd`)
- [ ] Specify all hardware abstraction and platform detection logic (e.g., RK3588 detection, NPU device node checks)
- [ ] List all scripts and utilities required for setup, validation, and deployment (e.g., `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`, `rk3588_secure_host.sh`)
- [ ] Document all code changes or diffs needed for porting (e.g., RKNN runner, modeld.py changes, SConscript skips, launch_env.sh env vars)
- [ ] Include all stability and safety guard checklist items (as above)
- [ ] Note all files/folders to keep, adapt, or remove (directory map)
- [ ] Summarize all tuning/parameter changes (e.g., camera focal length, DT_MDL, service frequencies)
- [ ] Reference all historical commits or diffs that must be replicated for new ports
- [ ] List all manual install steps (e.g., `rknn-toolkit-lite2` wheel, Mali driver, IMU wiring if used)
- [ ] Add any additional notes for automation, CI, or AI-driven porting

---

## 🟨 Orange Pi 5 Porting: openpilot, release, scripts Folders

### openpilot
**Purpose:** Main process tree (selfdrive, controls, modeld, car, etc.)

**Orange Pi 5 relevance:**
- `selfdrive/modeld/models/` contains `.rknn` models for RK3588 NPU. These must match your NPU budget (see model inventory and NPU_AND_MODELS.md).
- `selfdrive/modeld/README.md` and `docs/NPU_AND_MODELS.md` describe model requirements, NPU utilization, and conversion steps.
- `selfdrive/camerad/` and `common/hardware/rk3588/` handle all camera and hardware specifics (CSI, RGA, NPU, GPIO, PCIe accel).

**Action:**
- Ensure all required `.rknn` models are present in `selfdrive/modeld/models/`.
- Use `tools/rknn/convert_detection_models.sh` on a desktop (x86_64) to convert ONNX models to `.rknn` for RK3588.
- Validate NPU utilization does not exceed 6.0 TOPS (see model inventory table).
- For new models, update the inventory and test with `common/hardware/rk3588/npu.py`.

---

### release
**Purpose:** Build and release scripts for packaging and deployment.

**Orange Pi 5 relevance:**
- Use `build_devel.sh` or `build_release.sh` for packaging the stack for Orange Pi 5.
- No RK3588-specific logic is needed; scripts are platform-agnostic.

**Action:**
- Run `./release/build_devel.sh` for development builds.
- Run `./release/build_release.sh` for production images.
- Validate output images on Orange Pi 5 hardware.

---

### scripts
**Purpose:** Utility scripts for deployment, camera HAL, power management, and validation.

**Orange Pi 5 relevance:**
- **`rk3588_secure_host.sh`**: Secure lockdown, OpenBLT flashing, and SSH lockdown for RK3588 hosts. Use for production deployment and firmware flashing. Example usage:
	```bash
	./scripts/rk3588_secure_host.sh --lock
	./scripts/rk3588_secure_host.sh --unlock
	./scripts/rk3588_secure_host.sh --status
	./scripts/rk3588_secure_host.sh --flash --image firmware.srec
	```
- **`setup_camera_hal_env.sh`**: Sets up environment variables and system settings for the unified Camera HAL. Run before launching camera daemons to ensure zero-copy and high-performance operation.
	```bash
	source ./scripts/setup_camera_hal_env.sh
	```
- **`verify_big_core_allocation.sh`**: Verifies that safety-critical daemons (e.g., `controlsd`, `modeld`, `stereod`) are running on the correct RK3588 big CPU cores with proper priorities. Example output:
	```bash
	./scripts/verify_big_core_allocation.sh
	# Shows which daemons are on big cores (4-7) and their priorities
	```
- **`disable-powersave.py`**: Disables power-saving features on the device to ensure maximum performance. Run at boot or before starting OpenPilot:
	```bash
	python3 ./scripts/disable-powersave.py
	```
- **`reset_eop_params.sh`**: Backs up and wipes `/data/params` after a migration (e.g., EOP_ → EP_ prefix). Use with caution:
	```bash
	./scripts/reset_eop_params.sh
	# Prompts for confirmation, backs up, wipes, and recreates params dir
	```

**Action:**
- Use these scripts for setup, validation, and troubleshooting on Orange Pi 5.
- Automate their invocation in deployment scripts or CI pipelines for consistent bring-up and validation.

---

### Porting/Validation Checklist (for Orange Pi 5)

- [ ] All required `.rknn` models present and validated in `selfdrive/modeld/models/`
- [ ] NPU utilization ≤ 6.0 TOPS (see model inventory)
- [ ] Camera HAL environment configured (`setup_camera_hal_env.sh`)
- [ ] Daemon core affinity and priorities verified (`verify_big_core_allocation.sh`)
- [ ] Power-saving disabled (`disable-powersave.py`)
- [ ] Secure host lockdown and firmware flashing as needed (`rk3588_secure_host.sh`)
- [ ] Params reset after migration (`reset_eop_params.sh`)
- [ ] Build and release scripts tested (`build_devel.sh`, `build_release.sh`)

---

**Tip:** For automation, chain these scripts in your deployment pipeline and validate each step with log output. For new repo ports, copy this checklist and adapt as needed.

## 🟦 Step 2: Camera HAL & Daemon Migration
**Unified interface for all daemons:**

```python
from common.hardware.rk3588.camera import (
	OX03C10Camera, CSICameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
```

**USB Camera Example:**
```python
from common.hardware.rk3588.camera import (
	UVCCamera, USBCameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
camera_config = USBCameraConfig(
	device_path=device_path,
	width=width, height=height, pixel_format=V4L2PixelFormat.YUYV,
	fps=fps, usb_port="auto", uvc_version="1.5",
	---
	# 🧠 Orange Pi 5 Minimal OpenPilot Porting Guide (IMX415, Vision+Policy Only)

	This file is a **maximal, AI-automatable knowledge base** for porting any OpenPilot-based repo to Orange Pi 5 (RK3588) with only a single IMX415 front camera and only the `driving_vision.rknn` and `driving_policy.rknn` models. All other features (driver monitoring, stereo, Bluetooth, voice, grid, ground, track, predict, side cameras, etc.) are disabled or removed. Use this as the only reference for automation or manual porting.

	---

	## 1. Directory Map: What to Keep, What to Remove

	**Keep/Adapt:**
	- `common/hardware/rk3588/` (all files, especially `camera/`, `npu.py`, `rga.py`, `hardware.py`)
	- `selfdrive/camerad/` (only for IMX415 front camera)
	- `selfdrive/modeld/` (only `driving_vision.rknn`, `driving_policy.rknn`, and their wrappers)
	- `selfdrive/controls/` (only `controlsd.py`, `plannerd.py`, `radard.py`)
	- `selfdrive/car/` (only your car's interface and CAN parser)
	- `cereal/` (all, for Cap'n Proto messaging)
	- `system/manager/`, `system/hardware/`, `system/camerad/` (minimal, see below)
	- `scripts/` (only `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`)

	**Remove/Disable:**
	- All `monitoringd`, `stereod`, `externald`, `gridd`, `groundd`, `trackd`, `predictd`, `bluetoothd`, `voice`, `side cameras`, `driver monitoring`, `USB cameras`, `mapd`, `joystickd`, `elm327d`, `webjoystick`, `plated`, `snapd`, `loopd`, `crashd`, `debrisd`, `test/` folders not needed for your car.

	---

	## 2. Hardware Detection: RK3588-Only

	**File:** `system/hardware/__init__.py`

	```python
	from openpilot.common.hardware.rk3588.hardware import RK3588Hardware
	HARDWARE = RK3588Hardware(detected=True)
	RK3588 = True
	PC = False
	```

	**Remove all other hardware detection logic.**

	---

	## 3. Camera HAL: IMX415 Front Camera Only

	**File:** `common/hardware/rk3588/camera/csi.py`

	```python
	from common.hardware.rk3588.camera.v4l2 import V4L2Camera, V4L2Config, V4L2PixelFormat
	from common.hardware.rk3588.camera.sensors import IMX415Driver

	config = V4L2Config(
			device_path="/dev/video0",  # IMX415 front camera
			width=1920, height=1080, pixel_format=V4L2PixelFormat.YUYV,
			fps=30, memory_strategy="default"
	)
	camera = V4L2Camera(config)
	sensor = IMX415Driver(config.device_path)
	sensor.initialize()
	```

	**Remove all OX03C10, OS04C10, USB, and stereo camera logic.**

	---

	## 4. Model Inventory: Only Vision + Policy

	**Directory:** `selfdrive/modeld/models/`

	**Keep only:**
	- `driving_vision.rknn`
	- `driving_policy.rknn`

	**Remove all other models (YOLO, segmentation, headpose, etc.).**

	---

	## 5. Model Loading: Minimal RKNN Wrappers

	**File:** `selfdrive/modeld/vision/driving_vision_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingVisionRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load vision RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init vision RKNN runtime"
			def infer(self, img):
					return self.rknn.inference(inputs=[img])
	```

	**File:** `selfdrive/modeld/vision/driving_policy_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingPolicyRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load policy RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init policy RKNN runtime"
			def infer(self, features):
					return self.rknn.inference(inputs=[features])
	```

	---

	## 6. Minimal modeld: Only Vision + Policy

	**File:** `selfdrive/modeld/modeld.py` (simplified)

	```python
	from selfdrive.modeld.vision.driving_vision_rknn import DrivingVisionRKNN
	from selfdrive.modeld.vision.driving_policy_rknn import DrivingPolicyRKNN

	vision = DrivingVisionRKNN("models/driving_vision.rknn")
	policy = DrivingPolicyRKNN("models/driving_policy.rknn")

	# Main loop: get camera frame, run vision, then policy, publish result
	while True:
			img = get_camera_frame()  # Use IMX415 camera only
			vision_out = vision.infer(img)
			policy_out = policy.infer(vision_out)
			publish(policy_out)
	```

	---

	## 7. Process Registry: Only Required Daemons

	**File:** `system/manager/process_config.py`

	```python
	from openpilot.system.manager.process import PythonProcess, NativeProcess

	procs = [
		PythonProcess("camerad", "selfdrive.camerad.camerad", always_run),
		PythonProcess("modeld", "selfdrive.modeld.modeld", always_run),
		PythonProcess("controlsd", "selfdrive.controls.controlsd", always_run),
		PythonProcess("plannerd", "selfdrive.controls.plannerd", always_run),
		PythonProcess("radard", "selfdrive.controls.radard", always_run),
		PythonProcess("car", "selfdrive.car.card", always_run),
	]
	managed_processes = {p.name: p for p in procs}
	```

	**Remove all other processes (monitoringd, stereod, externald, bluetoothd, etc.).**

	---

	## 8. Controls: Minimal

	**File:** `selfdrive/controls/controlsd.py` (keep only core control loop, remove all references to unused features)

	**File:** `selfdrive/controls/plannerd.py`, `selfdrive/controls/radard.py` (keep only core logic)

	---

	## 9. Car Interface: Minimal

	**File:** `selfdrive/car/<yourcar>/interface.py` (implement only CAN parsing and actuator commands for your car)

	---

	## 10. Messaging: Cereal

	**Keep all Cap'n Proto schemas and messaging code in `cereal/`.**

	---

	## 11. Scripts: Only What You Need

	- `scripts/setup_camera_hal_env.sh` (run before launching)
	- `scripts/disable-powersave.py` (run at boot)
	- `scripts/verify_big_core_allocation.sh` (validate core affinity)

	---

	## 12. Build & Run

	**Build:**
	```bash
	./release/build_devel.sh
	# or
	./release/build_release.sh
	```

	**Run:**
	```bash
	source ./scripts/setup_camera_hal_env.sh
	python3 -m selfdrive.camerad.camerad &
	python3 -m selfdrive.modeld.modeld &
	python3 -m selfdrive.controls.controlsd &
	python3 -m selfdrive.controls.plannerd &
	python3 -m selfdrive.controls.radard &
	python3 -m selfdrive.car.card &
	```

	---

	## 13. Porting/Validation Checklist (AI/Automation Ready)

	- [ ] Only `driving_vision.rknn` and `driving_policy.rknn` present in `selfdrive/modeld/models/`
	- [ ] Only IMX415 front camera enabled (no wide, stereo, USB, or driver monitoring)
	- [ ] Only Orange Pi 5 hardware detection logic present
	- [ ] Only required daemons enabled in process registry
	- [ ] All unused features/processes removed or disabled
	- [ ] Camera HAL and IMX415 driver validated
	- [ ] Controls and car interface minimal and correct
	- [ ] Scripts for camera HAL and power validated
	- [ ] Build and run scripts tested

	---

	## 🟧 Stability & Safety Guard Checklist (AI/Manual Porting)

	**Track and implement these before any road testing or production deployment.**

### Critical Safety/Robustness Fixes
- [ ] Replace all `assert` with `raise RuntimeError` in `rknn_runner.py` (asserts can be disabled, raising is always safe)
- [ ] Add null check on RKNN `outputs_get()` before indexing (raise if None)
- [ ] Add `np.isfinite()` guard on all NPU outputs before parsing (raise if NaN/Inf)
- [ ] Verify policy input key order matches RKNN model input order at startup (log both orders)
- [ ] Ensure `release()` is called on RKNNRunner at shutdown (use `atexit` or `try/finally` in modeld)
- [ ] Add camera reconnect/retry loop in `camera.py` (for CSI/USB disconnect resilience)
- [ ] Verify A76 core numbering: `cat /sys/devices/system/cpu/cpu{4..7}/cpufreq/cpuinfo_max_freq` (should be 2400000 for big cores)
- [ ] Add/verify heatsink + fan for sustained NPU performance (thermal throttling can cause >30ms inference)
- [ ] Broaden `/dev/rknpu0` check to also match `/dev/rknpu` (kernel naming varies)
- [ ] Add `__del__` guard in RKNNRunner to prevent double-release segfaults

### Operational/Deployment Gaps
- [ ] Add `rknn-toolkit-lite2` install instructions to setup scripts (cannot be in pyproject.toml, not on PyPI)
- [ ] Add thermal warning in UI/log if modelExecutionTime > 0.025s (optional, but recommended)
- [ ] Track and log all stability/safety checklist items in CI or deployment pipeline

---

## 🟧 Stability & Safety Guard Reference (Details)

**1. RKNN Error Handling:**
  - Replace all `assert` with `raise RuntimeError` in `rknn_runner.py`.
  - Add null check on `outputs_get()` before indexing.
  - Add `np.isfinite()` guard on all NPU outputs before parsing.

**2. Policy Input Order:**
  - At startup, print/log both the policy input dict key order and the RKNN model's expected input order. Confirm they match.

**3. RKNN Resource Management:**
  - Ensure `release()` is always called on RKNNRunner at shutdown (use `atexit` or `try/finally`).
  - Add `__del__` guard to RKNNRunner to prevent double-release segfaults.

**4. Camera Robustness:**
  - Add a reconnect/retry loop in `camera.py` for CSI/USB disconnects.

**5. Core Affinity & Thermal:**
  - Verify A76 core numbering on your kernel (should be 2400000 kHz for big cores).
  - Add/verify heatsink + fan for sustained NPU performance.
  - Add thermal warning in UI/log if modelExecutionTime > 0.025s.

**6. NPU Device Node Detection:**
  - Broaden `/dev/rknpu0` check to also match `/dev/rknpu`.

**7. RKNN Dependency:**
  - Add `rknn-toolkit-lite2` install instructions to setup scripts (manual pip install from Rockchip wheel).

**8. CI/Automation:**
  - Track and log all stability/safety checklist items in CI or deployment pipeline.

---

## 🟩 Final Checklist: What to Extract and Document in learn.md

- [ ] List all required `.rknn` models and their exact paths (e.g., `selfdrive/modeld/models/driving_vision.rknn`, `driving_policy.rknn`)
- [ ] Document all environment variables and feature flags needed (e.g., `USE_WEBCAM=1`, `NO_DM=1`, `ROAD_CAM` auto-detect)
- [ ] Summarize all process/daemon requirements (minimal list: `camerad`, `modeld`, `controlsd`, `plannerd`, `radard`, `card`, `socketd`)
- [ ] Specify all hardware abstraction and platform detection logic (e.g., RK3588 detection, NPU device node checks)
- [ ] List all scripts and utilities required for setup, validation, and deployment (e.g., `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`, `rk3588_secure_host.sh`)
- [ ] Document all code changes or diffs needed for porting (e.g., RKNN runner, modeld.py changes, SConscript skips, launch_env.sh env vars)
- [ ] Include all stability and safety guard checklist items (as above)
- [ ] Note all files/folders to keep, adapt, or remove (directory map)
- [ ] Summarize all tuning/parameter changes (e.g., camera focal length, DT_MDL, service frequencies)
- [ ] Reference all historical commits or diffs that must be replicated for new ports
- [ ] List all manual install steps (e.g., `rknn-toolkit-lite2` wheel, Mali driver, IMU wiring if used)
- [ ] Add any additional notes for automation, CI, or AI-driven porting

---

## 🟨 Orange Pi 5 Porting: openpilot, release, scripts Folders

### openpilot
**Purpose:** Main process tree (selfdrive, controls, modeld, car, etc.)

**Orange Pi 5 relevance:**
- `selfdrive/modeld/models/` contains `.rknn` models for RK3588 NPU. These must match your NPU budget (see model inventory and NPU_AND_MODELS.md).
- `selfdrive/modeld/README.md` and `docs/NPU_AND_MODELS.md` describe model requirements, NPU utilization, and conversion steps.
- `selfdrive/camerad/` and `common/hardware/rk3588/` handle all camera and hardware specifics (CSI, RGA, NPU, GPIO, PCIe accel).

**Action:**
- Ensure all required `.rknn` models are present in `selfdrive/modeld/models/`.
- Use `tools/rknn/convert_detection_models.sh` on a desktop (x86_64) to convert ONNX models to `.rknn` for RK3588.
- Validate NPU utilization does not exceed 6.0 TOPS (see model inventory table).
- For new models, update the inventory and test with `common/hardware/rk3588/npu.py`.

---

### release
**Purpose:** Build and release scripts for packaging and deployment.

**Orange Pi 5 relevance:**
- Use `build_devel.sh` or `build_release.sh` for packaging the stack for Orange Pi 5.
- No RK3588-specific logic is needed; scripts are platform-agnostic.

**Action:**
- Run `./release/build_devel.sh` for development builds.
- Run `./release/build_release.sh` for production images.
- Validate output images on Orange Pi 5 hardware.

---

### scripts
**Purpose:** Utility scripts for deployment, camera HAL, power management, and validation.

**Orange Pi 5 relevance:**
- **`rk3588_secure_host.sh`**: Secure lockdown, OpenBLT flashing, and SSH lockdown for RK3588 hosts. Use for production deployment and firmware flashing. Example usage:
	```bash
	./scripts/rk3588_secure_host.sh --lock
	./scripts/rk3588_secure_host.sh --unlock
	./scripts/rk3588_secure_host.sh --status
	./scripts/rk3588_secure_host.sh --flash --image firmware.srec
	```
- **`setup_camera_hal_env.sh`**: Sets up environment variables and system settings for the unified Camera HAL. Run before launching camera daemons to ensure zero-copy and high-performance operation.
	```bash
	source ./scripts/setup_camera_hal_env.sh
	```
- **`verify_big_core_allocation.sh`**: Verifies that safety-critical daemons (e.g., `controlsd`, `modeld`, `stereod`) are running on the correct RK3588 big CPU cores with proper priorities. Example output:
	```bash
	./scripts/verify_big_core_allocation.sh
	# Shows which daemons are on big cores (4-7) and their priorities
	```
- **`disable-powersave.py`**: Disables power-saving features on the device to ensure maximum performance. Run at boot or before starting OpenPilot:
	```bash
	python3 ./scripts/disable-powersave.py
	```
- **`reset_eop_params.sh`**: Backs up and wipes `/data/params` after a migration (e.g., EOP_ → EP_ prefix). Use with caution:
	```bash
	./scripts/reset_eop_params.sh
	# Prompts for confirmation, backs up, wipes, and recreates params dir
	```

**Action:**
- Use these scripts for setup, validation, and troubleshooting on Orange Pi 5.
- Automate their invocation in deployment scripts or CI pipelines for consistent bring-up and validation.

---

### Porting/Validation Checklist (for Orange Pi 5)

- [ ] All required `.rknn` models present and validated in `selfdrive/modeld/models/`
- [ ] NPU utilization ≤ 6.0 TOPS (see model inventory)
- [ ] Camera HAL environment configured (`setup_camera_hal_env.sh`)
- [ ] Daemon core affinity and priorities verified (`verify_big_core_allocation.sh`)
- [ ] Power-saving disabled (`disable-powersave.py`)
- [ ] Secure host lockdown and firmware flashing as needed (`rk3588_secure_host.sh`)
- [ ] Params reset after migration (`reset_eop_params.sh`)
- [ ] Build and release scripts tested (`build_devel.sh`, `build_release.sh`)

---

**Tip:** For automation, chain these scripts in your deployment pipeline and validate each step with log output. For new repo ports, copy this checklist and adapt as needed.

## 🟦 Step 2: Camera HAL & Daemon Migration
**Unified interface for all daemons:**

```python
from common.hardware.rk3588.camera import (
	OX03C10Camera, CSICameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
```

**USB Camera Example:**
```python
from common.hardware.rk3588.camera import (
	UVCCamera, USBCameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
camera_config = USBCameraConfig(
	device_path=device_path,
	width=width, height=height, pixel_format=V4L2PixelFormat.YUYV,
	fps=fps, usb_port="auto", uvc_version="1.5",
	---
	# 🧠 Orange Pi 5 Minimal OpenPilot Porting Guide (IMX415, Vision+Policy Only)

	This file is a **maximal, AI-automatable knowledge base** for porting any OpenPilot-based repo to Orange Pi 5 (RK3588) with only a single IMX415 front camera and only the `driving_vision.rknn` and `driving_policy.rknn` models. All other features (driver monitoring, stereo, Bluetooth, voice, grid, ground, track, predict, side cameras, etc.) are disabled or removed. Use this as the only reference for automation or manual porting.

	---

	## 1. Directory Map: What to Keep, What to Remove

	**Keep/Adapt:**
	- `common/hardware/rk3588/` (all files, especially `camera/`, `npu.py`, `rga.py`, `hardware.py`)
	- `selfdrive/camerad/` (only for IMX415 front camera)
	- `selfdrive/modeld/` (only `driving_vision.rknn`, `driving_policy.rknn`, and their wrappers)
	- `selfdrive/controls/` (only `controlsd.py`, `plannerd.py`, `radard.py`)
	- `selfdrive/car/` (only your car's interface and CAN parser)
	- `cereal/` (all, for Cap'n Proto messaging)
	- `system/manager/`, `system/hardware/`, `system/camerad/` (minimal, see below)
	- `scripts/` (only `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`)

	**Remove/Disable:**
	- All `monitoringd`, `stereod`, `externald`, `gridd`, `groundd`, `trackd`, `predictd`, `bluetoothd`, `voice`, `side cameras`, `driver monitoring`, `USB cameras`, `mapd`, `joystickd`, `elm327d`, `webjoystick`, `plated`, `snapd`, `loopd`, `crashd`, `debrisd`, `test/` folders not needed for your car.

	---

	## 2. Hardware Detection: RK3588-Only

	**File:** `system/hardware/__init__.py`

	```python
	from openpilot.common.hardware.rk3588.hardware import RK3588Hardware
	HARDWARE = RK3588Hardware(detected=True)
	RK3588 = True
	PC = False
	```

	**Remove all other hardware detection logic.**

	---

	## 3. Camera HAL: IMX415 Front Camera Only

	**File:** `common/hardware/rk3588/camera/csi.py`

	```python
	from common.hardware.rk3588.camera.v4l2 import V4L2Camera, V4L2Config, V4L2PixelFormat
	from common.hardware.rk3588.camera.sensors import IMX415Driver

	config = V4L2Config(
			device_path="/dev/video0",  # IMX415 front camera
			width=1920, height=1080, pixel_format=V4L2PixelFormat.YUYV,
			fps=30, memory_strategy="default"
	)
	camera = V4L2Camera(config)
	sensor = IMX415Driver(config.device_path)
	sensor.initialize()
	```

	**Remove all OX03C10, OS04C10, USB, and stereo camera logic.**

	---

	## 4. Model Inventory: Only Vision + Policy

	**Directory:** `selfdrive/modeld/models/`

	**Keep only:**
	- `driving_vision.rknn`
	- `driving_policy.rknn`

	**Remove all other models (YOLO, segmentation, headpose, etc.).**

	---

	## 5. Model Loading: Minimal RKNN Wrappers

	**File:** `selfdrive/modeld/vision/driving_vision_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingVisionRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load vision RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init vision RKNN runtime"
			def infer(self, img):
					return self.rknn.inference(inputs=[img])
	```

	**File:** `selfdrive/modeld/vision/driving_policy_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingPolicyRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load policy RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init policy RKNN runtime"
			def infer(self, features):
					return self.rknn.inference(inputs=[features])
	```

	---

	## 6. Minimal modeld: Only Vision + Policy

	**File:** `selfdrive/modeld/modeld.py` (simplified)

	```python
	from selfdrive.modeld.vision.driving_vision_rknn import DrivingVisionRKNN
	from selfdrive.modeld.vision.driving_policy_rknn import DrivingPolicyRKNN

	vision = DrivingVisionRKNN("models/driving_vision.rknn")
	policy = DrivingPolicyRKNN("models/driving_policy.rknn")

	# Main loop: get camera frame, run vision, then policy, publish result
	while True:
			img = get_camera_frame()  # Use IMX415 camera only
			vision_out = vision.infer(img)
			policy_out = policy.infer(vision_out)
			publish(policy_out)
	```

	---

	## 7. Process Registry: Only Required Daemons

	**File:** `system/manager/process_config.py`

	```python
	from openpilot.system.manager.process import PythonProcess, NativeProcess

	procs = [
		PythonProcess("camerad", "selfdrive.camerad.camerad", always_run),
		PythonProcess("modeld", "selfdrive.modeld.modeld", always_run),
		PythonProcess("controlsd", "selfdrive.controls.controlsd", always_run),
		PythonProcess("plannerd", "selfdrive.controls.plannerd", always_run),
		PythonProcess("radard", "selfdrive.controls.radard", always_run),
		PythonProcess("car", "selfdrive.car.card", always_run),
	]
	managed_processes = {p.name: p for p in procs}
	```

	**Remove all other processes (monitoringd, stereod, externald, bluetoothd, etc.).**

	---

	## 8. Controls: Minimal

	**File:** `selfdrive/controls/controlsd.py` (keep only core control loop, remove all references to unused features)

	**File:** `selfdrive/controls/plannerd.py`, `selfdrive/controls/radard.py` (keep only core logic)

	---

	## 9. Car Interface: Minimal

	**File:** `selfdrive/car/<yourcar>/interface.py` (implement only CAN parsing and actuator commands for your car)

	---

	## 10. Messaging: Cereal

	**Keep all Cap'n Proto schemas and messaging code in `cereal/`.**

	---

	## 11. Scripts: Only What You Need

	- `scripts/setup_camera_hal_env.sh` (run before launching)
	- `scripts/disable-powersave.py` (run at boot)
	- `scripts/verify_big_core_allocation.sh` (validate core affinity)

	---

	## 12. Build & Run

	**Build:**
	```bash
	./release/build_devel.sh
	# or
	./release/build_release.sh
	```

	**Run:**
	```bash
	source ./scripts/setup_camera_hal_env.sh
	python3 -m selfdrive.camerad.camerad &
	python3 -m selfdrive.modeld.modeld &
	python3 -m selfdrive.controls.controlsd &
	python3 -m selfdrive.controls.plannerd &
	python3 -m selfdrive.controls.radard &
	python3 -m selfdrive.car.card &
	```

	---

	## 13. Porting/Validation Checklist (AI/Automation Ready)

	- [ ] Only `driving_vision.rknn` and `driving_policy.rknn` present in `selfdrive/modeld/models/`
	- [ ] Only IMX415 front camera enabled (no wide, stereo, USB, or driver monitoring)
	- [ ] Only Orange Pi 5 hardware detection logic present
	- [ ] Only required daemons enabled in process registry
	- [ ] All unused features/processes removed or disabled
	- [ ] Camera HAL and IMX415 driver validated
	- [ ] Controls and car interface minimal and correct
	- [ ] Scripts for camera HAL and power validated
	- [ ] Build and run scripts tested

	---

	## 🟧 Stability & Safety Guard Checklist (AI/Manual Porting)

	**Track and implement these before any road testing or production deployment.**

### Critical Safety/Robustness Fixes
- [ ] Replace all `assert` with `raise RuntimeError` in `rknn_runner.py` (asserts can be disabled, raising is always safe)
- [ ] Add null check on RKNN `outputs_get()` before indexing (raise if None)
- [ ] Add `np.isfinite()` guard on all NPU outputs before parsing (raise if NaN/Inf)
- [ ] Verify policy input key order matches RKNN model input order at startup (log both orders)
- [ ] Ensure `release()` is called on RKNNRunner at shutdown (use `atexit` or `try/finally` in modeld)
- [ ] Add camera reconnect/retry loop in `camera.py` (for CSI/USB disconnect resilience)
- [ ] Verify A76 core numbering: `cat /sys/devices/system/cpu/cpu{4..7}/cpufreq/cpuinfo_max_freq` (should be 2400000 for big cores)
- [ ] Add/verify heatsink + fan for sustained NPU performance (thermal throttling can cause >30ms inference)
- [ ] Broaden `/dev/rknpu0` check to also match `/dev/rknpu` (kernel naming varies)
- [ ] Add `__del__` guard in RKNNRunner to prevent double-release segfaults

### Operational/Deployment Gaps
- [ ] Add `rknn-toolkit-lite2` install instructions to setup scripts (cannot be in pyproject.toml, not on PyPI)
- [ ] Add thermal warning in UI/log if modelExecutionTime > 0.025s (optional, but recommended)
- [ ] Track and log all stability/safety checklist items in CI or deployment pipeline

---

## 🟧 Stability & Safety Guard Reference (Details)

**1. RKNN Error Handling:**
  - Replace all `assert` with `raise RuntimeError` in `rknn_runner.py`.
  - Add null check on `outputs_get()` before indexing.
  - Add `np.isfinite()` guard on all NPU outputs before parsing.

**2. Policy Input Order:**
  - At startup, print/log both the policy input dict key order and the RKNN model's expected input order. Confirm they match.

**3. RKNN Resource Management:**
  - Ensure `release()` is always called on RKNNRunner at shutdown (use `atexit` or `try/finally`).
  - Add `__del__` guard to RKNNRunner to prevent double-release segfaults.

**4. Camera Robustness:**
  - Add a reconnect/retry loop in `camera.py` for CSI/USB disconnects.

**5. Core Affinity & Thermal:**
  - Verify A76 core numbering on your kernel (should be 2400000 kHz for big cores).
  - Add/verify heatsink + fan for sustained NPU performance.
  - Add thermal warning in UI/log if modelExecutionTime > 0.025s.

**6. NPU Device Node Detection:**
  - Broaden `/dev/rknpu0` check to also match `/dev/rknpu`.

**7. RKNN Dependency:**
  - Add `rknn-toolkit-lite2` install instructions to setup scripts (manual pip install from Rockchip wheel).

**8. CI/Automation:**
  - Track and log all stability/safety checklist items in CI or deployment pipeline.

---

## 🟩 Final Checklist: What to Extract and Document in learn.md

- [ ] List all required `.rknn` models and their exact paths (e.g., `selfdrive/modeld/models/driving_vision.rknn`, `driving_policy.rknn`)
- [ ] Document all environment variables and feature flags needed (e.g., `USE_WEBCAM=1`, `NO_DM=1`, `ROAD_CAM` auto-detect)
- [ ] Summarize all process/daemon requirements (minimal list: `camerad`, `modeld`, `controlsd`, `plannerd`, `radard`, `card`, `socketd`)
- [ ] Specify all hardware abstraction and platform detection logic (e.g., RK3588 detection, NPU device node checks)
- [ ] List all scripts and utilities required for setup, validation, and deployment (e.g., `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`, `rk3588_secure_host.sh`)
- [ ] Document all code changes or diffs needed for porting (e.g., RKNN runner, modeld.py changes, SConscript skips, launch_env.sh env vars)
- [ ] Include all stability and safety guard checklist items (as above)
- [ ] Note all files/folders to keep, adapt, or remove (directory map)
- [ ] Summarize all tuning/parameter changes (e.g., camera focal length, DT_MDL, service frequencies)
- [ ] Reference all historical commits or diffs that must be replicated for new ports
- [ ] List all manual install steps (e.g., `rknn-toolkit-lite2` wheel, Mali driver, IMU wiring if used)
- [ ] Add any additional notes for automation, CI, or AI-driven porting

---

## 🟨 Orange Pi 5 Porting: openpilot, release, scripts Folders

### openpilot
**Purpose:** Main process tree (selfdrive, controls, modeld, car, etc.)

**Orange Pi 5 relevance:**
- `selfdrive/modeld/models/` contains `.rknn` models for RK3588 NPU. These must match your NPU budget (see model inventory and NPU_AND_MODELS.md).
- `selfdrive/modeld/README.md` and `docs/NPU_AND_MODELS.md` describe model requirements, NPU utilization, and conversion steps.
- `selfdrive/camerad/` and `common/hardware/rk3588/` handle all camera and hardware specifics (CSI, RGA, NPU, GPIO, PCIe accel).

**Action:**
- Ensure all required `.rknn` models are present in `selfdrive/modeld/models/`.
- Use `tools/rknn/convert_detection_models.sh` on a desktop (x86_64) to convert ONNX models to `.rknn` for RK3588.
- Validate NPU utilization does not exceed 6.0 TOPS (see model inventory table).
- For new models, update the inventory and test with `common/hardware/rk3588/npu.py`.

---

### release
**Purpose:** Build and release scripts for packaging and deployment.

**Orange Pi 5 relevance:**
- Use `build_devel.sh` or `build_release.sh` for packaging the stack for Orange Pi 5.
- No RK3588-specific logic is needed; scripts are platform-agnostic.

**Action:**
- Run `./release/build_devel.sh` for development builds.
- Run `./release/build_release.sh` for production images.
- Validate output images on Orange Pi 5 hardware.

---

### scripts
**Purpose:** Utility scripts for deployment, camera HAL, power management, and validation.

**Orange Pi 5 relevance:**
- **`rk3588_secure_host.sh`**: Secure lockdown, OpenBLT flashing, and SSH lockdown for RK3588 hosts. Use for production deployment and firmware flashing. Example usage:
	```bash
	./scripts/rk3588_secure_host.sh --lock
	./scripts/rk3588_secure_host.sh --unlock
	./scripts/rk3588_secure_host.sh --status
	./scripts/rk3588_secure_host.sh --flash --image firmware.srec
	```
- **`setup_camera_hal_env.sh`**: Sets up environment variables and system settings for the unified Camera HAL. Run before launching camera daemons to ensure zero-copy and high-performance operation.
	```bash
	source ./scripts/setup_camera_hal_env.sh
	```
- **`verify_big_core_allocation.sh`**: Verifies that safety-critical daemons (e.g., `controlsd`, `modeld`, `stereod`) are running on the correct RK3588 big CPU cores with proper priorities. Example output:
	```bash
	./scripts/verify_big_core_allocation.sh
	# Shows which daemons are on big cores (4-7) and their priorities
	```
- **`disable-powersave.py`**: Disables power-saving features on the device to ensure maximum performance. Run at boot or before starting OpenPilot:
	```bash
	python3 ./scripts/disable-powersave.py
	```
- **`reset_eop_params.sh`**: Backs up and wipes `/data/params` after a migration (e.g., EOP_ → EP_ prefix). Use with caution:
	```bash
	./scripts/reset_eop_params.sh
	# Prompts for confirmation, backs up, wipes, and recreates params dir
	```

**Action:**
- Use these scripts for setup, validation, and troubleshooting on Orange Pi 5.
- Automate their invocation in deployment scripts or CI pipelines for consistent bring-up and validation.

---

### Porting/Validation Checklist (for Orange Pi 5)

- [ ] All required `.rknn` models present and validated in `selfdrive/modeld/models/`
- [ ] NPU utilization ≤ 6.0 TOPS (see model inventory)
- [ ] Camera HAL environment configured (`setup_camera_hal_env.sh`)
- [ ] Daemon core affinity and priorities verified (`verify_big_core_allocation.sh`)
- [ ] Power-saving disabled (`disable-powersave.py`)
- [ ] Secure host lockdown and firmware flashing as needed (`rk3588_secure_host.sh`)
- [ ] Params reset after migration (`reset_eop_params.sh`)
- [ ] Build and release scripts tested (`build_devel.sh`, `build_release.sh`)

---

**Tip:** For automation, chain these scripts in your deployment pipeline and validate each step with log output. For new repo ports, copy this checklist and adapt as needed.

## 🟦 Step 2: Camera HAL & Daemon Migration
**Unified interface for all daemons:**

```python
from common.hardware.rk3588.camera import (
	OX03C10Camera, CSICameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
```

**USB Camera Example:**
```python
from common.hardware.rk3588.camera import (
	UVCCamera, USBCameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
camera_config = USBCameraConfig(
	device_path=device_path,
	width=width, height=height, pixel_format=V4L2PixelFormat.YUYV,
	fps=fps, usb_port="auto", uvc_version="1.5",
	---
	# 🧠 Orange Pi 5 Minimal OpenPilot Porting Guide (IMX415, Vision+Policy Only)

	This file is a **maximal, AI-automatable knowledge base** for porting any OpenPilot-based repo to Orange Pi 5 (RK3588) with only a single IMX415 front camera and only the `driving_vision.rknn` and `driving_policy.rknn` models. All other features (driver monitoring, stereo, Bluetooth, voice, grid, ground, track, predict, side cameras, etc.) are disabled or removed. Use this as the only reference for automation or manual porting.

	---

	## 1. Directory Map: What to Keep, What to Remove

	**Keep/Adapt:**
	- `common/hardware/rk3588/` (all files, especially `camera/`, `npu.py`, `rga.py`, `hardware.py`)
	- `selfdrive/camerad/` (only for IMX415 front camera)
	- `selfdrive/modeld/` (only `driving_vision.rknn`, `driving_policy.rknn`, and their wrappers)
	- `selfdrive/controls/` (only `controlsd.py`, `plannerd.py`, `radard.py`)
	- `selfdrive/car/` (only your car's interface and CAN parser)
	- `cereal/` (all, for Cap'n Proto messaging)
	- `system/manager/`, `system/hardware/`, `system/camerad/` (minimal, see below)
	- `scripts/` (only `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`)

	**Remove/Disable:**
	- All `monitoringd`, `stereod`, `externald`, `gridd`, `groundd`, `trackd`, `predictd`, `bluetoothd`, `voice`, `side cameras`, `driver monitoring`, `USB cameras`, `mapd`, `joystickd`, `elm327d`, `webjoystick`, `plated`, `snapd`, `loopd`, `crashd`, `debrisd`, `test/` folders not needed for your car.

	---

	## 2. Hardware Detection: RK3588-Only

	**File:** `system/hardware/__init__.py`

	```python
	from openpilot.common.hardware.rk3588.hardware import RK3588Hardware
	HARDWARE = RK3588Hardware(detected=True)
	RK3588 = True
	PC = False
	```

	**Remove all other hardware detection logic.**

	---

	## 3. Camera HAL: IMX415 Front Camera Only

	**File:** `common/hardware/rk3588/camera/csi.py`

	```python
	from common.hardware.rk3588.camera.v4l2 import V4L2Camera, V4L2Config, V4L2PixelFormat
	from common.hardware.rk3588.camera.sensors import IMX415Driver

	config = V4L2Config(
			device_path="/dev/video0",  # IMX415 front camera
			width=1920, height=1080, pixel_format=V4L2PixelFormat.YUYV,
			fps=30, memory_strategy="default"
	)
	camera = V4L2Camera(config)
	sensor = IMX415Driver(config.device_path)
	sensor.initialize()
	```

	**Remove all OX03C10, OS04C10, USB, and stereo camera logic.**

	---

	## 4. Model Inventory: Only Vision + Policy

	**Directory:** `selfdrive/modeld/models/`

	**Keep only:**
	- `driving_vision.rknn`
	- `driving_policy.rknn`

	**Remove all other models (YOLO, segmentation, headpose, etc.).**

	---

	## 5. Model Loading: Minimal RKNN Wrappers

	**File:** `selfdrive/modeld/vision/driving_vision_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingVisionRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load vision RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init vision RKNN runtime"
			def infer(self, img):
					return self.rknn.inference(inputs=[img])
	```

	**File:** `selfdrive/modeld/vision/driving_policy_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingPolicyRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load policy RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init policy RKNN runtime"
			def infer(self, features):
					return self.rknn.inference(inputs=[features])
	```

	---

	## 6. Minimal modeld: Only Vision + Policy

	**File:** `selfdrive/modeld/modeld.py` (simplified)

	```python
	from selfdrive.modeld.vision.driving_vision_rknn import DrivingVisionRKNN
	from selfdrive.modeld.vision.driving_policy_rknn import DrivingPolicyRKNN

	vision = DrivingVisionRKNN("models/driving_vision.rknn")
	policy = DrivingPolicyRKNN("models/driving_policy.rknn")

	# Main loop: get camera frame, run vision, then policy, publish result
	while True:
			img = get_camera_frame()  # Use IMX415 camera only
			vision_out = vision.infer(img)
			policy_out = policy.infer(vision_out)
			publish(policy_out)
	```

	---

	## 7. Process Registry: Only Required Daemons

	**File:** `system/manager/process_config.py`

	```python
	from openpilot.system.manager.process import PythonProcess, NativeProcess

	procs = [
		PythonProcess("camerad", "selfdrive.camerad.camerad", always_run),
		PythonProcess("modeld", "selfdrive.modeld.modeld", always_run),
		PythonProcess("controlsd", "selfdrive.controls.controlsd", always_run),
		PythonProcess("plannerd", "selfdrive.controls.plannerd", always_run),
		PythonProcess("radard", "selfdrive.controls.radard", always_run),
		PythonProcess("car", "selfdrive.car.card", always_run),
	]
	managed_processes = {p.name: p for p in procs}
	```

	**Remove all other processes (monitoringd, stereod, externald, bluetoothd, etc.).**

	---

	## 8. Controls: Minimal

	**File:** `selfdrive/controls/controlsd.py` (keep only core control loop, remove all references to unused features)

	**File:** `selfdrive/controls/plannerd.py`, `selfdrive/controls/radard.py` (keep only core logic)

	---

	## 9. Car Interface: Minimal

	**File:** `selfdrive/car/<yourcar>/interface.py` (implement only CAN parsing and actuator commands for your car)

	---

	## 10. Messaging: Cereal

	**Keep all Cap'n Proto schemas and messaging code in `cereal/`.**

	---

	## 11. Scripts: Only What You Need

	- `scripts/setup_camera_hal_env.sh` (run before launching)
	- `scripts/disable-powersave.py` (run at boot)
	- `scripts/verify_big_core_allocation.sh` (validate core affinity)

	---

	## 12. Build & Run

	**Build:**
	```bash
	./release/build_devel.sh
	# or
	./release/build_release.sh
	```

	**Run:**
	```bash
	source ./scripts/setup_camera_hal_env.sh
	python3 -m selfdrive.camerad.camerad &
	python3 -m selfdrive.modeld.modeld &
	python3 -m selfdrive.controls.controlsd &
	python3 -m selfdrive.controls.plannerd &
	python3 -m selfdrive.controls.radard &
	python3 -m selfdrive.car.card &
	```

	---

	## 13. Porting/Validation Checklist (AI/Automation Ready)

	- [ ] Only `driving_vision.rknn` and `driving_policy.rknn` present in `selfdrive/modeld/models/`
	- [ ] Only IMX415 front camera enabled (no wide, stereo, USB, or driver monitoring)
	- [ ] Only Orange Pi 5 hardware detection logic present
	- [ ] Only required daemons enabled in process registry
	- [ ] All unused features/processes removed or disabled
	- [ ] Camera HAL and IMX415 driver validated
	- [ ] Controls and car interface minimal and correct
	- [ ] Scripts for camera HAL and power validated
	- [ ] Build and run scripts tested

	---

	## 🟧 Stability & Safety Guard Checklist (AI/Manual Porting)

	**Track and implement these before any road testing or production deployment.**

### Critical Safety/Robustness Fixes
- [ ] Replace all `assert` with `raise RuntimeError` in `rknn_runner.py` (asserts can be disabled, raising is always safe)
- [ ] Add null check on RKNN `outputs_get()` before indexing (raise if None)
- [ ] Add `np.isfinite()` guard on all NPU outputs before parsing (raise if NaN/Inf)
- [ ] Verify policy input key order matches RKNN model input order at startup (log both orders)
- [ ] Ensure `release()` is called on RKNNRunner at shutdown (use `atexit` or `try/finally` in modeld)
- [ ] Add camera reconnect/retry loop in `camera.py` (for CSI/USB disconnect resilience)
- [ ] Verify A76 core numbering: `cat /sys/devices/system/cpu/cpu{4..7}/cpufreq/cpuinfo_max_freq` (should be 2400000 for big cores)
- [ ] Add/verify heatsink + fan for sustained NPU performance (thermal throttling can cause >30ms inference)
- [ ] Broaden `/dev/rknpu0` check to also match `/dev/rknpu` (kernel naming varies)
- [ ] Add `__del__` guard in RKNNRunner to prevent double-release segfaults

### Operational/Deployment Gaps
- [ ] Add `rknn-toolkit-lite2` install instructions to setup scripts (cannot be in pyproject.toml, not on PyPI)
- [ ] Add thermal warning in UI/log if modelExecutionTime > 0.025s (optional, but recommended)
- [ ] Track and log all stability/safety checklist items in CI or deployment pipeline

---

## 🟧 Stability & Safety Guard Reference (Details)

**1. RKNN Error Handling:**
  - Replace all `assert` with `raise RuntimeError` in `rknn_runner.py`.
  - Add null check on `outputs_get()` before indexing.
  - Add `np.isfinite()` guard on all NPU outputs before parsing.

**2. Policy Input Order:**
  - At startup, print/log both the policy input dict key order and the RKNN model's expected input order. Confirm they match.

**3. RKNN Resource Management:**
  - Ensure `release()` is always called on RKNNRunner at shutdown (use `atexit` or `try/finally`).
  - Add `__del__` guard to RKNNRunner to prevent double-release segfaults.

**4. Camera Robustness:**
  - Add a reconnect/retry loop in `camera.py` for CSI/USB disconnects.

**5. Core Affinity & Thermal:**
  - Verify A76 core numbering on your kernel (should be 2400000 kHz for big cores).
  - Add/verify heatsink + fan for sustained NPU performance.
  - Add thermal warning in UI/log if modelExecutionTime > 0.025s.

**6. NPU Device Node Detection:**
  - Broaden `/dev/rknpu0` check to also match `/dev/rknpu`.

**7. RKNN Dependency:**
  - Add `rknn-toolkit-lite2` install instructions to setup scripts (manual pip install from Rockchip wheel).

**8. CI/Automation:**
  - Track and log all stability/safety checklist items in CI or deployment pipeline.

---

## 🟩 Final Checklist: What to Extract and Document in learn.md

- [ ] List all required `.rknn` models and their exact paths (e.g., `selfdrive/modeld/models/driving_vision.rknn`, `driving_policy.rknn`)
- [ ] Document all environment variables and feature flags needed (e.g., `USE_WEBCAM=1`, `NO_DM=1`, `ROAD_CAM` auto-detect)
- [ ] Summarize all process/daemon requirements (minimal list: `camerad`, `modeld`, `controlsd`, `plannerd`, `radard`, `card`, `socketd`)
- [ ] Specify all hardware abstraction and platform detection logic (e.g., RK3588 detection, NPU device node checks)
- [ ] List all scripts and utilities required for setup, validation, and deployment (e.g., `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`, `rk3588_secure_host.sh`)
- [ ] Document all code changes or diffs needed for porting (e.g., RKNN runner, modeld.py changes, SConscript skips, launch_env.sh env vars)
- [ ] Include all stability and safety guard checklist items (as above)
- [ ] Note all files/folders to keep, adapt, or remove (directory map)
- [ ] Summarize all tuning/parameter changes (e.g., camera focal length, DT_MDL, service frequencies)
- [ ] Reference all historical commits or diffs that must be replicated for new ports
- [ ] List all manual install steps (e.g., `rknn-toolkit-lite2` wheel, Mali driver, IMU wiring if used)
- [ ] Add any additional notes for automation, CI, or AI-driven porting

---

## 🟨 Orange Pi 5 Porting: openpilot, release, scripts Folders

### openpilot
**Purpose:** Main process tree (selfdrive, controls, modeld, car, etc.)

**Orange Pi 5 relevance:**
- `selfdrive/modeld/models/` contains `.rknn` models for RK3588 NPU. These must match your NPU budget (see model inventory and NPU_AND_MODELS.md).
- `selfdrive/modeld/README.md` and `docs/NPU_AND_MODELS.md` describe model requirements, NPU utilization, and conversion steps.
- `selfdrive/camerad/` and `common/hardware/rk3588/` handle all camera and hardware specifics (CSI, RGA, NPU, GPIO, PCIe accel).

**Action:**
- Ensure all required `.rknn` models are present in `selfdrive/modeld/models/`.
- Use `tools/rknn/convert_detection_models.sh` on a desktop (x86_64) to convert ONNX models to `.rknn` for RK3588.
- Validate NPU utilization does not exceed 6.0 TOPS (see model inventory table).
- For new models, update the inventory and test with `common/hardware/rk3588/npu.py`.

---

### release
**Purpose:** Build and release scripts for packaging and deployment.

**Orange Pi 5 relevance:**
- Use `build_devel.sh` or `build_release.sh` for packaging the stack for Orange Pi 5.
- No RK3588-specific logic is needed; scripts are platform-agnostic.

**Action:**
- Run `./release/build_devel.sh` for development builds.
- Run `./release/build_release.sh` for production images.
- Validate output images on Orange Pi 5 hardware.

---

### scripts
**Purpose:** Utility scripts for deployment, camera HAL, power management, and validation.

**Orange Pi 5 relevance:**
- **`rk3588_secure_host.sh`**: Secure lockdown, OpenBLT flashing, and SSH lockdown for RK3588 hosts. Use for production deployment and firmware flashing. Example usage:
	```bash
	./scripts/rk3588_secure_host.sh --lock
	./scripts/rk3588_secure_host.sh --unlock
	./scripts/rk3588_secure_host.sh --status
	./scripts/rk3588_secure_host.sh --flash --image firmware.srec
	```
- **`setup_camera_hal_env.sh`**: Sets up environment variables and system settings for the unified Camera HAL. Run before launching camera daemons to ensure zero-copy and high-performance operation.
	```bash
	source ./scripts/setup_camera_hal_env.sh
	```
- **`verify_big_core_allocation.sh`**: Verifies that safety-critical daemons (e.g., `controlsd`, `modeld`, `stereod`) are running on the correct RK3588 big CPU cores with proper priorities. Example output:
	```bash
	./scripts/verify_big_core_allocation.sh
	# Shows which daemons are on big cores (4-7) and their priorities
	```
- **`disable-powersave.py`**: Disables power-saving features on the device to ensure maximum performance. Run at boot or before starting OpenPilot:
	```bash
	python3 ./scripts/disable-powersave.py
	```
- **`reset_eop_params.sh`**: Backs up and wipes `/data/params` after a migration (e.g., EOP_ → EP_ prefix). Use with caution:
	```bash
	./scripts/reset_eop_params.sh
	# Prompts for confirmation, backs up, wipes, and recreates params dir
	```

**Action:**
- Use these scripts for setup, validation, and troubleshooting on Orange Pi 5.
- Automate their invocation in deployment scripts or CI pipelines for consistent bring-up and validation.

---

### Porting/Validation Checklist (for Orange Pi 5)

- [ ] All required `.rknn` models present and validated in `selfdrive/modeld/models/`
- [ ] NPU utilization ≤ 6.0 TOPS (see model inventory)
- [ ] Camera HAL environment configured (`setup_camera_hal_env.sh`)
- [ ] Daemon core affinity and priorities verified (`verify_big_core_allocation.sh`)
- [ ] Power-saving disabled (`disable-powersave.py`)
- [ ] Secure host lockdown and firmware flashing as needed (`rk3588_secure_host.sh`)
- [ ] Params reset after migration (`reset_eop_params.sh`)
- [ ] Build and release scripts tested (`build_devel.sh`, `build_release.sh`)

---

**Tip:** For automation, chain these scripts in your deployment pipeline and validate each step with log output. For new repo ports, copy this checklist and adapt as needed.

## 🟦 Step 2: Camera HAL & Daemon Migration
**Unified interface for all daemons:**

```python
from common.hardware.rk3588.camera import (
	OX03C10Camera, CSICameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
```

**USB Camera Example:**
```python
from common.hardware.rk3588.camera import (
	UVCCamera, USBCameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
camera_config = USBCameraConfig(
	device_path=device_path,
	width=width, height=height, pixel_format=V4L2PixelFormat.YUYV,
	fps=fps, usb_port="auto", uvc_version="1.5",
	---
	# 🧠 Orange Pi 5 Minimal OpenPilot Porting Guide (IMX415, Vision+Policy Only)

	This file is a **maximal, AI-automatable knowledge base** for porting any OpenPilot-based repo to Orange Pi 5 (RK3588) with only a single IMX415 front camera and only the `driving_vision.rknn` and `driving_policy.rknn` models. All other features (driver monitoring, stereo, Bluetooth, voice, grid, ground, track, predict, side cameras, etc.) are disabled or removed. Use this as the only reference for automation or manual porting.

	---

	## 1. Directory Map: What to Keep, What to Remove

	**Keep/Adapt:**
	- `common/hardware/rk3588/` (all files, especially `camera/`, `npu.py`, `rga.py`, `hardware.py`)
	- `selfdrive/camerad/` (only for IMX415 front camera)
	- `selfdrive/modeld/` (only `driving_vision.rknn`, `driving_policy.rknn`, and their wrappers)
	- `selfdrive/controls/` (only `controlsd.py`, `plannerd.py`, `radard.py`)
	- `selfdrive/car/` (only your car's interface and CAN parser)
	- `cereal/` (all, for Cap'n Proto messaging)
	- `system/manager/`, `system/hardware/`, `system/camerad/` (minimal, see below)
	- `scripts/` (only `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`)

	**Remove/Disable:**
	- All `monitoringd`, `stereod`, `externald`, `gridd`, `groundd`, `trackd`, `predictd`, `bluetoothd`, `voice`, `side cameras`, `driver monitoring`, `USB cameras`, `mapd`, `joystickd`, `elm327d`, `webjoystick`, `plated`, `snapd`, `loopd`, `crashd`, `debrisd`, `test/` folders not needed for your car.

	---

	## 2. Hardware Detection: RK3588-Only

	**File:** `system/hardware/__init__.py`

	```python
	from openpilot.common.hardware.rk3588.hardware import RK3588Hardware
	HARDWARE = RK3588Hardware(detected=True)
	RK3588 = True
	PC = False
	```

	**Remove all other hardware detection logic.**

	---

	## 3. Camera HAL: IMX415 Front Camera Only

	**File:** `common/hardware/rk3588/camera/csi.py`

	```python
	from common.hardware.rk3588.camera.v4l2 import V4L2Camera, V4L2Config, V4L2PixelFormat
	from common.hardware.rk3588.camera.sensors import IMX415Driver

	config = V4L2Config(
			device_path="/dev/video0",  # IMX415 front camera
			width=1920, height=1080, pixel_format=V4L2PixelFormat.YUYV,
			fps=30, memory_strategy="default"
	)
	camera = V4L2Camera(config)
	sensor = IMX415Driver(config.device_path)
	sensor.initialize()
	```

	**Remove all OX03C10, OS04C10, USB, and stereo camera logic.**

	---

	## 4. Model Inventory: Only Vision + Policy

	**Directory:** `selfdrive/modeld/models/`

	**Keep only:**
	- `driving_vision.rknn`
	- `driving_policy.rknn`

	**Remove all other models (YOLO, segmentation, headpose, etc.).**

	---

	## 5. Model Loading: Minimal RKNN Wrappers

	**File:** `selfdrive/modeld/vision/driving_vision_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingVisionRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load vision RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init vision RKNN runtime"
			def infer(self, img):
					return self.rknn.inference(inputs=[img])
	```

	**File:** `selfdrive/modeld/vision/driving_policy_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingPolicyRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load policy RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init policy RKNN runtime"
			def infer(self, features):
					return self.rknn.inference(inputs=[features])
	```

	---

	## 6. Minimal modeld: Only Vision + Policy

	**File:** `selfdrive/modeld/modeld.py` (simplified)

	```python
	from selfdrive.modeld.vision.driving_vision_rknn import DrivingVisionRKNN
	from selfdrive.modeld.vision.driving_policy_rknn import DrivingPolicyRKNN

	vision = DrivingVisionRKNN("models/driving_vision.rknn")
	policy = DrivingPolicyRKNN("models/driving_policy.rknn")

	# Main loop: get camera frame, run vision, then policy, publish result
	while True:
			img = get_camera_frame()  # Use IMX415 camera only
			vision_out = vision.infer(img)
			policy_out = policy.infer(vision_out)
			publish(policy_out)
	```

	---

	## 7. Process Registry: Only Required Daemons

	**File:** `system/manager/process_config.py`

	```python
	from openpilot.system.manager.process import PythonProcess, NativeProcess

	procs = [
		PythonProcess("camerad", "selfdrive.camerad.camerad", always_run),
		PythonProcess("modeld", "selfdrive.modeld.modeld", always_run),
		PythonProcess("controlsd", "selfdrive.controls.controlsd", always_run),
		PythonProcess("plannerd", "selfdrive.controls.plannerd", always_run),
		PythonProcess("radard", "selfdrive.controls.radard", always_run),
		PythonProcess("car", "selfdrive.car.card", always_run),
	]
	managed_processes = {p.name: p for p in procs}
	```

	**Remove all other processes (monitoringd, stereod, externald, bluetoothd, etc.).**

	---

	## 8. Controls: Minimal

	**File:** `selfdrive/controls/controlsd.py` (keep only core control loop, remove all references to unused features)

	**File:** `selfdrive/controls/plannerd.py`, `selfdrive/controls/radard.py` (keep only core logic)

	---

	## 9. Car Interface: Minimal

	**File:** `selfdrive/car/<yourcar>/interface.py` (implement only CAN parsing and actuator commands for your car)

	---

	## 10. Messaging: Cereal

	**Keep all Cap'n Proto schemas and messaging code in `cereal/`.**

	---

	## 11. Scripts: Only What You Need

	- `scripts/setup_camera_hal_env.sh` (run before launching)
	- `scripts/disable-powersave.py` (run at boot)
	- `scripts/verify_big_core_allocation.sh` (validate core affinity)

	---

	## 12. Build & Run

	**Build:**
	```bash
	./release/build_devel.sh
	# or
	./release/build_release.sh
	```

	**Run:**
	```bash
	source ./scripts/setup_camera_hal_env.sh
	python3 -m selfdrive.camerad.camerad &
	python3 -m selfdrive.modeld.modeld &
	python3 -m selfdrive.controls.controlsd &
	python3 -m selfdrive.controls.plannerd &
	python3 -m selfdrive.controls.radard &
	python3 -m selfdrive.car.card &
	```

	---

	## 13. Porting/Validation Checklist (AI/Automation Ready)

	- [ ] Only `driving_vision.rknn` and `driving_policy.rknn` present in `selfdrive/modeld/models/`
	- [ ] Only IMX415 front camera enabled (no wide, stereo, USB, or driver monitoring)
	- [ ] Only Orange Pi 5 hardware detection logic present
	- [ ] Only required daemons enabled in process registry
	- [ ] All unused features/processes removed or disabled
	- [ ] Camera HAL and IMX415 driver validated
	- [ ] Controls and car interface minimal and correct
	- [ ] Scripts for camera HAL and power validated
	- [ ] Build and run scripts tested

	---

	## 🟧 Stability & Safety Guard Checklist (AI/Manual Porting)

	**Track and implement these before any road testing or production deployment.**

### Critical Safety/Robustness Fixes
- [ ] Replace all `assert` with `raise RuntimeError` in `rknn_runner.py` (asserts can be disabled, raising is always safe)
- [ ] Add null check on RKNN `outputs_get()` before indexing (raise if None)
- [ ] Add `np.isfinite()` guard on all NPU outputs before parsing (raise if NaN/Inf)
- [ ] Verify policy input key order matches RKNN model input order at startup (log both orders)
- [ ] Ensure `release()` is called on RKNNRunner at shutdown (use `atexit` or `try/finally` in modeld)
- [ ] Add camera reconnect/retry loop in `camera.py` (for CSI/USB disconnect resilience)
- [ ] Verify A76 core numbering: `cat /sys/devices/system/cpu/cpu{4..7}/cpufreq/cpuinfo_max_freq` (should be 2400000 for big cores)
- [ ] Add/verify heatsink + fan for sustained NPU performance (thermal throttling can cause >30ms inference)
- [ ] Broaden `/dev/rknpu0` check to also match `/dev/rknpu` (kernel naming varies)
- [ ] Add `__del__` guard in RKNNRunner to prevent double-release segfaults

### Operational/Deployment Gaps
- [ ] Add `rknn-toolkit-lite2` install instructions to setup scripts (cannot be in pyproject.toml, not on PyPI)
- [ ] Add thermal warning in UI/log if modelExecutionTime > 0.025s (optional, but recommended)
- [ ] Track and log all stability/safety checklist items in CI or deployment pipeline

---

## 🟧 Stability & Safety Guard Reference (Details)

**1. RKNN Error Handling:**
  - Replace all `assert` with `raise RuntimeError` in `rknn_runner.py`.
  - Add null check on `outputs_get()` before indexing.
  - Add `np.isfinite()` guard on all NPU outputs before parsing.

**2. Policy Input Order:**
  - At startup, print/log both the policy input dict key order and the RKNN model's expected input order. Confirm they match.

**3. RKNN Resource Management:**
  - Ensure `release()` is always called on RKNNRunner at shutdown (use `atexit` or `try/finally`).
  - Add `__del__` guard to RKNNRunner to prevent double-release segfaults.

**4. Camera Robustness:**
  - Add a reconnect/retry loop in `camera.py` for CSI/USB disconnects.

**5. Core Affinity & Thermal:**
  - Verify A76 core numbering on your kernel (should be 2400000 kHz for big cores).
  - Add/verify heatsink + fan for sustained NPU performance.
  - Add thermal warning in UI/log if modelExecutionTime > 0.025s.

**6. NPU Device Node Detection:**
  - Broaden `/dev/rknpu0` check to also match `/dev/rknpu`.

**7. RKNN Dependency:**
  - Add `rknn-toolkit-lite2` install instructions to setup scripts (manual pip install from Rockchip wheel).

**8. CI/Automation:**
  - Track and log all stability/safety checklist items in CI or deployment pipeline.

---

## 🟩 Final Checklist: What to Extract and Document in learn.md

- [ ] List all required `.rknn` models and their exact paths (e.g., `selfdrive/modeld/models/driving_vision.rknn`, `driving_policy.rknn`)
- [ ] Document all environment variables and feature flags needed (e.g., `USE_WEBCAM=1`, `NO_DM=1`, `ROAD_CAM` auto-detect)
- [ ] Summarize all process/daemon requirements (minimal list: `camerad`, `modeld`, `controlsd`, `plannerd`, `radard`, `card`, `socketd`)
- [ ] Specify all hardware abstraction and platform detection logic (e.g., RK3588 detection, NPU device node checks)
- [ ] List all scripts and utilities required for setup, validation, and deployment (e.g., `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`, `rk3588_secure_host.sh`)
- [ ] Document all code changes or diffs needed for porting (e.g., RKNN runner, modeld.py changes, SConscript skips, launch_env.sh env vars)
- [ ] Include all stability and safety guard checklist items (as above)
- [ ] Note all files/folders to keep, adapt, or remove (directory map)
- [ ] Summarize all tuning/parameter changes (e.g., camera focal length, DT_MDL, service frequencies)
- [ ] Reference all historical commits or diffs that must be replicated for new ports
- [ ] List all manual install steps (e.g., `rknn-toolkit-lite2` wheel, Mali driver, IMU wiring if used)
- [ ] Add any additional notes for automation, CI, or AI-driven porting

---

## 🟨 Orange Pi 5 Porting: openpilot, release, scripts Folders

### openpilot
**Purpose:** Main process tree (selfdrive, controls, modeld, car, etc.)

**Orange Pi 5 relevance:**
- `selfdrive/modeld/models/` contains `.rknn` models for RK3588 NPU. These must match your NPU budget (see model inventory and NPU_AND_MODELS.md).
- `selfdrive/modeld/README.md` and `docs/NPU_AND_MODELS.md` describe model requirements, NPU utilization, and conversion steps.
- `selfdrive/camerad/` and `common/hardware/rk3588/` handle all camera and hardware specifics (CSI, RGA, NPU, GPIO, PCIe accel).

**Action:**
- Ensure all required `.rknn` models are present in `selfdrive/modeld/models/`.
- Use `tools/rknn/convert_detection_models.sh` on a desktop (x86_64) to convert ONNX models to `.rknn` for RK3588.
- Validate NPU utilization does not exceed 6.0 TOPS (see model inventory table).
- For new models, update the inventory and test with `common/hardware/rk3588/npu.py`.

---

### release
**Purpose:** Build and release scripts for packaging and deployment.

**Orange Pi 5 relevance:**
- Use `build_devel.sh` or `build_release.sh` for packaging the stack for Orange Pi 5.
- No RK3588-specific logic is needed; scripts are platform-agnostic.

**Action:**
- Run `./release/build_devel.sh` for development builds.
- Run `./release/build_release.sh` for production images.
- Validate output images on Orange Pi 5 hardware.

---

### scripts
**Purpose:** Utility scripts for deployment, camera HAL, power management, and validation.

**Orange Pi 5 relevance:**
- **`rk3588_secure_host.sh`**: Secure lockdown, OpenBLT flashing, and SSH lockdown for RK3588 hosts. Use for production deployment and firmware flashing. Example usage:
	```bash
	./scripts/rk3588_secure_host.sh --lock
	./scripts/rk3588_secure_host.sh --unlock
	./scripts/rk3588_secure_host.sh --status
	./scripts/rk3588_secure_host.sh --flash --image firmware.srec
	```
- **`setup_camera_hal_env.sh`**: Sets up environment variables and system settings for the unified Camera HAL. Run before launching camera daemons to ensure zero-copy and high-performance operation.
	```bash
	source ./scripts/setup_camera_hal_env.sh
	```
- **`verify_big_core_allocation.sh`**: Verifies that safety-critical daemons (e.g., `controlsd`, `modeld`, `stereod`) are running on the correct RK3588 big CPU cores with proper priorities. Example output:
	```bash
	./scripts/verify_big_core_allocation.sh
	# Shows which daemons are on big cores (4-7) and their priorities
	```
- **`disable-powersave.py`**: Disables power-saving features on the device to ensure maximum performance. Run at boot or before starting OpenPilot:
	```bash
	python3 ./scripts/disable-powersave.py
	```
- **`reset_eop_params.sh`**: Backs up and wipes `/data/params` after a migration (e.g., EOP_ → EP_ prefix). Use with caution:
	```bash
	./scripts/reset_eop_params.sh
	# Prompts for confirmation, backs up, wipes, and recreates params dir
	```

**Action:**
- Use these scripts for setup, validation, and troubleshooting on Orange Pi 5.
- Automate their invocation in deployment scripts or CI pipelines for consistent bring-up and validation.

---

### Porting/Validation Checklist (for Orange Pi 5)

- [ ] All required `.rknn` models present and validated in `selfdrive/modeld/models/`
- [ ] NPU utilization ≤ 6.0 TOPS (see model inventory)
- [ ] Camera HAL environment configured (`setup_camera_hal_env.sh`)
- [ ] Daemon core affinity and priorities verified (`verify_big_core_allocation.sh`)
- [ ] Power-saving disabled (`disable-powersave.py`)
- [ ] Secure host lockdown and firmware flashing as needed (`rk3588_secure_host.sh`)
- [ ] Params reset after migration (`reset_eop_params.sh`)
- [ ] Build and release scripts tested (`build_devel.sh`, `build_release.sh`)

---

**Tip:** For automation, chain these scripts in your deployment pipeline and validate each step with log output. For new repo ports, copy this checklist and adapt as needed.

## 🟦 Step 2: Camera HAL & Daemon Migration
**Unified interface for all daemons:**

```python
from common.hardware.rk3588.camera import (
	OX03C10Camera, CSICameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
```

**USB Camera Example:**
```python
from common.hardware.rk3588.camera import (
	UVCCamera, USBCameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
camera_config = USBCameraConfig(
	device_path=device_path,
	width=width, height=height, pixel_format=V4L2PixelFormat.YUYV,
	fps=fps, usb_port="auto", uvc_version="1.5",
	---
	# 🧠 Orange Pi 5 Minimal OpenPilot Porting Guide (IMX415, Vision+Policy Only)

	This file is a **maximal, AI-automatable knowledge base** for porting any OpenPilot-based repo to Orange Pi 5 (RK3588) with only a single IMX415 front camera and only the `driving_vision.rknn` and `driving_policy.rknn` models. All other features (driver monitoring, stereo, Bluetooth, voice, grid, ground, track, predict, side cameras, etc.) are disabled or removed. Use this as the only reference for automation or manual porting.

	---

	## 1. Directory Map: What to Keep, What to Remove

	**Keep/Adapt:**
	- `common/hardware/rk3588/` (all files, especially `camera/`, `npu.py`, `rga.py`, `hardware.py`)
	- `selfdrive/camerad/` (only for IMX415 front camera)
	- `selfdrive/modeld/` (only `driving_vision.rknn`, `driving_policy.rknn`, and their wrappers)
	- `selfdrive/controls/` (only `controlsd.py`, `plannerd.py`, `radard.py`)
	- `selfdrive/car/` (only your car's interface and CAN parser)
	- `cereal/` (all, for Cap'n Proto messaging)
	- `system/manager/`, `system/hardware/`, `system/camerad/` (minimal, see below)
	- `scripts/` (only `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`)

	**Remove/Disable:**
	- All `monitoringd`, `stereod`, `externald`, `gridd`, `groundd`, `trackd`, `predictd`, `bluetoothd`, `voice`, `side cameras`, `driver monitoring`, `USB cameras`, `mapd`, `joystickd`, `elm327d`, `webjoystick`, `plated`, `snapd`, `loopd`, `crashd`, `debrisd`, `test/` folders not needed for your car.

	---

	## 2. Hardware Detection: RK3588-Only

	**File:** `system/hardware/__init__.py`

	```python
	from openpilot.common.hardware.rk3588.hardware import RK3588Hardware
	HARDWARE = RK3588Hardware(detected=True)
	RK3588 = True
	PC = False
	```

	**Remove all other hardware detection logic.**

	---

	## 3. Camera HAL: IMX415 Front Camera Only

	**File:** `common/hardware/rk3588/camera/csi.py`

	```python
	from common.hardware.rk3588.camera.v4l2 import V4L2Camera, V4L2Config, V4L2PixelFormat
	from common.hardware.rk3588.camera.sensors import IMX415Driver

	config = V4L2Config(
			device_path="/dev/video0",  # IMX415 front camera
			width=1920, height=1080, pixel_format=V4L2PixelFormat.YUYV,
			fps=30, memory_strategy="default"
	)
	camera = V4L2Camera(config)
	sensor = IMX415Driver(config.device_path)
	sensor.initialize()
	```

	**Remove all OX03C10, OS04C10, USB, and stereo camera logic.**

	---

	## 4. Model Inventory: Only Vision + Policy

	**Directory:** `selfdrive/modeld/models/`

	**Keep only:**
	- `driving_vision.rknn`
	- `driving_policy.rknn`

	**Remove all other models (YOLO, segmentation, headpose, etc.).**

	---

	## 5. Model Loading: Minimal RKNN Wrappers

	**File:** `selfdrive/modeld/vision/driving_vision_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingVisionRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load vision RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init vision RKNN runtime"
			def infer(self, img):
					return self.rknn.inference(inputs=[img])
	```

	**File:** `selfdrive/modeld/vision/driving_policy_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingPolicyRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load policy RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init policy RKNN runtime"
			def infer(self, features):
					return self.rknn.inference(inputs=[features])
	```

	---

	## 6. Minimal modeld: Only Vision + Policy

	**File:** `selfdrive/modeld/modeld.py` (simplified)

	```python
	from selfdrive.modeld.vision.driving_vision_rknn import DrivingVisionRKNN
	from selfdrive.modeld.vision.driving_policy_rknn import DrivingPolicyRKNN

	vision = DrivingVisionRKNN("models/driving_vision.rknn")
	policy = DrivingPolicyRKNN("models/driving_policy.rknn")

	# Main loop: get camera frame, run vision, then policy, publish result
	while True:
			img = get_camera_frame()  # Use IMX415 camera only
			vision_out = vision.infer(img)
			policy_out = policy.infer(vision_out)
			publish(policy_out)
	```

	---

	## 7. Process Registry: Only Required Daemons

	**File:** `system/manager/process_config.py`

	```python
	from openpilot.system.manager.process import PythonProcess, NativeProcess

	procs = [
		PythonProcess("camerad", "selfdrive.camerad.camerad", always_run),
		PythonProcess("modeld", "selfdrive.modeld.modeld", always_run),
		PythonProcess("controlsd", "selfdrive.controls.controlsd", always_run),
		PythonProcess("plannerd", "selfdrive.controls.plannerd", always_run),
		PythonProcess("radard", "selfdrive.controls.radard", always_run),
		PythonProcess("car", "selfdrive.car.card", always_run),
	]
	managed_processes = {p.name: p for p in procs}
	```

	**Remove all other processes (monitoringd, stereod, externald, bluetoothd, etc.).**

	---

	## 8. Controls: Minimal

	**File:** `selfdrive/controls/controlsd.py` (keep only core control loop, remove all references to unused features)

	**File:** `selfdrive/controls/plannerd.py`, `selfdrive/controls/radard.py` (keep only core logic)

	---

	## 9. Car Interface: Minimal

	**File:** `selfdrive/car/<yourcar>/interface.py` (implement only CAN parsing and actuator commands for your car)

	---

	## 10. Messaging: Cereal

	**Keep all Cap'n Proto schemas and messaging code in `cereal/`.**

	---

	## 11. Scripts: Only What You Need

	- `scripts/setup_camera_hal_env.sh` (run before launching)
	- `scripts/disable-powersave.py` (run at boot)
	- `scripts/verify_big_core_allocation.sh` (validate core affinity)

	---

	## 12. Build & Run

	**Build:**
	```bash
	./release/build_devel.sh
	# or
	./release/build_release.sh
	```

	**Run:**
	```bash
	source ./scripts/setup_camera_hal_env.sh
	python3 -m selfdrive.camerad.camerad &
	python3 -m selfdrive.modeld.modeld &
	python3 -m selfdrive.controls.controlsd &
	python3 -m selfdrive.controls.plannerd &
	python3 -m selfdrive.controls.radard &
	python3 -m selfdrive.car.card &
	```

	---

	## 13. Porting/Validation Checklist (AI/Automation Ready)

	- [ ] Only `driving_vision.rknn` and `driving_policy.rknn` present in `selfdrive/modeld/models/`
	- [ ] Only IMX415 front camera enabled (no wide, stereo, USB, or driver monitoring)
	- [ ] Only Orange Pi 5 hardware detection logic present
	- [ ] Only required daemons enabled in process registry
	- [ ] All unused features/processes removed or disabled
	- [ ] Camera HAL and IMX415 driver validated
	- [ ] Controls and car interface minimal and correct
	- [ ] Scripts for camera HAL and power validated
	- [ ] Build and run scripts tested

	---

	## 🟧 Stability & Safety Guard Checklist (AI/Manual Porting)

	**Track and implement these before any road testing or production deployment.**

### Critical Safety/Robustness Fixes
- [ ] Replace all `assert` with `raise RuntimeError` in `rknn_runner.py` (asserts can be disabled, raising is always safe)
- [ ] Add null check on RKNN `outputs_get()` before indexing (raise if None)
- [ ] Add `np.isfinite()` guard on all NPU outputs before parsing (raise if NaN/Inf)
- [ ] Verify policy input key order matches RKNN model input order at startup (log both orders)
- [ ] Ensure `release()` is called on RKNNRunner at shutdown (use `atexit` or `try/finally` in modeld)
- [ ] Add camera reconnect/retry loop in `camera.py` (for CSI/USB disconnect resilience)
- [ ] Verify A76 core numbering: `cat /sys/devices/system/cpu/cpu{4..7}/cpufreq/cpuinfo_max_freq` (should be 2400000 for big cores)
- [ ] Add/verify heatsink + fan for sustained NPU performance (thermal throttling can cause >30ms inference)
- [ ] Broaden `/dev/rknpu0` check to also match `/dev/rknpu` (kernel naming varies)
- [ ] Add `__del__` guard in RKNNRunner to prevent double-release segfaults

### Operational/Deployment Gaps
- [ ] Add `rknn-toolkit-lite2` install instructions to setup scripts (cannot be in pyproject.toml, not on PyPI)
- [ ] Add thermal warning in UI/log if modelExecutionTime > 0.025s (optional, but recommended)
- [ ] Track and log all stability/safety checklist items in CI or deployment pipeline

---

## 🟧 Stability & Safety Guard Reference (Details)

**1. RKNN Error Handling:**
  - Replace all `assert` with `raise RuntimeError` in `rknn_runner.py`.
  - Add null check on `outputs_get()` before indexing.
  - Add `np.isfinite()` guard on all NPU outputs before parsing.

**2. Policy Input Order:**
  - At startup, print/log both the policy input dict key order and the RKNN model's expected input order. Confirm they match.

**3. RKNN Resource Management:**
  - Ensure `release()` is always called on RKNNRunner at shutdown (use `atexit` or `try/finally`).
  - Add `__del__` guard to RKNNRunner to prevent double-release segfaults.

**4. Camera Robustness:**
  - Add a reconnect/retry loop in `camera.py` for CSI/USB disconnects.

**5. Core Affinity & Thermal:**
  - Verify A76 core numbering on your kernel (should be 2400000 kHz for big cores).
  - Add/verify heatsink + fan for sustained NPU performance.
  - Add thermal warning in UI/log if modelExecutionTime > 0.025s.

**6. NPU Device Node Detection:**
  - Broaden `/dev/rknpu0` check to also match `/dev/rknpu`.

**7. RKNN Dependency:**
  - Add `rknn-toolkit-lite2` install instructions to setup scripts (manual pip install from Rockchip wheel).

**8. CI/Automation:**
  - Track and log all stability/safety checklist items in CI or deployment pipeline.

---

## 🟩 Final Checklist: What to Extract and Document in learn.md

- [ ] List all required `.rknn` models and their exact paths (e.g., `selfdrive/modeld/models/driving_vision.rknn`, `driving_policy.rknn`)
- [ ] Document all environment variables and feature flags needed (e.g., `USE_WEBCAM=1`, `NO_DM=1`, `ROAD_CAM` auto-detect)
- [ ] Summarize all process/daemon requirements (minimal list: `camerad`, `modeld`, `controlsd`, `plannerd`, `radard`, `card`, `socketd`)
- [ ] Specify all hardware abstraction and platform detection logic (e.g., RK3588 detection, NPU device node checks)
- [ ] List all scripts and utilities required for setup, validation, and deployment (e.g., `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`, `rk3588_secure_host.sh`)
- [ ] Document all code changes or diffs needed for porting (e.g., RKNN runner, modeld.py changes, SConscript skips, launch_env.sh env vars)
- [ ] Include all stability and safety guard checklist items (as above)
- [ ] Note all files/folders to keep, adapt, or remove (directory map)
- [ ] Summarize all tuning/parameter changes (e.g., camera focal length, DT_MDL, service frequencies)
- [ ] Reference all historical commits or diffs that must be replicated for new ports
- [ ] List all manual install steps (e.g., `rknn-toolkit-lite2` wheel, Mali driver, IMU wiring if used)
- [ ] Add any additional notes for automation, CI, or AI-driven porting

---

## 🟨 Orange Pi 5 Porting: openpilot, release, scripts Folders

### openpilot
**Purpose:** Main process tree (selfdrive, controls, modeld, car, etc.)

**Orange Pi 5 relevance:**
- `selfdrive/modeld/models/` contains `.rknn` models for RK3588 NPU. These must match your NPU budget (see model inventory and NPU_AND_MODELS.md).
- `selfdrive/modeld/README.md` and `docs/NPU_AND_MODELS.md` describe model requirements, NPU utilization, and conversion steps.
- `selfdrive/camerad/` and `common/hardware/rk3588/` handle all camera and hardware specifics (CSI, RGA, NPU, GPIO, PCIe accel).

**Action:**
- Ensure all required `.rknn` models are present in `selfdrive/modeld/models/`.
- Use `tools/rknn/convert_detection_models.sh` on a desktop (x86_64) to convert ONNX models to `.rknn` for RK3588.
- Validate NPU utilization does not exceed 6.0 TOPS (see model inventory table).
- For new models, update the inventory and test with `common/hardware/rk3588/npu.py`.

---

### release
**Purpose:** Build and release scripts for packaging and deployment.

**Orange Pi 5 relevance:**
- Use `build_devel.sh` or `build_release.sh` for packaging the stack for Orange Pi 5.
- No RK3588-specific logic is needed; scripts are platform-agnostic.

**Action:**
- Run `./release/build_devel.sh` for development builds.
- Run `./release/build_release.sh` for production images.
- Validate output images on Orange Pi 5 hardware.

---

### scripts
**Purpose:** Utility scripts for deployment, camera HAL, power management, and validation.

**Orange Pi 5 relevance:**
- **`rk3588_secure_host.sh`**: Secure lockdown, OpenBLT flashing, and SSH lockdown for RK3588 hosts. Use for production deployment and firmware flashing. Example usage:
	```bash
	./scripts/rk3588_secure_host.sh --lock
	./scripts/rk3588_secure_host.sh --unlock
	./scripts/rk3588_secure_host.sh --status
	./scripts/rk3588_secure_host.sh --flash --image firmware.srec
	```
- **`setup_camera_hal_env.sh`**: Sets up environment variables and system settings for the unified Camera HAL. Run before launching camera daemons to ensure zero-copy and high-performance operation.
	```bash
	source ./scripts/setup_camera_hal_env.sh
	```
- **`verify_big_core_allocation.sh`**: Verifies that safety-critical daemons (e.g., `controlsd`, `modeld`, `stereod`) are running on the correct RK3588 big CPU cores with proper priorities. Example output:
	```bash
	./scripts/verify_big_core_allocation.sh
	# Shows which daemons are on big cores (4-7) and their priorities
	```
- **`disable-powersave.py`**: Disables power-saving features on the device to ensure maximum performance. Run at boot or before starting OpenPilot:
	```bash
	python3 ./scripts/disable-powersave.py
	```
- **`reset_eop_params.sh`**: Backs up and wipes `/data/params` after a migration (e.g., EOP_ → EP_ prefix). Use with caution:
	```bash
	./scripts/reset_eop_params.sh
	# Prompts for confirmation, backs up, wipes, and recreates params dir
	```

**Action:**
- Use these scripts for setup, validation, and troubleshooting on Orange Pi 5.
- Automate their invocation in deployment scripts or CI pipelines for consistent bring-up and validation.

---

### Porting/Validation Checklist (for Orange Pi 5)

- [ ] All required `.rknn` models present and validated in `selfdrive/modeld/models/`
- [ ] NPU utilization ≤ 6.0 TOPS (see model inventory)
- [ ] Camera HAL environment configured (`setup_camera_hal_env.sh`)
- [ ] Daemon core affinity and priorities verified (`verify_big_core_allocation.sh`)
- [ ] Power-saving disabled (`disable-powersave.py`)
- [ ] Secure host lockdown and firmware flashing as needed (`rk3588_secure_host.sh`)
- [ ] Params reset after migration (`reset_eop_params.sh`)
- [ ] Build and release scripts tested (`build_devel.sh`, `build_release.sh`)

---

**Tip:** For automation, chain these scripts in your deployment pipeline and validate each step with log output. For new repo ports, copy this checklist and adapt as needed.

## 🟦 Step 2: Camera HAL & Daemon Migration
**Unified interface for all daemons:**

```python
from common.hardware.rk3588.camera import (
	OX03C10Camera, CSICameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
```

**USB Camera Example:**
```python
from common.hardware.rk3588.camera import (
	UVCCamera, USBCameraConfig, V4L2PixelFormat,
	AutoExposure, ExposureController
)
camera_config = USBCameraConfig(
	device_path=device_path,
	width=width, height=height, pixel_format=V4L2PixelFormat.YUYV,
	fps=fps, usb_port="auto", uvc_version="1.5",
	---
	# 🧠 Orange Pi 5 Minimal OpenPilot Porting Guide (IMX415, Vision+Policy Only)

	This file is a **maximal, AI-automatable knowledge base** for porting any OpenPilot-based repo to Orange Pi 5 (RK3588) with only a single IMX415 front camera and only the `driving_vision.rknn` and `driving_policy.rknn` models. All other features (driver monitoring, stereo, Bluetooth, voice, grid, ground, track, predict, side cameras, etc.) are disabled or removed. Use this as the only reference for automation or manual porting.

	---

	## 1. Directory Map: What to Keep, What to Remove

	**Keep/Adapt:**
	- `common/hardware/rk3588/` (all files, especially `camera/`, `npu.py`, `rga.py`, `hardware.py`)
	- `selfdrive/camerad/` (only for IMX415 front camera)
	- `selfdrive/modeld/` (only `driving_vision.rknn`, `driving_policy.rknn`, and their wrappers)
	- `selfdrive/controls/` (only `controlsd.py`, `plannerd.py`, `radard.py`)
	- `selfdrive/car/` (only your car's interface and CAN parser)
	- `cereal/` (all, for Cap'n Proto messaging)
	- `system/manager/`, `system/hardware/`, `system/camerad/` (minimal, see below)
	- `scripts/` (only `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`)

	**Remove/Disable:**
	- All `monitoringd`, `stereod`, `externald`, `gridd`, `groundd`, `trackd`, `predictd`, `bluetoothd`, `voice`, `side cameras`, `driver monitoring`, `USB cameras`, `mapd`, `joystickd`, `elm327d`, `webjoystick`, `plated`, `snapd`, `loopd`, `crashd`, `debrisd`, `test/` folders not needed for your car.

	---

	## 2. Hardware Detection: RK3588-Only

	**File:** `system/hardware/__init__.py`

	```python
	from openpilot.common.hardware.rk3588.hardware import RK3588Hardware
	HARDWARE = RK3588Hardware(detected=True)
	RK3588 = True
	PC = False
	```

	**Remove all other hardware detection logic.**

	---

	## 3. Camera HAL: IMX415 Front Camera Only

	**File:** `common/hardware/rk3588/camera/csi.py`

	```python
	from common.hardware.rk3588.camera.v4l2 import V4L2Camera, V4L2Config, V4L2PixelFormat
	from common.hardware.rk3588.camera.sensors import IMX415Driver

	config = V4L2Config(
			device_path="/dev/video0",  # IMX415 front camera
			width=1920, height=1080, pixel_format=V4L2PixelFormat.YUYV,
			fps=30, memory_strategy="default"
	)
	camera = V4L2Camera(config)
	sensor = IMX415Driver(config.device_path)
	sensor.initialize()
	```

	**Remove all OX03C10, OS04C10, USB, and stereo camera logic.**

	---

	## 4. Model Inventory: Only Vision + Policy

	**Directory:** `selfdrive/modeld/models/`

	**Keep only:**
	- `driving_vision.rknn`
	- `driving_policy.rknn`

	**Remove all other models (YOLO, segmentation, headpose, etc.).**

	---

	## 5. Model Loading: Minimal RKNN Wrappers

	**File:** `selfdrive/modeld/vision/driving_vision_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingVisionRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load vision RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init vision RKNN runtime"
			def infer(self, img):
					return self.rknn.inference(inputs=[img])
	```

	**File:** `selfdrive/modeld/vision/driving_policy_rknn.py`

	```python
	from rknnlite.api import RKNNLite
	from pathlib import Path

	class DrivingPolicyRKNN:
			def __init__(self, model_path, use_npu_cores="all"):
					self.model_path = Path(model_path)
					self.rknn = RKNNLite(verbose=False)
					ret = self.rknn.load_rknn(str(self.model_path))
					assert ret == 0, f"Failed to load policy RKNN: {self.model_path}"
					ret = self.rknn.init_runtime(core_mask=7)
					assert ret == 0, f"Failed to init policy RKNN runtime"
			def infer(self, features):
					return self.rknn.inference(inputs=[features])
	```

	---

	## 6. Minimal modeld: Only Vision + Policy

	**File:** `selfdrive/modeld/modeld.py` (simplified)

	```python
	from selfdrive.modeld.vision.driving_vision_rknn import DrivingVisionRKNN
	from selfdrive.modeld.vision.driving_policy_rknn import DrivingPolicyRKNN

	vision = DrivingVisionRKNN("models/driving_vision.rknn")
	policy = DrivingPolicyRKNN("models/driving_policy.rknn")

	# Main loop: get camera frame, run vision, then policy, publish result
	while True:
			img = get_camera_frame()  # Use IMX415 camera only
			vision_out = vision.infer(img)
			policy_out = policy.infer(vision_out)
			publish(policy_out)
	```

	---

	## 7. Process Registry: Only Required Daemons

	**File:** `system/manager/process_config.py`

	```python
	from openpilot.system.manager.process import PythonProcess, NativeProcess

	procs = [
		PythonProcess("camerad", "selfdrive.camerad.camerad", always_run),
		PythonProcess("modeld", "selfdrive.modeld.modeld", always_run),
		PythonProcess("controlsd", "selfdrive.controls.controlsd", always_run),
		PythonProcess("plannerd", "selfdrive.controls.plannerd", always_run),
		PythonProcess("radard", "selfdrive.controls.radard", always_run),
		PythonProcess("car", "selfdrive.car.card", always_run),
	]
	managed_processes = {p.name: p for p in procs}
	```

	**Remove all other processes (monitoringd, stereod, externald, bluetoothd, etc.).**

	---

	## 8. Controls: Minimal

	**File:** `selfdrive/controls/controlsd.py` (keep only core control loop, remove all references to unused features)

	**File:** `selfdrive/controls/plannerd.py`, `selfdrive/controls/radard.py` (keep only core logic)

	---

	## 9. Car Interface: Minimal

	**File:** `selfdrive/car/<yourcar>/interface.py` (implement only CAN parsing and actuator commands for your car)

	---

	## 10. Messaging: Cereal

	**Keep all Cap'n Proto schemas and messaging code in `cereal/`.**

	---

	## 11. Scripts: Only What You Need

	- `scripts/setup_camera_hal_env.sh` (run before launching)
	- `scripts/disable-powersave.py` (run at boot)
	- `scripts/verify_big_core_allocation.sh` (validate core affinity)

	---

	## 12. Build & Run

	**Build:**
	```bash
	./release/build_devel.sh
	# or
	./release/build_release.sh
	```

	**Run:**
	```bash
	source ./scripts/setup_camera_hal_env.sh
	python3 -m selfdrive.camerad.camerad &
	python3 -m selfdrive.modeld.modeld &
	python3 -m selfdrive.controls.controlsd &
	python3 -m selfdrive.controls.plannerd &
	python3 -m selfdrive.controls.radard &
	python3 -m selfdrive.car.card &
	```

	---

	## 13. Porting/Validation Checklist (AI/Automation Ready)

	- [ ] Only `driving_vision.rknn` and `driving_policy.rknn` present in `selfdrive/modeld/models/`
	- [ ] Only IMX415 front camera enabled (no wide, stereo, USB, or driver monitoring)
	- [ ] Only Orange Pi 5 hardware detection logic present
	- [ ] Only required daemons enabled in process registry
	- [ ] All unused features/processes removed or disabled
	- [ ] Camera HAL and IMX415 driver validated
	- [ ] Controls and car interface minimal and correct
	- [ ] Scripts for camera HAL and power validated
	- [ ] Build and run scripts tested

	---

	## 🟧 Stability & Safety Guard Checklist (AI/Manual Porting)

	**Track and implement these before any road testing or production deployment.**

### Critical Safety/Robustness Fixes
- [ ] Replace all `assert` with `raise RuntimeError` in `rknn_runner.py` (asserts can be disabled, raising is always safe)
- [ ] Add null check on RKNN `outputs_get()` before indexing (raise if None)
- [ ] Add `np.isfinite()` guard on all NPU outputs before parsing (raise if NaN/Inf)
- [ ] Verify policy input key order matches RKNN model input order at startup (log both orders)
- [ ] Ensure `release()` is called on RKNNRunner at shutdown (use `atexit` or `try/finally` in modeld)
- [ ] Add camera reconnect/retry loop in `camera.py` (for CSI/USB disconnect resilience)
- [ ] Verify A76 core numbering: `cat /sys/devices/system/cpu/cpu{4..7}/cpufreq/cpuinfo_max_freq` (should be 2400000 for big cores)
- [ ] Add/verify heatsink + fan for sustained NPU performance (thermal throttling can cause >30ms inference)
- [ ] Broaden `/dev/rknpu0` check to also match `/dev/rknpu` (kernel naming varies)
- [ ] Add `__del__` guard in RKNNRunner to prevent double-release segfaults

### Operational/Deployment Gaps
- [ ] Add `rknn-toolkit-lite2` install instructions to setup scripts (cannot be in pyproject.toml, not on PyPI)
- [ ] Add thermal warning in UI/log if modelExecutionTime > 0.025s (optional, but recommended)
- [ ] Track and log all stability/safety checklist items in CI or deployment pipeline

---

## 🟧 Stability & Safety Guard Reference (Details)

**1. RKNN Error Handling:**
  - Replace all `assert` with `raise RuntimeError` in `rknn_runner.py`.
  - Add null check on `outputs_get()` before indexing.
  - Add `np.isfinite()` guard on all NPU outputs before parsing.

**2. Policy Input Order:**
  - At startup, print/log both the policy input dict key order and the RKNN model's expected input order. Confirm they match.

**3. RKNN Resource Management:**
  - Ensure `release()` is always called on RKNNRunner at shutdown (use `atexit` or `try/finally`).
  - Add `__del__` guard to RKNNRunner to prevent double-release segfaults.

**4. Camera Robustness:**
  - Add a reconnect/retry loop in `camera.py` for CSI/USB disconnects.

**5. Core Affinity & Thermal:**
  - Verify A76 core numbering on your kernel (should be 2400000 kHz for big cores).
  - Add/verify heatsink + fan for sustained NPU performance.
  - Add thermal warning in UI/log if modelExecutionTime > 0.025s.

**6. NPU Device Node Detection:**
  - Broaden `/dev/rknpu0` check to also match `/dev/rknpu`.

**7. RKNN Dependency:**
  - Add `rknn-toolkit-lite2` install instructions to setup scripts (manual pip install from Rockchip wheel).

**8. CI/Automation:**
  - Track and log all stability/safety checklist items in CI or deployment pipeline.

---

## 🟩 Final Checklist: What to Extract and Document in learn.md

- [ ] List all required `.rknn` models and their exact paths (e.g., `selfdrive/modeld/models/driving_vision.rknn`, `driving_policy.rknn`)
- [ ] Document all environment variables and feature flags needed (e.g., `USE_WEBCAM=1`, `NO_DM=1`, `ROAD_CAM` auto-detect)
- [ ] Summarize all process/daemon requirements (minimal list: `camerad`, `modeld`, `controlsd`, `plannerd`, `radard`, `card`, `socketd`)
- [ ] Specify all hardware abstraction and platform detection logic (e.g., RK3588 detection, NPU device node checks)
- [ ] List all scripts and utilities required for setup, validation, and deployment (e.g., `setup_camera_hal_env.sh`, `disable-powersave.py`, `verify_big_core_allocation.sh`, `rk3588_secure_host.sh`)
- [ ] Document all code changes or diffs needed for porting (e.g., RKNN runner, modeld.py changes, SConscript skips, launch_env.sh env vars)
- [ ] Include all stability and safety guard checklist items (as above)
- [ ] Note all files/folders to keep, adapt, or remove (directory map)
- [ ] Summarize all tuning/parameter changes (e.g., camera focal length, DT_MDL, service frequencies)
- [ ] Reference all historical commits or diffs that must be replicated for new ports
- [ ] List all manual install steps (e.g., `rknn-toolkit-lite2` wheel, Mali driver, IMU wiring if used)
- [ ] Add any additional notes for automation, CI, or AI-driven porting

---

## 🟨 Orange Pi 5 Porting: openpilot, release, scripts Folders

### openpilot
**Purpose:** Main process tree (selfdrive, controls, modeld, car, etc.)

**Orange Pi 5 relevance:**
- `selfdrive/modeld/models/` contains `.rknn` models for RK3588 NPU. These must match your NPU budget (see model inventory and NPU_AND_MODELS.md).
- `selfdrive/modeld/README.md` and `docs/NPU_AND_MODELS.md` describe model requirements, NPU utilization, and conversion steps.
- `selfdrive/camerad/` and `common/hardware/rk3588/` handle all camera and hardware specifics (CSI, RGA, NPU, GPIO, PCIe accel


🟦 Essential Folders and Files to Port for Orange Pi 5 (RK3588)
Keep/Adapt:

rk3588 (all files: camera, npu.py, rga.py, hardware.py, etc.)
models (only: driving_vision.rknn, driving_policy.rknn, and their metadata)
rknn_runner.py (RKNN wrapper)
modeld.py (with RKNN path and core pinning)
camerad (only for IMX415 front camera, minimal)
controls (only: controlsd.py, plannerd.py, radard.py)
car (only your car's interface and CAN parser, plus card.py)
socketd.py (CAN bridge for BlackPanda)
cereal (all: Cap'n Proto schemas, messaging)
manager, hardware, camerad (minimal, for process registry, hardware detection, and camera integration)
scripts (only: setup_camera_hal_env.sh, disable-powersave.py, verify_big_core_allocation.sh, rk3588_secure_host.sh, install-autostart.sh)
Remove/Disable:

All monitoringd, stereod, externald, gridd, groundd, trackd, predictd, bluetoothd, voice, side cameras, driver monitoring, USB cameras, mapd, joystickd, elm327d, webjoystick, plated, snapd, loopd, crashd, debrisd, and any test/ folders not needed for your car.
Summary:

Only port the minimal set required for IMX415 front camera, vision+policy RKNN models, CAN interface (BlackPanda), and core OpenPilot daemons.
All other features, daemons, and hardware integrations should be removed or disabled for a clean, fast, and maintainable Orange Pi 5 port.

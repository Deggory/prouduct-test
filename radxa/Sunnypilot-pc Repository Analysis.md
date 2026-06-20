# Sunnypilot-pc Repository Analysis

This repository is a fork of sunnypilot (which is itself a fork of comma.ai's openpilot) specifically modified to run on standard PC/Linux architectures (aarch64/x86_64) using webcams instead of dedicated MIPI CSI cameras. 

Here is the breakdown of the directory and file structure, highlighting what is relevant to your Radxa Dragon Q8B port.

---

## 1. Root Directory Files

### Core Build & Configuration
*   **`SConstruct`**: The build system file for `scons`. This dictates how the C++ code is compiled. Since you are on ARM64 (aarch64), you likely won't need to touch this unless specific Qualcomm flags are missing.
*   **`Dockerfile.openpilot` / `Dockerfile.openpilot_base`**: Used to build the containerized environment. Comma runs openpilot in Docker. For your Q8B, you can either build inside Docker or natively on Ubuntu.
*   **`.python-version`**: Specifies the Python version (usually 3.8 or 3.11). Ensure your Q8B has this version.
*   **`launch_chffrplus.sh` / `launch_openpilot.sh`**: Shell scripts to start the openpilot process.
*   **`launch_env.sh`**: **(Important)** This script sets up environment variables. This is where you will define `USE_WEBCAM=1` and `WEBCAM_DEVICE="/dev/video0"` for your Q8B setup.

### Documentation
*   **`README.md`**: Overview of the fork.
*   **`CHANGELOGS.md` / `RELEASES.md`**: Version history.
*   **`HOW-TOS.md` / `FEATURES.md`**: Guides for sunnypilot-specific features.

---

## 2. Core Directories

### `selfdrive/` (The Heart of the System)
This folder contains 95% of the active code. It is divided into several subdirectories:

#### `selfdrive/manager/`
*   **`manager.py`**: The main orchestrator. It starts, stops, and monitors all the individual daemons (camerad, modeld, ui, etc.). If a daemon crashes, manager restarts it.
*   **`manage_*.py`**: Defines the process list for different car brands or configurations.

#### `selfdrive/camerad/` (Camera Daemon - CRITICAL FOR Q8B)
*   This is the C++ daemon that reads camera frames.
*   In standard openpilot, this is highly tied to the Snapdragon ISP (Spectra 280).
*   **In `sunnypilot-pc`**, this folder is heavily modified to support standard V4L2 (Video4Linux2) webcams. 
*   **What to check**: Look for a file like `webcam.cc` or camera drivers that use `O_RDWR` and `V4L2_CAP_VIDEO_CAPTURE`. If the repo is set up correctly, setting `USE_WEBCAM=1` will route execution to these files instead of the Qualcomm ISP files.

#### `selfdrive/modeld/` (AI Inference Daemon - CRITICAL FOR Q8B)
*   **`modeld.cc` / `runners/`**: Contains the ONNX Runtime logic.
*   **What to check**: Standard openpilot uses ONNX Runtime with an OpenCL execution provider to run on the Adreno GPU. You need to verify that this fork hasn't been modified to force CPU inference or x86-specific CUDA/TensorRT.
*   **Action**: Ensure the ONNX Runtime shared libraries (`.so` files) in this folder or in `third_party/` are compiled for `aarch64` (ARM64). If they are for x86, you will need to replace them with ARM64 versions.

#### `selfdrive/boardd/` (CAN Bus Daemon)
*   **`boardd.cc`**: Communicates with the CAN bus interface.
*   In Comma 3x, this talks to the TDA4VM over Ethernet. In your setup, this will eventually talk to a USB-to-CAN adapter.
*   **What to check**: Ensure it supports SocketCAN. If it only looks for a "Panda" (Comma's hardware), you may need to run it in a simulated or bypass mode for now.

#### `selfdrive/controls/` (Vehicle Control Logic)
*   **`controlsd.py`**: The main Python loop that reads model predictions and CAN data, then calculates steering torque and acceleration.
*   This is pure Python and should run identically on the Q8B as on a Comma 3x.

#### `selfdrive/ui/` (User Interface)
*   **`ui.cc` / `qt/`**: The Qt-based user interface.
*   **What to check**: Ensure it uses standard Qt5/Qt6. The Q8B's Adreno 740 GPU should easily handle the Qt rendering via OpenGL/Vulkan.

#### `selfdrive/locationd/` (Positioning & Sensor Fusion)
*   Handles GPS, accelerometers, and gyroscopes to determine vehicle position.
*   For desktop testing, this is usually bypassed or fed simulated data.

---

### `cereal/` (Messaging System)
*   This is openpilot's custom pub/sub messaging system (built on Cap'n Proto).
*   All daemons communicate via cereal messages (e.g., `camerad` publishes `Image`, `modeld` subscribes to `Image`).
*   **Action**: You don't need to modify this, but you must run `scons` to generate the C++ and Python bindings from the `.capnp` files.

### `common/`
*   Shared utility functions, matrix math, and hardware abstraction macros.
*   **What to check**: Look for `hardware/` or files defining the target architecture. Ensure it isn't hardcoding SDM845 specific paths (like `/sys/kernel/debug/msm_vidc/` for video encoding).

### `opendbc/`
*   Contains DBC (Database CAN) files for hundreds of car models.
*   These are plain text files defining how to translate raw CAN bus frames into engineering values (speed, steering angle, etc.).
*   You will need these later when you connect your USB-to-CAN adapter.

### `panda/`
*   Firmware and drivers for the Comma Panda (CAN bus dongle).
*   Since you are using a generic USB-to-CAN adapter later, you likely won't flash this firmware, but `boardd` uses the Python files here to structure CAN messages.

### `body/`
*   Code specific to the Comma Body (a 2-wheel balancing robot). You can ignore this folder.

### `tools/`
*   Miscellaneous scripts: simulators, data replay tools, and flashing utilities.
*   **What to check**: Look for `sim/` or `replay/`. These tools are incredibly useful for testing your Q8B setup without actually driving a car. You can feed prerecorded video and CAN data into the system to verify the UI and AI model work.

### `installer/` & `scripts/`
*   Setup scripts. 
*   **What to check**: `scripts/` often contains `reset_defines.py` or hardware setup scripts. Look at `installer/custom` to see if the fork has specific PC setup instructions.

### `third_party/`
*   Pre-compiled libraries.
*   **CRITICAL**: This is where the biggest Q8B compatibility risk lies. 
*   Openpilot relies on specific ONNX Runtime, OpenCL, and Vulkan libraries. If `third_party/` contains `.so` files compiled for x86_64, they will crash on your aarch64 Q8B. You may need to download the ARM64 versions of ONNX Runtime and replace them here.

---

## 3. Summary: What to Modify for Radxa Dragon Q8B

1.  **Environment (`launch_env.sh` or terminal)**: 
    *   `export USE_WEBCAM=1`
    *   `export WEBCAM_DEVICE="/dev/video0"`
    *   This activates the PC-specific V4L2 camera code in `selfdrive/camerad/`.

2.  **Libraries (`third_party/` and `selfdrive/modeld/`)**:
    *   Verify ONNX Runtime `.so` files are ARM64. If not, replace them.
    *   Verify OpenCL is correctly routed to the Mesa/Freedreno driver for the Adreno 740.

3.  **CAN Bus (`selfdrive/boardd/`)**:
    *   Since you are dropping CAN for now, check if there is an environment variable like `export BOARD=fake` or `export SIMULATION=1` to prevent `boardd` from crashing when it doesn't find a Panda.

4.  **Build**:
    *   Run `scons -j$(nproc)` from the root directory. This will compile C++ files and generate `cereal` bindings.

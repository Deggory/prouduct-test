# File-by-File Porting Guide: Sunnypilot-pc to Radxa Q8B

**Target OS:** Ubuntu 24.04 (aarch64)
**Target Board:** Radxa Dragon Q8B (Snapdragon 8cx Gen 3, Adreno 740 GPU)
**Goal:** Run sunnypilot-pc using a single IMX414 webcam.

Since the maintainer uses standard ONNX Runtime on the GPU, we do not need to rewrite AI code. However, Ubuntu 24.04 introduces Python 3.12 and stricter library paths, which requires specific tweaks.

---

## 1. Root Directory (`/`)

### `SConstruct`
*   **What it is:** The main build configuration file for `scons`.
*   **Action:** **MODIFY**.
    *   Ubuntu 24.04 uses Python 3.12. Scons sometimes struggles to find the correct Python paths.
    *   Open this file and ensure the Python include paths point to `python3.12`.
    *   If you see hardcoded flags for `mali` or `rockchip` (e.g., `-lMali` or `-lrknn`), delete them and replace with standard Linux defaults.

### `launch_env.sh`
*   **What it is:** Script that exports environment variables before launching.
*   **Action:** **MODIFY (CRITICAL)**.
    *   Add the following lines to force webcam mode and define your camera:
    ```bash
    export USE_WEBCAM=1
    export WEBCAM_DEVICE="/dev/video0" # Verify this path with `ls /dev/video*`
    export WEBCAM_WIDTH=1920
    export WEBCAM_HEIGHT=1080
    export WEBCAM_FPS=30
    # Disable real CAN board lookup (prevents boardd crashes)
    export BOARD=fake
    ```

### `launch_openpilot.sh`
*   **What it is:** The main startup script.
*   **Action:** **REVIEW ONLY**. Ensure it calls `launch_env.sh` before starting `manager.py`.

---

## 2. `third_party/` (Dependencies)

### `third_party/onnxruntime/`
*   **What it is:** Pre-compiled ONNX Runtime libraries for AI inference.
*   **Action:** **MODIFY (CRITICAL)**.
    *   Run `file third_party/onnxruntime/libonnxruntime.so`.
    *   If it is NOT `aarch64`, you must replace it. Download the `onnxruntime-linux-aarch64` release from Microsoft's GitHub, extract it, and overwrite the `.so` file here.
    *   **Ubuntu 24.04 Note:** Ensure you also install `libstdc++` and `libc6` updates, as ONNX Runtime expects modern C++ standard libraries.

### `third_party/capnp/` / `third_party/cereal/`
*   **What it is:** Messaging protocol libraries.
*   **Action:** **REVIEW ONLY**. `scons` will compile these natively for your Q8B.

---

## 3. `selfdrive/camerad/` (Camera Pipeline)

### `selfdrive/camerad/cameras/camera_webcam.cc` (or similar V4L2 file)
*   **What it is:** The C++ code that reads frames from a webcam using Video4Linux2 (V4L2).
*   **Action:** **MODIFY (CRITICAL FOR IMX414)**.
    *   Because you are using **one camera** instead of three, but the AI model expects three inputs, you must modify this file to duplicate your single IMX414 frame.
    *   Find the buffer copying logic (usually involving `mmap` or `memcpy`).
    *   **Logic to add:** When a frame is captured from `/dev/video0`, copy it into the `main` camera buffer, copy it again into the `wide` camera buffer, and write zeroes (black frame) to the `driver` monitoring buffer.
    *   *Code concept:*
    ```cpp
    // After reading frame from V4L2
    memcpy(buf_main->addr, v4l2_buffer, frame_size);
    memcpy(buf_wide->addr, v4l2_buffer, frame_size); // Duplicate for wide
    memset(buf_driver->addr, 0, frame_size); // Black frame for driver
    ```

### `selfdrive/camerad/main.cc`
*   **What it is:** The entry point for the camera daemon.
*   **Action:** **REVIEW ONLY**. Ensure it checks for the `USE_WEBCAM` env variable and routes to the webcam code instead of Qualcomm ISP code.

---

## 4. `selfdrive/modeld/` (AI Inference)

### `selfdrive/modeld/runners/onnx_runner.cc` (or similar)
*   **What it is:** The C++ wrapper that loads `supercombo.onnx` and executes it.
*   **Action:** **REVIEW ONLY**.
    *   Verify which Execution Provider it uses. Look for strings like `OpenCL`, `CUDA`, or `CPU`.
    *   If it says `CUDAExecutionProvider`, change it to `OpenCLExecutionProvider` or `CPUExecutionProvider` (OpenCL is preferred for the Adreno 740).

### `selfdrive/modeld/models/drivingvigi.h` / `drivingmodel.cc`
*   **What it is:** Definitions for the driving model inputs/outputs.
*   **Action:** **REVIEW ONLY**. Ensure the input tensor shapes match your 1-camera setup (though the duplication in `camera_webcam.cc` usually handles this).

---

## 5. `selfdrive/boardd/` (CAN Bus)

### `selfdrive/boardd/boardd.cc`
*   **What it is:** Communicates with the car's CAN bus.
*   **Action:** **MODIFY (TEMPORARY)**.
    *   Since you are not using CAN right now, `boardd` will crash looking for a Comma Panda or USB CAN adapter.
    *   Either comment out `boardd` from `selfdrive/manager/manager.py` (see below), or set `BOARD=fake` in `launch_env.sh`.

---

## 6. `selfdrive/manager/` (System Orchestrator)

### `selfdrive/manager/manager.py`
*   **What it is:** The Python script that starts all daemons (`camerad`, `modeld`, `ui`, `boardd`).
*   **Action:** **MODIFY (CRITICAL)**.
    *   Open this file. Look for the process list.
    *   Find the line that starts `boardd` and comment it out:
    ```python
    # "boardd": ...,  # Comment this out for now
    ```
    *   *Alternative:* Use the `BOARD=fake` env variable if the code supports it (openpilot usually does).

---

## 7. `selfdrive/ui/` (User Interface)

### `selfdrive/ui/ui.cc` / `selfdrive/ui/qt/`
*   **What it is:** The Qt-based graphical interface.
*   **Action:** **REVIEW ONLY**.
    *   The Q8B's Adreno 740 GPU will handle Qt rendering easily via standard OpenGL/Vulkan.
    *   If the UI fails to launch with an `EGL` or `GLX` error, run:
    ```bash
    export QT_QPA_PLATFORM=wayland  # or linuxfb
    ```

---

## 8. `common/` (Shared Code)

### `common/params.h` / `params.cc`
*   **What it is:** System parameters and configuration storage.
*   **Action:** **MODIFY (URGENT FOR UBUNTU 24.04)**.
    *   openpilot writes parameters to `/data/params`. Ubuntu 24.04 restricts writing to root paths.
    *   Find where the base directory is defined.
    *   Change it from `/data/params` to a local directory: `/home/youruser/sunnypilot_data/params`.

---

## 9. `tools/` (Utilities)

### `tools/sim/` or `tools/replay/`
*   **What it all is:** Simulation and replay scripts.
*   **Action:** **USE FOR TESTING**.
    *   Before taking the Q8B to a car, run the replay tool to feed prerecorded video and CAN data into sunnypilot. This verifies your UI, AI model, and camera pipeline work without needing a car.

---

## Summary Checklist for Ubuntu 24.04 + Q8B

1.  ✅ **OS Drivers:** Install `mesa-opencl-icd`, `mesa-vulkan-drivers`, `v4l-utils`.
2.  ✅ **Python 3.12:** Verify `python3 --version` is 3.12 (Ubuntu 24.04 default).
3.  1. Install OS drivers (`mesa-opencl-icd`, `mesa-vulkan-drivers`, `v4l-utils`).
4.  2. Verify Python 3.12 (Ubuntu 24.04 default).
5.  3. Modify `launch_env.sh` (Set `USE_WEBCAM=1` and `BOARD=fake`).
6.  4. Check/Replace `third_party/onnxruntime/libonnxruntime.so` (Must be aarch64).
7.  5. Modify `selfdrive/camerad/cameras/camera_webcam.cc` (Duplicate IMX414 frame to `main` and `wide`, black out `driver`).
8.  6. Modify `common/params.cc` (Change `/data/params` to local home directory).
9.  7. Run `scons -j$(nproc)`.
10. 8. Launch: `./launch_openpilot.sh`.

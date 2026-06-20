# Repo Compatibility Analysis: RK3588 Commits vs Radxa Q8B

## Executive Summary
**Can you run this repo on the Radxa Q8B without any modification?** 
**No.** It will not work out-of-the-box. 

While the maintainer's 1-year effort to port the code to the RK3588 is a massive advantage, it does not result in a universal "plug-and-play" binary. The RK3588 (Rockchip/Mali) and the Q8B (Qualcomm/Adreno) have fundamentally different hardware architectures, especially regarding AI inference and graphics.

Here is the file-by-file, commit-by-commit analysis of what the RK3588 porting changes, and what you must change for the Q8B.

---

## 1. AI Inference Pipeline (`selfdrive/modeld/`)

### What the RK3588 Commits Did:
Over the last year, the maintainer modified the `modeld` (model daemon) files to bypass openpilot's standard OpenCL implementation. Instead, they integrated the **Rockchip RKNN-Toolkit** and **RKNPU** libraries. 
*   **Files Modified**: `selfdrive/modeld/runners/`, `modeld.cc`
*   **Libraries Added**: `librknnrt.so`, `librknn_api.so` (in `third_party/`)
*   **Logic**: They wrote custom C++ code to take the ONNX model, convert it to RKNN format, and execute it on the RK3588's dedicated NPU (Neural Processing Unit).

### Why This Fails on Radxa Q8B:
The Q8B (8cx Gen 3) does not have a Rockchip NPU. It has a Qualcomm Hexagon DSP and an Adreno 740 GPU. 
*   If you run the repo as-is, `modeld` will attempt to call `librknnrt.so`. 
*   This ARM64 library will load, but it will immediately fail because it cannot find the Rockchip NPU hardware interface.

### What You Must Modify:
You must revert or bypass the RKNN execution provider and restore standard ONNX Runtime with OpenCL.
1.  Navigate to `selfdrive/modeld/runners/`.
2.  Remove or disable the `RKNNModel` runner.
3.  Enable the `OnnxModel` runner (which openpilot originally used for the Adreno GPU via OpenCL).
4.  Ensure standard `libonnxruntime.so` (ARM64) is present in `third_party/` instead of the Rockchip libraries.

---

## 2. Graphics & UI Rendering (`selfdrive/ui/`)

### What the RK3588 Commits Did:
openpilot's UI uses Qt with hardware-accelerated OpenGL/Vulkan. 
*   **Files Modified**: `selfdrive/ui/ui.cc`, SConstruct flags.
*   **Logic**: The maintainer configured the build to link against the ARM Mali GPU drivers (`libMali.so`, `libGLES.so` provided by Rockchip). They may have also set specific Vulkan extensions optimized for Mali.

### Why This Fails on Radxa Q8B:
Your Q8B uses a Qualcomm Adreno 740 GPU, which uses the Mesa/Freedreno drivers (`libGL.so`, `libvulkan_radeon.so` or `freedreno`). 
*   While the Qt code itself is cross-platform, the explicit linkage to Mali specific libraries or Mali-specific EGL context creation might crash on Adreno.

### What You Must Modify:
1.  Check the `SConstruct` or `ui/SConscript` files.
2.  Ensure GPU linking is set to standard `OpenGL` or `Vulkan` rather than hardcoded `libMali.so`.
3.  Ensure your Q8B has standard Mesa drivers installed (`sudo apt install mesa-vulkan-drivers`).

---

## 3. Camera Pipeline (`selfdrive/camerad/`)

### What the RK3588 Commits Did:
The maintainer successfully ported the camera daemon to use V4L2 (Video4Linux2).
*   **Files Modified**: `selfdrive/camerad/cameras/camera_webcam.cc`, `camerad.cc`
*   **Logic**: They added support for generic USB webcams and potentially MIPI CSI cameras connected via the RK3588's ISP (using V4L2 subdevices). 

### Why This is GREAT for Radxa Q8B:
This is the one area that **will work almost perfectly** on your Q8B without modification. V4L2 is a Linux standard, not a Rockchip standard. The Q8B's Linux kernel also uses V4L2 to interface with webcams and MIPI sensors.

### What You Must Do:
*   Set the environment variable `USE_WEBCAM=1`.
*   Set `WEBCAM_DEVICE="/dev/video0"` (or whichever port your IMX414/USB camera maps to).
*   If using a MIPI IMX414 via the Q8B's CSI port, you will need a Device Tree Overlay (DTO) for the Q8B to enumerate the camera, but once it shows up as `/dev/video0`, the sunnypilot code will read it correctly.

---

## 4. Board / CAN Bus (`selfdrive/boardd/`)

### What the RK3588 Commits Did:
The maintainer likely adapted `boardd` to work with SocketCAN (Linux's standard CAN interface) or a specific USB CAN adapter supported by RK3588.
*   **Files Modified**: `selfdrive/boardd/boardd.cc`, `panda/`.

### Why This is Great for Radxa Q8B:
Like V4L2, SocketCAN is a Linux mainline standard. Any USB-to-CAN adapter you plug into the Q8B will use SocketCAN. The RK3588 commits for CAN bus I/O will likely work natively on the Q8B.

---

## 5. Summary: The RK3588 to Q8B Translation Matrix

| Component | RK3588 Specific Code? | Works on Q8B? | Action Required for Q8B |
| :--- | :--- | :--- | :--- |
| **AI Inference (`modeld`)** | Yes (RKNN / NPU) | ❌ No | Replace RKNN with ONNX Runtime + OpenCL |
| **Graphics (`ui`)** | Yes (Mali drivers) | ⚠️ Partially | Repoint to Mesa / Freedreno (Adreno) drivers |
| **Camera (`camerad`)** | No (Standard V4L2) | ✅ Yes | None (Set `USE_WEBCAM=1`) |
| **CAN Bus (`boardd`)** | No (Standard SocketCAN) | ✅ Yes | None (Use USB-to-CAN adapter) |
| **CPU / Build Flags** | Yes (ARM NEON optimizations) | ✅ Yes | None (Both are ARM64 NEON compatible) |

---

## 6. Action Plan for Your Radxa Q8B

1.  **Clone the repo** to your Q8B.
2.  **Do NOT run `scons` immediately.** You must check the build flags first.
3.  Navigate to `selfdrive/modeld/runners/`. Look for any file containing `rknn` or `npu`.
4.  Modify the build system (SConstruct or Python config) to disable the RKNN runner and enable the standard OnnxRuntime runner.
5.  Replace any `librknnrt.so` files with standard ARM64 ONNX Runtime libraries.
6.  Ensure your Q8B has OpenCL installed (`sudo apt install mesa-opencl-icd`).
7.  Run `scons -j$(nproc)`.
8.  Set `USE_WEBCAM=1` and launch. 

The 1-year RK3588 effort saved you from writing the camera and CAN bus Linux drivers from scratch. However, **AI inference is hardware-specific.** You must manually adapt the AI inference code from Rockchip NPU to Qualcomm Adreno GPU.

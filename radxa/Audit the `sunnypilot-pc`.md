Role: Senior Open Source Engineer / Embedded Linux Expert

Task: Audit the `sunnypilot-pc` repository for portability to the **Radxa Dragon Q8B** (Snapdragon 8cx Gen 3) on **Ubuntu 24.04 (aarch64)**.

Hardware Context:
- SoC: Qualcomm Snapdragon 8cx Gen 3
- GPU: Adreno 740 (Uses OpenCL/Vulkan via Mesa/Freedreno drivers)
- Camera: Single Webcam via V4L2 (Simulating 3-camera input, no RGA hardware)
- OS: Ubuntu 24.04 (aarch64), User Mode (No root access to /data)
- Requirements: Must run in "Fake Car" / Dashcam mode without real CAN hardware.

Audit Instructions:
Analyze the codebase (specifically `selfdrive/modeld`, `selfdrive/camerad`, `third_party/`, `common/params.cc`, `selfdrive/manager/manager.py`) and provide a status checklist:

| Audit Category | Status (Done / In Progress / Not Done) | Notes / Specific Files to Check |
| :--- | :--- | :--- |
| **1. Build System** | | |
| | Is the code compiled for aarch64 (ARM64)? | Check `SConstruct` and pre-compiled binaries in `third_party/`. |
| | Are there hardcoded Rockchip (RK3588) or Mali flags? | Look for `-lrknn`, `-lmali`, or Rockchip-specific paths. |
| **2. AI Inference** | | |
| | Is ONNX Runtime set to use the GPU (OpenCL)? | Check `selfdrive/modeld/runners/` for execution provider settings. |
| | Are the ONNX Runtime libraries ARM64? | Run `file libonnxruntime.so`. It must say "ELF 64-bit LSB shared object, ARM aarch64". |
| **3. Camera Pipeline** | | |
| | Is V4L2 (Webcam mode) implemented? | Check `selfdrive/camerad/cameras/`. Look for `USE_WEBCAM` logic. |
| | Is it set up for a single IMX414 input? | Does the code handle 1 input instead of 3? |
| **4. System Paths** | | |
| | Does it use `/data/params` (requires root)? | Check `common/params.cc`. Must be changed to a local home directory path. |
| **5. Simulation** | | |
| | Does it support `BOARD=fake` or `SIMULATION=1`? | Check `selfdrive/boardd/` and `manager.py` to see how ignition state is handled. |

Please analyze the current state of the repo against these criteria and list what is already implemented, what is missing, and what specific code blocks you would need to modify to get this running on the Radxa Q8B.

# Sunnypilot-pc on Radxa Dragon Q8B: Simplified Setup Guide

By utilizing the built-in **webcam mode** and bypassing the CAN bus for now, the porting effort drops from "major hardware integration" to a **standard Linux software build and configuration** task. 

Here is your focused roadmap to get sunnypilot-pc running on the 8cx Gen 3.

---

## 1. Prerequisites: OS & Drivers

Since you are using UEFI on the 8cx Gen 3, install a standard ARM64 Linux distribution (Ubuntu 22.04+ or Armbian).

### 1.1 Install Base Dependencies
```bash
sudo apt update
sudo apt install -y \
  git build-essential cmake python3-pip \
  libopencv-dev qtbase5-dev libqt5gui5 \
  libusb-1.0-0-dev libcapnp-dev capnproto \
  mesa-vulkan-drivers mesa-opencl-icd \
  v4l-utils
```

### 1.2 Verify GPU Compute (Crucial for Inference)
Since we are bypassing the DSP, the Adreno 740 GPU must handle AI inference. Verify the Mesa Freedreno drivers are loaded:
```bash
# Check OpenCL support (clinfo might need installing: sudo apt install clinfo)
clinfo | grep "Device Name"

# Check Vulkan support
vulkaninfo --summary | grep "Device Name"
```
*You should see "Adreno (TM) 740" or similar. If yes, you are ready for GPU inference.*

---

## 2. Build Sunnypilot-pc

### 2.1 Clone the Repository
```bash
git clone https://github.com/Deggory/sunnypilot-pc.git
cd sunnypilot-pc
git submodule update --init --recursive
```

### 2.2 Compile
The sunnypilot-pc project typically uses `scons` or `make`. Check the repo for the exact command, but it usually looks like this:

```bash
# If it uses Scons
scons -j$(nproc)

# If it uses standard Make
make -j$(nproc)
```
*Note: Ensure your compiler targets `aarch64`. The default `gcc` on the Q8B will do this natively.*

---

## 3. Configure Webcam Mode

Since you are bypassing the SDM845 ISP, you need to tell sunnypilot to read from a standard V4L2 (Video4Linux2) webcam.

### 3.1 Find your Webcam
Plug in your USB webcam and find its device path:
```bash
v4l2-ctl --list-devices
# Look for /dev/video0 or /dev/video1
```

### 3.2 Set Environment Variables
Sunnypilot-pc (and openpilot) uses environment variables to switch input modes. Before running the executable, set these in your terminal:

```bash
# Use the standard webcam input instead of the Snapdragon ISP
export USE_WEBCAM=1

# Set the specific video device (change if yours is video1)
export WEBCAM_DEVICE="/dev/video0"

# Set desired resolution and fps (ensure your webcam supports this)
export WEBCAM_WIDTH=1920
export WEBCAM_HEIGHT=1080
export WEBCAM_FPS=30

# Optional: If the build system requires you to specify the model format
# export MODEL_PATH="/path/to/supercombo.onnx"
```

---

## 4. Run the Application

With the environment variables set, launch the UI and vision pipeline:

```bash
./sunnypilot  # (or whatever the compiled binary is named, e.g., ./ui, ./selfdrive)
```

If everything is wired up correctly, you should see the Qt-based UI launch, and the webcam feed should appear on the screen. The AI model inference will either run on the CPU or the Adreno GPU (depending on how the repo's ONNX/TFLite runtime is configured).

---

## 5. Troubleshooting on 8cx Gen 3

### Issue 1: "No camera found"
Run `v4l2-ctl --list-devices` again. Some webcams map to `/dev/video1` for video and `/dev/video0` for metadata. Try switching the `WEBCAM_DEVICE` variable.

### Issue 2: UI launches but extremely slow / low FPS
The model might be running on the CPU. Check your CPU usage (`htop`). If your CPU is maxed out, you need to configure the inference engine to use OpenCL or Vulkan. Look in the sunnypilot configuration files for a `runtime` setting and change it from `cpu` to `opencl` or `vulkan`.

### Issue 3: Thermal Throttling
The 8cx Gen 3 is powerful but can heat up during sustained AI inference. If performance drops after a few minutes, check temperatures:
```bash
watch -n 1 cat /sys/class/thermal/thermal_zone*/temp
```
Consider adding a small active cooler (fan) over the Q8B heatsink.

### Issue 4: Missing Qt Platform Plugin
If you get an error like `Could not initialize EGL`, try running:
```bash
export QT_QPA_PLATFORM=linuxfb
# or
export QT_QPA_PLATFORM=wayland
```

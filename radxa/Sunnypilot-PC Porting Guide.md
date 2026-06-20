# Sunnypilot-PC Porting Guide: Radxa Dragon Q8B

## Executive Summary

**Target Board**: Radxa Dragon Q8B (Snapdragon 8cx Gen 3)  
**Source Repository**: `https://github.com/Deggory/sunnypilot-pc.git`  
**Original Target**: Snapdragon 845 (SDM845) based devices  

Porting sunnypilot-pc from SDM845 to the 8cx Gen 3 is **feasible** because both processors share Qualcomm's architectural lineage (Kryo CPU cores, Adreno GPU, Hexagon DSP). However, the board targets differ significantly.

---

## 1. Hardware & Architecture Comparison

| Feature | Original Target (SDM845) | New Target (8cx Gen 3) | Impact |
|---------|-------------------------|------------------------|--------|
| **CPU** | 4x Kryo 385 Gold (2.8GHz) + 4x Silver (1.8GHz) | 4x Kryo Prime (3.0GHz) + 4x Gold (2.4GHz) | ⚠️ Performance improvement; potential thermal throttling logic mismatch. |
| **GPU** | Adreno 630 | Adreno 740 | ⚠️ Driver binaries differ. OpenCL/Vulkan compute shaders may need updated dispatch logic. |
| **DSP/AI** | Hexagon 685 DSP | Hexagon (29+ TOPS) | ✅ Hexagon SDK should be backward compatible, but direct memory access (DMA) paths may differ. |
| **Camera ISP** | Spectra 280 | Spectra 690 | 🔴 **High Risk**: Camera frame formats, MIPI CSI lane configs, and ISP tuning data are entirely different. |
| **OS Boot** | ABL (Android Bootloader) | UEFI | ⚠️ Driver loading mechanism changes from Android-style to Linux mainline. |
| **Linux Support** | Vendor + Mainline (Partial) | UEFI Mainline (Strong Qualcomm Upstreaming) | ✅ Better mainline kernel support; less reliance on vendor trees. |

---

## 2. Pre-Port Checklist: Environment Setup

### 2.1 Operating System Recommendation
Install **Ubuntu 22.04 LTS (ARM64)** via UEFI on the Dragon Q8B. The 8cx Gen 3 has excellent mainline support, making generic ARM distributions viable without custom kernel trees.

### 2.2 Toolchain
```bash
# Install cross-compilation toolchain if building on x86 host
sudo apt update
sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu \
    build-essential cmake git python3-pip \
    libopencv-dev clang-format
```

### 2.3 Clone & Build (Initial Attempt)
```bash
git clone https://github.com/Deggory/sunnypilot-pc.git
cd sunnypilot-pc
git submodule update --init --recursive

# Check build system (CMake/SCons/Makefile)
# Attempt initial build to identify missing dependencies
```

---

## 3. Porting Strategy: Component by Component

### Phase 1: Boot & Base OS (Low Risk)
The Dragon Q8B uses standard UEFI booting. Unlike the SDM845 (which often uses Android Bootloader), device tree loading is standard.

**Action Items:**
1. Ensure the Linux kernel includes `sc8280xp` (8cx Gen 3 SoC family) device tree support.
2. Verify `CONFIG_ARCH_QCOM` and `CONFIG_PCIE_QCOM` are enabled in the kernel config.
3. Check that PCIe devices (M.2 slots, 2.5GbE) are enumerated at boot:
   ```bash
   lspci -vv
   ip link show  # Verify both 2.5GbE interfaces
   ```

### Phase 2: Camera & Vision Pipeline (High Risk)
Sunnypilot relies on a camera input stream. The SDM845 uses the Spectra 280 ISP; the 8cx Gen 3 uses the Spectra 690.

**Action Items:**
1. **Avoid Direct ISP Access**: Do not attempt to port vendor-specific ISP tuning blobs. Instead, use standard V4L2 (Video4Linux2) interfaces.
2. **USB Camera Alternative**: For initial testing, connect a USB 3.0 camera and modify the input source in sunnypilot's camera config:
   ```yaml
   # Example config modification
   camera:
     input_type: "v4l2"
     device_path: "/dev/video0"
     resolution: "1920x1080"
     fps: 30
   ```
3. **MIPI CSI Camera (If required)**:
   - The Dragon Q8B may expose MIPI CSI via an FPC connector.
   - You will need a new device tree overlay for your specific camera module (e.g., IMX477).
   - Example DTS fragment:
     ```dts
     &camss {
         status = "okay";
         ports {
             port@0 {
                 reg = <0>;
                 endpoint {
                     remote-endpoint = <&cam_sensor_out>;
                     data-lanes = <1 2 3 4>;
                 };
             };
         };
     };
     ```
4. **Frame Format**: The SDM845 may output NV12 or BG10. Check what the 8cx Gen 3 V4L2 driver reports and adapt the format conversion in sunnypilot:
   ```bash
   v4l2-ctl --list-formats-ext -d /dev/video0
   ```

### Phase 3: GPU Compute (Adreno 630 → Adreno 740)
Sunnypilot uses the GPU for model inference (via OpenCL or Vulkan).

**Action Items:**
1. **Install Freedreno (Mesa) Drivers**:
   The 8cx Gen 3's Adreno 740 is supported by the open-source `freedreno` driver in Mesa.
   ```bash
   sudo apt install mesa-vulkan-drivers mesa-opencl-icd
   ```
2. **Verify GPU Detection**:
   ```bash
   vulkaninfo | grep "Device Name"
   clinfo  # For OpenCL
   ```
3. **Shader Compilation**: If sunnypilot ships pre-compiled Adreno 630 shader binaries, they must be recompiled. OpenCL kernels (.cl files) are usually portable, but SPIR-V binaries may not be.
4. **Thermal Throttling**: The 8cx Gen 3 is a 7W TDP part. If sunnypilot was tuned for a phone (5W), adjust power profiles:
   ```bash
   # Check available thermal zones
   cat /sys/class/thermal/thermal_zone*/type
   # Set performance governor
   echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
   ```

### Phase 4: AI/Model Inference (Hexagon DSP)
The original SDM845 port likely uses the Qualcomm Neural Processing SDK (SNPE) or QNN to offload inference to the Hexagon DSP.

**Action Items:**
1. **SNPE/QNN Compatibility**: Download the latest QNN SDK from Qualcomm. The 8cx Gen 3's Hexagon tensor cores are fully backwards compatible with SNPE models compiled for SDM845.
2. **Library Paths**: Update the library path in the build scripts from `aarch64-android` to `aarch64-ubuntu` or `aarch64-linux`.
3. **DSP Runtime**: On the SDM845, the DSP is accessed via FastRPC over `/dev/ion` or `/dev/dsp`. On the 8cx Gen 3 with a mainline Linux kernel, check:
   ```bash
   ls -la /dev/dsp* /dev/ion /dev/fastrpc*
   ```
   If these nodes are missing, you must either:
   - Use the GPU (Adreno 740) fallback for inference instead of DSP.
   - Compile and load the `fastrpc` kernel module.
4. **Model Conversion**: Re-quantize models for the 8cx Gen 3's Hexagon architecture:
   ```bash
   # Using QNN SDK tools
   qnn-onnx-converter --input_model model.onnx --output_path model_q8b.cpp
   qnn-model-lib-generator -c model_q8b.cpp -b model_q8b.bin
   ```

### Phase 5: Vehicle CAN Bus I/O
Sunnypilot communicates with the vehicle via CAN bus.

**Action Items:**
1. **CAN Interface**: The Dragon Q8B does not have a built-in CAN controller. You must use a **USB-to-CAN adapter** (e.g., CANable, PCAN-USB, or a Comma.ai Red Panda).
2. **Kernel Modules**: Ensure the appropriate kernel module is loaded for your adapter:
   ```bash
   # For SocketCAN compatible adapters (e.g., CANable)
   sudo modprobe gs_usb
   # Or for FTDI based adapters
   sudo modprobe ftdi_sio
   ```
3. **Interface Configuration**:
   ```bash
   sudo ip link set can0 type can bitrate 500000
   sudo ip link set can0 up
   candump can0  # Verify traffic
   ```

---

## 4. Build & Execution Workflow

### 4.1 Dependency Matrix
| Dependency | SDM845 Requirement | 8cx Gen 3 Status | Action |
|------------|--------------------|--------------------|--------|
| Qt5/Qt6 | Required for UI | Available via apt | `sudo apt install qtbase5-dev` |
| OpenCV | Vision processing | Available via apt | `sudo apt install libopencv-dev` |
| OpenCL | GPU compute | Available via Mesa | `sudo apt install mesa-opencl-icd` |
| SNPE/QNN | DSP inference | Manual install | Download from Qualcomm Developer Network |
| libusb | CAN/Panda dongle | Available via apt | `sudo apt install libusb-1.0-0-dev` |
| capnp | Messaging (Sunnypilot) | Build from source or apt | `sudo apt install capnproto libcapnp-dev` |

### 4.2 Build Commands
```bash
# Navigate to repo
cd sunnypilot-pc

# Example: If using CMake (adapt to actual build system)
mkdir build && cd build
cmake .. \
    -DCMAKE_SYSTEM_NAME=Linux \
    -DCMAKE_SYSTEM_PROCESSOR=aarch64 \
    -DTARGET_SOC=sdm8cxgen3 \
    -DUSE_GPU_INFERENCE=ON \
    -DUSE_DSP_INFERENCE=OFF  # Disable until fastrpc is confirmed working

make -j$(nproc)
```

### 4.3 Runtime Configuration
Create or modify the configuration file to point to the correct device paths:
```bash
# /etc/sunnypilot/config.ini
[Camera]
device=/dev/video0
format=NV12
width=1920
height=1080

[Can]
bus=can0
speed=500000

[Model]
runtime=opencl
model_path=/opt/sunnypilot/models/supercombo.onnx
```

---

## 5. Known Risks & Mitigations

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|------------|--------|------------|
| 1 | ISP camera pipeline incompatible | High | Critical | Use USB camera or V4L2-compatible MIPI module with custom DTS. |
| 2 | Hexagon DSP unavailable in mainline Linux | High | High | Use GPU (OpenCL) inference as fallback; 29 TOPS GPU may suffice. |
| 3 | Adreno 740 driver bugs in Mesa | Medium | High | Use Mesa stable branch (e.g., 24.x); report issues to freedreno project. |
| 4 | Thermal throttling under sustained load | Medium | Medium | Add heatsink + active cooling; tune CPU/GPU governor. |
| 5 | CAN bus timing jitter over USB | Low | Medium | Use a high-quality USB-CAN adapter with embedded timestamps. |
| 6 | Qualcomm QNN SDK licensing for non-Android | Low | Low | Verify EULA allows Linux deployment. |

---

## 6. Quick Start: First Boot Validation Checklist

Run this checklist on the Dragon Q8B before attempting to build sunnypilot:

```bash
#!/bin/bash
# === Dragon Q8B Pre-Flight Check ===
echo "=== CPU Info ==="
lscpu | grep -E "Model name|Architecture|CPU\(s\)"

echo "=== Memory ==="
free -h

echo "=== Kernel & DTB ==="
uname -a
ls /proc/device-tree/ 2>/dev/null | head -20
cat /proc/device-tree/compatible 2>/dev/null | tr '\0' '\n'

echo "=== PCIe Devices ==="
lspci -vv 2>/dev/null | grep -E "Network|Display|USB"

echo "=== GPU (Vulkan) ==="
vulkaninfo --summary 2>/dev/null || echo "Vulkan tools not installed"

echo "=== Camera Devices ==="
ls -la /dev/video* 2>/dev/null || echo "No camera devices found"
v4l2-ctl --list-devices 2>/dev/null

echo "=== CAN Interfaces ==="
ip link show type can 2>/dev/null || echo "No CAN interfaces found"

echo "=== Thermal Zones ==="
for zone in /sys/class/thermal/thermal_zone*; do
    echo "$(cat $zone/type): $(cat $zone/temp)temp"
done

echo "=== Storage ==="
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT
```

---

## 7. Conclusion & Recommendation

Porting sunnypilot-pc to the Radxa Dragon Q8B is **architecturally feasible** but requires addressing three major gaps:

1. **Camera Pipeline**: The SDM845 ISP code is incompatible. Plan to use a **USB camera** or a mainline-supported MIPI CSI sensor with a custom device tree overlay.
2. **AI Inference**: The Hexagon DSP may not be accessible via mainline Linux without additional kernel modules. The safest path is to use the **Adreno 740 GPU via OpenCL** for inference, leveraging the 29+ TOPS of compute.
3. **CAN Bus**: You will need an external **USB-to-CAN adapter**, as the board lacks a native CAN controller.

**Recommended Starting Point**: Begin with a **USB camera + GPU inference + USB CAN adapter** configuration. This bypasses the highest-risk components (ISP and DSP) and allows you to validate the core sunnypilot logic on the 8cx Gen 3 platform before attempting deeper hardware integration.

---

*Generated as a technical porting reference. Adapt build commands to the actual build system used by the sunnypilot-pc repository.*

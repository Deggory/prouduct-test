# Radxa Dragon Q8B: Comprehensive Hardware Details

## 1. System-on-Chip (SoC): Qualcomm Snapdragon 8cx Gen 3

The core of the board is a custom version of the Snapdragon 8cx Gen 3 mobile processor.

*   **CPU Architecture**: 8-core Kryo 585 (based on ARM Cortex-A76 and A55)
    *   **Performance Cluster**: 4x Cortex-A76 @ 2.84 GHz (Prime)
    *   **Efficiency Cluster**: 4x Cortex-A55 @ 1.80 GHz (Gold)
*   **Die Process**: 4nm (TSMC). *Note: Significant power efficiency advantage over 10nm competitors.*

## 2. Graphics: Adreno 740 (Crucial for Sunnypilot)

The Q8B does *not* have a separate dedicated GPU like a PC. The Adreno 740 is integrated into the SoC but functions like a powerful discrete GPU for openpilot's needs.

*   **Architecture**: Adreno 740 (Gen 4 GPU).
*   **Compute Power**: ~3.1 TFLOPs (FP32).
*   **VRAM**: **4GB of internal Video Memory** (LPDDR4X). This is critical: the GPU has dedicated memory for textures and AI models, preventing slowdowns from swapping to system RAM.
*   **API Support**:
    *   **OpenGL ES 3.2 / OpenGL 4.4**: Supported via Mesa.
    *   **Vulkan 1.1**: Supported via Mesa Freesreno.
    *   **OpenCL 1.2 / 2.0**: Supported via Mesa OpenCL.
*   **Linux Driver**: `Mesa Freesreno`. This is the open-source driver stack used on Linux.

## 3. AI & Inference: Hexagon DSP & Adreno 740

Unlike some ARM chips that have a dedicated NPU (Neural Processing Unit), the 8cx Gen 3 uses a combination of a DSP and the GPU for AI.

*   **Hexagon DSP**: 6th Generation Hexagon (formerly known as Hexagon 685).
    *   Capable of up to 15 TOPS (Tera Operations Per Second) with vector extensions.
    *   *Relevance*: Good for traditional signal processing, but often hard to use for modern AI models without proprietary Qualcomm SDKs.
*   **Adreno 740 (GPU)**:
    *   *Relevance*: This is what you must use. The Hexagon DSP is rarely used by openpilot (which prefers the GPU via OpenCL).
*   **Chassis Design**: The Dragon Q8B is designed as an enthusiast board with a massive passive aluminum heatsink. It is tuned to handle **~7W** of sustained thermal load.

## 4. Image Signal Processor (ISP): Spectra 650 (Generic 8cx)

*   **Format**: Supports MIPI CSI-2.
*   **Capabilities**:
    *   Up to 4-lane input.
    *   16-bit deep color processing.
    *   Supports HDR (High Dynamic Range) capture.
    *   **Video Encoder**: Supports H.264 and H.265 (HEVC) at up to 4K@120Hz (using the dedicated NPU encoder).
*   **API Interface**: V4L2 (Video4Linux2) is the standard Linux interface. This means you can use standard tools like `v4l2-ctl` and `gst-launch` to test your camera input.

## 5. RGA (Raster Graphics Acceleration)

*   **Status**: **NOT AVAILABLE / NONE**.
*   **Explanation**: The Snapdragon 8cx Gen 3 does **not** have a dedicated, low-power 2D image blitter (RGA unit) like the Rockchip RK3588. The RGA is an older architecture common in ARM SoCs for cheap image scaling.
*   **Implication**: Sunnypilot must use the **Adreno 740 GPU** for all image cropping, rotation, and resizing operations. You cannot rely on an RGA accelerator for performance. This confirms why you must configure ONNX Runtime to use **OpenCL** (GPU) instead of just the CPU.

## 6. Memory & Storage

*   **RAM**: 4GB or 8GB LPDDR4X-4266.
    *   **Bus Width**: 128-bit (Quad-channel).
    *   **Bandwidth**: ~34 GB/s (Shared with GPU).
    *   *Note*: The shared memory bandwidth is a bottleneck for the Adreno 740. If you run heavy AI loads, ensure the cooling is active.
*   **Storage**: 128GB UFS 3.1 (High-speed, suitable for OS and data).

## 7. Connectivity

*   **Video Out**: HDMI 2.1 (Up to 4K@120Hz).
*   **Network**: Dual 2.5GbE (RJ45) ports (Gigabit is not supported).
*   **Storage**: M.2 Key M (PCIe 3.0/4.0 x4) for SSDs. *Note: Ensure you plug an SSD into this slot, not just use microSD, for performance.*

## 8. Summary of Software Relevance

| Component | What you use it for | Driver Stack |
| :--- | :--- | :--- |
| **Adreno 740** | **AI Inference** (ONNX Runtime + OpenCL) | `mesa-opencl-icd`, `mesa-vulkan-drivers` |
| **Spectra 650 ISP** | Camera Capture (MIPI CSI-2) | `libv4l2`, `linux-media` |
| **Hexagon DSP** | Optional (Signal processing) | `hexagon-sys-utils` |
| **Adreno GPU** | UI Rendering (Qt) | `libEGL`, `libGLESv2` |

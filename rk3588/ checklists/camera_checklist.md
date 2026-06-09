# CAMERA_CHECKLIST.MD (Authoritative Version)

# Engineering Checklist + Validation Checklist + Production Checklist + AI Agent Operating Checklist

Version: 3.0

Target Hardware:

* RK3588
* RK3588S
* Orange Pi 5
* Orange Pi 5 Plus

Target Sensor:

* IMX415

Target Runtime:

* RKISP
* V4L2
* VisionIPC
* DMA-BUF
* EGLImage
* OpenCL
* RKNN

---

# Section A — Pre-Bringup Checklist

## Hardware Verification

Board Power Stable

[ ]

Camera Connected

[ ]

FFC Orientation Verified

[ ]

MIPI Connector Locked

[ ]

Camera Detected Physically

[ ]

No Visible Damage

[ ]

---

## Operating System Verification

Ubuntu Installed

[ ]

Kernel Boot Successful

[ ]

SSH Accessible

[ ]

Storage Healthy

[ ]

No Critical Boot Errors

[ ]

---

## RK3588 Verification

CPU Detected

[ ]

GPU Detected

[ ]

NPU Detected

[ ]

ISP Detected

[ ]

RGA Detected

[ ]

DMA-BUF Support Present

[ ]

---

# Section B — IMX415 Bring-Up Checklist

## Sensor Detection

Sensor Driver Loaded

[ ]

Sensor Enumerated

[ ]

No Probe Errors

[ ]

No Kernel Warnings

[ ]

No I2C Errors

[ ]

---

## MIPI CSI Validation

MIPI Link Active

[ ]

Lane Configuration Verified

[ ]

No Packet Errors

[ ]

No Link Resets

[ ]

No CRC Errors

[ ]

---

## Sensor Configuration

Resolution Correct

[ ]

FPS Correct

[ ]

Exposure Working

[ ]

Gain Working

[ ]

Image Stable

[ ]

---

# Section C — RKISP Checklist

## ISP Startup

RKISP Loaded

[ ]

RKISP Streaming

[ ]

No ISP Errors

[ ]

No ISP Resets

[ ]

---

## ISP Output

Frames Generated

[ ]

NV12 Output Verified

[ ]

Correct Resolution

[ ]

Correct FPS

[ ]

No Corruption

[ ]

---

## Image Quality

Exposure Correct

[ ]

White Balance Correct

[ ]

Noise Acceptable

[ ]

No Artifacts

[ ]

No Frame Tearing

[ ]

---

# Section D — V4L2 Checklist

## Device Validation

Video Device Present

[ ]

Device Accessible

[ ]

Permissions Correct

[ ]

---

## Stream Validation

Streaming Successful

[ ]

No Frame Drops

[ ]

No Buffer Errors

[ ]

Stable Operation

[ ]

---

## Format Validation

NV12 Selected

[ ]

Width Correct

[ ]

Height Correct

[ ]

Stride Verified

[ ]

Buffer Size Verified

[ ]

---

# Section E — NV12 Checklist

## Frame Layout

Y Plane Correct

[ ]

UV Plane Correct

[ ]

Offsets Verified

[ ]

Layout Verified

[ ]

---

## Tight vs Padded Validation

Stride Recorded

[ ]

Visible Width Recorded

[ ]

Visible Height Recorded

[ ]

Padding Recorded

[ ]

---

## Corruption Validation

No Green Image

[ ]

No Purple Image

[ ]

No Split Frame

[ ]

No Repeated Bottom Region

[ ]

---

# Section F — DMA-BUF Checklist

## Export Validation

DMA-BUF Enabled

[ ]

FD Export Successful

[ ]

FD Reuse Verified

[ ]

No Lifetime Errors

[ ]

---

## Import Validation

Import Successful

[ ]

VisionIPC Compatible

[ ]

OpenCL Compatible

[ ]

EGL Compatible

[ ]

---

## Stability Validation

No Corruption

[ ]

No FD Leaks

[ ]

No Buffer Reuse Errors

[ ]

No Synchronization Errors

[ ]

---

# Section G — VisionIPC Checklist

## Stream Validation

Road Camera Stream

[ ]

Frames Arriving

[ ]

Timestamps Valid

[ ]

Ordering Correct

[ ]

---

## Timing Validation

Monotonic Timestamps

[ ]

Latency Measured

[ ]

No Queue Overflow

[ ]

No Drops

[ ]

---

## Replay Validation

Replay Route Works

[ ]

Replay Matches Live Input

[ ]

No Replay Corruption

[ ]

---

# Section H — EGLImage Checklist

## GPU Preview Validation

DMA-BUF Import

[ ]

EGLImage Creation

[ ]

Texture Creation

[ ]

Preview Visible

[ ]

---

## UI Validation

Preview Stable

[ ]

No Flicker

[ ]

No Corruption

[ ]

Overlay Visible

[ ]

---

## Performance Validation

GPU Path Enabled

[ ]

CPU Copies Reduced

[ ]

Latency Recorded

[ ]

---

# Section I — Intrinsics Checklist

## Camera Geometry

Width Verified

[ ]

Height Verified

[ ]

Focal Length Verified

[ ]

Principal Point Verified

[ ]

---

## Calibration Data

Intrinsics File Exists

[ ]

Values Valid

[ ]

Version Recorded

[ ]

---

# Section J — Extrinsics Checklist

## Mount Geometry

Pitch Recorded

[ ]

Yaw Recorded

[ ]

Roll Recorded

[ ]

Mount Position Recorded

[ ]

---

## Alignment

Camera Centered

[ ]

Horizon Correct

[ ]

Road Alignment Correct

[ ]

---

# Section K — Warp Checklist

## Warp Generation

Warp Matrix Generated

[ ]

Transform Valid

[ ]

Scale Correct

[ ]

Alignment Correct

[ ]

---

## Overlay Validation

Path Overlay Correct

[ ]

Lane Overlay Correct

[ ]

Road Edge Overlay Correct

[ ]

Lead Vehicle Overlay Correct

[ ]

---

# Section L — OpenPilot Integration Checklist

## Camerad

Frames Received

[ ]

Timestamps Correct

[ ]

No Errors

[ ]

---

## Modeld

Frames Consumed

[ ]

Tensor Generation Works

[ ]

No Runtime Errors

[ ]

---

## Planner

modelV2 Published

[ ]

Planner Alive

[ ]

Planner Stable

[ ]

---

# Section M — Performance Checklist

## Camera Timing

Capture Time Measured

[ ]

Publish Time Measured

[ ]

Receive Time Measured

[ ]

---

## Pipeline Timing

Camera → modelV2

Measured

[ ]

Target < 30 ms

[ ]

---

## UI Timing

Camera → UI

Measured

[ ]

Target < 35 ms

[ ]

---

# Section N — Stress Checklist

## Long Duration Test

1 Hour Test

[ ]

4 Hour Test

[ ]

---

## Stability

No Crashes

[ ]

No Camera Disconnects

[ ]

No ISP Failures

[ ]

No DMA-BUF Failures

[ ]

---

## Thermal Stability

CPU Stable

[ ]

GPU Stable

[ ]

NPU Stable

[ ]

No Throttling

[ ]

---

# Section O — Recovery Checklist

## Restart Tests

Camera Restart

[ ]

RKISP Restart

[ ]

Replay Restart

[ ]

Modeld Restart

[ ]

---

## Recovery

Automatic Recovery Works

[ ]

No Corruption After Recovery

[ ]

No Data Loss

[ ]

---

# Section P — Production Readiness Checklist

## Validation

Sensor PASS

[ ]

MIPI PASS

[ ]

RKISP PASS

[ ]

V4L2 PASS

[ ]

NV12 PASS

[ ]

DMA-BUF PASS

[ ]

VisionIPC PASS

[ ]

Warp PASS

[ ]

Replay PASS

[ ]

---

## Performance

Latency PASS

[ ]

FPS PASS

[ ]

Memory PASS

[ ]

Thermal PASS

[ ]

---

## Deployment

Documentation Complete

[ ]

Validation Reports Complete

[ ]

Performance Reports Complete

[ ]

Deployment Reports Complete

[ ]

Rollback Plan Verified

[ ]

---

# Final Camera Certification

Hardware:

---

Camera:

---

Resolution:

---

FPS:

---

DMA-BUF:

YES / NO

EGLImage:

YES / NO

Production Ready:

YES / NO

Reviewer:

---

Date:

---

Result:

PASS / FAIL

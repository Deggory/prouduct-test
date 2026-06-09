# IMX415_RKISP_EXAMPLE.MD (Authoritative Version)

# Engineering Example + Integration Example + Validation Example + Production Example + AI Agent Operating Example

Version: 3.0

Target Hardware:

* RK3588
* RK3588S
* Orange Pi 5
* Orange Pi 5 Plus

Target Camera:

* Sony IMX415

Target Pipeline:

IMX415
↓
MIPI CSI-2
↓
RKISP
↓
V4L2
↓
NV12 DMA-BUF
├──────────────┬──────────────┐
│              │              │
▼              ▼              ▼
VisionIPC    EGLImage       loggerd
↓              ↓
OpenCL       Mali GPU
↓              ↓
RKNN         UI
↓
modelV2
↓
Planner

Purpose:

Demonstrate a complete production-grade IMX415 integration.

---

# Section A — Architecture Example

## Example Topology

Physical Hardware:

```text
IMX415 Camera
      │
      ▼
RK3588 CSI Receiver
      │
      ▼
RKISP
      │
      ▼
V4L2 Device
      │
      ▼
DMA-BUF Export
```

---

## Example Runtime Topology

```text
IMX415
↓
RKISP
↓
NV12 DMA-BUF
↓
VisionIPC
↓
modeld
↓
RKNN
↓
Planner
```

---

## Example UI Topology

```text
DMA-BUF
↓
EGLImage
↓
Mali GPU
↓
OpenGL Texture
↓
UI Preview
```

---

# Section B — Hardware Discovery Example

## Detect Camera

Example:

```bash
v4l2-ctl --list-devices
```

Expected:

```text
rkisp_mainpath
rkisp_selfpath
```

---

## Enumerate Formats

```bash
v4l2-ctl -d /dev/video11 --list-formats-ext
```

Expected:

```text
NV12
```

Preferred for production.

---

## Check Sensor

```bash
dmesg | grep imx415
```

Expected:

```text
imx415 detected
streaming enabled
```

---

## Check ISP

```bash
dmesg | grep rkisp
```

Expected:

```text
rkisp initialized
stream started
```

---

# Section C — V4L2 Example

## Open Camera

Example:

```cpp
int fd = open("/dev/video11", O_RDWR);
```

Validate:

```text
fd >= 0
```

---

## Configure Format

Example:

```cpp
fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
fmt.fmt.pix_mp.width = 1280;
fmt.fmt.pix_mp.height = 720;
fmt.fmt.pix_mp.pixelformat = V4L2_PIX_FMT_NV12;
```

---

## Start Streaming

Example:

```cpp
VIDIOC_STREAMON
```

Validate:

Frames arriving.

---

# Section D — DMA-BUF Example

## Allocate DMA Buffer

Example:

```cpp
VIDIOC_REQBUFS
```

Buffer Type:

```text
V4L2_MEMORY_DMABUF
```

---

## Export Buffer

Example:

```cpp
VIDIOC_EXPBUF
```

Returns:

```cpp
dmabuf_fd
```

Validate:

```text
fd >= 0
```

---

## Buffer Ownership

```text
RKISP
↓
DMA-BUF
↓
VisionIPC
↓
OpenCL
↓
RKNN
```

No CPU copy.

---

# Section E — NV12 Validation Example

## Frame Information

Example:

```text
Resolution:
1280×720

Format:
NV12

Stride:
1280

Size:
1382400 bytes
```

---

## Validate Layout

Y Plane:

```text
1280×720
```

UV Plane:

```text
1280×360
```

---

## Detect Padding

Example:

```cpp
stride != width
```

Record actual layout.

Never assume.

---

# Section F — VisionIPC Example

## Create Stream

Example:

```cpp
VisionIpcServer server;
```

---

## Publish Frame

Example:

```cpp
server.send(buf);
```

---

## Receive Frame

Example:

```cpp
VisionIpcClient client;
client.recv();
```

---

## Validation

Check:

```text
timestamps
frame ordering
drops
```

---

# Section G — EGLImage Example

## Import DMA-BUF

Example:

```cpp
eglCreateImageKHR(...)
```

Source:

```text
DMA-BUF FD
```

---

## Create Texture

Example:

```cpp
glEGLImageTargetTexture2DOES(...)
```

---

## Display Preview

Expected:

```text
Live camera preview
```

without RGB conversion.

---

# Section H — OpenCL Example

## loadyuv.cl

Input:

```text
NV12
```

Output:

```text
YUV tensor
```

---

## transform.cl

Input:

```text
camera tensor
```

Output:

```text
driving model tensor
```

---

## Validation

Measure:

```text
Execution Time
Tensor Statistics
Tensor Shape
```

---

# Section I — modeld Example

## Frame Flow

```text
VisionIPC
↓
DrivingModelFrame.prepare()
↓
Tensor
↓
RKNN
```

---

## Validation

Check:

```text
Shape
Layout
Dtype
```

---

# Section J — RKNN Example

## Load Model

Example:

```cpp
rknn_init(...)
```

Expected:

```text
Success
```

---

## Vision Assignment

```cpp
RKNN_NPU_CORE_0
```

---

## Policy Assignment

```cpp
RKNN_NPU_CORE_1
```

---

## Inference

Example:

```cpp
rknn_run(...)
```

Validate:

```text
Output count
Output shape
Latency
```

---

# Section K — Metadata Example

## Read Metadata

Example:

```json
{
  "inputs": [...],
  "outputs": [...]
}
```

---

## Validate Shapes

Example:

```text
1×12×128×256
```

or

```text
1×128×256×12
```

Never assume.

---

## Validate Slices

Example:

```text
path
lane
road edge
lead vehicle
```

---

# Section L — Validation Example

## Camera Validation

Generate:

```text
camera_validation.json
```

---

## VisionIPC Validation

Generate:

```text
visionipc_validation.json
```

---

## Metadata Validation

Generate:

```text
metadata_validation.json
```

---

## RKNN Validation

Generate:

```text
vision_validation.json
policy_validation.json
```

---

# Section M — Performance Example

## Baseline

Example:

```text
Camera Capture:
4.0 ms

OpenCL:
5.0 ms

Vision:
10.0 ms

Policy:
3.0 ms

Publish:
1.0 ms
```

---

## Total

```text
Camera → modelV2

≈ 23 ms
```

---

## UI

```text
Camera → UI

≈ 28 ms
```

---

## Production Targets

```text
Camera → modelV2
< 30 ms

Preferred:
< 25 ms
```

---

# Section N — Stress Example

## Duration

```text
4 Hours
```

---

## Validation

No Crashes

[ ]

No Frame Drops

[ ]

No RKNN Failures

[ ]

No Memory Leaks

[ ]

No Thermal Throttling

[ ]

---

# Section O — Recovery Example

## Camera Restart

Expected:

```text
Automatic Recovery
```

---

## RKNN Restart

Expected:

```text
Context Recreated
Inference Resumes
```

---

## Replay Restart

Expected:

```text
Replay Continues Normally
```

---

# Section P — Production Example

## Required Artifacts

```text
camera_validation.json
visionipc_validation.json
metadata_validation.json
vision_validation.json
policy_validation.json
latency_report.json
deployment_report.json
```

---

## Production Checklist

Camera PASS

[ ]

VisionIPC PASS

[ ]

Metadata PASS

[ ]

Vision PASS

[ ]

Policy PASS

[ ]

Latency PASS

[ ]

Stress PASS

[ ]

Recovery PASS

[ ]

---

## Production Result

```text
READY FOR PRODUCTION
```

Only after all validation passes.

---

# Section Q — AI Agent Operating Example

## Discovery Workflow

```text
Discover Camera
↓
Discover VisionIPC
↓
Discover Metadata
↓
Validate Tensor
↓
Validate RKNN
↓
Validate Planner
↓
Generate Reports
↓
Deploy
```

---

## Example Deliverables

```text
camera_inventory.json
runtime_inventory.json
metadata_inventory.json

camera_validation.json
vision_validation.json
policy_validation.json

latency_report.json
deployment_report.json
```

---

## Example Certification

Hardware:

Orange Pi 5

Camera:

IMX415

Runtime:

RKNN

Vision Core:

0

Policy Core:

1

Camera → modelV2:

23 ms

Camera → UI:

28 ms

Result:

PASS

Production Ready:

YES

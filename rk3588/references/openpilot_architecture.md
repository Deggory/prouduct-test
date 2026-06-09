# OPENPILOT_ARCHITECTURE.MD (Authoritative Version)

# Engineering Specification + Validation Specification + AI Agent Operating Manual

Version: 3.0

Target Platforms:

* OpenPilot
* Sunnypilot
* FrogPilot
* OPKR
* KisaPilot
* RK3588 OpenPilot Ports

Target Hardware:

* Comma 3X
* RK3588
* Orange Pi 5
* Orange Pi 5 Plus

Target Runtime:

* Tinygrad
* ONNX Runtime
* RKNN

---

# Section A — Engineering Specification

## 1. Objective

This document defines:

* OpenPilot architecture
* Process architecture
* Message architecture
* Camera architecture
* Model architecture
* Planning architecture
* Controls architecture
* Hardware abstraction
* AI-agent repository analysis

Goal:

Provide a complete architectural map of OpenPilot-derived systems.

---

## 2. OpenPilot Philosophy

OpenPilot is a distributed real-time system.

It is not:

A single application.

It is:

Many cooperating processes communicating through message buses.

---

## 3. High-Level System Architecture

Camera
↓
VisionIPC
↓
modeld
↓
modelV2
↓
plannerd
↓
controlsd
↓
Car Interface
↓
Vehicle

Supporting systems:

UI

loggerd

calibrationd

sensord

manager

---

## 4. Core Architecture Layers

Layer 1

Hardware

Layer 2

Drivers

Layer 3

Transport

Layer 4

Perception

Layer 5

Planning

Layer 6

Controls

Layer 7

UI

---

## 5. OpenPilot Repository Architecture

Major directories:

```text
selfdrive/
system/
cereal/
common/
msgq/
opendbc/
tools/
third_party/
```

Each subsystem has ownership boundaries.

---

## 6. Process Architecture

Major processes:

manager

camerad

modeld

plannerd

controlsd

ui

loggerd

calibrationd

radard

---

## 7. Manager Architecture

manager.py

Responsibilities:

Process startup

Process monitoring

Restart policies

Health checks

Manager is the root supervisor.

---

## 8. Camera Architecture

Camera
↓
camerad
↓
VisionIPC

Responsibilities:

Capture

Timestamp

Publish

---

## 9. VisionIPC Architecture

VisionIPC transports:

Road Camera

Wide Camera

Driver Camera

Frames

Metadata

Timestamps

VisionIPC does not perform inference.

---

## 10. Message Architecture

OpenPilot uses:

cereal

msgq

Messages are the system contract.

---

## 11. Cereal Architecture

Defines:

Schemas

Messages

Types

Serialization

---

## 12. MsgQ Architecture

Provides:

Publisher

Subscriber

Transport

Synchronization

---

## 13. Message Philosophy

Processes should communicate through:

Messages

not direct function calls.

---

## 14. Perception Architecture

Camera
↓
VisionIPC
↓
modeld

Perception generates:

Path

Lanes

Road Edges

Lead Vehicles

Pose

---

## 15. Modeld Architecture

Responsibilities:

Preprocessing

Tensor Generation

Inference

Output Parsing

Publishing

---

## 16. Model Pipeline

NV12
↓
loadyuv.cl
↓
transform.cl
↓
Tensor
↓
Vision Model
↓
Policy Model
↓
modelV2

---

## 17. Metadata Architecture

Model
↓
Metadata
↓
Parser
↓
modelV2

Metadata defines output meaning.

---

## 18. Planner Architecture

Planner consumes:

modelV2

Planner generates:

Trajectory

Desired Curvature

Future Vehicle Path

---

## 19. Controls Architecture

Planner
↓
controlsd
↓
Vehicle Commands

Controls execute planner intent.

---

## 20. Vehicle Interface Architecture

Vehicle Interface

Abstracts:

CAN

Steering

Braking

Acceleration

Vehicle-specific behavior.

---

## 21. Car Interface Architecture

Car Interface converts:

Planner Commands

into

Vehicle Commands

---

## 22. UI Architecture

Consumes:

modelV2

carState

controlsState

Displays:

Camera Preview

Path

Lanes

Alerts

---

## 23. Logger Architecture

Records:

Messages

Camera Streams

Events

Logs

---

## 24. Replay Architecture

Recorded Route
↓
Replay
↓
VisionIPC
↓
modeld
↓
Planner

Replay enables offline validation.

---

## 25. Calibration Architecture

Consumes:

Camera Data

Vehicle Motion

Produces:

Calibration Parameters

---

## 26. Sensor Architecture

Sensors include:

Camera

IMU

GPS

Vehicle Signals

---

## 27. Hardware Abstraction

OpenPilot separates:

Hardware

from

Planner Logic

through abstraction layers.

---

## 28. Runtime Architecture

Possible runtimes:

Tinygrad

ONNX Runtime

RKNN

Model outputs must remain compatible.

---

## 29. RK3588 Architecture

IMX415
↓
RKISP
↓
NV12 DMA-BUF
↓
VisionIPC
↓
OpenCL
↓
RKNN
↓
Planner

---

## 30. Production Architecture

IMX415
↓
RKISP
↓
DMA-BUF
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
↓
Controls

---

# Section B — Message Architecture

## 31. Message Ownership

Each process owns:

Published Messages

Consumes:

Subscribed Messages

---

## 32. Core Messages

Examples:

modelV2

carState

controlsState

cameraOdometry

liveCalibration

pandaStates

---

## 33. Message Validation

Validate:

Schema

Units

Frequency

Timestamp

---

## 34. Planner Messages

Planner consumes:

modelV2

Planner publishes:

trajectory-related outputs

---

## 35. Controls Messages

Controls consumes:

Planner outputs

Vehicle state

---

## 36. UI Messages

UI consumes:

Perception

Planning

Vehicle

Alert messages

---

## 37. Logging Messages

Logger consumes:

Nearly everything.

---

## 38. Replay Messages

Replay reproduces:

Recorded messages

for validation.

---

# Section C — Validation Specification

## 39. Repository Discovery

Discover:

Processes

Messages

Models

Metadata

Generate:

architecture_inventory.json

---

## 40. Process Validation

Validate:

Started

Alive

Healthy

Generate:

process_validation.json

---

## 41. Message Validation

Validate:

Schemas

Units

Frequency

Generate:

message_validation.json

---

## 42. Camera Validation

Validate:

Capture

VisionIPC

Timing

---

## 43. Model Validation

Validate:

Tensor Generation

Metadata

Inference

---

## 44. Planner Validation

Validate:

Planner Alive

Stable Outputs

---

## 45. Controls Validation

Validate:

Commands

Timing

Safety

---

## 46. UI Validation

Validate:

Preview

Overlay

Alerts

---

## 47. Logger Validation

Validate:

Logs

Routes

Message Recording

---

## 48. Replay Validation

Replay Route
↓
Modeld
↓
Planner

Validate outputs.

---

## 49. Latency Validation

Measure:

Camera

Perception

Planning

Controls

UI

Generate:

latency_report.json

---

## 50. System Validation

Validate:

End-to-End Stability

Message Integrity

Timing

Recovery

---

## 51. Stress Validation

1 Hour Minimum

4 Hours Preferred

Monitor:

Latency

Memory

Temperature

---

## 52. Recovery Validation

Restart:

Camera

Modeld

Planner

UI

Verify recovery.

---

## 53. Acceptance Criteria

Camera PASS

Messages PASS

Model PASS

Planner PASS

Controls PASS

Replay PASS

---

# Section D — AI Agent Operating Manual

## 54. Repository Discovery Workflow

Discover:

Processes

Messages

Models

Metadata

VisionIPC

Planner

Controls

Generate:

architecture_analysis.json

---

## 55. Fork Analysis Workflow

Repository
↓
Process Discovery
↓
Message Discovery
↓
Model Discovery
↓
Metadata Discovery
↓
Planner Discovery

---

## 56. Porting Workflow

Hardware Bring-Up
↓
Camera Validation
↓
Model Validation
↓
Planner Validation
↓
Performance Validation
↓
Deployment

---

## 57. RK3588 Port Workflow

IMX415
↓
RKISP
↓
VisionIPC
↓
OpenCL
↓
RKNN Vision Core 0
↓
RKNN Policy Core 1
↓
Planner

---

## 58. Fork Adaptation Rules

Never assume:

Paths

Process Names

Message Names

Model Names

Metadata Locations

Discover dynamically.

---

## 59. Allowed Modifications

Runtime

Camera Integration

Validation Hooks

Performance Tooling

Deployment Tooling

---

## 60. Avoid Modifications

Planner Semantics

Controls Semantics

Message Semantics

Unless required.

---

## 61. Reporting Requirements

Generate:

architecture_inventory.json

architecture_analysis.json

process_validation.json

message_validation.json

latency_report.json

---

## 62. Troubleshooting

Process Crash

Message Failure

Model Failure

Planner Failure

Controls Failure

Replay Failure

Latency Spike

Document root cause and fix.

---

## 63. Failure Modes

Camera Failure

VisionIPC Failure

Metadata Failure

Model Failure

Planner Failure

Controls Failure

Message Failure

---

## 64. Production Readiness

Required:

Camera PASS

Messages PASS

Model PASS

Planner PASS

Controls PASS

Replay PASS

Latency PASS

Recovery PASS

---

## 65. Final Checklist

Manager
[ ]

Camera
[ ]

VisionIPC
[ ]

Messages
[ ]

Metadata
[ ]

Modeld
[ ]

Planner
[ ]

Controls
[ ]

UI
[ ]

Logger

[ ]

Replay
[ ]

Latency
[ ]

Recovery
[ ]

Result:

PASS / FAIL

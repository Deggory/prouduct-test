# OPENPILOT_ARCHITECTURE.MD

# OpenPilot Architecture Reference

Version: 1.0

Purpose:

Provide a system-level architecture reference for AI agents modifying:

* openpilot
* sunnypilot
* frogpilot
* OPKR
* KisaPilot

Target Hardware:

* Comma Devices
* RK3588
* RK3588S
* Orange Pi 5
* Orange Pi 5 Plus

---

# 1. Overview

OpenPilot is a distributed real-time driving system.

It is not:

* a single process
* a single neural network
* a single executable

OpenPilot is a collection of cooperating daemons communicating through message buses.

---

# 2. High-Level Architecture

Vehicle

↓

Sensors

↓

Camera Pipeline

↓

Model Pipeline

↓

Planning

↓

Controls

↓

Vehicle

---

# 3. Core Subsystems

Primary subsystems:

Camera

Perception

Planning

Controls

Logging

UI

Vehicle Interface

Each subsystem should be modified independently.

---

# 4. Data Flow

Typical flow:

Camera

↓

camerad

↓

VisionIPC

↓

modeld

↓

plannerd

↓

controlsd

↓

CAN Messages

↓

Vehicle

---

# 5. Camera Subsystem

Responsibilities:

* Camera acquisition
* Frame buffering
* Frame publication

Outputs:

VisionIPC streams

---

# 6. camerad

Typical responsibilities:

* Camera initialization
* Camera synchronization
* VisionIPC publication

camerad should not perform inference.

---

# 7. VisionIPC

Responsibilities:

* Shared memory transport
* Frame synchronization
* Stream management

VisionIPC connects:

Camera

↓

modeld

↓

UI

---

# 8. modeld

modeld is the perception engine.

Responsibilities:

* Frame preprocessing
* Tensor preparation
* Model execution
* Output parsing
* Message publication

---

# 9. modeld Pipeline

Typical flow:

VisionIPC

↓

loadyuv.cl

↓

transform.cl

↓

DrivingModelFrame.prepare()

↓

Inference

↓

Metadata Parsing

↓

modelV2

---

# 10. AI Model Responsibilities

Models estimate:

* path
* lanes
* road edges
* lead vehicles
* driving features

Models do not directly control the vehicle.

---

# 11. Planner Overview

Planner consumes:

model outputs

vehicle state

driver inputs

Planner generates:

desired trajectory

---

# 12. plannerd

Responsibilities:

* trajectory generation
* path selection
* maneuver planning

Inputs:

modelV2

carState

other system messages

---

# 13. Controls Overview

Controls converts:

desired trajectory

into

steering

acceleration

braking commands

---

# 14. controlsd

Responsibilities:

* lateral control
* longitudinal control
* safety checks

Outputs:

CAN commands

---

# 15. Vehicle Interface

Responsibilities:

* CAN communication
* vehicle fingerprinting
* vehicle parameters

Examples:

wheelbase

steer ratio

vehicle mass

---

# 16. loggerd

Responsibilities:

* route recording
* log recording
* event recording

Used heavily during validation.

---

# 17. UI Overview

Responsibilities:

* camera preview
* path visualization
* alerts
* status display

UI correctness does not imply model correctness.

---

# 18. Messaging Architecture

OpenPilot uses message passing.

Processes should not communicate through:

global variables

shared mutable state

Instead:

messages

should be used.

---

# 19. Common Messages

Examples:

carState

carControl

modelV2

cameraOdometry

controlsState

selfdriveState

---

# 20. Message Ownership

Each message has:

Producer

Consumer

Schema

Units

Never modify message meaning without updating consumers.

---

# 21. Process Discovery

AI agents should discover:

Processes

Publishers

Subscribers

before modifying code.

Generate:

process_inventory.json

---

# 22. Camera Data Path

Typical flow:

IMX415

↓

RKISP

↓

NV12

↓

VisionIPC

↓

modeld

---

# 23. Preprocessing Path

Typical flow:

NV12

↓

loadyuv.cl

↓

transform.cl

↓

Tensor

Preprocessing should remain unchanged whenever possible.

---

# 24. Model Runtime Layer

Possible runtimes:

Tinygrad

RKNN

ONNX

Future runtimes

All should share:

Metadata

Tensor definitions

Message outputs

---

# 25. Metadata Layer

Metadata defines:

Inputs

Outputs

Slices

Hidden states

Features

Metadata is authoritative.

---

# 26. Hidden State Layer

Modern models contain memory.

Examples:

features_buffer

hidden_state

transformer cache

Must persist across frames.

---

# 27. Planning Inputs

Planner consumes:

modelV2

cameraOdometry

carState

liveParameters

Planner should remain runtime-agnostic.

---

# 28. Controls Inputs

Controls consumes:

trajectory

vehicle state

driver state

Controls should not know:

Tinygrad

RKNN

ONNX

---

# 29. Logging Inputs

loggerd records:

messages

routes

events

Performance reports should include logger impact.

---

# 30. Replay System

Replay allows:

recorded routes

↓

replayed messages

↓

validation

Replay is essential for regression testing.

---

# 31. Calibration System

Calibration consumes:

camera geometry

vehicle motion

Camera changes often require recalibration.

---

# 32. Process Lifecycle

Typical startup:

manager.py

↓

camerad

↓

modeld

↓

plannerd

↓

controlsd

↓

UI

---

# 33. manager.py

manager.py supervises:

process start

process stop

health monitoring

restart behavior

---

# 34. Health Monitoring

Monitor:

Alive status

Message frequency

Error counts

Generate:

health_report.json

---

# 35. Failure Domains

Camera Failure

↓

VisionIPC Failure

↓

modeld Failure

↓

Planner Failure

↓

Controls Failure

Failures should be isolated.

---

# 36. RK3588 Integration Point

Recommended modifications:

Camera Layer

modeld Layer

Runtime Layer

Avoid:

Planner changes

Controls changes

unless absolutely necessary.

---

# 37. AI Agent Modification Rules

Before modifying a fork:

Discover:

Camera

VisionIPC

modeld

Planner

Controls

Metadata

Generate architecture report.

---

# 38. Recommended RK3588 Architecture

IMX415

↓

RKISP

↓

NV12

↓

VisionIPC

↓

loadyuv.cl

↓

transform.cl

↓

DrivingModelFrame.prepare()

↓

RKNN Vision

↓

RKNN Policy

↓

Metadata Parsing

↓

modelV2

↓

plannerd

↓

controlsd

↓

Vehicle

---

# 39. Validation Flow

Camera

↓

VisionIPC

↓

Tensor Validation

↓

RKNN Validation

↓

Planner Validation

↓

Vehicle Validation

Each layer must pass before continuing.

---

# 40. Final Architecture Checklist

Camera Pipeline

[ ] PASS

VisionIPC

[ ] PASS

Preprocessing

[ ] PASS

Metadata

[ ] PASS

Runtime

[ ] PASS

Planner

[ ] PASS

Controls

[ ] PASS

Logging

[ ] PASS

Replay

[ ] PASS

Deployment

[ ] PASS

Result:

PASS / FAIL

This document is the authoritative architecture reference for AI-agent-driven OpenPilot modifications.

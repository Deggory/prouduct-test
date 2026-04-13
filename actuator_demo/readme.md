# ESP32 Dual N25 EPS Controller (MCP2515 + BTS7960)

## Overview

This project turns an **ESP32 Dev Module** into a **dual-motor EPS (Electric Power Steering) controller** using:

* **ESP32 Dev Module**
* **MCP2515 CAN controller**
* **2× BTS7960 motor drivers**
* **2× N25 gear motors with quadrature encoders**
* **CAN torque request input**
* **Cascade closed-loop control**

The controller receives **steering torque commands over CAN**, converts them into a **target steering position**, and drives **two synchronized motors** to follow that target smoothly.

---

# What the Code Does

The code is divided into **6 main functional blocks**.

## 1) CAN Communication

The MCP2515 handles vehicle CAN communication.

### CAN Receive

Reads torque request packets from:

* `0x22E` → steering torque command input

It validates:

* CRC8 checksum
* rolling counter
* packet sequence

Then extracts:

* signed torque request
* steering enable state

## 2) Encoder Feedback

Each N25 motor has a **quadrature encoder**.

The ESP32 reads:

* Motor 1 encoder → GPIO 34 / 35
* Motor 2 encoder → GPIO 36 / 39

Using interrupts, the code tracks:

* position
* direction
* speed
* synchronization between both motors

## 3) Cascade Control Loop

This is the main steering controller.

### Outer loop: Position control

Converts torque request into a **target steering position**.

```text
Torque request → target position
```

Then computes:

```text
Position error → target velocity
```

## 4) Inner loop: Velocity control

Compares:

* target speed
* actual speed from encoders

Then generates PWM.

```text
Velocity error → PWM output
```

This gives:

* smooth torque feel
* stable assist
* reduced oscillation
* better self-centering behavior

## 5) Dual Motor Synchronization

Both motors are mechanically linked, so they must stay aligned.

The code continuously checks:

```text
encoder1Count - encoder2Count
```

and adds correction PWM so both motors stay synchronized.

This prevents:

* fighting between motors
* rack twist
* current spikes
* gearbox stress

## 6) CAN Feedback to Vehicle

The ESP32 transmits two CAN frames:

### Steering feedback

* ID `0x22F`
* torque echo
* steering OK flag
* controller state

### Cruise / fake speed

* ID `0x22D`
* fake speed value
* engage button state

Useful for:

* spoofing OEM EPS
* ADAS integration
* lane keep assist experiments

---

# Full Pinout

## MCP2515 CAN Module

| MCP2515 | ESP32   |
| ------- | ------- |
| VCC     | 5V      |
| GND     | GND     |
| CS      | GPIO 5  |
| INT     | GPIO 15 |
| SCK     | GPIO 18 |
| MISO    | GPIO 19 |
| MOSI    | GPIO 23 |

---

## BTS7960 Driver #1

| BTS7960 | ESP32   |
| ------- | ------- |
| RPWM    | GPIO 25 |
| LPWM    | GPIO 26 |
| R_EN    | GPIO 27 |
| L_EN    | GPIO 14 |

## BTS7960 Driver #2

| BTS7960 | ESP32   |
| ------- | ------- |
| RPWM    | GPIO 32 |
| LPWM    | GPIO 33 |
| R_EN    | GPIO 12 |
| L_EN    | GPIO 13 |

---

## Encoder Inputs

## Motor 1 Encoder

| Encoder | ESP32   |
| ------- | ------- |
| A       | GPIO 34 |
| B       | GPIO 35 |

## Motor 2 Encoder

| Encoder | ESP32   |
| ------- | ------- |
| A       | GPIO 36 |
| B       | GPIO 39 |

> These pins are **input-only pins**, which is perfect for encoder reading.

---

## Engage Switch

| Signal        | ESP32  |
| ------------- | ------ |
| Engage button | GPIO 4 |

Uses internal pull-up.

---

# Control Flow (Simple)

```text
CAN torque request
        ↓
Target position update
        ↓
Position controller
        ↓
Target velocity
        ↓
Velocity controller
        ↓
PWM output
        ↓
BTS7960 drivers
        ↓
Dual N25 motors
        ↓
Encoder feedback
        ↺
```

---

# Important Tunable Parameters

These values control steering feel.

## Position loop

```cpp
float kp_pos = 0.25f;
float maxVelocity = 800.0f;
```

## Velocity loop

```cpp
float kv_vel = 0.9f;
float kd_damp = 0.02f;
```

## Motor behavior

```cpp
#define PWM_BREAKAWAY 180
#define PWM_MAX 1023
```

### Suggested smoother values

```cpp
kp_pos = 0.18f;
kv_vel = 0.6f;
kd_damp = 0.04f;
```

Better for:

* reduced oscillation
* smoother lane keep
* softer assist feel

---

# Safety Features

The code includes important protection:

## CAN timeout

If no valid CAN packet arrives for **500 ms**:

* torque request resets to zero
* assist disables
* state changes to timeout error

## Packet counter check

Detects:

* dropped frames
* repeated packets
* wrong order

## CRC8 verification

Rejects corrupted CAN frames.

## Dual motor sync correction

Protects the rack from motor mismatch.

---

# Power Wiring Notes

## IMPORTANT

Do **not** power BTS7960 motor supply from ESP32 5V.

Use separate motor supply:

* 12V battery
* 20–30A fuse
* thick GND wiring
* common GND with ESP32

Recommended:

```text
12V Battery → BTS7960 B+
Battery GND → BTS7960 B-
Battery GND → ESP32 GND
```

---

# Use Cases

This code is suitable for:

* EPS spoofing
* Kia / Hyundai steering experiments
* lane keep actuator
* torque overlay
* autonomous steering test bench
* rack simulator
* force feedback wheel projects

---

# Upload Settings

For Arduino IDE:

* **Board:** ESP32 Dev Module
* **Flash freq:** 80 MHz
* **Partition:** Default
* **PSRAM:** Disabled
* **Core version:** ESP32 v3.x recommended

---

# Final Notes

This project is a **high-performance dual-motor EPS controller**.

The cascade control structure makes it much better than direct PWM torque drive because it provides:

* smooth response
* stable center return
* strong damping
* accurate rack positioning
* synchronized dual motor assist

It is especially useful for **OEM-style EPS spoofing and ADAS steering control experiments**.

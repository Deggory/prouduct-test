
# ESP32 Dual N25 EPS Controller (2-Loop Cascaded Velocity)

A closed-loop EPS-style controller using:

- ESP32
- MCP2515 CAN
- `mcp_can.h`
- 2x BTS7960 motor drivers
- 2x N25 geared motors
- N25 quadrature encoder feedback
- 2-loop cascaded control
- CAN IDs compatible with original STM32 firmware

---

## Core Control Architecture

This firmware uses **2 nested control loops**.

### Outer loop: Position -> Velocity
CAN torque request updates a **target steering position**.
Position error generates a **target motor speed**.

### Inner loop: Velocity -> PWM
Measured encoder speed is compared with target speed.
PWM automatically rises if the motor slows under steering load.

This makes the N25 behave like a **virtual torque servo**.

---

## Why this is better for N25

N25 motors are:
- geared
- low RPM
- high friction
- nonlinear under load

Direct PWM from position error causes:
- stiction
- dead zone
- overshoot
- oscillation

The cascaded velocity loop solves this.

---

## Pinout

### MCP2515
- CS → GPIO5
- INT → GPIO15
- SCK → GPIO18
- MISO → GPIO19
- MOSI → GPIO23

### BTS7960 #1
- RPWM → GPIO25
- LPWM → GPIO26
- R_EN → GPIO27
- L_EN → GPIO14

### BTS7960 #2
- RPWM → GPIO32
- LPWM → GPIO33
- R_EN → GPIO12
- L_EN → GPIO13

### N25 Encoder Motor 1
- A → GPIO34
- B → GPIO35
- VCC → 3.3V
- GND → GND

### N25 Encoder Motor 2
- A → GPIO36
- B → GPIO39
- VCC → 3.3V
- GND → GND

### Engage / Cruise
- GPIO4 → active LOW switch

---

## CAN Protocol

### RX `0x22E`
| Byte | Function |
|---|---|
| 0 | CRC8 |
| 1 | rolling counter |
| 4 | torque LSB |
| 5 | torque MSB |

### TX `0x22F`
Controller feedback:
- requested torque echo
- steer status
- state
- rolling counter

### TX `0x22D`
Cruise spoof packet:
- fake speed = 6000
- engage switch state

---

## Safety Features

- CRC8 SAE J1850
- rolling counter validation
- 500ms timeout neutral
- breakaway PWM compensation
- encoder velocity damping
- output saturation

---

## Tuning Guide

### Position loop
```cpp
kp_pos = 0.25
maxVelocity = 800
````

Increase `kp_pos` for stronger steering hold.

### Velocity loop

```cpp
kv_vel = 0.9
kd_damp = 0.02
```

Increase:

* `kv_vel` → stronger load compensation
* `kd_damp` → less oscillation

---

## Breakaway Compensation

Because N25 gearbox has static friction, small PWM values may not move.

This firmware adds:

```cpp
PWM_BREAKAWAY = 180
```

This ensures reliable motion start.

---

## Best Use Cases

* DIY EPS column assist
* autonomous steering prototype
* steering simulator
* OpenPilot actuator emulator
* dual motor worm-drive assist
* robotics steering servo

---

## Dual Encoder Synchronization

Both N25 motors now use separate encoder feedback.
A synchronization correction term compares both encoder counts and automatically biases PWM:

* faster motor gets less PWM
* slower motor gets more PWM

This prevents gearbox fighting and keeps both assist motors aligned on the shared steering shaft.

---

## Future Upgrades

Recommended next improvements:

* center return assist
* speed-sensitive steering feel map
* dual encoder synchronization
* motor stall detection
* CAN diagnostics stream
* OTA tuning UI
ESP32 ↔ MCP2515
MCP2515 VCC   -> 5V
MCP2515 GND   -> GND
MCP2515 CS    -> GPIO5
MCP2515 INT   -> GPIO15
MCP2515 SCK   -> GPIO18
MCP2515 MISO  -> GPIO19
MCP2515 MOSI  -> GPIO23
CANH          -> Vehicle CAN High
CANL          -> Vehicle CAN Low

This is standard VSPI on ESP32.

BTS7960 Motor Driver #1
RPWM -> GPIO25
LPWM -> GPIO26
R_EN -> GPIO27
L_EN -> GPIO14
VCC  -> 5V
GND  -> GND
B+   -> Motor supply +
B-   -> Motor supply -
M+   -> N25 Motor 1 +
M-   -> N25 Motor 1 -
BTS7960 Motor Driver #2
RPWM -> GPIO32
LPWM -> GPIO33
R_EN -> GPIO12
L_EN -> GPIO13
VCC  -> 5V
GND  -> GND
B+   -> Motor supply +
B-   -> Motor supply -
M+   -> N25 Motor 2 +
M-   -> N25 Motor 2 -
N25 Encoder #1
Encoder VCC -> 3.3V
Encoder GND -> GND
A           -> GPIO34
B           -> GPIO35
N25 Encoder #2
Encoder VCC -> 3.3V
Encoder GND -> GND
A           -> GPIO36
B           -> GPIO39

These GPIOs are input-only pins, perfect for encoders.

Cruise / Engage Switch
Switch one side -> GPIO4
Other side      -> GND

The code uses:

INPUT_PULLUP

so switch = active LOW.

Power wiring (VERY important)

Do not power motors from ESP32.

Use:

24V battery / PSU
   -> both BTS7960 B+ / B-
ESP32 + MCP2515
   -> 5V buck converter
Encoders
   -> ESP32 3.3V

All grounds must be common:

ESP32 GND
MCP2515 GND
BTS7960 GND
encoder GND
power supply GND

Otherwise encoder sync will fail.

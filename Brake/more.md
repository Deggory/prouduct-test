# 🚗 Brake Pedal Robot (ADAS Retrofit) — Control System Design

## 🧠 Overview

This project implements a **brake pedal actuator** using:

* String potentiometer → position feedback (mm)
* Stepper motor + cable → actuation

The system behaves like an **assistive exoskeleton for the brake pedal**, combining:

* trajectory tracking (ADAS)
* human assist
* smooth return
* safety-first behavior

---

# 📏 System Variables

* `x` → current pedal position (mm)
* `ẋ` → velocity (mm/s)
* `x_t` → target position (ADAS/UI)
* `u` → motor command

---

# 🎯 Core Control Law

[
u = K_0(0 - x) - B\dot{x} + K_t(x_t - x) + A\max(\dot{x}, 0)
]

---

# ⚙️ Control Components

## 1. 🔁 Return to Zero (Fail-safe)

[
K_0(0 - x)
]

* Pulls pedal back to **0 mm**
* Active when:

  * ADAS OFF
  * driver releases
  * fault condition

---

## 2. ⚖️ Damping (Smoothness)

[

* B\dot{x}
  ]
* Reduces jerks
* Prevents oscillation

---

## 3. 🎯 Target Tracking (ADAS)

[
K_t(x_t - x)
]

* Moves pedal toward target
* Holds brake level

---

## 4. 💪 Assist (Driver Input)

[
A\max(\dot{x}, 0)
]

* Active only when pressing (`ẋ > 0`)
* Adds assist proportional to speed

---

# 🧠 Functional Mapping

| Function          | Algorithm                     |
| ----------------- | ----------------------------- |
| Follow path       | PD tracking via `Kt(x_t - x)` |
| Assist movement   | `A max(ẋ,0)`                 |
| Hold position     | `Kt(x_t - x)`                 |
| Detect intent     | velocity (`ẋ`)               |
| Compensation      | `Kg x` (optional)             |
| Smooth motion     | damping `-B ẋ`               |
| Stall detection   | motion mismatch               |
| Safety limits     | clamp + bounds                |
| Position tracking | ADC → mm                      |
| Speed control     | rate limiting                 |
| Mode switching    | state machine                 |
| Fail-safe         | return to zero                |
| Homing            | limit → reset                 |

---

# 🔄 System Modes

## PASSIVE

* No actuation
* Pedal free

---

## ASSIST

* Driver pressing
* Adds assist

---

## ADAS

* Follows target `x_t`
* Holds position

---

## HOLD

* Maintain current position

---

## FAILSAFE

* Release to 0 mm
* Disable motor

---

# ⚠️ Safety Rules

* Stroke limit:

```text
0 mm ≤ x ≤ 30 mm
```

* Human override:

```text
if x > x_t + margin → assist mode
```

* Fault:

```text
→ return to zero
```

---

# 🛑 Stall Detection

```text
motor active AND ẋ ≈ 0 → STALL
```

---

# 🔧 Calibration

* Move to physical limit
* Set:

```text
x = 0 mm
```

---

# ⚡ Implementation Loop

```cpp
x = read_position();
x_dot = x - last_x;

u = K0*(0 - x)
  - B*x_dot
  + Kt*(target - x)
  + A*max(x_dot, 0);

u = constrain(u);
drive_stepper(u);

last_x = x;
```

---

# 🎛️ Tuning Parameters

| Parameter | Effect           |
| --------- | ---------------- |
| K0        | return strength  |
| B         | smoothness       |
| Kt        | target stiffness |
| A         | assist strength  |

---

# 🧾 System Philosophy

> Human is always in control.
> System assists, stabilizes, and ensures safety.

---

# 🚀 Future Extensions

* ACC integration (distance → target)
* Force estimation (current/velocity)
* Adaptive assist tuning
* Sensor fusion

---

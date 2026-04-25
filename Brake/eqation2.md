# 🚗 Brake Pedal Robot (ADAS Retrofit) — Control Algorithms

## 🧠 Overview

This document maps each required function → **control algorithm + equation**
for a **brake pedal actuator (0–30 mm stroke)** using:

* string potentiometer (position)
* stepper motor (actuation)

---

# 1. 🎯 Follow the Path (Trajectory Tracking)

### Algorithm: PD Control

[
u = K_p(x_d - x) + K_d(\dot{x}_d - \dot{x})
]

### Simplified:

[
u = K_p(x_d - x) - K_d \dot{x}
]

---

# 2. 💪 Assist Movement

### Algorithm: Velocity-based Assist

[
u_{assist} = A \cdot \max(\dot{x}, 0)
]

* Active only when pressing
* Adds boost proportional to speed

---

# 3. 🧱 Resist / Support Load (Hold Position)

### Algorithm: Position Hold (Spring)

[
u = K_h (x_t - x)
]

* Maintains brake stroke
* Used in hold / traffic stop

---

# 4. 🧍 Detect User Intent

### Algorithm: Velocity Threshold

[
\dot{x} = x - x_{prev}
]

```text
if ẋ > threshold → pressing
if ẋ < -threshold → releasing
```

---

# 5. 🌍 Gravity / Resistance Compensation

### Algorithm: Position-based Compensation

[
u = K_g \cdot x
]

* Compensates pedal stiffness / spring

---

# 6. ⚖️ Stability (Damping)

### Algorithm: Damping

[
u = -B \cdot \dot{x}
]

* Prevents oscillation
* Smooth motion

---

# 7. 🛑 Stall / Obstruction Detection

### Algorithm: Motion Mismatch

[
\text{if } (u \neq 0) \land (\dot{x} \approx 0) \Rightarrow \text{STALL}
]

---

# 8. 🧷 Force Limiting / Safety

### Algorithm: Saturation

[
u = \text{clamp}(u, -u_{max}, u_{max})
]

[
x \in [0, 30 \text{ mm}]
]

---

# 9. 📏 Position Tracking

### Algorithm: Direct Measurement

[
x = \text{map(ADC → mm)}
]

---

# 10. ⚡ Speed Control

### Algorithm: Rate Limiting

[
u = \text{limit_rate}(u, \Delta u_{max})
]

OR

[
\dot{x}_{cmd} = f(error)
]

---

# 11. 🔄 Mode Switching

### Algorithm: State Machine

```text
STATE = {PASSIVE, ASSIST, ADAS, HOLD, FAILSAFE}
```

```text
if override → ASSIST
if ADAS active → FOLLOW
if fault → FAILSAFE
```

---

# 12. 🚨 Emergency Stop / Fail-safe

### Algorithm:

```text
if fault:
    u = 0
    → release to zero
```

---

# 13. 🎯 Calibration / Homing

### Algorithm:

```text
Move until limit switch → set x = 0
```

---

# 🔥 Final Combined Control Law

[
u = K_0(0 - x)

* B\dot{x}

- K_t(x_t - x)
- A\max(\dot{x}, 0)
  ]

---

## 🧠 Interpretation

* (K_0(0 - x)) → return to zero
* (-B\dot{x}) → damping
* (K_t(x_t - x)) → ADAS target tracking
* (A\max(\dot{x},0)) → assist

---

# 🧾 One-Line Summary

> A hybrid control system combining trajectory tracking, assist-as-needed, damping, and safety constraints for brake pedal actuation.

---

# 🚀 Next Step

* Tune gains: `K0, B, Kt, A`
* Map `u → stepper steps`
* Integrate override + ACC logic

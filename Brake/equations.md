# Brake Pedal Control (Impedance + Assist)

## Core Equation

[
u = K_0(0 - x) - B\dot{x} + K_t(x_t - x) + A\max(\dot{x}, 0)
]

---

## Variables

* `u` → motor command (step rate / step output)
* `x` → current pedal position (mm)
* `ẋ` → velocity (mm/s)
* `x_t` → ADAS target position (mm)

---

## Gains

* `K0` → return-to-zero stiffness
* `B` → damping (smoothness)
* `Kt` → target stiffness (ADAS hold)
* `A` → assist gain (press boost)

---

## Behavior Breakdown

### 1. Return to Zero

`K0(0 - x)`

* Pulls pedal back to **0 mm**
* Active mainly when ADAS is OFF

---

### 2. Damping

`-Bẋ`

* Opposes motion
* Removes jerks and oscillations

---

### 3. Target Hold (ADAS)

`Kt(x_t - x)`

* Moves pedal to target
* Holds brake position

---

### 4. Assist (Press Only)

`A max(ẋ, 0)`

* Active only when pressing (`ẋ > 0`)
* Adds boost → “power brake feel”

---

## Modes

### ADAS OFF

[
u = -K_0 x - B\dot{x}
]

* Pedal returns smoothly to zero

---

### ADAS ON

[
u = K_0(0 - x) - B\dot{x} + K_t(x_t - x) + A\max(\dot{x}, 0)
]

* Tracks target
* Assists driver input

---

## Key Behavior

* Press → assist
* Hold → stable
* Release → smooth return to zero
* Fast press → more assist

---

## Tuning Tips

* ↑ `K0` → faster return
* ↑ `B` → smoother, less oscillation
* ↑ `Kt` → stronger hold
* ↑ `A` → stronger assist

---

## One-Line Summary

> Virtual spring to zero + damping + target tracking + press-based assist.

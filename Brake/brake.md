# **Design and Control of an Exoskeleton-Inspired Pedal Robot for ADAS Brake Actuation**

---

## **Abstract**

This paper presents the design and implementation of a low-cost retrofit brake actuation system, referred to as a *pedal robot*, for Advanced Driver Assistance Systems (ADAS). The system converts high-level deceleration commands into physical brake pedal motion using a stepper-driven cable actuator. Inspired by exoskeleton control principles, the system enables shared control between human driver input and automated braking. A closed-loop control strategy based on position feedback, damping, and assistive force emulation is proposed. The system incorporates safety mechanisms such as override detection, fail-safe disengagement, and watchdog monitoring. Experimental design considerations and control formulations are discussed to bridge the gap between digital ADAS commands and physical vehicle actuation.

---

## **I. Introduction**

Advanced Driver Assistance Systems (ADAS) rely on precise brake actuation to achieve functionalities such as Adaptive Cruise Control (ACC) and collision avoidance. Most commercial implementations integrate directly with the vehicle’s braking system through electronic control units (ECUs). However, retrofit solutions require indirect actuation mechanisms.

This work proposes a **pedal robot** capable of physically actuating the brake pedal based on ADAS commands. Unlike conventional systems, the proposed design incorporates **exoskeleton-inspired control**, allowing seamless interaction between automated control and human input.

The main contributions of this paper are:

* A retrofit-compatible brake actuation mechanism
* A nonlinear mapping between deceleration and pedal stroke
* A unified control law combining tracking, damping, and assistive behavior
* A safety architecture for real-time operation

---

## **II. System Architecture**

The overall system converts ADAS commands into mechanical pedal motion using a feedback-controlled actuator.

### **A. System Block Diagram**

```text
ADAS Command (ACC_CMD)
        ↓
Deceleration Mapping
        ↓
Control Algorithm
        ↓
Motor Actuation
        ↓
Brake Pedal
        ↓
Vehicle Braking
        ↑
Position Feedback
```

---

### **B. Hardware Components**

1. **Sensor System**

   * String potentiometer for pedal position feedback
   * Optional current sensing for force estimation

2. **Actuation System**

   * Stepper motor
   * Cable-driven linear actuator

3. **Controller**

   * Microcontroller (ESP32 / STM32)
   * CAN interface for ADAS communication

---

## **III. System Modeling**

---

### **A. Deceleration to Stroke Mapping**

ADAS provides a desired deceleration:

[
a_{target}
]

This is mapped to pedal stroke:

[
x_{target} = f(a_{target})
]

A nonlinear relationship is used:

[
x_{target} = K \cdot |a_{target}|^n
]

where:

* (x_{target}): pedal displacement (mm)
* (K): scaling factor
* (n > 1): nonlinear gain

---

### **B. System Constraints**

[
0 \leq x_{target} \leq x_{max}
]

where (x_{max} \approx 30 , \text{mm})

---

## **IV. Control Strategy**

---

### **A. Closed-Loop Tracking**

Define:

[
e = x_{target} - x
]

[
\dot{x} = \frac{dx}{dt}
]

A proportional-derivative (PD) controller is used:

[
u = K_p e - K_d \dot{x}
]

---

### **B. Exoskeleton-Inspired Control Law**

To enable human-machine interaction, the control law is extended as:

[
u = K_0 (0 - x) - B \dot{x} + K_t (x_{target} - x) + A \cdot \max(\dot{x}, 0)
]

---

### **C. Interpretation**

* (K_0(0-x)): restores pedal to neutral position
* (-B\dot{x}): damping to avoid oscillations
* (K_t(x_{target}-x)): ADAS tracking
* (A \cdot \max(\dot{x}, 0)): assistive force when driver presses

---

## **V. Human Override Detection**

Driver intervention is detected using position deviation:

[
x > x_{target} + \Delta
]

When triggered:

* Automated control is disabled
* Actuator is released
* Driver gains full control

---

## **VI. Safety Mechanisms**

---

### **A. Fault Detection**

* Sensor freeze detection
* CAN communication timeout
* Overstroke detection
* Thermal limits

---

### **B. Fail-Safe Behavior**

[
u = 0
]

System actions:

* Disable motor
* Release actuator
* Reset control state

---

## **VII. Implementation**

---

### **A. Software Architecture**

The control loop operates as follows:

```cpp
readSensors();
readCAN();

x_target = map(a_target);

error = x_target - x;
velocity = dx/dt;

u = Kp*error - Kd*velocity + K0*(0-x) + A*max(velocity,0);

if(failure || override)
    u = 0;

applyMotor(u);
```

---

### **B. Integration with ADAS**

The system receives braking commands via CAN messages and converts them into actuator commands. Feedback signals are optionally transmitted for monitoring.

---

## **VIII. Calibration and Tuning**

---

### **A. Data Collection**

* Record pedal stroke vs deceleration
* Generate mapping function

---

### **B. Parameter Tuning**

* (K_p): tracking responsiveness
* (K_d): damping
* (K_0): return stiffness
* (A): assist gain

---

## **IX. Challenges**

* Nonlinear brake dynamics
* Mechanical backlash
* Sensor noise
* Real-time constraints
* Safety-critical operation

---

## **X. Future Work**

* Adaptive control based on driver behavior
* Model Predictive Control (MPC)
* Sensor fusion for improved estimation
* Redundant safety systems

---

## **XI. Conclusion**

This paper presented a novel pedal robot system for ADAS brake actuation. By combining nonlinear mapping, closed-loop control, and exoskeleton-inspired interaction, the system enables effective and safe human-machine collaboration. The approach demonstrates a practical pathway for retrofit ADAS solutions without direct integration into vehicle braking systems.

---

## **References**

[1] Automotive Control Systems, Rajesh Rajamani
[2] Exoskeleton Control Systems Literature
[3] ADAS and ACC Control Strategies
[4] Embedded Systems Safety Design Practices

---

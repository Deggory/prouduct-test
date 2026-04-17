# 🚗 CAN AI Reverse Engineering Tool

## 🔥 Features

### 🧠 Intelligent Detection
- Auto detects:
  - Steering (angle & torque)
  - Wheel speeds (4 clustering)
  - Accelerator (dual signals)
  - Brake / Indicator (binary)
- Uses:
  - Correlation analysis
  - Time alignment
  - Signal smoothness classification

---

### 🎯 Calibration-Aware Capture
- Capture ONLY during user-triggered windows
- Improves accuracy massively

---

### 🔍 Signal Analysis Engine
- Byte-level extraction
- Cross-correlation grouping
- Smoothness scoring
- Signal classification

---

### 📊 Smart Confidence Scoring
- Each detected signal gets %
- Based on:
  - consistency
  - grouping
  - behavior match

---

### 🧩 Auto Grouping
- Finds:
  - duplicate sensors (accel1/accel2)
  - wheel clusters
  - related signals

---

### 🧠 Signal Behavior Detection
- Smooth → speed
- Moderate → steering
- Binary → brake/indicator
- Periodic → indicators

---

### 🧾 Auto DBC Generator
- One-click DBC export
- Signals pre-labeled
- Ready for Cabana / Openpilot

---

### 🖥️ UI Features
- Start / Stop capture
- Live detection results
- Confidence display
- Final DBC preview

---

### 🔌 Panda Integration
- Auto-detect USB Panda
- Reads CAN directly
- Multi-bus support ready

---

## 🚀 How It Works

1. Connect Panda
2. Click "Start Capture"
3. Perform actions:
   - turn wheel
   - press brake
   - accelerate
4. Click "Analyze"
5. Tool auto-detects signals
6. DBC generated instantly

---

## 🔧 Future Additions

- Bit-level decoder UI
- Manual signal override
- ML training on logs
- MITM CAN injection
- Gear / clutch detection
- Cruise control detection

---

## ⚠️ Disclaimer
For research purposes only. Do NOT use on public roads.

---

## 💡 Summary

This tool replicates core ideas used in:
- OEM calibration tools
- CAN reverse engineering platforms
- ADAS development pipelines

But simplified into a **single AI-assisted workflow**

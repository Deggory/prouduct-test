# 🚗 CAN AI Reverse Engineering Tool

A Python-based tool to **capture CAN data from Panda**, automatically detect key vehicle signals, and generate a **ready-to-use DBC file**.

---

# 🔥 Features

## 🧠 Intelligent Detection

Automatically detects:

* Steering angle & torque
* Wheel speeds (auto-clustered)
* Vehicle speed
* RPM (partially inferred)
* Accelerator (dual sensors)
* Brake (pressed / pressure candidate)
* Indicator (left/right pattern)

Uses:

* Signal correlation (time-aligned)
* Smoothness classification
* Signal grouping (AI-style heuristics)

---

## 🎯 Smart Capture System

* Capture only when you want (Start/Stop)
* Designed for calibration-style testing
* Improves detection accuracy

---

## 📊 Confidence Scoring

* Each detected signal has a confidence %
* Based on:

  * signal behavior
  * correlation strength
  * grouping quality

---

## 🧾 Auto DBC Generator

* One-click DBC creation
* Pre-labeled signals
* Works with tools like Cabana / Openpilot

---

## 🖥️ UI (Tkinter)

* Start Capture button
* Stop + Analyze button
* Live detection output
* Final DBC preview in window

---

## 🔌 Panda Integration

* Auto-detects Panda via USB
* Reads raw CAN frames
* Supports multi-bus (expandable)

---

# 🧰 Requirements

## 🐍 Python Version

* Python **3.8 – 3.11 recommended**

Check:

```bash
python --version
```

---

## 📦 Required Python Packages

Install all dependencies:

```bash
pip install numpy pyusb
```

### 📌 What each does:

* `numpy` → signal processing (correlation, smoothing)
* `pyusb` → communication with Panda

---

## 🔌 USB Setup (VERY IMPORTANT)

### Linux (Ubuntu / Debian)

Install USB access:

```bash
sudo apt install libusb-1.0-0
```

Add permissions:

```bash
sudo usermod -aG plugdev $USER
```

(Optional udev rule for Panda)

```bash
sudo nano /etc/udev/rules.d/11-panda.rules
```

Paste:

```text
SUBSYSTEM=="usb", ATTR{idVendor}=="bbaa", ATTR{idProduct}=="ddcc", MODE="0666"
```

Then:

```bash
sudo udevadm control --reload-rules
```

---

### Windows

Install:

* Zadig (USB driver tool)

Steps:

1. Open Zadig
2. Select Panda device
3. Install **WinUSB driver**

---

# 📂 Project Setup

## 1. Create project folder

```bash
mkdir can_ai_tool
cd can_ai_tool
```

---

## 2. Add files

Create these files:

```
main.py
panda_interface.py
signal_processing.py
detector.py
dbc_generator.py
ui.py
```

Paste the code I gave you into each file.

---

# ▶️ Running the Tool

## Step 1: Connect Panda

Plug Panda into USB (car optional for testing, but recommended).

---

## Step 2: Run program

```bash
python main.py
```

---

## Step 3: Use UI

### In the window:

1. Click:

```
Start Capture
```

2. Perform actions in car:

* Turn steering left/right
* Press brake
* Accelerate
* Use indicator

3. Click:

```
Stop & Analyze
```

---

## 🎯 Output

You will see:

```text
wheel_speed (90%)
accelerator (85%)
vehicle_speed (80%)
brake_or_indicator (70%)
```

Then:

```
=== GENERATED DBC ===
BO_ ...
 SG_ ...
```

---

# 🧠 How Detection Works

## 1. Extract Signals

* Splits CAN data into byte-level signals

## 2. Analyze Behavior

* Smoothness → speed vs steering
* Unique values → binary signals

## 3. Correlation Engine

* Finds related signals:

  * accel1 ↔ accel2
  * 4 wheel speeds

## 4. Grouping

* Clusters signals into meaningful sets

## 5. Labeling

* Assigns best guess:

  * wheel_speed
  * accelerator
  * brake
  * steering

---

# 🔧 Customization (IMPORTANT)

## ➕ Add new signal detection

Example: clutch

Edit `detector.py`

```python
elif t == "binary" and size == 1:
    label = "clutch"
```

---

## ➕ Improve accuracy

* Capture longer data
* Perform clear actions (one at a time)
* Avoid noise (keep car steady when possible)

---

# ⚠️ Troubleshooting

## ❌ Panda not found

* Check USB connection
* Run:

```bash
lsusb
```

* Verify:

```
idVendor=0xbbaa idProduct=0xddcc
```

---

## ❌ Permission denied

Run:

```bash
sudo python main.py
```

(or fix udev rules properly)

---

## ❌ No CAN data

* Car ignition ON required
* Ensure Panda connected to CAN lines

---

## ❌ UI not opening

Install Tkinter:

### Linux:

```bash
sudo apt install python3-tk
```

---

# 🚀 Future Upgrades

Planned / can be added:

* 📊 Live graph (Cabana-style)
* 🧩 Bit-level decoder (click bits)
* 🧠 ML training on logs
* 🔧 MITM CAN injection
* 🚗 Gear & clutch detection
* 🎮 Cruise control detection

---

# ⚠️ Safety Disclaimer

This tool is for:

* Reverse engineering
* Research
* Development

❌ Do NOT use for controlling vehicle on public roads.

---

# 💡 Summary

This system combines:

* CAN sniffing
* Signal intelligence
* AI-style pattern detection

To create a **semi-automated DBC generator**, similar in concept to professional automotive tools.

---

# 🙌 Next Step

If you want, I can upgrade this into:

👉 Full **Cabana-style UI (graphs + bit decoding)**
👉 Real-time signal plotting
👉 AI-assisted labeling with training

Just tell me 🚀

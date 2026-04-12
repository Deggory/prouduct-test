# 🚗 Automotive Steering CAN Dashboard (ESP32 + MCP2515)

A real-time CAN bus steering visualization system using **ESP32 + MCP2515 + Python (Tkinter GUI)** with **Kalman filtering, velocity estimation, and smooth steering animation**.

It decodes steering data from CAN ID `0x25` and displays:
- Steering angle (real-time)
- Steering rate (derived & filtered)
- Live CAN frame monitor
- Smooth steering needle gauge

---

# 📌 Features

## 🧠 Signal Processing
- Kalman filter for steering angle smoothing
- Window-based velocity estimation (rate)
- Deadband filtering to remove jitter
- Latency-compensated timing using high precision clock

## 📊 Visualization
- Real-time steering needle gauge
- Live numeric display:
  - Steering angle (°)
  - Steering rate (°/s)
- Live CAN frame log viewer

## 🔌 Hardware Support
- ESP32 (USB serial communication)
- MCP2515 CAN module
- Automatic USB/COM port detection

---

# ⚙️ System Architecture
CAN Bus → MCP2515 → ESP32 → USB Serial → Python GUI


---

# 📡 CAN Frame Format (ID: 0x25)

Example frame:

FRAME 12 | ID:0x25 | LEN:8 | DATA: 10 87 88 00 78 78 00 3C


---

# 🧮 Signal Decoding

## Steering Angle
- 12-bit signed value
- Extracted from bytes 0–1
- Scaling: `* 1.5`

## Steering Fraction
- 4-bit signed nibble (byte 4 high nibble)
- Scaling: `* 0.1`

## Steering Rate
- NOT directly trusted from CAN
- Computed using:

- rate = Δangle / Δtime

- 
- Filtered using:
  - Moving window (last samples)
  - Exponential smoothing
  - Deadband filtering (< 0.5 ignored)

---

# 🧰 Requirements

Install dependencies:

```bash
pip install pyserial matplotlib

🚀 How to Run
1. Connect Hardware
ESP32 connected to MCP2515 CAN module
USB connected to PC
CAN bus connected to vehicle/test system
2. Run GUI
python3 steering_gui.py
🔌 Linux USB Permission Fix

If /dev/ttyUSB0 access fails:

sudo usermod -a -G dialout $USER
reboot
🖥️ GUI Layout
Left Panel
Live CAN frame log
START / STOP controls
Right Panel
Steering gauge (needle display)
Angle and rate values
📈 System Behavior
Condition	Output Behavior
Steering centered	0° angle / 0°s rate
Slow movement	smooth low rate values
Fast movement	high rate response
No movement	stable zero output
⚠️ Important Notes
Steering rate is derived, not directly trusted from CAN
Kalman filter introduces slight smoothing delay (normal)
Low-speed rate may appear near zero due to noise filtering
This system is optimized for stability over raw sensitivity
🔧 Troubleshooting
ESP32 not detected
Check USB cable
Ensure CP210x drivers installed
Try different USB port
No CAN data
Check MCP2515 wiring (SPI lines)
Verify CAN baud rate (default: 500 kbps)
Rate feels delayed or flat
This is expected due to filtering and window averaging
🚀 Future Improvements
True DBC-based automatic decoding
CAN signal reverse engineering tool
Steering torque estimation
OpenPilot / ROS bridge integration
Data logging + replay system
AI-based noise filtering
📜 License

For educational and development use only.


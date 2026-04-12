Universal CAN Steering Angle Sensor Dashboard

A complete ESP32 + MCP2515 + Python GUI toolkit for reverse engineering and testing any CAN-based steering angle sensor.

Designed for:

Toyota / Lexus spiral cable SAS
EPS rack angle sensors
Honda / Hyundai / BMW steering sensors
Unknown junkyard CAN steering modules
Bench calibration and center alignment
Features
ESP32 firmware
MCP2515 init status (OK / FAIL)
CAN alive status (OK / FAIL timeout)
Full CAN sniffer output
Universal unknown CAN ID discovery
Optional Toyota 0x25 decoder path
8 MHz MCP2515 support
Well-commented for GitHub collaboration
Python GUI
Auto-detect serial port
Round steering gauge
Moving needle
Zero center line
Packet counter
Min / Max capture
MCP2515 + CAN status
Live sniffer panel
Automatic steering CAN-ID detection
Confidence score
Universal sensor support 
Installation
pip install pyserial
Wiring
ESP32 ↔ MCP2515
CS -> GPIO5
INT -> GPIO4
SCK -> GPIO18
MISO -> GPIO19
MOSI -> GPIO23
VCC -> 5V
GND -> GND
MCP2515 crystal

This project is configured for:

8 MHz MCP2515
How Auto CAN-ID Detection Works

The GUI watches all sniffed IDs and finds the ID that:

repeats frequently
changes payload during rotation
changes smoothly like steering

Then it prints:

Detected Steering ID: 0xXXX
Confidence: HIGH

This makes it universal for almost any CAN steering sensor.

GitHub README tips

Suggested repo structure:

/firmware/steering_can_dashboard.ino
/gui/steering_dashboard.py
README.md

This document can directly be used as your README.md.

Done — I created a new GitHub-ready README.md style document with:

✅ Included in the new document
final ESP32 firmware
final universal Python GUI
heavy code comments
beginner-friendly explanations
auto CAN-ID detection logic
full wiring section
install steps
GitHub folder structure recommendation
universal sensor workflow
Toyota + unknown sensor support

I also made the code clean enough for new contributors, so anyone helping on GitHub can quickly understand:

sniffer logic
CAN-ID detection
Toyota fast decoder
GUI threading
gauge rendering
packet analysis


✅ Install required package

On Ubuntu:

sudo apt install python3-serial
✅ Run
python3 steering_dashboard.py

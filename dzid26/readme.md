StepperServoCAN Serial Tester

A Tkinter-based Python GUI tool for testing a StepperServoCAN steering actuator using:

Python → USB Serial → ESP32 → CAN

This program sends DBC-encoded steering CAN commands over a serial SLCAN/LAWICEL bridge at 100 Hz.

It is designed for:

steering actuator bench testing
torque mode experiments
angle control validation
joystick-style keyboard steering
openpilot actuator simulation
EPS / steer-by-wire development
Features
DBC-based CAN encoding
USB serial → ESP32 → CAN bridge
Works from any launch directory
100 Hz deterministic transmit loop
Rolling counter + checksum
Configurable CAN ID
Torque + angle control
Torque / Angle / SoftOff modes
Keyboard joystick steering
Live serial RX monitor
Thread-safe GUI updates
Safe shutdown
How It Works

The application uses a DBC file to encode the STEERING_COMMAND CAN message and continuously transmits it through an ESP32 acting as an SLCAN CAN adapter.

The full control chain is:

Python GUI
   ↓
DBC message encode
   ↓
SLCAN serial frame
   ↓
ESP32 USB serial bridge
   ↓
CAN bus
   ↓
StepperServoCAN motor controller

The motor controller firmware handles the actual closed-loop motor control.

Main Code Flow
1) Configuration

The script defines:

serial port
baud rate
CAN bitrate command
100 Hz transmit period
torque limits
angle limits
PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
TX_PERIOD = 0.01
2) DBC Loading

The DBC file is loaded relative to the script location so the code works from any folder.

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DBC_PATH = os.path.join(CURRENT_DIR, 'opendbc', 'ocelot_controls.dbc')

This loads:

STEERING_COMMAND

from the DBC.

3) GUI Inputs

The GUI allows live editing of:

CAN ID
steering torque
steering angle
steering mode

The supported steering modes are:

Off
TorqueControl
AngleControl
SoftOff
4) DBC Payload Builder

The function:

build_payload()

creates the CAN payload by encoding:

STEER_TORQUE
STEER_ANGLE
STEER_MODE
COUNTER
CHECKSUM

using the DBC file.

A rolling 4-bit counter is incremented every frame.

The checksum is calculated as:

sum(message_id + all data bytes) → 8-bit

5) SLCAN Serial Frame Transmission

The CAN payload is converted into LAWICEL/SLCAN ASCII format:

t22E5AABBCCDDEE

and sent through USB serial.

The ESP32 converts this serial frame into a real CAN message.

6) 100 Hz Deterministic Send Loop

A dedicated background thread continuously sends fresh steering commands every 10 ms:

TX_PERIOD = 0.01

This provides:

100 Hz steering command rate

which is suitable for real-time actuator testing.

The loop also prints live transmit frequency statistics.

7) Keyboard Steering Joystick

The left and right arrow keys behave like a steering joystick.

Left Arrow
sets negative torque
enables TorqueControl
rotates motor left
Right Arrow
sets positive torque
enables TorqueControl
rotates motor right
Key Release
sets torque to zero
safely stops steering effort

This makes the tester behave like a simple steering wheel controller.

8) Serial RX Monitor

A second background thread continuously reads serial data from the ESP32 and prints incoming lines:

RX: ...

Useful for:

debugging firmware replies
monitoring motor feedback
checking status messages
9) Safe Shutdown

When the GUI closes:

CAN transmission loop stops
SLCAN channel closes
serial port closes safely
background threads exit cleanly

This prevents stale steering commands.

Control Modes
TorqueControl

Uses:

STEER_TORQUE

Best for:

openpilot simulation
EPS torque assist testing
manual steering control
AngleControl

Uses:

STEER_ANGLE

Best for:

position testing
steering sweep
centering validation
SoftOff

Gradually ramps torque down before disabling.

Useful for safe disengagement testing.

Keyboard Controls
Key	Action
Left Arrow	Apply left steering torque
Right Arrow	Apply right steering torque
Release Key	Set torque to zero
Enter	Apply GUI values
Escape	Quit safely
Use Case

This tool is ideal for:

StepperServoCAN development
EPS bench testing
steer-by-wire experiments
Polo EPS projects
openpilot lateral actuator simulation
CAN motor controller debugging
Notes

This script only sends high-level steering commands.

The actual motor control (step generation, current control, position loop, thermal protection) is handled by the StepperServoCAN firmware.

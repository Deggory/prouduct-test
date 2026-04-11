import tkinter as tk
import serial
from serial.tools import list_ports
import pygame
import threading
import queue
import time

# =========================================================
# CONFIGURATION (USER EDITABLE)
# =========================================================
BAUD = 115200
SERIAL_WATCHDOG_MS = 200           # Timeout before emergency stop (ms)
SERIAL_TIMEOUT = 0.1               # Serial read timeout (seconds) - increased from 0.05

ESP32_KEYWORDS = [
    "CP210", "CH340", "USB Serial",
    "ttyUSB", "ttyACM", "COM"
]

STEER_DEADZONE = 0.05
THROTTLE_DEADZONE = 0.10

MAX_STEER = 300
MAX_SPEED = 140.0

ACCEL_RATE = 40.0                  # km/h per second at full throttle
BRAKE_RATE = 60.0                  # km/h per second at full brake
DRAG_RATE = 10.0                   # km/h per second coasting drag
WATCHDOG_DRAG_MULTIPLIER = 2.0     # Extra drag when watchdog active (e.g., 2 = double)

MAX_STEP = 8                       # Steering slew limit per 20ms

STEER_AXIS = 0
THROTTLE_AXIS = 1
THROTTLE_INVERT = True

FAULTS = {
    0: "NO_FAULT",
    1: "TIMEOUT",
    2: "TIMEOUT_VSS",
    3: "BAD_CHECKSUM",
    4: "SEND_FAIL",
    5: "SENSOR",
    6: "ADC_UNCONFIG",
}

# =========================================================
# GLOBAL STATE
# =========================================================
speed_kph = 0.0
current_steer = 0
throttle_input = 0.0

telemetry_tx = 0
telemetry_rx = 0

last_time = None
last_serial_send = 0.0

running = True

ser = None
current_port = None

js = None
joystick_name = "Not Connected"

data_queue = queue.Queue()

# =========================================================
# PYGAME INIT
# =========================================================
pygame.init()
pygame.joystick.init()

# =========================================================
# HELPERS
# =========================================================
def slew_limit(target, current):
    """Apply steering slew rate limiting."""
    if target > current + MAX_STEP:
        return current + MAX_STEP
    if target < current - MAX_STEP:
        return current - MAX_STEP
    return target


def clamp_axis(value):
    """Clamp joystick axis value to [-1.0, 1.0]."""
    return max(-1.0, min(1.0, value))


def find_esp32_port():
    """Auto-detect ESP32 serial port by VID/PID or keyword."""
    ports = list(list_ports.comports())

    # Method 1: known VID/PID pairs
    for p in ports:
        vid = getattr(p, "vid", None)
        pid = getattr(p, "pid", None)
        if (vid, pid) in [
            (0x10C4, 0xEA60),  # CP210x
            (0x1A86, 0x7523),  # CH340
            (0x0403, 0x6001),  # FTDI
        ]:
            return p.device

    # Method 2: keyword in description or device name
    for p in ports:
        desc = f"{p.description} {p.device}".lower()
        if any(k.lower() in desc for k in ESP32_KEYWORDS):
            return p.device

    return None


def open_serial():
    """Establish serial connection to ESP32 (auto-reconnect)."""
    global ser, current_port

    port = find_esp32_port()
    if not port:
        current_port = None
        return False

    # Already connected to the same port?
    if ser and ser.is_open and current_port == port:
        return True

    # Close any existing connection
    try:
        if ser and ser.is_open:
            ser.close()
    except Exception:
        pass

    # Open new connection
    try:
        ser = serial.Serial(port, BAUD, timeout=SERIAL_TIMEOUT)
        current_port = port
        print(f"ESP32 connected on {port}")
        return True
    except Exception as e:
        print("Serial open error:", e)
        current_port = None
        return False


def detect_joystick():
    """Detect and initialise joystick (hotplug aware)."""
    global js, joystick_name

    if js is not None and js.get_init():
        return True

    pygame.joystick.quit()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        js = None
        joystick_name = "Not Connected"
        return False

    js = pygame.joystick.Joystick(0)
    js.init()
    joystick_name = js.get_name()
    print("Joystick connected:", joystick_name)
    return True


def update_speed(dt, throttle_axis):
    """Update speed using acceleration, braking, and drag."""
    global speed_kph

    if dt <= 0:
        return
    if dt > 0.1:          # Cap delta time to avoid large jumps
        dt = 0.1

    if abs(throttle_axis) < THROTTLE_DEADZONE:
        throttle_axis = 0.0

    if throttle_axis > 0:
        speed_kph += throttle_axis * ACCEL_RATE * dt
    elif throttle_axis < 0:
        speed_kph -= abs(throttle_axis) * BRAKE_RATE * dt
    else:
        speed_kph -= DRAG_RATE * dt

    speed_kph = max(0.0, min(MAX_SPEED, speed_kph))


# =========================================================
# SERIAL READER THREAD
# =========================================================
def serial_reader():
    """Background thread: read telemetry lines from ESP32."""
    global ser, current_port, running

    while running:
        if not open_serial():
            time.sleep(0.5)
            continue

        try:
            line = ser.readline().decode(errors="ignore").strip()
            if line.startswith("TEL,"):
                data_queue.put(("TEL", line))
        except Exception:
            # Serial error - close and mark as dead
            try:
                ser.close()
            except Exception:
                pass
            ser = None
            current_port = None
            time.sleep(0.5)


# =========================================================
# GUI UPDATE (MAIN THREAD)
# =========================================================
def update_gui():
    """Process incoming telemetry and refresh labels."""
    global telemetry_rx

    # Process all pending telemetry frames
    try:
        while True:
            cmd, value = data_queue.get_nowait()
            if cmd == "TEL":
                parts = value.split(",")
                if len(parts) == 7:
                    _, adc0, adc1, override, fault, counter, relay = parts
                    telemetry_rx += 1
                    labels["adc0"].config(text=f"ADC0: {adc0}")
                    labels["adc1"].config(text=f"ADC1: {adc1}")
                    labels["override"].config(text=f"Override: {override}")
                    labels["fault"].config(
                        text=f"Fault: {FAULTS.get(int(fault), fault)}"
                    )
                    labels["relay"].config(
                        text=f"Relay: {'ON' if int(relay) else 'OFF'}"
                    )
                    labels["counter"].config(text=f"Counter: {counter}")
                    labels["rx"].config(text=f"RX: {telemetry_rx}")
    except queue.Empty:
        pass

    # Update status and other dynamic labels
    serial_status = current_port if current_port else "Searching ESP32"
    labels["status"].config(
        text=f"ESP32: {serial_status} | JS: {joystick_name}"
    )
    labels["tx"].config(text=f"TX: {telemetry_tx}")
    labels["steer"].config(text=f"Steer: {current_steer}")
    labels["speed"].config(text=f"Speed: {speed_kph:.1f} km/h")
    labels["throttle"].config(text=f"Throttle: {throttle_input:+.2f}")

    root.after(50, update_gui)   # Refresh at 20 Hz


# =========================================================
# MAIN CONTROL LOOP (50 Hz)
# =========================================================
def send_command():
    """Send CAN commands at 50 Hz, with watchdog safety."""
    global telemetry_tx, current_steer, throttle_input
    global last_time, last_serial_send, speed_kph, ser, current_port

    now = time.monotonic()

    # Initialise timestamps on first run
    if last_time is None:
        last_time = now
        last_serial_send = now
        root.after(20, send_command)
        return

    dt = now - last_time
    last_time = now

    # Check if serial communication is stalled
    watchdog_triggered = (now - last_serial_send) > (SERIAL_WATCHDOG_MS / 1000.0)

    if watchdog_triggered:
        # Emergency stop: zero throttle, centre steering, extra drag
        throttle_input = 0.0
        current_steer = slew_limit(0, current_steer)
        update_speed(dt, 0.0)
        # Apply extra drag when watchdog active
        speed_kph = max(0.0, speed_kph - DRAG_RATE * dt * WATCHDOG_DRAG_MULTIPLIER)
    else:
        # Normal operation: read joystick (if available)
        if not detect_joystick():
            throttle_input = 0.0
            current_steer = slew_limit(0, current_steer)
            update_speed(dt, 0.0)
        else:
            pygame.event.pump()

            # Steering axis (clamped)
            steer_axis = js.get_axis(STEER_AXIS)
            steer_axis = clamp_axis(steer_axis)
            if abs(steer_axis) < STEER_DEADZONE:
                steer_axis = 0.0
            target_steer = int(steer_axis * MAX_STEER)
            current_steer = slew_limit(target_steer, current_steer)

            # Throttle axis (clamped)
            throttle_axis = js.get_axis(THROTTLE_AXIS)
            throttle_axis = clamp_axis(throttle_axis)
            if THROTTLE_INVERT:
                throttle_axis = -throttle_axis
            throttle_input = throttle_axis

            update_speed(dt, throttle_axis)

    # Always send a command (either normal or safety zeros) if serial is open
    if ser and ser.is_open:
        try:
            cmd = f"CMD,{current_steer},{int(round(speed_kph))}\n"
            ser.write(cmd.encode())
            telemetry_tx += 1
            last_serial_send = now   # Reset watchdog timer on successful send
        except Exception:
            # Write failed – mark serial as dead
            ser = None
            current_port = None

    root.after(20, send_command)   # 50 Hz


# =========================================================
# KEYBOARD OVERRIDE (OPTIONAL)
# =========================================================
def key_handler(event):
    """Keyboard controls: '+'/'-' to adjust speed (for testing)."""
    global speed_kph
    if event.keysym in ("plus", "equal"):
        speed_kph = min(MAX_SPEED, speed_kph + 5)
    elif event.keysym == "minus":
        speed_kph = max(0, speed_kph - 5)


# =========================================================
# CLEAN SHUTDOWN
# =========================================================
def on_closing():
    """Gracefully close serial port, quit pygame, destroy window."""
    global running
    running = False

    try:
        if ser and ser.is_open:
            ser.close()
    except Exception:
        pass

    pygame.quit()
    root.destroy()


# =========================================================
# BUILD GUI WINDOW
# =========================================================
root = tk.Tk()
root.title("Interceptor Pro Dashboard - Final")
root.geometry("620x760")
root.protocol("WM_DELETE_WINDOW", on_closing)
root.bind("<Key>", key_handler)

labels = {}
for key in [
    "status", "steer", "speed", "throttle",
    "adc0", "adc1", "override", "fault",
    "relay", "counter", "tx", "rx"
]:
    labels[key] = tk.Label(root, text=f"{key}: ---", font=("Arial", 18))
    labels[key].pack(pady=5)

# Start background serial reader thread
threading.Thread(target=serial_reader, daemon=True).start()

# Start GUI update and main control loop
root.after(100, update_gui)
root.after(20, send_command)

# Start Tkinter event loop
root.mainloop()

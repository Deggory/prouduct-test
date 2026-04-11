import tkinter as tk
import serial
import pygame
import threading
import queue
import time
import math

# ========== CONFIGURATION ==========
PORT = "/dev/ttyUSB0"   # Change to COM5 on Windows
BAUD = 115200

# Joystick thresholds
STEER_DEADZONE = 0.05
THROTTLE_DEADZONE = 0.10
MAX_STEER = 300
MAX_SPEED = 140.0      # km/h (new limit)

# Acceleration / drag simulation constants (km/h per second)
ACCEL_RATE = 40.0      # Full throttle acceleration
BRAKE_RATE = 60.0      # Full brake deceleration
DRAG_RATE = 10.0       # Coasting drag when throttle neutral

# Slew limiting for steering (unchanged)
MAX_STEP = 8

FAULTS = {
    0: "NO_FAULT",
    1: "TIMEOUT",
    2: "TIMEOUT_VSS",
    3: "BAD_CHECKSUM",
    4: "SEND_FAIL",
    5: "SENSOR",
    6: "ADC_UNCONFIG",
}

# ========== GLOBAL STATE ==========
speed_kph = 0.0
current_steer = 0
running = True
telemetry_tx = 0
telemetry_rx = 0
last_time = None          # For delta time calculation
throttle_input = 0.0      # -1 (full brake) .. +1 (full throttle)

# Queue for passing data from serial thread to GUI
data_queue = queue.Queue()

# Serial port (will be opened later)
ser = None

# Joystick init
pygame.init()
pygame.joystick.init()
if pygame.joystick.get_count() == 0:
    print("No joystick found. Exiting.")
    exit(1)
js = pygame.joystick.Joystick(0)
js.init()
print(f"Joystick: {js.get_name()}")
print(f"Number of axes: {js.get_numaxes()}")


# ========== HELPER FUNCTIONS ==========
def slew_limit(target, current):
    if target > current + MAX_STEP:
        return current + MAX_STEP
    if target < current - MAX_STEP:
        return current - MAX_STEP
    return target


def open_serial():
    """Try to open serial port. Return True on success."""
    global ser
    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.05)
        return True
    except Exception as e:
        print(f"Serial error: {e}")
        return False


# ========== SPEED SIMULATION ==========
def update_speed(dt, throttle_axis):
    """
    Update global speed_kph based on throttle axis and drag.
    throttle_axis: -1 (full brake) .. +1 (full throttle)
    """
    global speed_kph
    if dt <= 0 or dt > 0.1:
        return

    # Apply deadzone
    if abs(throttle_axis) < THROTTLE_DEADZONE:
        throttle_axis = 0.0

    # Separate throttle (positive) and brake (negative)
    if throttle_axis > 0:
        # Acceleration
        accel_force = throttle_axis * ACCEL_RATE * dt
        speed_kph += accel_force
    elif throttle_axis < 0:
        # Braking
        brake_force = abs(throttle_axis) * BRAKE_RATE * dt
        speed_kph -= brake_force
    else:
        # Coasting drag
        speed_kph -= DRAG_RATE * dt

    # Clamp speed
    speed_kph = max(0.0, min(MAX_SPEED, speed_kph))


# ========== SERIAL READER THREAD ==========
def serial_reader():
    """Continuously read lines from serial and push them into a queue."""
    global ser, running
    while running:
        if ser is None or not ser.is_open:
            time.sleep(0.5)
            continue
        try:
            line = ser.readline().decode(errors="ignore").strip()
            if line.startswith("TEL,"):
                data_queue.put(("TEL", line))
        except Exception:
            ser = None
            time.sleep(0.5)


# ========== GUI UPDATE FUNCTIONS (called from main thread) ==========
def update_gui():
    """Process queued telemetry and steering updates."""
    global telemetry_tx, telemetry_rx
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
                    fault_text = FAULTS.get(int(fault), fault)
                    labels["fault"].config(text=f"Fault: {fault_text}")
                    labels["relay"].config(text=f"Relay: {'ON' if int(relay) else 'OFF'}")
                    labels["counter"].config(text=f"Counter: {counter}")
                    labels["rx"].config(text=f"RX: {telemetry_rx}")
            elif cmd == "STATUS":
                labels["status"].config(text=f"Status: {value}")
    except queue.Empty:
        pass

    # Update TX counter, steering, speed, and throttle display
    labels["tx"].config(text=f"TX: {telemetry_tx}")
    labels["steer"].config(text=f"Steer: {current_steer}")
    labels["speed"].config(text=f"Speed: {speed_kph:.1f} km/h")
    labels["throttle"].config(text=f"Throttle: {throttle_input:+.2f}")

    # Check serial connection
    if ser is None or not ser.is_open:
        if open_serial():
            data_queue.put(("STATUS", "Connected"))
        else:
            data_queue.put(("STATUS", "Disconnected"))

    root.after(50, update_gui)  # 20 Hz GUI refresh


def send_command():
    """Send CMD frame to ESP32 at 50 Hz, with speed simulation."""
    global telemetry_tx, current_steer, speed_kph, ser, last_time, throttle_input
    now = time.monotonic()
    if last_time is None:
        last_time = now
        root.after(20, send_command)
        return

    dt = now - last_time
    last_time = now

    # Read joystick axes
    pygame.event.pump()
    # Steering: axis 0 (left/right)
    steer_axis = js.get_axis(0)
    if abs(steer_axis) < STEER_DEADZONE:
        steer_axis = 0
    target_steer = int(steer_axis * MAX_STEER)
    current_steer = slew_limit(target_steer, current_steer)

    # Throttle / brake: axis 1 (up/down) - up = negative, down = positive
    # Invert so that up (negative) gives positive throttle (acceleration)
    throttle_axis = -js.get_axis(1)   # Now up = +1 throttle, down = -1 brake
    throttle_input = throttle_axis    # Store for display

    # Update speed with simulation
    update_speed(dt, throttle_axis)

    # Send command if serial is open
    if ser and ser.is_open:
        try:
            # Speed value sent to ESP32 must be integer (0..655)
            speed_int = int(round(speed_kph))
            cmd = f"CMD,{current_steer},{speed_int}\n"
            ser.write(cmd.encode())
            telemetry_tx += 1
            data_queue.put(("STATUS", "Sending"))
        except Exception:
            ser = None

    root.after(20, send_command)  # 50 Hz


def key_handler(event):
    """Optional keyboard override for debugging (still works)."""
    global speed_kph
    if event.keysym in ("plus", "equal"):
        speed_kph = min(MAX_SPEED, speed_kph + 5)
    elif event.keysym == "minus":
        speed_kph = max(0, speed_kph - 5)


def on_closing():
    """Clean shutdown."""
    global running
    running = False
    if ser and ser.is_open:
        ser.close()
    root.destroy()


# ========== BUILD GUI ==========
root = tk.Tk()
root.title("Interceptor Pro Dashboard - Speed Simulation")
root.geometry("560x750")
root.protocol("WM_DELETE_WINDOW", on_closing)

labels = {}
for key in ["status", "steer", "speed", "throttle", "adc0", "adc1",
            "override", "fault", "relay", "counter", "tx", "rx"]:
    labels[key] = tk.Label(root, text=f"{key}: ---", font=("Arial", 18))
    labels[key].pack(pady=5)

# Bind keyboard (optional)
root.bind("<Key>", key_handler)

# Start serial reader thread
threading.Thread(target=serial_reader, daemon=True).start()

# Start GUI periodic updates
root.after(100, update_gui)

# Start command sender (main thread via after)
root.after(20, send_command)

# Run main loop
root.mainloop()

# Cleanup
running = False
pygame.quit()

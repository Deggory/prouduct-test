import tkinter as tk
import serial
import pygame
import threading
import queue
import time

# ========== CONFIGURATION ==========
PORT = "/dev/ttyUSB0"   # Change to COM5 on Windows
BAUD = 115200

DEADZONE = 0.05
MAX_STEP = 8
MAX_STEER = 300
MAX_SPEED = 655      # km/h (ESP32 limit)

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
speed_kph = 0
current_steer = 0
running = True
telemetry_tx = 0
telemetry_rx = 0

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
            # Serial error – try to reopen later
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
                # Parse telemetry line
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
                # Update connection status
                labels["status"].config(text=f"Status: {value}")
    except queue.Empty:
        pass

    # Update TX counter and other values that change outside telemetry
    labels["tx"].config(text=f"TX: {telemetry_tx}")
    labels["steer"].config(text=f"Steer: {current_steer}")
    labels["speed"].config(text=f"Speed: {speed_kph} km/h")

    # Check serial connection periodically
    if ser is None or not ser.is_open:
        if open_serial():
            data_queue.put(("STATUS", "Connected"))
        else:
            data_queue.put(("STATUS", "Disconnected"))

    root.after(50, update_gui)  # Update GUI at ~20 Hz (fast enough)


def send_command():
    """Send CMD frame to ESP32 at 50 Hz."""
    global telemetry_tx, current_steer, speed_kph, ser
    if ser and ser.is_open:
        try:
            # Read joystick (non-blocking)
            pygame.event.pump()
            axis = js.get_axis(0)
            if abs(axis) < DEADZONE:
                axis = 0
            target = int(axis * MAX_STEER)
            current_steer = slew_limit(target, current_steer)

            # Build command
            cmd = f"CMD,{current_steer},{speed_kph}\n"
            ser.write(cmd.encode())
            telemetry_tx += 1

            # Update labels (via queue to avoid direct calls from timer)
            data_queue.put(("STATUS", "Sending"))
        except Exception:
            # Write error – mark serial as dead
            ser = None
    # Schedule next send
    root.after(20, send_command)  # 50 Hz


def key_handler(event):
    global speed_kph
    if event.keysym in ("plus", "equal"):
        speed_kph = min(MAX_SPEED, speed_kph + 10)
    elif event.keysym == "minus":
        speed_kph = max(0, speed_kph - 10)
    # Label will be updated in update_gui


def on_closing():
    """Clean shutdown."""
    global running
    running = False
    if ser and ser.is_open:
        ser.close()
    root.destroy()


# ========== BUILD GUI ==========
root = tk.Tk()
root.title("Interceptor Pro Dashboard")
root.geometry("520x700")
root.protocol("WM_DELETE_WINDOW", on_closing)

labels = {}
for key in ["status", "steer", "speed", "adc0", "adc1",
            "override", "fault", "relay", "counter", "tx", "rx"]:
    labels[key] = tk.Label(root, text=f"{key}: ---", font=("Arial", 18))
    labels[key].pack(pady=5)

# Bind keyboard
root.bind("<Key>", key_handler)

# Start serial reader thread
threading.Thread(target=serial_reader, daemon=True).start()

# Start GUI periodic updates
root.after(100, update_gui)

# Start command sender (runs in main thread via after())
root.after(20, send_command)

# Run main loop
root.mainloop()

# Cleanup
running = False
pygame.quit()

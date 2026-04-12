import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import time
import math
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque

# =========================
# GLOBAL STATE
# =========================
angle_filtered = 0.0
rate_filtered = 0.0

running = True
ser = None

history = deque(maxlen=12)

last_time = time.perf_counter()

ANGLE_DEADBAND = 0.8

# =========================
# AUTO DETECT ESP32
# =========================
def find_esp32():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if "USB" in p.description or "UART" in p.description or "CP210" in p.description:
            return p.device
    return None

# =========================
# SIMPLE KALMAN FILTER
# =========================
class Kalman1D:
    def __init__(self):
        self.x = 0.0
        self.p = 1.0
        self.q = 0.05
        self.r = 5

    def update(self, z):
        self.p += self.q
        k = self.p / (self.p + self.r)
        self.x += k * (z - self.x)
        self.p *= (1 - k)
        return self.x

kalman = Kalman1D()

# =========================
# DECODER
# =========================
def decode_steering(data):
    global rate_filtered, last_time

    # -------------------------
    # ANGLE (12-bit signed)
    # -------------------------
    angle_raw = ((data[0] & 0x0F) << 8) | data[1]
    if angle_raw & 0x0800:
        angle_raw -= 0x1000

    angle = angle_raw * 1.5

    # -------------------------
    # FRACTION
    # -------------------------
    frac = (data[4] & 0xF0) >> 4
    if frac & 0x08:
        frac -= 0x10

    angle += frac * 0.1

    # -------------------------
    # KALMAN FILTER (ANGLE)
    # -------------------------
    smooth_angle = kalman.update(angle)

    # -------------------------
    # TIME BASE
    # -------------------------
    now = time.perf_counter()
    dt = now - last_time if last_time != 0 else 0.01
    last_time = now

    # -------------------------
    # STORE HISTORY
    # -------------------------
    history.append((now, smooth_angle))

    # -------------------------
    # WINDOWED VELOCITY
    # -------------------------
    if len(history) > 6:
        t0, a0 = history[0]
        t1, a1 = history[-1]
        dtw = t1 - t0

        if dtw > 0:
            raw_rate = (a1 - a0) / dtw
        else:
            raw_rate = 0.0
    else:
        raw_rate = 0.0

    # -------------------------
    # DEADZONE FILTER
    # -------------------------
    if abs(raw_rate) < 0.5:
        raw_rate = 0.0

    # -------------------------
    # SMOOTH RATE
    # -------------------------
    rate_filtered = 0.85 * rate_filtered + 0.15 * raw_rate

    return smooth_angle, rate_filtered

# =========================
# SERIAL THREAD
# =========================
def read_serial():
    global angle_filtered, rate_filtered, ser, running

    while running:
        try:
            line = ser.readline().decode(errors='ignore').strip()

            if not line.startswith("FRAME"):
                continue

            log_box.insert(tk.END, line + "\n")
            log_box.see(tk.END)

            match = re.search(r"ID:0x([0-9A-Fa-f]+).*DATA:(.*)", line)
            if not match:
                continue

            can_id = int(match.group(1), 16)
            data = [int(x, 16) for x in match.group(2).split()]

            if can_id == 0x25 and len(data) >= 6:
                a, r = decode_steering(data)
                angle_filtered = a
                rate_filtered = r

        except:
            continue

# =========================
# GUI UPDATE
# =========================
def update_gui():
    ax.clear()
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)

    # circle
    ax.add_patch(plt.Circle((0, 0), 0.9, fill=False, linewidth=2))

    # needle
    try:
        theta = math.radians(180 - angle_filtered)
        x = 0.8 * math.cos(theta)
        y = 0.8 * math.sin(theta)
        ax.plot([0, x], [0, y], linewidth=3)
    except:
        pass

    # text
    ax.text(-0.95, 0.90, f"Angle: {angle_filtered:.2f}°", fontsize=12)
    ax.text(-0.95, 0.75, f"Rate: {rate_filtered:.2f} °/s", fontsize=12)

    canvas.draw()
    root.after(20, update_gui)

# =========================
# START SERIAL
# =========================
def start():
    global ser

    port = find_esp32()
    if not port:
        log_box.insert(tk.END, "ESP32 NOT FOUND\n")
        return

    ser = serial.Serial(port, 115200, timeout=1)
    log_box.insert(tk.END, f"Connected: {port}\n")

    t = threading.Thread(target=read_serial, daemon=True)
    t.start()

# =========================
# STOP
# =========================
def stop():
    global running
    running = False
    if ser:
        ser.close()
    root.destroy()

# =========================
# UI
# =========================
root = tk.Tk()
root.title("Automotive Steering Estimator FINAL")
root.geometry("1000x600")

left = tk.Frame(root)
left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

right = tk.Frame(root)
right.pack(side=tk.RIGHT, fill=tk.BOTH)

log_box = tk.Text(left, height=30)
log_box.pack(fill=tk.BOTH, expand=True)

fig, ax = plt.subplots(figsize=(4,4))
canvas = FigureCanvasTkAgg(fig, master=right)
canvas.get_tk_widget().pack()

ttk.Button(left, text="START", command=start).pack()
ttk.Button(left, text="STOP", command=stop).pack()

update_gui()
root.mainloop()import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import math
import re
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# =========================
# GLOBAL STATE
# =========================
angle = 0.0
rate = 0.0
running = True
ser = None

# =========================
# AUTO DETECT ESP32
# =========================
def find_esp32():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if "USB" in p.description or "UART" in p.description or "CP210" in p.description:
            return p.device
    return None

# =========================
# DECODER (BASED ON YOUR C++)
# =========================
def decode_steering(data):
    try:
        # ===== STEER ANGLE (12-bit signed) =====
        steerAngle = ((data[0] & 0x0F) << 8) | data[1]
        if steerAngle & 0x0800:
            steerAngle -= 0x1000
        steerAngle = steerAngle * 1.5

        # ===== STEER FRACTION (4-bit signed) =====
        frac = (data[4] & 0xF0) >> 4
        if frac & 0x08:
            frac -= 0x10
        frac = frac * 0.1   # approx scaling

        # ===== STEER RATE (12-bit signed) =====
        rate_raw = ((data[4] & 0x0F) << 8) | data[5]
        if rate_raw & 0x0800:
            rate_raw -= 0x1000
        rate_raw = rate_raw * 1

        total_angle = steerAngle + frac

        return total_angle, rate_raw

    except:
        return None, None

# =========================
# SERIAL THREAD
# =========================
def read_serial():
    global angle, rate, ser, running

    while running:
        try:
            line = ser.readline().decode(errors='ignore').strip()

            if not line.startswith("FRAME"):
                continue

            log_box.insert(tk.END, line + "\n")
            log_box.see(tk.END)

            match = re.search(r"ID:0x([0-9A-Fa-f]+).*DATA:(.*)", line)
            if not match:
                continue

            can_id = int(match.group(1), 16)
            data = [int(x, 16) for x in match.group(2).split()]

            if can_id == 0x25 and len(data) >= 6:
                a, r = decode_steering(data)
                if a is not None:
                    angle = a
                    rate = r

        except:
            continue

# =========================
# GAUGE UPDATE
# =========================
def update_gauge():
    ax.clear()
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)

    # circle
    circle = plt.Circle((0, 0), 0.9, fill=False, linewidth=2)
    ax.add_patch(circle)

    # needle (angle)
    try:
        theta = math.radians(180 - angle)
        x = 0.8 * math.cos(theta)
        y = 0.8 * math.sin(theta)
        ax.plot([0, x], [0, y], linewidth=3)
    except:
        pass

    ax.text(-0.9, 0.9, f"Angle: {angle:.2f}°", fontsize=12)
    ax.text(-0.9, 0.75, f"Rate: {rate:.2f} °/s", fontsize=12)

    canvas.draw()
    root.after(50, update_gauge)

# =========================
# START SERIAL
# =========================
def start_serial():
    global ser

    port = find_esp32()
    if not port:
        log_box.insert(tk.END, "ESP32 NOT FOUND\n")
        return

    ser = serial.Serial(port, 115200, timeout=1)
    log_box.insert(tk.END, f"Connected: {port}\n")

    t = threading.Thread(target=read_serial, daemon=True)
    t.start()

# =========================
# STOP
# =========================
def stop_app():
    global running
    running = False
    if ser:
        ser.close()
    root.destroy()

# =========================
# UI
# =========================
root = tk.Tk()
root.title("CAN Steering Dashboard (Angle + Rate)")
root.geometry("1000x600")

left = tk.Frame(root)
left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

right = tk.Frame(root)
right.pack(side=tk.RIGHT, fill=tk.BOTH)

log_box = tk.Text(left)
log_box.pack(fill=tk.BOTH, expand=True)

fig, ax = plt.subplots(figsize=(4,4))
canvas = FigureCanvasTkAgg(fig, master=right)
canvas.get_tk_widget().pack()

ttk.Button(left, text="START", command=start_serial).pack()
ttk.Button(left, text="STOP", command=stop_app).pack()

update_gauge()
root.mainloop()

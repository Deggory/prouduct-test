import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import time
import math
import re
from collections import deque

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# =========================================================
# CONFIG
# =========================================================
SERIAL_BAUD = 115200
UPDATE_MS = 20

TARGET_CAN_ID = 0x25

# Steering limits for display
MAX_STEER_ANGLE = 540.0

# Filtering
RATE_DEADBAND = 0.5
EMA_RATE_ALPHA = 0.15

# =========================================================
# GLOBAL STATE
# =========================================================
running = True
ser = None

angle_filtered = 0.0
rate_filtered = 0.0

packet_count = 0
last_rx = time.time()

mcp_status = "?"
can_status = "NO SIGNAL"
last_can_id = "NONE"

history = deque(maxlen=12)

# =========================================================
# THREAD SAFE UI DATA
# =========================================================
latest_line = ""

# =========================================================
# AUTO DETECT ESP32
# =========================================================
def find_esp32():
    ports = serial.tools.list_ports.comports()

    for p in ports:
        desc = (p.description or "").lower()
        dev = (p.device or "").lower()

        if (
            "cp210" in desc
            or "ch340" in desc
            or "usb" in desc
            or "uart" in desc
            or "ttyusb" in dev
            or "ttyacm" in dev
        ):
            return p.device

    return None

# =========================================================
# SIMPLE KALMAN FILTER
# =========================================================
class Kalman1D:
    def __init__(self):
        self.x = 0.0
        self.p = 1.0
        self.q = 0.05
        self.r = 5.0

    def update(self, z):
        self.p += self.q

        k = self.p / (self.p + self.r)

        self.x += k * (z - self.x)

        self.p *= (1.0 - k)

        return self.x

kalman = Kalman1D()

# =========================================================
# DECODE STEERING
# =========================================================
def decode_steering(data):
    global rate_filtered

    # =====================================================
    # ANGLE (12-bit signed)
    # =====================================================
    angle_raw = ((data[0] & 0x0F) << 8) | data[1]

    if angle_raw & 0x0800:
        angle_raw -= 0x1000

    angle = angle_raw * 1.5

    # =====================================================
    # FRACTION
    # =====================================================
    frac = (data[4] & 0xF0) >> 4

    if frac & 0x08:
        frac -= 0x10

    angle += frac * 0.1

    # =====================================================
    # KALMAN FILTER
    # =====================================================
    smooth_angle = kalman.update(angle)

    # =====================================================
    # HISTORY BUFFER
    # =====================================================
    now = time.perf_counter()

    history.append((now, smooth_angle))

    # =====================================================
    # WINDOWED RATE
    # =====================================================
    if len(history) > 6:
        t0, a0 = history[0]
        t1, a1 = history[-1]

        dt = t1 - t0

        if dt > 0:
            raw_rate = (a1 - a0) / dt
        else:
            raw_rate = 0.0
    else:
        raw_rate = 0.0

    # =====================================================
    # DEADZONE
    # =====================================================
    if abs(raw_rate) < RATE_DEADBAND:
        raw_rate = 0.0

    # =====================================================
    # EMA FILTER
    # =====================================================
    rate_filtered = (
        (1.0 - EMA_RATE_ALPHA) * rate_filtered
        + EMA_RATE_ALPHA * raw_rate
    )

    return smooth_angle, rate_filtered

# =========================================================
# SERIAL THREAD
# =========================================================
def serial_thread():
    global ser
    global running
    global latest_line
    global angle_filtered
    global rate_filtered
    global packet_count
    global last_rx
    global mcp_status
    global can_status
    global last_can_id

    while running:

        # =================================================
        # AUTO CONNECT
        # =================================================
        if ser is None:

            try:
                port = find_esp32()

                if port:
                    ser = serial.Serial(
                        port,
                        SERIAL_BAUD,
                        timeout=1
                    )

                    append_log(f"[CONNECTED] {port}")

                else:
                    append_log("[WAITING] ESP32 NOT FOUND")
                    time.sleep(2)
                    continue

            except Exception as e:
                append_log(f"[SERIAL ERROR] {e}")
                time.sleep(2)
                continue

        # =================================================
        # READ SERIAL
        # =================================================
        try:

            line = ser.readline().decode(
                errors="ignore"
            ).strip()

            if not line:
                continue

            latest_line = line

            # =================================================
            # LOG
            # =================================================
            root.after(
                0,
                lambda l=line: append_log(l)
            )

            # =================================================
            # MCP STATUS
            # =================================================
            if "MCP" in line and "OK" in line:
                mcp_status = "OK"

            if "FAIL" in line:
                mcp_status = "FAIL"

            # =================================================
            # CAN STATUS
            # =================================================
            if "TIMEOUT" in line:
                can_status = "NO SIGNAL"

            if "FOUND" in line or "DETECTED" in line:
                can_status = "OK"

            # =================================================
            # PARSE FRAME
            # =================================================
            match = re.search(
                r"ID:0x([0-9A-Fa-f]+).*DATA:(.*)",
                line
            )

            if not match:
                continue

            can_id = int(match.group(1), 16)

            last_can_id = f"0x{can_id:X}"

            data = [
                int(x, 16)
                for x in match.group(2).split()
            ]

            # =================================================
            # TARGET ID
            # =================================================
            if can_id == TARGET_CAN_ID and len(data) >= 6:

                angle_filtered, rate_filtered = decode_steering(data)

                packet_count += 1
                last_rx = time.time()

        except Exception:
            try:
                ser.close()
            except:
                pass

            ser = None
            time.sleep(1)

# =========================================================
# LOG BOX
# =========================================================
def append_log(text):

    log_box.insert(tk.END, text + "\n")
    log_box.see(tk.END)

    # limit log size
    if int(log_box.index('end-1c').split('.')[0]) > 400:
        log_box.delete("1.0", "100.0")

# =========================================================
# GUI UPDATE
# =========================================================
def update_gui():

    # =====================================================
    # UPDATE TEXT LABELS
    # =====================================================
    angle_label.config(
        text=f"ANGLE : {angle_filtered:.2f}°"
    )

    rate_label.config(
        text=f"RATE  : {rate_filtered:.2f} °/s"
    )

    packet_label.config(
        text=f"PACKETS : {packet_count}"
    )

    health_label.config(
        text=f"MCP:{mcp_status}  CAN:{can_status}  ID:{last_can_id}"
    )

    # =====================================================
    # NO SIGNAL
    # =====================================================
    no_signal = (time.time() - last_rx) > 1.0

    # =====================================================
    # PLOT
    # =====================================================
    ax.clear()

    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)

    ax.set_xticks([])
    ax.set_yticks([])

    # circle
    circle = plt.Circle(
        (0, 0),
        0.9,
        fill=False,
        linewidth=2
    )

    ax.add_patch(circle)

    # center line
    ax.plot([0, 0], [-0.9, 0.9], linestyle="--")

    # =====================================================
    # NEEDLE
    # =====================================================
    limited = max(
        -MAX_STEER_ANGLE,
        min(MAX_STEER_ANGLE, angle_filtered)
    )

    theta = math.radians(
        (limited / 3.0) - 90
    )

    x = 0.8 * math.cos(theta)
    y = 0.8 * math.sin(theta)

    ax.plot(
        [0, x],
        [0, y],
        linewidth=3
    )

    # =====================================================
    # SIGNAL WARNING
    # =====================================================
    if no_signal:
        ax.text(
            0,
            -0.75,
            "NO SIGNAL",
            ha="center",
            fontsize=16
        )

    canvas.draw()

    root.after(
        UPDATE_MS,
        update_gui
    )

# =========================================================
# START
# =========================================================
def start_serial():

    thread = threading.Thread(
        target=serial_thread,
        daemon=True
    )

    thread.start()

# =========================================================
# STOP
# =========================================================
def stop_app():

    global running

    running = False

    try:
        if ser:
            ser.close()
    except:
        pass

    root.destroy()

# =========================================================
# GUI
# =========================================================
root = tk.Tk()

root.title("ESP32 Automotive Steering Dashboard")
root.geometry("1100x650")

# =========================================================
# LEFT PANEL
# =========================================================
left = tk.Frame(root)
left.pack(
    side=tk.LEFT,
    fill=tk.BOTH,
    expand=True
)

# =========================================================
# RIGHT PANEL
# =========================================================
right = tk.Frame(root)
right.pack(
    side=tk.RIGHT,
    fill=tk.BOTH
)

# =========================================================
# LOG BOX
# =========================================================
log_box = tk.Text(
    left,
    height=35
)

log_box.pack(
    fill=tk.BOTH,
    expand=True
)

# =========================================================
# BUTTONS
# =========================================================
button_frame = tk.Frame(left)
button_frame.pack(fill=tk.X)

ttk.Button(
    button_frame,
    text="START",
    command=start_serial
).pack(side=tk.LEFT, padx=5, pady=5)

ttk.Button(
    button_frame,
    text="STOP",
    command=stop_app
).pack(side=tk.LEFT, padx=5, pady=5)

# =========================================================
# LABELS
# =========================================================
angle_label = tk.Label(
    right,
    text="ANGLE : 0.00°",
    font=("Arial", 16)
)

angle_label.pack()

rate_label = tk.Label(
    right,
    text="RATE : 0.00 °/s",
    font=("Arial", 16)
)

rate_label.pack()

packet_label = tk.Label(
    right,
    text="PACKETS : 0",
    font=("Arial", 14)
)

packet_label.pack()

health_label = tk.Label(
    right,
    text="MCP:? CAN:? ID:?",
    font=("Arial", 12)
)

health_label.pack()

# =========================================================
# MATPLOTLIB FIGURE
# =========================================================
fig, ax = plt.subplots(figsize=(5, 5))

canvas = FigureCanvasTkAgg(
    fig,
    master=right
)

canvas.get_tk_widget().pack()

# =========================================================
# START
# =========================================================
start_serial()

update_gui()

root.protocol(
    "WM_DELETE_WINDOW",
    stop_app
)

root.mainloop()

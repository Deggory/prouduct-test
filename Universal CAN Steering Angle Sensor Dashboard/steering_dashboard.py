import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import math
import re
import time

# =========================================================
# GLOBAL STATE
# =========================================================
angle_value = 0.0
min_angle = 9999
max_angle = -9999
packet_count = 0
last_packet_time = time.time()

mcp_status = "UNKNOWN"
can_status = "NO CAN"
detected_id = "NONE"
last_sniff = ""

ser = None


# =========================================================
# AUTO PORT DETECTION
# =========================================================
def auto_detect_port():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if "USB" in p.description or "CP210" in p.description or "CH340" in p.description:
            return p.device
    return None


# =========================================================
# SERIAL THREAD
# =========================================================
def serial_reader():
    global angle_value, min_angle, max_angle
    global packet_count, last_packet_time
    global mcp_status, can_status, detected_id, last_sniff

    port = auto_detect_port()
    if not port:
        status_label.config(text="ESP32 NOT FOUND")
        return

    status_label.config(text=f"PORT: {port}")

    try:
        s = serial.Serial(port, 115200, timeout=1)
    except Exception as e:
        status_label.config(text=f"SERIAL ERROR: {e}")
        return

    while True:
        try:
            line = s.readline().decode(errors="ignore").strip()
            if not line:
                continue

            last_sniff = line
            sniff_label.config(text=line[:90])

            # MCP/CAN status parse
            if "MCP:OK" in line:
                mcp_status = "OK"
            elif "MCP:FAIL" in line:
                mcp_status = "FAIL"

            if "CAN:OK" in line:
                can_status = "OK"
            elif "CAN:FAIL" in line:
                can_status = "NO CAN"

            # sniff CAN ID
            match_id = re.search(r"SNIFF ID:0x([0-9A-Fa-f]+)", line)
            if match_id:
                detected_id = "0x" + match_id.group(1)

            # angle parse
            match = re.search(r"ANGLE:([-0-9.]+)", line)
            if match:
                angle_value = float(match.group(1))
                packet_count += 1
                last_packet_time = time.time()

                min_angle = min(min_angle, angle_value)
                max_angle = max(max_angle, angle_value)

        except:
            pass


# =========================================================
# GAUGE DRAWING
# =========================================================
def update_gauge():
    canvas.delete("all")

    cx, cy = 200, 200
    radius = 150

    # outer circle
    canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius, width=3)

    # zero center line
    canvas.create_line(cx, cy-radius, cx, cy+radius, dash=(4, 2))

    # needle
    angle = max(-540, min(540, angle_value))
    needle_deg = angle / 3.0
    rad = math.radians(needle_deg - 90)

    x = cx + radius * 0.8 * math.cos(rad)
    y = cy + radius * 0.8 * math.sin(rad)

    canvas.create_line(cx, cy, x, y, width=4)

    # center point
    canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="black")

    # labels
    angle_label.config(text=f"{angle_value:7.1f}°")
    minmax_label.config(text=f"MIN {min_angle:.1f}°   MAX {max_angle:.1f}°")
    packet_label.config(text=f"PACKETS: {packet_count}")
    health_label.config(
        text=f"MCP:{mcp_status}   CAN:{can_status}   ID:{detected_id}"
    )

    # NO CAN warning
    if time.time() - last_packet_time > 1.0:
        canvas.create_text(200, 350, text="NO CAN", font=("Arial", 20))

    root.after(50, update_gauge)


# =========================================================
# GUI
# =========================================================
root = tk.Tk()
root.title("Universal Steering CAN Dashboard")
root.geometry("420x520")

canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()

angle_label = tk.Label(root, text="0.0°", font=("Arial", 24))
angle_label.pack()

minmax_label = tk.Label(root, text="MIN/MAX")
minmax_label.pack()

packet_label = tk.Label(root, text="PACKETS: 0")
packet_label.pack()

health_label = tk.Label(root, text="MCP:? CAN:? ID:?")
health_label.pack()

sniff_label = tk.Label(root, text="", wraplength=380)
sniff_label.pack()

status_label = tk.Label(root, text="Starting...")
status_label.pack()

# start serial thread
threading.Thread(target=serial_reader, daemon=True).start()

update_gauge()
root.mainloop()

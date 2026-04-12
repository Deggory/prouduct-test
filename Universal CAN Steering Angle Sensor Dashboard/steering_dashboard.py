import tkinter as tk
import serial
import serial.tools.list_ports
import threading
import math
import re
import time


# =========================
# STATE VARIABLES
# =========================
angle = 0.0
min_angle = 9999
max_angle = -9999
packet_count = 0
last_rx = time.time()

mcp = "?"
can = "NO CAN"
can_id = "NONE"


# =========================
# FIND ESP32 PORT
# =========================
def find_port():
    ports = serial.tools.list_ports.comports()

    for p in ports:
        d = (p.description or "").lower()
        dev = (p.device or "").lower()

        if "cp210" in d or "ch340" in d or "usb" in d or "ttyusb" in dev or "ttyacm" in dev:
            return p.device

    return None


# =========================
# SERIAL THREAD
# =========================
def reader():
    global angle, min_angle, max_angle
    global packet_count, last_rx
    global mcp, can, can_id

    port = find_port()

    if not port:
        status.config(text="ESP32 NOT FOUND")
        return

    status.config(text=f"PORT: {port}")

    try:
        s = serial.Serial(port, 115200, timeout=1)
    except Exception as e:
        status.config(text=f"SERIAL ERROR: {e}")
        return

    while True:
        try:
            line = s.readline().decode(errors="ignore").strip()
            if not line:
                continue

            sniff.config(text=line[:100])

            # MCP status
            if "MCP:OK" in line:
                mcp = "OK"
            if "MCP:FAIL" in line:
                mcp = "FAIL"

            # CAN status
            if "CAN:OK" in line:
                can = "OK"
            if "CAN:FAIL" in line:
                can = "NO CAN"

            # CAN ID detect
            m = re.search(r"SNIFF ID:0x([0-9A-Fa-f]+)", line)
            if m:
                can_id = "0x" + m.group(1)

            # ANGLE detect
            a = re.search(r"ANGLE:([-0-9.]+)", line)
            if a:
                angle = float(a.group(1))
                packet_count += 1
                last_rx = time.time()

                min_angle = min(min_angle, angle)
                max_angle = max(max_angle, angle)

        except:
            pass


# =========================
# GAUGE DRAWING
# =========================
def draw():
    canvas.delete("all")

    cx, cy = 200, 200
    r = 150

    # circle
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, width=3)

    # center line
    canvas.create_line(cx, cy-r, cx, cy+r, dash=(4, 2))

    # needle
    limited = max(-540, min(540, angle))
    rad = math.radians((limited / 3.0) - 90)

    x = cx + r * 0.8 * math.cos(rad)
    y = cy + r * 0.8 * math.sin(rad)

    canvas.create_line(cx, cy, x, y, width=4)
    canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="black")

    # labels
    angle_lbl.config(text=f"{angle:.1f}°")
    minmax.config(text=f"MIN {min_angle:.1f}  MAX {max_angle:.1f}")
    packets.config(text=f"PACKETS {packet_count}")
    health.config(text=f"MCP:{mcp} CAN:{can} ID:{can_id}")

    # NO CAN warning
    if time.time() - last_rx > 1.0:
        canvas.create_text(200, 350, text="NO CAN", font=("Arial", 18))

    root.after(50, draw)


# =========================
# GUI SETUP
# =========================
root = tk.Tk()
root.title("Steering CAN Dashboard")
root.geometry("420x560")

canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()

angle_lbl = tk.Label(root, text="0.0°", font=("Arial", 22))
angle_lbl.pack()

minmax = tk.Label(root, text="MIN/MAX")
minmax.pack()

packets = tk.Label(root, text="PACKETS 0")
packets.pack()

health = tk.Label(root, text="MCP:? CAN:? ID:?")
health.pack()

sniff = tk.Label(root, text="", wraplength=380)
sniff.pack()

status = tk.Label(root, text="Starting...")
status.pack()


# =========================
# START THREAD + LOOP
# =========================
threading.Thread(target=reader, daemon=True).start()

draw()
root.mainloop()

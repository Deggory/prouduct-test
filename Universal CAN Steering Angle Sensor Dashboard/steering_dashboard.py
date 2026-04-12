import tkinter as tk
import serial
import serial.tools.list_ports
import threading
import math
import re
import time

# =========================
# GLOBAL STATE
# =========================
angle = 0.0
min_angle = 0.0
max_angle = 0.0
first_sample = True

packet_count = 0
last_rx = time.time()

mcp = "?"
can = "NO SIGNAL"
can_id = "NONE"


# =========================
# FIND ESP32 PORT
# =========================
def find_port():
    ports = serial.tools.list_ports.comports()

    for p in ports:
        d = (p.description or "").lower()
        dev = (p.device or "").lower()

        if "cp210" in d or "ch340" in d or "silicon" in d or "usb" in dev:
            return p.device

    return None


# =========================
# SERIAL READER THREAD
# =========================
def reader():
    global angle, min_angle, max_angle, first_sample
    global packet_count, last_rx
    global mcp, can, can_id

    port = find_port()

    if not port:
        root.after(0, lambda: status.config(text="ESP32 NOT FOUND"))
        return

    root.after(0, lambda: status.config(text=f"PORT: {port}"))

    try:
        s = serial.Serial(port, 115200, timeout=1)
    except Exception as e:
        root.after(0, lambda: status.config(text=f"SERIAL ERROR: {e}"))
        return

    while True:
        try:
            line = s.readline().decode(errors="ignore").strip()
            if not line:
                continue

            root.after(0, lambda l=line: sniff.config(text=l[:120]))

            # ================= MCP STATUS =================
            if "MCP:FAIL" in line:
                mcp = "FAIL"
            elif "MCP:OK" in line:
                mcp = "OK"

            # ================= CAN STATUS =================
            if "CAN:TIMEOUT" in line:
                can = "NO SIGNAL"
            elif "CAN:OK" in line:
                can = "OK"
            elif "NO CAN" in line:
                can = "NO BUS"

            # ================= CAN ID =================
            m = re.search(r"ID:0x([0-9A-Fa-f]+)", line)
            if m:
                can_id = "0x" + m.group(1)

            # ================= ANGLE =================
            a = re.search(r"ANGLE:([-0-9.]+)", line)
            if a:
                angle = float(a.group(1))

                packet_count += 1
                last_rx = time.time()

                if first_sample:
                    min_angle = angle
                    max_angle = angle
                    first_sample = False
                else:
                    min_angle = min(min_angle, angle)
                    max_angle = max(max_angle, angle)

        except:
            pass


# =========================
# GAUGE DRAW
# =========================
def draw():
    canvas.delete("all")

    cx, cy = 200, 220
    r = 160

    # outer circle
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, width=3)

    # center zero line
    canvas.create_line(cx, cy-r, cx, cy+r, dash=(4, 2), fill="gray")

    # clamp angle
    limited = max(-540, min(540, angle))

    # steering mapping (realistic)
    scaled = (limited / 540.0) * 180.0
    rad = math.radians(scaled - 90)

    x = cx + r * 0.85 * math.cos(rad)
    y = cy + r * 0.85 * math.sin(rad)

    # needle
    canvas.create_line(cx, cy, x, y, width=4, fill="red")
    canvas.create_oval(cx-6, cy-6, cx+6, cy+6, fill="black")

    # labels
    angle_lbl.config(text=f"{angle:.2f}°")
    minmax.config(text=f"MIN {min_angle:.2f}  MAX {max_angle:.2f}")
    packets.config(text=f"PACKETS {packet_count}")
    health.config(text=f"MCP:{mcp}  CAN:{can}  ID:{can_id}")

    # NO SIGNAL WARNING
    if time.time() - last_rx > 1.0:
        canvas.create_text(200, 400, text="NO SIGNAL", font=("Arial", 20), fill="red")

    root.after(50, draw)


# =========================
# GUI SETUP
# =========================
root = tk.Tk()
root.title("ESP32 Steering CAN Dashboard")
root.geometry("420x600")

canvas = tk.Canvas(root, width=400, height=420)
canvas.pack()

angle_lbl = tk.Label(root, text="0.00°", font=("Arial", 20))
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
# START THREAD
# =========================
threading.Thread(target=reader, daemon=True).start()
draw()
root.mainloop()import tkinter as tk
import serial
import serial.tools.list_ports
import threading
import math
import re
import time

# =========================
# STATE
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
# SERIAL READER THREAD
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

            # ================= MCP STATUS =================
            if "MCP INIT OK" in line:
                mcp = "OK"
            if "MCP INIT FAIL" in line:
                mcp = "FAIL"

            # ================= CAN STATUS =================
            if "CAN:NO CAN DETECTED" in line:
                can = "NO BUS"
            elif "CAN:TIMEOUT" in line:
                can = "NO SIGNAL"
            elif "CAN DETECTED" in line:
                can = "OK"

            # ================= CAN ID =================
            m = re.search(r"ID:0x([0-9A-Fa-f]+)", line)
            if m:
                can_id = "0x" + m.group(1)

            # ================= ANGLE =================
            a = re.search(r"ANG:([-0-9.]+)", line)
            if a:
                angle = float(a.group(1))

                packet_count += 1
                last_rx = time.time()

                min_angle = min(min_angle, angle)
                max_angle = max(max_angle, angle)

        except:
            pass


# =========================
# DRAW GAUGE
# =========================
def draw():
    canvas.delete("all")

    cx, cy = 200, 200
    r = 150

    # outer circle
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

    # NO SIGNAL WARNING
    if time.time() - last_rx > 1.0:
        canvas.create_text(200, 350, text="NO SIGNAL", font=("Arial", 18), fill="red")

    root.after(50, draw)


# =========================
# GUI SETUP
# =========================
root = tk.Tk()
root.title("Steering CAN Dashboard (FINAL)")
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
# START THREAD
# =========================
threading.Thread(target=reader, daemon=True).start()

draw()
root.mainloop()

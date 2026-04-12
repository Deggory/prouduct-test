import tkinter as tk
import serial
import serial.tools.list_ports
import threading
import math
import re
import time

# =========================
# STATE
# =========================
packet_count = 0
last_rx = time.time()

can_id = "NONE"
last_frame = ""

angle = 0.0


# =========================
# FIND ESP32 PORT
# =========================
def find_port():
    ports = serial.tools.list_ports.comports()

    for p in ports:
        d = (p.description or "").lower()
        dev = (p.device or "").lower()

        if "cp210" in d or "ch340" in d or "usb" in dev or "ttyusb" in dev or "ttyacm" in dev:
            return p.device

    return None


# =========================
# SERIAL THREAD
# =========================
def reader():
    global packet_count, last_rx, can_id, last_frame, angle

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

            last_frame = line
            sniff.config(text=line[:120])

            # ================= FRAME DETECT =================
            if "FRAME" in line:

                packet_count += 1
                last_rx = time.time()

                # ================= CAN ID =================
                m = re.search(r"ID:0x([0-9A-Fa-f]+)", line)
                if m:
                    can_id = "0x" + m.group(1)

                # ================= OPTIONAL: ANGLE FROM DATA =================
                # Example: use first byte as steering proxy
                d = re.search(r"DATA:\s*([0-9A-Fa-f ]+)", line)
                if d:
                    try:
                        bytes_str = d.group(1).strip().split()
                        if len(bytes_str) > 0:
                            angle = int(bytes_str[0], 16)  # simple mapping
                    except:
                        pass

        except:
            pass


# =========================
# DRAW GAUGE
# =========================
def draw():
    canvas.delete("all")

    cx, cy = 200, 200
    r = 150

    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, width=3)
    canvas.create_line(cx, cy-r, cx, cy+r, dash=(4, 2))

    # clamp
    limited = max(-540, min(540, angle))

    rad = math.radians((limited / 3.0) - 90)

    x = cx + r * 0.8 * math.cos(rad)
    y = cy + r * 0.8 * math.sin(rad)

    canvas.create_line(cx, cy, x, y, width=4, fill="red")
    canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="black")

    # labels
    angle_lbl.config(text=f"{angle:.1f}")
    packets.config(text=f"PACKETS {packet_count}")
    health.config(text=f"CAN ID: {can_id}")

    # NO SIGNAL
    if time.time() - last_rx > 1.0:
        canvas.create_text(200, 350, text="NO SIGNAL", fill="red", font=("Arial", 18))

    root.after(50, draw)


# =========================
# GUI
# =========================
root = tk.Tk()
root.title("CAN Dashboard (FIXED FOR YOUR FIRMWARE)")
root.geometry("420x560")

canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()

angle_lbl = tk.Label(root, text="0", font=("Arial", 22))
angle_lbl.pack()

packets = tk.Label(root, text="PACKETS 0")
packets.pack()

health = tk.Label(root, text="CAN ID: NONE")
health.pack()

sniff = tk.Label(root, text="", wraplength=380)
sniff.pack()

status = tk.Label(root, text="Starting...")
status.pack()


threading.Thread(target=reader, daemon=True).start()
draw()
root.mainloop()

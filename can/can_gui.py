import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import time

# ================= GLOBAL =================
running = True
ser = None

# ================= AUTO DETECT ESP32 =================
def find_esp32_port():
    keywords = ["CP210", "CH340", "USB Serial", "UART", "ttyUSB", "ttyACM"]

    ports = serial.tools.list_ports.comports()
    for p in ports:
        info = f"{p.device} {p.description}"
        if any(k in info for k in keywords):
            return p.device
    return None

# ================= SERIAL READER =================
def read_serial():
    global ser, running

    while running:
        if ser and ser.in_waiting:
            try:
                line = ser.readline().decode(errors="ignore").strip()

                if "," in line:
                    parts = line.split(",")

                    if len(parts) == 4:
                        frame, cid, dlc, data = parts

                        tree.insert("", 0, values=(frame, cid, dlc, data))

                        if len(tree.get_children()) > 200:
                            tree.delete(tree.get_children()[-1])

            except:
                pass

# ================= CONNECT =================
def connect():
    global ser

    port = find_esp32_port()

    if not port:
        status.set("ESP32 NOT FOUND")
        return

    try:
        ser = serial.Serial(port, 115200, timeout=1)
        status.set(f"CONNECTED: {port}")

    except Exception as e:
        status.set(f"FAILED: {e}")

# ================= GUI =================
root = tk.Tk()
root.title("ESP32 CAN SNIFFER PRO")
root.geometry("800x500")

status = tk.StringVar()
status.set("Searching ESP32...")

label = tk.Label(root, textvariable=status)
label.pack()

cols = ("Frame", "ID", "DLC", "Data")
tree = ttk.Treeview(root, columns=cols, show="headings")

for c in cols:
    tree.heading(c, text=c)
    tree.column(c, width=180)

tree.pack(expand=True, fill="both")

btn = tk.Button(root, text="Connect", command=connect)
btn.pack()

# ================= THREAD =================
t = threading.Thread(target=read_serial, daemon=True)
t.start()

root.mainloop()

running = False
if ser:
    ser.close()

import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import time

# ================= STATE =================
ser = None
running = True
freeze = False
selected_id = None

# ================= AUTO DETECT ESP32 =================
def find_esp32():
    keywords = ["CP210", "CH340", "USB Serial", "UART", "ttyUSB", "ttyACM"]

    ports = serial.tools.list_ports.comports()

    for p in ports:
        text = f"{p.device} {p.description}"
        if any(k in text for k in keywords):
            return p.device
    return None

# ================= CONNECT =================
def connect():
    global ser

    port = find_esp32()

    if not port:
        status.set("ESP32 NOT FOUND")
        return

    try:
        ser = serial.Serial(port, 115200, timeout=1)
        status.set(f"CONNECTED: {port}")

    except Exception as e:
        status.set(f"ERROR: {e}")

# ================= GUI UPDATE =================
def update_gui(frame, cid, dlc, data):

    global freeze, selected_id

    if freeze:
        if selected_id == cid:
            detail_box.insert("end", f"{frame} | {cid} | {dlc} | {data}\n")
        return

    tree.insert("", 0, values=(frame, cid, dlc, data))

    # limit rows
    if len(tree.get_children()) > 300:
        tree.delete(tree.get_children()[-1])

# ================= SERIAL THREAD =================
def reader():
    global ser, running

    while running:
        if ser and ser.in_waiting:
            try:
                line = ser.readline().decode(errors="ignore").strip()

                if line.count(",") == 3:
                    frame, cid, dlc, data = line.split(",")

                    update_gui(frame, cid, dlc, data)

            except:
                pass

# ================= FREEZE BUTTON =================
def toggle_freeze():
    global freeze
    freeze = not freeze

    if freeze:
        status.set("FROZEN (click frame ID to inspect)")
    else:
        status.set("LIVE MODE")

# ================= CLEAR DETAILS =================
def clear_detail():
    detail_box.delete("1.0", "end")

# ================= SELECT FRAME =================
def select_item(event):
    global selected_id

    item = tree.focus()
    if item:
        values = tree.item(item, "values")
        if values:
            selected_id = values[1]
            status.set(f"LOCKED ID: {selected_id}")

# ================= GUI =================
root = tk.Tk()
root.title("ESP32 CAN ANALYZER PRO")
root.geometry("950x600")

status = tk.StringVar()
status.set("Searching ESP32...")

tk.Label(root, textvariable=status).pack()

# ===== BUTTONS =====
btn_frame = tk.Frame(root)
btn_frame.pack()

tk.Button(btn_frame, text="Connect ESP32", command=connect).pack(side="left", padx=5)
tk.Button(btn_frame, text="Freeze / Unfreeze", command=toggle_freeze).pack(side="left", padx=5)
tk.Button(btn_frame, text="Clear Detail", command=clear_detail).pack(side="left", padx=5)

# ===== MAIN TABLE =====
cols = ("Frame", "ID", "DLC", "Data")
tree = ttk.Treeview(root, columns=cols, show="headings")

for c in cols:
    tree.heading(c, text=c)
    tree.column(c, width=200)

tree.pack(expand=True, fill="both")
tree.bind("<<TreeviewSelect>>", select_item)

# ===== DETAIL WINDOW =====
tk.Label(root, text="Frozen Frame View (selected ID)").pack()

detail_box = tk.Text(root, height=10)
detail_box.pack(fill="both")

# ===== THREAD =====
t = threading.Thread(target=reader, daemon=True)
t.start()

root.mainloop()
running = False
if ser:
    ser.close()import tkinter as tk
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

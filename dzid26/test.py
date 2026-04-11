#!/usr/bin/env python3
"""
Best-of-both StepperServoCAN tester
- Uses Python -> USB serial -> ESP32 -> CAN (SLCAN/LAWICEL text)
- Works from any launch directory
- DBC-based encoding
- Configurable CAN ID
- 100 Hz deterministic transmit loop
- Proper checksum + rolling counter
- Safe GUI shutdown
- Immediate live updates from GUI
"""

import os
import time
import threading
import serial
import tkinter as tk
from tkinter import messagebox
import cantools

# =============================
# CONFIG
# =============================
PORT = '/dev/ttyUSB0'   # Linux default
BAUD_RATE = 115200
TIMEOUT = 0.02
CAN_BITRATE_CMD = 'S6'  # 500 kbps in SLCAN
TX_PERIOD = 0.01        # 100 Hz

MIN_TORQUE = -16.0
MAX_TORQUE = 15.875
MIN_ANGLE = -4096
MAX_ANGLE = 4096

# =============================
# GLOBAL STATE
# =============================
can_enabled = True
counter = 0
message_id = 0x22E

torque = 0.0
angle = 0.0

tx_lock = threading.Lock()

# =============================
# DBC LOAD (works from any dir)
# =============================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DBC_PATH = os.path.join(CURRENT_DIR, 'opendbc', 'ocelot_controls.dbc')
db = cantools.database.load_file(DBC_PATH)
msg = db.get_message_by_name('STEERING_COMMAND')

# =============================
# HELPERS
# =============================
def msg_calc_checksum_8bit(data: bytes, length: int, msg_id: int) -> int:
    checksum = msg_id
    for i in range(length):
        checksum += data[i]
    checksum = (checksum & 0xFF) + (checksum >> 8)
    return checksum & 0xFF


def validate_float(value_str, min_value, max_value):
    try:
        value = float(value_str)
        if min_value <= value <= max_value:
            return value
    except ValueError:
        pass
    return None


def update_msg_id(event=None):
    global message_id
    try:
        s = msg_id_var.get().strip()
        message_id = int(s, 16) if s.lower().startswith('0x') else int(s)
    except ValueError:
        messagebox.showerror('Error', 'Invalid CAN ID')


def update_values(event=None):
    global torque, angle
    update_msg_id()

    new_torque = validate_float(torque_var.get(), MIN_TORQUE, MAX_TORQUE)
    new_angle = validate_float(angle_var.get(), MIN_ANGLE, MAX_ANGLE)

    if new_torque is None:
        messagebox.showerror('Error', f'Torque must be {MIN_TORQUE} to {MAX_TORQUE}')
        return
    if new_angle is None:
        messagebox.showerror('Error', f'Angle must be {MIN_ANGLE} to {MAX_ANGLE}')
        return

    with tx_lock:
        torque = new_torque
        angle = new_angle


def build_payload():
    global counter

    with tx_lock:
        local_torque = torque
        local_angle = angle
        local_mode = steer_mode_widget.get_value()
        local_id = message_id

    counter = (counter + 1) & 0xF

    raw = msg.encode({
        'STEER_TORQUE': local_torque,
        'STEER_ANGLE': local_angle,
        'STEER_MODE': local_mode,
        'COUNTER': counter,
        'CHECKSUM': 0,
    })

    checksum = msg_calc_checksum_8bit(raw, len(raw), local_id)

    return msg.encode({
        'STEER_TORQUE': local_torque,
        'STEER_ANGLE': local_angle,
        'STEER_MODE': local_mode,
        'COUNTER': counter,
        'CHECKSUM': checksum,
    })


def slcan_send_frame(ser, arb_id, data: bytes):
    dlc = len(data)
    hex_payload = ''.join(f'{b:02X}' for b in data)
    frame = f't{arb_id:03X}{dlc:X}{hex_payload}\r'
    ser.write(frame.encode('ascii'))


def serial_reader(ser):
    while can_enabled:
        try:
            if ser.in_waiting:
                line = ser.readline().decode(errors='ignore').strip()
                if line:
                    print(f'RX: {line}')
        except Exception as e:
            print('Serial RX error:', e)
            break


def send_loop(ser):
    global can_enabled

    ser.write((CAN_BITRATE_CMD + '\r').encode())
    time.sleep(0.05)
    ser.write(b'O\r')
    time.sleep(0.05)

    next_time = time.monotonic()
    loop_count = 0
    stat_time = time.monotonic()

    while can_enabled:
        payload = build_payload()  # FIXED: update before sending

        with tx_lock:
            arb_id = message_id

        slcan_send_frame(ser, arb_id, payload)

        loop_count += 1
        now = time.monotonic()
        if now - stat_time >= 1.0:
            print(f'TX frequency: {loop_count / (now - stat_time):.1f} Hz')
            loop_count = 0
            stat_time = now

        next_time += TX_PERIOD
        sleep_time = next_time - time.monotonic()
        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            next_time = time.monotonic()

    try:
        ser.write(b'C\r')
        ser.close()
    except Exception:
        pass


class SteerModeWidget:
    def __init__(self, master, label_text, options):
        self.var = tk.IntVar(value=0)
        tk.Label(master, text=label_text).grid(row=4, column=0, sticky='w')

        for idx, (value, text) in enumerate(options):
            tk.Radiobutton(
                master,
                text=text,
                variable=self.var,
                value=value,
                command=update_values,
            ).grid(row=4 + idx, column=1, sticky='w')

    def get_value(self):
        return self.var.get()


# =============================
# GUI
# =============================
window = tk.Tk()
window.title('StepperServoCAN Serial Tester')
window.geometry('420x300')

msg_id_var = tk.StringVar(value=hex(message_id))
torque_var = tk.StringVar(value='0')
angle_var = tk.StringVar(value='0')

# Row 0-3
tk.Label(window, text='Serial Port:').grid(row=0, column=0, sticky='w')
tk.Label(window, text=PORT).grid(row=0, column=1, sticky='w')

tk.Label(window, text='CAN ID:').grid(row=1, column=0, sticky='w')
tk.Entry(window, textvariable=msg_id_var).grid(row=1, column=1, sticky='w')

tk.Label(window, text='Torque:').grid(row=2, column=0, sticky='w')
tk.Entry(window, textvariable=torque_var).grid(row=2, column=1, sticky='w')

tk.Label(window, text='Angle:').grid(row=3, column=0, sticky='w')
tk.Entry(window, textvariable=angle_var).grid(row=3, column=1, sticky='w')

STEER_MODE_OPTIONS = [
    (0, 'Off - instant 0 torque'),
    (1, 'TorqueControl'),
    (2, 'AngleControl'),
    (3, 'SoftOff - ramp to 0'),
]

steer_mode_widget = SteerModeWidget(window, 'Steer Mode:', STEER_MODE_OPTIONS)

tk.Button(window, text='Update', command=update_values).grid(row=9, column=0, columnspan=2)


def on_closing():
    global can_enabled
    can_enabled = False
    window.destroy()


tk.Button(window, text='Quit', command=on_closing).grid(row=10, column=0, columnspan=2, sticky='nsew')
window.bind('<Return>', update_values)

# Keyboard steering control (acts like a joystick)
KEY_TORQUE_STEP = 6.0

def steer_left_press(event=None):
    torque_var.set(str(-KEY_TORQUE_STEP))
    steer_mode_widget.var.set(1)  # TorqueControl
    update_values()


def steer_right_press(event=None):
    torque_var.set(str(KEY_TORQUE_STEP))
    steer_mode_widget.var.set(1)  # TorqueControl
    update_values()


def steer_release(event=None):
    torque_var.set('0')
    update_values()

window.bind('<Left>', steer_left_press)
window.bind('<Right>', steer_right_press)
window.bind('<KeyRelease-Left>', steer_release)
window.bind('<KeyRelease-Right>', steer_release)
window.bind('<Escape>', lambda e: on_closing())
window.protocol('WM_DELETE_WINDOW', on_closing)

# =============================
# START SERIAL + THREADS
# =============================
ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)

threading.Thread(target=serial_reader, args=(ser,), daemon=True).start()
threading.Thread(target=send_loop, args=(ser,), daemon=True).start()

window.mainloop()

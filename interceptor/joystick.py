#!/usr/bin/env python3
"""
Interceptor Core - ESP32 CAN Bridge Joystick UI

Sends steering and speed commands to an ESP32 over serial.
The ESP32 translates these into CAN packets for the interceptor core.

Serial Protocol:
  TX to ESP32:   CMD,{magnitude},{speed_kph},{enable}\n
    - magnitude: integer, -400 to +400 (CAN val0-val1 difference)
    - speed_kph: integer, 0 to 140
    - enable: 0 or 1 (engage/disengage relay)

  RX from ESP32: TEL,{adc0},{adc1},{override},{fault},{counter},{relay}\n
    - adc0/adc1: current ADC readings from interceptor
    - override: driver override detected (0/1)
    - fault: fault state code
    - counter: packet counter
    - relay: derived relay state (0/1)

Engage/Disengage:
  Press E to toggle engage. When disengaged:
    - ESP32 sends enable=0 → interceptor relay OFF → car drives normally
  When engaged:
    - ESP32 sends enable=1 → interceptor relay ON → joystick controls EPS

Speed Model:
  Throttle forward = accelerate, throttle back = brake.
  Releasing throttle = natural drag (coast down).
  Keyboard UP/DOWN also adjusts speed; releasing causes coast.

Torque Scaling (from firmware torque_lut.h):
  0 kph   → 100% torque allowed
  50 kph  → 75%
  100 kph → 50%
  >100    → 50% (clamped)
  Formula: scale = 100 - (kph / 2) for kph <= 100, else 50

Input Filtering:
  EMA low-pass filter on joystick axes to eliminate noise/jitter.
  filtered = alpha * current + (1 - alpha) * previous
  This prevents CAN bus spam from joystick oscillations causing EPS jitter.
"""

import tkinter as tk
import serial
from serial.tools import list_ports
import pygame
import threading
import queue
import time
import sys

# =========================================================
# CONFIGURATION
# =========================================================
BAUD = 115200
SERIAL_TIMEOUT = 0.1
SERIAL_WATCHDOG_MS = 200  # ms before emergency stop

ESP32_VID_PID = [
    (0x10C4, 0xEA60),  # CP210x
    (0x1A86, 0x7523),  # CH340
    (0x0403, 0x6001),  # FTDI
    (0x303A, 0x1001),  # ESP32-S3 native USB
]

ESP32_KEYWORDS = ["CP210", "CH340", "USB Serial", "ttyUSB", "ttyACM", "ESP32"]

# Joystick input
STEER_DEADZONE = 0.05
THROTTLE_DEADZONE = 0.10
STEER_AXIS = 0
THROTTLE_AXIS = 1
THROTTLE_INVERT = True

# Input filtering (EMA low-pass)
# Lower alpha = smoother but more lag. 0.2 is good for eliminating jitter.
STEER_FILTER_ALPHA = 0.2
THROTTLE_FILTER_ALPHA = 0.3

# Steering (magnitude sent to ESP32, firmware limit is 400)
MAX_MAGNITUDE = 100       # BENCH TEST LIMIT. Increase gradually: 100→200→300→400
MAX_STEER_STEP = 20       # Slew rate limit per 20ms tick (in magnitude units)

# Speed model (simulated vehicle dynamics)
MAX_SPEED = 140.0         # kph
ACCEL_RATE = 40.0         # kph/s at full throttle
BRAKE_RATE = 60.0         # kph/s at full brake
DRAG_RATE = 5.0           # kph/s natural coast-down (engine braking)
WATCHDOG_DRAG_MULTIPLIER = 4.0  # Emergency decel multiplier

# Keyboard speed control
KBD_SPEED_STEP = 5.0      # kph per key press

FAULT_NAMES = {
    0: "NO_FAULT",
    1: "STARTUP",
    2: "SENSOR",
    3: "SEND_FAIL",
    4: "SCE",
    5: "TIMEOUT",
    6: "BAD_CHECKSUM",
    7: "INVALID_CKSUM",
    8: "REQ_TOO_HIGH",
    9: "REQ_INVALID",
    10: "ADC_UNCONFIG",
    11: "TIMEOUT_VSS",
}


# =========================================================
# TORQUE LUT (display only — firmware applies this internally)
# =========================================================
# The interceptor firmware has its own torque LUT in flash that
# scales the received command by speed. We do NOT apply it here
# to avoid double-scaling. This is only used for the UI display
# so the operator can see what % the firmware will apply.
#
# Firmware formula: scale = 100 - (kph / 2) for kph <= 100, else 50

def get_firmware_torque_scale_display(speed_kph):
    """Display-only: shows what the firmware will scale internally.
    NOT applied to the output command."""
    kph = int(max(0, min(255, speed_kph)))
    if kph <= 100:
        return 100 - (kph // 2)
    return 50


# =========================================================
# STATE
# =========================================================
speed_kph = 0.0
current_steer = 0
throttle_input = 0.0
steer_request = 0.0       # Raw steer magnitude sent to ESP32 (-400..+400)
fw_scale_pct = 100        # Display-only: what firmware will apply internally
engaged = False           # Relay engage state (E key to toggle)

telemetry_tx = 0
telemetry_rx = 0

last_time = None
last_serial_send = 0.0

running = True
ser = None
current_port = None

js = None
joystick_name = "Not Connected"

# Filtered joystick values (EMA state)
filtered_steer = 0.0
filtered_throttle = 0.0

# Keyboard speed hold state
kbd_accel_held = False
kbd_brake_held = False

data_queue = queue.Queue()

# =========================================================
# PYGAME INIT (joystick only, no display window)
# =========================================================
pygame.init()
pygame.joystick.init()


# =========================================================
# HELPERS
# =========================================================
def clamp(v, lo=-1.0, hi=1.0):
    return max(lo, min(hi, v))


def ema_filter(current, previous, alpha):
    """Exponential Moving Average filter.
    alpha=1.0 means no filtering (raw input).
    alpha=0.2 means heavy smoothing (80% old + 20% new).
    """
    return alpha * current + (1.0 - alpha) * previous


def apply_deadzone(value, deadzone):
    """Apply deadzone with smooth ramp-in (no discontinuity at edge)."""
    if abs(value) < deadzone:
        return 0.0
    # Remap remaining range to 0..1 so there's no jump at deadzone edge
    sign = 1.0 if value > 0 else -1.0
    return sign * (abs(value) - deadzone) / (1.0 - deadzone)


def slew_limit(target, current, max_step):
    """Rate-limit steering changes to prevent sudden jumps."""
    if target > current + max_step:
        return current + max_step
    if target < current - max_step:
        return current - max_step
    return target


def find_esp32_port():
    """Auto-detect ESP32 serial port by VID/PID or description keywords."""
    ports = list(list_ports.comports())

    for p in ports:
        vid = getattr(p, "vid", None)
        pid = getattr(p, "pid", None)
        if vid and pid and (vid, pid) in ESP32_VID_PID:
            return p.device

    for p in ports:
        desc = f"{p.description} {p.device}".lower()
        if any(k.lower() in desc for k in ESP32_KEYWORDS):
            return p.device

    return None


def open_serial():
    """Connect to ESP32, auto-reconnect on failure."""
    global ser, current_port

    port = find_esp32_port()
    if not port:
        current_port = None
        return False

    if ser and ser.is_open and current_port == port:
        return True

    try:
        if ser and ser.is_open:
            ser.close()
    except Exception:
        pass

    try:
        ser = serial.Serial(port, BAUD, timeout=SERIAL_TIMEOUT)
        current_port = port
        return True
    except Exception:
        ser = None
        current_port = None
        return False


def detect_joystick():
    """Detect joystick with hotplug support."""
    global js, joystick_name

    if js is not None and js.get_init():
        return True

    pygame.joystick.quit()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        js = None
        joystick_name = "Not Connected"
        return False

    js = pygame.joystick.Joystick(0)
    js.init()
    joystick_name = js.get_name()
    return True


def update_speed(dt, throttle):
    """Vehicle speed model: accelerate, brake, or coast.
    Mimics real vehicle behavior - releasing throttle causes gradual deceleration.
    """
    global speed_kph

    if dt <= 0 or dt > 0.2:
        dt = 0.02

    if throttle > THROTTLE_DEADZONE:
        # Accelerating
        speed_kph += throttle * ACCEL_RATE * dt
    elif throttle < -THROTTLE_DEADZONE:
        # Braking (active deceleration)
        speed_kph += throttle * BRAKE_RATE * dt
    else:
        # Coasting - natural drag always pulls speed toward zero
        speed_kph -= DRAG_RATE * dt

    speed_kph = clamp(speed_kph, 0.0, MAX_SPEED)


def send_calibration():
    """Send CAL command to ESP32 for ADC center calibration."""
    if ser and ser.is_open:
        try:
            ser.write(b"CAL\n")
        except Exception:
            pass


# =========================================================
# SERIAL READER THREAD
# =========================================================
def serial_reader():
    """Background thread: read telemetry from ESP32."""
    global ser, current_port, running

    while running:
        if not open_serial():
            time.sleep(0.5)
            continue

        try:
            line = ser.readline().decode(errors="ignore").strip()
            if line.startswith("TEL,"):
                data_queue.put(line)
        except Exception:
            try:
                ser.close()
            except Exception:
                pass
            ser = None
            current_port = None
            time.sleep(0.5)


# =========================================================
# GUI UPDATE
# =========================================================
def update_gui():
    global telemetry_rx

    try:
        while True:
            line = data_queue.get_nowait()
            parts = line.split(",")
            if len(parts) == 7:
                _, adc0, adc1, override, fault, counter, relay = parts
                telemetry_rx += 1

                labels["adc0"].config(text=f"ADC0: {adc0}")
                labels["adc1"].config(text=f"ADC1: {adc1}")
                labels["override"].config(
                    text=f"Override: {'YES' if int(override) else 'No'}",
                    fg="orange" if int(override) else "white"
                )
                fault_code = int(fault)
                fault_name = FAULT_NAMES.get(fault_code, f"UNKNOWN({fault_code})")
                fault_color = "lime" if fault_code == 0 else "red"
                labels["fault"].config(text=f"Fault: {fault_name}", fg=fault_color)
                labels["relay"].config(
                    text=f"Relay: {'ON' if int(relay) else 'OFF'}",
                    fg="lime" if int(relay) else "red"
                )
                labels["counter"].config(text=f"Counter: {counter}")
                labels["rx"].config(text=f"RX: {telemetry_rx}")
    except queue.Empty:
        pass

    # Connection status
    serial_str = current_port if current_port else "Searching..."
    serial_color = "lime" if current_port else "orange"
    labels["status"].config(text=f"ESP32: {serial_str}  |  JS: {joystick_name}", fg=serial_color)

    # Speed with color gradient (green=slow, yellow=mid, red=fast)
    if speed_kph < 40:
        spd_color = "lime"
    elif speed_kph < 80:
        spd_color = "yellow"
    else:
        spd_color = "#ff6644"
    labels["speed"].config(text=f"Speed: {speed_kph:.1f} kph", fg=spd_color)

    # Torque display: show what we send + what firmware will scale it to
    torque_color = "lime" if abs(steer_request) < MAX_MAGNITUDE * 0.5 else "yellow"
    if abs(steer_request) > MAX_MAGNITUDE * 0.8:
        torque_color = "#ff6644"
    fw_effective = steer_request * (fw_scale_pct / 100.0)
    labels["torque"].config(
        text=f"Mag: {steer_request:+.0f}/400 → FW:{fw_scale_pct}% → eff:{fw_effective:+.0f}",
        fg=torque_color
    )

    # Engage state
    engage_color = "lime" if engaged else "#ff4444"
    engage_text = "ENGAGED" if engaged else "DISENGAGED"
    labels["steer"].config(text=f"[{engage_text}]  Steer: {current_steer:+d}", fg=engage_color)
    labels["throttle"].config(text=f"Throttle: {throttle_input:+.2f}")
    labels["tx"].config(text=f"TX: {telemetry_tx}")

    # Steer bar visualization
    bar_canvas.delete("all")
    w = bar_canvas.winfo_width()
    h = bar_canvas.winfo_height()
    if w > 1:
        mid = w // 2
        # Background zones (green center, yellow edges, red extremes)
        zone_w = w // 6
        bar_canvas.create_rectangle(mid - zone_w, 0, mid + zone_w, h, fill="#1a3a1a", outline="")
        bar_canvas.create_line(mid, 0, mid, h, fill="#555", width=2)

        # Indicator position
        pos_x = mid + int((current_steer / MAX_MAGNITUDE) * (w // 2 - 10))
        color = "#00ff88" if (current_port and engaged) else "#ff4444"
        bar_canvas.create_rectangle(pos_x - 6, 2, pos_x + 6, h - 2, fill=color, outline="white")
        bar_canvas.create_text(10, h // 2, text="L", fill="#aaa", font=("Arial", 10, "bold"))
        bar_canvas.create_text(w - 10, h // 2, text="R", fill="#aaa", font=("Arial", 10, "bold"))

        # Scale indicator text (shows firmware's internal scaling)
        bar_canvas.create_text(mid, h // 2, text=f"FW:{fw_scale_pct}%", fill="#888", font=("Arial", 8))

    # Update engage button appearance
    if engaged:
        engage_btn.config(text="DISENGAGE (E)", bg="#339933", activebackground="#44bb44")
    else:
        engage_btn.config(text="ENGAGE (E)", bg="#993333", activebackground="#bb4444")

    root.after(50, update_gui)


# =========================================================
# CONTROL LOOP (50 Hz)
#
# This runs every 20ms via tkinter's after() scheduler.
# It reads the joystick, applies filtering and safety limits,
# then sends a CMD to the ESP32 which forwards it to the interceptor.
#
# Signal path:
#   Joystick axis (-1..+1)
#   → EMA filter (removes jitter)
#   → Deadzone (removes center drift)
#   → Scale to magnitude (-MAX_MAGNITUDE..+MAX_MAGNITUDE)
#   → Slew rate limit (prevents instant jumps)
#   → Serial CMD to ESP32
#   → ESP32 builds CAN 0x300 with CRC + counter
#   → Interceptor receives, applies torque LUT, drives DAC
#
# The 'engaged' flag controls whether the relay is ON or OFF.
# When disengaged, the ESP32 still sends packets (with enable=0)
# so the interceptor knows we're alive (no timeout fault).
# =========================================================
def control_loop():
    global current_steer, throttle_input, speed_kph
    global last_time, last_serial_send, telemetry_tx
    global ser, current_port
    global filtered_steer, filtered_throttle
    global steer_request, fw_scale_pct

    now = time.monotonic()

    if last_time is None:
        last_time = now
        last_serial_send = now
        root.after(20, control_loop)
        return

    dt = now - last_time
    last_time = now

    watchdog_triggered = (now - last_serial_send) > (SERIAL_WATCHDOG_MS / 1000.0)

    if watchdog_triggered:
        # Emergency: zero everything, coast to stop fast
        throttle_input = 0.0
        filtered_steer = 0.0
        filtered_throttle = 0.0
        current_steer = slew_limit(0, current_steer, MAX_STEER_STEP)
        speed_kph = max(0.0, speed_kph - DRAG_RATE * dt * WATCHDOG_DRAG_MULTIPLIER)
        steer_request = 0.0
    else:
        if not detect_joystick():
            # No joystick: handle keyboard-only speed control
            throttle_input = 0.0
            filtered_steer = ema_filter(0.0, filtered_steer, STEER_FILTER_ALPHA)
            filtered_throttle = 0.0
            current_steer = slew_limit(0, current_steer, MAX_STEER_STEP)

            # Keyboard speed: held keys accelerate, release coasts
            if kbd_accel_held:
                speed_kph = min(MAX_SPEED, speed_kph + ACCEL_RATE * dt * 0.5)
            elif kbd_brake_held:
                speed_kph = max(0.0, speed_kph - BRAKE_RATE * dt * 0.5)
            else:
                speed_kph = max(0.0, speed_kph - DRAG_RATE * dt)
        else:
            pygame.event.pump()

            # --- Raw joystick read ---
            raw_steer_axis = clamp(js.get_axis(STEER_AXIS))
            raw_throttle_axis = clamp(js.get_axis(THROTTLE_AXIS))

            if THROTTLE_INVERT:
                raw_throttle_axis = -raw_throttle_axis

            # --- EMA filter (eliminates jitter/noise) ---
            filtered_steer = ema_filter(raw_steer_axis, filtered_steer, STEER_FILTER_ALPHA)
            filtered_throttle = ema_filter(raw_throttle_axis, filtered_throttle, THROTTLE_FILTER_ALPHA)

            # --- Deadzone (applied AFTER filtering for stability) ---
            steer_clean = apply_deadzone(filtered_steer, STEER_DEADZONE)
            throttle_clean = apply_deadzone(filtered_throttle, THROTTLE_DEADZONE)

            throttle_input = throttle_clean

            # --- Compute steer magnitude (NO scaling here — firmware has its own LUT) ---
            steer_request = steer_clean * MAX_MAGNITUDE
            fw_scale_pct = get_firmware_torque_scale_display(speed_kph)  # display only

            # Apply slew rate limiting to final steer command
            target_steer = int(round(steer_request))
            target_steer = max(-MAX_MAGNITUDE, min(MAX_MAGNITUDE, target_steer))
            current_steer = slew_limit(target_steer, current_steer, MAX_STEER_STEP)

            # Update simulated speed
            update_speed(dt, throttle_clean)

    # Send command to ESP32 every tick (20ms = 50 Hz)
    # Format: CMD,{magnitude},{speed_kph},{enable}
    # - magnitude is the CAN val0-val1 difference (-400..+400)
    # - speed is the simulated vehicle speed for torque LUT
    # - enable controls the interceptor relay (1=on, 0=off)
    # NOTE: We ALWAYS send, even when disengaged (enable=0).
    # This keeps the interceptor's CAN timeout from triggering.
    if ser and ser.is_open:
        try:
            enable_int = 1 if engaged else 0
            cmd = f"CMD,{current_steer},{int(round(speed_kph))},{enable_int}\n"
            ser.write(cmd.encode())
            telemetry_tx += 1
            last_serial_send = now
        except Exception:
            ser = None
            current_port = None

    root.after(20, control_loop)


# =========================================================
# KEYBOARD HANDLER
# =========================================================
def toggle_engage():
    """Toggle relay engage/disengage.
    
    ENGAGED:    ESP32 sends enable=1 → interceptor relay ON → joystick controls EPS
    DISENGAGED: ESP32 sends enable=0 → interceptor relay OFF → car drives normally
    
    Safety: even when engaged, the interceptor will auto-disengage if:
      - CAN timeout (no packets for ~1 second)
      - Speed timeout (no 0x76 for ~0.4 second)
      - CRC error on any packet
      - Magnitude exceeds 400
    """
    global engaged
    engaged = not engaged


def key_press(event):
    global speed_kph, kbd_accel_held, kbd_brake_held
    if event.keysym in ("Up", "plus", "equal"):
        kbd_accel_held = True
    elif event.keysym in ("Down", "minus"):
        kbd_brake_held = True
    elif event.keysym == "e":
        toggle_engage()
    elif event.keysym == "c":
        send_calibration()
    elif event.keysym == "q":
        on_closing()


def key_release(event):
    global kbd_accel_held, kbd_brake_held
    if event.keysym in ("Up", "plus", "equal"):
        kbd_accel_held = False
    elif event.keysym in ("Down", "minus"):
        kbd_brake_held = False


# =========================================================
# SHUTDOWN
# =========================================================
def on_closing():
    global running
    running = False
    try:
        if ser and ser.is_open:
            ser.close()
    except Exception:
        pass
    pygame.quit()
    root.destroy()


# =========================================================
# BUILD GUI
# =========================================================
root = tk.Tk()
root.title("Interceptor Core - Joystick Controller")
root.geometry("700x750")
root.configure(bg="#1e1e1e")
root.protocol("WM_DELETE_WINDOW", on_closing)
root.bind("<KeyPress>", key_press)
root.bind("<KeyRelease>", key_release)

LABEL_FONT = ("Consolas", 16)
LABEL_BG = "#1e1e1e"
LABEL_FG = "white"

labels = {}
label_keys = [
    "status", "speed", "torque", "steer", "throttle",
    "adc0", "adc1", "override", "fault",
    "relay", "counter", "tx", "rx"
]

for key in label_keys:
    lbl = tk.Label(root, text=f"{key}: ---", font=LABEL_FONT, bg=LABEL_BG, fg=LABEL_FG, anchor="w")
    lbl.pack(fill="x", padx=20, pady=2)
    labels[key] = lbl

# Steering bar
bar_frame = tk.Frame(root, bg=LABEL_BG)
bar_frame.pack(fill="x", padx=20, pady=10)
tk.Label(bar_frame, text="Steering (scaled by speed LUT):", font=("Consolas", 11), bg=LABEL_BG, fg="#888").pack(anchor="w")
bar_canvas = tk.Canvas(bar_frame, height=34, bg="#222", highlightthickness=0)
bar_canvas.pack(fill="x")

# Engage/Disengage button
engage_btn = tk.Button(
    root, text="ENGAGE (E)", command=toggle_engage,
    font=("Arial", 14, "bold"), bg="#993333", fg="white", activebackground="#bb4444",
    width=20, height=2
)
engage_btn.pack(pady=8)

# Calibration button
cal_btn = tk.Button(
    root, text="Calibrate ESP32 (send CAL)", command=send_calibration,
    font=("Arial", 12), bg="#336699", fg="white", activebackground="#4488bb"
)
cal_btn.pack(pady=4)

# Help text
tk.Label(
    root,
    text="Joystick: X=Steer, Y=Throttle | Keys: E=Engage, Up/Down=Speed, C=Cal, Q=Quit\n"
         "DISENGAGE = relay off = car drives normally | ENGAGE = relay on = joystick controls",
    font=("Arial", 9), bg=LABEL_BG, fg="#666", justify="center"
).pack(side="bottom", pady=5)

# =========================================================
# START
# =========================================================
threading.Thread(target=serial_reader, daemon=True).start()

root.after(100, update_gui)
root.after(20, control_loop)

root.mainloop()

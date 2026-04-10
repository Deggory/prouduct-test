import tkinter as tk
import serial
import pygame
import threading
import time

PORT = "/dev/ttyUSB0"   # Windows: COM5
BAUD = 115200

DEADZONE = 0.05
MAX_STEP = 8
MAX_STEER = 300

FAULTS = {
    0: "NO_FAULT",
    1: "TIMEOUT",
    2: "TIMEOUT_VSS",
    3: "BAD_CHECKSUM",
    4: "SEND_FAIL",
    5: "SENSOR",
    6: "ADC_UNCONFIG",
}

speed_kph = 0
current_steer = 0
running = True
telemetry = {"tx": 0, "rx": 0}

ser = serial.Serial(PORT, BAUD, timeout=0.05)

pygame.init()
pygame.joystick.init()
js = pygame.joystick.Joystick(0)
js.init()


def slew_limit(target, current):
    if target > current + MAX_STEP:
        return current + MAX_STEP
    if target < current - MAX_STEP:
        return current - MAX_STEP
    return target


def send_loop(labels):
    global current_steer
    while running:
        pygame.event.pump()

        axis = js.get_axis(0)

        # soft center deadzone
        if abs(axis) < DEADZONE:
            axis = 0

        target = int(axis * MAX_STEER)

        # slew limiter
        current_steer = slew_limit(target, current_steer)

        ser.write(f"CMD,{current_steer},{speed_kph}\n".encode())
        telemetry["tx"] += 1

        labels["steer"].config(text=f"Steer: {current_steer}")
        labels["speed"].config(text=f"Speed: {speed_kph} km/h")
        labels["tx"].config(text=f"TX: {telemetry['tx']}")

        time.sleep(0.02)  # 50 Hz


def rx_loop(labels):
    while running:
        line = ser.readline().decode(errors="ignore").strip()

        if not line.startswith("TEL,"):
            continue

        try:
            _, adc0, adc1, override, fault, counter, relay = line.split(",")

            telemetry["rx"] += 1

            labels["adc0"].config(text=f"ADC0: {adc0}")
            labels["adc1"].config(text=f"ADC1: {adc1}")
            labels["override"].config(text=f"Override: {override}")
            labels["fault"].config(
                text=f"Fault: {FAULTS.get(int(fault), fault)}"
            )
            labels["relay"].config(
                text=f"Relay: {'ON' if int(relay) else 'OFF'}"
            )
            labels["counter"].config(text=f"Counter: {counter}")
            labels["rx"].config(text=f"RX: {telemetry['rx']}")

        except Exception:
            pass


def key_handler(event):
    global speed_kph

    if event.keysym in ["plus", "equal"]:
        speed_kph += 10
    elif event.keysym == "minus":
        speed_kph = max(0, speed_kph - 10)


root = tk.Tk()
root.title("Interceptor Pro Dashboard")
root.geometry("520x650")

labels = {}

for key in [
    "steer",
    "speed",
    "adc0",
    "adc1",
    "override",
    "fault",
    "relay",
    "counter",
    "tx",
    "rx",
]:
    labels[key] = tk.Label(root, text=f"{key}: 0", font=("Arial", 18))
    labels[key].pack(pady=5)

root.bind("<Key>", key_handler)

threading.Thread(target=send_loop, args=(labels,), daemon=True).start()
threading.Thread(target=rx_loop, args=(labels,), daemon=True).start()

root.mainloop()
running = False

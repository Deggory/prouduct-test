#!/usr/bin/env python3
import time
import threading
from pynput import keyboard

# ---------------------------
# INTERCEPTOR / DAC SETTINGS
# ---------------------------
MAX_STEP = 8        # torque step per loop
UPDATE_RATE = 0.02  # 50 Hz loop
MAX_DAC = 4095      # max DAC value
MIN_DAC = 0         # min DAC value
RAMP_FACTOR = 0.2   # smoothing factor (0 = no ramp, 1 = instant)

# ---------------------------
# GLOBAL VARIABLES
# ---------------------------
center_a = 0
center_b = 0
max_delta = 0
current_delta = 0
target_delta = 0
running = True
left_pressed = False
right_pressed = False
emergency_stop = False
torque_scale = 1.0   # scaling factor (0.0 - 1.0)

# ---------------------------
# MOCK FUNCTIONS (replace with real interceptor functions)
# ---------------------------
def read_eps_adc():
    """Read the Polo EPS torque sensor channels."""
    return 0, 0  # replace with real ADC readings

def send_dac_to_interceptor(dac0, dac1):
    """Send torque values to Interceptor board."""
    print(f"DAC -> A:{dac0:.0f} B:{dac1:.0f} (Scale={torque_scale:.2f})")

# ---------------------------
# KEYBOARD CALLBACKS
# ---------------------------
def on_press(key):
    global left_pressed, right_pressed, emergency_stop, torque_scale
    try:
        if key == keyboard.Key.left:
            left_pressed = True
        elif key == keyboard.Key.right:
            right_pressed = True
        elif key == keyboard.Key.esc:
            emergency_stop = True
        elif key.char == '+':
            torque_scale = min(torque_scale + 0.1, 1.0)
            print(f"Torque scale increased: {torque_scale:.2f}")
        elif key.char == '-':
            torque_scale = max(torque_scale - 0.1, 0.0)
            print(f"Torque scale decreased: {torque_scale:.2f}")
    except AttributeError:
        pass

def on_release(key):
    global left_pressed, right_pressed
    if key == keyboard.Key.left:
        left_pressed = False
    elif key == keyboard.Key.right:
        right_pressed = False

# ---------------------------
# CALIBRATION FUNCTION
# ---------------------------
def calibrate_eps():
    global center_a, center_b, max_delta
    print("=== Calibration phase ===")
    print("Turn the wheel full left, then full right slowly.")
    print("You have 10 seconds...")

    adc_a_values = []
    adc_b_values = []

    start_time = time.time()
    while time.time() - start_time < 10:
        a, b = read_eps_adc()
        adc_a_values.append(a)
        adc_b_values.append(b)
        time.sleep(0.01)

    min_a, max_a = min(adc_a_values), max(adc_a_values)
    min_b, max_b = min(adc_b_values), max(adc_b_values)

    center_a = (min_a + max_a) / 2
    center_b = (min_b + max_b) / 2
    max_delta = min(max_a - center_a, center_a - min_a,
                    max_b - center_b, center_b - min_b)

    print(f"Calibration complete:")
    print(f" CENTER_A = {center_a:.0f}, CENTER_B = {center_b:.0f}")
    print(f" MAX_DELTA = {max_delta:.0f}")
    print("========================")

# ---------------------------
# MAIN CONTROL LOOP
# ---------------------------
def control_loop():
    global current_delta, target_delta, running, emergency_stop, torque_scale

    while running:
        if emergency_stop:
            current_delta = 0
            send_dac_to_interceptor(center_a, center_b)
            print("EMERGENCY STOP! Torque set to 0.")
            break

        # Set target based on keys
        if left_pressed:
            target_delta = max_delta * torque_scale
        elif right_pressed:
            target_delta = -max_delta * torque_scale
        else:
            target_delta = 0

        # Smooth ramping towards target (soft PID-like behavior)
        current_delta += (target_delta - current_delta) * RAMP_FACTOR

        # Clamp delta
        current_delta = max(min(current_delta, max_delta), -max_delta)

        # Send DAC
        dac0 = center_a + current_delta
        dac1 = center_b - current_delta
        dac0 = max(min(dac0, MAX_DAC), MIN_DAC)
        dac1 = max(min(dac1, MAX_DAC), MIN_DAC)

        send_dac_to_interceptor(dac0, dac1)
        time.sleep(UPDATE_RATE)

# ---------------------------
# PROGRAM ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    calibrate_eps()
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    try:
        control_loop()
    except KeyboardInterrupt:
        print("Exiting program...")
    finally:
        listener.stop()
        send_dac_to_interceptor(center_a, center_b)
        print("Torque set to center. Goodbye!")

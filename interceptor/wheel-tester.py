#!/usr/bin/env python3
import time
from pynput import keyboard

# ==========================================
# EPS INTERCEPTOR SAFE SETTINGS
# ==========================================
MAX_DAC = 4095
MIN_DAC = 0

UPDATE_RATE = 0.01       # 100 Hz
RAMP_FACTOR = 0.12       # smooth ramp
MAX_STEP = 4             # max DAC counts per loop
MAX_DELTA = 80           # SAFE spoof torque limit
PLAUSIBILITY_LIMIT = 20  # A+B constant check

# ==========================================
# GLOBALS
# ==========================================
center_a = 0
center_b = 0
sum_center = 0

current_delta = 0.0
target_delta = 0.0

left_pressed = False
right_pressed = False
emergency_stop = False
running = True

torque_scale = 1.0

# ==========================================
# REPLACE WITH REAL ADC READ
# ==========================================
def read_eps_adc():
    """
    Read real ADC values from torque sensor channels.
    Replace this with STM32 ADC or Panda ADC.
    """
    return 2113, 2097


# ==========================================
# REPLACE WITH REAL DAC SEND
# ==========================================
def send_dac_to_interceptor(dac0, dac1):
    """
    Replace with MCP4728 / STM32 DAC write.
    """
    print(f"DAC A:{dac0:.0f} B:{dac1:.0f}  Delta:{current_delta:.1f}")


# ==========================================
# KEYBOARD HANDLER
# ==========================================
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
            torque_scale = min(1.0, torque_scale + 0.1)
            print(f"Torque scale: {torque_scale:.1f}")
        elif key.char == '-':
            torque_scale = max(0.1, torque_scale - 0.1)
            print(f"Torque scale: {torque_scale:.1f}")
    except AttributeError:
        pass


def on_release(key):
    global left_pressed, right_pressed

    if key == keyboard.Key.left:
        left_pressed = False
    elif key == keyboard.Key.right:
        right_pressed = False


# ==========================================
# CENTER CALIBRATION
# ==========================================
def calibrate_center():
    global center_a, center_b, sum_center

    print("Keep steering wheel centered...")
    samples_a = []
    samples_b = []

    for _ in range(100):
        a, b = read_eps_adc()
        samples_a.append(a)
        samples_b.append(b)
        time.sleep(0.01)

    center_a = sum(samples_a) / len(samples_a)
    center_b = sum(samples_b) / len(samples_b)
    sum_center = center_a + center_b

    print(f"Center calibrated:")
    print(f" A = {center_a:.1f}")
    print(f" B = {center_b:.1f}")
    print(f" SUM = {sum_center:.1f}")


# ==========================================
# MAIN CONTROL LOOP
# ==========================================
def control_loop():
    global current_delta, target_delta, emergency_stop

    while running:
        if emergency_stop:
            send_dac_to_interceptor(center_a, center_b)
            print("EMERGENCY STOP")
            break

        # ----------------------------------
        # target torque from keyboard
        # ----------------------------------
        if left_pressed:
            target_delta = MAX_DELTA * torque_scale
        elif right_pressed:
            target_delta = -MAX_DELTA * torque_scale
        else:
            target_delta = 0

        # ----------------------------------
        # smooth ramp
        # ----------------------------------
        desired = current_delta + (target_delta - current_delta) * RAMP_FACTOR

        # ----------------------------------
        # step limiter
        # ----------------------------------
        step = desired - current_delta
        step = max(min(step, MAX_STEP), -MAX_STEP)
        current_delta += step

        # ----------------------------------
        # clamp safe range
        # ----------------------------------
        current_delta = max(min(current_delta, MAX_DELTA), -MAX_DELTA)

        # ----------------------------------
        # complementary torque channels
        # ----------------------------------
        dac0 = center_a + current_delta
        dac1 = center_b - current_delta

        dac0 = max(min(dac0, MAX_DAC), MIN_DAC)
        dac1 = max(min(dac1, MAX_DAC), MIN_DAC)

        # ----------------------------------
        # plausibility safety
        # ----------------------------------
        if abs((dac0 + dac1) - sum_center) > PLAUSIBILITY_LIMIT:
            emergency_stop = True
            print("PLAUSIBILITY FAULT!")
            continue

        send_dac_to_interceptor(dac0, dac1)
        time.sleep(UPDATE_RATE)


# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    calibrate_center()

    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )
    listener.start()

    try:
        control_loop()
    finally:
        listener.stop()
        send_dac_to_interceptor(center_a, center_b)
        print("Returned to center safely")

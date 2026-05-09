# ESP32 Interceptor Test Tools

Two Python tools that communicate with the Interceptor Core **through the ESP32 CAN bridge** (`esp32_can_bridge.ino`). No Chimera USB or direct CAN adapter needed.

---

## ESP32 Firmware Compatibility

**File:** `esp32_can_bridge.ino`  
**Status:** ✅ Fully compatible with both tools — no firmware changes required.

| Protocol | ESP32 supports | Both tools use |
|---|---|---|
| `CMD,{mag},{speed},{enable}\n` | ✅ | ✅ |
| `TEL,{adc0},{adc1},{override},{fault},{counter},{relay}\n` | ✅ | ✅ |
| `CAL\n` → `[CAL] ACK` | ✅ | ✅ (UI only) |

**One mandatory change already applied:** `sendSteer()` now sends `val0=0, val1=0` when `enable=0`. This fixes `FAULT_INVALID_CKSUM`. If you have not reflashed your ESP32 yet, do it now — both tools will hit this fault otherwise.

---

## Requirements

```bash
pip install pyserial
```

No `pygame`, no `usb1`, no Chimera, no Panda class. Just the ESP32 over USB serial.

---

## Tool 1 — Automated Sweep Test

**File:** `test_interceptor_dac_esp32.py`

### What it does

Runs a headless (no GUI) automated 7-step magnitude sweep and prints pass/fail for each step:

```
[Baseline]  magnitude=   0
  ADC0=1538  ADC1=1579  |diff|=41

[Sweep]  magnitude= +100  small positive (+100)
  ADC0=1488(Δ-50)  ✓   ADC1=1629(Δ+50)  ✓   → PASS

[Sweep]  magnitude= +200  medium positive (+200)
  ADC0=1438(Δ-100) ✓   ADC1=1679(Δ+100) ✓   → PASS
...
=== Sweep done: 7/7 passed ===
```

### What it checks

1. **Reaches NO_FAULT** — if ADC channels are not configured it aborts with a clear message.
2. **Reads baseline** ADC values at magnitude=0 (your calibrated centers: ~1538, ~1579).
3. **For each magnitude**, verifies ADC direction response:
   - Positive magnitude → DAC0 should decrease, DAC1 should increase (relative to baseline)
   - Negative magnitude → opposite
   - Zero → both return near baseline
4. **Checks fault stays 0** during every step.
5. **Safe shutdown** — sends `enable=0` (val0=0, val1=0) at the end.

### Usage

```bash
# Auto-detect ESP32
python3 tests/test_interceptor_dac_esp32.py

# Specify port manually
python3 tests/test_interceptor_dac_esp32.py /dev/ttyUSB0
```

### Exit codes
- `0` — all tests passed
- `1` — one or more tests failed, or ESP32 not found

### What a failure looks like

```
ABORT: Cannot reach NO_FAULT.
  Check that:
  1. ADC channels are configured (run stm_flash_config.py)
  2. CAN bus is connected (ESP32 ↔ Interceptor Core)
  3. Interceptor Core is powered and running
```

---

## Tool 2 — Live Control & Monitor UI

**File:** `test_interceptor_esp32_ui.py`

### What it does

A dark-themed GUI window with full real-time control and telemetry. Does not need a joystick.

```
┌─────────────────────────────────────────────────────────┐
│  Interceptor Core · ESP32 Test & Control    ● /dev/ttyUSB0 │
├─────────────────┬───────────────────────────────────────┤
│  CONTROL        │  TELEMETRY                            │
│                 │                                       │
│  Steer  [+050]  │  ADC0 :      1538                    │
│  ────────●────  │  ADC1 :      1579                    │
│                 │  |ADC0-ADC1| :  41                   │
│  Speed  [ 30 kph] │  Fault :   NO_FAULT  (green)       │
│  ──────────●──  │  Override :  No                      │
│                 │  Relay :     ON   (green)             │
│  [DISENGAGE (E)]│  Pkt# :      7                       │
│  [Zero Steer]   │                                       │
│  [Calibrate]    │  ┌── ADC Live Graph ──────────────┐  │
│  [Sweep Test]   │  │  green=ADC0   cyan=ADC1        │  │
│                 │  │  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~│  │
│  TX: 412  RX:411│  └───────────────────────────────┘  │
├─────────────────┴───────────────────────────────────────┤
│  LOG                                                    │
│  [14:22:01] Connected to ESP32 on /dev/ttyUSB0         │
│  [14:22:08] Sweep: ALL 7/7 PASSED                      │
└─────────────────────────────────────────────────────────┘
```

### Controls

| Input | Action |
|---|---|
| Steer slider | Set magnitude −400 to +400 |
| Speed slider | Set simulated speed 0–140 kph |
| `E` key | Toggle ENGAGE / DISENGAGE |
| `←` / `→` keys (hold) | Nudge steer ±10 per tick continuously |
| `Space` | Emergency stop: zero steer + disengage |
| `T` key | Run sweep test (same 7-step test as the CLI tool, runs in background) |
| `C` key | Send `CAL` to ESP32 |
| `Q` key | Quit safely |

### Panels

**Left panel — Control:**
- Steer slider and current magnitude value
- Speed slider and current kph value
- ENGAGE/DISENGAGE button (red when off, green when on)
- Zero Steer, Calibrate, Run Sweep Test buttons
- TX/RX packet counters

**Right panel — Telemetry:**
- ADC0, ADC1 raw values (updated every incoming TEL frame)
- `|ADC0−ADC1|` — differential torque magnitude
- Fault state — green for NO_FAULT, red for anything else
- Override flag — yellow warning if driver fighting the wheel
- Relay state — green ON / red OFF
- Packet counter from interceptor

**ADC Live Graph:**
- Scrolling 300-sample history
- Green line = ADC0, Cyan line = ADC1
- Current values shown at right edge
- Reference lines at 1024, 2048, 3072

**Log panel:**
- Timestamped messages from ESP32 (`[ESP32] ...`)
- Sweep test results per step
- Connection events

### Usage

```bash
python3 tests/test_interceptor_esp32_ui.py
```

Auto-detects the ESP32. If multiple serial devices are present and it picks the wrong one, unplug other devices first.

---

## Which tool to use when

| Situation | Use |
|---|---|
| First-time setup — verify the whole chain works | `test_interceptor_dac_esp32.py` (automated pass/fail) |
| Ongoing bench testing and manual control | `test_interceptor_esp32_ui.py` (live GUI) |
| Debugging a specific fault or direction issue | `test_interceptor_esp32_ui.py` (see fault in real time) |
| Automated CI / scripted verification | `test_interceptor_dac_esp32.py` (exit code 0/1) |

---

## Before running either tool

1. **ADC channels must be configured** in interceptor flash:
   ```bash
   python3 stm_flash_config.py
   # ADC0: center=1538, tolerance=125, enable=1
   # ADC1: center=1579, tolerance=100, enable=1
   ```
2. **ESP32 must be flashed** with the current `esp32_can_bridge.ino` (with the `FAULT_INVALID_CKSUM` fix).
3. **CAN bus wired**: ESP32 MCP2515 ↔ Interceptor Core CAN_H/CAN_L.
4. **Interceptor Core powered** and running in differential mode (`mode=1`).

If these are met, both tools will show `NO_FAULT` and operate normally.

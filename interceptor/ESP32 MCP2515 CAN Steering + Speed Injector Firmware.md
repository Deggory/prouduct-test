# ESP32 MCP2515 CAN Steering + Speed Injector Firmware

A robust **ESP32 + MCP2515 CAN firmware** for steering torque injection, speed simulation, and live telemetry feedback.

This project is designed for:

* steering interceptor / torque sensor emulation
* EPS bench testing
* autonomous steering experiments
* PC GUI control over Serial
* live telemetry visualization

---

# Features

* Differential **dual-channel torque sensor emulation**
* Vehicle **speed CAN frame simulation**
* **Rolling counter** support for OEM-style freshness checks
* **CAN auto-recovery watchdog** after repeated TX failures
* **Telemetry RX** for ADC feedback, override, and faults
* Simple **CSV serial protocol** for Python GUI integration
* Stable **50 Hz control loop**
* Verified **ESP32 VSPI pin mapping**

---

# Hardware

## ESP32 ↔ MCP2515 VSPI Wiring

| MCP2515 |                      ESP32 |
| ------- | -------------------------: |
| CS      |                     GPIO 5 |
| SCK     |                    GPIO 18 |
| MISO    |                    GPIO 19 |
| MOSI    |                    GPIO 23 |
| VCC     | 5V / 3.3V module dependent |
| GND     |                        GND |

> MCP2515 crystal is configured for **8 MHz**.

---

# CAN Configuration

* **Bitrate:** 500 kbps
* **Oscillator:** 8 MHz
* **Torque TX ID:** `0x220`
* **Telemetry RX ID:** `0x221`
* **Speed TX ID:** `0x076`
* **Loop Rate:** 50 Hz

---

# Serial Protocol

## PC → ESP32 Command

Format:

```text
CMD,<steer>,<speed>
```

Example:

```text
CMD,300,60
```

Meaning:

* `steer = +300` → right torque
* `speed = 60` → 60 km/h

---

## ESP32 → PC Telemetry

Format:

```text
TEL,<adc0>,<adc1>,<override>,<fault>,<counter>,<relay>
```

Example:

```text
TEL,2080,2016,0,0,5,1
```

Fields:

* `adc0` → channel A feedback
* `adc1` → channel B feedback
* `override` → human steering override flag
* `fault` → fault nibble
* `counter` → rolling counter
* `relay` → virtual active state

---

# Firmware Architecture

## 1) CAN Recovery Watchdog

The firmware automatically resets MCP2515 if CAN transmission fails repeatedly.

### Recovery steps

1. Reset MCP2515
2. Wait 10 ms
3. Reconfigure bitrate
4. Enter normal mode

This prevents bus lockups during long bench tests.

---

## 2) Differential Torque Injection

Torque is generated around DAC center value `2048`.

```text
ch0 = 2048 + steer
ch1 = 2048 - steer
```

This mimics a real torque sensor:

* one channel rises
* the other falls

This preserves plausibility checks used by EPS ECUs.

---

## 3) Speed Frame Simulation

Vehicle speed is scaled by:

```text
speed_raw = kmh × 100
```

Example:

* `60 km/h → 6000`

This is packed into CAN ID `0x076`.

---

## 4) Telemetry Feedback

The interceptor ECU responds with:

* live ADC values
* override status
* fault nibble
* rolling counter confirmation

Useful for:

* GUI live plotting
* calibration
* fault detection
* relay state visualization

---

# Main Loop Sequence

The loop runs every **20 ms (50 Hz)**.

Execution order:

1. Read serial command
2. Send torque frame
3. Send speed frame
4. Read telemetry
5. Increment rolling counter
6. Wait 20 ms

---

# Data Flow

```text
PC GUI
   ↓ Serial CMD
ESP32
   ↓ SPI
MCP2515
   ↓ CAN torque + speed
Interceptor ECU
   ↑ CAN telemetry
ESP32
   ↑ Serial TEL
GUI plots / logging
```

---

# Safety Notes

* Always clamp `steer` values in GUI side
* Recommended safe range: `±1000`
* Use isolated power for bench testing
* Add external watchdog for in-vehicle tests
* Validate all CAN IDs with your DBC
* Never test on-road without independent override path

---

# Suggested Future Improvements

* steering ramp / inertia simulation
* speed-based torque gain
* auto-centering
* CRC nibble support
* heartbeat timeout
* EEPROM saved center trim
* human override cancel
* telemetry rate measurement
* GUI auto-detect COM port

---

# Example Use Cases

* openpilot steering bench simulator
* EPS torque interceptor development
* CAN reverse engineering
* steering torque DAC testing
* telemetry dashboard validation
* speed dependent assist experiments

---

# License

MIT License

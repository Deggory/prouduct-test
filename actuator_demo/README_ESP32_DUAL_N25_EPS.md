# ESP32 Dual N25 EPS Controller

## 1. Purpose and Scope

This project implements an EPS actuator controller on ESP32 using:

- ESP32 Dev Module
- MCP2515 CAN controller (500 kbps, 8 MHz crystal)
- One BTS7960 H-bridge board driving two parallel N25 motors
- Two quadrature encoders (one per motor) for feedback and mismatch protection

The firmware accepts STM-style CAN steering commands, runs a cascade controller (position outer loop + velocity inner loop), drives PWM to the H-bridge, and publishes actuator status frames.

Primary implementation file:

- `tests/esp32_dual_n25_eps_controller.ino`

## 2. Functional Architecture

Control flow:

```text
CAN 0x22E torque request
        ↓
Packet validation (CRC + rolling counter)
        ↓
Torque request accepted
        ↓
Position target integrator
        ↓
Position loop (target velocity)
        ↓
Velocity loop (PWM command)
        ↓
BTS7960 output (single driver, dual motors)
        ↓
Encoders (motor 1 + motor 2)
        ↺
```

Safety gates run in parallel:

- Engage switch gating
- CAN command timeout
- Encoder mismatch detection

When any gate fails, controller output is forced to neutral PWM.

## 3. CAN Protocol Compatibility

### 3.1 Received Command Frame

- ID: `0x22E`
- DLC: 6

Byte map:

- `data[0]`: CRC8
- `data[1]`: lower nibble rolling counter (`0..15`), upper nibble mode/reserved
- `data[2..3]`: signed angle request (currently parsed but not used)
- `data[4..5]`: signed torque request (used)

Validation:

1. CRC8 (SAE J1850 style in this project)
2. Rolling counter progression check

Accepted torque request is constrained to `[-512, +512]`.

### 3.2 Status Feedback Frame

- ID: `0x22F`
- DLC: 7

Byte map:

- `data[0]`: CRC8
- `data[1]`: `(state << 4) | pkt_idx`
- `data[2]`: `steer_ok` flag
- `data[3]`: reserved (0)
- `data[4]`: reserved (0)
- `data[5..6]`: torque echo (LSB/MSB)

### 3.3 Cruise/Fake-Speed Frame

- ID: `0x22D`
- DLC: 4

Byte map:

- `data[0]`: CRC8
- `data[1]`: engage status (`1` engaged, `0` disengaged)
- `data[2..3]`: fake speed (`6000`)

### 3.4 CRC Details

- Polynomial: `0x1D`
- Init: `0xFF`
- Final XOR: `0xFF`
- Covers bytes `1..N-1` (CRC stored at byte 0)

## 4. Pin Map and Wiring

### 4.1 ESP32 <-> MCP2515

| MCP2515 Pin | ESP32 Pin | Notes |
|---|---|---|
| VCC | 5V | Module logic supply (board-dependent; many MCP2515 modules are 5V-powered) |
| GND | GND | Common ground required |
| CS | GPIO5 | SPI chip select |
| INT | GPIO15 | Interrupt output from MCP2515 |
| SCK | GPIO18 | SPI clock |
| MISO | GPIO19 | SPI MISO |
| MOSI | GPIO23 | SPI MOSI |
| CANH | CAN bus H | To EPS CAN network |
| CANL | CAN bus L | To EPS CAN network |

### 4.2 ESP32 <-> BTS7960 (single board)

| BTS7960 Pin | ESP32 Pin | Notes |
|---|---|---|
| RPWM | GPIO25 | Right-side PWM command |
| LPWM | GPIO26 | Left-side PWM command |
| R_EN | GPIO27 | Right-side enable (driven HIGH in firmware) |
| L_EN | GPIO14 | Left-side enable (driven HIGH in firmware) |
| VCC | 5V | Logic supply for BTS board |
| GND | GND | Must share ground with ESP32 and motor supply |
| B+ | Motor battery +12V | High-current motor supply, not ESP32 5V |
| B- | Motor battery GND | High-current return path |

Enable behavior in code:

- `R_EN` (GPIO27) is set `HIGH` at startup.
- `L_EN` (GPIO14) is set `HIGH` at startup.
- Assist is controlled by PWM command and safety logic; enable pins stay asserted unless firmware is changed.

### 4.3 Encoders

Motor 1:

- A: GPIO34
- B: GPIO35

Motor 2:

- A: GPIO36
- B: GPIO39

Important electrical note:

- GPIO34/35/36/39 are input-only on ESP32.
- These pins do not provide internal pullups.
- Use external pullup resistors on encoder channels.

### 4.3.1 N25 6-Wire Motor/Encoder Wiring (per motor)

Typical 6-wire N25 with encoder has:

- 2 motor power wires (for brushed motor)
- 4 encoder wires (`VCC`, `GND`, `A`, `B`)

For this project (two motors):

Motor 1:

- Motor leads -> BTS7960 motor output pair (`M+`, `M-`)
- Encoder `A` -> GPIO34
- Encoder `B` -> GPIO35
- Encoder `VCC` -> 3.3V (preferred for direct ESP32 IO compatibility)
- Encoder `GND` -> GND

Motor 2:

- Motor leads -> same BTS7960 motor output pair in parallel with motor 1
- Encoder `A` -> GPIO36
- Encoder `B` -> GPIO39
- Encoder `VCC` -> 3.3V (preferred)
- Encoder `GND` -> GND

If motor direction is opposite between the two motors:

- swap the two motor power wires on one motor (or invert encoder phase mapping).

### 4.3.2 Wire Color Warning

N25 wire colors are not universal across vendors.

- Do not trust color labels blindly.
- Verify motor pair with a multimeter (low resistance pair = motor terminals).
- Verify encoder supply and channels from vendor pinout/datasheet.
- If encoder outputs are 5V push-pull, use level shifting/divider before ESP32 pins.

### 4.4 ESP32 <-> Engage Switch

| Signal | ESP32 Pin | Notes |
|---|---|---|
| Engage switch input | GPIO4 | Configured as `INPUT_PULLUP`, active-low |

Logic:

- Switch open -> GPIO4 reads HIGH -> disengaged state
- Switch closed to GND -> GPIO4 reads LOW -> engaged state

### 4.5 Quick Bench Wiring Diagram

```text
                    USB
PC  --------------------------------->  ESP32 Dev Module
                                           |  |  |  |
                                           |  |  |  +-- GPIO4  <--- Engage switch ---> GND
                                           |  |  |
                                           |  |  +----- SPI -----> MCP2515
                                           |  |          GPIO5  -> CS
                                           |  |          GPIO18 -> SCK
                                           |  |          GPIO19 -> MISO
                                           |  |          GPIO23 -> MOSI
                                           |  |          GPIO15 <- INT
                                           |  |
                                           |  +------------> BTS7960 logic
                                           |               GPIO25 -> RPWM
                                           |               GPIO26 -> LPWM
                                           |               GPIO27 -> R_EN
                                           |               GPIO14 -> L_EN
                                           |
                      Encoder 1 ---------> GPIO34 (A), GPIO35 (B)
                      Encoder 2 ---------> GPIO36 (A), GPIO39 (B)

Motor Power Path (separate from ESP32 USB power):

12V Battery +  -------------------------> BTS7960 B+
12V Battery -  -------------------------> BTS7960 B-
Battery - / Power GND ------------------> ESP32 GND
Battery - / Power GND ------------------> MCP2515 GND

CAN Bus:
MCP2515 CANH ---------------------------> CANH network
MCP2515 CANL ---------------------------> CANL network
```

Important:

- Do not power motor stage from ESP32 5V.
- Use a fused 12V motor supply sized for startup current.
- Ensure all grounds are common before sending PWM.

### 4.6 First Power-On Sequence (Bench)

1. Leave engage switch open (disengaged).
2. Power ESP32 by USB first and verify serial output starts.
3. Power MCP2515 logic and confirm CAN transceiver is alive.
4. Power BTS7960 motor supply last.
5. Verify neutral output at startup (no wheel movement).
6. Send known CAN command stream on 0x22E.
7. Confirm state transitions from startup/timeout to no-fault.
8. Close engage switch only after command stream is stable.
9. Increase torque commands gradually while monitoring encoder mismatch.
10. If any unexpected movement occurs, open engage switch and remove motor power.

## 5. Controller Design

### 5.1 Signal Definitions

- `canTorqueRequest`: signed torque command from CAN
- `targetPosition`: integrated virtual position target
- `targetVelocity`: velocity setpoint from position loop
- `avgPos`: average of both encoder counts
- `velocity`: estimated from `avgPos` delta over `dt`

### 5.2 Outer Loop (Position)

Position target integrator:

```text
posStep = (torque / 512.0) * 20.0
targetPosition += posStep
```

Position control:

```text
posError = targetPosition - avgPos
targetVelocity = kp_pos * posError
```

### 5.3 Inner Loop (Velocity)

```text
velError = targetVelocity - velocity
pwm = kv_vel * velError - kd_damp * velocity
```

Output is constrained to `[-PWM_MAX, +PWM_MAX]`.

### 5.4 H-Bridge Drive Mapping

For signed PWM command:

```text
outR = PWM_CENTER + pwm/2
outL = PWM_CENTER - pwm/2
```

Breakaway compensation:

- Small non-zero commands are raised to `±PWM_BREAKAWAY` to overcome static friction.

## 6. Safety and State Machine

State codes used by this firmware:

- `0`: NO_FAULT
- `1`: FAULT_BAD_CHECKSUM
- `2`: FAULT_SEND
- `3`: FAULT_SCE (reserved)
- `4`: FAULT_STARTUP
- `5`: FAULT_TIMEOUT
- `6`: FAULT_INVALID (reserved)
- `7`: FAULT_COUNTER
- `8`: FAULT_DISENGAGED
- `9`: FAULT_ENCODER_MISMATCH

Safety decisions:

1. Engage switch not active -> force neutral
2. CAN timeout (`MAX_TIMEOUT_MS`) -> force neutral
3. Encoder mismatch (`|enc1-enc2| > ENCODER_MISMATCH_LIMIT`) -> force neutral

Neutral mode behavior:

- Torque request reset to zero
- `steer_ok = false`
- `targetPosition` reset to measured average position to prevent integrator windup
- PWM outputs set to center

## 7. Tunable Parameters

Current defaults in source:

- `kp_pos = 0.18`
- `maxVelocity = 700.0`
- `kv_vel = 0.6`
- `kd_damp = 0.04`
- `PWM_BREAKAWAY = 180`
- `ENCODER_MISMATCH_LIMIT = 300`

Tuning guidance:

1. If oscillation appears around center:
- decrease `kp_pos`
- increase `kd_damp`

2. If response is too slow:
- increase `kv_vel`
- increase `maxVelocity` carefully

3. If motors buzz but do not move:
- increase `PWM_BREAKAWAY`

4. If false mismatch faults occur:
- verify encoder wiring/noise first
- only then adjust `ENCODER_MISMATCH_LIMIT`

## 8. Build and Upload

Arduino IDE / ESP32 core:

- Board: ESP32 Dev Module
- Flash Frequency: 80 MHz
- Partition Scheme: Default
- PSRAM: Disabled

Libraries required:

- `mcp_can`

Upload target file:

- `tests/esp32_dual_n25_eps_controller.ino`

## 9. Bring-Up Checklist

1. Verify 12V motor power is separate from ESP32 5V logic rail.
2. Ensure common ground between battery, BTS7960, MCP2515, ESP32.
3. Confirm MCP2515 crystal is 8 MHz and CAN bitrate set to 500 kbps.
4. Verify CAN termination (typically 120 ohm at each bus end).
5. Confirm encoder channels have external pullups.
6. Boot with motors unloaded first.
7. Check serial output (`115200`) for state transitions.
8. Send known CAN command pattern and verify:
- state transitions to `NO_FAULT`
- torque echo updates in `0x22F`
- `0x22D` engage bit follows switch state

## 10. Troubleshooting

### 10.1 Stuck in timeout state

- No valid `0x22E` command frames are being received.
- Verify CAN ID, bitrate, and counter progression.

### 10.2 Bad checksum faults

- Sender and receiver CRC implementation differ.
- Confirm sender uses same polynomial/init/final XOR and byte coverage.

### 10.3 Counter faults

- Missing frames or repeated frames on command stream.
- Ensure sender increments lower nibble every frame.

### 10.4 Mismatch faults while mechanically linked

- Encoder polarity mismatch or noisy lines.
- Check A/B phase wiring and external pullups.

### 10.5 Motor never develops torque

- Engage switch not active
- Driver enable pins not high
- PWM pins swapped
- Motor supply not present

## 11. Limitations and Next Steps

Current implementation uses one BTS7960 for both motors, so per-motor corrective torque is not possible.

Possible upgrade path:

- move to two independent BTS7960 channels
- keep same CAN interface
- add explicit motor synchronization correction term in PWM split

This yields better dual-motor balancing under asymmetric load.

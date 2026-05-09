/*
 * ============================================================================
 * ESP32 + MCP2515 CAN Bridge for Ocelot Interceptor Core
 * ============================================================================
 * 
 * WHAT THIS DOES:
 *   This ESP32 acts as a bridge between a PC (running the joystick UI) and
 *   the Ocelot Interceptor Core (STM32 on CAN bus). The PC sends simple
 *   serial commands, and this ESP32 converts them into properly formatted
 *   CAN packets with CRC checksums and rolling counters.
 *
 * SYSTEM ARCHITECTURE:
 *   ┌──────────┐    Serial/USB     ┌──────────┐     CAN Bus      ┌─────────────┐
 *   │  PC/UI   │ ← CMD,mag,spd,en →│  ESP32   │← 0x300,0x76,0x301→│ Interceptor │
 *   │(joystick)│    TEL,adc,...     │(this code)│                  │   (STM32)   │
 *   └──────────┘                    └──────────┘                   └─────────────┘
 *
 * HOW THE INTERCEPTOR WORKS:
 *   The interceptor sits between the car's torque sensor and the EPS ECU.
 *   - RELAY OFF: car's torque sensor → EPS directly (normal driving)
 *   - RELAY ON:  interceptor's DAC output → EPS (joystick controls steering)
 *   The relay is controlled by the "enable" bit in the CAN packet.
 *
 * SERIAL PROTOCOL (PC ↔ ESP32):
 *   PC → ESP32:  "CMD,{magnitude},{speed_kph},{enable}\n"
 *     - magnitude: -400 to +400 (steering force, + = right, - = left)
 *     - speed_kph: 0 to 140 (simulated vehicle speed)
 *     - enable:    0 or 1 (0 = relay OFF/safe, 1 = relay ON/controlling)
 *
 *   ESP32 → PC:  "TEL,{adc0},{adc1},{override},{fault},{counter},{relay}\n"
 *     - adc0/adc1:  actual torque sensor readings (12-bit, 0-4095)
 *     - override:   1 if driver is physically fighting the steering
 *     - fault:      fault code (0 = OK, see fault table below)
 *     - counter:    rolling packet counter (0-15)
 *     - relay:      derived relay state (1 if fault==0 AND enable==1)
 *
 *   PC → ESP32:  "CAL\n"  (calibration trigger, acknowledged with "[CAL] ACK")
 *
 * CAN PROTOCOL (ESP32 → Interceptor):
 * 
 *   STEER COMMAND (ID: 0x300, DLC: 6 bytes):
 *   ┌──────┬─────────┬─────────┬─────────┬─────────┬──────────────────┐
 *   │ [0]  │  [1]    │  [2]    │  [3]    │  [4]    │      [5]         │
 *   │ CRC8 │ val0_lo │ val0_hi │ val1_lo │ val1_hi │(enable<<7)|count │
 *   └──────┴─────────┴─────────┴─────────┴─────────┴──────────────────┘
 *   - Firmware computes: magnitude = val0 - val1
 *   - We encode: val0 = 2048 + mag/2, val1 = 2048 - mag/2
 *   - This ensures |val0 - val1| = |magnitude| (the 2048 base is arbitrary)
 *   - Firmware REJECTS packets where |magnitude| > 400 (zeros output)
 *   - enable bit (bit 7 of byte[5]): 1 = relay ON, 0 = relay OFF
 *   - counter (bits 3:0 of byte[5]): must increment by 1 each packet
 *
 *   SPEED (ID: 0x76, DLC: 8 bytes):
 *   ┌──────┬──────┬──────┬──────┬──────┬──────────┬──────────┬─────────┐
 *   │ [0]  │ [1]  │ [2]  │ [3]  │ [4]  │   [5]    │   [6]    │  [7]    │
 *   │ CRC8 │  0   │  0   │  0   │  0   │ speed_lo │ speed_hi │ counter │
 *   └──────┴──────┴──────┴──────┴──────┴──────────┴──────────┴─────────┘
 *   - speed = kph × 100 (e.g., 60 kph = 6000)
 *   - Used by firmware's torque LUT to reduce max force at higher speeds
 *   - If no speed packet for 300 ticks → FAULT_TIMEOUT_VSS
 *
 * CAN PROTOCOL (Interceptor → ESP32):
 *
 *   TELEMETRY (ID: 0x301, DLC: 8 bytes):
 *   ┌──────┬─────────┬─────────┬─────────┬─────────┬──────────┬──────┬────────────────┐
 *   │ [0]  │  [1]    │  [2]    │  [3]    │  [4]    │   [5]    │ [6]  │     [7]        │
 *   │ CRC8 │ adc0_lo │ adc0_hi │ adc1_lo │ adc1_hi │ override │  0   │(state<<4)|idx  │
 *   └──────┴─────────┴─────────┴─────────┴─────────┴──────────┴──────┴────────────────┘
 *   - adc0/adc1: real-time torque sensor readings
 *   - override: 1 if driver torque exceeds threshold (physical hand-turn)
 *   - state (upper nibble of [7]): fault code
 *   - idx (lower nibble of [7]): rolling packet index
 *
 * CRC8 ALGORITHM:
 *   - Polynomial: 0x1D (SAE J1850)
 *   - Init value: 0xFF
 *   - Final XOR:  0xFF
 *   - Scope: bytes[1] through bytes[len-1] (byte[0] stores the CRC itself)
 *   - EVERY packet (TX and RX) uses CRC. No CRC = FAULT_BAD_CHECKSUM.
 *
 * FAULT CODES (from interceptor firmware):
 *   0  = NO_FAULT          (system healthy)
 *   1  = FAULT_STARTUP     (initial state, not yet configured)
 *   2  = FAULT_SENSOR      (ADC/DAC hardware failure)
 *   3  = FAULT_SEND        (CAN TX mailbox full)
 *   4  = FAULT_SCE         (safety check error)
 *   5  = FAULT_TIMEOUT     (no 0x300 packet for ~1 second)
 *   6  = FAULT_BAD_CHECKSUM(CRC mismatch in received packet)
 *   7  = FAULT_INVALID_CKSUM (non-zero values sent while enable=0)
 *   8  = FAULT_REQ_TOO_HIGH  (requested torque exceeds limits)
 *   9  = FAULT_REQ_INVALID   (invalid request format)
 *   10 = FAULT_ADC_UNCONFIGURED (flash not programmed with ADC centers)
 *   11 = FAULT_TIMEOUT_VSS (no speed signal for ~0.4 seconds)
 *
 * SAFETY LAYERS:
 *   1. ESP32 serial watchdog: no CMD for 200ms → zero steer + disable
 *   2. Interceptor CAN watchdog: no 0x300 for 700 ticks → FAULT → relay OFF
 *   3. Interceptor VSS watchdog: no 0x76 for 300 ticks → FAULT → relay OFF
 *   4. Firmware magnitude limit: |mag| > 400 → output zeroed
 *   5. Firmware torque LUT: reduces max force at higher speeds
 *   6. Driver override detection: if driver turns wheel hard → override flag
 *   7. CRC on every packet: corrupted data → FAULT → relay OFF
 *   8. Rolling counter: missed/replayed packets detected
 *
 * HARDWARE WIRING:
 *   ESP32 GPIO5  → MCP2515 CS (chip select)
 *   ESP32 GPIO18 → MCP2515 SCK (SPI clock)
 *   ESP32 GPIO19 → MCP2515 MISO (SPI data in)
 *   ESP32 GPIO23 → MCP2515 MOSI (SPI data out)
 *   ESP32 GPIO2  → Error LED (active high, optional)
 *   MCP2515 CAN_H/CAN_L → vehicle CAN bus (500 kbps)
 *   MCP2515 crystal: 8 MHz
 *
 * REQUIRED LIBRARIES:
 *   - mcp2515 by autowp (https://github.com/autowp/arduino-mcp2515)
 *   Install via Arduino Library Manager or PlatformIO
 */

#include <SPI.h>
#include <mcp2515.h>

// =========================================================
// PIN DEFINITIONS
// =========================================================
#define MCP_CS   5      // MCP2515 chip select (directly connects to CS pin)
#define MCP_SCK  18     // SPI clock
#define MCP_MISO 19     // SPI data: MCP2515 → ESP32
#define MCP_MOSI 23     // SPI data: ESP32 → MCP2515
#define LED_ERR  2      // Onboard LED used as error indicator

// =========================================================
// CAN ADDRESSES
// These MUST match the interceptor firmware (common.h):
//   #define CAN_DIFFERENTIAL_INPUT  0x300
//   #define CAN_DIFFERENTIAL_OUTPUT 0x301U
// Speed address 0x76 is also hardcoded in firmware.
// =========================================================
#define CAN_STEER_INPUT   0x300   // We send steer commands TO interceptor
#define CAN_SPEED_INPUT   0x76    // We send speed info TO interceptor
#define CAN_STEER_OUTPUT  0x301   // We receive telemetry FROM interceptor

// =========================================================
// SAFETY LIMITS
// =========================================================
#define MAX_MAGNITUDE     400     // Firmware hard limit: |val0-val1| > 400 → zeroed
#define MAX_SPEED_KPH     140     // Maximum speed value we'll accept
#define CMD_TIMEOUT_MS    200     // If no serial CMD for this long → emergency disable

// =========================================================
// CRC8 LOOKUP TABLE
// 
// The interceptor firmware uses CRC8 with polynomial 0x1D (SAE J1850).
// We pre-compute a 256-byte lookup table at startup for fast CRC calculation.
// This MUST match the firmware's gen_crc_lookup_table() and lut_checksum().
// =========================================================
uint8_t crc8_lut[256];

// Generate the CRC8 lookup table. Called once in setup().
// This is identical to the firmware's gen_crc_lookup_table(0x1D, crc8_lut_1d).
void gen_crc8_table(uint8_t poly) {
  for (uint16_t i = 0; i < 256; i++) {
    uint8_t crc = (uint8_t)i;
    for (uint8_t j = 0; j < 8; j++) {
      if (crc & 0x80)
        crc = (crc << 1) ^ poly;
      else
        crc <<= 1;
    }
    crc8_lut[i] = crc;
  }
}

// Calculate CRC8 over a packet, matching firmware's lut_checksum().
// IMPORTANT: Skips byte[0] (where CRC will be stored), CRCs bytes[1..len-1].
// Init=0xFF, final XOR=0xFF.
uint8_t calc_crc8(uint8_t *dat, uint8_t len) {
  uint8_t crc = 0xFF;                  // Initial value
  for (uint8_t i = 1; i < len; i++) {  // Skip byte[0], start from byte[1]
    crc ^= dat[i];
    crc = crc8_lut[crc];               // Table lookup (equivalent to 8 bit shifts)
  }
  return crc ^ 0xFF;                   // Final XOR
}

// =========================================================
// MCP2515 CAN CONTROLLER
// =========================================================
MCP2515 mcp2515(MCP_CS);
struct can_frame txMsg;
struct can_frame rxMsg;

// =========================================================
// CONTROL STATE (updated by serial commands from PC)
// =========================================================
int16_t cmd_steer = 0;       // Steering magnitude: -400 to +400
                              // Positive = steer right, Negative = steer left
                              // This becomes (val0 - val1) in the CAN packet
uint16_t cmd_speed = 0;      // Vehicle speed in kph (0..140)
                              // Multiplied by 100 for CAN (firmware expects kph*100)
bool cmd_enable = false;     // Engage/disengage relay
                              // true  = relay ON, interceptor controls EPS
                              // false = relay OFF, car's own torque sensor active

uint8_t counter_steer = 0;  // Rolling counter for 0x300 (increments 0..15, wraps)
                              // Firmware checks: must be (previous + 1) & 0xF
uint8_t counter_speed = 0;  // Rolling counter for 0x76 (independent from steer)

// =========================================================
// STATUS TRACKING
// =========================================================
uint32_t tx_count = 0;        // Total CAN frames sent successfully
uint32_t rx_count = 0;        // Total telemetry frames received
uint8_t send_fail_count = 0;  // Consecutive CAN send failures (triggers recovery)
unsigned long last_cmd_time = 0;  // Timestamp of last serial CMD (for watchdog)
unsigned long last_rx_time = 0;   // Timestamp of last CAN RX (for health monitoring)

bool led_state = false;
unsigned long last_blink = 0;

// =========================================================
// TELEMETRY (last received from interceptor on 0x301)
// =========================================================
uint16_t tel_adc0 = 0;      // Torque sensor channel 0 (12-bit: 0-4095)
uint16_t tel_adc1 = 0;      // Torque sensor channel 1 (12-bit: 0-4095)
uint8_t tel_override = 0;   // Driver override flag (1 = driver turning wheel hard)
uint8_t tel_fault = 0;      // Fault state from interceptor (0 = healthy)
uint8_t tel_pkt_idx = 0;    // Packet index from interceptor (0-15, rolling)

// =========================================================
// CAN INITIALIZATION AND RECOVERY
// =========================================================

// Initialize the MCP2515 CAN controller.
// Sets 500kbps bitrate (standard automotive CAN speed).
// MCP_8MHZ = crystal frequency on MCP2515 module.
void canInit() {
  mcp2515.reset();
  delay(10);  // Wait for MCP2515 internal reset
  mcp2515.setBitrate(CAN_500KBPS, MCP_8MHZ);  // Match your crystal!
  mcp2515.setNormalMode();  // Enable TX and RX
  send_fail_count = 0;
  Serial.println("[CAN] Initialized");
}

// Recovery: called when too many TX failures occur.
// Resets the MCP2515 and re-initializes. This clears any bus-off state.
void canRecover() {
  Serial.println("[CAN] Recovering...");
  canInit();
}

// =========================================================
// SEND STEER COMMAND (0x300)
//
// This is the main control packet. Sent every 20ms (50 Hz).
// The interceptor uses this to:
//   1. Compute steering magnitude (val0 - val1)
//   2. Apply torque LUT scaling based on vehicle speed
//   3. Drive DAC outputs to control EPS
//   4. Control relay (via enable bit)
//
// ENCODING:
//   We want to send magnitude M where M = val0 - val1.
//   We use 2048 as an arbitrary base (firmware ignores absolute values):
//     val0 = 2048 + M/2
//     val1 = 2048 - (M - M/2)    ← handles odd M correctly
//   This guarantees val0 - val1 == M exactly.
//
// COUNTER:
//   Firmware expects counter to increment by 1 each packet.
//   If it doesn't match (previous+1)&0xF, the packet is silently dropped.
//   This prevents replayed/delayed packets from being accepted.
// =========================================================
void sendSteer() {
  // Clamp magnitude to firmware's absolute safety limit
  int16_t mag = constrain(cmd_steer, -MAX_MAGNITUDE, MAX_MAGNITUDE);

  // When disabling, firmware requires val0=0 AND val1=0 exactly.
  // Sending any non-zero value with enable=0 triggers FAULT_INVALID_CKSUM.
  uint16_t val0, val1;
  if (!cmd_enable) {
    val0 = 0;
    val1 = 0;
  } else {
    // Encode into val0/val1 pair (firmware only uses the difference)
    val0 = (uint16_t)(2048 + mag / 2);
    val1 = (uint16_t)(2048 - (mag - mag / 2));
  }

  // Build the 6-byte CAN frame
  uint8_t dat[6];
  dat[0] = 0;                    // Placeholder — CRC goes here after computation
  dat[1] = val0 & 0xFF;          // val0 low byte
  dat[2] = (val0 >> 8) & 0xFF;   // val0 high byte
  dat[3] = val1 & 0xFF;          // val1 low byte
  dat[4] = (val1 >> 8) & 0xFF;   // val1 high byte
  dat[5] = (cmd_enable ? 0x80 : 0x00) | (counter_steer & 0x0F);
  //         ^^^^^^^^                     ^^^^^^^^^^^^^^^^^^^^
  //         bit 7 = enable (relay)       bits 3:0 = rolling counter

  // Compute CRC8 over bytes[1..5], result stored in byte[0]
  dat[0] = calc_crc8(dat, 6);

  // Send via MCP2515
  txMsg.can_id = CAN_STEER_INPUT;  // 0x300
  txMsg.can_dlc = 6;                // 6 bytes (NOT 8!)
  memcpy(txMsg.data, dat, 6);

  if (mcp2515.sendMessage(&txMsg) == MCP2515::ERROR_OK) {
    tx_count++;
    send_fail_count = 0;
  } else {
    send_fail_count++;
  }

  // Increment counter (wraps 0→1→2→...→15→0)
  counter_steer = (counter_steer + 1) & 0x0F;

  // If too many consecutive failures, MCP2515 may be in bus-off → recover
  if (send_fail_count > 10) {
    canRecover();
  }
}

// =========================================================
// SEND SPEED FRAME (0x76)
//
// Tells the interceptor the current vehicle speed.
// The firmware uses this for:
//   1. Torque LUT scaling (less force allowed at higher speeds)
//   2. VSS timeout detection (no speed → FAULT_TIMEOUT_VSS)
//
// Speed is sent as kph × 100 (integer). E.g., 60 kph = 6000.
// The firmware divides by 100 to get the LUT index.
//
// IMPORTANT: Even if speed is 0, you MUST keep sending this packet.
// If the firmware doesn't receive 0x76 for 300 ticks (~0.4s), it faults.
// =========================================================
void sendSpeed() {
  // Convert kph to firmware's format (kph * 100)
  uint16_t speed_raw = constrain(cmd_speed, 0, MAX_SPEED_KPH) * 100;

  // Build 8-byte CAN frame
  uint8_t dat[8];
  memset(dat, 0, 8);               // Clear all bytes
  dat[0] = 0;                      // Placeholder for CRC
  dat[5] = speed_raw & 0xFF;       // Speed low byte
  dat[6] = (speed_raw >> 8) & 0xFF; // Speed high byte
  dat[7] = counter_speed & 0x0F;   // Rolling counter

  // CRC over bytes[1..7]
  dat[0] = calc_crc8(dat, 8);

  // Send via MCP2515
  txMsg.can_id = CAN_SPEED_INPUT;  // 0x76
  txMsg.can_dlc = 8;               // 8 bytes
  memcpy(txMsg.data, dat, 8);

  mcp2515.sendMessage(&txMsg);  // No error tracking for speed (non-critical)

  counter_speed = (counter_speed + 1) & 0x0F;
}

// =========================================================
// READ TELEMETRY FROM INTERCEPTOR (0x301)
//
// The interceptor sends this at ~732 Hz (every TIM3 tick).
// Contains:
//   - Real-time ADC readings of the car's actual torque sensor
//   - Override flag (driver physically fighting the joystick)
//   - Fault state (0 = healthy, anything else = problem)
//   - Packet index (rolling counter, for debugging)
//
// We verify the CRC before trusting the data.
// We then format it as a TEL line and send to PC via serial.
//
// RELAY STATE DERIVATION:
//   The interceptor does NOT explicitly send relay state on CAN.
//   Relay = (fault == 0) AND (we are sending enable == 1).
//   We know both of these, so we can derive it reliably.
// =========================================================
void readTelemetry() {
  while (mcp2515.readMessage(&rxMsg) == MCP2515::ERROR_OK) {
    // Only process 0x301 telemetry frames with expected length
    if (rxMsg.can_id == CAN_STEER_OUTPUT && rxMsg.can_dlc == 8) {
      last_rx_time = millis();
      rx_count++;

      // Verify CRC integrity (same algorithm as TX)
      // Firmware computes CRC over bytes[1..5] with len=6
      uint8_t expected_crc = calc_crc8(rxMsg.data, 6);
      if (rxMsg.data[0] != expected_crc) {
        continue;  // Corrupted frame — discard silently
      }

      // Parse telemetry fields
      tel_adc0 = rxMsg.data[1] | (rxMsg.data[2] << 8);      // 16-bit ADC ch0
      tel_adc1 = rxMsg.data[3] | (rxMsg.data[4] << 8);      // 16-bit ADC ch1
      tel_override = rxMsg.data[5];                           // Override flag
      tel_fault = (rxMsg.data[7] >> 4) & 0x0F;               // Upper nibble = fault
      tel_pkt_idx = rxMsg.data[7] & 0x0F;                    // Lower nibble = counter

      // Derive relay state (not explicitly in packet)
      // Relay is ON only when: no fault AND we're commanding enable
      uint8_t relay = (tel_fault == 0 && cmd_enable) ? 1 : 0;

      // Send formatted telemetry to PC (Python UI parses this)
      Serial.printf("TEL,%u,%u,%u,%u,%u,%u\n",
                    tel_adc0, tel_adc1, tel_override,
                    tel_fault, tel_pkt_idx, relay);
    }
  }
}

// =========================================================
// ERROR LED INDICATOR
//
// Provides visual feedback without needing a serial monitor:
//   - OFF:          Everything healthy
//   - SOLID ON:     Minor CAN errors or interceptor reporting fault
//   - BLINKING:     CAN recovery in progress (bus-off or hardware issue)
// =========================================================
void updateLed() {
  if (send_fail_count == 0 && tel_fault == 0) {
    digitalWrite(LED_ERR, LOW);       // All good
  } else if (send_fail_count <= 10) {
    digitalWrite(LED_ERR, HIGH);      // Warning
  } else {
    // Fast blink = critical (recovery happening)
    if (millis() - last_blink >= 200) {
      last_blink = millis();
      led_state = !led_state;
      digitalWrite(LED_ERR, led_state);
    }
  }
}

// =========================================================
// SERIAL COMMAND PARSER
//
// Reads lines from USB serial and updates control state.
// Format: "CMD,{steer},{speed},{enable}\n"
// Also handles: "CAL\n" for calibration acknowledgment.
//
// sscanf is used for parsing — it's safe here because:
//   - Input is from USB serial (not network/untrusted)
//   - Values are constrained immediately after parsing
// =========================================================
void handleSerial() {
  if (!Serial.available()) return;

  String line = Serial.readStringUntil('\n');
  line.trim();

  if (line == "CAL") {
    // Calibration: acknowledge to PC. Actual calibration uses ADC telemetry.
    Serial.println("[CAL] ACK");
  }
  else if (line.startsWith("CMD,")) {
    int s, sp, en;
    if (sscanf(line.c_str(), "CMD,%d,%d,%d", &s, &sp, &en) == 3) {
      cmd_steer = constrain(s, -MAX_MAGNITUDE, MAX_MAGNITUDE);
      cmd_speed = constrain(sp, 0, MAX_SPEED_KPH);
      cmd_enable = (en != 0);
      last_cmd_time = millis();  // Reset watchdog timer
    }
  }
}

// =========================================================
// SETUP — runs once at power-on
// =========================================================
void setup() {
  Serial.begin(115200);
  pinMode(LED_ERR, OUTPUT);
  digitalWrite(LED_ERR, LOW);

  // Initialize SPI bus for MCP2515 communication
  SPI.begin(MCP_SCK, MCP_MISO, MCP_MOSI, MCP_CS);

  // Pre-compute CRC8 lookup table (must happen before any CAN communication)
  gen_crc8_table(0x1D);  // Polynomial 0x1D (SAE J1850)

  // Initialize MCP2515 CAN controller
  canInit();

  last_cmd_time = millis();
  Serial.println("ESP32 CAN Bridge Ready");
}

// =========================================================
// MAIN LOOP — runs at 50 Hz (20ms cycle)
//
// Execution order matters:
//   1. Parse serial first (get latest commands)
//   2. Check watchdog (safety: zero outputs if PC disconnected)
//   3. Send CAN (apply commands to interceptor)
//   4. Read CAN (get telemetry back)
//   5. Update LED (visual feedback)
//
// The 20ms delay gives a consistent 50 Hz rate which matches
// the UI's control loop frequency. The interceptor's CAN timeout
// is 700 ticks at ~732 Hz ≈ 0.96 seconds, so 50 Hz is well within spec.
// =========================================================
void loop() {
  // 1. Parse any incoming serial commands from PC
  handleSerial();

  // 2. SAFETY: Serial watchdog
  //    If no CMD received for 200ms, assume PC crashed or cable disconnected.
  //    Zero everything and disengage → interceptor will see enable=0 → relay OFF.
  if (millis() - last_cmd_time > CMD_TIMEOUT_MS) {
    cmd_steer = 0;
    cmd_speed = 0;
    cmd_enable = false;  // CRITICAL: disengage relay on timeout
  }

  // 3. Send control CAN frames to interceptor
  sendSteer();   // 0x300: steering magnitude + enable + counter
  sendSpeed();   // 0x76:  vehicle speed + counter

  // 4. Read telemetry from interceptor and forward to PC
  readTelemetry();  // 0x301: ADC, override, fault, counter

  // 5. Update error LED
  updateLed();

  // 50 Hz loop rate (20ms per cycle)
  delay(20);
}

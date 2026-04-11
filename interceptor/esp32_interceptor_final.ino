/*
 * ESP32 + MCP2515 CAN Bus Interceptor
 * Final Safe Firmware with Serial Watchdog
 * 
 * Pair with Python GUI that sends "CMD,steer,speed" at 50 Hz.
 * 
 * Hardware:
 *   MCP2515 CS  -> GPIO5
 *   SCK         -> GPIO18
 *   MISO        -> GPIO19
 *   MOSI        -> GPIO23
 *   Error LED   -> GPIO2 (active high)
 * 
 * CAN bitrate: 500 kbps, assuming 8 MHz crystal on MCP2515.
 *              If your module uses 16 MHz, change MCP_8MHZ to MCP_16MHZ.
 */

#include <SPI.h>
#include <mcp2515.h>
#include <stdlib.h>

// =========================================================
// PIN DEFINITIONS
// =========================================================
#define MCP_CS   5
#define MCP_SCK  18
#define MCP_MISO 19
#define MCP_MOSI 23
#define LED_ERR  2

// =========================================================
// WATCHDOG CONFIGURATION
// =========================================================
const unsigned long CMD_TIMEOUT_MS = 200;   // Zero outputs if no command for 200ms

// =========================================================
// MCP2515 OBJECT
// =========================================================
MCP2515 mcp2515(MCP_CS);

// =========================================================
// CAN FRAMES
// =========================================================
struct can_frame txMsg;   // Transmit buffer
struct can_frame rxMsg;   // Receive buffer

// =========================================================
// CONTROL STATE
// =========================================================
int steer = 0;      // Steering torque (-2048..2047)
int speed = 0;      // Speed command (0..655, will be *100 before sending)

// =========================================================
// STATUS & TELEMETRY
// =========================================================
uint8_t counter = 0;          // Rolling counter (0..15) for CAN frames
uint32_t tx_count = 0;        // Successful CAN sends
uint32_t rx_count = 0;        // Received telemetry frames
uint8_t send_fail_count = 0;  // Consecutive send failures

bool led_state = false;
unsigned long last_blink = 0;
unsigned long last_cmd_time = 0;

// =========================================================
// FUNCTION DECLARATIONS
// =========================================================
void canRecover();
void sendTorque();
void sendSpeed();
void readTelemetry();
void updateErrorLed();

// =========================================================
// MCP2515 RECOVERY (reset and reconfigure)
// =========================================================
void canRecover() {
  mcp2515.reset();
  delay(10);
  // CRITICAL: Set correct crystal frequency (8MHz or 16MHz)
  // Change MCP_8MHZ to MCP_16MHZ if your module has a 16 MHz crystal.
  mcp2515.setBitrate(CAN_500KBPS, MCP_8MHZ);
  mcp2515.setNormalMode();
  send_fail_count = 0;   // Reset failure counter after recovery
}

// =========================================================
// SEND TORQUE COMMAND (CAN ID 0x220)
// Data format: center-based steering (2048 ± steer), enable bit + counter
// =========================================================
void sendTorque() {
  // Clamp steering to safe 12-bit range (prevents overflow)
  int clamped_steer = constrain(steer, -2048, 2047);

  uint16_t center = 2048;
  uint16_t ch0 = center + clamped_steer;   // Right channel
  uint16_t ch1 = center - clamped_steer;   // Left channel

  txMsg.can_id = 0x220;
  txMsg.can_dlc = 8;
  memset(txMsg.data, 0, 8);   // Clear all bytes

  // Little-endian packing
  txMsg.data[1] = ch0 & 0xFF;
  txMsg.data[2] = ch0 >> 8;
  txMsg.data[3] = ch1 & 0xFF;
  txMsg.data[4] = ch1 >> 8;

  // Enable bit (0x80) + rolling counter (lower 4 bits)
  txMsg.data[5] = 0x80 | (counter & 0x0F);

  // Attempt to send
  if (mcp2515.sendMessage(&txMsg) == MCP2515::ERROR_OK) {
    tx_count++;
    send_fail_count = 0;   // Success resets failure counter
  } else {
    send_fail_count++;
  }

  // If too many consecutive failures, recover the MCP2515
  if (send_fail_count > 10) {
    canRecover();
  }
}

// =========================================================
// SEND SPEED COMMAND (CAN ID 0x76)
// Data format: speed*100 in bytes 5-6, counter in byte 7
// =========================================================
void sendSpeed() {
  // Clamp speed to max 655 (655 * 100 = 65500 fits in 16 bits)
  uint16_t sp = constrain(speed, 0, 655) * 100;

  txMsg.can_id = 0x76;
  txMsg.can_dlc = 8;
  memset(txMsg.data, 0, 8);   // Clear previous data

  // Little-endian speed value
  txMsg.data[5] = sp & 0xFF;
  txMsg.data[6] = sp >> 8;
  txMsg.data[7] = counter & 0x0F;   // Lower 4 bits of counter

  // Send (no error checking for speed frame – less critical)
  mcp2515.sendMessage(&txMsg);
}

// =========================================================
// READ TELEMETRY (CAN ID 0x221)
// Outputs CSV line: TEL,adc0,adc1,override_flag,fault,counter,relay
// =========================================================
void readTelemetry() {
  // Read all pending messages to avoid buffer overflow
  while (mcp2515.readMessage(&rxMsg) == MCP2515::ERROR_OK) {
    if (rxMsg.can_id == 0x221) {
      rx_count++;

      // Extract ADC values (little-endian)
      uint16_t adc0 = rxMsg.data[1] | (rxMsg.data[2] << 8);
      uint16_t adc1 = rxMsg.data[3] | (rxMsg.data[4] << 8);

      uint8_t override_flag = rxMsg.data[5];
      uint8_t fault = (rxMsg.data[7] >> 4) & 0x0F;   // Upper nibble of byte 7

      // Relay control: engage if no fault and steering torque is applied
      uint8_t relay = (fault == 0 && abs(steer) > 0) ? 1 : 0;

      // Send telemetry to Serial (for Python GUI)
      Serial.printf("TEL,%u,%u,%u,%u,%u,%u\n",
                    adc0, adc1, override_flag, fault, counter, relay);
    }
  }
}

// =========================================================
// ERROR LED INDICATOR
// - OFF:           No errors
// - Solid ON:      1-10 consecutive send failures
// - Blink (5 Hz):  >10 failures (recovery mode active)
// =========================================================
void updateErrorLed() {
  if (send_fail_count == 0) {
    digitalWrite(LED_ERR, LOW);
    led_state = false;
  }
  else if (send_fail_count <= 10) {
    digitalWrite(LED_ERR, HIGH);
    led_state = true;
  }
  else {
    unsigned long now = millis();
    if (now - last_blink >= 200) {   // 200ms = 5 Hz
      last_blink = now;
      led_state = !led_state;
      digitalWrite(LED_ERR, led_state);
    }
  }
}

// =========================================================
// SETUP: Serial, SPI, MCP2515, LED
// =========================================================
void setup() {
  Serial.begin(115200);

  pinMode(LED_ERR, OUTPUT);
  digitalWrite(LED_ERR, LOW);

  SPI.begin(MCP_SCK, MCP_MISO, MCP_MOSI, MCP_CS);

  canRecover();   // Initialize MCP2515

  // Initialise watchdog timer
  last_cmd_time = millis();
}

// =========================================================
// MAIN LOOP (50 Hz)
// 1. Read serial commands (CMD,steer,speed)
// 2. Serial watchdog: zero outputs if command timeout
// 3. Send CAN frames (torque + speed)
// 4. Read incoming telemetry
// 5. Update counters and error LED
// =========================================================
void loop() {
  // ---------- Serial Command Input ----------
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    if (line.startsWith("CMD,")) {
      int s, sp;
      if (sscanf(line.c_str(), "CMD,%d,%d", &s, &sp) == 2) {
        steer = constrain(s, -2048, 2047);
        speed = constrain(sp, 0, 655);
        // Refresh watchdog timer
        last_cmd_time = millis();
      }
    }
  }

  // ---------- Serial Watchdog Fail-Safe ----------
  if (millis() - last_cmd_time > CMD_TIMEOUT_MS) {
    steer = 0;
    speed = 0;
    // Note: watchdog does not reset last_cmd_time, so zeros persist
    // until a new command arrives.
  }

  // ---------- CAN Communication ----------
  sendTorque();      // Send steering torque command
  sendSpeed();       // Send speed command
  readTelemetry();   // Process incoming telemetry

  // ---------- Update Counters and LED ----------
  counter = (counter + 1) & 0x0F;   // Rolling counter 0..15
  updateErrorLed();

  // ---------- 50 Hz Timing ----------
  delay(20);   // 20 ms = 50 Hz
}

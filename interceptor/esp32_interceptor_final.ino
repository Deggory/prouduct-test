/*
 * ESP32 + MCP2515 CAN Bus Interceptor
 * - Sends torque command (ID 0x220) and speed command (ID 0x76)
 * - Receives telemetry (ID 0x221)
 * - Includes CAN recovery and error LED feedback
 */

#include <SPI.h>
#include <mcp2515.h>
#include <stdlib.h>   // for abs() and constrain()

// ========== ESP32 VSPI Pin Definitions ==========
#define MCP_CS   5   // Chip Select for MCP2515
#define MCP_SCK  18  // SPI Clock
#define MCP_MISO 19  // Master In Slave Out
#define MCP_MOSI 23  // Master Out Slave In

// ========== Error LED Pin ==========
#define LED_ERR  2   // Built-in LED on many ESP32 boards (active high)

// ========== CAN Object ==========
MCP2515 mcp2515(MCP_CS);

// ========== CAN Frames ==========
struct can_frame txMsg;   // Transmit buffer
struct can_frame rxMsg;   // Receive buffer

// ========== Command Values ==========
int steer = 0;            // Steering torque (-2048..2047)
int speed = 0;            // Speed command (0..655, will be multiplied by 100)

// ========== Counters & Status ==========
uint8_t counter = 0;           // Rolling counter (0..15) for CAN messages
uint32_t tx_count = 0;         // Successful sends
uint32_t rx_count = 0;         // Received telemetry frames
uint8_t send_fail_count = 0;   // Consecutive send failures
bool led_state = false;        // Current LED state (for blinking)
unsigned long last_blink = 0;  // Last time LED toggled

// ========== Function Prototypes ==========
void canRecover();
void sendTorque();
void sendSpeed();
void readTelemetry();
void updateErrorLed();

// ------------------------------------------------------------------
// CAN Recovery: Reset MCP2515, reinit bitrate, set normal mode
// ------------------------------------------------------------------
void canRecover() {
  mcp2515.reset();                         // Hardware reset
  delay(10);                               // Wait for reset to complete
  mcp2515.setBitrate(CAN_500KBPS, MCP_8MHZ); // Configure 500 kbps, 8 MHz crystal
  mcp2515.setNormalMode();                 // Enter normal operation mode
  send_fail_count = 0;                     // Reset failure counter after recovery
}

// ------------------------------------------------------------------
// Send Torque Command (CAN ID 0x220)
// Data format: center-based steering (2048 ± steer), plus enable + counter
// ------------------------------------------------------------------
void sendTorque() {
  // Clamp steering value to safe range (prevents overflow of 12-bit ADC)
  int clamped_steer = constrain(steer, -2048, 2047);
  uint16_t center = 2048;
  uint16_t ch0 = center + clamped_steer;   // Channel 0 (right)
  uint16_t ch1 = center - clamped_steer;   // Channel 1 (left)

  // Prepare CAN frame
  txMsg.can_id = 0x220;
  txMsg.can_dlc = 8;
  memset(txMsg.data, 0, 8);               // Clear all data bytes

  // Little-endian packing of ch0 and ch1
  txMsg.data[1] = ch0 & 0xFF;
  txMsg.data[2] = ch0 >> 8;
  txMsg.data[3] = ch1 & 0xFF;
  txMsg.data[4] = ch1 >> 8;

  // Enable bit (0x80) + rolling counter (lower 4 bits)
  txMsg.data[5] = 0x80 | (counter & 0x0F);

  // Attempt to send
  if (mcp2515.sendMessage(&txMsg) == MCP2515::ERROR_OK) {
    tx_count++;            // Increment successful send counter
    send_fail_count = 0;   // Reset failure streak on success
  } else {
    send_fail_count++;     // Increment failure counter
  }

  // If too many consecutive failures, attempt to recover
  if (send_fail_count > 10) {
    canRecover();
  }
}

// ------------------------------------------------------------------
// Send Speed Command (CAN ID 0x76)
// Data format: speed*100 in bytes 5-6, counter in byte 7
// ------------------------------------------------------------------
void sendSpeed() {
  // Clamp speed to max 655 (because 655 * 100 = 65500 fits in 16 bits)
  uint16_t sp = constrain(speed, 0, 655) * 100;

  txMsg.can_id = 0x76;
  txMsg.can_dlc = 8;
  memset(txMsg.data, 0, 8);               // Clear previous data

  // Little-endian speed value
  txMsg.data[5] = sp & 0xFF;
  txMsg.data[6] = sp >> 8;
  txMsg.data[7] = counter & 0x0F;         // Lower 4 bits of counter

  // Send (no error checking needed for this frame per original design)
  mcp2515.sendMessage(&txMsg);
}

// ------------------------------------------------------------------
// Read Telemetry: Process all pending CAN messages
// Expected ID: 0x221 (steering interceptor feedback)
// Outputs CSV line: TEL,adc0,adc1,override_flag,fault,counter,relay
// ------------------------------------------------------------------
void readTelemetry() {
  // Read all available messages (prevents buffer overflow)
  while (mcp2515.readMessage(&rxMsg) == MCP2515::ERROR_OK) {
    if (rxMsg.can_id == 0x221) {
      rx_count++;   // Count received telemetry frames

      // Extract ADC values (little-endian)
      uint16_t adc0 = rxMsg.data[1] | (rxMsg.data[2] << 8);
      uint16_t adc1 = rxMsg.data[3] | (rxMsg.data[4] << 8);

      uint8_t override_flag = rxMsg.data[5];
      uint8_t fault = (rxMsg.data[7] >> 4) & 0x0F;  // Upper nibble of byte 7

      // Relay control: engage if no fault and steering torque is applied
      uint8_t relay = (fault == 0 && abs(steer) > 0) ? 1 : 0;

      // Output to Serial Monitor (CSV format)
      Serial.printf("TEL,%u,%u,%u,%u,%u,%u\n",
                    adc0, adc1, override_flag, fault, counter, relay);
    }
  }
}

// ------------------------------------------------------------------
// Update Error LED:
// - Solid ON if send_fail_count > 0 (communication problem)
// - Blink fast if send_fail_count > 10 (recovery in progress)
// - OFF if everything OK
// ------------------------------------------------------------------
void updateErrorLed() {
  if (send_fail_count == 0) {
    // No error: LED off
    digitalWrite(LED_ERR, LOW);
    led_state = false;
  } 
  else if (send_fail_count <= 10) {
    // Minor errors: LED solid on
    digitalWrite(LED_ERR, HIGH);
    led_state = true;
  } 
  else {
    // Severe errors (recovery mode): blink at 5 Hz (200ms period)
    unsigned long now = millis();
    if (now - last_blink >= 200) {  // 200 ms = 5 Hz
      last_blink = now;
      led_state = !led_state;
      digitalWrite(LED_ERR, led_state);
    }
  }
}

// ------------------------------------------------------------------
// Setup: Serial, SPI, MCP2515, LED pin
// ------------------------------------------------------------------
void setup() {
  Serial.begin(115200);                     // USB serial for commands and telemetry

  // Configure LED pin
  pinMode(LED_ERR, OUTPUT);
  digitalWrite(LED_ERR, LOW);

  // Initialize SPI with custom ESP32 VSPI pins
  SPI.begin(MCP_SCK, MCP_MISO, MCP_MOSI, MCP_CS);

  // Initialize MCP2515 (reset, set bitrate, normal mode)
  canRecover();
}

// ------------------------------------------------------------------
// Main Loop: 50 Hz execution
// 1. Read serial commands (format: "CMD,steer,speed")
// 2. Send CAN frames
// 3. Read incoming telemetry
// 4. Update counter and error LED
// ------------------------------------------------------------------
void loop() {
  // ---------- Handle Serial Commands ----------
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    if (line.startsWith("CMD,")) {
      int s, sp;
      // Parse two integers from the line
      if (sscanf(line.c_str(), "CMD,%d,%d", &s, &sp) == 2) {
        // Apply bounds before storing
        steer = constrain(s, -2048, 2047);
        speed = constrain(sp, 0, 655);
      }
    }
  }

  // ---------- CAN Communication ----------
  sendTorque();      // Send steering torque command
  sendSpeed();       // Send speed command
  readTelemetry();   // Process incoming telemetry

  // ---------- Update Counters and LED ----------
  counter = (counter + 1) & 0x0F;   // Rolling counter 0..15
  updateErrorLed();                 // Reflect error status on LED

  // ---------- Timing: 50 Hz loop ----------
  delay(20);   // 20 ms = 50 Hz
}

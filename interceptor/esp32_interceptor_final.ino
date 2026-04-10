#include <SPI.h>
#include <mcp2515.h>

// =============================
// VERIFIED ESP32 VSPI PINS
// =============================
#define MCP_CS   5
#define MCP_SCK  18
#define MCP_MISO 19
#define MCP_MOSI 23

MCP2515 mcp2515(MCP_CS);

struct can_frame txMsg;
struct can_frame rxMsg;

int steer = 0;
int speed = 0;

uint8_t counter = 0;

uint32_t tx_count = 0;
uint32_t rx_count = 0;
uint8_t send_fail_count = 0;


// =============================
// CAN recovery watchdog
// =============================
void canRecover() {
  mcp2515.reset();
  delay(10);
  mcp2515.setBitrate(CAN_500KBPS, MCP_8MHZ);
  mcp2515.setNormalMode();
}


// =============================
// Send torque command
// =============================
void sendTorque() {
  uint16_t center = 2048;

  uint16_t ch0 = center + steer;
  uint16_t ch1 = center - steer;

  txMsg.can_id = 0x220;
  txMsg.can_dlc = 8;
  memset(txMsg.data, 0, 8);

  txMsg.data[1] = ch0 & 0xFF;
  txMsg.data[2] = ch0 >> 8;
  txMsg.data[3] = ch1 & 0xFF;
  txMsg.data[4] = ch1 >> 8;

  // enable + rolling counter
  txMsg.data[5] = 0x80 | (counter & 0x0F);

  if (mcp2515.sendMessage(&txMsg) == MCP2515::ERROR_OK) {
    tx_count++;
    send_fail_count = 0;
  } else {
    send_fail_count++;
  }

  if (send_fail_count > 10) {
    canRecover();
  }
}


// =============================
// Send speed frame
// =============================
void sendSpeed() {
  uint16_t sp = speed * 100;

  txMsg.can_id = 0x76;
  txMsg.can_dlc = 8;
  memset(txMsg.data, 0, 8);

  txMsg.data[5] = sp & 0xFF;
  txMsg.data[6] = sp >> 8;
  txMsg.data[7] = counter & 0x0F;

  mcp2515.sendMessage(&txMsg);
}


// =============================
// Read interceptor telemetry
// =============================
void readTelemetry() {
  if (mcp2515.readMessage(&rxMsg) == MCP2515::ERROR_OK) {
    if (rxMsg.can_id == 0x221) {
      rx_count++;

      uint16_t adc0 = rxMsg.data[1] | (rxMsg.data[2] << 8);
      uint16_t adc1 = rxMsg.data[3] | (rxMsg.data[4] << 8);

      uint8_t override_flag = rxMsg.data[5];
      uint8_t fault = (rxMsg.data[7] >> 4) & 0x0F;

      uint8_t relay =
          (fault == 0 && abs(steer) > 0) ? 1 : 0;

      Serial.printf(
          "TEL,%u,%u,%u,%u,%u,%u\n",
          adc0,
          adc1,
          override_flag,
          fault,
          counter,
          relay
      );
    }
  }
}


// =============================
// Setup
// =============================
void setup() {
  Serial.begin(115200);

  SPI.begin(MCP_SCK, MCP_MISO, MCP_MOSI, MCP_CS);

  canRecover();
}


// =============================
// Main loop
// =============================
void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');

    if (line.startsWith("CMD,")) {
      sscanf(line.c_str(), "CMD,%d,%d", &steer, &speed);
    }
  }

  sendTorque();
  sendSpeed();
  readTelemetry();

  counter = (counter + 1) & 0x0F;

  delay(20);  // 50 Hz
}

#include <Arduino.h>
#include <SPI.h>
#include <mcp_can.h>

// =====================================================
// ESP32 <-> MCP2515 PIN DEFINITIONS
// Crystal = 8 MHz
// =====================================================
#define CAN_CS   5
#define CAN_INT  4

// VSPI pins on ESP32
#define CAN_SCK  18
#define CAN_MISO 19
#define CAN_MOSI 23

// MCP2515 object
MCP_CAN CAN0(CAN_CS);

// =====================================================
// GLOBAL VARIABLES
// =====================================================
unsigned long rxId = 0;
unsigned char len = 0;
unsigned char rxBuf[8];

int totalSteerAngle = 0;
int steerRate = 0;

unsigned long lastCanRx = 0;

// =====================================================
// OPTIONAL TOYOTA 0x25 DECODER
// =====================================================
void decodeToyotaSteering(const unsigned char *buf) {
  int rawAngle = ((buf[0] & 0x0F) << 8) | buf[1];

  // signed 12-bit
  if (rawAngle & 0x800) rawAngle -= 0x1000;

  int angle = rawAngle * 15; // 1.5 deg * 10

  int frac = (buf[4] >> 4) & 0x0F;
  if (frac > 8) frac -= 16;

  int rawRate = ((buf[4] & 0x0F) << 8) | buf[5];
  if (rawRate & 0x800) rawRate -= 0x1000;

  steerRate = rawRate;
  totalSteerAngle = angle + frac;
}

// =====================================================
// SETUP
// =====================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("Universal Steering CAN Dashboard");

  // Start VSPI bus
  SPI.begin(CAN_SCK, CAN_MISO, CAN_MOSI, CAN_CS);

  // Start MCP2515
  if (CAN0.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ) == CAN_OK) {
    Serial.println("MCP:OK");
  } else {
    Serial.println("MCP:FAIL");
    while (1);
  }

  CAN0.setMode(MCP_NORMAL);

  pinMode(CAN_INT, INPUT);

  Serial.println("CAN Sniffer Ready");
}

// =====================================================
// MAIN LOOP
// =====================================================
void loop() {
  bool can_alive = (millis() - lastCanRx) < 1000;

  // New CAN frame available
  if (digitalRead(CAN_INT) == LOW) {
    if (CAN0.readMsgBuf(&rxId, &len, rxBuf) == CAN_OK) {

      lastCanRx = millis();

      // -------------------------------
      // UNIVERSAL CAN SNIFFER OUTPUT
      // -------------------------------
      Serial.printf("SNIFF ID:0x%lX LEN:%d DATA:", rxId, len);
      for (int i = 0; i < len; i++) {
        Serial.printf(" %02X", rxBuf[i]);
      }
      Serial.println();

      // -------------------------------
      // Optional Toyota fast decode
      // -------------------------------
      if (rxId == 0x25 && len >= 6) {
        decodeToyotaSteering(rxBuf);

        Serial.print("MCP:OK,CAN:OK,ANGLE:");
        Serial.print(totalSteerAngle / 10.0);
        Serial.print(",RATE:");
        Serial.println(steerRate);
      }
    }
  }

  // CAN timeout health message
  static unsigned long lastStatus = 0;
  if (millis() - lastStatus > 1000) {
    lastStatus = millis();

    if (!can_alive) {
      Serial.println("MCP:OK,CAN:FAIL");
    }
  }
}

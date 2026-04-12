#include <Arduino.h>
#include <SPI.h>
#include <mcp_can.h>

// =====================================================
// PIN CONFIG
// =====================================================
#define CAN_CS   5
#define CAN_INT  4

#define CAN_SCK  18
#define CAN_MISO 19
#define CAN_MOSI 23

MCP_CAN CAN0(CAN_CS);

// =====================================================
// FIXED MCP CLOCK (YOU SAID 8MHz)
// =====================================================
#define MCP_CLOCK MCP_8MHZ

// =====================================================
// CAN SPEED LIST
// =====================================================
const long canSpeeds[] = {
  CAN_125KBPS,
  CAN_250KBPS,
  CAN_500KBPS
};

const char* speedNames[] = {
  "125KBPS",
  "250KBPS",
  "500KBPS"
};

// =====================================================
// GLOBALS
// =====================================================
unsigned long rxId;
unsigned char len = 0;
unsigned char rxBuf[8];

unsigned long lastCanRx = 0;
bool canFound = false;

// =====================================================
// TRY SINGLE SPEED
// =====================================================
bool testSpeed(long speed, const char* name) {

  Serial.print("[TEST] ");
  Serial.println(name);

  CAN0.reset();
  delay(50);

  if (CAN0.begin(MCP_ANY, speed, MCP_CLOCK) != CAN_OK) {
    return false;
  }

  CAN0.setMode(MCP_NORMAL);
  delay(50);

  unsigned long start = millis();

  while (millis() - start < 400) {

    if (CAN0.checkReceive() == CAN_MSGAVAIL) {

      CAN0.readMsgBuf(&rxId, &len, rxBuf);

      Serial.print("[OK] CAN DETECTED AT ");
      Serial.println(name);

      return true;
    }
  }

  return false;
}

// =====================================================
// AUTO BAUD DETECTION
// =====================================================
void autoBaud() {

  Serial.println("\n========================");
  Serial.println("AUTO CAN SPEED DETECTOR");
  Serial.println("========================");

  for (int i = 0; i < 3; i++) {

    if (testSpeed(canSpeeds[i], speedNames[i])) {

      Serial.println("[SUCCESS] CAN BUS FOUND");
      canFound = true;
      return;
    }
  }

  Serial.println("[FAIL] NO CAN TRAFFIC FOUND");
  canFound = false;
}

// =====================================================
// SETUP
// =====================================================
void setup() {

  Serial.begin(115200);
  delay(1000);

  Serial.println("\nESP32 MCP2515 AUTO BAUD SYSTEM (8MHz)");

  SPI.begin(CAN_SCK, CAN_MISO, CAN_MOSI, CAN_CS);

  autoBaud();
}

// =====================================================
// LOOP
// =====================================================
void loop() {

  if (!canFound) {
    delay(500);
    return;
  }

  if (CAN0.checkReceive() == CAN_MSGAVAIL) {

    CAN0.readMsgBuf(&rxId, &len, rxBuf);
    lastCanRx = millis();

    // ================= GUI FORMAT =================
    Serial.printf("ID:0x%lX LEN:%d", rxId, len);

    for (int i = 0; i < len; i++) {
      Serial.printf(" %02X", rxBuf[i]);
    }

    Serial.println();
  }

  // ================= CAN HEALTH =================
  if (millis() - lastCanRx > 1000) {
    Serial.println("CAN:TIMEOUT");
  }
}

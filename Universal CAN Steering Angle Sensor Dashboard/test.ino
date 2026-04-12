#include <Arduino.h>
#include <SPI.h>
#include <mcp_can.h>

// ===================== PINS =====================
#define CAN_CS   5
#define CAN_INT  4

#define CAN_SCK  18
#define CAN_MISO 19
#define CAN_MOSI 23

#define MCP_CLOCK MCP_8MHZ

MCP_CAN CAN0(CAN_CS);

// ===================== CAN DATA =====================
unsigned long rxId;
unsigned char len;
unsigned char rxBuf[8];

// ===================== STATE =====================
unsigned long lastFrameTime = 0;
unsigned long frameCount = 0;

// ===================== SETUP =====================
void setup() {

  Serial.begin(115200);
  delay(1000);

  Serial.println("\n==============================");
  Serial.println(" ESP32 MCP2515 SAFE CAN SNIFFER");
  Serial.println("==============================");

  pinMode(CAN_INT, INPUT);

  SPI.begin(CAN_SCK, CAN_MISO, CAN_MOSI, CAN_CS);

  if (CAN0.begin(MCP_ANY, CAN_500KBPS, MCP_CLOCK) == CAN_OK) {
    Serial.println("MCP2515 INIT: OK");
  } else {
    Serial.println("MCP2515 INIT: FAIL");
  }

  CAN0.setMode(MCP_NORMAL);

  Serial.println("LISTENING TO CAN BUS...");
}

// ===================== LOOP =====================
void loop() {

  // ===================== SAFE INTERRUPT CHECK =====================
  if (digitalRead(CAN_INT) == LOW) {

    if (CAN0.readMsgBuf(&rxId, &len, rxBuf) == CAN_OK) {

      frameCount++;
      lastFrameTime = millis();

      Serial.print("FRAME ");
      Serial.print(frameCount);

      Serial.print(" | ID:0x");
      Serial.print(rxId, HEX);

      Serial.print(" | LEN:");
      Serial.print(len);

      Serial.print(" | DATA:");

      for (byte i = 0; i < len; i++) {
        Serial.print(" ");
        Serial.print(rxBuf[i], HEX);
      }

      Serial.println();
    }
  }

  // ===================== BUS SILENT CHECK =====================
  if (millis() - lastFrameTime > 1500) {
    Serial.println("STATUS: NO CAN TRAFFIC (bus silent)");
    lastFrameTime = millis();
  }

  delay(2); // CRITICAL: prevents ESP32 crash
}

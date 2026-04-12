#include <Arduino.h>

// CAN health timer
unsigned long lastCanRx = 0;

// ================= OPTIONAL TOYOTA DECODER =================
// This decodes Toyota-style ID 0x25 steering frames.
// Safe to keep even for universal sniffing.
void decodeToyotaSteering(const unsigned char *buf) {
  int rawAngle = ((buf[0] & 0x0F) << 8) | buf[1];

  // Convert signed 12-bit value
  if (rawAngle & 0x800) rawAngle -= 0x1000;

  int angle = rawAngle * 15; // 1.5 degree * 10

  int frac = (buf[4] >> 4) & 0x0F;
  if (frac > 8) frac -= 16;

  int rawRate = ((buf[4] & 0x0F) << 8) | buf[5];
  if (rawRate & 0x800) rawRate -= 0x1000;

  steerRate = rawRate;
  totalSteerAngle = angle + frac;
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  // VSPI pins: SCK=18 MISO=19 MOSI=23
  SPI.begin(18, 19, 23, CAN_CS);

  // IMPORTANT: your MCP2515 crystal is 8 MHz
  if (CAN0.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ) == CAN_OK) {
    Serial.println("MCP:OK");
  } else {
    Serial.println("MCP:FAIL");
    while (1);
  }

  CAN0.setMode(MCP_NORMAL);
  pinMode(CAN_INT, INPUT);
}

void loop() {
  bool can_alive = (millis() - lastCanRx) < 1000;

  // MCP2515 interrupt goes LOW when a frame is received
  if (digitalRead(CAN_INT) == LOW) {
    if (CAN0.readMsgBuf(&rxId, &len, rxBuf) == CAN_OK) {
      lastCanRx = millis();

      // ================= UNIVERSAL CAN SNIFFER =================
      // This is what the Python GUI uses to auto-detect the steering CAN ID.
      Serial.printf("SNIFF ID:0x%lX LEN:%d DATA:", rxId, len);
      for (int i = 0; i < len; i++) {
        Serial.printf(" %02X", rxBuf[i]);
      }
      Serial.println();

      // ================= OPTIONAL TOYOTA FAST PATH =================
      // If the sensor is known Toyota SAS, this gives instant angle decode.
      if (rxId == 0x25 && len >= 6) {
        decodeToyotaSteering(rxBuf);

        Serial.print("MCP:OK,CAN:OK,ANGLE:");
        Serial.print(totalSteerAngle / 10.0);
        Serial.print(",RATE:");
        Serial.println(steerRate);
      }
    }
  }

  // Report CAN timeout once per second
  static unsigned long lastStatus = 0;
  if (millis() - lastStatus > 1000) {
    lastStatus = millis();
    if (!can_alive) {
      Serial.println("MCP:OK,CAN:FAIL");
    }
  }
}

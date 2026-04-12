#include <SPI.h>
#include <mcp_can.h>

#define CAN_CS 5
MCP_CAN CAN0(CAN_CS);

unsigned long frameCount = 0;

void setup() {
  Serial.begin(115200);
  delay(1500);

  Serial.println("ESP32_CAN_STREAM_READY");

  if (CAN0.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ) == CAN_OK) {
    Serial.println("CAN_OK");
  } else {
    Serial.println("CAN_FAIL");
    while (1);
  }

  CAN0.setMode(MCP_NORMAL);
}

void loop() {
  long unsigned int id;
  unsigned char len = 0;
  unsigned char buf[8];

  if (CAN0.checkReceive() == CAN_MSGAVAIL) {

    CAN0.readMsgBuf(&id, &len, buf);
    frameCount++;

    // 🚀 MACHINE PARSABLE FORMAT (IMPORTANT FOR GUI)
    Serial.print(frameCount);
    Serial.print(",");

    Serial.print(id, HEX);
    Serial.print(",");

    Serial.print(len);
    Serial.print(",");

    for (int i = 0; i < len; i++) {
      if (buf[i] < 0x10) Serial.print("0");
      Serial.print(buf[i], HEX);
      if (i < len - 1) Serial.print("-");
    }

    Serial.println();
  }
}

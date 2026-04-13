# `esp32_dual_n25_eps_cascaded_velocity.ino`

#include <SPI.h>
#include <mcp_can.h>

// ============================================================
// ESP32 + MCP2515 + Dual BTS7960 + N25 Encoder EPS Controller
// 2-loop cascaded position -> velocity -> PWM control
// CAN compatible with original STM32 IDs
// ============================================================

// ---------------- MCP2515 ----------------
#define MCP_CS   5
#define MCP_INT  15
MCP_CAN CAN0(MCP_CS);

// ---------------- BTS7960 #1 ----------------
#define M1_RPWM 25
#define M1_LPWM 26
#define M1_REN  27
#define M1_LEN  14

// ---------------- BTS7960 #2 ----------------
#define M2_RPWM 32
#define M2_LPWM 33
#define M2_REN  12
#define M2_LEN  13

// ---------------- Encoder Motor 1 ----------------
#define ENC1_A_PIN 34
#define ENC1_B_PIN 35

// ---------------- Encoder Motor 2 ----------------
#define ENC2_A_PIN 36
#define ENC2_B_PIN 39

// ---------------- Engage ----------------
#define ENGAGE_PIN 4

// ---------------- CAN IDs ----------------
#define INPUT_ADDRESS          0x22E
#define OUTPUT_ADDRESS         0x22F
#define OUTPUT_ADDRESS_CRUISE  0x22D

// ---------------- Control ----------------
#define COUNTER_CYCLE 0x0F
#define PWM_MAX 1023
#define PWM_CENTER 512
#define PWM_BREAKAWAY 180
#define MAX_TIMEOUT_MS 500

// ---------------- State ----------------
volatile long encoder1Count = 0;
volatile long encoder2Count = 0;
volatile int16_t canTorqueRequest = 0;
volatile uint8_t current_index = 0;
volatile bool steer_ok = false;

float targetPosition = 0.0f;
float targetVelocity = 0.0f;

// Outer position loop
float kp_pos = 0.25f;      // position error -> speed target
float maxVelocity = 800.0f; // counts/sec

// Inner velocity loop
float kv_vel = 0.9f;       // speed error -> pwm
float kd_damp = 0.02f;     // extra damping

long lastEncoderCount = 0;
uint32_t lastLoopMicros = 0;
uint32_t lastCommandTime = 0;

uint8_t pkt_idx = 0;
uint8_t state = 0;

// ============================================================
// CRC8 SAE J1850
// ============================================================
uint8_t crc8_j1850(uint8_t *data, int len) {
  uint8_t crc = 0xFF;
  for (int i = 1; i < len; i++) {
    crc ^= data[i];
    for (int b = 0; b < 8; b++) {
      crc = (crc & 0x80) ? ((crc << 1) ^ 0x1D) : (crc << 1);
    }
  }
  return crc;
}

// ============================================================
// Encoder ISR
// ============================================================
void IRAM_ATTR enc1A_ISR() {
  bool a = digitalRead(ENC1_A_PIN);
  bool b = digitalRead(ENC1_B_PIN);
  encoder1Count += (a == b) ? 1 : -1;
}

void IRAM_ATTR enc1B_ISR() {
  bool a = digitalRead(ENC1_A_PIN);
  bool b = digitalRead(ENC1_B_PIN);
  encoder1Count += (a != b) ? 1 : -1;
}

void IRAM_ATTR enc2A_ISR() {
  bool a = digitalRead(ENC2_A_PIN);
  bool b = digitalRead(ENC2_B_PIN);
  encoder2Count += (a == b) ? 1 : -1;
}

void IRAM_ATTR enc2B_ISR() {
  bool a = digitalRead(ENC2_A_PIN);
  bool b = digitalRead(ENC2_B_PIN);
  encoder2Count += (a != b) ? 1 : -1;
}

// ============================================================
// Motor drive
// ============================================================
void driveSingleMotor(uint8_t chA, uint8_t chB, int pwm) {
  pwm = constrain(pwm, -PWM_MAX, PWM_MAX);

  if (pwm > 0 && pwm < PWM_BREAKAWAY) pwm = PWM_BREAKAWAY;
  if (pwm < 0 && pwm > -PWM_BREAKAWAY) pwm = -PWM_BREAKAWAY;

  int outA = PWM_CENTER + pwm / 2;
  int outB = PWM_CENTER - pwm / 2;

  outA = constrain(outA, 0, PWM_MAX);
  outB = constrain(outB, 0, PWM_MAX);

  ledcWrite(chA, outA);
  ledcWrite(chB, outB);
}

void driveMotors(int basePwm) {
  long syncError = encoder1Count - encoder2Count;
  int syncCorrection = constrain((int)(syncError * 0.15f), -120, 120);

  int pwm1 = basePwm - syncCorrection;
  int pwm2 = basePwm + syncCorrection;

  driveSingleMotor(0, 1, pwm1);
  driveSingleMotor(2, 3, pwm2);
}

// ============================================================
// 2-loop cascaded controller
// ============================================================
int computeCascadePWM() {
  uint32_t now = micros();
  float dt = (now - lastLoopMicros) / 1000000.0f;
  if (dt <= 0.0f) dt = 0.001f;
  lastLoopMicros = now;

  long pos = (encoder1Count + encoder2Count) / 2;
  long delta = pos - lastEncoderCount;
  float velocity = delta / dt;
  lastEncoderCount = pos;

  // CAN torque -> incremental target position
  float posStep = (canTorqueRequest / 512.0f) * 20.0f;
  targetPosition += posStep;
  targetPosition = constrain(targetPosition, -6000.0f, 6000.0f);

  // OUTER LOOP: position -> target velocity
  float posError = targetPosition - pos;
  targetVelocity = kp_pos * posError;
  targetVelocity = constrain(targetVelocity, -maxVelocity, maxVelocity);

  // INNER LOOP: velocity -> PWM
  float velError = targetVelocity - velocity;
  float pwm = kv_vel * velError - kd_damp * velocity;

  return constrain((int)pwm, -PWM_MAX, PWM_MAX);
}

// ============================================================
// CAN RX
// ============================================================
void processCAN() {
  if (CAN0.checkReceive() != CAN_MSGAVAIL) return;

  long unsigned int rxId;
  uint8_t len;
  uint8_t buf[8];

  CAN0.readMsgBuf(&rxId, &len, buf);

  if (rxId != INPUT_ADDRESS || len < 6) return;
  if (buf[0] != crc8_j1850(buf, 6)) return;

  uint8_t index = buf[1] & COUNTER_CYCLE;
  if (steer_ok && (((current_index + 1) & COUNTER_CYCLE) != index)) {
    state = 7;
    return;
  }

  canTorqueRequest = (int16_t)((buf[5] << 8) | buf[4]);
  canTorqueRequest = constrain(canTorqueRequest, -512, 512);

  current_index = index;
  steer_ok = true;
  state = 0;
  lastCommandTime = millis();
}

// ============================================================
// CAN TX status
// ============================================================
void sendFeedback() {
  uint8_t data[7];
  data[6] = (canTorqueRequest >> 8) & 0xFF;
  data[5] = canTorqueRequest & 0xFF;
  data[4] = 0;
  data[3] = 0;
  data[2] = steer_ok;
  data[1] = ((state & 0x0F) << 4) | pkt_idx;
  data[0] = crc8_j1850(data, 7);

  CAN0.sendMsgBuf(OUTPUT_ADDRESS, 0, 7, data);
  pkt_idx = (pkt_idx + 1) & COUNTER_CYCLE;
}

void sendCruise() {
  uint8_t data[4];
  uint16_t fakeSpeed = 6000;

  data[3] = (fakeSpeed >> 8) & 0xFF;
  data[2] = fakeSpeed & 0xFF;
  data[1] = !digitalRead(ENGAGE_PIN);
  data[0] = crc8_j1850(data, 4);

  CAN0.sendMsgBuf(OUTPUT_ADDRESS_CRUISE, 0, 4, data);
}

// ============================================================
// Setup
// ============================================================
void setup() {
  Serial.begin(115200);
  SPI.begin();

  pinMode(MCP_INT, INPUT);
  pinMode(ENGAGE_PIN, INPUT_PULLUP);

  pinMode(M1_REN, OUTPUT);
  pinMode(M1_LEN, OUTPUT);
  pinMode(M2_REN, OUTPUT);
  pinMode(M2_LEN, OUTPUT);

  digitalWrite(M1_REN, HIGH);
  digitalWrite(M1_LEN, HIGH);
  digitalWrite(M2_REN, HIGH);
  digitalWrite(M2_LEN, HIGH);

  pinMode(ENC1_A_PIN, INPUT_PULLUP);
  pinMode(ENC1_B_PIN, INPUT_PULLUP);
  pinMode(ENC2_A_PIN, INPUT_PULLUP);
  pinMode(ENC2_B_PIN, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(ENC1_A_PIN), enc1A_ISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC1_B_PIN), enc1B_ISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC2_A_PIN), enc2A_ISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC2_B_PIN), enc2B_ISR, CHANGE);

  ledcSetup(0, 20000, 10);
  ledcSetup(1, 20000, 10);
  ledcSetup(2, 20000, 10);
  ledcSetup(3, 20000, 10);

  ledcAttachPin(M1_RPWM, 0);
  ledcAttachPin(M1_LPWM, 1);
  ledcAttachPin(M2_RPWM, 2);
  ledcAttachPin(M2_LPWM, 3);

  while (CAN0.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ) != CAN_OK) {
    Serial.println("MCP2515 init failed, retrying...");
    delay(100);
  }
  CAN0.setMode(MCP_NORMAL);

  lastLoopMicros = micros();
  lastCommandTime = millis();

  Serial.println("Dual N25 EPS cascade controller ready");
}

// ============================================================
// Main loop
// ============================================================
void loop() {
  processCAN();

  if (millis() - lastCommandTime > MAX_TIMEOUT_MS) {
    canTorqueRequest = 0;
    steer_ok = false;
    state = 5;
  }

  int pwm = computeCascadePWM();
  driveMotors(pwm);

  static uint32_t lastTx = 0;
  if (millis() - lastTx >= 10) {
    sendFeedback();
    sendCruise();
    lastTx = millis();
  }
}

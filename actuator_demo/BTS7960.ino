#include <SPI.h>
#include <mcp_can.h>

// ============================================================
// ESP32 Dual N25 EPS Controller (MCP2515 + 1x BTS7960)
// ------------------------------------------------------------
// Goal: replicate STM32 steer_actuator_demo CAN behavior while
// running a cascade controller with dual encoder feedback.
//
// Hardware topology in this implementation:
//   - One BTS7960 drives two motors electrically in parallel.
//   - Two encoders are read independently for safety and diagnostics.
//   - Because drive channel is shared, encoder mismatch is handled as a
//     protective fault (assist disabled) rather than active correction.
//
// CAN compatibility (STM demo style):
//   RX 0x22E (6 bytes): torque command + counter + CRC8
//   TX 0x22F (7 bytes): status + torque echo + state + CRC8
//   TX 0x22D (4 bytes): fake cruise state + engage + CRC8
//
// Safety:
//   - CRC check
//   - rolling counter check
//   - command timeout
//   - encoder mismatch fault
//   - disengage switch gating
// ============================================================

// ---------------- MCP2515 ----------------
#define MCP_CS   5
#define MCP_INT  15
MCP_CAN CAN0(MCP_CS);

// ---------------- Single BTS7960 ----------------
#define RPWM_PIN 25
#define LPWM_PIN 26
#define R_EN_PIN 27
#define L_EN_PIN 14

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

// ---------------- Protocol/limits ----------------
#define COUNTER_CYCLE 0x0F
#define MAX_TIMEOUT_MS 500

// ---------------- Control ----------------
#define PWM_MAX 1023
#define PWM_CENTER 512
#define PWM_BREAKAWAY 180
#define ENCODER_MISMATCH_LIMIT 300

#define PWM_FREQ 20000
#define PWM_RES  10
#define CH_RPWM 0
#define CH_LPWM 1

// ---------------- Fault/state codes ----------------
// Matches steer_actuator_demo states where possible.
enum {
  NO_FAULT = 0,
  FAULT_BAD_CHECKSUM = 1,
  FAULT_SEND = 2,
  FAULT_SCE = 3,
  FAULT_STARTUP = 4,
  FAULT_TIMEOUT = 5,
  FAULT_INVALID = 6,
  FAULT_COUNTER = 7,
  FAULT_DISENGAGED = 8,
  FAULT_ENCODER_MISMATCH = 9,
};

// ---------------- Shared state ----------------
// ISR-updated values are declared volatile because they can change outside
// normal control flow.
volatile long encoder1Count = 0;
volatile long encoder2Count = 0;

volatile int16_t canTorqueRequest = 0;  // -512..512
volatile uint8_t current_index = 0;
volatile bool steer_ok = false;

// Control loop internal state.
float targetPosition = 0.0f;  // virtual position target generated from torque req
float targetVelocity = 0.0f;  // velocity setpoint from outer loop

// Tunables (starting values chosen for smoother response)
float kp_pos = 0.18f;
float maxVelocity = 700.0f;
float kv_vel = 0.6f;
float kd_damp = 0.04f;

long lastEncoderAvg = 0;
uint32_t lastLoopMicros = 0;
uint32_t lastCommandTime = 0;

uint8_t pkt_idx = 0;
uint8_t state = FAULT_STARTUP;

// ============================================================
// CRC8 SAE J1850 (STM style for these packets)
// init=0xFF, poly=0x1D, final xor=0xFF, skip byte0
// ============================================================
uint8_t crc8_j1850(const uint8_t *data, int len) {
  uint8_t crc = 0xFF;
  for (int i = 1; i < len; i++) {
    crc ^= data[i];
    for (int b = 0; b < 8; b++) {
      if (crc & 0x80) {
        crc = (uint8_t)((crc << 1) ^ 0x1D);
      } else {
        crc <<= 1;
      }
    }
  }
  return (uint8_t)(crc ^ 0xFF);
}

// ============================================================
// Encoder ISRs
// ------------------------------------------------------------
// Quadrature decode uses both A and B transitions for each motor.
// If direction is inverted mechanically/electrically, swap A/B wiring
// for that motor or invert ISR increment signs as needed.
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
// Atomic snapshot helpers
// ------------------------------------------------------------
// These functions read shared encoder counters atomically to prevent
// torn reads while ISR updates are occurring.
// ============================================================
long readEncoder1() {
  noInterrupts();
  long v = encoder1Count;
  interrupts();
  return v;
}

long readEncoder2() {
  noInterrupts();
  long v = encoder2Count;
  interrupts();
  return v;
}

long readEncoderAvg() {
  noInterrupts();
  long a = encoder1Count;
  long b = encoder2Count;
  interrupts();
  return (a + b) / 2;
}

// ============================================================
// Single driver output for both motors
// ------------------------------------------------------------
// The control signal is symmetric around PWM_CENTER:
//   outR = center + pwm/2
//   outL = center - pwm/2
// This preserves differential drive behavior with a single signed command.
// ============================================================
void driveMotors(int pwm) {
  pwm = constrain(pwm, -PWM_MAX, PWM_MAX);

  if (pwm > 0 && pwm < PWM_BREAKAWAY) pwm = PWM_BREAKAWAY;
  if (pwm < 0 && pwm > -PWM_BREAKAWAY) pwm = -PWM_BREAKAWAY;

  int outR = PWM_CENTER + pwm / 2;
  int outL = PWM_CENTER - pwm / 2;

  outR = constrain(outR, 0, PWM_MAX);
  outL = constrain(outL, 0, PWM_MAX);

  ledcWrite(CH_RPWM, outR);
  ledcWrite(CH_LPWM, outL);
}

void driveNeutral() {
  // Neutral command: both channels centered, equivalent to no assist torque.
  ledcWrite(CH_RPWM, PWM_CENTER);
  ledcWrite(CH_LPWM, PWM_CENTER);
}

// ============================================================
// Cascade controller (outer position, inner velocity)
// ------------------------------------------------------------
// Outer loop:
//   position error -> target velocity
// Inner loop:
//   velocity error -> PWM command
//
// Torque request is treated as a command shaping term that moves the virtual
// target position over time. This gives smoother behavior than direct PWM.
// ============================================================
int computeCascadePWM() {
  uint32_t now = micros();
  float dt = (now - lastLoopMicros) / 1000000.0f;
  if (dt <= 0.0f || dt > 0.05f) dt = 0.001f;
  lastLoopMicros = now;

  long avgPos = readEncoderAvg();
  long delta = avgPos - lastEncoderAvg;
  float velocity = delta / dt;
  lastEncoderAvg = avgPos;

  // Integrate position target from torque request.
  // 512 is full-scale command in protocol; scale factor maps this to
  // position steps per control cycle.
  float posStep = (canTorqueRequest / 512.0f) * 20.0f;
  targetPosition += posStep;
  targetPosition = constrain(targetPosition, -6000.0f, 6000.0f);

  float posError = targetPosition - avgPos;
  targetVelocity = kp_pos * posError;
  targetVelocity = constrain(targetVelocity, -maxVelocity, maxVelocity);

  float velError = targetVelocity - velocity;
  float pwm = kv_vel * velError - kd_damp * velocity;

  return constrain((int)pwm, -PWM_MAX, PWM_MAX);
}

bool encoderMismatchFault() {
  // In this one-driver topology we cannot independently correct each motor,
  // so mismatch is treated as a safety fault.
  long diff = labs(readEncoder1() - readEncoder2());
  return diff > ENCODER_MISMATCH_LIMIT;
}

// ============================================================
// CAN RX: process 0x22E command packet
// Packet layout:
//   [0]=crc, [1]=mode/counter, [2..3]=angle_req, [4..5]=torque_req
//
// Acceptance rules:
//   1) valid CRC
//   2) expected rolling counter (once stream is locked)
// If either fails, packet is rejected and state is updated.
// ============================================================
void processCAN() {
  if (CAN0.checkReceive() != CAN_MSGAVAIL) return;

  unsigned long rxId = 0;
  uint8_t len = 0;
  uint8_t buf[8] = {0};

  CAN0.readMsgBuf(&rxId, &len, buf);

  if (rxId != INPUT_ADDRESS || len < 6) {
    return;
  }

  if (buf[0] != crc8_j1850(buf, 6)) {
    state = FAULT_BAD_CHECKSUM;
    return;
  }

  uint8_t index = buf[1] & COUNTER_CYCLE;
  if (steer_ok && (((current_index + 1U) & COUNTER_CYCLE) != index)) {
    state = FAULT_COUNTER;
    return;
  }

  // Angle currently not used in control (kept for protocol compatibility).
  int16_t angle_req = (int16_t)((buf[3] << 8) | buf[2]);
  (void)angle_req;

  int16_t torque_req = (int16_t)((buf[5] << 8) | buf[4]);
  torque_req = constrain(torque_req, -512, 512);

  canTorqueRequest = torque_req;
  current_index = index;
  steer_ok = true;
  state = NO_FAULT;
  lastCommandTime = millis();
}

// ============================================================
// CAN TX: status packet 0x22F (7 bytes), STM-style
// ------------------------------------------------------------
// data[1] upper nibble carries state, lower nibble carries packet index.
// data[5..6] echoes torque request for external observers/logging.
// ============================================================
void sendFeedback() {
  uint8_t data[7];

  data[6] = (uint8_t)((canTorqueRequest >> 8) & 0xFF);
  data[5] = (uint8_t)(canTorqueRequest & 0xFF);
  data[4] = 0;
  data[3] = 0;
  data[2] = steer_ok ? 1U : 0U;
  data[1] = (uint8_t)(((state & 0x0F) << 4) | (pkt_idx & 0x0F));
  data[0] = crc8_j1850(data, 7);

  uint8_t rc = CAN0.sendMsgBuf(OUTPUT_ADDRESS, 0, 7, data);
  if (rc != CAN_OK) {
    state = FAULT_SEND;
  }

  pkt_idx = (pkt_idx + 1U) & COUNTER_CYCLE;
}

// ============================================================
// CAN TX: fake cruise packet 0x22D (4 bytes), STM-style
// ------------------------------------------------------------
// This frame is used by demo stacks expecting cruise/current-state style
// activity. data[1] mirrors local engage switch state.
// ============================================================
void sendCruise() {
  uint8_t data[4];
  uint16_t fakeSpeed = 6000;  // matches STM demo
  bool engaged = !digitalRead(ENGAGE_PIN);

  data[3] = (uint8_t)(fakeSpeed >> 8);
  data[2] = (uint8_t)(fakeSpeed & 0xFF);
  data[1] = engaged ? 1U : 0U;
  data[0] = crc8_j1850(data, 4);

  uint8_t rc = CAN0.sendMsgBuf(OUTPUT_ADDRESS_CRUISE, 0, 4, data);
  if (rc != CAN_OK) {
    state = FAULT_SEND;
  }
}

// ============================================================
// Setup
// ------------------------------------------------------------
// Initialization order:
//   1) serial + SPI + GPIO
//   2) encoder interrupts
//   3) PWM channels and neutral output
//   4) CAN bring-up
// ============================================================
void setup() {
  Serial.begin(115200);
  SPI.begin();

  pinMode(MCP_INT, INPUT);
  pinMode(ENGAGE_PIN, INPUT_PULLUP);

  pinMode(R_EN_PIN, OUTPUT);
  pinMode(L_EN_PIN, OUTPUT);
  digitalWrite(R_EN_PIN, HIGH);
  digitalWrite(L_EN_PIN, HIGH);

  // NOTE: GPIO34..39 are input-only and do not have internal pullups on ESP32.
  // Use external pullup resistors on encoder lines.
  pinMode(ENC1_A_PIN, INPUT);
  pinMode(ENC1_B_PIN, INPUT);
  pinMode(ENC2_A_PIN, INPUT);
  pinMode(ENC2_B_PIN, INPUT);

  attachInterrupt(digitalPinToInterrupt(ENC1_A_PIN), enc1A_ISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC1_B_PIN), enc1B_ISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC2_A_PIN), enc2A_ISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC2_B_PIN), enc2B_ISR, CHANGE);

  ledcSetup(CH_RPWM, PWM_FREQ, PWM_RES);
  ledcSetup(CH_LPWM, PWM_FREQ, PWM_RES);
  ledcAttachPin(RPWM_PIN, CH_RPWM);
  ledcAttachPin(LPWM_PIN, CH_LPWM);
  driveNeutral();

  while (CAN0.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ) != CAN_OK) {
    Serial.println("MCP2515 init failed...");
    delay(100);
  }
  CAN0.setMode(MCP_NORMAL);

  lastLoopMicros = micros();
  lastCommandTime = millis();

  Serial.println("ESP32 dual N25 EPS controller ready");
}

// ============================================================
// Main loop
// ------------------------------------------------------------
// Priority order each cycle:
//   1) accept CAN command updates
//   2) evaluate safety gates (engage, timeout, mismatch)
//   3) run control only if healthy
//   4) transmit status at fixed rate
// ============================================================
void loop() {
  processCAN();

  bool engaged = !digitalRead(ENGAGE_PIN);
  bool timeoutFault = (millis() - lastCommandTime) > MAX_TIMEOUT_MS;
  bool mismatchFault = encoderMismatchFault();

  if (!engaged) {
    canTorqueRequest = 0;
    steer_ok = false;
    state = FAULT_DISENGAGED;
  } else if (timeoutFault) {
    canTorqueRequest = 0;
    steer_ok = false;
    state = FAULT_TIMEOUT;
  } else if (mismatchFault) {
    canTorqueRequest = 0;
    steer_ok = false;
    state = FAULT_ENCODER_MISMATCH;
  }

  int pwm = 0;
  if (state == NO_FAULT && steer_ok && engaged) {
    pwm = computeCascadePWM();
    driveMotors(pwm);
  } else {
    // Keep controller from winding up when not actively controlling.
    long avgPos = readEncoderAvg();
    targetPosition = (float)avgPos;
    targetVelocity = 0.0f;
    driveNeutral();
  }

  static uint32_t lastTx = 0;
  if (millis() - lastTx >= 10) {  // 100 Hz status/cruise TX
    sendFeedback();
    sendCruise();
    lastTx = millis();
  }

  // Optional debug at low rate.
  static uint32_t lastDbg = 0;
  if (millis() - lastDbg >= 200) {
    Serial.print("state=");
    Serial.print(state);
    Serial.print(" steer_ok=");
    Serial.print(steer_ok);
    Serial.print(" tq=");
    Serial.print(canTorqueRequest);
    Serial.print(" e1=");
    Serial.print(readEncoder1());
    Serial.print(" e2=");
    Serial.print(readEncoder2());
    Serial.print(" engaged=");
    Serial.println(engaged ? 1 : 0);
    lastDbg = millis();
  }
}

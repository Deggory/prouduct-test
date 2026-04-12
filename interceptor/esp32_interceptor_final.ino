/*
 * ESP32 + MCP2515 CAN Interceptor (FINAL FIXED VERSION)
 * - Stable CAN RX/TX
 * - Auto recovery state machine
 * - Clean GUI serial stream
 * - Health monitoring
 */

#include <SPI.h>
#include <mcp2515.h>

// =========================
// PINS
// =========================
#define MCP_CS   5
#define MCP_SCK  18
#define MCP_MISO 19
#define MCP_MOSI 23

// =========================
// CAN OBJECT
// =========================
MCP2515 can(MCP_CS);
struct can_frame rxMsg;
struct can_frame txMsg;

// =========================
// CAN STATE MACHINE
// =========================
enum CAN_STATE {
  CAN_OK,
  CAN_WARNING,
  CAN_FAIL
};

CAN_STATE canState = CAN_FAIL;

// =========================
// TIMERS
// =========================
unsigned long lastRxTime = 0;
unsigned long lastTxTime = 0;
unsigned long lastHealthCheck = 0;

// =========================
// ERROR TRACKING
// =========================
uint8_t errorCounter = 0;

// =========================================================
// INIT CAN
// =========================================================
bool initCAN() {
  can.reset();
  delay(20);

  if (can.setBitrate(CAN_500KBPS, MCP_8MHZ) != MCP2515::ERROR_OK) {
    Serial.println("[CAN] Bitrate init FAILED");
    return false;
  }

  can.setNormalMode();

  lastRxTime = millis();
  lastTxTime = millis();
  errorCounter = 0;
  canState = CAN_OK;

  Serial.println("[CAN] Initialized OK");
  return true;
}

// =========================================================
// CAN RECOVERY
// =========================================================
void recoverCAN() {
  Serial.println("[CAN] RECOVERY START");

  canState = CAN_FAIL;

  for (int i = 0; i < 3; i++) {
    if (initCAN()) {
      Serial.println("[CAN] RECOVERY SUCCESS");
      return;
    }
    delay(50);
  }

  Serial.println("[CAN] RECOVERY FAILED");
}

// =========================================================
// UPDATE CAN STATE
// =========================================================
void updateCANState() {
  unsigned long now = millis();

  // No RX activity = possible bus issue
  if (now - lastRxTime > 500) {
    errorCounter++;
  } else {
    errorCounter = 0;
  }

  if (errorCounter == 0) {
    canState = CAN_OK;
  }
  else if (errorCounter < 3) {
    canState = CAN_WARNING;
  }
  else {
    canState = CAN_FAIL;
    recoverCAN();
  }
}

// =========================================================
// SEND CAN FRAME (SAFE)
// =========================================================
bool sendCAN(uint16_t id, uint8_t *data, uint8_t len) {

  txMsg.can_id = id;
  txMsg.can_dlc = len;

  for (int i = 0; i < len; i++) {
    txMsg.data[i] = data[i];
  }

  if (can.sendMessage(&txMsg) == MCP2515::ERROR_OK) {
    lastTxTime = millis();
    return true;
  }

  errorCounter++;
  return false;
}

// =========================================================
// READ CAN (NON-BLOCKING)
// =========================================================
void readCAN() {
  while (can.readMessage(&rxMsg) == MCP2515::ERROR_OK) {

    lastRxTime = millis();
    errorCounter = 0;

    // =========================
    // CLEAN GUI FORMAT OUTPUT
    // =========================
    Serial.print("FRAME | ID:0x");
    Serial.print(rxMsg.can_id, HEX);
    Serial.print(" | LEN:");
    Serial.print(rxMsg.can_dlc);
    Serial.print(" | DATA:");

    for (int i = 0; i < rxMsg.can_dlc; i++) {
      Serial.print(" ");
      Serial.print(rxMsg.data[i], HEX);
    }

    Serial.println();
  }
}

// =========================================================
// HEARTBEAT DEBUG (OPTIONAL)
// =========================================================
void printCANState() {
  Serial.print("[CAN STATE] ");

  if (canState == CAN_OK) Serial.println("OK");
  else if (canState == CAN_WARNING) Serial.println("WARNING");
  else Serial.println("FAIL");
}

// =========================================================
// SETUP
// =========================================================
void setup() {
  Serial.begin(115200);

  SPI.begin(MCP_SCK, MCP_MISO, MCP_MOSI, MCP_CS);

  Serial.println("=================================");
  Serial.println(" ESP32 MCP2515 CAN INTERCEPTOR");
  Serial.println("=================================");

  if (!initCAN()) {
    Serial.println("CAN INIT FAILED - retrying...");
    delay(500);
    recoverCAN();
  }
}

// =========================================================
// LOOP
// =========================================================
void loop() {

  // 1. READ CAN BUS
  readCAN();

  // 2. UPDATE CAN HEALTH STATE
  updateCANState();

  // 3. PERIODIC STATUS (optional debug)
  if (millis() - lastHealthCheck > 1000) {
    lastHealthCheck = millis();
    printCANState();
  }

  delay(5);  // stable CPU usage
}/*
 * ESP32 + MCP2515 CAN Bus Interceptor
 * Auto-Calibration + Serial Watchdog + Error LED
 * 
 * Features:
 * - Auto-calibration using telemetry ADC values (median of 100 samples)
 * - EEPROM storage of calibrated centers (persistent across reboots)
 * - Tolerance check (±100) to prevent erroneous calibration
 * - Serial watchdog: zeros steer/speed if no CMD for 200ms
 * - CAN recovery on send failures
 * - Error LED: off = OK, solid = minor errors, blink = recovery
 * 
 * Commands:
 *   CMD,steer,speed   - control command (steer: -22..22, speed: 0..655)
 *   CAL               - manual recalibration
 * 
 * Hardware:
 *   MCP2515 CS  -> GPIO5
 *   SCK         -> GPIO18
 *   MISO        -> GPIO19
 *   MOSI        -> GPIO23
 *   Error LED   -> GPIO2 (active high)
 */

#include <SPI.h>
#include <mcp2515.h>
#include <EEPROM.h>

// =========================================================
// PIN DEFINITIONS
// =========================================================
#define MCP_CS   5
#define MCP_SCK  18
#define MCP_MISO 19
#define MCP_MOSI 23
#define LED_ERR  2

// =========================================================
// EEPROM CONFIGURATION
// =========================================================
#define EEPROM_SIZE 16
#define ADDR_CENTER0 0      // uint16_t
#define ADDR_CENTER1 2      // uint16_t
#define ADDR_MAGIC   4      // uint16_t (0x5A5A = valid)

// =========================================================
// CALIBRATION PARAMETERS
// =========================================================
const int CALIBRATION_SAMPLES = 100;   // number of ADC samples to collect
const int TOLERANCE = 100;             // ±100 acceptable deviation from previous calibration
const int MAX_STEER_CMD = 22;          // safe steer limit (from physical headroom)

// =========================================================
// WATCHDOG TIMEOUT
// =========================================================
const unsigned long CMD_TIMEOUT_MS = 200;   // zero outputs if no command received

// =========================================================
// MCP2515 OBJECT
// =========================================================
MCP2515 mcp2515(MCP_CS);
struct can_frame txMsg;
struct can_frame rxMsg;

// =========================================================
// CONTROL STATE
// =========================================================
int steer = 0;           // commanded steering (-22..22)
int speed = 0;           // commanded speed (0..655)

// =========================================================
// CALIBRATION STATE
// =========================================================
uint16_t cal_center0 = 1538;   // default fallback (your measured values)
uint16_t cal_center1 = 1579;
bool cal_valid = false;

bool calibration_requested = false;
bool calibration_running = false;
int cal_sample_count = 0;
uint16_t cal_samples0[CALIBRATION_SAMPLES];
uint16_t cal_samples1[CALIBRATION_SAMPLES];

// =========================================================
// STATUS VARIABLES
// =========================================================
uint8_t counter = 0;
uint32_t tx_count = 0;
uint32_t rx_count = 0;
uint8_t send_fail_count = 0;

bool led_state = false;
unsigned long last_blink = 0;
unsigned long last_cmd_time = 0;

// =========================================================
// FUNCTION PROTOTYPES
// =========================================================
void canRecover();
void sendTorque();
void sendSpeed();
void readTelemetry();
void updateErrorLed();
void saveCalibration();
void loadCalibration();
void startCalibration();
void addCalibrationSample(uint16_t adc0, uint16_t adc1);
void finishCalibration();
uint16_t median(uint16_t *arr, int n);

// =========================================================
// EEPROM HELPERS
// =========================================================
void saveCalibration() {
  EEPROM.put(ADDR_CENTER0, cal_center0);
  EEPROM.put(ADDR_CENTER1, cal_center1);
  uint16_t magic = 0x5A5A;
  EEPROM.put(ADDR_MAGIC, magic);
  EEPROM.commit();
  Serial.println("Calibration saved to EEPROM.");
}

void loadCalibration() {
  uint16_t magic;
  EEPROM.get(ADDR_MAGIC, magic);
  if (magic == 0x5A5A) {
    EEPROM.get(ADDR_CENTER0, cal_center0);
    EEPROM.get(ADDR_CENTER1, cal_center1);
    cal_valid = true;
    Serial.print("Loaded calibration from EEPROM: ");
    Serial.print(cal_center0);
    Serial.print(", ");
    Serial.println(cal_center1);
  } else {
    Serial.println("No valid calibration in EEPROM, using defaults.");
    cal_valid = false;
  }
}

// =========================================================
// CALIBRATION ROUTINES
// =========================================================
void startCalibration() {
  if (calibration_running) {
    Serial.println("Calibration already in progress.");
    return;
  }
  calibration_running = true;
  calibration_requested = false;
  cal_sample_count = 0;
  Serial.println("Starting auto-calibration. Keep steering at zero for 2 seconds...");
}

void addCalibrationSample(uint16_t adc0, uint16_t adc1) {
  if (!calibration_running) return;
  if (cal_sample_count < CALIBRATION_SAMPLES) {
    cal_samples0[cal_sample_count] = adc0;
    cal_samples1[cal_sample_count] = adc1;
    cal_sample_count++;
    if (cal_sample_count == CALIBRATION_SAMPLES) {
      finishCalibration();
    }
  }
}

uint16_t median(uint16_t *arr, int n) {
  // Simple bubble sort for small array (n=100 is fine)
  uint16_t sorted[n];
  for (int i = 0; i < n; i++) sorted[i] = arr[i];
  for (int i = 0; i < n-1; i++) {
    for (int j = i+1; j < n; j++) {
      if (sorted[i] > sorted[j]) {
        uint16_t tmp = sorted[i];
        sorted[i] = sorted[j];
        sorted[j] = tmp;
      }
    }
  }
  return sorted[n/2];
}

void finishCalibration() {
  uint16_t new_center0 = median(cal_samples0, CALIBRATION_SAMPLES);
  uint16_t new_center1 = median(cal_samples1, CALIBRATION_SAMPLES);
  
  Serial.print("Calibration results: ");
  Serial.print(new_center0);
  Serial.print(", ");
  Serial.println(new_center1);
  
  // Check tolerance against previous calibration (if valid)
  if (cal_valid) {
    if (abs((int)new_center0 - (int)cal_center0) <= TOLERANCE &&
        abs((int)new_center1 - (int)cal_center1) <= TOLERANCE) {
      cal_center0 = new_center0;
      cal_center1 = new_center1;
      saveCalibration();
      Serial.println("Calibration accepted (within tolerance) and saved.");
    } else {
      Serial.println("Calibration out of tolerance (±100). Keeping previous calibration.");
    }
  } else {
    // first calibration
    cal_center0 = new_center0;
    cal_center1 = new_center1;
    saveCalibration();
    cal_valid = true;
    Serial.println("Initial calibration saved.");
  }
  
  calibration_running = false;
}

// =========================================================
// MCP2515 RECOVERY
// =========================================================
void canRecover() {
  mcp2515.reset();
  delay(10);
  // IMPORTANT: Set correct crystal frequency (8MHz or 16MHz)
  mcp2515.setBitrate(CAN_500KBPS, MCP_8MHZ);
  mcp2515.setNormalMode();
  send_fail_count = 0;
}

// =========================================================
// SEND TORQUE FRAME (0x220) with calibrated centers
// =========================================================
void sendTorque() {
  // Clamp steering to safe physical limits
  int clamped_steer = constrain(steer, -MAX_STEER_CMD, MAX_STEER_CMD);
  
  // Compute channel values using calibrated centers
  int32_t ch0_raw = cal_center0 + clamped_steer;
  int32_t ch1_raw = cal_center1 - clamped_steer;
  
  // Constrain to 12-bit ADC range
  uint16_t ch0 = constrain(ch0_raw, 0, 4095);
  uint16_t ch1 = constrain(ch1_raw, 0, 4095);
  
  txMsg.can_id = 0x220;
  txMsg.can_dlc = 8;
  memset(txMsg.data, 0, 8);
  
  txMsg.data[1] = ch0 & 0xFF;
  txMsg.data[2] = ch0 >> 8;
  txMsg.data[3] = ch1 & 0xFF;
  txMsg.data[4] = ch1 >> 8;
  
  txMsg.data[5] = 0x80 | (counter & 0x0F);   // enable + counter
  
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

// =========================================================
// SEND SPEED FRAME (0x76)
// =========================================================
void sendSpeed() {
  uint16_t sp = constrain(speed, 0, 655) * 100;
  
  txMsg.can_id = 0x76;
  txMsg.can_dlc = 8;
  memset(txMsg.data, 0, 8);
  
  txMsg.data[5] = sp & 0xFF;
  txMsg.data[6] = sp >> 8;
  txMsg.data[7] = counter & 0x0F;
  
  mcp2515.sendMessage(&txMsg);   // no error check for speed
}

// =========================================================
// READ TELEMETRY (0x221) and collect calibration samples
// =========================================================
void readTelemetry() {
  while (mcp2515.readMessage(&rxMsg) == MCP2515::ERROR_OK) {
    if (rxMsg.can_id == 0x221) {
      rx_count++;
      
      uint16_t adc0 = rxMsg.data[1] | (rxMsg.data[2] << 8);
      uint16_t adc1 = rxMsg.data[3] | (rxMsg.data[4] << 8);
      
      uint8_t override_flag = rxMsg.data[5];
      uint8_t fault = (rxMsg.data[7] >> 4) & 0x0F;
      uint8_t relay = (fault == 0 && abs(steer) > 0) ? 1 : 0;
      
      // If calibration is active, collect this sample
      if (calibration_running) {
        addCalibrationSample(adc0, adc1);
      }
      
      // Output telemetry to serial (for Python GUI)
      Serial.printf("TEL,%u,%u,%u,%u,%u,%u\n",
                    adc0, adc1, override_flag, fault, counter, relay);
    }
  }
}

// =========================================================
// ERROR LED INDICATOR
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
    if (now - last_blink >= 200) {   // 5 Hz blink
      last_blink = now;
      led_state = !led_state;
      digitalWrite(LED_ERR, led_state);
    }
  }
}

// =========================================================
// SETUP
// =========================================================
void setup() {
  Serial.begin(115200);
  pinMode(LED_ERR, OUTPUT);
  digitalWrite(LED_ERR, LOW);
  
  SPI.begin(MCP_SCK, MCP_MISO, MCP_MOSI, MCP_CS);
  canRecover();
  
  EEPROM.begin(EEPROM_SIZE);
  loadCalibration();
  
  last_cmd_time = millis();
  
  // Auto-calibrate if no valid calibration exists
  if (!cal_valid) {
    Serial.println("No calibration found. Starting auto-calibration...");
    startCalibration();
  } else {
    Serial.println("Ready. Send 'CAL' to recalibrate.");
  }
}

// =========================================================
// MAIN LOOP (50 Hz)
// =========================================================
void loop() {
  // ---------- Handle Serial Commands ----------
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    
    if (line == "CAL") {
      startCalibration();
    }
    else if (line.startsWith("CMD,")) {
      int s, sp;
      if (sscanf(line.c_str(), "CMD,%d,%d", &s, &sp) == 2) {
        steer = constrain(s, -MAX_STEER_CMD, MAX_STEER_CMD);
        speed = constrain(sp, 0, 655);
        last_cmd_time = millis();   // reset watchdog
      }
    }
  }
  
  // ---------- Serial Watchdog ----------
  if (millis() - last_cmd_time > CMD_TIMEOUT_MS) {
    steer = 0;
    speed = 0;
  }
  
  // ---------- CAN Communication ----------
  sendTorque();
  sendSpeed();
  readTelemetry();
  
  // ---------- Update Counters and LED ----------
  counter = (counter + 1) & 0x0F;
  updateErrorLed();
  
  delay(20);   // 50 Hz loop
}

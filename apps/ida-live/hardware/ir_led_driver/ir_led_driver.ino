// IDA Live - external IR LED driver
// For an Arduino Uno or Nano (ATmega328P). Drives one 850 nm LED through a
// transistor or constant-current driver on pin 9. See docs/HARDWARE.md for wiring.
//
// The app never times pulses itself: it queues a pattern, then says "go", and this
// board times every edge with micros(). The limits below are enforced here as
// well as in the app, so a bad pattern is refused even if the app is wrong.
//
// Serial protocol at 115200 baud, one command per line:
//   P <on_us> <off_us> <count> <pwm0-255>   queue a run of identical pulses
//   G                                        execute the queue, then clear it
//   X                                        abort now (LED off)
//   L                                        report limits
// Replies: "S <micros>" when a pattern starts, "D <micros>" when it ends,
//          "E <reason>" when a command is refused, "K" after a successful queue.

#include <Arduino.h>

const uint8_t LED_PIN = 9;                 // Timer1 PWM pin on Uno/Nano
const uint8_t MAX_PWM = 255;               // lower this to cap brightness in hardware
const unsigned long MAX_ON_TOTAL_MS = 30000UL;   // most light-on time per "G"
const unsigned long MIN_REST_MS = 500UL;         // enforced pause between patterns
const uint8_t MAX_RUNS = 32;

struct Run { unsigned long on_us, off_us, count; uint8_t pwm; };
Run queue_[MAX_RUNS];
uint8_t nRuns = 0;
unsigned long lastEndMs = 0;
char line[64];
uint8_t len = 0;

void ledOff() { analogWrite(LED_PIN, 0); digitalWrite(LED_PIN, LOW); }

void setup() {
  pinMode(LED_PIN, OUTPUT);
  ledOff();
  // Move pin 9/10 PWM from ~490 Hz to ~31 kHz so dimming does not add a
  // low-frequency flicker that could leak into (or alias onto) the EEG.
  TCCR1B = (TCCR1B & 0b11111000) | 0x01;
  Serial.begin(115200);
  Serial.println("READY ida-led 1");
}

bool abortRequested() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == 'X') return true;
  }
  return false;
}

// wait with the LED held at a level, checking for abort; returns false if aborted
bool hold(uint8_t pwm, unsigned long us) {
  if (pwm == 0) ledOff(); else analogWrite(LED_PIN, pwm);
  unsigned long t0 = micros();
  while ((unsigned long)(micros() - t0) < us) {
    if (us > 2000 && abortRequested()) { ledOff(); return false; }
  }
  return true;
}

void execute() {
  unsigned long onTotalMs = 0;
  for (uint8_t i = 0; i < nRuns; i++) onTotalMs += (queue_[i].on_us / 1000UL) * queue_[i].count;
  if (onTotalMs > MAX_ON_TOTAL_MS) { Serial.println("E pattern exceeds MAX_ON_TOTAL_MS"); nRuns = 0; return; }
  if (millis() - lastEndMs < MIN_REST_MS && lastEndMs != 0) { Serial.println("E rest period not over"); nRuns = 0; return; }
  Serial.print("S "); Serial.println(micros());
  bool ok = true;
  for (uint8_t i = 0; i < nRuns && ok; i++) {
    for (unsigned long k = 0; k < queue_[i].count && ok; k++) {
      ok = hold(queue_[i].pwm, queue_[i].on_us) && hold(0, queue_[i].off_us);
    }
  }
  ledOff();
  lastEndMs = millis();
  nRuns = 0;
  if (ok) { Serial.print("D "); Serial.println(micros()); }
  else Serial.println("E aborted");
}

void handle(char *s) {
  if (s[0] == 'P') {
    unsigned long on_us, off_us, count; unsigned int pwm;
    if (sscanf(s + 1, "%lu %lu %lu %u", &on_us, &off_us, &count, &pwm) != 4) { Serial.println("E bad P"); return; }
    if (nRuns >= MAX_RUNS) { Serial.println("E queue full"); return; }
    if (pwm > MAX_PWM) pwm = MAX_PWM;
    queue_[nRuns++] = {on_us, off_us, count, (uint8_t)pwm};
    Serial.println("K");
  } else if (s[0] == 'G') {
    execute();
  } else if (s[0] == 'X') {
    ledOff(); nRuns = 0; Serial.println("E aborted");
  } else if (s[0] == 'L') {
    Serial.print("LIMITS max_pwm="); Serial.print(MAX_PWM);
    Serial.print(" max_on_ms="); Serial.print(MAX_ON_TOTAL_MS);
    Serial.print(" min_rest_ms="); Serial.println(MIN_REST_MS);
  }
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (len) { line[len] = 0; handle(line); len = 0; }
    } else if (len < sizeof(line) - 1) {
      line[len++] = c;
    }
  }
}

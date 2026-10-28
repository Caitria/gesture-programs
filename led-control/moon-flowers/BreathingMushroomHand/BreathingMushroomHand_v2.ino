// Breathing Mushroom — HAND CONTROL edition (v5), Oct 26 2026
// Same wiring as v4 — nothing on the breadboard changes:
//   LED 1: red ~3, green ~5, blue ~6      LED 2: red ~9, green ~10, blue ~11
//   Both commons -> 5V hub. COMMON ANODE = true. 220 ohm per colour leg.
//
// What v5 adds: the Uno listens on USB serial (9600 baud) for hand
// commands sent by mushroom_hand.py on the Mac, which watches your
// hand through the camera (same MediaPipe stack as the morning's
// hand-controlled LED build — in fact this is that build, grown up).
//
// Command format (one per line):
//   G <color> <intensity> <period>
//       color     0..1000   position on the colour journey
//                           (0 = cyan end, 1000 = magenta-violet end)
//       intensity 0..255    pulse strength (peak brightness)
//       period    1200..9000  breath cadence in milliseconds
//   P                       pause: freeze both mushrooms exactly as
//                           they are (the script sends this while
//                           exactly one hand is up). Any G or A
//                           unpauses. If P and G both stop arriving
//                           (hands hidden), the pause times out
//                           after 3.5 s and the autonomous show
//                           resumes — hiding your hands = resume.
//   A                       back to autonomous breathing (the v4 show)
//
// Hand mode stays active while G lines keep arriving (the script
// sends them many times a second). If no G arrives for 3.5 seconds —
// hand left the frame, script quit, cable out — the mushrooms fall
// back to autonomous breathing on their own. They never sit frozen.
//
// In hand mode the colour is yours and it still pulses: the pulse
// swings between a dim floor and your intensity, at your cadence.
// LED 2 pulses half a cycle behind LED 1, as before.

#include <math.h>

const byte LED1_RED = 3,  LED1_GREEN = 5,  LED1_BLUE = 6;
const byte LED2_RED = 9,  LED2_GREEN = 10, LED2_BLUE = 11;

const bool COMMON_ANODE = true;  // verified for your LEDs — do not set to false
const float BRIGHTNESS = 0.6;
const float BREATH_PERIOD = 4200.0;
const float COLOR_PERIOD  = 18000.0;

const unsigned long LED2_BREATH_OFFSET = 2100;
const unsigned long LED2_COLOR_OFFSET  = 9000;

const unsigned long HAND_TIMEOUT = 3500;  // ms without a G line -> auto

// ---- hand-mode state -------------------------------------------------
bool handMode = false;
bool paused = false;
unsigned long lastHandMs = 0;
float handColor = 0.0;        // journey position 0..3 (smoothed); 3 = magenta end, no wrap
float handColorTarget = 0.0;
int   handIntensity = 200;    // 0..255
long  handPeriod = 4200;      // ms per breath

void setChannel(byte pin, int value) {
  value = constrain(value, 0, 255);
  analogWrite(pin, COMMON_ANODE ? 255 - value : value);
}

void setLED(byte rPin, byte gPin, byte bPin, int r, int g, int b) {
  setChannel(rPin, r);
  setChannel(gPin, g);
  setChannel(bPin, b);
}

void flashTest(byte rPin, byte gPin, byte bPin) {
  setLED(rPin, gPin, bPin, 220, 0, 0);
  delay(600);
  setLED(rPin, gPin, bPin, 0, 220, 0);
  delay(600);
  setLED(rPin, gPin, bPin, 0, 0, 220);
  delay(600);
  setLED(rPin, gPin, bPin, 0, 0, 0);
  delay(400);
}

void setup() {
  pinMode(LED1_RED, OUTPUT);
  pinMode(LED1_GREEN, OUTPUT);
  pinMode(LED1_BLUE, OUTPUT);
  pinMode(LED2_RED, OUTPUT);
  pinMode(LED2_GREEN, OUTPUT);
  pinMode(LED2_BLUE, OUTPUT);
  setLED(LED1_RED, LED1_GREEN, LED1_BLUE, 0, 0, 0);
  setLED(LED2_RED, LED2_GREEN, LED2_BLUE, 0, 0, 0);

  Serial.begin(9600);

  // Power-on flash test, same as v4: LED 1 red/green/blue, then LED 2.
  flashTest(LED1_RED, LED1_GREEN, LED1_BLUE);
  flashTest(LED2_RED, LED2_GREEN, LED2_BLUE);
}

// The colour journey: four stops, travelled in order, then back.
const int STOPS[4][3] = {
  {   0, 230, 210 },  // cyan
  {   0,  90, 255 },  // azure
  { 120,   0, 255 },  // violet
  { 215,   0, 185 }   // magenta-violet
};

// Colour at a journey position (0..4, wraps). Writes into out[3].
void journeyColor(float pos, int out[3]) {
  int from = ((int)pos) % 4;
  int to = (from + 1) % 4;
  float frac = pos - (int)pos;
  for (int i = 0; i < 3; i++) {
    out[i] = (int)(STOPS[from][i] + (STOPS[to][i] - STOPS[from][i]) * frac);
  }
}

// ---- serial ----------------------------------------------------------
// Read any complete lines waiting. G sets hand targets; A leaves hand
// mode immediately. Anything else is ignored.
void readSerial() {
  static char buf[40];
  static int len = 0;
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (len > 0) {
        buf[len] = '\0';
        if (buf[0] == 'G') {
          int color, intensity;
          long period;
          if (sscanf(buf + 1, "%d %d %ld", &color, &intensity, &period) == 3) {
            handColorTarget = constrain(color, 0, 1000) / 1000.0 * 3.0;
            handIntensity = constrain(intensity, 0, 255);
            handPeriod = constrain(period, 1200L, 9000L);
            handMode = true;
            paused = false;
            lastHandMs = millis();
          }
        } else if (buf[0] == 'P') {
          paused = true;
          lastHandMs = millis();
        } else if (buf[0] == 'A') {
          handMode = false;
          paused = false;
        }
        len = 0;
      }
    } else if (len < (int)sizeof(buf) - 1) {
      buf[len++] = c;
    }
  }
}

// ---- autonomous mode (the v4 show, unchanged) ------------------------
void runAuto(byte rPin, byte gPin, byte bPin, unsigned long t) {
  float breathPhase = 2.0 * PI * (t % (unsigned long)BREATH_PERIOD) / BREATH_PERIOD;
  float breath = (sin(breathPhase - PI / 2.0) + 1.0) / 2.0;
  breath = 0.04 + 0.96 * breath;

  float pos = ((t % (unsigned long)COLOR_PERIOD) / COLOR_PERIOD) * 4.0;
  int col[3];
  journeyColor(pos, col);

  setLED(rPin, gPin, bPin,
         (int)(col[0] * breath * BRIGHTNESS),
         (int)(col[1] * breath * BRIGHTNESS),
         (int)(col[2] * breath * BRIGHTNESS));
}

// ---- hand mode -------------------------------------------------------
void runHand(byte rPin, byte gPin, byte bPin, unsigned long t,
             unsigned long phaseOffset) {
  float phase = 2.0 * PI * ((t + phaseOffset) % (unsigned long)handPeriod)
              / (float)handPeriod;
  float wave = (sin(phase - PI / 2.0) + 1.0) / 2.0;   // 0..1, starts low
  float pulse = 0.10 + 0.90 * wave;                  // dim floor, never off
  float scale = pulse * (handIntensity / 255.0);

  int col[3];
  journeyColor(handColor, col);
  setLED(rPin, gPin, bPin,
         (int)(col[0] * scale),
         (int)(col[1] * scale),
         (int)(col[2] * scale));
}

void loop() {
  readSerial();
  unsigned long now = millis();

  if ((handMode || paused) && now - lastHandMs > HAND_TIMEOUT) {
    handMode = false;  // hands gone — resume the autonomous show
    paused = false;
  }

  if (paused) {
    delay(15);
    return;  // outputs stay exactly as last written: a true freeze
  }

  if (handMode) {
    // Glide the colour toward the hand's target so it never jumps.
    handColor += (handColorTarget - handColor) * 0.08;
    runHand(LED1_RED, LED1_GREEN, LED1_BLUE, now, 0);
    runHand(LED2_RED, LED2_GREEN, LED2_BLUE, now, handPeriod / 2);
  } else {
    runAuto(LED1_RED, LED1_GREEN, LED1_BLUE, now);
    runAuto(LED2_RED, LED2_GREEN, LED2_BLUE,
            now + LED2_COLOR_OFFSET + LED2_BREATH_OFFSET);
  }
  delay(15);
}

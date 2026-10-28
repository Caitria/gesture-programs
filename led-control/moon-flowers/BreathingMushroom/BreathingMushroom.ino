// Breathing Mushroom — adapted for Caitria's setup, Oct 25 2026
// Board for prototype: genuine Arduino Uno R3 (already working today)
// LEDs: CHANZON 5mm clear RGB, COMMON ANODE (confirmed from bag photo Oct 25)
//   Common (longest leg) of EACH LED -> shared 5V hub strip on the board
//   Each colour leg -> its own 220 ohm resistor -> its own Uno pin
//   The Uno pins SINK current, so the code inverts the values (COMMON_ANODE = true)
// Resistors: 220 ohm x6 (from your taped "220" strip — NOT the 10M ohm bag)
//
// v4 (Oct 25 evening): SECOND RGB LED added.
//   LED 1: red ~3, green ~5, blue ~6      (rows 12-15, as built)
//   LED 2: red ~9, green ~10, blue ~11    (rows 18-21, same pattern)
// These are all six of the Uno's fading (PWM) pins — this is the
// direct-pin maximum for one Uno.
// The two mushrooms run the same colour journey and breathing, but
// LED 2 is offset by half a cycle on both, so the pair looks like two
// living things rather than one light mirrored. To make them match
// exactly instead, set both OFFSET values below to 0.
// Flash test now covers both LEDs in turn: LED 1 red/green/blue,
// then LED 2 red/green/blue, 600 ms each.

#include <math.h>

const byte LED1_RED = 3,  LED1_GREEN = 5,  LED1_BLUE = 6;
const byte LED2_RED = 9,  LED2_GREEN = 10, LED2_BLUE = 11;

const bool COMMON_ANODE = true;  // verified for your LEDs — do not set to false
const float BRIGHTNESS = 0.6;
const float BREATH_PERIOD = 4200.0;   // ~4.2 seconds per breath
const float COLOR_PERIOD  = 18000.0;  // ~18 seconds for the full colour journey

const unsigned long LED2_BREATH_OFFSET = 2100;  // half a breath behind LED 1
const unsigned long LED2_COLOR_OFFSET  = 9000;  // half the journey behind LED 1

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

  // Power-on flash test: LED 1 red, green, blue — then LED 2 red,
  // green, blue. A colour that does not flash has a wiring fault on
  // that colour's row of that LED. The code has done its part.
  flashTest(LED1_RED, LED1_GREEN, LED1_BLUE);
  flashTest(LED2_RED, LED2_GREEN, LED2_BLUE);
}

// The colour journey: four stops, travelled in order, then back to the
// first. Each row is one stop: { red, green, blue }.
const int STOPS[4][3] = {
  {   0, 230, 210 },  // cyan        (green + blue, no red)
  {   0,  90, 255 },  // azure       (mostly blue)
  { 120,   0, 255 },  // violet      (blue + some red)
  { 215,   0, 185 }   // magenta-violet (red in front, blue turned down)
};

// Work out one LED's colour at a given moment and send it.
void runLED(byte rPin, byte gPin, byte bPin, unsigned long t) {
  float breathPhase = 2.0 * PI * (t % (unsigned long)BREATH_PERIOD) / BREATH_PERIOD;
  float breath = (sin(breathPhase - PI / 2.0) + 1.0) / 2.0;
  breath = 0.04 + 0.96 * breath;

  float pos = ((t % (unsigned long)COLOR_PERIOD) / COLOR_PERIOD) * 4.0;
  int from = (int)pos;
  int to = (from + 1) % 4;
  float frac = pos - from;

  int r = (int)((STOPS[from][0] + (STOPS[to][0] - STOPS[from][0]) * frac) * breath * BRIGHTNESS);
  int g = (int)((STOPS[from][1] + (STOPS[to][1] - STOPS[from][1]) * frac) * breath * BRIGHTNESS);
  int b = (int)((STOPS[from][2] + (STOPS[to][2] - STOPS[from][2]) * frac) * breath * BRIGHTNESS);

  setLED(rPin, gPin, bPin, r, g, b);
}

void loop() {
  unsigned long now = millis();
  runLED(LED1_RED, LED1_GREEN, LED1_BLUE, now);
  runLED(LED2_RED, LED2_GREEN, LED2_BLUE, now + LED2_COLOR_OFFSET + LED2_BREATH_OFFSET);
  delay(20);
}

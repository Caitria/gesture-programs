// Hand-controlled LED — Uno side
// Receives commands from the computer over USB serial at 9600 baud:
//   C0 .. C5   = how many fingers are up -> light that many LEDs (pins 8-12)
//   B0 .. B255 = pinch brightness -> PWM brightness of the LED on pin 9
// The built-in LED on pin 13 lights whenever a hand is seen (count >= 1).
// Wiring for the 5 LEDs: pin -> 220 ohm resistor -> LED long leg (+),
// LED short leg (-) -> GND rail. See PLAN.md, Stage 2.
//
// How commands are read (v3, Oct 25): one byte at a time, no waiting
// for line endings and no Serial.parseInt(). A letter arms the parser;
// the next digit acts IMMEDIATELY (for C). Brightness digits collect
// until 400 ms pass with no new digit, then apply. v1 waited for a
// newline some tools never send; v2's parseInt() repeatedly produced
// count=0 for a sent C5 on Caitria's machine, for a reason not visible
// from outside — so v3 also REPORTS every byte it receives:
//   rx 67 'C'      <- each received byte, as number and character
// That echo turns "what is actually on the wire" into evidence instead
// of guesswork. Receipts (count= / bright=) still print per command.

const int LED_PINS[5] = {8, 9, 10, 11, 12};
const int BUILTIN = 13;

char pending = 0;              // 'C' or 'B' while awaiting digits
int  pendingValue = 0;         // digits collected so far (for B)
bool pendingHasDigit = false;
unsigned long lastDigitAt = 0;

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < 5; i++) pinMode(LED_PINS[i], OUTPUT);
  pinMode(BUILTIN, OUTPUT);
  // Power-on test: chase once so you know the wiring works before
  // the computer is even involved.
  for (int i = 0; i < 5; i++) { digitalWrite(LED_PINS[i], HIGH); delay(120); }
  for (int i = 0; i < 5; i++) { digitalWrite(LED_PINS[i], LOW); }
  Serial.println("uno-ready");
}

void showCount(int count) {
  for (int i = 0; i < 5; i++) {
    digitalWrite(LED_PINS[i], i < count ? HIGH : LOW);
  }
  digitalWrite(BUILTIN, count > 0 ? HIGH : LOW);
}

void applyPending() {
  if (pending == 'B' && pendingHasDigit) {
    int value = constrain(pendingValue, 0, 255);
    analogWrite(9, value);  // pin 9 is a PWM pin on the Uno: it can dim
    Serial.print("bright=");
    Serial.println(value);
  }
  pending = 0;
  pendingValue = 0;
  pendingHasDigit = false;
}

void loop() {
  // Brightness applies once its digits stop arriving.
  if (pending == 'B' && pendingHasDigit &&
      millis() - lastDigitAt > 400) {
    applyPending();
  }

  if (!Serial.available()) return;
  int b = Serial.read();

  // Report the byte, whatever it is.
  Serial.print("rx ");
  Serial.print(b);
  if (b >= 32 && b < 127) {
    Serial.print(" '");
    Serial.print((char)b);
    Serial.print("'");
  }
  Serial.println();

  if (b == 'C' || b == 'c' || b == 'B' || b == 'b') {
    applyPending();  // finish any half-typed brightness first
    pending = (b == 'C' || b == 'c') ? 'C' : 'B';
    pendingValue = 0;
    pendingHasDigit = false;
  } else if (b >= '0' && b <= '9' && pending) {
    int digit = b - '0';
    if (pending == 'C') {
      showCount(digit);
      Serial.print("count=");
      Serial.println(digit);
      pending = 0;
    } else {  // 'B': brightness can be several digits
      pendingValue = pendingValue * 10 + digit;
      pendingHasDigit = true;
      lastDigitAt = millis();
    }
  }
  // Any other byte (endings, spaces, stray text) is reported above
  // and otherwise ignored.
}

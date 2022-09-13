
#include <Servo.h>

Servo LickSwapper;

int pos = 0;

String Program = "Lick Spout Swapping Servo";
int servoOutPin = 3;
int servoRelayIn = 7;

void setup() {
  // put your setup code here, to run once:
  pinMode(servoOutPin, OUTPUT);
  pinMode(servoRelayIn, INPUT);
  Serial.begin(38400);
  Serial.println(Programname);
  LickSwapper.attach(servoOutPin);
}

void loop() {
  // put your main code here, to run repeatedly:

  if (digitalRead(servoRelayIn)==HIGH) {
    Serial.println("HIGH");
    LickSwapper.write(180);
    delay(100);
    
  }
  else if (digitalRead(servoRelayIn)==LOW) {
    Serial.println("LOW");
    LickSwapper.write(0);
    delay(100);
  }
  else {
    Serial.println("CONFUSED");
  }
}


#include <Servo.h>

Servo LickSwapper;
Servo LickRemover

// String Program = "Lick Spout Swapping Servo";
int servo_swapper_out = 3;
int servo_swapper_in = 7;
int servo_remover_out = 5;
int servo_remover_in = 9 ;

void setup() {
  pinMode(servo_swapper_out, OUTPUT);
  pinMode(servo_swapper_in, INPUT);
  pinMode(servo_remover_out, OUTPUT);
  pinMode(servo_remover_in, INPUT);

  // Serial.begin(38400);
  // Serial.println(Program);
  LickSwapper.attach(servo_swapper_in);
  LickRemover.attach(servo_remover_out);
}

void loop() {

  if (digitalRead(servo_swapper_in)==HIGH) {
    // Serial.println("HIGH");
    LickSwapper.write(180);
    delay(100);
    
  }
  else if (digitalRead(servo_swapper_in)==LOW) {
    // Serial.println("LOW");
    LickSwapper.write(0);
    delay(100);
  }
  else {
    // Serial.println("CONFUSED");
  }

  if (digitalRead(servo_remover_in)==HIGH) {
        LickRemover.write(180);
        delay(100);
  }
  else if (digitalRead(servo_remover_in)==LOW) {
        LickRemover.write(0);
        delay(100);
  }
  else {
    // Serial.println("CONFUSED");
  }
}

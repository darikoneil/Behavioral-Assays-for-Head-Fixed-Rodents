String Program = "Reward Delivery System";

// Behavioral Parameters
long reward_duration = 6533;
long reward_sucrose_start = 0;
long reward_water_start = 0;

// Digital Pins
int delivered_sucrose_pin = 13;
int delivered_water_pin = 12;
int licked_sucrose_pin = 11;
int licked_water_pin = 10;
int trigger_sucrose_pin = 9;
int trigger_water_pin = 8;
int sucrose_cap_touch_pin = 7;
int water_cap_touch_pin = 6;
int sucrose_calibration_pin = 5;
int water_calibration_pin = 4;

// Debouncing
int num_sucrose_reading = 0;
int num_water_reading = 0;

// booleans or pseudo-booleans
int sucrose_licking = 0; // 0 is False, 1 is True
int water_licking = 0 ; // 0 is False, 1 is True
int rewarding_sucrose = 0; // 0 is False, 1 is True
int rewarding_water = 0; // 0 is False, 1 is True

// Parameters
int signals_per_reward = 4;
int reading_period = 5;
int rolling_sucrose_licks = 0;
int rolling_water_licks = 0;
long calibration_duration = reward_duration * 333;
int rewarding_calibration = 0;
long calib_start = 0;

void setup() {
    pinMode(delivered_sucrose_pin, OUTPUT);
    pinMode(delivered_water_pin, OUTPUT);
    pinMode(licked_sucrose_pin, OUTPUT);
    pinMode(licked_water_pin, OUTPUT);
    pinMode(trigger_sucrose_pin, OUTPUT);
    pinMode(trigger_water_pin, OUTPUT);
    pinMode(sucrose_cap_touch_pin, INPUT);
    pinMode(water_cap_touch_pin, INPUT);
    pinMode(water_calibration_pin, INPUT);
    pinMode(sucrose_calibration_pin, INPUT);
    

    Serial.begin(38400);
    Serial.println(Program);
}

void loop() {

    if(rewarding_sucrose == 1){
        checkTerminateSucrose();
    }
    else if(rewarding_water == 1){
        checkTerminateWater();
    }
    else if (rewarding_calibration == 1){
        checkTerminateCalibration();
    }
    else {
        checkSucrose();
        checkWater();
        checkCalibration();
    }
}

void checkSucrose() {
        ++num_sucrose_reading;
        sucrose_licking = digitalRead(sucrose_cap_touch_pin);
        rolling_sucrose_licks = rolling_sucrose_licks + sucrose_licking;
         // Alert licking
         if (sucrose_licking){
         digitalWrite(licked_sucrose_pin, HIGH);
         Serial.println("LICKED SUCROSE");
         }
         else {
         digitalWrite(licked_sucrose_pin, LOW);
         }
        // Check every 5th reading
        if (num_sucrose_reading == reading_period) {
            if (rolling_sucrose_licks > signals_per_reward){
            deliverSucrose();
            }
            num_sucrose_reading = 0;
            rolling_sucrose_licks = 0;
        }
}

void checkWater() {
        ++num_water_reading;
        water_licking = digitalRead(water_cap_touch_pin);
        rolling_water_licks = rolling_water_licks + water_licking;
         // Alert licking
         if (water_licking){
         digitalWrite(licked_water_pin, HIGH);
         Serial.println("LICKED WATER");
         }
         else {
         digitalWrite(licked_water_pin, LOW);
         }
        // Check every 5th reading
        if (num_water_reading == reading_period) {
            if (rolling_water_licks > signals_per_reward){
            deliverWater();
            }
            num_water_reading = 0;
            rolling_water_licks = 0;
        }

}

void deliverSucrose(){
    Serial.println("REWARDING SUCROSE - NC");
    reward_sucrose_start = micros();
    digitalWrite(trigger_sucrose_pin, HIGH);
    digitalWrite(delivered_sucrose_pin, HIGH);
    rewarding_sucrose = 1;
}

void deliverWater(){
      Serial.println("REWARDING WATER -NC");
       reward_water_start = micros();
       digitalWrite(trigger_water_pin, HIGH);
       digitalWrite(delivered_water_pin, HIGH);
       rewarding_water = 1;
}

void checkTerminateSucrose(){
    if((micros()-reward_sucrose_start) > reward_duration){
        digitalWrite(trigger_sucrose_pin, LOW);
        digitalWrite(delivered_sucrose_pin, LOW);
        rewarding_sucrose = 0;
    }
}

void checkTerminateWater(){
    if((micros()-reward_water_start) > reward_duration){
        digitalWrite(trigger_water_pin, LOW);
        digitalWrite(delivered_water_pin, LOW);
        rewarding_water = 0;
    }
}

void checkCalibration() {
       if (digitalRead(water_calibration_pin)==HIGH) {
        
          if (rewarding_calibration==0) {
           //Serial.println("REWARDING WATER");
              rewarding_calibration = 1;
              calib_start = micros();
              digitalWrite(trigger_water_pin, HIGH);
              digitalWrite(delivered_water_pin, HIGH);
          }
       }
      if (digitalRead(sucrose_calibration_pin)==HIGH) {

        if (rewarding_calibration==0) {
          //Serial.println("REWARDING SUCROSE");
              rewarding_calibration = 1;
              calib_start = micros();
             digitalWrite(trigger_sucrose_pin, HIGH);
             digitalWrite(delivered_sucrose_pin, HIGH);
        }
      }
}

void checkTerminateCalibration() {
  if ((micros()-calib_start) > calibration_duration) {
    digitalWrite(trigger_water_pin, LOW);
    digitalWrite(trigger_sucrose_pin, LOW);
    digitalWrite(delivered_water_pin, LOW);
    digitalWrite(delivered_sucrose_pin, LOW);
    rewarding_calibration = 2;
  }
}

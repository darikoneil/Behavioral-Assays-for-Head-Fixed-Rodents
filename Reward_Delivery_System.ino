String Program = "Reward Delivery System";

// Behavioral Parameters
int reward_duration = 30;
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

void setup() {
    pinMode(delivered_sucrose_pin, OUTPUT);
    pinMode(delivered_water_pin, OUTPUT);
    pinMode(licked_sucrose_pin, OUTPUT);
    pinMode(licked_water_pin, OUTPUT);
    pinMode(trigger_sucrose_pin, OUTPUT);
    pinMode(trigger_water_pin, OUTPUT);
    pinMode(sucrose_cap_touch_pin, INPUT);
    pinMode(water_cap_touch_pin, INPUT);

    // Serial.begin(38400);
    //Serial.println(Program);
}

void loop() {

    if(rewarding_sucrose == 1){
        checkTerminateSucrose;
    }
    else if(reward_water_start == 1){
        checkTerminateWater;
    }
    else {
        checkSucrose();
        checkWater();
    }

}

void checkSucrose() {
        ++num_sucrose_reading;
        sucrose_licking = digitalRead(sucrose_cap_touch_pin);
        rolling_sucrose_licks = rolling_sucrose_licks + sucrose_licking;
         // Alert licking
         if (sucrose_licking){
         digitalWrite(licked_sucrose_pin, HIGH);
         }
         else {
         digitalWrite(licked_sucrose_pin, LOW);
         }
        // Check every 5th reading
        if (num_sucrose_reading == reading_period) {
            if (rolling_sucrose_licks > signals_per_reward){
            deliverSucrose();
            }
        }
        num_sucrose_reading = 0;
        rolling_sucrose_licks = 0;
}

void checkWater() {
        ++num_water_reading;
        water_licking = digitalRead(water_cap_touch_pin);
        rolling_water_licks = rolling_water_licks + water_licking;
         // Alert licking
         if (water_licking){
         digitalWrite(licked_water_pin, HIGH);
         }
         else {
         digitalWrite(licked_water_pin, LOW);
         }
        // Check every 5th reading
        if (num_water_reading == reading_period) {
            if (rolling_water_licks > signals_per_reward){
            deliverWater();
            }
        }
        num_water_reading = 0;
        rolling_water_licks = 0;
}

void deliverSucrose(){
    reward_sucrose_start = millis();
    digitalWrite(trigger_sucrose_pin, HIGH);
    digitalWrite(delivered_sucrose_pin, HIGH);
    rewarding_sucrose = 1;
}

void deliverWater(){
       reward_water_start = millis();
       digitalWrite(trigger_water_pin, HIGH);
       digitalWrite(delivered_water_pin, HIGH);
       rewarding_water = 1;
}

void checkTerminateSucrose(){
    if((millis()-reward_sucrose_start) > reward_duration){
        digitalWrite(trigger_sucrose_pin, LOW);
        digitalWrite(delivered_sucrose_pin, LOW);
    }
}

void checkTerminateWater(){
    if((millis()-reward_water_start) > reward_duration){
        digitalWrite(trigger_water_pin, LOW);
        digitalWrite(delivered_water_pin, LOW);
    }
}
String Program = "Reward Delivery System";

// Behavioral Parameters
long cycling_time = 8000; // Approximate Solenoid Turnover Time
long reward_dur_water = 12125 + cycling_time; // Calibrated Duration to leave water solenoid open
long reward_dur_sucrose = 10500 + cycling_time; // Calibrated Duration to leave sucrose solenoid open
long reward_water_start = 0; // Time (micros-seconds) since water reward started delivery
long reward_sucrose_start = 0; // Time (micros-seconds) since sucrose reward started delivery

// Digital Out Pins
int licked_water_pin = 31; // Signal to DAQ that water spout was licked
int licked_sucrose_pin = 29; // Signal to DAQ that sucrose spout was licked
int rewarded_water_pin = 27; // Signal to DAQ that water reward was delivered
int rewarded_sucrose_pin = 25; // Signal to DAQ that sucrose reward was delivered
int trigger_water_pin = 12; // Trigger delivery of water reward
int trigger_sucrose_pin = 13; // Trigger delivery of sucrose reward

// Digital In Pins
int permission_water_pin = 53; // Permits water reward triggering upon licking
int permission_sucrose_pin = 51; // Permits sucrose reward triggering upon licking
int water_cap_touch_pin = 49; // water cap touch input
int sucrose_cap_touch_pin = 47; // sucrose cpa touch input

// Servo Pins I/O
int request_swap_pin = 8; // request lick spout swap
int request_remove_pin = 9; // request lick spout removal
int command_swap_pin = 10; // servo command lick spout swap
int command_remove_pin = 11; // servo command lick spout removal

// Debouncing
int num_sucrose_reading = 0;
int num_water_reading = 0;

// booleans or pseudo-booleans
int sucrose_licking = 0; // 0 is False, 1 is True
int water_licking = 0 ; // 0 is False, 1 is True
int rewarding_sucrose = 0; // 0 is False, 1 is True
int rewarding_water = 0; // 0 is False, 1 is True

// Parameters
int signals_per_reward = 4; // must be 4 / 5
int reading_period = 5;
int rolling_sucrose_licks = 0;
int rolling_water_licks = 0;

// Setup Servos
#include <Servo.h>
Servo LickSwapper;
Servo LickRemover;
int swap_pos = 0;
int remove_pos = 0;

void setup() {
    // Rewards I/O
    pinMode(licked_water_pin, OUTPUT);
    pinMode(licked_sucrose_pin, OUTPUT);
    pinMode(rewarded_water_pin, OUTPUT);
    pinMode(rewarded_sucrose_pin, OUTPUT);
    pinMode(trigger_water_pin, OUTPUT);
    pinMode(trigger_sucrose_pin, OUTPUT);
    pinMode(permission_water_pin, INPUT);
    pinMode(permission_sucrose_pin, INPUT);
    pinMode(water_cap_touch_pin, INPUT);
    pinMode(sucrose_cap_touch_pin, INPUT);
    // Servo I/O
    pinMode(request_swap_pin, INPUT);
    pinMode(request_remove_pin, INPUT);
    pinMode(command_swap_pin, OUTPUT);
    pinMode(command_remove_pin, OUTPUT);
    LickSwapper.attach(command_swap_pin);
    LickRemover.attach(command_remove_pin);

    

    //Serial.begin(38400);
    Serial.println(Program);
}

void loop() {

    if(rewarding_sucrose == 1){
        checkTerminateSucrose();
    }

    if(rewarding_water == 1){
        checkTerminateWater();
    }

     checkSucrose();
     checkWater();
     checkSpoutSwap();
     checkSpoutRemove();
}

void checkSucrose() {
        if (rewarding_sucrose == 0) {
            ++num_sucrose_reading;
            sucrose_licking = digitalRead(sucrose_cap_touch_pin);
            rolling_sucrose_licks = rolling_sucrose_licks + sucrose_licking;
            // Alert licking
            // Check every 5th reading
            if (num_sucrose_reading == reading_period) {
                if (rolling_sucrose_licks > signals_per_reward){
                    // First alert licked
                    digitalWrite(licked_sucrose_pin, HIGH);
                    if (digitalRead(permission_sucrose_pin)==HIGH) {
                       deliverSucrose();
                    }
                }
                else {
                    digitalWrite(licked_sucrose_pin, LOW);
                }
            num_sucrose_reading = 0;
            rolling_sucrose_licks = 0;
            }

        }
}

void checkWater() {
        if (rewarding_water == 0) {
            ++num_water_reading;
            water_licking = digitalRead(water_cap_touch_pin);
            rolling_water_licks = rolling_water_licks + water_licking;
            // Check every 5th reading
            if (num_water_reading == reading_period) {
                if (rolling_water_licks > signals_per_reward){
                    // First alert licked
                    digitalWrite(licked_water_pin, HIGH);
                    if (digitalRead(permission_water_pin)==HIGH) {
                        deliverWater();
                    }
                }
                else {
                    digitalWrite(licked_water_pin, LOW);
                }
                num_water_reading = 0;
                rolling_water_licks = 0;
            }
        }
}

void deliverSucrose(){
    //Serial.println("REWARDING SUCROSE - NC");
    reward_sucrose_start = micros();
    digitalWrite(trigger_sucrose_pin, HIGH);
    digitalWrite(rewarded_sucrose_pin, HIGH);
    rewarding_sucrose = 1;
}

void deliverWater(){
      //Serial.println("REWARDING WATER -NC");
       reward_water_start = micros();
       digitalWrite(trigger_water_pin, HIGH);
       digitalWrite(rewarded_water_pin, HIGH);
       rewarding_water = 1;
}

void checkTerminateSucrose(){
    if((micros()-reward_sucrose_start) > reward_dur_sucrose){
        digitalWrite(trigger_sucrose_pin, LOW);
        digitalWrite(rewarded_sucrose_pin, LOW);
        rewarding_sucrose = 0;
    }
}

void checkTerminateWater(){
    if((micros()-reward_water_start) > reward_dur_water){
        digitalWrite(trigger_water_pin, LOW);
        digitalWrite(rewarded_water_pin, LOW);
        rewarding_water = 0;
    }
}

void checkSpoutSwap() {
    if (digitalRead(request_swap_pin)==HIGH) {
            if (swap_pos == 0) {
                LickSwapper.write(180);
                swap_pos = 180;
            }
            else if (swap_pos == 180) {
                LickSwapper.write(0);
                swap_pos = 0;
            }

    }

}

void checkSpoutRemove() {
    if (digitalRead(request_remove_pin)==HIGH) {
        if (remove_pos==0) {
            LickRemover.write(180);
            remove_pos = 180;
        }
        else if (remove_pos==180) {
            LickRemover.write(0);
            remove_pos = 0;
        }

    }
}

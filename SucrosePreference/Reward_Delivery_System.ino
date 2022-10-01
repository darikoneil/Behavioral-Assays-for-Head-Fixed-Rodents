// String Program = "Reward Delivery System";

// Behavioral Parameters
const long cycling_time = 8000; // Approximate Solenoid Turnover Time
const long reward_dur_water = 12125 + cycling_time; // Calibrated Duration to leave water solenoid open
const long reward_dur_sucrose = 10500 + cycling_time; // Calibrated Duration to leave sucrose solenoid open
long reward_water_start = 0; // Time (micros-seconds) since water reward started delivery
long reward_sucrose_start = 0; // Time (micros-seconds) since sucrose reward started delivery

// Digital Out Pins
const int licked_water_pin = 31; // Signal to DAQ that water spout was licked
const int licked_sucrose_pin = 29; // Signal to DAQ that sucrose spout was licked
const int rewarded_water_pin = 27; // Signal to DAQ that water reward was delivered
const int rewarded_sucrose_pin = 25; // Signal to DAQ that sucrose reward was delivered
const int trigger_water_pin = 12; // Trigger delivery of water reward
const int trigger_sucrose_pin = 13; // Trigger delivery of sucrose reward

// Digital In Pins
const int permission_water_pin = 53; // Permits water reward triggering upon licking
const int permission_sucrose_pin = 51; // Permits sucrose reward triggering upon licking
const int water_cap_touch_pin = 49; // water cap touch input
const int sucrose_cap_touch_pin = 47; // sucrose cap touch input
const int wet_start_water_pin = 45; // wet start water pin
const int wet_start_sucrose_pin = 43; // wet start sucrose pin

// Servo Pins I/O
const int request_swap_pin = 8; // request lick spout swap
const int request_remove_pin = 9; // request lick spout removal
const int command_swap_pin = 10; // servo command lick spout swap
const int command_remove_pin = 11; // servo command lick spout removal

// Debouncing
int num_sucrose_reading = 0; // current sucrose readings this period
int num_water_reading = 0; // current water readings this period

// booleans or pseudo-booleans
int sucrose_licking = 0; // 0 is False, 1 is True
int water_licking = 0 ; // 0 is False, 1 is True
int rewarding_sucrose = 0; // 0 is False, 1 is True
int rewarding_water = 0; // 0 is False, 1 is True

// Parameters
const int signals_per_reward = 4; // threshold for reward delivery per reading period
const int reading_period = 5; // number of reads per period
int rolling_sucrose_licks = 0; // rolling tally per period
int rolling_water_licks = 0; // rolling tally per period

// Setup Servos
#include <Servo.h>
Servo LickSwapper;
Servo LickRemover;
int swap_pos = 0; // current lick swapper position
int remove_pos = 0; // current lick remover position

// Circular Buffers (Commented Out, See Comment on Check Functions)
// #include <CircularBuffer.h>
// CircularBuffer<int, reading_period> water_buffer; // circular buffer for water readings
// CircularBuffer<int, reading_period> sucrose_buffer; // circular buffer for sucrose readings

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
    pinMode(wet_start_water_pin, INPUT);
    pinMode(wet_start_sucrose_pin, INPUT);
    // Servo I/O
    pinMode(request_swap_pin, INPUT);
    pinMode(request_remove_pin, INPUT);
    pinMode(command_swap_pin, OUTPUT);
    pinMode(command_remove_pin, OUTPUT);
    LickSwapper.attach(command_swap_pin);
    LickRemover.attach(command_remove_pin);

    

    // Serial.begin(38400);
    // Serial.println(Program);
}

void loop() {

    if(rewarding_sucrose == 1){
        checkTerminateSucrose(); // Don't bother calling these unless delivering
    }

    if(rewarding_water == 1){
        checkTerminateWater(); // Don't bother calling these unless delivering
    }

     checkWetStart();
     checkSucrose();
     checkWater();
     checkSpoutSwap();
     checkSpoutRemove();
}

void checkSucrose() {
        // Here we deliver sucrose if and only if:
            // there is not currently a reward
            // rolling sucrose licks > signals_per_reward
        // Note we only check the rolling licks every 5th reading
        // This is probably not the best way to do it
        // Below is a better implementation, but needs tested first
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

        //if (rewarding_sucrose == 0) {
        //    sucrose_buffer.push(digitalRead(sucrose_cap_touch_pin));
        //    if (sum(sucrose_buffer)>signals_per_reward) {
        //        digitalWrite(licked_sucrose_pin, HIGH);
        //        if (digitalRead(permission_sucrose_pin)==HIGH) {
        //            deliverSucrose();
        //        }
        //    }
}

void checkWater() {
        // Here we deliver water if and only if:
            // there is not currently a reward
            // rolling water licks > signals_per_reward
        // Note we only check the rolling licks every 5th reading
        // This is probably not the best way to do it
        // Below is a better implementation, but needs tested first
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
        //    if (rewarding_water == 0) {
        //    water_buffer.push(digitalRead(water_cap_touch_pin));
        //    if (sum(water_buffer)>signals_per_reward) {
        //        digitalWrite(licked_water_pin, HIGH);
        //        if (digitalRead(permission_water_pin)==HIGH) {
        //            deliverWater();
        //        }
        //    }
        //}

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

void checkWetStart() {
    if (rewarding_water == 0){
        if (digitalRead(wet_start_water_pin==HIGH)) {
            deliverWater();
        }
    }
    if (rewarding_sucrose == 0) {
        if (digitalRead(wet_start_sucrose_pin==HIGH)) {
            deliverSucrose();
        }
    }
}

//void sum(circular_buffer) {
//    // Here we calculate the sum (declared "value") of a circular buffer
//    int value;
//    for (int i=0; i < (circular_buffer.size()-1); ++i) {
//        value += b[i];
//    }
//    return value
//}

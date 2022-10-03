String Program = "Reward Delivery System";

// Behavioral Parameters
const long cycling_time = 8000; // Approximate Solenoid Turnover Time
const long reward_dur_water = 12125 + cycling_time; // Calibrated Duration to leave water solenoid open
const long reward_dur_sucrose = 10500 + cycling_time; // Calibrated Duration to leave sucrose solenoid open
const long wet_start_timeout_dur = 60000000; // Timeout for wet start
long reward_water_start = 0; // Time (micros-seconds) since water reward started delivery
long reward_sucrose_start = 0; // Time (micros-seconds) since sucrose reward started delivery
long wet_start_reward_start = 0; // Time (micros-seconds) since wet start reward


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
const int wet_start_pin = 23; // wet start pin

// Servo Pins I/O
const int request_swap_pin = 11; // request lick spout swap
const int request_remove_pin = 10; // request lick spout removal
const int command_swap_pin = 9; // servo command lick spout swap
const int command_remove_pin = 8;// servo command lick spout removal

// booleans or pseudo-booleans
int rewarding_sucrose = 0; // 0 is False, 1 is True
int rewarding_water = 0; // 0 is False, 1 is True
int wet_starting = 0; // 0 is False, 1 is True

// Parameters
const int signals_per_reward = 4; // threshold for reward delivery per reading period
const int reading_period = 5; // number of reads per period
int rolling_sucrose_licks = 0; // rolling tally per period
int rolling_water_licks = 0; // rolling tally per period
const long reward_timeout_dur = 250000; // timeout reward (micros)
long reward_water_timeout_start = 0; // timeout reward start time (water)
long reward_sucrose_timeout_start = 0; // timeout reward start time (sucrose)

// Setup Servos
#include <Servo.h>
Servo LickSwapper;
Servo LickRemover;
int swap_pos = 0; // current lick swapper position
int remove_pos = 0; // current lick remover position
long swapper_timeout_dur = 0; // timeout for servos in seconds
long remover_timeout_dur = 5000000; // timeout for servos in seconds
long swapper_timeout_start = 0; // timeout start
long remover_timeout_start = 0; // timeout start

// Circular Buffers (Commented Out, See Comment on Check Functions)
#include <CircularBuffer.h>
CircularBuffer<int, reading_period> water_buffer; // circular buffer for water readings
CircularBuffer<int, reading_period> sucrose_buffer; // circular buffer for sucrose readings

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
    pinMode(wet_start_pin, INPUT);
    // Servo I/O
    //pinMode(request_swap_pin, INPUT);
    //pinMode(request_remove_pin, INPUT);
    //pinMode(command_swap_pin, OUTPUT);
    //pinMode(command_remove_pin, OUTPUT);
    //LickSwapper.attach(command_swap_pin);
    //LickRemover.attach(command_remove_pin);


    //SerialUSB.begin(38400);
    //while (!SerialUSB);
    //{
    //  ;
    //}
    //SerialUSB.flush();
    //SerialUSB.println(Program);
    //SerialUSB.flush();
    //SerialUSB.println("Hello World");
}

void loop() {

    if(rewarding_sucrose == 1){
        checkTerminateSucrose(); // Don't bother calling these unless delivering
    }

    if(rewarding_water == 1){
        checkTerminateWater(); // Don't bother calling these unless delivering
    }
     if ((micros()- wet_start_timeout_dur) > wet_start_reward_start) {
           checkWetStart();
     }

     if ((micros() - reward_timeout_dur) > reward_sucrose_timeout_start) {
           checkSucrose();
     }

     if ((micros() - reward_timeout_dur) > reward_water_timeout_start) {
           checkWater();
     }

     if ((micros() - swapper_timeout_dur) > swapper_timeout_start) {
           checkSpoutSwap();
     }

     if ((micros() - remover_timeout_dur) > remover_timeout_start) {
          checkSpoutRemove();
     }
}

void checkSucrose() {
        // Here we deliver sucrose if and only if:
            // there is not currently a reward
            // rolling sucrose licks > signals_per_reward

        if (rewarding_sucrose == 0) {
          sucrose_buffer.push(digitalRead(sucrose_cap_touch_pin));
            rolling_sucrose_licks = 0;
            for(int i=0; i <sucrose_buffer.size(); i++) {
              rolling_sucrose_licks += sucrose_buffer[i];
            }
            if (rolling_sucrose_licks>signals_per_reward) {
                digitalWrite(licked_sucrose_pin, HIGH);
                if (digitalRead(permission_sucrose_pin)==HIGH) {
                  //SerialUSB.println("Sucrose Permitted & Licked");
                    deliverSucrose();
                }
            }
            else {
              digitalWrite(licked_sucrose_pin, LOW);
            }
        }
}

void checkWater() {
        // Here we deliver water if and only if:
            // there is not currently a reward
            // rolling water licks > signals_per_reward

            if (rewarding_water == 0) {
              water_buffer.push(digitalRead(water_cap_touch_pin));
              rolling_water_licks = 0;
              for(int i=0; i <water_buffer.size(); i++) {
                rolling_water_licks += water_buffer[i];
              }
            if (rolling_water_licks>signals_per_reward) {
                digitalWrite(licked_water_pin, HIGH);
                if (digitalRead(permission_water_pin)==HIGH) {
                  //SerialUSB.println("Water Permitted & Licked");
                   deliverWater();
                }
            }
           else {
            digitalWrite(licked_water_pin, LOW);
           }
        }

}

void deliverSucrose(){
    //SerialUSB.println("REWARDING SUCROSE - NC");
    reward_sucrose_start = micros();
    reward_sucrose_timeout_start = reward_sucrose_start;
    digitalWrite(trigger_sucrose_pin, HIGH);
    digitalWrite(rewarded_sucrose_pin, HIGH);
    rewarding_sucrose = 1;
}

void deliverWater(){
      //SerialUSB.println("REWARDING WATER -NC");
       reward_water_start = micros();
       reward_water_timeout_start = reward_water_start;
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
            //SerialUSB.println("Spout Swapper");
swapper_timeout_start = micros();
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
        //SerialUSB.println("Spout Remover");
        remover_timeout_start = micros();
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
    // SerialUSB.println("Checking Wet Start");

    if (wet_starting == 0 && digitalRead(wet_start_pin)==HIGH) {
      //SerialUSB.println("WET STARTING");
      wet_starting = 1;
      wet_start_reward_start = micros();

      if (rewarding_water == 0){
          if (digitalRead(wet_start_pin)==HIGH && digitalRead(permission_water_pin)==HIGH) {
              //SerialUSB.println("Wet Start Water");
              deliverWater();
          }
      }
      if (rewarding_sucrose == 0) {
          if (digitalRead(wet_start_pin)==HIGH && digitalRead(permission_sucrose_pin)==HIGH) {
              //SerialUSB.println("Wet Start Sucrose");
              deliverSucrose();
          }
      }
  }
}
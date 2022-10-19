/*
 Name:    Consolidated_Microcontroller_Script.ino
 Created: 10/19/2022 10:52:14 AM
 Author:  Darik A. O'Neil, Rafael Yuste Laboratory, Columbia University
*/

/*
This is a a consolidation of four scripts

1: Rewards
2: Motors
3: Quadratic Encoder
4: Load Cell

*/

String program_name = "Consolidated_Script";

// Use Serials
#define UseSerial

// Input Checking
#define CheckSignalInputsSucrose
#define CheckSignalInputsWater
#define CheckSignalInputsWetStart
#define CheckSignalInputsMotorSwapper
#define CheckSignalInputsMotorRemover

// Event Feedback
#define EventFeedback

// Performance Checks
#define CheckTimingFull
#define CheckTimingBufferSize

/*
 Code Begins Below Here
*/

// Quadratic Encoder Parameters
int pulses = 0; // Quadratic Encoder Pulses
int prev = LOW;
int curr;
int update_frequency = 1000; // Hz
long interval = (1/update_frequency)*1000;
long interval_start = 0;

// Quadratic Encoder Pins
const int encoder_pin_A = 48;
const int encoder_pin_B = 50;


// Behavioral Parameters
const long cycling_time = 8000; // Approximate Solenoid Turnover Time
const long reward_dur_water = 12125 + cycling_time; // Calibrated Duration to leave water solenoid open
const long reward_dur_sucrose = 10500 + cycling_time; // Calibrated Duration to leave sucrose solenoid open
const long wet_start_timeout_dur = 60000000; // Timeout for wet start
long reward_water_start = 0; // Time (micros-seconds) since water reward started delivery
long reward_sucrose_start = 0; // Time (micros-seconds) since sucrose reward started delivery
long wet_start_reward_start = 0; // Time (micros-seconds) since wet start reward

// Motor Parameters
const long swapper_timeout_dur = 5000000; // timeout for servos in seconds
const long remover_timeout_dur = 5000000; // timeout for servos in seconds
long swapper_timeout_start = 0; // timeout start
long remover_timeout_start = 0; // timeout start

// Motor Pins
const int request_swap_pin = 22;
const int request_remove_pin = 24;
const int command_swap_pin = 2;
const int command_remove_pin = 3;

// Motor Positions
int swap_pos = 0;
int remove_pos = 0;

// Motors
#include <Servo.h>
Servo LickSwapper;
Servo LickRemover;

// Load Cell
#include "HX711.h"
HX711 scale;

// Load Cell Parameters
long reading;

// Load Cell Pins
const int DOUT = 49;
const int CLK = 51;
const int SDA_FORCE = SDA1;
const int SCL_FORCE = SCL1;


#ifdef  CheckTimingFull
long time1 = 0;
long time2 = 0;
#endif

#ifdef Flush
int flush = 0; // Proceeds 0 -> 1 -> 2
#endif

// Digital Out Pins
const int licked_water_pin = 29; // Signal to DAQ that water spout was licked
const int licked_sucrose_pin = 27; // Signal to DAQ that sucrose spout was licked
const int rewarded_water_pin = 25; // Signal to DAQ that water reward was delivered
const int rewarded_sucrose_pin = 23; // Signal to DAQ that sucrose reward was delivered
const int enable_water_solenoid = 37; // remain high always
const int enable_sucrose_solenoid = 39; // remain high always
const int trigger_water_pin = 41; // Trigger delivery of water reward
const int trigger_sucrose_pin = 43; // Trigger delivery of sucrose reward


// Digital In Pins
const int permission_water_pin = 31; // Permits water reward triggering upon licking
const int permission_sucrose_pin = 33; // Permits sucrose reward triggering upon licking
const int water_cap_touch_pin = 45; // water cap touch input
const int sucrose_cap_touch_pin = 47; // sucrose cap touch input
const int wet_start_pin = 35; // wet start pin

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

    // Motors I/O
    pinMode(request_swap_pin, INPUT);
    pinMode(request_remove_pin, INPUT);
    pinMode(command_swap_pin, OUTPUT);
    pinMode(command_remove_pin, OUTPUT);

    // Attach Motors
    LickSwapper.attach(command_swap_pin);
    LickRemover.attach(command_remove_pin);

    // Attach Load Cell
    scale.begin(DOUT, CLK);

    #ifdef UseSerial
    SerialUSB.begin(9600);
    while (!SerialUSB);
    {
      ;
    }
    SerialUSB.flush();
    SerialUSB.println(program_name);
    SerialUSB.flush();
    #endif
}

void loop() {

    #ifdef CheckTimingFull
    time1 = micros();
    #endif

    #ifdef CheckSignalInputsSucrose
      SerialUSB.print("Sucrose Licked: ");
      SerialUSB.println(digitalRead(sucrose_cap_touch_pin));
      SerialUSB.flush();
      SerialUSB.print("Sucrose Permitted: ");
      SerialUSB.println(digitalRead(permission_sucrose_pin));
      SerialUSB.flush();
    #endif

    #ifdef CheckSignalInputsWater
      SerialUSB.print("Water Licked: ");
      SerialUSB.println(digitalRead(water_cap_touch_pin));
      SerialUSB.flush();
      SerialUSB.print("Water Permitted: ");
      SerialUSB.println(digitalRead(permission_water_pin));
      SerialUSB.flush();
    #endif

    #ifdef CheckSignalInputsWetStart
      SerialUSB.print("Wet Start: ");
      SerialUSB.println(digitalRead(wet_start_pin));
      SerialUSB.flush();
    #endif

    #ifdef CheckSignalInputsMotorSwapper
        SerialUSB.print("Swapper: ");
        SerialUSB.println(digitalRead(request_swap_pin));
        SerialUSB.flush();
    #endif

    #ifdef CheckSignalInputsMotorRemover
        SerialUSB.print("Remover: ");
        SerialUSB.println(digitalRead(request_remove_pin));
        SerialUSB.flush();
    #endif

    #ifdef Flush
    if (flush==0) {
      digitalWrite(trigger_sucrose_pin, HIGH);
      digitalWrite(rewarded_sucrose_pin, HIGH);
      delay(5000);
      digitalWrite(trigger_sucrose_pin, LOW);
      digitalWrite(rewarded_sucrose_pin, LOW);
      flush = 1;
      #ifdef EventFeedback
        SerialUSB.println("Flushed Sucrose");
        SerialUSB.flush();
      #endif
    }
    if (flush==1) {
      digitalWrite(trigger_water_pin, HIGH);
      digitalWrite(rewarded_water_pin, HIGH);
      delay(5000);
      digitalWrite(trigger_water_pin, LOW);
      digitalWrite(rewarded_water_pin, LOW);
      flush = 2;
      #ifdef EventFeedback
        SerialUSB.println("Flushed Water");
        SerialUSB.flush();
      #endif
    }
    #endif

    if(rewarding_sucrose == 1){
        checkTerminateSucrose(); // Don't bother calling these unless delivering
    }

    if(rewarding_water == 1){
        checkTerminateWater(); // Don't bother calling these unless delivering
    }
     if ((micros()- wet_start_timeout_dur) > wet_start_reward_start) { // Don't bother calling these unless past timeout
           checkWetStart();
     }

     if ((micros() - reward_timeout_dur) > reward_sucrose_timeout_start) { // Don't bother calling these unless past timeout
           checkSucrose();
     }

     if ((micros() - reward_timeout_dur) > reward_water_timeout_start) { // Don't bother calling these unless past timeout
           checkWater();
     }

    #ifdef CheckTimingFull
    time2 = micros()-time1;
    SerialUSB.print("Loop Time: ");
    SerialUSB.print(time2);
    SerialUSB.println(" microseconds");
    SerialUSB.flush();
    #endif

    #ifdef CheckTimingBufferSize
    SerialUSB.print("Buffer Size: ");
    SerialUSB.print(5*time2);
    SerialUSB.flush();
    #endif
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
            if ((rolling_sucrose_licks>signals_per_reward) && (digitalRead(permission_sucrose_pin)==HIGH)) {
                digitalWrite(licked_sucrose_pin, HIGH);
                deliverSucrose();
                #ifdef EventFeedback
                  SerialUSB.println("Licked Sucrose & Reward Permitted");
                  SerialUSB.flush();
                #endif
                }
            else if ((rolling_sucrose_licks>signals_per_reward) && (digitalRead(permission_sucrose_pin)==LOW)) {
              digitalWrite(licked_sucrose_pin, HIGH);
              #ifdef EventFeedback
                SerialUSB.println("Licked Sucrose & Not Permitted");
                SerialUSB.flush();
              #endif
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
            if ((rolling_water_licks>signals_per_reward) && (digitalRead(permission_water_pin)==HIGH)) {
                digitalWrite(licked_water_pin, HIGH);
                deliverWater();
                #ifdef EventFeedback
                  SerialUSB.println("Licked Water & Permitted Reward");
                  SerialUSB.flush();
                #endif
            }
            else if ((rolling_water_licks>signals_per_reward) && (digitalRead(permission_water_pin)==LOW)) {
              digitalWrite(licked_water_pin, HIGH);
                #ifdef EventFeedback
                  SerialUSB.println("Licked Water & Not Permitted");
                  SerialUSB.flush();
                #endif
            }
           else {
            digitalWrite(licked_water_pin, LOW);
           }
        }
}

void deliverSucrose(){
    reward_sucrose_start = micros();
    reward_sucrose_timeout_start = reward_sucrose_start;
    digitalWrite(trigger_sucrose_pin, HIGH);
    digitalWrite(rewarded_sucrose_pin, HIGH);
    rewarding_sucrose = 1;
    #ifdef EventFeedback
      SerialUSB.println("Delivered Sucrose");
      SerialUSB.flush();
    #endif
}

void deliverWater(){
       reward_water_start = micros();
       reward_water_timeout_start = reward_water_start;
       digitalWrite(trigger_water_pin, HIGH);
       digitalWrite(rewarded_water_pin, HIGH);
       rewarding_water = 1;
       #ifdef EventFeedback
          SerialUSB.println("Delivered Water");
          SerialUSB.flush();
       #endif
}

void checkTerminateSucrose(){
    if((micros()-reward_sucrose_start) > reward_dur_sucrose){
        digitalWrite(trigger_sucrose_pin, LOW);
        digitalWrite(rewarded_sucrose_pin, LOW);
        rewarding_sucrose = 0;
        #ifdef EventFeedback
          SerialUSB.println("Terminate Sucrose");
          SerialUSB.flush();
        #endif
    }
}

void checkTerminateWater(){
    if((micros()-reward_water_start) > reward_dur_water){
        digitalWrite(trigger_water_pin, LOW);
        digitalWrite(rewarded_water_pin, LOW);
        rewarding_water = 0;
        #ifdef EventFeedback
          SerialUSB.println("Terminate Sucrose");
          SerialUSB.flush();
        #endif
    }
}

void checkWetStart() {
    if (wet_starting == 0 && digitalRead(wet_start_pin)==HIGH) {
      #ifdef EventFeedback
        SerialUSB.println("Wet Starting...");
        SerialUSB.flush();
      #endif
      wet_starting = 1;
      wet_start_reward_start = micros();

      if ((rewarding_water == 0) && (digitalRead(wet_start_pin)==HIGH) && (digitalRead(permission_water_pin)==HIGH)) {
              deliverWater();
              #ifdef EventFeedback
                  SerialUSB.println("Water Primed");
                  SerialUSB.flush();
              #endif
      }
      if ((rewarding_sucrose == 0) && (digitalRead(wet_start_pin)==HIGH) && (digitalRead(permission_sucrose_pin)==HIGH)) {
              deliverSucrose();
               #ifdef EventFeedback
                  SerialUSB.println("Sucrose Primed");
                  SerialUSB.flush();
               #endif
      }
  }
}

void checkLickSwap() {
    if ((digitalRead(request_swap_pin)==HIGH) && (micros()>(swapper_timeout_start+swapper_timeout_dur))) {
        if (swap_pos==0) {
            swap_pos = 180;
            swapper_timeout_start = micros();
            LickSwapper.write(swap_pos);

            #ifdef EventFeedback
                SerialUSB.println("Swapper Motor Trigger.")
                SerialUSB.flush();
            #endif

        }
        else {
            swap_pos = 0;
            swapper_timeout_start = micros();
            LickSwapper.write(swap_pos);

            #ifdef EventFeedback
                SerialUSB.println("Swapper Motor Trigger.")
                SerialUSB.flush();
            #endif
        }
    }
}

void checkLickRemove() {
    if ((digitalRead(request_remove_pin)==HIGH) && (micros()>(remover_timeout_start+remover_timeout_dur))) {
        if (remove_pos==0) {
            remove_pos = 180;
            remover_timeout_start = micros();
            LickRemover.write(remove_pos);

            #ifdef EventFeedback
                SerialUSB.println("Remover Motor Triggered.")
                SerialUSB.flush();
            #endif
        }
        else {
            remove_pos = 0;
            remover_timeout_start = micros();
            LickRemover.write(remove_pos);

            #ifdef EventFeedback
                SerialUSB.println("Remover Motor Triggered.")
                SerialUSB.flush();
            #endif
        }
    }
}

void checkQuadraticEncoder() {
    curr = digitalRead(encoder_pin_A);
    // if A then B Clockwise
    // if B then A Counter-Clockwise
    if ((prev == LOW) && (curr == HIGH)) {
        if (digitalRead(encoder_pin_B) == LOW) {
            pulses--;
        }
        else {
            pulses++;
        }
    }
    prev = curr;
}

void reportPosition() {
    if (micros() > (interval_start + interval)) {
        // Do Something
       //
       // Now reset
       pulses = 0;
       interval_start = micros();
    }

}

void checkLoadCell() {
    reading = scale.read();
    // Do Something
}
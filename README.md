# A Collection of Burrow-Based Licking Behaviors

Dependencies not included in environment file   

https://www.arduino.cc/reference/en/libraries/servo/

## To Test Integrity

Enter "pytest -q testing.py --show-progress" in terminal

## To Install
conda env create -f environment.yml

## Details
1. All Configurations located in LickBehaviorConfigurations.py file   

2. Note that the attributes do not have setters and cannot be modified once initialized. This is for your own safety. I have not gotten to implementing a single-use setter function; change configuration directly in respective classes

3. Mouse IDs must always be unique; the classes do not have the privelege to overwrite files. This is for your own safety.

4. Hardware, wiring, and IO configuration described within HardwareConfiguration.py

5. C++ scripts must be uploaded to appropriate microcontrollers. Pytest does not handle these & the included PyCharm project meta does not add an external compiler or uploader. This is can be added by editing the project configuration & entering arduino_debug.exe as an external tool. [See here for details.](https://samclane.dev/Pycharm-Arduino/)

## Behaviors

### Burrow Preference
Anxiolytic assessment comparing the balance of burrowing and exploratory behavior

### Sucrose Preference
Anhedonia assessment comparing the consumption of sugar-water & water

### Simple Discrimination Test
Cognitive assay assessing reward learning

### Reversal Test
Cognitive assay assessing behavioral flexibility


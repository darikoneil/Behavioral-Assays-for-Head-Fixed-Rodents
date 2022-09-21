# Behavioral Assays for Head-Fixed Rodents
---
##    

## **_Under Construction..._**

## Running-Disk Behaviors

**_Locomotion_**     
Motor assay assessing hyperactivity & motor function

**_Acoustic Startle Threshold_**      
Sensory assay assessing sensorimotor gating

**_Pre-Pulse Inhibition_**      
Sensory assay assessing sensorimotor gating

## Mobile-Burrow Behaviors      

**_Burrow Preference_**      
Anxiolytic assessment comparing the balance of burrowing and exploratory behavior

**_Sucrose Preference_**      
Anhedonia assessment comparing the consumption of sugar-water & water     

**_Simple Discrimination Test_**      
Cognitive assay assessing reward learning     

**_Reversal Test_**     
Cognitive assay assessing behavioral flexibility      

## Installation     
0. Clone this repository  


1. Open an [anaconda](https://www.anaconda.com/) terminal  

2. Enter the repo's directory    

```
cd [path to repo]
```

3. Create an environment

```
conda env create -f environment.yml      
```

4. Install [Arduino's IDE](https://www.arduino.cc/en/software)      

5. Install [Servo Library](https://www.arduino.cc/reference/en/libraries/servo/)

6. Confirm the hardware, wiring, and IO setup matches that described in HardwareConfiguration.py      

7. Upload C++ scripts to appropriate microcontrollers.    
> The included [PyCharm](https://www.jetbrains.com/pycharm/) project meta does not add an external compiler or uploader. This functionality is can be added by editing the project configuration & entering arduino_debug.exe as an external tool. [See here for details.](https://samclane.dev/Pycharm-Arduino/). It is simply easier to upload the scripts to the respective devices in Arduino's IDE. [See here for details](https://support.arduino.cc/hc/en-us/articles/4733418441116-Upload-a-sketch-in-Arduino-IDE). Also note, the included [Pytest](https://docs.pytest.org/en/7.1.x/) checks do not assess the integrity of the microcontrollers.     

7. Enter the created anaconda environment     

```
conda activate LickingBehavior
```

8. Assess the integrity of the installaton      

```
pytest -q testing.py --show-progress
```

9. If all tests pass, the installation is complete      

## Initiating Behavioral Tasks      

All behavioral tasks are implemented as finite state machines which interface with one or more national instruments data acquisition boards. All data acquisition is syncronized to the analog input of a single DAQ. For ease of experimentation all behaviors can be controlled using graphical user interfaces.    

1. Enter relevant behavioral parameters for the desired behavior in the LickBehaviorConfigurations.py file. 
> Note that the attributes do not have setters and cannot be modified once initialized. This is for your own safety. I have not gotten to implementing a single-use setter function; change configuration directly in respective classes. Furthermore, mouse IDs must always be unique; the classes do not have the privelege to overwrite files. This is again for your own safety.

2. Execute the respective behavioral script in the terminal of your anaconda environment.

```
python RespectiveBehavioralScript.pyw
```

3. Confirm that DAQ is functional via a green DAQ indicator     

4. Initiate cameras if desired using *Cameras* button & confirm functional via green cameras indicator         
> In some behaviors there are two camera indicator for a *body cam* and *face cam*

5. Initiate behavior using *Behavior* button & confirm functional via green behavior indicator    

6. If conducting concurrent imaging, ensure synchronization via green synchronous imaging indicator   

7. Start behavior using *Start* button.

8. After "End" is displayed in the behavioral stage, it is safe to press the *Close* button.    

## Dictionary of Behavioral Scripts     

| **_Behavioral Task_** | **_Associated Script_** |
| --------------- | ----------------- |
| Burrow Preference | RunBurrowPreference.pyw |
| Sucrose Preference | RunSucrosePreference.pyw |
| Licking Training | RunLickTraining.py |
| Simple Discrimination | RunSimpleDiscrimination.pyw |
| Reversal Test | RunReversalTest.pyw |


# Romi Project
**Overview:**  
This project uses a differential-drive robot (Romi) that autonomously follows a high-contrast track using a centroid-based line-sensor algorithm and PID motor controllers. Additionally, to track distance, two quadrature encoders, one on each gear motor, are used in the wheel system. These encoders measure the rotational distance of each wheel, allowing Romi's travel distance to be set for sections of the track where line following is not applicable. 

# Demonstration
Demo Video:  
[![Watchthedemo](https://img.youtube.com/vi/rJuXOP3_y1Q/0.jpg)](https://youtu.be/rJuXOP3_y1Q)  

Course:  
![ME405Track](https://github.com/user-attachments/assets/66447394-3b0a-4a0a-a0d2-30eefef25190)

# Hardware
![romi](https://github.com/user-attachments/assets/43540a37-eb58-451f-94a6-f14b92d9e887)

The image above is of Romi, a differential-drive robot kit produced by Pololu.

**Chassis:**  
Romi's chassis is injection-molded plastic, measuring 165 mm in diameter and with an integrated battery holder. Six AA batteries power it.

**Motor Driver and Power Distribution Board:**  
The Pololu manufacturers provide a custom motor driver and power distribution board built specifically for the Romi chassis. It features two DRV8838 motor drivers and a switching step-down regulator that can supply continuous 2.5A at 5V or 3.3V. A small push button is pre-installed to easily control the power output to the NUCLEO. For motor control, the board features two sets of PWM, DIR, and SLP pin outputs for each motor. For the encoders, the board features VCC pin inputs and two sets of easily accessible A and B channel pin outputs for each encoder. 

**Wheels:**  
Two Pololu 70x8 mm wheels are attached to the motor shafts. These wheels have silicone tires for gripping the surface.


**Motors:**  
Romi uses two brushed DC plastic gearmotors, operating at a nominal voltage of 4.5 V. Its gearbox ratio is 120:1.


**Encoders:**  
For rotational distance and velocity tracking, two quadrature encoders were attached to the mini plastic gearmotors. The encoders are dual-channel Hall effect sensors. They offer a resolution of 12 counts per revolution, but paired with 120:1 gearmotors, the effective resolution is 1440 counts per wheel revolution.



**Reflectance Sensor Array:**  
For this project, the QTRX-MD-05A 5-channel reflectance sensor array was implemented. The five sensors are each spaced 8 mm apart on the board. This allows the generation of a centroid to determine the line's position relative to the sensor array. 


**Ultrasonic Distance Sensor:**  
The HC-SR04 ultrasonic distance sensor allows Romi to detect an object from 2 to 400 cm away. The sensor sends a 10 µs, 40 kHz pulse that reflects off an object and is received by the sensor. The amount of time between pulse transmission and reception allows the distance to be calculated.

**Nucleo-L476RG:**  
The STM32 Nucleo-L476RG microcontroller is the brain of Romi. It interfaces all of the sensors and actuators. It is programmed in MicroPython.

**The Shoe of Brian:**  
The Shoe of Brian is an ME 405-specific piece of ancillary hardware that allows the user to directly flash MicroPython code onto the MCU instead of going through the ST-Link onboard the Nucleo-L476RG.

# NUCLEO-L476RG Pin Assignments

| Component        | Function           | Pin | Notes                       |
|------------------|--------------------|-----|-----------------------------|
| **Power**                                                                 |
| NUCLEO-L476RG    | Power in           | VIN | 7V - 12V (From Power Board) |
| NUCLEO-L476RG    | Ground             | GND | 0V Reference                |
| Line Sensor      | Power in           | 3V3 | 3.3V                        |
| Line Sensor      | Ground             | GND | 0V Reference                |
| Range Sensor     | Power in           | 3V3 | 3.3V                        |
| Range Sensor     | Ground             | GND | 0V Reference                |
| **Motors**       |                    |     |                             |
| Left Motor PWM   | PWM                | B5  | Timer 3 Channel 2           |
| Right Motor PWM  | PWM                | B4  | Timer 3 Channel 1           |
| Left Motor DIR   | Direction          | B3  | Motor driver input          |
| Left Motor SLP   | Enable             | A10 | Motor driver input          |
| Right Motor Dir  | Direction          | B6  | Motor driver input          |
| Right Motor SLP  | Enable             | A7  | Motor driver input          |
| **Encoders**     |                    |     |                             |
| Left Encoder A   | Quadrature Input A | A8  | Timer 1 Channel 1           |
| Left Encoder B   | Quadrature Input B | A9  | Timer 1 Channel 2           |
| Right Encoder A  | Quadrature Input A | A0  | Timer 2 Channel 1           |
| Right Encoder B  | Quadrature Input B | A1  | Timer 2 CHannel 2           |
| **Line Sensors** |                    |     |                             |
| Line Sensor Ch 1 | Analog Input       | B0  | ADC                         |
| Line Sensor Ch 2 | Analog Input       | C0  | ADC                         |
| Line Sensor Ch 3 | Analog Input       | C1  | ADC                         |
| Line Sensor Ch 4 | Analog Input       | C2  | ADC                         |
| Line Sensor Ch 5 | Analog Input       | C3  | ADC                         |
| **Range Sensor** |                    |     |                             |
| Trigger          | Digital Output     | A6  | Sends pulse (Push-Pull)     |
| Echo             | Digital Input      | C7  | Receives signal (Pull Down) |
| **User Input**   |                    |     |                             |
| User Push Button | External Interrupt | C13 | Falling edge interrupt      |



# Software

**Software Overview:**  
Romi uses cooperative tasking to run through the various tasks required to complete the obstacle course. Each task is implemented as a finite state machine. In total, Romi runs five tasks: leftMotorTask, rightMotorTask, userTask, lineTask, and plannerTask. In addition, some classes complement these tasks by serving as sensor drivers. Another class is our motor controller.

**Tasks:**  

Task Diagram:
<img width="786" height="889" alt="Romi Task Diagram" src="https://github.com/user-attachments/assets/76a0caf2-913d-46c8-9581-2df607958d52" />


**leftMotorTask & rightMotorTask:**  
Each motor task is instantiated with its respective motor object, encoder object, controller object, motorGo share, and motor effort share. Each motor task runs periodically at 25 ms with priority 1. The responsibilities of each motor task include: Updating and retrieving velocity data from the encoders, applying a closed-loop PI controller to get motor effort, and commanding motor effort. Each motor task remains in an idle state until its corresponding go flag is set by the UI task. Although both tasks use the same class definition, they operate independently because each instance uses its own internal variables, motor driver object, encoder object, and shares. 

<img width="933" height="880" alt="Left Motor Task State Diagram" src="https://github.com/user-attachments/assets/1efaac74-e904-4ab8-9584-d24ddb7cac96" />

<img width="1003" height="880" alt="Right Motor Task State Diagram" src="https://github.com/user-attachments/assets/dad63bc0-b3b5-4a4a-9083-ad8e2cd80ef0" />

**States**

S0_WAIT:
This state waits for the goFlag to be set to True by the planner task. Once True, it transitions to the run state.

S1_RUN:
This measures the current encoder value, then calculates its respective motor velocity. It also receives the velocity setpoint from the planner task or the line follower task, depending on the state of the planner task. The setpoint and measured velocity are input to the motor controller (controller.py), where a motor effort is calculated. Once the goFlag is set False elsewhere, the motor is disabled and transitions back to the waiting state.

**userTask:**  
The User Interface (UI) task is strictly used for calibrating the reflectance sensors for line following. It is instantiated with simply whiteFlag and blackFlag. Both are shares filled with a single boolean. The UI task runs at priority 0 and handles serial communication through PuTTY. The UI task is separated from the motor tasks to prevent serial communication from interfering with critical control execution.

<img width="1270" height="828" alt="User Interface State Diagram" src="https://github.com/user-attachments/assets/9103f137-d855-4a0b-adcb-4f2f9544178d" />

**States**  

S0_INIT:  
This is the initialization state for the UI task. It prints the UI menu for calibration.

S1_CMD:  
This state waits for the user to input a character. Once it detects a listed character, either “c” or “h”, it moves to the corresponding state.\

S2_WHT_C:  
This state prompts the user to press “w” on the keyboard to trigger the white portion of the reflectance sensor calibration. Once “w” is read, it sets the whiteFlag True and transitions to the next state.

S3_BLK_C:  
The UI prompts the user to press “b” on the keyboard to trigger the black portion of the reflectance sensor calibration. Once “b” is read, it sets the blackFlag True and transitions back to S0_init.

**Task_follower:**  
This task’s purpose is to calibrate the reflectance sensor array and perform line following. The line follower task is instantiated with a line array object, line channels array, whiteFlag share, blackFlag share, setpoint share, vDiff share, leftEffort share, rightEffort share, and followEnable share. The line array object is an instance of the lineArray class, while the line channels array is an array of the five line channels for use in the lineArray class. whiteFlag and blackFlag are as discussed in the userTask section. Setpoint is a share that contains the default forward speed in mm/s of each motor while line following. vDiff is a share that contains the differential speed added to or subtracted from the setpoint. leftEffort and rightEffort are shares that contain the speed in mm/s at which motorTask uses to control motor speed. followEnable is a boolean share that enables and disables line following. lineTask has a priority of 1 and a period of 25 ms.

<img width="897" height="885" alt="Line Follower Task State Diagram" src="https://github.com/user-attachments/assets/fd2a11df-c389-466e-a16d-7a5f880d5882" />

**States**

S0_INIT:  
The initialization task waits for the UI to trigger calibration of the reflectance sensors. It waits for whiteFlag and blackFlag to both be set to True before transitioning to the run state.

S1_RUN:  
The run state is where all of the line following occurs. The centroid is generated from the lineArray object. If the centroid is None, the previous centroid from the last line detection is kept. The normalized error is calculated by subtracting the centroid from the centroid setpoint (0). This error is multiplied by vDiff, the differential turning speed. This speed is added to the right wheel’s total speed and subtracted from the left wheel’s total speed. These two speeds are put in leftEffort and rightEffort for sharing with the right and left motor tasks.


**plannerTask:**  
The plannerTask plans Romi’s movements, transitioning through a finite state machine. This task is instantiated with the startFlag share, followEnable share, leftMotorGo and rightMotorGo shares, setpoint share, vDiff share, leftEncoder and rightEncoder objects, rightEffort and leftEffort shares, dSense object, and lineArray object. The startFlag share is filled with a single Boolean object that starts the finite state machine. This is actuated using the onboard button on the NUCLEO-L476RG. The rightMotorGo, leftMotorGo, leftEncoder, and rightEncoder shares are discussed in the motorTask section. The followEnable, setpoint, vDiff, rightEffort, and leftEffort shares are discussed previously in the lineTask section. The leftMotorGo and rightMotorGo are discussed in the motorTask section. The lineArray object is also discussed in the lineTask section. The dSense object is an instance of the distance class used to measure Romi’s distance from an object using the ultrasonic range sensor. 

<img width="1041" height="899" alt="Planner Task State Diagram" src="https://github.com/user-attachments/assets/b81623ee-500f-4b00-8406-baa92476daaf" />

**States**  

S0_WAIT:  
This state waits for the onboard button to be pressed to begin the obstacle course and zeros the encoder values. 

S1_DELAY:  
This state is a 2-second delay so that Romi does not move immediately after the button is pressed.

S2_LineFollow_1:  
This state is for the straight line section. It triggers the encoders to update and calculates the distance travelled by each wheel. It also sets the setpoint vDiff shares. Once a certain encoder value is reached, the encoders and wheel distances are zeroed.

S3_Turn_1:  
This state is for after checkpoint 1 on the track. It updates encoder values and decreases motor speeds for the turn into the “garage.” It also checks to see if certain wheel distances have been met before transitioning to S4.

S4_GARAGE:  
This small state simply drives Romi forward 125 mm so that it can be centered in the “garage” portion of the track.

S5_Right90:  
This state performs a right-hand 90-degree turn. It transitions to the next state, S6_Wall, if it is the first time in this state. If it is the second time through this state, it transitions to S9_Snake.

S6_Wall:  
This state has Romi drive straight forward at 300 mm/s until the ultrasonic range sensor detects the wall to be 10 or less cm in front of it, then transitioning to the next state.

S7_Left90:  
This state performs a left-hand 90-degree turn out of the “garage” section of the track. This is done by setting the right effort to +200 mm/s and the left effort to -200 mm/s. To end the turn, a distance of 107 or greater is detected on the right encoder.

S8_preSnake:  
This state enables line following again. Then Romi drives forward 100 mm and then checks the line sensor for a None reading. Once None is detected, the finite state machine transitions to S5_Right90 again.

S9_Snake:  
This state continues line following through the snaking line section all the way to checkpoint 4, approximately 1570 mm from the start of this state. Once the encoders measure that distance, a transition to the next state occurs.

S10_Flip:   
Similar to the right 90-degree turn, this state performs a right-hand 180-degree turn to realign Romi with the line. This is done by setting the right and left motors at opposite efforts until the right encoder measures 214 mm.

S11_arc:  
This state has Romi perform a hardcoded right arcing turn so that line following can resume. Otherwise, there is a chance Romi tracks the line on the left and begins doing the course backwards. Once the encoder measures 175 mm, the state transitions.

S12_finalTurn:  
This state is the last portion of the line following. Line following is reactivated, and Romi follows for 150 mm, where the final transition occurs. 

S13_Finish:  
Romi performs one more arcing turn to the right by biasing one motor faster than the other. Romi stops after 80 mm over the spot where the course began. The state transitions back to S0_wait.

# Sensor Drivers and Additional Software:  

controller.py:  
This class allows for a controller object to be created within the motor task. This is a PI controller with feed-forward gain.

encoder.py:  
This class allows for encoder objects to be made and used to report velocity from the encoders.

main.py:  
This file is where all the objects are instantiated, and tasks are given their periods and priority. Everything works through main.py.

motor.py:  
This class allows for motor objects to be created for each motor (left and right). It has methods that allow for effort to be set and the motors to be enabled/disabled.

multichar_input.py:  
This file allows the user to input floats into the UI and save the floats in our shares.

task_share.py:  
This file was created by JR Ridgely so that we can share data between tasks without risk of data corruption by interrupts. 

line_sensor_driver.py:  
This file contains two classes: LineChannel and LineArray. LineChannel allows for the creation of individual ADC channels for each reflectance sensor. LineArray creates a line array object that creates the centroid for control purposes.

range_driver.py:  
The range_driver class allows the creation of the distance sensor object for distance measuring.

# Romi Project
Overview:

This project utilizes a differential-drive robot (Romi) that autonomously follows a high-contrast track using a centroid-based line sensor algorithm and PID motor controllers. Additonally to track distance two quadrature encoders, one on each gear motor, wheel system. Theses encoders measure the rotational distane of each wheel allowing Romi's travel distance to be set for sections of the track where line following is not applicable. 

# Demonstration
[![Watch the demo](https://img.youtube.com/vi/rJuXOP3_y1Q/0.jpg)](https://youtu.be/rJuXOP3_y1Q)

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


# Software

**Software Overview:**  
Romi uses cooperative tasking to run through the various tasks required to complete the obstacle course. Each task is implemented as a finite state machine. In total, Romi runs five tasks: leftMotorTask, rightMotorTask, userTask, lineTask, and plannerTask. In addition, some classes complement these tasks by serving as sensor drivers. Another class is our motor controller.

**Tasks:**  

leftMotorTask & rightMotorTask:  
Each motor task is instantiated with its respective motor object, encoder object, controller object, motorGo share, and motor effort share. Each motor task runs periodically at 25 ms with priority 1. The responsibilities of each motor task include: Updating and retrieving velocity data from the encoders, applying a closed-loop PI controller to get motor effort, and commanding motor effort. Each motor task remains in an idle state until its corresponding go flag is set by the UI task. Although both tasks use the same class definition, they operate independently because each instance uses its own internal variables, motor driver object, encoder object, and shares. 

INSERT FINITE STATE MACHINE DIAGRAMS

userTask:  
The User Interface (UI) task is strictly used for calibrating the reflectance sensors for line following. It is instantiated with simply whiteFlag and blackFlag. Both are shares filled with a single boolean. The UI task runs at priority 0 and handles serial communication through PuTTY. The UI task is separated from the motor tasks to prevent serial communication from interfering with critical control execution.

INSERT FINITE STATE MACHINE DIAGRAM

STATE DISCUSSION

lineTask:
The line follower task is instantiated with a line array object, line channels array, whiteFlag share, blackFlag share, setpoint share, vDiff share, leftEffortSet share, rightEffortSet share, and followEnable share.  
The line array object is an instance of the lineArray class, while the line channels array is an array of the five line channels for use in the lineArray class. whiteFlag and blackFlag are as discussed in the userTask section. Setpoint is a share that contains the default forward speed in mm/s of each motor while line following. vDiff is a share that contains the differential speed added to or subtracted from the setpoint. leftEffortSet and rightEffortSet are shares that contain the speed in mm/s at which motorTask uses to control motor speed. followEnable is a boolean share that enables and disables line following. lineTask has a priority of 1 and a period of 25 ms.

INSERT FINITE STATE MACHINE DIAGRAM

STATE DISCUSSION

plannerTask:  



# NUCLEO-L476RG Pin Assignments

| Component        | Function           | Pin | Notes                       |
|------------------|--------------------|-----|-----------------------------|
| **Power**        |                    |     |                             |
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
**Overview:**  
Romi utilizes cooperative tasking to run through the various tasks which 


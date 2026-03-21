''' This file demonstrates an example UI task using a custom class with a
   run method implemented as a generator
'''
from pyb import USB_VCP, UART
from task_share import Share
from multichar_input import float_gen
import micropython


S0_INIT = micropython.const(0) # State 0 - initialiation
S1_CMD  = micropython.const(1) # State 1 - wait for character input
S2_WHT_C = micropython.const(2) # State 2 - Calibrate White Baseline
S3_BLK_C = micropython.const(3) # State 3 - Calibrate Black Baseline
UI_prompt = ">: "


class task_user:
   '''
   A class that represents a UI task. The task is responsible for reading user
   input over a serial port, parsing the input for single-character commands,
   and then manipulating shared variables to communicate with other tasks based
   on the user commands.
   '''


   def __init__(self, whiteFlag, blackFlag):
       '''
       Initializes a UI task object

       Args:
           leftMotorGo (Share):  A share object representing a boolean flag to
                                 start data collection on the left motor
           rightMotorGo (Share): A share object representing a boolean flag to
                                 start data collection on the right motor
           dataValues (Queue):   A queue object used to store collected encoder
                                 position values
           timeValues (Queue):   A queue object used to store the time stamps
                                 associated with the collected encoder data
       '''

       self._state: int          = S0_INIT      # The present state

       self._whiteFlag: Share = whiteFlag
       self._blackFlag: Share = blackFlag

       self._ser: stream         = USB_VCP()    # A serial port object used to
                                                # read character entry and to
                                                # print output

       self._ser.write("User Task object instantiated\r\n")
       self._IMU_instr = False


   def run(self):
       '''
       Runs one iteration of the task
       '''

       while True:

           if self._state == S0_INIT: # Init state (can be removed if unneeded)
               self._ser.write("+--------------------------------------"
                               "----------------------------------------+\r\n")
               self._ser.write("| ME 405 Romi Tuning Interface Help Menu"
                               "                                       |\r\n")
               self._ser.write("+---+-----------------------------------"
                               "---------------------------------------+\r\n")
               self._ser.write("| h | Print help menu                   "
                               "                                       |\r\n")
               self._ser.write("| c | Calibrate Sensors                "
                               "                                        |\r\n")
               self._ser.write("+---+------------------------------------"
                               "--------------------------------------+\r\n")
               self._ser.write(UI_prompt)
               self._state = S1_CMD

           elif self._state == S1_CMD: # Wait for UI commands
               # Wait for at least one character in serial buffer
               if self._ser.any():
                   # Read the character and decode it into a string
                   inChar = self._ser.read(1).decode()
                   # If the character is an upper or lower case "l", start data
                   # collection on the left motor and if it is an "r", start
                   # data collection on the right motor
                   if inChar in {"h", "H"}:
                       self._ser.write(f"{inChar}\r\n")
                       self._state = S0_INIT

                   elif inChar in {"c", "C"}:
                       self._ser.write(f"{inChar}\r\n")
                       self._ser.write("Place Romi on white space\r\n"
                                       "Press w to calibrate:\r\n")
                       self._ser.write(UI_prompt)
                       self._state = S2_WHT_C


           elif self._state == S2_WHT_C:
               if self._ser.any():
                    inChar = self._ser.read(1).decode()
                    if inChar in {"w", "W"}:
                        self._ser.write(f"{inChar}\r\n")
                        self._whiteFlag.put(True)

                        self._ser.write("Place Romi on black space\r\n"
                                        "Press b to calibrate:\r\n")
                        self._ser.write(UI_prompt)
                        self._state = S3_BLK_C


           elif self._state == S3_BLK_C:
               if self._ser.any():
                    inChar = self._ser.read(1).decode()
                    if inChar in {"b", "B"}:
                        self._ser.write(f"{inChar}\r\n")
                        self._blackFlag.put(True)
                        self._ser.write("Line Sensor Calibration Complete\r\n\n"
                                        "Place Romi on Track and Press Blue Button\r\n\n")
                        self._state = S0_INIT

           yield self._state
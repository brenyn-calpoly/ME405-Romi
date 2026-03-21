''' This file demonstrates an example motor task using a custom class with a
   run method implemented as a generator
'''
from motor        import Motor
from encoder      import Encoder
from controller   import Controller
from task_share   import Share, Queue
from utime        import ticks_us, ticks_diff
import micropython
from line_sensor_driver import LineChannel, LineArray


S0_WAIT = micropython.const(0) # State 1 - wait for go command
S1_RUN  = micropython.const(1) # State 2 - run closed loop control


class task_motor:
   '''
   A class that represents a motor task. The task is responsible for reading
   data from an encoder, performing closed loop control, and actuating a motor.
   Multiple objects of this class can be created to work with multiple motors
   and encoders.
   '''


   def __init__(self, mot: Motor, enc: Encoder, con: Controller, goFlag: Share, effort: Share):
       '''
       Initializes a motor task object

       Args:
           mot (motor_driver): A motor driver object
           enc (encoder):      An encoder object
           goFlag (Share):     A share object representing a boolean flag to
                               start data collection
           dataValues (Queue): A queue object used to store collected encoder
                               position values
           timeValues (Queue): A queue object used to store the time stamps
                               associated with the collected encoder data
       '''

       self._state: int        = S0_WAIT    # The present state of the task

       self._mot: Motor = mot        # A motor object

       self._enc: Encoder = enc        # An encoder object

       self._con: Controller = con  # A controller object

       self._goFlag: Share     = goFlag     # A share object representing a
                                            # flag to start data collection

       self._setpoint: Share   = effort


   def run(self):
       '''
       Runs one iteration of the task
       '''

       while True:

           if self._state == S0_WAIT: # Wait for "go command" state
               if self._goFlag.get():
                   self._state = S1_RUN

           elif self._state == S1_RUN: # Closed-loop control state
               self._enc.update()
               vel = (self._enc.get_velocity() * 70 * 3.141592) / 1437.1 # mm/s conversion

               self._mot.enable()
               sp = self._setpoint.get()

               eff = self._con.update(sp, vel)
               self._mot.set_effort(eff)

               if not self._goFlag.get():
                   self._mot.disable()
                   self._state = S0_WAIT

           yield self._state
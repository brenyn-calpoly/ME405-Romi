from line_sensor_driver import LineChannel, LineArray
from task_share import Share, Queue
import micropython

S0_INIT = micropython.const(0)  # State 1
S1_RUN = micropython.const(1)  # State 2


class task_follower:
    '''
       A class that represents the line follower task. This task
       gets the centroid from the line sensor array and determines the mm/s on
       each wheel required to maintain the circle.
    '''

    def __init__(self, linArray: LineArray, channels: list[LineChannel], whiteFlag: Share,
                 blackFlag: Share, setpoint: Share, vDiff: Share, leftEffort: Share,
                 rightEffort: Share, followEnable: Share):
        '''
               Initializes a line follower task object
               Args:
                   linArray (LineArray):    A line array object
                   channels (list):      A list of channel objects
                   whiteFlag (Share):     A share object representing a boolean flag to
                                       calibrate white
                   blackFlag (Share):     A share object representing a boolean flag to
                                          calibrate black
                   vForward (Share):      A share object used to store set base forward velocity from UI
                   vDiff (Share):         A share object used to store set max diff velocity from UI
                   leftEffort (Share):    A share object used to store left motor effort for motor task
                   rightEffort (share):   A share object used to store right motor effort for motor task
               '''

        self._state: int = S0_INIT  # cal state

        self._array: LineArray = linArray  # line array object

        self._channels: list[LineChannel] = channels  # channel lists

        self._whiteFlag: Share = whiteFlag  # flags to calibrate sensors
        self._blackFlag: Share = blackFlag

        self._vDiff: Share = vDiff  # diff speed component

        self._leftEffort: Share = leftEffort  # setpoints for motor controllers
        self._rightEffort: Share = rightEffort

        self._setpoint: Share = setpoint
        self._e_prev = 0
        self._prev_centroid = 0

        self._followEnable: Share = followEnable

    def run(self):
        "Runs task"

        while True:
            if self._state == S0_INIT:  # Wait for "go command" state
                if not (self._whiteFlag.get() or self._blackFlag.get()):
                    self._state = S0_INIT

                elif self._whiteFlag.get():
                    self._array.calibrate_white()
                    self._whiteFlag.put(False)

                elif self._blackFlag.get():
                    self._array.calibrate_black()
                    self._blackFlag.put(False)
                    self._state = S1_RUN

            elif self._state == S1_RUN:
                if self._followEnable.get():
                    sp = 0
                    vDiff = self._vDiff.get()

                    centroid = self._array.find_centroid()

                    # checks to see if line is lost, if lost continue prev action
                    if centroid == None:
                        centroid = self._prev_centroid
                        print("NONE")

                    # normalized error
                    error = (sp - centroid) / 16

                    self._e_prev = error

                    x = error * vDiff

                    forward = self._setpoint.get()
                    #forward = forward - forward * abs(error)

                    left = forward - x
                    right = forward + x

                    self._leftEffort.put(left)  # set left and right efforts in motor task
                    self._rightEffort.put(right)

                    self._prev_centroid = centroid

            yield self._state

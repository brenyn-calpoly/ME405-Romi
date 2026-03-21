from time import ticks_ms, ticks_diff
import micropython
from encoder import Encoder
from task_share import Share
from line_sensor_driver import LineArray
from range_driver import distance
import math

S0_WAIT = micropython.const(0)
S1_DELAY = micropython.const(1)
S2_LineFollow_1 = micropython.const(2)
S3_Turn_1 = micropython.const(3)
S4_GARAGE = micropython.const(4)
S5_Right90 = micropython.const(5)
S6_Wall = micropython.const(6)
S7_Left90 = micropython.const(7)
S8_preSnake = micropython.const(8)
S9_Snake = micropython.const(9)
S10_Flip = micropython.const(10)
S11_arc = micropython.const(11)
S12_finalTurn = micropython.const(12)
S13_Finish = micropython.const(13)


class task_planner:

    def __init__(self, startFlag: Share, followEnable: Share, leftMotorGo: Share, rightMotorGo: Share, setpoint: Share,
                 vDiff: Share, leftEncoder: Encoder, rightEncoder: Encoder, rightEffort, leftEffort, dSense, LineArray):

        self._startFlag: Share = startFlag
        self._followEnable: Share = followEnable
        self._leftMotorGo: Share = leftMotorGo
        self._rightMotorGo: Share = rightMotorGo
        self._setpoint: Share = setpoint
        self._vDiff: Share = vDiff
        self._encL: Encoder = leftEncoder
        self._encR: Encoder = rightEncoder
        self._lineArray: LineArray = LineArray
        self._rightEffortSet: Share = rightEffort
        self._leftEffortSet: Share = leftEffort
        self._distance = dSense
        self.d = 0
        self.i = 0

        self._t0 = 0
        self._S_l = 0
        self._S_r = 0
        self._encR_pos = 0
        self._state = S0_WAIT

    def run(self):

        while True:

            if self._state == S0_WAIT:
                if self._startFlag.get():
                    self._t0 = ticks_ms()
                    self._encL.zero()
                    self._encR.zero()
                    self._state = S1_DELAY

            elif self._state == S1_DELAY:
                t_now = ticks_diff(ticks_ms(), self._t0)
                if t_now >= 2000:
                    self._state = S2_LineFollow_1

            elif self._state == S2_LineFollow_1:
                self._encL.update()
                self._encR.update()

                self._S_l = self._encL.get_position() * (math.pi * 70 / 1437.1)
                self._S_r = self._encR.get_position() * (math.pi * 70 / 1437.1)

                self._setpoint.put(350.0)
                self._vDiff.put(50.0)

                self._leftMotorGo.put(True)
                self._rightMotorGo.put(True)
                self._followEnable.put(True)

                if self._S_l >= 1290.0:
                    self._encL.zero()
                    self._encR.zero()
                    self._S_l = 0
                    self._S_r = 0
                    self._state = S3_Turn_1


            elif self._state == S3_Turn_1:
                self._encL.update()
                self._encR.update()

                self._S_l = self._encL.get_position() * (math.pi * 70 / 1437.1)
                self._S_r = self._encR.get_position() * (math.pi * 70 / 1437.1)

                self._setpoint.put(150.0)
                self._vDiff.put(125.0)

                if self._S_l >= 485:
                    self._leftMotorGo.put(False)
                if self._S_r >= 250:
                    self._leftEffortSet.put(75)
                    self._followEnable.put(False)
                    self._rightMotorGo.put(False)

                if not self._rightMotorGo.get() and not self._leftMotorGo.get():
                    self._encL.zero()
                    self._encR.zero()
                    self._S_l = 0
                    self._S_r = 0
                    self._state = S4_GARAGE


            elif self._state == S4_GARAGE:
                self._followEnable.put(False)
                self._encL.update()
                self._encR.update()

                self._S_l = self._encL.get_position() * (math.pi * 70 / 1437.1)
                self._S_r = self._encR.get_position() * (math.pi * 70 / 1437.1)

                self._rightEffortSet.put(170)
                self._leftEffortSet.put(170)

                self._rightMotorGo.put(True)
                self._leftMotorGo.put(True)

                if self._S_l >= 125:
                    self._encL.zero()
                    self._encR.zero()
                    self._S_l = 0
                    self._S_r = 0
                    self._rightMotorGo.put(False)
                    self._leftMotorGo.put(False)
                    self._state = S5_Right90

            elif self._state == S5_Right90:
                self._encL.update()
                self._encR.update()

                self._S_l = self._encL.get_position() * (math.pi * 70 / 1437.1)
                self._S_r = self._encR.get_position() * (math.pi * 70 / 1437.1)

                self._rightEffortSet.put(-200)
                self._leftEffortSet.put(200)

                self._rightMotorGo.put(True)
                self._leftMotorGo.put(True)

                if self._S_l >= 104:
                    self._encL.zero()
                    self._encR.zero()
                    self._S_l = 0
                    self._S_r = 0
                    self._rightMotorGo.put(False)
                    self._leftMotorGo.put(False)
                    if self.i == 0:
                        self.i = 1
                        self._state = S6_Wall
                    else:
                        self._state = S9_Snake

            elif self._state == S6_Wall:
                self._encL.update()
                self._encR.update()

                self._rightEffortSet.put(300)
                self._leftEffortSet.put(300)

                self._rightMotorGo.put(True)
                self._leftMotorGo.put(True)

                self.d = self._distance.find_distance()
                print(self.d)

                if self.d is not None and self.d <= 10:
                    self._encL.zero()
                    self._encR.zero()
                    self._S_l = 0
                    self._S_r = 0
                    self._rightMotorGo.put(False)
                    self._leftMotorGo.put(False)
                    self._state = S7_Left90
                else:
                    print("None")


            elif self._state == S7_Left90:
                self._encL.update()
                self._encR.update()

                self._S_l = self._encL.get_position() * (math.pi * 70 / 1437.1)
                self._S_r = self._encR.get_position() * (math.pi * 70 / 1437.1)

                self._rightEffortSet.put(200)
                self._leftEffortSet.put(-200)

                self._rightMotorGo.put(True)
                self._leftMotorGo.put(True)

                if self._S_r >= 107:
                    self._encL.zero()
                    self._encR.zero()
                    self._S_l = 0
                    self._S_r = 0
                    self._rightMotorGo.put(False)
                    self._leftMotorGo.put(False)
                    self._state = S8_preSnake

            elif self._state == S8_preSnake:
                self._followEnable.put(True)
                self._setpoint.put(200.0)
                self._vDiff.put(50.0)

                self._encL.update()
                self._encR.update()

                self._S_l = self._encL.get_position() * (math.pi * 70 / 1437.1)
                self._S_r = self._encR.get_position() * (math.pi * 70 / 1437.1)

                self._rightMotorGo.put(True)
                self._leftMotorGo.put(True)

                centroid = self._lineArray.find_centroid()

                if self._S_l >= 100:
                    if centroid is None:
                        self._encL.zero()
                        self._encR.zero()
                        self._S_l = 0
                        self._S_r = 0
                        self._rightMotorGo.put(False)
                        self._leftMotorGo.put(False)
                        self._followEnable.put(False)
                        self._state = S5_Right90

            elif self._state == S9_Snake:
                self._followEnable.put(True)
                self._setpoint.put(150.0)
                self._vDiff.put(125.0)

                self._encL.update()
                self._encR.update()

                self._S_l = self._encL.get_position() * (math.pi * 70 / 1437.1)
                self._S_r = self._encR.get_position() * (math.pi * 70 / 1437.1)

                self._rightMotorGo.put(True)
                self._leftMotorGo.put(True)

                if self._S_r >= 1570:
                    self._encL.zero()
                    self._encR.zero()
                    self._S_l = 0
                    self._S_r = 0
                    self._rightMotorGo.put(False)
                    self._leftMotorGo.put(False)
                    self._followEnable.put(False)
                    self._state = S10_Flip

            elif self._state == S10_Flip:
                self._encL.update()
                self._encR.update()

                self._S_l = self._encL.get_position() * (math.pi * 70 / 1437.1)
                self._S_r = self._encR.get_position() * (math.pi * 70 / 1437.1)

                self._rightEffortSet.put(200)
                self._leftEffortSet.put(-200)

                self._rightMotorGo.put(True)
                self._leftMotorGo.put(True)

                if self._S_r >= 214:
                    self._encL.zero()
                    self._encR.zero()
                    self._S_l = 0
                    self._S_r = 0
                    self._rightMotorGo.put(False)
                    self._leftMotorGo.put(False)
                    self._state = S11_arc

            elif self._state == S11_arc:
                self._encL.update()
                self._encR.update()

                self._S_l = self._encL.get_position() * (math.pi * 70 / 1437.1)
                self._S_r = self._encR.get_position() * (math.pi * 70 / 1437.1)

                self._rightEffortSet.put(125)
                self._leftEffortSet.put(180)

                self._rightMotorGo.put(True)
                self._leftMotorGo.put(True)

                if self._S_r >= 175:
                    self._encL.zero()
                    self._encR.zero()
                    self._S_l = 0
                    self._S_r = 0
                    self._rightMotorGo.put(False)
                    self._leftMotorGo.put(False)
                    self._state = S12_finalTurn

            elif self._state == S12_finalTurn:
                self._encL.update()
                self._encR.update()

                self._S_l = self._encL.get_position() * (math.pi * 70 / 1437.1)
                self._S_r = self._encR.get_position() * (math.pi * 70 / 1437.1)

                self._setpoint.put(150.0)
                self._vDiff.put(100.0)

                self._rightMotorGo.put(True)
                self._leftMotorGo.put(True)
                self._followEnable.put(True)

                centroid = self._lineArray.find_centroid()

                if self._S_r >= 150:
                    if centroid is None:
                        self._encL.zero()
                        self._encR.zero()
                        self._S_l = 0
                        self._S_r = 0
                        self._rightMotorGo.put(False)
                        self._leftMotorGo.put(False)
                        self._followEnable.put(False)
                        self._state = S13_Finish

            elif self._state == S13_Finish:
                self._encL.update()
                self._encR.update()

                self._S_l = self._encL.get_position() * (math.pi * 70 / 1437.1)
                self._S_r = self._encR.get_position() * (math.pi * 70 / 1437.1)

                self._rightEffortSet.put(75)
                self._leftEffortSet.put(150)

                self._rightMotorGo.put(True)
                self._leftMotorGo.put(True)

                if self._S_r >= 80:
                    self._encL.zero()
                    self._encR.zero()
                    self._S_l = 0
                    self._S_r = 0
                    self._rightMotorGo.put(False)
                    self._leftMotorGo.put(False)
                    self._startFlag.put(False)
                    self.i = 0
                    self._state = S0_WAIT

            yield self._state

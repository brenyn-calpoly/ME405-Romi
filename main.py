from motor import Motor
from encoder import Encoder
from controller import Controller
from task_motor import task_motor
from task_user import task_user
from task_share import Share, Queue, show_all
from cotask import Task, task_list
from gc import collect
from task_follower import task_follower
from line_sensor_driver import LineChannel, LineArray
from task_planner import task_planner
from range_driver import distance
from pyb import Pin, Timer, ADC, I2C, ExtInt

pyb.repl_uart(None)

# Build shares and queues
leftMotorGo = Share("B", name="Left Mot. Go Flag")
rightMotorGo = Share("B", name="Right Mot. Go Flag")
setpoint = Share("f", name="Setpoint")
leftEffortSet = Share("f", name="leftEffort")
rightEffortSet = Share("f", name="rightEffort")
whiteFlag = Share("B", name="white cal")
blackFlag = Share("B", name="black cal")
vDiff = Share("f", name="vDiff")
startFlag = Share("B", name="start flag")
followEnable = Share("B", name="enable line following")

# build driver objects
tim3 = Timer(3, freq=20000)
leftPWM = tim3.channel(2, Timer.PWM, pin=Pin.cpu.B5)  # PWM = EN
rightPWM = tim3.channel(1, Timer.PWM, pin=Pin.cpu.B4)  # PWM = EN

# Motor Objs
rightMotor = Motor(rightPWM, Pin.cpu.B6, Pin.cpu.A7)
leftMotor = Motor(leftPWM, Pin.cpu.B3, Pin.cpu.A10)

# Right Encoder
tim2 = Timer(2, period=0xFFFF, prescaler=0)
T2_ch1 = tim2.channel(1, pin=Pin.cpu.A0, mode=Timer.ENC_AB)
T2_ch2 = tim2.channel(2, pin=Pin.cpu.A1, mode=Timer.ENC_AB)

# Left Encoder
tim1 = Timer(1, period=0xFFFF, prescaler=0)
T1_ch1 = tim1.channel(1, pin=Pin.cpu.A8, mode=Timer.ENC_AB)
T1_ch2 = tim1.channel(2, pin=Pin.cpu.A9, mode=Timer.ENC_AB)

# Encoder Objs
rightEncoder = Encoder(tim2, T2_ch1, T2_ch2)
leftEncoder = Encoder(tim1, T1_ch1, T1_ch2)

# Motor Controller Object
controllerObjR = Controller(0.02, 1.7, 0.02, 0.025)
controllerObjL = Controller(0.02, 1.7, 0.02, 0.025)

# Line channel objects
ch1 = LineChannel(ADC(Pin(Pin.cpu.B0, mode=Pin.ANALOG)))
ch2 = LineChannel(ADC(Pin(Pin.cpu.C0, mode=Pin.ANALOG)))
ch3 = LineChannel(ADC(Pin(Pin.cpu.C1, mode=Pin.ANALOG)))
ch4 = LineChannel(ADC(Pin(Pin.cpu.C2, mode=Pin.ANALOG)))
ch5 = LineChannel(ADC(Pin(Pin.cpu.C3, mode=Pin.ANALOG)))

# Line channels
channels = [ch1, ch2, ch3, ch4, ch5]

# Line array object
lineArrayObj = LineArray(channels)

# Range finder Obj
trigger = Pin(Pin.cpu.A6, mode=Pin.OUT_PP)
echo = Pin(Pin.cpu.C7, mode=Pin.IN, pull=Pin.PULL_DOWN)
dSense = distance(trigger, echo)


def start_button_callback(buttonPin):
    startFlag.put(True)

button_int = ExtInt(Pin.cpu.C13, ExtInt.IRQ_FALLING, Pin.PULL_NONE, start_button_callback)

# Build task class objects
leftMotorTask = task_motor(leftMotor, leftEncoder, controllerObjL, leftMotorGo, leftEffortSet)

rightMotorTask = task_motor(rightMotor, rightEncoder, controllerObjR, rightMotorGo, rightEffortSet)

userTask = task_user(whiteFlag, blackFlag)

lineTask = task_follower(lineArrayObj, channels, whiteFlag, blackFlag, setpoint, vDiff, leftEffortSet, rightEffortSet, followEnable)

plannerTask = task_planner(startFlag, followEnable, leftMotorGo, rightMotorGo, setpoint, vDiff, leftEncoder, rightEncoder, rightEffortSet,
                           leftEffortSet, dSense, lineArrayObj)

# Add tasks to task list
task_list.append(Task(leftMotorTask.run, name="Left Mot. Task",
                      priority=1, period=25, profile=True))
task_list.append(Task(rightMotorTask.run, name="Right Mot. Task",
                      priority=1, period=25, profile=True))
task_list.append(Task(userTask.run, name="User Int. Task",
                      priority=0, period=0, profile=False))
task_list.append(Task(lineTask.run, name="Line Follower Task",
                      priority=1, period=25, profile=True))
task_list.append(Task(plannerTask.run, name="Planner Task",
                      priority=1, period=50, profile=True))

# Run the garbage collector preemptively
collect()

# Run the scheduler until the user quits the program with Ctrl-C
while True:
    try:
        task_list.pri_sched()

    except KeyboardInterrupt:
        print("Program Terminating")
        leftMotor.disable()
        rightMotor.disable()
        break

print("\n")
print(task_list)
print(show_all())

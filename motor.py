from pyb import Pin

class Motor:
    '''A motor driver interface encapsulated in a Python class. Works with
       motor drivers using separate PWM and direction inputs such as the DRV8838
       drivers present on the Romi chassis from Pololu.'''

    def __init__(self, PWM, DIR, nSLP = 1):
        '''Initializes a Motor object
           Configure Timer and select PWM channel in Lab3.py
           Ex. tim3 = Timer(3, freq= 20000)
           Ex. rightPWM = tim3.channel(2, Timer.PWM, pin=Pin.cpu.B5)
           Ex. PWM = rightPWM ## in the motor object'''

        # Sleep Pin
        self.nSLP_pin = Pin(nSLP, mode=Pin.OUT_PP, value=0)

        # Direction Pin
        self.DIR_pin = Pin(DIR, mode=Pin.OUT_PP, value=0)

        #PWM Pin
        self.PWM_pin = PWM

        self.PWM_pin.pulse_width_percent(0)
        self.nSLP_pin.low()

    def set_effort(self, effort: float):
        '''Sets the present effort requested from the motor based on an input value
           between -100.0 and 100.0'''

        # addresses entry if |effort| > 100
        if effort > 100:
            effort = 100.0
        elif effort < -100:
            effort = -100.0

        if effort >= 0:
            self.DIR_pin.low()
            self.PWM_pin.pulse_width_percent(effort)
        else:
            self.DIR_pin.high()
            self.PWM_pin.pulse_width_percent(-effort)



    def enable(self):
        '''Enables the motor driver by taking it out of sleep mode into brake mode'''
        self.nSLP_pin.high()

    def disable(self):
        '''Disables the motor driver by taking it into sleep mode'''
        self.PWM_pin.pulse_width_percent(0)
        self.nSLP_pin.low()
from time import ticks_us, ticks_diff   # Use to get dt value in update()

class Encoder:
    '''A quadrature encoder decoding interface encapsulated in a Python class'''

    def __init__(self, tim, chA_pin, chB_pin):
        '''Initializes an Encoder object'''

        self.tim = tim
        self.chA_pin = chA_pin
        self.chB_pin = chB_pin

        self.max_count = 65535
        self.half_range = 32768

        self.position = 0  # Total accumulated position of the encoder
        self.prev_count = self.tim.counter()  # Counter value from the most recent update
        self.delta = 0  # Change in count between last two updates
        self.dt = 0  # Amount of time between last two updates
        self._last_time_us = ticks_us()

    def update(self):
        '''Runs one update step on the encoder's timer counter to keep
           track of the change in count and check for counter reload'''

        cur = self.tim.counter()
        now = ticks_us()

        dt_us = ticks_diff(now, self._last_time_us)

        # Avoid divide by 0
        if dt_us <= 0:
            return

        # Convert us to seconds
        self.dt = dt_us / 1000000

        raw_delta = cur - self.prev_count

        # Detect wrap around
        # If change since last update is larger than half the range -> underflow
        if raw_delta > self.half_range:
            raw_delta -= (self.max_count + 1)
        # If delta is less than negative half the total range -> overflow
        elif raw_delta < -self.half_range:
            raw_delta += (self.max_count + 1)

        self.delta = raw_delta
        self.position += raw_delta
        self.prev_count = cur
        self._last_time_us = now

    def get_position(self):
        '''Returns the most recently updated value of position as determined
           within the update() method'''

        return self.position

    def get_velocity(self):
        '''Returns a measure of velocity using the the most recently updated
           value of delta as determined within the update() method'''

        if self.dt == 0:
            return 0

        return self.delta / self.dt

    def zero(self):
        '''Sets the present encoder position to zero and causes future updates
           to measure with respect to the new zero position'''

        self.position = 0
        self.prev_count = self.tim.counter()
        self._last_time_us = ticks_us()

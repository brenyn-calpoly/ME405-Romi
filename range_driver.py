from utime import ticks_us, ticks_diff, sleep_us, ticks_ms

class distance:

    def __init__(self, trigger, echo):
        self.trigger = trigger
        self.echo = echo
        self.trigger.low()
        self.last_trigger_ms = 0
        self.min_interval_ms = 60
        self.last_distance = None

    def find_distance(self, timeout_us=30000):

        self.trigger.low()
        sleep_us(2)
        self.trigger.high()
        sleep_us(10)
        self.trigger.low()

        t0 = ticks_us()
        while self.echo.value() == 0:
            if ticks_diff(ticks_us(), t0) > timeout_us:
                return None
        start = ticks_us()

        t0 = ticks_us()
        while self.echo.value() == 1:
            if ticks_diff(ticks_us(), t0) > timeout_us:
                return None
        end = ticks_us()

        pulse_time = ticks_diff(end, start)

        self.last_distance = pulse_time / 58.0
        return self.last_distance
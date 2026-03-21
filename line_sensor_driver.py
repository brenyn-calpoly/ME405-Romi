oversample = 4
calibration_samples = 30


class LineChannel:
    def __init__(self, adc):

        self.adc = adc
        self.white_ctrl = None
        self.black_ctrl = None


    def read_raw(self):
        total = 0

        for _ in range(oversample):
            total += self.adc.read()

        return (total // oversample)

    def calibrate_white(self):
        total = 0

        for _ in range(calibration_samples):
            total += self.read_raw()
        self.white_ctrl = (total // calibration_samples)

    def calibrate_black(self):
        total = 0

        for _ in range(calibration_samples):
            total += self.read_raw()
        self.black_ctrl = (total // calibration_samples)

    def read_norm(self):
        raw = self.read_raw()

        # If not calibrated normalize to full range
        if self.white_ctrl == None or self.black_ctrl == None or self.white_ctrl == self.black_ctrl:
            return (raw / 4095.0)

        # Normalize the raw data to a 0 - 1 scale
        if self.black_ctrl > self.white_ctrl:
            value = (raw - self.white_ctrl) / (self.black_ctrl - self.white_ctrl)
        else:
            value = (self.white_ctrl - raw) / (self.white_ctrl - self.black_ctrl)

        if value < 0:
            value = 0
        if value > 1:
            value = 1

        return value


positions = [-16, -8, 0, 8, 16]  # [mm]


class LineArray:
    def __init__(self, channels):

        self.channels = channels
        self.line_threshold = 0.4

    def calibrate_white(self):
        for chan in self.channels:
            chan.calibrate_white()

    def calibrate_black(self):
        for chan in self.channels:
            chan.calibrate_black()

    def find_centroid(self):

        # centroid = [sum(position(i) * norms(i))] / sum(norms(i))

        norms = []
        for chan in self.channels:
            val = chan.read_norm()
            if val < self.line_threshold:
                val = 0
            norms.append(val)

        denominator = sum(norms)

        if denominator == 0:
            return None

        numerator = 0.0
        for position, weight in zip(positions, norms):
            numerator += position * weight

        centroid_raw = numerator / denominator

        return centroid_raw
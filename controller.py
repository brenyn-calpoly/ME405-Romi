class Controller:


   def __init__(self, Kp, Ki, Kff, dt):
       '''Init of the controller requires gains (Kp, Ki, Kff)
          and a period time: dt'''


       self.Kp = Kp
       self.Ki = Ki
       self.Kff = Kff
       self.dt = dt
       self.i_error = 0.0




   def update(self, setpoint, measure):
       '''setpoint = desired velocity
          measure = measrued velocity'''

       # e = r - x
       error = setpoint - measure


       # feedforward section
       # setpoint * ff gain
       ff = self.Kff * setpoint


       # PI controller section
       # integrates error over time
       self.i_error += error * self.dt
       # error times P gain
       self.p_error = self.Kp * error


       # Ki*integral_error + Kp*error + Kff*setpoint
       effort = (self.Ki * self.i_error) + self.p_error + ff

       if effort > 100:
           effort = 100.0
       elif effort < -100:
           effort = -100.0

       return effort



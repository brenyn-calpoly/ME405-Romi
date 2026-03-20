# Romi Project
Overview:

This project utilizes a differential-drive robot (Romi) that autonomously follows a high-contrast track using a centroid-based line sensor algorithm and PID motor controllers. Additonally to track distance two quadrature encoders, one on each gear motor, wheel system. Theses encoders measure the rotational distane of each wheel allowing Romi's travel distance to be set for sections of the track where line following is not applicable. 

# Demonstration
[![Watch the demo](https://img.youtube.com/vi/rJuXOP3_y1Q/0.jpg)](https://youtu.be/rJuXOP3_y1Q)

# Hardware
![romi](https://github.com/user-attachments/assets/43540a37-eb58-451f-94a6-f14b92d9e887)

The image above is of Romi, a differential-drive robot kit produced by Pololu.

**Chassis:**  
Romi's chassis is injection molded plastic with a diameter of 165 mm and an integrated battery holder. It is powered by six AA batteries.


Wheels:

Two Pololu 70x8 mm wheels are attached to the motor shafts. These wheels have silicone tires for gripping the surface.


Motors:

Romi uses two brushed DC plastic gearmotors, operating at a nominal voltage of 4.5 V. It's gearbox ratio is 120:1.


Encoders:

For rotational distance and velocity tracking two quadrature encoders attached to the mini plastic gearmotors were implemented. The encoders are dual-channel Hall effect sensors. They offer a resolution of 12 counts per revolution, but paired with 120:1 gearmotors, the effective resolution is 1440 counts per wheel revolution.


**Reflectance Sensor:**
INSERT NAME, a five channel reflectance sensor board


# Software
Over


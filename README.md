Module mpu9150
-----------------
mpu9150 is a micropython module for the InvenSense MPU9150 sensor.
It measures acceleration, turn rate and the magnetic field in three axis.  
Breakoutboard: http://www.adafruit.com/products/1603  
data-sheet: http://ae-bst.resource.bosch.com/media/products/dokumente/bmp180/BST-BMP180-DS000-09.pdf

If you have any questions, open an issue.

### Wiring the sensor to the pyboard

| pyboard| bmp180 |
|:------:|:------:|
| VIN    | VIN    |
| 3V3    | 3Vo    |
| GND    | GND    |
| SCL    | SCL    |
| SDA    | SDA    |
| SCL    | ESC    |
| SDA    | ESD    |

Both the sensors SCL, SDA and ESC, ESD go to the same SDA, SCL on the pyboard.

### Quickstart

Example:
```python
from mpu9150 import MPU9150
imu = MPU9150()
print(imu.mode('wake'))
print(imu.sample_rate())
print(imu.accel_range())
print(imu.gyro_range())
temp = imu.get_temperature()
ax, ay, az = imu.get_accel()
gx, gy, gz = imu.get_gyro()
mx, my, mz = imu.get_mag()
print(temp, ax, gx, mx)
print(imu.accel_range(3))
print(imu.get_accel('x'))
```

Classes
-------
``MPU9150``  
Module for the MPU9150 pressure sensor.  
![UML diagramm](https://raw.githubusercontent.com/turbinenreiter/micropython-mpu9150/master/classes_MPU9150.png "UML diagramm")


Methods
--------------


`` mode(mode=None)``  
Returns current mode and sets it to ``mode`` if argument is passed.
``'wake'``: wakes the device
``'sleep'``: sets the device to sleep mode

``sample_rate(rate=None)``  
Returns the current sample rate and sets it to ``rate`` if argument is passed.
Any int can be passed, but not all rates are possible. Check the return value to see
what has been set.

``accel_range(accel_range=None)``  
Returns the current accel range and sets it to ``accel_range`` if argument is passed.
``accel_range`` can be 0, 1, 2 or 3.

`gyro_range(gyro_range=None)``  
Returns the current gyro range and sets it to ``gyro_range`` if argument is passed.
``gyro_range`` can be 0, 1, 2 or 3.

``get_accel(xyz=None)``  
Returns a list of accelerations in the specified directions in g. Pass a sting containing
the axis you want to get.
i.E.:   ``'xyz'`` returns ``[ax, ay, az]``
        ``'x'``   returns ``[ax]``
        ``'xz'``  returns ``[ax,az]``
        ``None``  defaults to ``'xyz'``

``get_gyro(xyz=None)``  
Returns a list of trun rates in the specified directions in deg/s. Pass a sting containing
the axis you want to get.
i.E.:   ``'xyz'`` returns ``[gx, gy, gz]``
        ``'x'``   returns ``[gx]``
        ``'xz'``  returns ``[gx,gz]``
        ``None``  defaults to ``'xyz'``

``get_mag(xyz=None)``  
Returns a list of the magnetic fields in the specified directions in uT. Pass a sting containing
the axis you want to get.
i.E.:   ``'xyz'`` returns ``[mx, my, mz]``
        ``'x'``   returns ``[mx]``
        ``'xz'``  returns ``[mx,mz]``
        ``None``  defaults to ``'xyz'``

``get_temperature()``  
Returns the temperature in degrees C.


Instance variables
------------------
``chip_id``  
ID of chip is hardcoded on the sensor.

``mpu_addr``  
I2C adress of the accelerometer and the gyroscope.

``mag_addr``  
I2C adress of the magnetometer.

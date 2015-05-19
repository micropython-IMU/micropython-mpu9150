Module mpu9150
-----------------
mpu9150 is a micropython module for the InvenSense MPU9150 sensor.
It measures acceleration, turn rate and the magnetic field in three axis.  
Breakoutboard: https://www.sparkfun.com/products/11486  

If you have any questions, open an issue.

### Wiring the sensor to the pyboard

| pyboard| mpu9150 |
|:------:|:-------:|
| VIN    | 3V3     |
| GND    | GND     |
| SCL    | SCL     |
| SDA    | SDA     |

### Quickstart

Example:
```python
from mpu9150 import MPU9150
imu = MPU9150()
print(imu.wake())
print(imu.sample_rate())
print(imu.accel_range())
print(imu.gyro_range())
temp = imu.get_temperature()
ax, ay, az = imu.get_accel()
gx, gy, gz = imu.get_gyro()
mx, my, mz = imu.get_mag()
print(temp, ax, gx, mx)

print(imu.sample_rate(4000))
print(imu.accel_range(3))
print(imu.gyro_range(3))

print(imu.get_accel('x'))
print(imu.get_gyro('xy'))
print(imu.get_mag('yz'))

print(imu.get_accel_raw())
print(imu.get_gyro_raw())
print(imu.get_mag_raw())

print(imu.sleep())
```

Classes
-------
``MPU9150``  
Module for the MPU9150 sensor.  
![UML diagramm](https://raw.githubusercontent.com/turbinenreiter/micropython-mpu9150/master/classes_MPU9150.png "UML diagramm")


Methods
--------------


`` wake()``  
wakes the device  

``sleep()``
sets the device to sleep mode  

``passthrough()``
sets passthrough mode  
``True``: activates  
``False``: deactivates  
If active, the magnetometer is passed through to the SDA, SCL pads. If you don't
connect ESD and ESC, you have to activate passthrough to use the magnetometer.

``sample_rate(rate=None)``  
Returns the current sample rate and sets it to ``rate`` if argument is passed.
Any int can be passed, but not all rates are possible. Check the return value to see
what has been set.

``accel_range(accel_range=None)``  
Returns the current accel range and sets it to ``accel_range`` if argument is passed.  
``accel_range`` can be 0, 1, 2 or 3.

``gyro_range(gyro_range=None)``  
Returns the current gyro range and sets it to ``gyro_range`` if argument is passed.  
``gyro_range`` can be 0, 1, 2 or 3.

``get_accel(xyz=None)``  
Returns a list of accelerations in the specified directions in g. Pass a sting containing
the axis you want to get.  
``'xyz'`` returns ``[ax, ay, az]``  
``'x'``   returns ``[ax]``  
``'xz'``  returns ``[ax,az]``  
``None``  defaults to ``'xyz'``  

``get_gyro(xyz=None, use_radians=False)``  
Returns a list of turn rates in the specified directions in deg/s or rad/s, defaulting to degrees.
Pass a sting containing the axis you want to get.  
``'xyz'`` returns ``[gx, gy, gz]``  
``'x'``   returns ``[gx]``  
``'xz'``  returns ``[gx,gz]``  
``None``  defaults to ``'xyz'``  

``get_mag(xyz=None)``  
Returns a list of the magnetic fields in the specified directions in uT. Pass a sting containing
the axis you want to get.  
``'xyz'`` returns ``[mx, my, mz]``  
``'x'``   returns ``[mx]``  
``'xz'``  returns ``[mx,mz]``  
``None``  defaults to ``'xyz'``  

``get_temperature()``  
Returns the temperature in degrees C.

``filter_range(filter_range=None)``
Returns the current accel and gyro low pass filter range and sets to ``filter_range`` if argument is passed.
``filter_range`` can be 0 to 6.
The digital low pass filter enables the effect of vibration to be reduced in the accelerometer and gyro readings.
The following table gives the approximate bandwidth and delay for the filter. Precise values differ
slightly between the accelerometer and the gyro and can be obtained from the device datasheet.

| value | bw(Hz) | Delay(mS) |
|:-----:|:------:|:---------:|
|  0    |  260   |    0.0    |
|  1    |  184   |    2.0    |
|  2    |   94   |    3.0    |
|  3    |   44   |    4.9    |
|  4    |   21   |    8.5    |
|  5    |   10   |   13.8    |
|  6    |    5   |   19.0    |

### Use in interrupt callbacks

These don't support code which uses the heap, which rules out a number of standard Python techniques including
exception handling and the use of floating point. The following methods provide access to the device where this
must be performed in a callback.

``get_accel_irq()``
``get_gyro_irq()``
``get_mag_irq()``
These methods populate iaccel[], igyro[], and imag[] instance variables respectively. These are 3 element lists
containing integer values with elements 0, 1 and 2 holding x, y and z values. These values are signed but not scaled:
it is the responsibility of the callback to apply a scaling factor depending on the range in use.

All return immediately. The magnetometer device differs from the others: whereas the accelerometer and gyro values
are automatically kept up to date the magnetometer has to be triggered and takes time to acquire a reading. Hence
``get_mag_irq()`` is designed for repeated polling, as in a timer callback. If the device has been triggered
and is ready it reads the data into the ``imag`` instance array. If it's triggered but not yet ready it does
nothing. If it's untriggered it triggers it leaves the array unchanged. Thus, under repeated polling, the array
will always hold the most recent data acquired from the magnetometer.

Note that the scaling factors of the accelerometer and gyro depend only on the range selected, hence these
can be hard coded in the callback. This works with the magnetometer but to get the most accurate readings the
factory-set corrections should be applied. These are in instance variable ``mag_correction[]`` but being
floating point values can't be used in a callback. Options (depending on application) are to apply them
outside the callback, or convert them to scaled integers in initialisation code.

See tests/irqtest.py for example code.

Instance variables
------------------
``chip_id``  
ID of chip is hardcoded on the sensor.

``mpu_addr``  
I2C adress of the accelerometer and the gyroscope.

``mag_addr``  
I2C adress of the magnetometer.

``timeout``  
Timeout for I2C operations.

``disable_interrupts``  
True or False, disables/enables interrupts. Disable to protect I2C operations.

``iaccel``
``igyro``
``imag``
3 element lists containing integer x, y, z accelerometer and gyro readings. These are used in conjunction with
get_accel_irq(), get_gyro_irq() and get_mag_irq() where the device is accessed from within an interrupt handler. In
normal use they are unpopulated.

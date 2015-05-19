# Test program for IRQ based access to MPU9150
# Note there will be small differences between the lines because
# of drift or movement occurring between the readings
import pyb
from mpu9150 import MPU9150
import micropython
micropython.alloc_emergency_exception_buf(100)

# Note: with a magnetometer read in the callback, a frequency of 1KHz hogged the CPU
tim = pyb.Timer(4, freq=500)            # freq in Hz

imu = MPU9150('Y', 1, True)
imu.gyro_range(0)
imu.accel_range(0)

def cb(timer):                          # Callback: populate array members
    imu.get_gyro_irq()
    imu.get_accel_irq()
    imu.get_mag_irq()

tim.callback(cb)

for count in range(10):
    pyb.delay(400)
    scale = 3.33198                     # Correction factors involve floating point
    mag = [0]*3                         # hence can't be done in interrupt callback
    for x in range(3):
        mag[x] = imu.imag[x]*imu.mag_correction[x]/scale
    print("Interrupt:", [x/16384 for x in imu.iaccel], [x/131 for x in imu.igyro], mag)
    print("Normal:   ", imu.get_accel(), imu.get_gyro(), imu.get_mag())
    print()

tim.callback(None)

def timing():                           # Check magnetometer call timings
    imu.mag_triggered = False           # May have been left True by above code
    start = pyb.micros()
    imu.get_mag_irq()
    t1 = pyb.elapsed_micros(start)
    start = pyb.micros()
    imu.get_mag_irq()
    t2 = pyb.elapsed_micros(start)
    pyb.delay(200)
    start = pyb.micros()
    imu.get_mag_irq()
    t3 = pyb.elapsed_micros(start)

    # 1st call initialises hardware
    # 2nd call tests it (not ready)
    # 3rd call tests ready and reads data
    print(t1, t2, t3) # 1st call takes 265uS second takes 175uS. 3rd takes 509uS

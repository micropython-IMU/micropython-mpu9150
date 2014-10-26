# Example 2 of nonblocking magnetometer reads, demonstrating delegation of polling to the scheduler
# Expects an MPU9150 on Y side and a 24*2 LCD with Hitachi controller wired as per PINLIST

import pyb
from usched import Sched, wait, Poller
from lcdthread import LCD, PINLIST                          # Library supporting Hitachi LCD module
from mpu9150 import MPU9150

def lcd_thread(mylcd,mpu9150):
    k = mpu9150.mag_correction
    mylcd[1] = "x {:5.3f} y {:5.3f} z {:5.3f}".format(k[0],k[1],k[2])
    while True:
        reason = (yield Poller(mpu9150.get_mag_status()))   # Scheduler returns when function instantiated by get_mag_status()
        if reason[1] == 1:                                  # returns something other than None. 1 indicates ready.
            z = mpu9150.get_mag()
            mylcd[0] = "x {:5.1f} y {:5.1f} z {:5.1f}".format(z[0],z[1],z[2])
        elif reason[1] == 2:
            mylcd[0] = "Mag read failure"
        yield from wait(0.5)

objSched = Sched()
lcd0 = LCD(PINLIST, objSched, cols = 24)
mpu9150 = MPU9150('Y',1,True)
objSched.add_thread(lcd_thread(lcd0, mpu9150))
objSched.run()



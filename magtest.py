'''
Demo of MPU9150 nonblocking reads and the reading and use of correction factors.
Shows that call to get_mag() returns fast.
'''

from mpu9150 import MPU9150
import pyb
TIMERPERIOD = 0x7fffffff

def makedt():     # Produce a function returning the time since it was last called
    t = pyb.micros()
    def gdt():
        nonlocal t
        end = pyb.micros()
        dt = ((end - t) & TIMERPERIOD)/1000000.0
        t = end
        return dt
    return gdt

def testfunc(a):
    getdt = makedt() # Start the clock
    runmag = a.get_mag_status()
    mag_status = runmag()          # Create a run-and-test function instance
    while mag_status is None:
        mag_status = runmag()
    print("Wait time = {:5.2f}mS".format(getdt()*1000))
    z = a.get_mag()
    print("Time to get = {:5.2f}mS".format(getdt()*1000))
    print("x = {:5.3f} y = {:5.3f} z = {:5.3f}".format(z[0],z[1],z[2]))
    print("Mag", mag_status)
    print("Correction factors: x = {:5.3f} y = {:5.3f} z = {:5.3f}".format(
        a.mag_correction[0],
        a.mag_correction[1],
        a.mag_correction[2]))

def test():
    mpu9150 = MPU9150('Y',1,True)
    testfunc(mpu9150)
    print()
    pyb.delay(250)
    print("Repeating")
    testfunc(mpu9150)

test()


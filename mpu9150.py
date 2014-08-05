'''
mpu9150 is a micropython module for the InvenSense MPU9150 sensor.
It measures acceleration, turn rate and the magnetic field in three axis.

The MIT License (MIT)
Copyright (c) 2014 Sebastian Plamauer, oeplse@gmail.com
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import pyb
import os
from struct import unpack as unp

class MPU9150():
    '''
    Module for the MPU9150 9DOF IMU. Pass X or Y according to on which side the
    sensor is connected. Pass 1 for the first, 2 for the second connected sensor.
    '''

    _mpu_addr = (104, 105)  # addresses of MPU9150
                            # there can be two devices
                            # connected, first on 104,
                            # second on 105
    _mag_addr = 12

    # init
    def __init__(self, side_str=None, no_of_dev=None):

        # choose wich i2c port to use
        if side_str == 'X':
            side = 1
        elif side_str == 'Y':
            side = 2
        else:
            print('pass either X or Y, defaulting to Y')
            side = 2

        if no_of_dev is not in (1, 2):
            print('pass either 1 or 2, defaulting to 1)
            no_of_dev = 1

        # create i2c object
        self._mpu_i2c = pyb.I2C(side, pyb.I2C.MASTER)
        self.mpu_addr = self._mpu_addr[no_of_dev-1]
        self.mag_addr = self._mag_addr
        self.chip_id = unp('>h', self._mpu_i2c.mem_read(1, self.mpu_addr, 0x75))[0]

    # mode
    def mode(self, mode=None):
        '''
        Returns mode, pass sleep or wake to set asleep or awake.
        '''
        # set mode
        if mode is None:
            pass
        elif mode == 'wake':
            self._mpu_i2c.mem_write(0x01, self.mpu_addr, 0x6B)
        elif mode == 'sleep':
            self._mpu_i2c.mem_write(0x40, self.mpu_addr, 0x6B)
        else:
            print('pass either wake or sleep')

        # get mode
        if self._mpu_i2c.mem_read(1, self.mpu_addr, 0x6B) == b'\x01':
            return 'awake'
        else:
            return 'asleep'

    # sample rate
    def sample_rate(self, rate=None):
        '''
        Returns the sample rate or sets it to the passed arg in Hz. Note that
        not all sample rates are possible. Check the return value to see which
        rate was actually set.
        '''

        gyro_rate = 8000 # Hz

        # set rate
        if rate is not None:
            rate_div = int( gyro_rate/rate - 1 )
            if rate_div > 255:
                rate_div = 255
            self._mpu_i2c.mem_write(rate_div, self.mpu_addr, 0x19)

        # get rate
        return gyro_rate/(unp('<H', self._mpu_i2c.mem_read(1, self.mpu_addr, 0x19))[0]+1)

    # accelerometer range
    def accel_range(self, accel_range=None):
        '''
        Returns the accelerometer range or sets it to the passed arg.
        Pass:               0   1   2   3
        for range +/-:      2   4   8   16  g 
        '''
        # set range
        if accel_range is None:
            pass
        else:
            ar = (0x00, 0x08, 0x10, 0x18)
            try:
                self._mpu_i2c.mem_write(ar[accel_range], self.mpu_addr, 0x1C)
            except IndexError:
                print('accel_range can only be 0, 1, 2 or 3')

        # get range
        return int(unp('<H', self._mpu_i2c.mem_read(1, self.mpu_addr, 0x1C))[0]/8)

    # gyroscope range
    def gyro_range(self, gyro_range=None):
        '''
        Returns the gyroscope range or sets it to the passed arg.
        Pass:               0   1   2    3
        for range +/-:      250 500 1000 2000  degrees/second
        '''
        # set range
        if gyro_range is None:
            pass
        else:
            gr = (0x00, 0x08, 0x10, 0x18)
            try:
                self._mpu_i2c.mem_write(gr[gyro_range], self.mpu_addr, 0x1B)
            except IndexError:
                print('gyro_range can only be 0, 1, 2 or 3')

        # get range
        return int(unp('<H', self._mpu_i2c.mem_read(1, self.mpu_addr, 0x1B))[0]/8)

    # get acceleration
    def get_accel(self, xyz=None):
        '''
        Returns the accelerations on axis passed in arg. Pass xyz or every 
        subset of this string. None defaults to xyz.
        '''
        if xyz is None:
            xyz = 'xyz'
        scale = (16384, 8192, 4096, 2048)
        ar = self.accel_range()
        axyz = {'x': unp('>h', self._mpu_i2c.mem_read(2, self.mpu_addr, 0x3B))[0]/scale[ar],
                'y': unp('>h', self._mpu_i2c.mem_read(2, self.mpu_addr, 0x3D))[0]/scale[ar],
                'z': unp('>h', self._mpu_i2c.mem_read(2, self.mpu_addr, 0x3F))[0]/scale[ar]}
        aout = []
        for char in xyz:
            aout.append(axyz[char])
        return aout

    def get_temperature(self):
        '''
        Returns the temperature in degree C.
        '''
        return unp('>h', self._mpu_i2c.mem_read(2, self.mpu_addr, 0x41))[0]/340 + 35

    def get_gyro(self, xyz=None):
        '''
        Returns the turn rate on axis passed in arg in deg/s. Pass xyz or every 
        subset of this string. None defaults to xyz.
        '''
        if xyz is None:
            xyz = 'xyz'
        scale = (131, 65.5, 32.8, 16.4)
        gr = self.gyro_range()
        gxyz = {'x': unp('>h', self._mpu_i2c.mem_read(2, self.mpu_addr, 0x43))[0]/scale[gr],
                'y': unp('>h', self._mpu_i2c.mem_read(2, self.mpu_addr, 0x45))[0]/scale[gr],
                'z': unp('>h', self._mpu_i2c.mem_read(2, self.mpu_addr, 0x47))[0]/scale[gr]}
        gout = []
        for char in xyz:
            gout.append(gxyz[char])
        return gout

    def get_mag(self, xyz=None):
        '''
        Returns the turn rate on axis passed in arg in uT. Pass xyz or every 
        subset of this string. None defaults to xyz.
        '''
        if xyz is None:
            xyz = 'xyz'
        self._mpu_i2c.mem_write(0x01, self.mag_addr, 0x0A)
        pyb.delay(1)
        print(self._mpu_i2c.mem_read(6, 12, 0x03))
        scale = 3.33198
        mxyz = {'y': unp('<h', self._mpu_i2c.mem_read(2, self.mag_addr, 0x03))[0]/scale,
                'x': unp('<h', self._mpu_i2c.mem_read(2, self.mag_addr, 0x05))[0]/scale,
                'z': -unp('<h', self._mpu_i2c.mem_read(2, self.mag_addr, 0x07))[0]/scale}
        mout = []
        for char in xyz:
            mout.append(mxyz[char])
        return mout

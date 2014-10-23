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

class MPU9150_Exception(Exception):
    pass

class MPU9150():
    '''
    Module for the MPU9150 9DOF IMU. Pass X or Y according to on which side the
    sensor is connected. Pass 1 for the first, 2 for the second connected sensor.
    By default interrupts are disabled while reading or writing to the device. This
    prevents occasional bus lockups in the presence of pin interrupts, at the cost
    of disabling interrupts for about 250uS.
    '''

    _mpu_addr = (104, 105)  # addresses of MPU9150
                            # there can be two devices
                            # connected, first on 104,
                            # second on 105
    _mag_addr = 12

    # init
    def __init__(self, side_str=None, no_of_dev=None, disable_interrupts=None):

        # choose which i2c port to use
        if side_str == 'X':
            side = 1
        elif side_str == 'Y':
            side = 2
        else:
            print('pass either X or Y, defaulting to X')
            side = 1

        # choose which sensor to use if two are connected
        if no_of_dev is None:
            print('pass either 1 or 2, defaulting to 1')
            no_of_dev = 1

        self.timeout = 10

        # create i2c object
        self.disable_interrupts = False
        self._mpu_i2c = pyb.I2C(side, pyb.I2C.MASTER)
        self.mpu_addr = int(self._mpu_addr[no_of_dev-1])
        self.mag_addr = self._mag_addr
        self.chip_id = int(unp('>h', self._read(1, 0x75, self.mpu_addr))[0])

        # now apply user setting for interrupts
        if disable_interrupts is True:
            self.disable_interrupts = True
        elif disable_interrupts is False:
            self.disable_interrupts = False
        else:
            print('pass either True or False, defaulting to True')
            self.disable_interrupts = True

        # wake it up
        self.wake()
        self.passthrough(False)
        self.accel_range(3)
        self._ar = self.accel_range()
        self.gyro_range(3)
        self._gr = self.gyro_range()


    # read from device
    def _read(self, count, memaddr, devaddr):
        '''
        Perform a memory read.
        '''
        irq_state = True
        if self.disable_interrupts:
            irq_state = pyb.disable_irq()
        try:
            result = self._mpu_i2c.mem_read(count,
                                            devaddr,
                                            memaddr,
                                            timeout=self.timeout)
        except:
            raise MPU9150_Exception("I2C Memory read failed")
        pyb.enable_irq(irq_state)
        return result

    # write to device
    def _write(self, data, memaddr, devaddr):
        '''
        Perform a memory write.
        '''
        irq_state = True
        if self.disable_interrupts:
            irq_state = pyb.disable_irq()
        try:
            result = self._mpu_i2c.mem_write(data,
                                             devaddr,
                                             memaddr,
                                             timeout=self.timeout)
        except:
            raise MPU9150_Exception("I2C Memory write failed")
        pyb.enable_irq(irq_state)
        return result

    # wake
    def wake(self):
        '''
        Wakes the device.
        '''
        try:
            self._write(0x01, 0x6B, self.mpu_addr)
        except MPU9150_Exception as response:
            print(response)
        return 'awake'

    # mode
    def sleep(self):
        '''
        Sets the device to sleep mode.
        '''
        try:
            self._write(0x40, 0x6B, self.mpu_addr)
        except MPU9150_Exception as response:
            print(response)
        return 'asleep'

    # passthrough
    def passthrough(self, mode=None):
        '''
        Returns passthrough mode, pass True or False to activate/deactivate.
        '''
        # set mode
        try:
            if mode is None:
                pass
            elif mode == True:
                self._write(0x00, 0x37, self.mpu_addr)
                self._write(0x00, 0x6A, self.mpu_addr)
            elif mode == False:
                self._write(0x02, 0x37, self.mpu_addr)
                self._write(0x00, 0x6A, self.mpu_addr)
            else:
                print('pass either True or False')

            # get mode
            if self._read(1, 0x37, self.mpu_addr) == b'\x02':
                return False
            else:
                return True
        except MPU9150_Exception as response:
            print(response)

    # sample rate
    def sample_rate(self, rate=None):
        '''
        Returns the sample rate or sets it to the passed arg in Hz. Note that
        not all sample rates are possible. Check the return value to see which
        rate was actually set.
        '''

        gyro_rate = 8000 # Hz

        # set rate
        try:
            if rate is not None:
                rate_div = int( gyro_rate/rate - 1 )
                if rate_div > 255:
                    rate_div = 255
                self._write(rate_div, 0x19, self.mpu_addr)

            # get rate
            rate = gyro_rate/(unp('<H', self._read(1, 0x19, self.mpu_addr))[0]+1)
        except MPU9150_Exception as response:
            print(response)
            rate = None
        return rate

    # accelerometer range
    def accel_range(self, accel_range=None):
        '''
        Returns the accelerometer range or sets it to the passed arg.
        Pass:               0   1   2   3
        for range +/-:      2   4   8   16  g 
        '''
        # set range
        try:
            if accel_range is None:
                pass
            else:
                ar = (0x00, 0x08, 0x10, 0x18)
                try:
                    self._write(ar[accel_range], 0x1C, self.mpu_addr)
                except IndexError:
                    print('accel_range can only be 0, 1, 2 or 3')
            # get range
            ari = int(unp('<H', self._read(1, 0x1C, self.mpu_addr))[0]/8)
        except MPU9150_Exception as response:
            print(response)
            ari = None
        if ari is not None:
            self._ar = ari
        return ari

    # gyroscope range
    def gyro_range(self, gyro_range=None):
        '''
        Returns the gyroscope range or sets it to the passed arg.
        Pass:               0   1   2    3
        for range +/-:      250 500 1000 2000  degrees/second
        '''
        # set range
        try:
            if gyro_range is None:
                pass
            else:
                gr = (0x00, 0x08, 0x10, 0x18)
                try:
                    self._write(gr[gyro_range], 0x1B, self.mpu_addr)
                except IndexError:
                    print('gyro_range can only be 0, 1, 2 or 3')
            # get range
            gri = int(unp('<H', self._read(1, 0x1B, self.mpu_addr))[0]/8)
        except MPU9150_Exception as response:
            gri = None
            print(response)

        if gri is not None:
            self._gr = gri
        return gri

    # get raw temperature
    def get_temperature_raw(self):
        '''
        Returns the temperature in bytes.
        '''
        try:
            t = self._read(2, 0x41, self.mpu_addr)
        except MPU9150_Exception as response:
            print(response)
            t = b'\x00\x00'
        return t

    # get temperature
    def get_temperature(self):
        '''
        Returns the temperature in degree C.
        '''
        return unp('>h', self.get_temperature_raw())[0]/340 + 35

    # get raw acceleration
    def get_accel_raw(self):
        '''
        Returns the accelerations on xyz in bytes.
        '''
        try:
            axyz = self._read(6, 0x3B, self.mpu_addr)
        except MPU9150_Exception as response:
            print(response)
            axyz = b'\x00\x00\x00\x00\x00\x00'
        return axyz

    # get acceleration
    def get_accel(self, xyz=None):
        '''
        Returns the accelerations on axis passed in arg. Pass xyz or every 
        subset of this string. None defaults to xyz.
        '''
        if xyz is None:
            xyz = 'xyz'
        scale = (16384, 8192, 4096, 2048)
        raw = self.get_accel_raw()
        axyz = {'x': unp('>h', raw[0:2])[0]/scale[self._ar],
                'y': unp('>h', raw[2:4])[0]/scale[self._ar],
                'z': unp('>h', raw[4:6])[0]/scale[self._ar]}

        aout = []
        for char in xyz:
            aout.append(axyz[char])
        return aout

    # get raw gyro
    def get_gyro_raw(self):
        '''
        Returns the turn rate on xyz in bytes.
        '''
        try:
            gxyz = self._read(6, 0x43, self.mpu_addr)
        except MPU9150_Exception as response:
            print(response)
            gxyz = b'\x00\x00\x00\x00\x00\x00'
        return gxyz

    # get gyro
    def get_gyro(self, xyz=None):
        '''
        Returns the turn rate on axis passed in arg in deg/s. Pass xyz or every 
        subset of this string. None defaults to xyz.
        '''
        if xyz is None:
            xyz = 'xyz'
        scale = (131, 65.5, 32.8, 16.4)
        raw = self.get_gyro_raw()
        gxyz = {'x': unp('>h', raw[0:2])[0]/scale[self._gr],
                'y': unp('>h', raw[2:4])[0]/scale[self._gr],
                'z': unp('>h', raw[4:6])[0]/scale[self._gr]}

        gout = []
        for char in xyz:
            gout.append(gxyz[char])
        return gout

    # get raw mag
    def get_mag_raw(self):
        '''
        Returns the mag on xyz in bytes.
        '''
        try:
            self._write(0x01, 0x0A, self.mag_addr)
            while self._read(1, 0x02, self.mag_addr) != b'\x01':
                pass
            mxyz = self._read(6, 0x03, self.mag_addr)
        except MPU9150_Exception as response:
            print(response)
            mxyz = b'\x00\x00\x00\x00\x00\x00'
        return mxyz

    # get mag
    def get_mag(self, xyz=None):
        '''
        Returns the compass data on axis passed in arg in uT. Pass xyz or every 
        subset of this string. None defaults to xyz.
        '''
        # TODO: Sensitivity Adjustment as described in page 59 of register map
        if xyz is None:
            xyz = 'xyz'
        scale = 3.33198
        raw = self.get_mag_raw()
        mxyz = {'y': unp('<h', raw[0:2])[0]/scale,
                'x': unp('<h', raw[2:4])[0]/scale,
                'z': -unp('<h', raw[4:6])[0]/scale}

        mout = []
        for char in xyz:
            mout.append(mxyz[char])
        return mout

from mpu9250_jmdev.mpu_9250 import MPU9250
from mpu9250_jmdev.registers import *
from time import sleep
import numpy as np
import math
from scipy.fftpack import fft
from scipy import signal


class IMU:
    def __init__(self):
        self.mpu = MPU9250(
            address_ak=AK8963_ADDRESS,
            address_mpu_master=MPU9050_ADDRESS_68,  # In 0x68 Address
            address_mpu_slave=None,
            bus=1,
            gfs=GFS_1000,
            afs=AFS_8G,
            mfs=AK8963_BIT_16,
            mode=AK8963_MODE_C100HZ)
        self.mpu.calibrateMPU6500()
        sleep(1)
        self.mpu.configure()  # Apply the settings to the registers.
        sleep(1)

    def read(self):
        return round(self.mpu.readAccelerometerMaster()[1], 3)
        # yield [self.mpu.readAccelerometerMaster(), self.mpu.readGyroscopeMaster(), self.mpu.readMagnetometerMaster(), self.mpu.readTemperatureMaster()]


if __name__ == "__main__":
    imu = IMU()
    # for i in imu.reader():
    # print(i)
    # sleep(0.1)
    while True:
        print(imu.read())

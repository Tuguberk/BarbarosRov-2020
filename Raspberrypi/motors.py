import time
from adafruit_servokit import ServoKit #Pca9685
kit = ServoKit(channels=16)


class SMotor: #Servo Motor
    def __init__(self, number, mid=90):
        self.number = number
        self.mid = mid
        kit.servo[self.number].angle = self.mid

    def speed(self, speed):
        kit.servo[self.number].angle = speed


class BMotor(SMotor): #Brushless Motor
    def __init__(self, number, mid=90):
        super().__init__(number, mid)
        kit.servo[self.number].set_pulse_width_range(1000, 1720) #Motor ppm min-max kalibrasyonu


if __name__ == "__main__":
    motors = []
    for i in range(4):
        motors.append(BMotor(i))
    while True:
        for i in motors:
            i.speed(90)

        time.sleep(1)
        speed = int(input("Hız giriniz: "))
        for i in motors:
            i.speed(speed)
        input("tamam mı?")

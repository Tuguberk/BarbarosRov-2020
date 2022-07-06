import numpy as np
from threading import Thread
import base64
import cv2
import zmq
from time import sleep
from picamera.array import PiRGBArray
from picamera import PiCamera

from imu import IMU
from motors import kit, BMotor, SMotor


def vmap(x, in_min, in_max, out_min, out_max): #Arduino map
    return int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)


def constrain(x, min, max):
    if x < min:
        return min
    elif x > max:
        return max
    else:
        return x


def SpeedCalculate(x, y, orta=90):
    x_fark = x-orta
    y_fark = y-orta
    if x_fark == 0 or y_fark == 0:
        return [orta+(x_fark+y_fark), orta+(-x_fark+y_fark)]

    else:
        return [orta+(x_fark+y_fark)/2, orta+(-x_fark+y_fark)/2]


class Threads:
    def startThreads(self, *args):
        for i in args:
            i.deamon = True
            i.start()


class SendMessage(Threads):
    def __init__(self, ip="192.168.137.19", port="5557"):
        self.message = ""
        self.contex = zmq.Context()
        self.socket = self.contex.socket(zmq.PUB)
        self.socket.bind("tcp://{}:{}".format(ip, port))
        self.thread = Thread(target=self.sender)
        self.startThreads(self.thread)

    def send(self, message):
        self.message = message

    def sender(self):
        while True:
            if self.message != "":
                self.socket.send_pyobj(self.message)
                self.message = ""


class SendUsbCam(SendMessage):
    def __init__(self, ip="192.168.137.19", port="5555", device=0):
        self.camera = cv2.VideoCapture(device)
        super().__init__(ip, port)

    def sender(self):
        while True:
            grabbed, frame = self.camera.read()  # grab the current frame
            frame = cv2.resize(frame, (640, 480))  # resize the frame
            #frame= cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            encoded, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer)
            self.socket.send(jpg_as_text)


class SendRaspiCam(SendMessage):
    def __init__(self, ip="192.168.137.19", port="5554"):
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.framerate = 32
        self.rawCapture = PiRGBArray(self.camera, size=(640, 480))
        # self.rawCapture = io.BytesIO()
        super().__init__(ip, port)

    def sender(self):
        for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=False):
            encoded, buffer = cv2.imencode('.jpg', frame.array)
            jpg_as_text = base64.b64encode(buffer)
            self.socket.send(jpg_as_text)
            self.rawCapture.truncate(0)
            self.rawCapture.seek(0)


class RecvMessage(Threads):
    def __init__(self, ip="192.168.137.1", port="5556"):
        self.data = []
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect('tcp://{}:{}'.format(ip, port))
        self.socket.setsockopt(zmq.SUBSCRIBE, b'')
        self.thread = Thread(target=self.recver)
        self.startThreads(self.thread)

    def recver(self):
        print("Mesajlar alınıyor!")
        while True:
            self.data = self.socket.recv_pyobj()
            # print(self.data)


class RDrive(RecvMessage):
    def __init__(self, ip="192.168.1.30", port="5556", mid=90):
        super().__init__(ip, port)
        self.imu = IMU()
        self.data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.motors = []
        self.servo = SMotor(6)
        self.mid = mid
        for i in range(6):
            self.motors.append(BMotor(i))
        for i in self.motors:
            i.speed(self.mid)
        print("Motorlar Hazır!")
        ###PID###
        self.error, self.errorLast, self.errorInte = 0, 0, 0
        self.Kp = 20
        self.Ki = 0
        self.Kd = 15
        ########
        self.startThreads(Thread(target=self.drive))

    def drive(self):
        while True:
            speedCross = SpeedCalculate(vmap(
                self.data[0], -1, 1, 0, 180), vmap(self.data[1], -1, 1, 0, 180))
            speedTurn = vmap(self.data[3], -1, 1, -90, 90)
            speedHeight = vmap(self.data[2], 1, -1, 180, 0)
            speedServo = vmap(self.data[6], 0, 1, 0, 180)
            control = self.data[9]
            ###PID####
            data = self.imu.read()
            pidOutput = self.pidCalulate(data)
            ##########
            speedA = constrain(speedCross[1]+speedTurn, 0, 180)
            speedB = constrain(speedCross[0]-speedTurn, 0, 180)
            speedC = constrain(speedCross[1]-speedTurn, 0, 180)
            speedD = constrain(speedCross[0]+speedTurn, 0, 180)
            speedE = speedHeight
            speedF = speedHeight
            speedG = speedServo
            print(
                f"A:{speedA}  B:{speedB}   C:{speedC} D:{speedD}  E:{speedE}  F:{speedF}  G:{speedG}  IMU:{data}  PID:{pidOutput}")
            if control:
                self.motors[0].speed(speedA)
                self.motors[1].speed(speedB)
                self.motors[2].speed(speedC)
                self.motors[3].speed(speedD)
                self.motors[4].speed(speedE)
                self.motors[5].speed(speedF)
                self.servo.speed(speedG)
            else:
                self.motors[0].speed(90)
                self.motors[1].speed(90)
                self.motors[2].speed(90)
                self.motors[3].speed(90)
                self.motors[4].speed(90)
                self.motors[5].speed(90)
                self.servo.speed(0)

    def pidCalulate(self, input):
        self.error = self.error * 0.3 + input * 0.7  # filter
        errorDiff = self.error - self.errorLast
        errorInte = constrain(self.errorInte+self.error, -50, 50)
        output = self.Kp * self.error + self.Ki * errorInte + self.Kd * errorDiff
        self.errorLast = self.error
        return output


if __name__ == '__main__':
    """
    Çalışmasını istediğin kodları yorumdan çıkar. 
    Her biri ayrı bir thread spawn edecek
    """

    # camera = SendUsbCam()
    # camera_2 = SendRaspiCam()
    driver = RDrive()
    # message_recv = RecvMessage()
    # message_send = SendMessage()
    # imu_sensor = IMU()
    # for i in imu_sensor.reader():
    # print(i)
    # sleep(0.4)

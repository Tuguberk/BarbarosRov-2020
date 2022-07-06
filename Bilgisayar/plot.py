import random
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from threading import Thread
from time import sleep



class Animation:
    def __init__(self,interval=100):
        plt.style.use("fivethirtyeight")
        self.interval = interval
        self.x_vals = []
        self.y_vals = []
        self.y2_vals = []
        self.y3_vals = []
        self.index = count()
        Thread(target=plt.show).start()
        

    def next(self,y1,y2,y3):
        self.x_vals.append(next(self.index))
        self.y_vals.append(y1)
        self.y2_vals.append(y2)
        self.y3_vals.append(y3)
        plt.cla()
        plt.plot(self.x_vals,self.y_vals, label = "Veri1")
        plt.plot(self.x_vals,self.y2_vals, label = "Veri2")
        plt.plot(self.x_vals,self.y3_vals, label = "Veri3")
        

ani= Animation()
while True:
    ani.next(random.randint(0,100),random.randint(0,100),random.randint(0,100))
    sleep(0.1)


        

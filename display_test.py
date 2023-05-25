import tkinter as tk
from tkinter import * # VERY INEFFICIENT, CHANGE LATER WHEN I REALIZE WHAT I ACTUALLY NEED FROM TK
from tkinter import ttk
import sqlite3
import time
import math
import RPi.GPIO as GPIO
import time, sys

REVERSE_SENSOR_GPIO = 21
NETURAL_SENSOR_GPIO = 16
ONE_SENSOR_GPIO = 20
TWO_SENSOR_GPIO = 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(REVERSE_SENSOR_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(NETURAL_SENSOR_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(ONE_SENSOR_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(TWO_SENSOR_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)


def countPulseR(channel2):
    global reverse
    reverse = 'R'
    print(reverse)
    time.sleep(1)
    
    
def countPulseN(channel3):
    global netural
    netural = 'N'
    print(netural)
    time.sleep(1)
    
def countPulse1(channel4):
    global one
    one = '1'
    print(one)
    time.sleep(1)
    
def countPulse2(channel5):
    global two
    two = '2'
    print(two)
    time.sleep(1)

class Meter(tk.Canvas):
    def __init__(self, master=None, size=600, startAngle=-135, totalAngle=-270, maxVal=30.0, decimals=0, text='mph', labelCount=7, labelIsRatio=False, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        # Setting up size parameters
        self.center = (int)(size / 2)
        margin = size / 25
        
        # Setting up pointer parameters
        self.startAngle = startAngle
        self.totalAngle = totalAngle
        self.angleMaxMultiplier = 270 / maxVal
        self.pointerLength = size / 2.7
        pointerWidth = size / 50
        
        # Setting up text parameters
        self.textSize = (int)(size / 10)
        self.text = text
        self.decimals = decimals
        
        # Placing labels
        for i in range (labelCount):
            angle = ((i / (labelCount - 1)) * totalAngle * -1) - startAngle # Formula derivation in System Specification
            x = self.center + (self.pointerLength - (size / 20)) * math.cos(math.radians(angle))
            y = self.center + (self.pointerLength - (size / 20)) * math.sin(math.radians(angle))
            
            if labelIsRatio is True:
                if i is (labelCount - 1):
                    val = 'F'
                elif i is 0:
                    val = 'E'
                else:
                    ratio = (((angle + startAngle) / self.angleMaxMultiplier) / maxVal).as_integer_ratio()
                    val = f"{ratio[0]}/{ratio[1]}"
            else:
                val = int((angle + startAngle) / self.angleMaxMultiplier)
            
            self.create_text(x, y, text=val, font=('Arial', int(self.textSize * 0.5)), fill='white')
            
        
        # Placing components onto the canvas
        self.configure(width=size, height=size, borderwidth=0)
        self.create_oval(5, 5, size - 5, size - 5, width=5, outline='white') # Outline
        self.create_text(size / 2, (size * 9) / 11, text="0 mph", font=('Arial', self.textSize), tags=('speed'), fill='white') # Text on the bottom
        self.create_arc(margin * 2, margin * 2, size - (margin * 2), size - (margin * 2), start=startAngle, extent=totalAngle, width=(int)(size / 60), style='arc', outline='green2') # Arc from min to max
        self.pointer = self.create_line(self.center, self.center, 0, 0, width=pointerWidth, arrow='last', fill='red2') # Pointer
        self.set_value(0)


    def set_value(self, val):
        angle = (val * self.angleMaxMultiplier) - self.startAngle # Formula derivation in System Specification
        x = self.center + self.pointerLength * math.cos(math.radians(angle))
        y = self.center + self.pointerLength * math.sin(math.radians(angle))
        self.coords(self.pointer, self.center, self.center, x, y)
        if self.decimals > 0:
            self.itemconfigure('speed', text=f"{round(val, self.decimals)} {self.text}")
        else:
            self.itemconfigure('speed', text=f"{round(val)} {self.text}")


class Indicator(tk.Canvas):
    def __init__(self, master=None, size=90, text='N', *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.configure(width=size, height=size, bg='whitesmoke', borderwidth=1, relief='solid')
        self.create_text(45, 45, text=text, font=('Arial', 50))
        
    def turnOn(self):
        self.configure(bg='red2')
        
    def turnOff(self):
        self.configure(bg='whitesmoke')

class BarMeter(tk.Canvas):
    def __init__(self, master=None, width=20, height=100, bottomText='E', topText='F', *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.configure(width=width, height=height, borderwidth=0)
        
    def set_value(self, val):
        print("hi")


def update():
    speed()
    gear()
    fuel()

    # Invalid command name "bunchofnumbersupdate" is an okay error to have. It occurs because we closed the window and then .after tries to run on nothingness.
    speedometer.after(35,update)

def speed():
    mphArray = connector.execute("SELECT mph FROM speed")
    connector.commit()
    for i in mphArray:
        countString = i
        # Turn it into a string, then get the substring, which can be converted to an integer
        holdCount = str(countString)
        stop = holdCount.find(",")
        mph = (holdCount[1:stop])
        
    speedometer.set_value(float(mph))


def gear():
    gearIndicatorR.turnOff()
    gearIndicatorN.turnOff()
    gearIndicator1.turnOff()
    gearIndicator2.turnOff()
    

    if GPIO.input(NETURAL_SENSOR_GPIO) == 0:
        gearIndicatorN.turnOn()
    elif GPIO.input(ONE_SENSOR_GPIO) == 0:
        gearIndicator1.turnOn()
    elif GPIO.input(TWO_SENSOR_GPIO) == 0:
        gearIndicator2.turnOn()
    else:
        gearIndicatorR.turnOn()


def fuel():
    global connector
    percentageArray = connector.execute("SELECT percentage FROM fuelFlow")
    connector.commit()
    for i in percentageArray:
        countString = i
        # Turn it into a string, then get the substring, which can be converted to an integer
        holdCount = str(countString)
        stop = holdCount.find(",")
        percentage = (holdCount[1:stop])
    
    fuelGauge.set_value(float(percentage) * 5.7)


try:
    root = Tk()
    root.attributes("-fullscreen", True)
    root.configure(background="black")
    root.config(cursor="none")
    root.geometry("1024x600")

    connector = sqlite3.connect('/home/pi/Documents/Baja 2023/Fuel Data 2')
    cursor = connector.cursor()

    speedometer = Meter(root, size=580, startAngle=-135, totalAngle=-270, maxVal=30.0, decimals=0, text='mph', labelCount=7, labelIsRatio=False)
    #fuelGauge = BarMeter(root, width=100, height=500, bottomText='E', topText='F')
    fuelGauge = Meter(root, size=325, startAngle=-135, totalAngle=-270, maxVal=5.7, decimals=1, text='L', labelCount=5, labelIsRatio=True)

    speedometer.pack(side=LEFT, padx=(5,0))
    fuelGauge.pack(side=LEFT, pady=(265,0), padx=(0,5))

    gearIndicatorR = Indicator(root, text='R')
    gearIndicatorN = Indicator(root, text='N')
    gearIndicator1 = Indicator(root, text='1')
    gearIndicator2 = Indicator(root, text='2')

    gearIndicatorR.pack(side=TOP, pady=(10, 5), padx=(0,5))
    gearIndicatorN.pack(side=TOP, pady=(5), padx=(0,5))
    gearIndicator1.pack(side=TOP, pady=(5), padx=(0,5))
    gearIndicator2.pack(side=TOP, pady=(5), padx=(0,5))

    speedometer.configure(background="black", highlightthickness=0)
    fuelGauge.configure(background="black", highlightthickness=0)

    update()
    root.mainloop()
    
except KeyboardInterrupt:
    print('\nkeyboard interrupt!')
    # This makes sure that the input from the gpio ports stops. This is IMPORTANT
    GPIO.cleanup()
    connector.close()
    sys.exit()

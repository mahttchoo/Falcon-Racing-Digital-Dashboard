import RPi.GPIO as GPIO
import time, sys
import sqlite3
import queue

HALL_EFFECT_GPIO = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(HALL_EFFECT_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)

conn = sqlite3.connect('/home/pi/Documents/Baja 2023/Fuel Data 2')
c = conn.cursor
cursor = conn.cursor()

rotationsTotal = 0
rotationsTemp = 0
q = queue.Queue()

for i in range (480):
    q.put(0)

def hallPulse(channel):
    global rotationsTemp
    rotationsTemp += 1

# Causes the countPulse() function to run when a pulse is sent into pin 13
GPIO.add_event_detect(HALL_EFFECT_GPIO, GPIO.FALLING, callback=hallPulse)

while True:
    q.put(rotationsTemp)
    rotationsDumped = q.get()
    
    rotationsTotal = rotationsTotal + rotationsTemp - rotationsDumped
    
    rotationsTemp = 0
    
    rps = 0.42 * rotationsTotal
    mph = 1.38 * rps
    #mph = round(mph, 5)
    
    conn.execute("DELETE FROM speed")
    conn.execute("INSERT INTO speed VALUES (?)", (mph, ))
    conn.commit()
    
    time.sleep(0.005)
    

GPIO.cleanup()
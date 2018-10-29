
from time import sleep
import time
import threading
import json
import RPi.GPIO as GPIO

try:
    GPIOs = {"TRIG": 15, "ECHO": 13}
    GPIO.setwarnings(False)    # Ignore warning for now
    GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
    GPIO.setup(GPIOs["TRIG"], GPIO.OUT)
    GPIO.setup(GPIOs["ECHO"], GPIO.IN)

    pulse_duration = 0.00
    pulse_start_time = 0.00
    pulse_end_time = 0.00
    distance = 0.00

    GPIO.output(GPIOs["TRIG"], GPIO.LOW)

    sleep(2)

    while True:


        print("Calculating distance")

        GPIO.output(GPIOs["TRIG"], GPIO.HIGH)

        sleep(0.00001)

        GPIO.output(GPIOs["TRIG"], GPIO.LOW)

        while GPIO.input(GPIOs["ECHO"])==0:
            pulse_start_time = time.time()
        while GPIO.input(GPIOs["ECHO"])==1:
            pulse_end_time = time.time()

        pulse_duration = pulse_end_time - pulse_start_time

        distance = round(pulse_duration * 17150, 0)

        print("Distance:",distance,"cm")

        sleep(0.25)

        GPIO.output(GPIOs["TRIG"], GPIO.LOW)
        #GPIO.cleanup(GPIOs.values())

finally:
      GPIO.cleanup()
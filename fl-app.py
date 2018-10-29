#!/usr/bin/python3

from flask import Flask, render_template
from time import sleep
import time
import threading
import json
import statistics
import RPi.GPIO as GPIO

values = {"cur": 63.00, "new": 63.00, "up": 97.00, "down": 63.00, "busy": False}

GPIOs = {"UP": 18, "DOWN": 16, "TRIG": 15, "ECHO": 13}
GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(GPIOs["UP"], GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(GPIOs["DOWN"], GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(GPIOs["TRIG"], GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(GPIOs["ECHO"], GPIO.IN)

app = Flask(__name__)

try:
    def triggerRelay(e, thread):
        if not values["busy"]:
            values["busy"] = True
            tn = threading.currentThread().getName()

            print(readHeight())

            print("cur", values["cur"])

            if tn == 'UP':
                while values["cur"] <= values["new"]:
                    print("cur", values["cur"])
                    print("new", values["new"])
                    GPIO.output(GPIOs[tn], GPIO.HIGH)
                    values["cur"] = readHeight()
                    sleep(0.075)

            if tn == 'DOWN':
                while values["cur"] >= values["new"]:
                    print("cur", values["cur"])
                    print("new", values["new"])
                    GPIO.output(GPIOs[tn], GPIO.HIGH)
                    values["cur"] = readHeight()
                    sleep(0.075)

            GPIO.output(GPIOs[tn], GPIO.LOW)
            print('Relay OFF \n')
            values["busy"] = False
        else:
            print('Desk is already busy moving!')

    def readHeight():
        return readHeightActual(10)

    def readHeightActual(times):
        distance = list()
        for t in range(times):
            pulse_start_time = time.time()
            pulse_end_time = time.time()
            GPIO.output(GPIOs["TRIG"], GPIO.HIGH)

            sleep(0.00001)

            GPIO.output(GPIOs["TRIG"], GPIO.LOW)

            while GPIO.input(GPIOs["ECHO"])==0:
                pulse_start_time = time.time()
            while GPIO.input(GPIOs["ECHO"])==1:
                pulse_end_time = time.time()

            pulse_duration = pulse_end_time - pulse_start_time
            
            distance.append(round(pulse_duration * 17150, 1))

        print("Distance:", distance, "cm")
        print("Distance:", statistics.median(distance), "cm")

        return round(statistics.median(distance), 1)


    @app.route('/')
    def index():
        values["cur"] = readHeight()
        return render_template('index.html', val=str(round(values["cur"], 1)))

    @app.route("/<action>")
    def action(action):
        if str(action).upper() == 'UP':
            values["new"] = values["up"]
            e = threading.Event()
            thread = threading.Thread(name=str(action).upper(), target=triggerRelay, args=(e, 2))
            thread.start()
            return "Desk is going UP"

        if str(action).upper() == 'DOWN' :
            values["new"] = values["down"]
            e = threading.Event()
            thread = threading.Thread(name=str(action).upper(), target=triggerRelay, args=(e, 2))
            thread.start()
            return "Desk is going DOWN"

        return "Desk is NOT moving"

    @app.route("/set/<action>")
    def actionSet(action):
        values["cur"] = readHeight()

        if str(action).upper() == 'UP':
            values["up"] = values["cur"]
            print("SET", action, ":", values[action])
            return "Desk upper height has been SET"

        if str(action).upper() == 'DOWN' :
            values["down"] = values["cur"]
            print("SET", action, ":", values[action])
            return "Desk lower height has been SET"

        return "Desk height has been SET"

    @app.route("/<action>/<val>")
    def actionTime(action, val):
        values["cur"] = readHeight()
        
        if str(action).upper() == 'UP':
            values["new"] = values["cur"] + float(val)
            e = threading.Event()
            thread = threading.Thread(name=str(action).upper(), target=triggerRelay, args=(e, 2))
            thread.start()
            return "Desk is going UP"

        if str(action).upper() == 'DOWN':
            values["new"] = values["cur"] - float(val)
            e = threading.Event()
            thread = threading.Thread(name=str(action).upper(), target=triggerRelay, args=(e, 2))
            thread.start()
            return "Desk is going DOWN"
            
        return "Desk is NOT moving"
    
    values["cur"] = readHeight()
    print("cur", values["cur"])

    if __name__ == "__main__":
        app.run(debug=False, host='0.0.0.0', port=80)

finally:
    GPIO.setup(GPIOs["UP"], GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(GPIOs["DOWN"], GPIO.OUT, initial=GPIO.LOW)
    GPIO.cleanup()
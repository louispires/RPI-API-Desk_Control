#!/usr/bin/python3

from flask import Flask, render_template
from time import sleep
import threading
import json
import RPi.GPIO as GPIO

values = {"new": 10, "cur": 10, "up": 11, "down": 9.5, "busy": False}

Relays = {"UP": 18, "DOWN": 16}
GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(Relays["UP"], GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Relays["DOWN"], GPIO.OUT, initial=GPIO.LOW)

app = Flask(__name__)

try:

    def triggerRelay(e, thread):
        if not values["busy"]:
            values["busy"] = True
            tn = threading.currentThread().getName()

            GPIO.output(Relays[tn], GPIO.HIGH)
            print('Relay ON \n')

            print(values["new"])

            tt = int(values["new"] * 10)

            print(range(tt))
            
            for t in range(tt):
                print(t)
                if tn == 'UP':
                    values["cur"] = values["cur"] + (0.1)
                if tn == 'DOWN':
                    values["cur"] = values["cur"] - (0.1)
                print(round(values["cur"], 1))
                sleep(0.1)

            GPIO.output(Relays[tn], GPIO.LOW)
            print('Relay OFF \n')
            values["busy"] = False
        else:
            print('Desk is already busy moving!')

    @app.route('/')
    def index():
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

    @app.route("/<action>/<time>")
    def actionTime(action, time):
        values["new"] = float(time)

        if str(action).upper() == 'UP':
            print(time)
            e = threading.Event()
            thread = threading.Thread(name=str(action).upper(), target=triggerRelay, args=(e, 2))
            thread.start()
            return "Desk is going UP"

        if str(action).upper() == 'DOWN':
            e = threading.Event()
            thread = threading.Thread(name=str(action).upper(), target=triggerRelay, args=(e, 2))
            thread.start()
            return "Desk is going DOWN"
            
        return "Desk is NOT moving"
    if __name__ == "__main__":
        app.run(debug=False, host='0.0.0.0', port=80)

except:
    GPIO.setup(Relays["UP"], GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(Relays["DOWN"], GPIO.OUT, initial=GPIO.LOW)
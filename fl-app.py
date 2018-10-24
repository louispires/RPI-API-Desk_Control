#!/usr/bin/python3


from flask import Flask, render_template
from time import sleep
import threading
import json
import RPi.GPIO as GPIO

try:
    values = {"new": 7.5, "cur": 7.5}

    LEDS = {"UP": 16, "DOWN": 40}
    GPIO.setwarnings(False)    # Ignore warning for now
    GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
    GPIO.setup(LEDS["UP"], GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(LEDS["DOWN"], GPIO.OUT, initial=GPIO.LOW)

    app = Flask(__name__)

    def triggerRelay(e, thread):
        tn = threading.currentThread().getName()

        GPIO.output(LEDS[tn], GPIO.HIGH)
        print('LED ON \n')

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

        GPIO.output(LEDS[tn], GPIO.LOW)
        print('LED OFF \n')

    @app.route('/')
    def index():
        return render_template('index.html', val=str(round(values["cur"], 1)))

    @app.route("/<action>")
    def action(action):
        if action == 'UP':
            e = threading.Event()
            thread = threading.Thread(name='UP', target=triggerRelay, args=(e, 2))
            thread.start()
            return "Desk is going UP"

        if action == 'DOWN':
            e = threading.Event()
            thread = threading.Thread(name='DOWN', target=triggerRelay, args=(e, 2))
            thread.start()
            return "Desk is going DOWN"

    @app.route("/<action>/<time>")
    def actionTime(action, time):
        values["new"] = float(time)

        if action == 'UP':
            print(time)
            e = threading.Event()
            thread = threading.Thread(name='UP', target=triggerRelay, args=(e, 2))
            thread.start()
            return "Desk is going UP"

        if action == 'DOWN':
            e = threading.Event()
            thread = threading.Thread(name='DOWN', target=triggerRelay, args=(e, 2))
            thread.start()
            return "Desk is going DOWN"

    if __name__ == "__main__":
        app.run(debug=True, host='0.0.0.0', port=80)

except:
    GPIO.output(LEDS["DOWN"], GPIO.LOW)
    GPIO.output(LEDS["UP"], GPIO.LOW)
import os
from flask import Flask, render_template, request, send_from_directory
from time import sleep
import time
import threading
import statistics
import RPi.GPIO as GPIO
import VL53L0X
import logging
import atexit
from flask import jsonify

# --- Configuration ---
GPIOs = {"UP": 18, "DOWN": 16, "TRIG": 15, "ECHO": 13}
TOF_ADDRESS = 0x29

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- GPIO Setup ---
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
for pin_name, pin in GPIOs.items():
    if pin_name != "ECHO":
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    else:
        GPIO.setup(pin, GPIO.IN)

# --- TOF Sensor Setup ---
tof = VL53L0X.VL53L0X(i2c_bus=1, i2c_address=TOF_ADDRESS)
global_timing = 20000

# --- Desk Controller Class ---
class DeskController:
    def __init__(self):
        self.lock = threading.Lock()
        self.state = {"cur": 71.0, "up": 105.0, "down": 71.0, "busy": False}
        self.exit_flag = False
        self._init_tof()

    def _init_tof(self):
        tof.open()
        tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.HIGH_SPEED)
        timing = tof.get_timing()
        global global_timing
        global_timing = max(timing, 20000)

    def _shutdown_tof(self):
        tof.stop_ranging()
        tof.close()

    def read_height(self):
        distances = []
        for _ in range(10):
            distance = tof.get_distance() / 10  # mm to cm
            if distance < 200:
                distances.append(distance)
            time.sleep(global_timing / 1000000.0)
        return round(statistics.mean(distances), 1) if distances else 0

    def trigger_relay(self, direction):
        with self.lock:
            if self.state["busy"]:
                return "Desk is already busy moving!"
            self.state["busy"] = True
            self.exit_flag = False

        try:
            target = self.state["up"] if direction == "UP" else self.state["down"]
            GPIO.output(GPIOs[direction], GPIO.HIGH)

            while not self.exit_flag:
                self.state["cur"] = self.read_height()
                if (direction == "UP" and self.state["cur"] >= target) or \
                   (direction == "DOWN" and self.state["cur"] <= target):
                    break
                sleep(0.5)
        finally:
            GPIO.output(GPIOs[direction], GPIO.LOW)
            self.state["busy"] = False

        return "Desk stopped after moving {}".format(direction)

    def trigger_micro(self, direction):
        with self.lock:
            if self.state["busy"]:
                return "Desk is already busy moving!"
            self.state["busy"] = True
            self.exit_flag = False

        GPIO.output(GPIOs[direction], GPIO.HIGH)
        try:
            while not self.exit_flag:
                sleep(0.1)
        finally:
            GPIO.output(GPIOs[direction], GPIO.LOW)
            with self.lock:
                self.state["busy"] = False

        return "Desk micro-hold stopped {}".format(direction)

    def stop(self):
        self.exit_flag = True
        GPIO.output(GPIOs["UP"], GPIO.LOW)
        GPIO.output(GPIOs["DOWN"], GPIO.LOW)
        return "Desk has been stopped!"

    def set_position(self, position):
        self.state[position] = self.read_height()
        return "Desk {} position set to {}".format(position, self.state[position])

    def read_position(self, position):
        return str(self.state[position])

    def adjust_height(self, direction, delta):
        self.state["cur"] = self.read_height()
        self.state["up"] = self.state["cur"] + delta if direction == "UP" else self.state["up"]
        self.state["down"] = self.state["cur"] - delta if direction == "DOWN" else self.state["down"]
        return self.trigger_relay(direction)

controller = DeskController()
app = Flask(__name__)

# --- Routes ---
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
@app.route("/")
def index():
    controller.state["cur"] = controller.read_height()
    return render_template('index.html', val=str(controller.state["cur"]))

@app.route("/read/height")
def get_height_api():
    height = controller.read_height()
    controller.state["cur"] = height # Update state if needed
    return jsonify({"height": height})

@app.route("/stop", methods=["POST"])
def stop():
    return controller.stop()

@app.route("/<direction>", methods=["POST"])
def move(direction):
    direction = direction.upper()
    if direction in ("UP", "DOWN"):
        thread = threading.Thread(target=controller.trigger_relay, args=(direction,))
        thread.start()
        return "Desk is going {}".format(direction)
    return "Invalid direction"

@app.route("/<direction>/micro", methods=["POST"])
def micro_move(direction):
    direction = direction.upper()
    if direction in ("UP", "DOWN"):
        thread = threading.Thread(target=controller.trigger_micro, args=(direction,))
        thread.start()
        return "Desk is holding micro-move {}".format(direction)
    return "Invalid direction"

@app.route("/set/<position>", methods=["POST"])
def set_position(position):
    position = position.upper()
    if position in ("UP", "DOWN"):
        return controller.set_position(position.lower())
    return "Invalid position"

@app.route("/read/<position>", methods=["GET"])
def read_position(position):
    position = position.upper()
    if position in ("UP", "DOWN"):
        return controller.read_position(position.lower())
    return "Invalid position"

@app.route("/<direction>/<float:delta>", methods=["POST"])
def adjust_height(direction, delta):
    direction = direction.upper()
    if direction in ("UP", "DOWN"):
        thread = threading.Thread(target=controller.adjust_height, args=(direction, delta))
        thread.start()
        return "Desk is adjusting height {} by {} cm".format(direction, delta)
    return "Invalid direction"

# --- Cleanup ---
@atexit.register
def cleanup():
    controller._shutdown_tof()
    GPIO.cleanup()

# --- Main ---
if __name__ == "__main__":
    controller.state["cur"] = controller.read_height()
    app.run(debug=False, host='0.0.0.0', port=80)

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import datetime
import json
import board
import neopixel
import threading
import subprocess
import logging
import tracemalloc
import threading
import copy

from AnimationEngine import AnimationEngine

#datefmt="%m/%d/%y %I:%M:%S %p"
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(filename)s.%(funcName)s.%(lineno)d: %(message)s')

logging.basicConfig(filename='server.log',
                    level=logging.INFO,
                    encoding='utf-8')
logging.getLogger().handlers[0].setFormatter(formatter)

host = "0.0.0.0"
port = 8081

ledCount = 450
leds = neopixel.NeoPixel(board.D18, ledCount, auto_write=False)
leds.fill((0, 0, 0))
leds.show()

animation_thread = None

daily_restart = True
now = datetime.datetime.now()
#4am tomorrow
restart_time = datetime.datetime(now.year,now.month,now.day,4,0,0) + datetime.timedelta(1)
restart_delay = restart_time-now
print("Time in seconds till reboot: ", end="")
print(restart_delay.total_seconds())

system_status_logging_toggle = False
system_status_delay_between_logging = 3600
tracemalloc.start()

class LEDServer(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server) -> None:
        super().__init__(request, client_address, server)

    def do_GET(self):
        logging.info("GET " + self.path + " from: " + self.client_address[0] + " : " + str(self.client_address[1]))
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("""{"ledCount":"450", "ledAddressible":"true", "ledAnimations":"true"}""", "utf-8"))

    def do_POST(self):
        logging.info("POST " + self.path + " from: " + self.client_address[0] + " : " + str(self.client_address[1]))
        if(self.path == '/led'):
            contentLength = int(self.headers.get('Content-Length'))
            body = json.loads(self.rfile.read(contentLength))
            logging.info(body)
            thread = threading.Thread(group=None, target=self.basic_led_update, args=([body]))
            thread.start()
            self.send_response(200)

        elif(self.path == '/led/animation'):
            contentLength = int(self.headers.get('Content-Length'))
            body = json.loads(self.rfile.read(contentLength))
            logging.info(body)
            global animation_thread
            if(body["namedAnimation"] is not None):
                logging.info("Starting animation: " + body["namedAnimation"])
                if animation_thread is not None:
                    animation_thread.stopAnimation()
                    animation_thread.join()
                    animation_thread = None
                animation_thread = AnimationEngine(leds, ledCount, animation_name=body["namedAnimation"], command=body["command"])
                animation_thread.start()

        elif(self.path == '/led/off'):
            logging.info("Shutting off LEDs")
            if(animation_thread is not None):
                animation_thread.stopAnimation()
                animation_thread.join()
                animation_thread = None

        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes("""{"ledCount":"450", "ledAddressible":"true", "ledAnimations":"true"}""", "utf-8"))

    def basic_led_update(self, body):
        logging.info(body)
        global animation_thread
        if(animation_thread is not None):
            animation_thread.stopAnimation()
            animation_thread.join()
        self.update_leds(body)

    def update_leds(self, command):
        print(command)
        for status in command["status"]:
            for i in range(status["ledStart"], status["ledEnd"]):
                leds[i] = (status["r"],status["g"],status["b"])
        leds.show()
        print(command)

def restart_pi():
    time.sleep(restart_delay.total_seconds())
    subprocess.Popen("sudo reboot", shell=True)

def system_status_logging():
    while True:
        logging.info("start system status log")
        logging.info("Memory being used: ")
        logging.info(tracemalloc.get_traced_memory())
        logging.info("End system status log")
        time.sleep(system_status_delay_between_logging)

if __name__ == "__main__":
    webServer = HTTPServer((host, port), LEDServer)
    print("Server started at: " + host + ":", end="")
    print(port)

    if daily_restart:
        restart_thread = threading.Thread(target=restart_pi)
        restart_thread.start()

    if system_status_logging_toggle:
        system_status_logging_thread = threading.Thread(target=system_status_logging)
        system_status_logging_thread.start()

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("server stopped")
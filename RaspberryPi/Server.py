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

from AnimationEngine import AnimationEngine

logging.basicConfig(filename='server.log', encoding='utf-8', level=logging.INFO)

host = "0.0.0.0"
port = 8081

ledCount = 450
leds = neopixel.NeoPixel(board.D18, ledCount, auto_write=False)
leds.fill((0, 0, 0))
leds.show()

animationThread = None

daily_restart = True
now = datetime.datetime.now()
#4am tomorrow
restart_time = datetime.datetime(now.year,now.month,now.day,4,0,0) + datetime.timedelta(1)
restart_delay = restart_time-now
print("Time in seconds till reboot: ", end="")
print(restart_delay.total_seconds())

system_status_logging = True
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
            self.update_leds(body)
        elif(self.path == '/led/animation'):
            contentLength = int(self.headers.get('Content-Length'))
            body = json.loads(self.rfile.read(contentLength))
            logging.info(body)
            global animationThread
            if(body['stopAnimation'] == 'true' or body['stopAnimation'] == True):
                logging.info("Stopping animation")
                if(animationThread is not None):
                    animationThread.stopAnimation()
                    # animation will fade out
                    # animationThread.join()
            elif(body["namedAnimation"] is not None):
                logging.info("Starting animation: " + body["namedAnimation"])
                if animationThread is not None:
                    animationThread.stopAnimation()
                    animationThread.join()
                animationThread = AnimationEngine()
                animationThread.setAnimation(body["namedAnimation"], leds, ledCount)
                animationThread.start()
        elif(self.path == '/led/off'):
            logging.info("Shutting off LEDs")
            if(animationThread is not None):
                animationThread.hardStopAnimation()
                animationThread.join()
            for i in range(0, ledCount):
                leds[i] = (0,0,0)
            leds.show()

        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes("""{"ledCount":"450", "ledAddressible":"true", "ledAnimations":"true"}""", "utf-8"))

    def update_leds(self, command):
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

    if system_status_logging:
        system_status_logging_thread = threading.Thread(target=system_status_logging)
        system_status_logging_thread.start();

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("server stopped")

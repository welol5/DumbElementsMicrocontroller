from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import datetime
import json
import board
import neopixel
import threading
import subprocess

from AnimationEngine import AnimationEngine

host = "0.0.0.0"
port = 8081

ledCount = 450
leds = neopixel.NeoPixel(board.D18, ledCount, auto_write=False)
leds.fill((0, 0, 0))
leds.show()

animationThread = None

daily_restart = True
now = datetime.now()
#4am tomorrow
restart_time = datetime.date(now.year,now.month,now.day+1,4,0,0)
restart_delay = restart_time-datetime.now()
if daily_restart:
    threading.Thread(target=restart_pi)

def restart_pi():
    time.sleep(restart_delay.total_seconds)
    subprocess.Popen("sudo reboot", shell=True)


class LEDServer(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server) -> None:
        super().__init__(request, client_address, server)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("""{"ledCount":"450", "ledAddressible":"true", "ledAnimations":"true"}""", "utf-8"))

    def do_POST(self):
        if(self.path == '/led'):
            contentLength = int(self.headers.get('Content-Length'))
            body = json.loads(self.rfile.read(contentLength))
            print(body)
            self.update_leds(body)
        elif(self.path == '/led/animation'):
            contentLength = int(self.headers.get('Content-Length'))
            body = json.loads(self.rfile.read(contentLength))
            print(body)
            global animationThread
            if(body['stopAnimation'] == 'true'):
                if(animationThread is not None):
                    animationThread.stopAnimation()
                    animationThread.join()
            elif(body["namedAnimation"] is not None):
                if animationThread is not None:
                    animationThread.stopAnimation()
                    animationThread.join()
                animationThread = AnimationEngine()
                animationThread.setAnimation(body["namedAnimation"], leds, ledCount)
                animationThread.start()
        elif(self.path == '/led/off'):
            if(animationThread is not None):
                animationThread.stopAnimation()
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

if __name__ == "__main__":
    webServer = HTTPServer((host, port), LEDServer)
    print("Server started at: " + host + ":", end="")
    print(port)

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("server stopped")

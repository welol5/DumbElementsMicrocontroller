from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
import board
import neopixel
import threading

from AnimationEngine import AnimationEngine

host = "0.0.0.0"
port = 8081

ledCount = 450
leds = neopixel.NeoPixel(board.D18, ledCount, auto_write=False)
leds.fill((0, 0, 0))
leds.show()

animationThread = None


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



# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# # Simple test for NeoPixels on Raspberry Pi
# import time
# import board
# import neopixel


# # Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# # NeoPixels must be connected to D10, D12, D18 or D21 to work.
# pixel_pin = board.D18

# # The number of NeoPixels
# num_pixels = 2

# # The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# # For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
# ORDER = neopixel.GRB

# pixels = neopixel.NeoPixel(
#     pixel_pin, num_pixels, brightness=1, auto_write=False, pixel_order=ORDER
# )

# def wheel(pos):
#     # Input a value 0 to 255 to get a color value.
#     # The colours are a transition r - g - b - back to r.
#     if pos < 0 or pos > 255:
#         r = g = b = 0
#     elif pos < 85:
#         r = int(pos * 3)
#         g = int(255 - pos * 3)
#         b = 0
#     elif pos < 170:
#         pos -= 85
#         r = int(255 - pos * 3)
#         g = 0
#         b = int(pos * 3)
#     else:
#         pos -= 170
#         r = 0
#         g = int(pos * 3)
#         b = int(255 - pos * 3)
#     return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


# def rainbow_cycle(wait):
#     for j in range(255):
#         for i in range(num_pixels):
#             pixel_index = (i * 256 // num_pixels) + j
#             pixels[i] = wheel(pixel_index & 255)
#         pixels.show()
#         time.sleep(wait)


# while True:
#     # Comment this line out if you have RGBW/GRBW NeoPixels
#     pixels.fill((255, 0, 0))
#     # Uncomment this line if you have RGBW/GRBW NeoPixels
#     # pixels.fill((255, 0, 0, 0))
#     pixels.show()
#     time.sleep(1)

#     # Comment this line out if you have RGBW/GRBW NeoPixels
#     pixels.fill((0, 255, 0))
#     # Uncomment this line if you have RGBW/GRBW NeoPixels
#     # pixels.fill((0, 255, 0, 0))
#     pixels.show()
#     time.sleep(1)

#     # Comment this line out if you have RGBW/GRBW NeoPixels
#     pixels.fill((0, 0, 255))
#     # Uncomment this line if you have RGBW/GRBW NeoPixels
#     # pixels.fill((0, 0, 255, 0))
#     pixels.show()
#     time.sleep(1)

#     rainbow_cycle(0.1)  # rainbow cycle with 1ms delay per step

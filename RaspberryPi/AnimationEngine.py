import colorsys
import random
import threading
import time

class AnimationEngine(threading.Thread):

    stop = 0
    animation = None
    leds = None
    ledCount = None

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        if (self.animation != None):
            self.animation(self.leds, self.ledCount)

    def stopAnimation(self):
        self.stop = 1

    def setAnimation(self, name, leds, ledCount):
        if(name == "stars"):
            self.animation = self.stars
            self.leds = leds
            self.ledCount = ledCount

    def stars(self, leds, ledCount):
        chance = 0.005
        colors = [(0,0,0)]*ledCount
        leds_on = [0]*ledCount

        self.stop = 0
        while self.stop == 0:
            time.sleep(0.2)
            #set colors
            for i in range(ledCount):
                leds[i] = colors[i]
                
                #add new stars
                if leds_on[i] == 0:
                    if random.random() < chance:
                        leds_on[i] = 1
                        colors[i] = (random.random()*256,random.random()*128,random.random()*256)

                #fade old stars
                else:
                    hls = colorsys.rgb_to_hls(colors[i][0],colors[i][1],colors[i][2])
                    new_hls = (hls[0], hls[1]-1, hls[2])
                    if new_hls[1] <= 0:
                        colors[i] = (0,0,0)
                        leds_on[i] = 0
                    else:
                        colors[i] = colorsys.hls_to_rgb(new_hls[0],new_hls[1],new_hls[2])
            leds.show()
                
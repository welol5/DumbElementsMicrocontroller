import colorsys
import random
import copy

from .animation import Animation

class StarsAnimation(Animation):

    chance = None
    led_count = None
    colors = None
    leds_on = None

    def __init__(self, led_count, chance=0.005):
        self.led_count = led_count
        self.colors = [(0,0,0)]*led_count
        self.leds_on = [0]*led_count
        self.chance = chance

    def get_next_animation_frame(self) -> list[tuple]:
            
        for i in range(self.led_count): 
            #add new stars
            if self.leds_on[i] == 0:
                if random.random() < self.chance:
                    self.leds_on[i] = 1
                    self.colors[i] = (random.random()*256,random.random()*128,random.random()*256)

            #fade old stars
            else:
                hls = colorsys.rgb_to_hls(self.colors[i][0],self.colors[i][1],self.colors[i][2])
                new_hls = (hls[0], hls[1]-1, hls[2])
                if new_hls[1] <= 0:
                    self.colors[i] = (0,0,0)
                    self.leds_on[i] = 0
                else:
                    self.colors[i] = colorsys.hls_to_rgb(new_hls[0],new_hls[1],new_hls[2])
        return copy.deepcopy(self.colors)
    
    def get_current_state(self) -> list[tuple]:
        return copy.deepcopy(self.colors)
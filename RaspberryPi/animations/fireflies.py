import colorsys
import random
import copy

from .animation import Animation

class FirefliesAnimation(Animation):

    chance = None
    led_count = None
    colors = None
    target_colors = None
    leds_on = None

    def __init__(self, led_count, chance=0.0025):
        self.led_count = led_count
        self.colors = [(0,0,0)]*led_count
        self.target_colors = [(0,0,0)]*led_count
        self.leds_fade_on = [0]*led_count
        self.leds_fade_off = [0]*led_count
        self.chance = chance

    def get_next_animation_frame(self) -> list[tuple]:
            
        for i in range(self.led_count): 
            #add new stars
            if self.leds_fade_on[i] == 0 & self.leds_fade_off[i] == 0:
                if random.random() < self.chance:
                    self.leds_fade_on[i] = 1
                    self.target_colors[i] = colorsys.hsv_to_rgb((random.random()*45),1,1)
                    self.target_colors[i] = (self.target_colors[i][0] * 255,self.target_colors[i][1] * 255,self.target_colors[i][2] * 255)

            #fade on new fireflies
            elif self.leds_fade_on[i] > 0:
                self.colors[i] = self.calc_fade_state(self.leds_fade_on[i]/255.0, self.target_colors[i])
                self.leds_fade_on[i] = self.leds_fade_on[i] +1
                if(self.leds_fade_on[i] == 255):
                    self.leds_fade_on[i] = 0
                    self.leds_fade_off[i] = 1

            #fade off old fireflies
            elif self.leds_fade_off[i] == 1:
                hls = colorsys.rgb_to_hls(self.colors[i][0],self.colors[i][1],self.colors[i][2])
                new_hls = (hls[0], hls[1]-1, hls[2])
                if new_hls[1] <= 0:
                    self.colors[i] = (0,0,0)
                    self.leds_fade_off[i] = 0
                else:
                    self.colors[i] = colorsys.hls_to_rgb(new_hls[0],new_hls[1],new_hls[2])
        return copy.deepcopy(self.colors)
    
    def get_current_state(self) -> list[tuple]:
        return copy.deepcopy(self.colors)
    
    #state is a % of target
    def calc_fade_state(self, state, target):
        r = int(target[0]*state)
        g = int(target[1]*state)
        b = int(target[2]*state)
        return (r,g,b)
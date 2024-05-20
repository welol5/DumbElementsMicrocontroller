import colorsys
import random
import copy
import time

from .animation import Animation

class StaticAnimation(Animation):

    chance = None
    led_count = None
    colors = None
    leds_on = None

    def __init__(self, led_count, command):
        self.led_count = led_count
        self.colors = [(0,0,0)]*led_count
        self.leds_on = [0]*led_count
        
        for status in command:
            for i in range(status["ledStart"], status["ledEnd"]):
                self.colors[i] = (status["r"],status["g"],status["b"])

    def get_next_animation_frame(self) -> list[tuple]:
        return copy.deepcopy(self.colors)
    
    def get_current_state(self) -> list[tuple]:
        return copy.deepcopy(self.colors)
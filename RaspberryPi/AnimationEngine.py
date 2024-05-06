import threading
import logging
import time

from animations.animation import Animation
from animations.stars import StarsAnimation

from filters.filter import Filter
from filters.fade import FadeFilter

logging.basicConfig(filename='server.log', encoding='utf-8', level=logging.INFO)

class AnimationEngine(threading.Thread):

    stop = False

    leds = None
    led_count = None
    animation_delay = None

    animation: Animation = None

    standard_fade_rate = 0.0001

    def __init__(self, leds, led_count, animation_name, animation_delay=0.4):
        threading.Thread.__init__(self)
        self.leds = leds
        self.led_count = led_count
        self.animation_delay = animation_delay
        self.setup_animation(animation_name)

    def run(self):
        while(not self.stop):
            self.update_leds()
            time.sleep(self.animation_delay)

        colors = self.animation.get_current_state()
        fade = FadeFilter(fade_rate=self.standard_fade_rate)

        for i in range (0,int(1.0/self.standard_fade_rate),1):
            current_colors = fade.apply_filter(colors)
            #update led colors
            for k in range(self.led_count):
                self.leds[k] = current_colors[k]
            self.leds.show()

    def stopAnimation(self):
        self.stop = True

    def setup_animation(self, animation_name):
        if(animation_name == "stars"):
            self.animation = StarsAnimation(self.led_count)

    def update_leds(self):
        #get base colors
        colors = self.animation.get_next_animation_frame()

        #apply filters

        #update led colors
        for i in range(self.led_count):
            self.leds[i] = colors[i]
        self.leds.show()
import threading
import logging
import time
import copy

from animations.animation import Animation
from animations.stars import StarsAnimation
from animations.static import StaticAnimation
from animations.fireflies import FirefliesAnimation

from filters.filter import Filter
from filters.fade import FadeFilter

logging.basicConfig(filename='server.log', encoding='utf-8', level=logging.INFO)

class AnimationEngine(threading.Thread):

    stop = False

    leds = None
    led_count = None
    animation_delay = None

    animation: Animation = None
    is_static = False

    #fade over 1 min
    standard_fade_rate = 1.0/60.0

    #basic animations only need to know the led count
    basic_animations = {"stars": StarsAnimation,
                     "fireflies": FirefliesAnimation}

    def __init__(self, leds, led_count, animation_name, animation_delay=0.4, command = None):
        threading.Thread.__init__(self)
        self.leds = leds
        self.led_count = led_count
        self.animation_delay = animation_delay
        self.setup_animation(animation_name, command)

    def run(self):

        if(self.is_static):
            self.update_leds()
        else:
            while(not self.stop):
                self.update_leds()
                time.sleep(self.animation_delay)

            colors = self.animation.get_current_state()
            fade = FadeFilter(fade_rate=self.standard_fade_rate)

            for i in range (0,int(1.0/self.standard_fade_rate),1):
                faded_colors = fade.apply_filter(copy.deepcopy(colors))
                #update led colors
                for k in range(self.led_count):
                    self.leds[k] = faded_colors[k]
                self.leds.show()

    def stopAnimation(self):
        self.stop = True

        if(self.is_static):
            colors = self.animation.get_current_state()
            fade = FadeFilter(fade_rate=self.standard_fade_rate)
            for i in range (0,int(1.0/self.standard_fade_rate),1):
                faded_colors = fade.apply_filter(copy.deepcopy(colors))
                #update led colors
                for k in range(self.led_count):
                    self.leds[k] = faded_colors[k]
                self.leds.show()

    def setup_animation(self, animation_name, command = None):
        if(animation_name == "static"):
            self.animation = StaticAnimation(self.led_count, command)
            self.is_static = True
        else:
            self.animation = self.basic_animations[animation_name](self.led_count)
            self.is_static = False

    def update_leds(self):
        #get base colors
        colors = self.animation.get_next_animation_frame()

        #apply filters

        #update led colors
        for i in range(self.led_count):
            self.leds[i] = colors[i]
        self.leds.show()
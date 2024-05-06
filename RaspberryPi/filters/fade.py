import colorsys
import numpy
from .filter import Filter

class FadeFilter(Filter):

    fade_percent = 0.0
    fade_rate = None

    def __init__(self, fade_rate=0.001):
        self.fade_rate=fade_rate

    def apply_filter(self, colors:list[tuple]) -> list[tuple]:
            
        self.fade_percent += self.fade_rate
        if(self.fade_percent > 1):
            self.fade_percent = 1

        for i in range(len(colors)): 
            hls = colorsys.rgb_to_hls(colors[i][0],colors[i][1],colors[i][2])

            fade_amount = numpy.interp(self.fade_percent, [0,1], [0,255])
            new_hls = (hls[0], hls[1]-fade_amount, hls[2])
            if new_hls[1] <= 0:
                colors[i] = (0,0,0)
            else:
                colors[i] = colorsys.hls_to_rgb(new_hls[0],new_hls[1],new_hls[2])

        return colors
#!/usr/bin/env python3

import math
import random
from PIL import Image

def create_image(size, func, prefunc=None, freq=1, phase=0):
    dest = Image.new("L", size)
    data = []
    for y in range(size[1]):
        for x in range(size[0]):
            x1 = (x - (size[0]/2)) / (size[0]/2)
            y1 = (y - (size[1]/2)) / (size[1]/2)
            if prefunc:
                x1,y1 = prefunc(x1,y1)
            data.append(
                ((func(
                    x1,
                    y1,
                    freq,
                    phase)
                 * 255)+255)/2)
    dest.putdata(data)
    return dest


def rotate(x,y,angle):
    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)
    return ((x * cos_theta) - (y * sin_theta),
            (x1 * sin_theta) - (y1 * cos_theta))
    
    
def shear_m(m, axis):
    if axis == "x":
        def shear(x,y):
            return (x + (y*m), y)
    elif axis == "y":
        def shear(x,y):
            return (x, y + (x*m))
    return shear

def make_phased_function(f, arg=0, r=math.pi):
     def _f(x, y, freq, phase):
        return f(
            (r/2)*(((freq * ([x,y][arg]+1) % 2) + ((phase*2))) % 2)-1)
     _f.__name__ = f.__name__ + "(" + "xy"[arg] + ")"
     _f.axis = "xy"[arg]
     return _f


def triangle(v):
    return (2 * abs(v - math.floor(v + (1/2)))) - 1

def sawtooth(v):
    return 2*(v - math.floor(v + (1/2)))

def square(v):
    return -1 if v < 0 else 1


functions = {f.__name__: f for f in [
    make_phased_function(mathfunc, xy, funcrange)
    for xy in [0,1]
    for mathfunc, funcrange in [(math.sin, 2*math.pi),
                                (math.cos, 2*math.pi),
                                (triangle, 1),
                                (sawtooth, 1)]
                                #(square, 2)]
    ]
}


def random_greyscale_image(size):
    func = functions[random.choice(list(functions.keys()))]
    axis = func.axis
    freq = random.randrange(1,round(min(size)/8))
    prefunc = shear_m(random.randrange(0,freq+1) * random.choice([-1,1]), axis)
    phase = random.random()
    im = create_image(size, func, prefunc, freq, phase)
    return im
    
def random_image(size):
    r = random_greyscale_image(size)
    g = random_greyscale_image(size)
    b = random_greyscale_image(size)
    return Image.merge("RGB", (r,g,b))
    
if __name__ == "__main__":
    import sys
    size = (int(sys.argv[1]), int(sys.argv[2]))
    im = random_image(size)
    im.save(sys.argv[3])



      

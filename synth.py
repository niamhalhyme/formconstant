#!/usr/bin/env python3

import math
import random
from PIL import Image
from collections import namedtuple

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

def generate_greyscale_image(size, func, axis, freq, prefunc, phase):
    return create_image(size, func, prefunc, freq, phase)
 
GreyscaleArgs = namedtuple("GreyscaleArgs", ["size", "func", "axis", "freq", "prefunc", "phase"])
    
def random_greyscale_args(size):
    func = functions[random.choice(list(functions.keys()))]
    axis = func.axis
    freq = random.randrange(1,min([64,round(min(size)/8)]))
    prefunc = shear_m(random.randrange(0,freq+1) * random.choice([-1,1]), axis)
    phase = random.random()
    return GreyscaleArgs(size, func, axis, freq, prefunc, phase)

def random_greyscale_image(size):    
    return generate_greyscale_image(*random_greyscale_args(size))
    
def random_image(size, mode="RGB"):
    r = random_greyscale_image(size)
    g = random_greyscale_image(size)
    b = random_greyscale_image(size)
    return Image.merge(mode, (r,g,b))
    
def random_sequence(size, number, mode="RGB"):
    channel_args = [random_greyscale_args(size) for _ in range(3)]
    b_args = random_greyscale_args(size)
    phase_dir = [random.choice([-1,1]) for _ in range(len(channel_args))]
    info = [mode]
    info.extend(["c %d: %s" % (i, "/".join([str(arg) if not hasattr(arg, "__name__") else str(arg.__name__)
                                            for arg in channel_args[i] + (phase_dir[i],)]))
            for i in range(len(channel_args))])
    for i in range(number):
        phase_add = (i / number)
        channels = [generate_greyscale_image(*channel_args[i][:-1] +
                                             ((channel_args[i][-1] +
                                             (phase_add*phase_dir[i]))%1,))
                    for i in range(len(channel_args))]
        merged = Image.merge(mode, channels)
        merged.info["comment"] = "\n".join(info).encode()
        yield merged


if __name__ == "__main__":
    import sys
    size = (int(sys.argv[1]), int(sys.argv[2]))
    im = random_image(size)
    im.save(sys.argv[3])



      

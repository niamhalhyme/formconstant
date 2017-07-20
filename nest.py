#!/usr/bin/env python3

import random
import math
import cortex
import sys
from PIL import Image
from collections import namedtuple

class Variable:
    def __init__(self, phase_direction, phase_offset, frequency):
        self.phase_direction = phase_direction
        self.phase_offset = phase_offset
        self.frequency = frequency
        self.name = self.__class__.__name__.lower()
        self.varidx = self.__class__.varidx
        
    @classmethod
    def random(cls):
        return cls(random.choice([-1, 0, 1]),
                   random.random(),
                   math.ceil(random.expovariate(1)))
                   
    def __call__(self, variables, phase):
        return (((((variables[self.varidx] + 1) + 
               ((self.phase_direction + self.phase_offset) * 2)) *
               self.frequency) % 2) - 1)

    def __str__(self):
        return "{0}(phase={1:.3f}{2}, freq={3:d})".format(
            self.name,
            self.phase_offset,
            "=><"[self.phase_direction],
            self.frequency
        )
        

class X(Variable):
    varidx = 0
    

class Y(Variable):
    varidx = 1
    

class Function:
    arity = 1
    fmt = ""
    func = None
    def __init__(self, args, dimensions, phase_direction, phase_offset,
                 frequency):
        self.args = args
        self.dimensions = dimensions
        self.phase_direction = phase_direction
        self.phase_offset = phase_offset 
        self.frequency = frequency
        self.fmt = self.__class__.fmt
        self.func = self.__class__.func
       
    @classmethod 
    def random(cls, probability, level, builder):
        return cls([builder.build(probability*probability, level)
                    for _ in range(cls.arity)],
                   builder.dimensions,
                   cls.random_phase_direction(level),
                   random.random(),
                   math.ceil(random.expovariate(1)))
                   
    @classmethod
    def random_phase_direction(cls, level):
        return 0
                   
    def __str__(self):
        funcname = self.func.__name__ if self.func is not None else ""
        return self.fmt.format(*self.args,
                               name=funcname,
                               phase_offset=self.phase_offset,
                               phased="=><"[self.phase_direction],
                               freq=self.frequency)


class TrigfuncPi(Function):
    fmt = "{name}((pi * {0} * {freq:d}) + phase({phase_offset:.3f}{phased}))"

    @classmethod
    def random_phase_direction(cls, level):
        if level == 1:
            return random.choice([-1,1])
        else:
            return 0

    def __call__(self, variables, phase):
        phase_term = (self.phase_direction *
                      ((2 * math.pi * (phase + self.phase_offset)) %
                       (2 * math.pi)))
        return self.func((math.pi *
                         self.args[0](variables, phase) *
                         self.frequency) +       
                         self.phase_direction * phase_term)
    

class SinPi(TrigfuncPi):
    func = math.sin
    
    
class CosPi(TrigfuncPi):
    func = math.cos
            

class Times(Function):
    fmt = "{0} * {1}"
    arity = 2
    
    @classmethod 
    def random(cls, probability, level, builder):
        return super().random(probability, level-1, builder)
        
    def __call__(self, variables, phase):
        return self.args[0](variables, phase) * self.args[1](variables, phase)
        
        
class Builder:
    def __init__(self, functions, variables):
        self.functions = functions
        self.variables = variables
        self.dimensions = len(variables)
        
    def build(self, probability=0.99, level=0):
        if random.random() < probability:
            return random.choice(self.functions).random(probability,
                                                        level+1,
                                                        self)
        else:
            return random.choice(self.variables).random()
            
            
phase_adjustments = [
    lambda p: p,
    lambda p: (1 / (1 + (math.e**(-1*(p-0.5)))) + 6)/12,
    lambda p: (math.cos(math.pi + (p * math.pi)) + 1) / 2,
    lambda p: math.sin(p * (math.pi/2)),
    lambda p: (math.cos(math.pi + (2 * math.pi * p)) + 1) / 2
]

functions = [SinPi, CosPi, Times]

def create_image(size, expression, phase=0):
    """
    Return an image of the given size plotting intensity of the given
    nested function of frequency and phase, with x and y mapped by prefunc.
    """
    data = []
    for y in range(size[1]):
        for x in range(size[0]):
            x1,y1 = ((x - (size[0]/2)) / (size[0]/2),
                     (y - (size[1]/2)) / (size[1]/2))
            data.append(
                int(expression([x1,y1], phase) * 127.5) + 127.5)
    dest = Image.new("L", size)
    dest.putdata(data)
    return dest

def generate_greyscale_image(size, expression, phase, phase_adjust):
    """
    Return an image of the given size plotting the given function called with
    the given arguments.
    """
    return create_image(size, expression, phase_adjust(phase))
 
GreyscaleArgs = namedtuple("GreyscaleArgs",
                           ["size", "expression", "phase"])
    
def random_greyscale_args(size):
    """
    Return a GreyscaleArgs tuple with the given size and randomly chosen
    values.
    """
    expression = Builder(functions, [X,Y]).build(
                                        probability=random.uniform(0.95,0.99))
    
    phase = random.random()
    return GreyscaleArgs(size, expression, phase)

def random_greyscale_image(size):
    """
    Return an greyscale image of the given size plotting a random function
    with random arguments
    """    
    return generate_greyscale_image(*random_greyscale_args(size))
    
modes = {
    "RGB": 3,
    "HSV": 3,
    "YCbCr": 3,
    "CMYK": 4
}    

def random_image(size, mode=None):
    """
    Return an image of the given mode with each channel as a random greyscale
    image. If mode is None, select a random multi-channel mode.
    """
    if mode is None:
        mode = random.choice(list(modes.keys()))
    if mode == "L":
        return random_greyscale_image(size)
    else:
        channels = [random_greyscale_image(size) for _ in range(modes[mode])]
        im = Image.merge(mode, channels)
        if mode != "RGB":
            im = im.convert("RGB")
        return im
    
def random_sequence(size, number, mode=None):
    """
    Yield Image objects of given size and mode in a sequence with length given
    by number. The phase is varied producing a sequence that should loop. The
    wave arguments for each channel are random.
    """
    if mode is None:
        mode = random.choice(list(modes.keys()))
    number_of_channels = modes[mode]   
    channel_args = [random_greyscale_args(size)
                    for _ in range(number_of_channels)]
    phase_adjusts = [random.choice(phase_adjustments)
                     for _ in range(number_of_channels)]
    mapped = random.choice([True, False])
    yield from create_sequence(size, number, mode, channel_args, phase_adjusts,
                               mapped)
                    
def create_sequence(size, number, mode, channel_args, phase_adjusts, mapped):
    """
    Yield Image objects of given size and mode in a sequence with length given
    by number. The phase is varied producing a sequence that should loop. The
    wave arguments for each channel are provided by channel_args.
    """
    number_of_channels = len(channel_args)
    phase_dir = [random.choice([-1,1]) for _ in range(len(channel_args))]
    info = [mode]
    info.extend(["c %d: %s" %
        (i, 
        "/".join(
            [str(arg) if not hasattr(arg, "__name__")
                      else str(arg.__name__)
             for arg in channel_args[i] + (phase_dir[i],)]))
         for i in range(len(channel_args))])
    for i in range(number):
        phase = (1/number)*i
        channels = [generate_greyscale_image(
                    *channel_args[i][:-1] +
                     (channel_args[i][-1] + (phase*phase_dir[i]) % 1,
                      phase_adjusts[i]))    
                    for i in range(number_of_channels)]
        merged = Image.merge(mode, channels).convert("RGB")
        if mapped:
            merged = cortex.derive_image(merged)
        merged.info["comment"] = "\n".join(info).encode()
        yield merged

def save_random_sequence(size, number, duration, path, mode=None):
    if mode is None:
        mode = random.choice(["RGB", "HSV", "YCbCr", "CMYK"])
    frame_duration = duration // number
    seq = [frame for frame in random_sequence(size, number, mode)]
    print(len(seq))
    im = seq.pop(0)
    im.save(path, save_all=True, duration=frame_duration, loop=0,
            append_images=seq, comment=im.info["comment"][:255])

if __name__ == "__main__":
    size = [int(sys.argv[1]), int(sys.argv[2])]
    number = int(sys.argv[3])
    duration = int(sys.argv[4])
    path = sys.argv[5]
    save_random_sequence(size, number, duration, path)
    

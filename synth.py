#!/usr/bin/env python3

import math
import random
import argparse
import os.path
from PIL import Image
from collections import namedtuple

def create_image(size, func, prefunc=None, freq=1, phase=0):
    """
    Return an image of the given size plotting intensity of the given
    function of frequency and phase, with x and y mapped by prefunc.
    """
    data = []
    if prefunc is None:
        prefunc = lambda x,y: (x,y)
    for y in range(size[1]):
        for x in range(size[0]):
            x1,y1 = prefunc((x - (size[0]/2)) / (size[0]/2),
                           (y - (size[1]/2)) / (size[1]/2))
            data.append((func(x1, y1, freq, phase) * 127.5) + 127.5)
    dest = Image.new("L", size)
    dest.putdata(data)
    return dest

def shear_m(m, axis):
    """
    Return a function returning an (x,y) tuple sheared by factor m
    """
    if axis == "x":
        def shear(x,y):
            return (x + (y*m), y)
    elif axis == "y":
        def shear(x,y):
            return (x, y + (x*m))
    return shear
    

def make_phased_function(f, arg=0, r=math.pi):
    """
    Return a function composition to take x, y, freq and phase arguments
    """
    def _f(x, y, freq, phase):
        return f((r/2) * (((freq*([x,y,(x*y)**2][arg]+1)%2)+((phase*2)))%2)-1)
    _f.__name__ = f.__name__ + "(" + ["x", "y", "x*y"][arg] + ")"
    _f.axis = ["x", "y", "x*y"][arg]
    return _f


def triangle(v):
    """
    Return a value corresponding to a triangle wave
    """
    return (2 * abs(v - math.floor(v + (1/2)))) - 1

def sawtooth(v):
    """
    Return a value corresponding to a sawtooth wave
    """
    return 2*(v - math.floor(v + (1/2)))
    

# create a dictionary of phased functions for both x and y axes
functions = {f.__name__: f for f in [
    make_phased_function(mathfunc, xy, funcrange)
    for xy in [0,1]
    for mathfunc, funcrange in [(math.sin, 2*math.pi),
                                (math.cos, 2*math.pi),
                                (triangle, 1),
                                (sawtooth, 1)]]}


def generate_greyscale_image(size, func, freq, prefunc, phase, phase_adjust):
    """
    Return an image of the given size plotting the given function called with
    the given arguments.
    """
    return create_image(size, func, prefunc, freq, phase_adjust(phase))
 
GreyscaleArgs = namedtuple("GreyscaleArgs",
                           ["size", "func", "freq", "prefunc", "phase"])
    
def random_greyscale_args(size):
    """
    Return a GreyscaleArgs tuple with the given size and randomly chosen
    values.
    """
    func = functions[random.choice(list(functions.keys()))]
    axis = func.axis
    freq = random.randrange(1,min([64,round(min(size)/8)]))
    prefunc = (shear_m(random.randrange(0,freq+1) *
               random.choice([-1,1]), axis))
    phase = random.random()
    return GreyscaleArgs(size, func, freq, prefunc, phase)

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

phase_adjustments = [
    lambda p: p,
]

def create_image_from_spec(size, mode, channel_args):
    channels = [generate_greyscale_image(*channel_arg)
                for channel_arg in channel_args]
    return Image.merge(mode, channels)
    

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
    phase_adjusts = [random.choice(phase_adjustments)
                     for _ in range(number_of_channels)]
    channel_args = [random_greyscale_args(size)
                    for _ in range(number_of_channels)]
    yield from create_sequence(size, number, mode, channel_args, phase_adjusts)
                    
def create_sequence(size, number, mode, channel_args, phase_adjusts=None):
    """
    Yield Image objects of given size and mode in a sequence with length given
    by number. The phase is varied producing a sequence that should loop. The
    wave arguments for each channel are provided by channel_args.
    """
    number_of_channels = len(channel_args)
    if phase_adjusts is None:
        phase_adjusts = [(lambda p: p) for _ in range(number_of_channels)]
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
        phase = (1 / number) * i
        channels = [generate_greyscale_image(
                     *channel_args[i][:-1] +
                     (channel_args[i][-1] + (phase*phase_dir[i]) % 1,
                      phase_adjusts[i]))
                    for i in range(number_of_channels)]
        merged = Image.merge(mode, channels).convert("RGB")
        merged.info["comment"] = "\n".join(info).encode()
        yield merged


def parse_spec(s):
    """
    Parse a command-line specification and return a list of (func, freq,
    shear, phase) tuples.
    """
    return [parse_channel(c) for c in s.split(";")]
   

def parse_channel(s):
    """
    Parse one channel of a command-line specification and return a
    (func, freq, shear, phase) tuple.
    """
    fields = s.split(",")
    if len(fields) != 4:
        raise argparseArgumentTypeError(
            "Unable to parse channel specification: %s" % (s,))
    func = functions.get(fields[0])
    if func is None:
        raise argparse.ArgumentTypeError("Unknown function: %s" % (fields[0],))
    try:
        freq = float(fields[1])
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Unable to parse channel frequency field: %s" % (fields[1],))
    try:
        shear = int(fields[2])
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Unable to parse channel shear field: %s" % (fields[2],))
    try:
        phase = float(fields[3])
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Unable to parse channel phase field: %s" % (fields[3],))
    return (func, freq, shear, phase)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Produce images synthesized from waves")
    parser.add_argument("width", type=int, help="width in pixels")
    parser.add_argument("height", type=int, help="height in pixels")
    parser.add_argument("destination", help="destination path")
    parser.add_argument("-m", "--mode",
        choices=["L", "RGB", "HSV", "YCbCr", "CMYK"],
        help="image mode")
    parser.add_argument("-s", "--spec",
        type=parse_spec,
        help="list of func,freq,shear,phase;[...] arguments per channel ")
    parser.add_argument("-n", "--number",
        type=int,
        help="number of images to produce in a sequence")
    args = parser.parse_args()
    if args.spec:
        if args.mode is None:
            raise argparse.ArgumentTypeError(
                "Must specify mode with spec."
            )
        if args.mode == "L":
            channels = 1
        else:
            channels = modes[args.mode]
        if len(args.spec) != channels:
            raise argparse.ArgumentTypeError(
                "Wrong number of channels in spec for mode %s" % (args.mode,))
        greyscale_args = []
        for spec in args.spec:
            greyscale_args.append(GreyscaleArgs(
                (args.width, args.height),
                spec[0],
                spec[1],
                shear_m(spec[2], spec[0].axis),
                spec[3]))
        if args.number is not None:
            z = len(str(args.number))
            if os.path.splitext(args.destination)[1] == ".gif":
                seq = []
                anim = True
            else:
                anim = False
            for i, image in enumerate(create_sequence(
                                        (args.width, args.height),
                                        args.number,
                                        args.mode,
                                        greyscale_args)):
                if not anim:
                    path, ext = os.path.splitext(args.destination)
                    image.save(path + "_" + str(i).zfill(z) + ext)
                else:
                    seq.append(image)
            if anim:
                im = seq.pop(0)
                im.save(args.destination, save_all=True,
                    duration=1000/24, loop=0, append_images=seq)
        else:
            im = create_image_from_spec(
                (args.width, args.height), args.mode, greyscale_args)
            im.save(args.destination)
    else:
        if args.mode is None:
            mode = random.choice(["RGB", "HSV", "YCbCr", "CMYK"])
        else:
            mode = args.mode
        if args.number is not None:
            if os.path.splitext(args.destination)[1] == ".gif":
                seq = []
                anim = True
            else:
                anim = False
            z = len(str(args.number))
            for i, image in enumerate(random_sequence((args.width, args.height),
                                          args.number,
                                          mode)):
                if not anim:
                    path, ext = os.path.splitext(args.destination)
                    image.save(path + "_" + str(i).zfill(z) + ext)
                else:
                    seq.append(image)
            if anim:
                im = seq.pop(0)
                im.save(args.destination, save_all=True,
                    duration=1000/24, loop=0, append_images=seq)
        else:
            im = random_image((args.width, args.height), mode)
            im.save(args.destination)

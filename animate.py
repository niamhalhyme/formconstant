#!/usr/bin/env python3

import cortex
import synth
import sys
import random
import argparse
import time

def save_random_sequence(size, number, duration, path, mode=None):
    if mode is None:
        mode = random.choice(["RGB", "HSV", "YCbCr", "CMYK"])
    frame_duration = duration // number
    seq =[cortex.derive_image(frame)
          for frame in synth.random_sequence(size, number, mode)]
    im = seq.pop(0)
    im.save(path, save_all=True, duration=frame_duration, loop=0,
            append_images=seq, comment=im.info["comment"][:255])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create form-constant style amimations.")
    parser.add_argument("width", type=int, help="width in pixels")
    parser.add_argument("height", type=int, help="height in pixels")
    parser.add_argument("number", type=int, help="number of frames")
    parser.add_argument("duration", type=int,
        help="duration of image loop in milliseconds")
    parser.add_argument("destination", help="destination path")
    args = parser.parse_args()
    start = time.time()
    save_random_sequence((args.width, args.height), args.number,
        args.duration, args.destination)
    end = time.time()
    print(end-start)

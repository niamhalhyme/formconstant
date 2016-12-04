#!/usr/bin/env python3

import cortex
import synth
import sys
import random

def save_random_sequence(size, number, duration, path, mode=None):
    if mode is None:
        mode = random.choice(["RGB", "HSV", "LAB", "YCbCr"])
    frame_duration = duration // number
    seq =[cortex.derive_image(frame) for frame in synth.random_sequence(size, number, mode)]
    im = seq.pop(0)
    im.save(path, save_all=True, duration=frame_duration, loop=0, append_images=seq,
            comment=im.info["comment"][:255])

if __name__ == "__main__":
    size = (int(sys.argv[1]), int(sys.argv[2]))
    number = int(sys.argv[3])
    duration = float(sys.argv[4])
    path = sys.argv[5]
    save_random_sequence(size, number, duration, path)

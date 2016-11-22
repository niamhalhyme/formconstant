#!/usr/bin/env python3

import math, cmath
from PIL import Image

def image_to_cortex_graph(im):
    dest = Image.new("RGB", im.size)
    max_r = (math.sqrt(im.size[0]**2 + im.size[1]**2)) / 2
    max_theta = 2*math.pi
    theta_values = [t for t in gen_theta(max_theta, im.size[1])]
    r_values = [r for r in gen_r(max_r, im.size[0])]
    for y, theta in enumerate(theta_values):
        print(y)
        for x, r in enumerate(r_values):
            xy = cmath.rect(r, theta)
            src_x  = round(xy.real + (im.size[0]/2))
            src_y = round(xy.imag + (im.size[1]/2))
            if src_x >= im.size[0] or src_y >= im.size[1] or src_x < 0 or src_y < 0:
                pixel_val = (0,0,0)
            else:
                pixel_val = im.getpixel((src_x, src_y))
            dest.putpixel((x,y), pixel_val)
    return dest 
    
def cortex_graph_to_image(im):
    dest = Image.new("RGB", im.size)
    max_r = (math.sqrt(im.size[0]**2 + im.size[1]**2)) / 2
    r_step = max_r / im.size[0]
    max_theta = 2*math.pi
    theta_step = max_theta / im.size[1]
    for y in range(im.size[1]):
        print(y)
        for x in range(im.size[0]):
            xy = complex(x - im.size[0]/2, y - im.size[1]/2)
            r, theta = cmath.polar(xy)
            if theta < 0:
                theta = (2*math.pi) + theta
            r = round(r / r_step)
            theta = round(theta / theta_step)
            src_x = abs(r)
            src_y = abs(theta)
            if src_x >= im.size[0] or src_y >= im.size[1] or src_x < 0 or src_y < 0:
                pixel_val = (0,0,0)
            else:
                pixel_val = im.getpixel((src_x, src_y))
            dest.putpixel((x,y), pixel_val)
    return dest 
            
            
    
def gen_r(max_r, size):
    step = (max_r / size)
    for i in range(size):
        yield (i * step)
 
def gen_theta(max_theta, size):
    step = max_theta/size
    for i in range(size):
        yield (step*i)
        
if __name__ == "__main__":
    import sys
    src_path = sys.argv[1]
    dest_path = sys.argv[2]
    src_im = Image.open(src_path)
    dest_im = cortex_graph_to_image(src_im)
    #dest_im = image_to_cortex_graph(src_im)
    dest_im.save(dest_path)

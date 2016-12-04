#!/usr/bin/env python3

import math, cmath
from PIL import Image

            
def get_mapped_pixel(im, src_coord, derived_coord):
    x,y = derived_coord
    x = x % im.size[0]
    y = y % im.size[0]
    x_int = int(x) 
    x_frac = x - x_int
    y_int = int(y)
    y_frac = y - y_int
    values = []
    distances = []
#if x_int >= 0 and x_int < im.size[0] and y_int >= 0 and y_int < im.size[1]:
    values.append(im.getpixel((x_int, y_int)))
    distances.append(math.sqrt((x_frac**2) + (y_frac**2)))
    values.append(im.getpixel(((x_int + 1) % im.size[0], y_int)))
    distances.append(math.sqrt(((1 - x_frac)**2) + (y_frac**2)))
    values.append(im.getpixel((x_int, (y_int + 1) % im.size[1])))
    distances.append(math.sqrt((x_frac**2) + ((1 - y_frac)**2)))
    values.append(im.getpixel(((x_int + 1) % im.size[0], (y_int + 1) % im.size[1])))
    distances.append(math.sqrt(((1 - x_frac)**2) + ((1 - y_frac)**2)))
    total_distance = sum(distances)
    if total_distance:
        channels = []
        for channel in [0,1,2]:
            channels.append(round(sum([values[i][channel] *
                                 (distances[i] / total_distance)
                                 for i in range(len(values))])))
        pixel_value = tuple(channels)
    else:
        pixel_value = (0,0,0)
#else:
#    pixel_value = (0,0,0)
    return pixel_value


def combine_with(im, source_weight=0.5):
    def _combine_with(src_im, src_coord, derived_coord):
        px1 = src_im.getpixel(src_coord)
        px2 = get_mapped_pixel(im, None, derived_coord)
        pixel_value = tuple([round((px1[i] * source_weight) +
                                  (px2[i] * (1 - source_weight)))
                             for i in [0,1,2]])
        return pixel_value
    return _combine_with
        


def derive_image(im, modifier=get_mapped_pixel):
    # create a new image for the derived image to be wrtten to
    dest = Image.new("RGB", im.size)
    # the maximum value of r is the length of the diagonal from the centre of
    # the image to a corner
    max_r = math.log1p(math.sqrt(im.size[0]**2 + im.size[1]**2) / 2)
    # the maximum value of phi is the constant 2*pi
    max_phi = 2 * math.pi
    #r_step = max_r / im.size[0]
    phi_step = max_phi / im.size[1]
    data = []
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            xy = complex(x - im.size[0]/2, y - im.size[1]/2)
            r, phi = cmath.polar(xy)
            if phi < 0:
                phi = (2*math.pi) + phi
            deriv_x = (math.log1p(r)/max_r) * im.size[0]
            deriv_y = (phi/max_phi) * im.size[1]
            data.append(modifier(im, (x,y), (deriv_x, deriv_y)))
    dest.putdata(data)
    try:
        dest.info["comment"] = im.info["comment"]
    except KeyError:
        pass
    return dest
    


if __name__ == "__main__":
    import sys
    src_path = sys.argv[1]
#    combin_path = sys.argv[2]
    dest_path = sys.argv[2]
    src_im = Image.open(src_path)
#    combin_im = Image.open(combin_path)
    #dest_im = derive_image(src_im, combine_with(combin_im, 0.1))
    dest_im = derive_image(src_im)
    dest_im.save(dest_path)

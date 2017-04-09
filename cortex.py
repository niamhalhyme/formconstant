#!/usr/bin/env python3

import math
import cmath
import argparse
import time
from PIL import Image

            
def get_mapped_pixel(size, imdata, derived_coord):
    """
    Return the interpolated pixel value in an image at the given coordinate.
    """
    # map coordinates outside of the image back into the image
    # get the integer and fractional parts of the x and y coordinates
    x_int, x_frac = divmod(derived_coord[0] % size[0], 1)
    y_int, y_frac = divmod(derived_coord[1] % size[1], 1)
    # get the values of the four bounding pixels
    values = [
        imdata[int((y_int * size[0]) + x_int)],
        imdata[int((y_int * size[0]) + ((x_int +1) % size[0]))],
        imdata[int((((y_int + 1) % size[1]) * size[0]) + x_int)],
        imdata[int((((y_int + 1) % size[1]) * size[0]) + 
                     ((x_int + 1) % size[0]))]
    ]
    # get the distance of the coord from its four bounding pixels
    distances = [
        math.hypot(x_frac, y_frac),
        math.hypot(1-x_frac, y_frac),
        math.hypot(x_frac, 1-y_frac),
        math.hypot(1-x_frac, 1-y_frac)

    ]
    total_dist = sum(distances)
    distance_weights = [distances[0] / total_dist,
                        distances[1] / total_dist,
                        distances[2] / total_dist,
                        distances[3] / total_dist]
    # get the number of channels in the image
    return (
        (int(round(
            (values[0][0] * distance_weights[0]) +
            (values[1][0] * distance_weights[1]) +
            (values[2][0] * distance_weights[2]) +
            (values[3][0] * distance_weights[3])))),
        (int(round(
            (values[0][1] * distance_weights[0]) +
            (values[1][1] * distance_weights[1]) +
             (values[2][1] * distance_weights[2]) +
            (values[3][1] * distance_weights[3])))),
        (int(round(
            (values[0][2] * distance_weights[0]) +
            (values[1][2] * distance_weights[1]) +
            (values[2][2] * distance_weights[2]) +
            (values[3][2] * distance_weights[3])))))



def derive_image(im):
    """
    Return an image derived from a source image by mapping the x axis to
    the log of r and the y axis to phi where r and phi are polar coordinates
    """
    im = im.convert("RGB")
    imdata = list(im.getdata())
    # max_r is the log of the distance from the centre to a corner
    max_r = math.log1p(math.sqrt(im.size[0]**2 + im.size[1]**2) / 2)
    # max_phi is the constant 2*pi
    max_phi = 2 * math.pi
    phi_step = max_phi / im.size[1]
    data = []
    # for each pixel in the source image
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            # convert to polar coords
            r, phi = cmath.polar(complex(x - im.size[0]/2, y - im.size[1]/2))
            if phi < 0:
                phi = max_phi + phi
            # map x and y 
            data.append(get_mapped_pixel(im.size, imdata,
                ((math.log1p(r)/max_r) * im.size[0],
                (phi/max_phi) * im.size[1])))
    dest = Image.new("RGB", im.size)
    dest.putdata(data)
    try:
        dest.info["comment"] = im.info["comment"]
    except KeyError:
        pass
    return dest
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert an image into a form constant mapping of itself.")
    parser.add_argument("source", help="source path")
    parser.add_argument("destination", help="destination path")
    args = parser.parse_args()
    start = time.time()
    derive_image(Image.open(args.source)).save(args.destination)
    end = time.time()
    print(end - start)


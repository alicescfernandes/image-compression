import cv2
import numpy as np
from time import time
from math import sqrt
from executiontime import printexecutiontime, LIGHBLUE

from blocks.tables import ind_O,ind_Z
from blocks.dct import calc_dct, calc_idct
from blocks.quant import quantize, dequantize
from blocks.encode import dc_encode, ac_encode,dc_decode, ac_decode
from classes.stream import Stream
from bin_utils import int_to_bit_array

# IDEA: Separate the processing in threads and get back the data in order
# IDEA: Encode Cb and Cr. Read about this

input = "sources/balls_16.jpg"

# Convert to YCbCr (YUV)
input_rgb = cv2.imread(input)
img_yuv = cv2.cvtColor(input_rgb, cv2.COLOR_BGR2YUV)
y,cb,cr = cv2.split(img_yuv)

image_shape = input_rgb.shape


def encode_image(y,cb,cr):
    for l in range(0, y.shape[0], 8):
        for c in range(0, y.shape[1], 8):            
            y_slice = y[l:l+8,c:c+8]
            cb_slice = cb[l:l+8,c:c+8]
            cr_slice = cr[l:l+8,c:c+8]

            print(y_slice)


encode_image(y,cb,cr)
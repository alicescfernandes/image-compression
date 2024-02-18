import cv2
import numpy as np
from time import time
from math import sqrt
from executiontime import printexecutiontime, LIGHBLUE

from tables import ind_O,ind_Z, k3_lookup,k5_lookup
from dct import calc_dct, calc_idct
from quant import quantize, dequantize
from encode import dc_encode, ac_encode
from stream import Stream, bin_to_byte
# IDEA: Separate the processing in threads and get back the data in order


input = "sources/16x16.tiff"
#input = "sources/flower-luma-gray.jpg"

# Convert to YCbCr (YUV)
input_rgb = cv2.imread(input)
img_yuv = cv2.cvtColor(input_rgb, cv2.COLOR_BGR2YUV)
y,cb,cr = cv2.split(img_yuv)

image_shape = input_rgb.shape

# create and 
output_name = "tmp_file.bin"


@printexecutiontime("Encoding Image took {0}", color=LIGHBLUE)
def encode_image(image):
    #wipe temp file and open file
    open(output_name, 'w').close()
    output_file = open(output_name, mode="ab")
    last_dc = 0
    bytes_array = []
    encoded_message = []
    for l in range(0, image.shape[0], 8):
        for c in range(0, image.shape[1], 8):            
            block = image[l:l+8,c:c+8]
            
            # DCT             
            dct_block = calc_dct(block)

            # Quantize
            quantize_block = quantize(dct_block)

            # Convert to zig zag & extract AC and DC
            block_flat = quantize_block.flatten(order='F')
            zigzag = block_flat[ind_Z]

            dc = zigzag[0]
            ac = zigzag[1::]

            # Convert DC
            # Apply DPCM algo. The encoded DC value is the Dc_x - Dc-(x-1)
            dc_diff = dc - last_dc
            last_dc = dc;   

            dc_encoded = dc_encode(dc_diff)
            ac_encoded = ac_encode(ac)

            encoded_message = encoded_message + dc_encoded + list(ac_encoded)

    # save message 
    # hint: first byte of block will be the trailing zeros
    bits_to_bytes = Stream(encoded_message, 1)
    end = False                
    while(end is False):
        byte = bits_to_bytes.get_byte()
        end = bits_to_bytes.eof()
        bytes_array += [byte]
    
    bytes_array = [bits_to_bytes.trailing_zeros] + bytes_array
    output_file.write(bytearray(bytes_array))

            
# encode_image(y)

# TODO: iterate per each 64 codes
# After each block end, go to next


def get_bits(stream, size):
    byte_from_bin = [stream.get_bit() for i in range(size)]
    byte_from_bin = bin_to_byte(byte_from_bin)
    return byte_from_bin

def decode_image():
    input_file = open(output_name, mode="rb")
    stream = Stream(input_file, 0)

    # First byte is the trailing zeroes. Cut them from the actual bit stream or exclude them from the end (if end of file is reached)
    trailing_zeros = get_bits(stream,8)
    
    dc_dpcm = 0
    
    # Iterate until (0,0)
    # Each block starts with the DC component and ends with the (0,0) AC. Each code is unique
    for k in range(4):
        block = []
        dc_detected = 0
        while len(block) < 64:
            if(len(block) < 1):
                dc_block = k3_lookup(stream)
                block += [dc_block]
                continue; # first dc achieved, end the iteration here

            (zeroes_counter, ac_block) = k5_lookup(stream)
            end_of_block = zeroes_counter == 0 and ac_block == 0
            
            # Every AC block ends with (0,0) huffman code
            if(end_of_block is False):
                zeroes = [0] * zeroes_counter
                block += zeroes + [ac_block]
                continue; # end the iteration here. its not end of block

            # end of block here. add the remaining zeroes and undo zigzag
            trailing_zeros_block = [0] * (64 - len(block))
            block += trailing_zeros_block
            print(block)
            # TODO: Undo zigzag



        # read until detect code
        # it was better if we had the huffman as tree, but we only have it as values of an object
        # another solution would to convert it to bytes and check if the byte exists, since they are unique (NOPE, SOME SYMBOLS ARE 15 LENGTH)
        # best case scenario is to reverse the lists and look on the keys
        # after code is detected, increment counter
        # first code is always AC
        # rest of codes are DC
        # AC uses run length encoding, so keep it to decode the next ac's
    

decode_image()


# Convert back to RGB
#output_rgb= cv2.merge([idct_matrix,cb,cr])
#output_rgb = cv2.cvtColor(output_rgb, cv2.COLOR_YUV2BGR)

# show both images
#numpy_vertical = np.hstack((input_rgb, output_rgb))
#cv2.imshow("in", numpy_vertical) 
#cv2.waitKey(0) 
# cv2.destroyAllWindows() 
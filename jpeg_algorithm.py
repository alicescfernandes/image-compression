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

input = "sources/balls.tiff"
# input = "sources/16x16.tiff"
# input = "sources/flower-luma-gray.jpg"

# Convert to YCbCr (YUV)
input_rgb = cv2.imread(input)
img_yuv = cv2.cvtColor(input_rgb, cv2.COLOR_BGR2YUV)
y,cb,cr = cv2.split(img_yuv)

image_shape = input_rgb.shape

output_name = "tmp_file.bin"

def encode_header():
    bits = []
    height = image_shape[0]
    width = image_shape[1]
    
    bits_height = int_to_bit_array(height, 16)
    bits_width = int_to_bit_array(width, 16)
    bits_size = int_to_bit_array(16,8)
    
    end_of_header1 = int_to_bit_array(255)
    end_of_header2 = int_to_bit_array(4)
    
    bits = bits_height + bits_width
    
    return bits

def decode_header(input_file):
    # 2 bytes for width and 2 more for height
    height = int.from_bytes(input_file.read(2))
    width = int.from_bytes(input_file.read(2))
    return (height,width)

@printexecutiontime("Encoding Image took {0}", color=LIGHBLUE)
def encode_image(image):
    # wipe temp file and open file
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

    header = encode_header()
    encoded_message = header + encoded_message
    # save message 
    # hint: first byte of block will be the trailing zeros
    bits_to_bytes = Stream(encoded_message, 1)
    end = False                
    while(end is False):
        byte = bits_to_bytes.get_byte()
        end = bits_to_bytes.eof()
        bytes_array += [byte]
    
    output_file.write(bytearray(bytes_array))

# shape: : (H, W, D) 
@printexecutiontime("Decoding Image took {0}", color=LIGHBLUE)
def decode_image():
    input_file = open(output_name, mode="rb")
    
    (height,width) = decode_header(input_file)

    total_blocks = (height // 8) * (width // 8)

    # Keep reference for DC DPCM coding
    dc_dpcm = 0
    
    stream = Stream(input_file, 0)
    # Iterate until (0,0)
    # Each block starts with the DC component and ends with the (0,0) AC. Each code is unique
    reconstructed_image = np.zeros((height,width))
    current_column = 0
    current_line = 0
    for k in range(total_blocks):
        block_zigzag = []
        dc_detected = 0

        while len(block_zigzag) < (8*8):
            if(len(block_zigzag) < 1):
                dc_block = dc_decode(stream)
                dc_dpcm = dc_dpcm + dc_block
                block_zigzag += [dc_dpcm]
                continue; # first dc achieved, end the iteration here

            (zeroes_counter, ac_block) = ac_decode(stream)
            
            # Every AC block ends with (0,0) huffman code
            end_of_block = zeroes_counter == 0 and ac_block == 0
            
            if(end_of_block is False):
                zeroes = [0] * zeroes_counter
                block_zigzag += zeroes + [ac_block]
                continue; # end the iteration here. its not end of block

            # end of block here. add the remaining zeroes and undo zigzag
            trailing_zeros_block = [0] * (64 - len(block_zigzag))
            block_zigzag += trailing_zeros_block

            # Undo zigzag
            block_zigzag = np.array(block_zigzag).flatten(order='F')
            block_8x8 = block_zigzag[ind_O].reshape((8,8),order='F')

            # Undo quantization
            dequant = dequantize(block_8x8)

            # reverse idct
            original_block = calc_idct(dequant)
            
            # Reconstruct image
            reconstructed_image[current_line:current_line+8,current_column:current_column+8] = original_block
            current_column = current_column + 8
            if(current_column >= width):
                current_column = 0
                current_line = current_line + 8

    return reconstructed_image.astype(np.uint8)

encode_image(y)
y_decoded = decode_image()

# Convert back to RGB
output_rgb= cv2.merge([y_decoded,cb,cr])
output_rgb = cv2.cvtColor(output_rgb, cv2.COLOR_YUV2BGR)

# show both images
numpy_vertical = np.hstack((input_rgb,output_rgb))
cv2.imshow("in", numpy_vertical) 
cv2.waitKey(0) 
cv2.destroyAllWindows() 

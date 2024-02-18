import cv2
import numpy as np
from tables import K3,K5, quality_factor
from bin_utils import  get_bin_repr, bin_string_to_arr
from executiontime import printexecutiontime, LIGHBLUE


# returns DC encoded data in the binary form
# example:  -176
# -176 = [0, 1, 0, 0, 1, 1, 1, 1], size 8 (8 bits)
# k3[8] = [1,1,1,1,1,0]
# returns  [1,1,1,1,1,0, 0, 1, 0, 0, 1, 1, 1, 1 ] (k3, -176)
#@printexecutiontime("DC Encode: {0}", color=LIGHBLUE)
def dc_encode(dc_coef):
    dc_coded = []

    if(dc_coef == 0):
        K3_code =  bin_string_to_arr(K3[0])
        dc_coded = dc_coded = K3_code
    else:
        (size, binary_repr) = get_bin_repr(dc_coef)
        K3_code = K3[size]
        dc_coded += K3_code +binary_repr
    print("DC",size,dc_coef, binary_repr)
    return dc_coded

# Encodes RLC and huffman
#@printexecutiontime("AC Encode: {0}", color=LIGHBLUE)
def ac_encode(ac_coef):
    zeroes_counter = 0;

    rlc_code_raw = []
    rlc_code_huffman = []

    n_arr = []


    # remove all zeroes after the last non-zero code
    # we dont need to encode zeroes, the decoder can pad blocks on decoding, and this logic saves processing time
    ac_reverse = ac_coef[::-1]
    ac_reverse = [v != 0 for v in ac_reverse ]
    last_true = len(ac_reverse) - ac_reverse.index(True)

    if(last_true > 0):
        ac_coef = ac_coef[0:last_true]


    for n in ac_coef:
        n_arr += [n]
        if(n == 0):
            if(zeroes_counter == 15):
                rlc_code_huffman = rlc_code_huffman + bin_string_to_arr(K5[(15, 0)])
                zeroes_counter = 0;
            else:
                zeroes_counter = zeroes_counter+1;
        
        else:
            (size, binary_repr) = get_bin_repr(n)
            rlc_code_huffman = rlc_code_huffman + bin_string_to_arr(K5[(zeroes_counter, size)]) + binary_repr
            zeroes_counter = 0

            print("AC",n,zeroes_counter, bin_string_to_arr(K5[(zeroes_counter, size)]), binary_repr)
    print(n_arr)
    rlc_code_huffman = rlc_code_huffman + bin_string_to_arr(K5[(0, 0)])

    return rlc_code_huffman
import cv2
import numpy as np

def calc_dct(slice_image):
    # convert to floats
    slice_float = np.float32(slice_image)

    # subtract 128
    slice_float = slice_float - 128
    
    # calculate dct
    dct_block = cv2.dct(slice_float, cv2.DCT_INVERSE)

    return dct_block


def calc_idct(dct_bloco):
    # reverse idct
    idct_bloco = cv2.idct(dct_bloco)

    # add 128
    img_reconv = idct_bloco + 128

    return img_reconv.astype("uint8")
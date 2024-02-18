import cv2
import numpy as np
from tables import K1, quality_factor

# TODO: Temp fix é meter isto em uint8
def quantize(block, quality=90):
    block_quant = np.round(block / (K1 * quality_factor(quality)))

    return block_quant.astype("int")



def dequantize(dct_quant):

    (rows,cols) = dct_quant.shape
    matrix_dequant = np.zeros((rows, cols))
    dct_quant = dct_quant.astype(np.float32)

    for l in range(0, rows, 8):
        for c in range(0, cols, 8):

            block = dct_quant[l:l+8,c:c+8]

            block_dequant =  quality_factor(90) * K1 * block

            matrix_dequant[l:l+8,c:c+8] = block_dequant


    matrix_dequant.astype("int")
    return matrix_dequant
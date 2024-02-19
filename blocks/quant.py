import cv2
import numpy as np
from blocks.tables import K1, quality_factor

# TODO: Temp fix é meter isto em uint8
def quantize(block, quality=90, quant_table = K1):
    block_quant = np.round(block / (quant_table * quality_factor(quality)))

    return block_quant.astype("int")

def dequantize(block, quality=90, quant_table = K1):
    block_dequant = block.astype("float32")
    block_dequant =  quality_factor(quality) * quant_table * block_dequant
    
    return block_dequant


def dequantize_no_quality(block, quant_table = K1):
    block_dequant = block.astype("float32")
    block_dequant =  quant_table * block_dequant
    
    return block_dequant

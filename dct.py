import cv2
import numpy as np

# todo: convert back to uint8. this os probably because of conversion
def calc_dct(slice_image):
    # convert to floats
    slice_float = np.float32(slice_image)

    # subtract 128
    slice_float = slice_float;
    
    slice_float = slice_float - 128
    
    # calculate dct
    dct_block = cv2.dct(slice_float, cv2.DCT_INVERSE)

    return dct_block


def calc_idct(dct_matrix):

    (rows,cols) = dct_matrix.shape

    img_rec = np.zeros((rows,cols))
    idct_matrix = np.zeros((rows,cols), dtype=np.uint8)

    for l in range(0, rows, 8):
        for c in range(0, cols, 8):

            dct_bloco = dct_matrix[l:l+8,c:c+8]

            idct_bloco = cv2.idct(dct_bloco)
            img_reconv = idct_bloco + 128

            idct_matrix[l:l+8,c:c+8] = img_reconv

    return idct_matrix
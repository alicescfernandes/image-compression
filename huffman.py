# Excutes the stuff
def encode(matrix):
    (rows, cols) = matrix.shape
    img_rec = np.zeros((rows,cols))
    idct_matrix = np.zeros((rows,cols))
    dpcm_encoding = []

    last_dc = 0;

    encoded_block = []

    encoded_msg = []

    for l in range(0, rows, slice_size):
        for c in range(0, cols, slice_size):

            block = matrix[l:l+slice_size,c:c+slice_size]
            block_flat = block.flatten(order='F')
            zigzag = block_flat[ind_Z]
            
            dc = int(zigzag[0]);
            dc_diff = dc - last_dc
            last_dc = dc;

            dc_encoded = dc_encode(dc_diff) # Gets the DC factor
            ac_encoded = ac_encode(zigzag[1::]) # Gets the remaining AC stuff

            encoded_msg = encoded_msg + dc_encoded + ac_encoded

    return encoded_msg

# TODO: This is not really fast, mostly because its a while with alot of operations
# It should be possible to paralelize this somehow
# Time this function
# TODO: This is not moving well to new blocks
def decode(bit_stream):
    bit_buffer = ""
    current_dc = 0;
    encoded_stuff = []
    pointer = 0;
    is_new_block = True
    iters = 0
    bit_stream_length = len(bit_stream)
    end_image = np.array([])

    while pointer < bit_stream_length:
        bit = bit_stream[pointer]
        bit_buffer = bit_buffer + str(bit)
        increment = 1
        # Detect K3 table
        if (is_new_block is True and bit_buffer in reverse_K3):
            is_new_block = False

            # Grab the K3 size and coded number, and pass into decoder
            K3_size = reverse_K3[bit_buffer]
            dc_coeff = bit_stream[pointer+1: pointer+1+K3_size]
            current_dc = dc_decode(dc_coeff, K3_size,current_dc)

            increment = increment + K3_size
            bit_buffer = ''
    
            ac_zigzag = np.array([],dtype=np.uint8)

        # Detect K5 only after K3 is detected
        if(is_new_block is False and bit_buffer in reverse_K5):
            # Detect the block end before, to use that to decide what to do
            is_new_block = bit_buffer == K5[(0,0)] # block ended. next block detect the DC first
            

            if(is_new_block == False):
                (run_zero_length,size) = reverse_K5[bit_buffer]
                amplitude_bin = bit_stream[pointer+1: pointer+1+size]
                amp = bit_array_to_int(amplitude_bin, True) 
                ac_zigzag = np.append(ac_zigzag, [ (run_zero_length,size, amp)])

            if(is_new_block == True):
                decoded = ac_decode(ac_zigzag,current_dc)
                end_image = np.append(end_image, decoded)

            bit_buffer = ''
            increment = increment + size

        pointer = pointer + increment


    # Calculate the original size image
    #size = int(sqrt(len(end_image))) # 16x16 = 256 -> sqrt(256) = 16
    #matrix = end_image.reshape((size,size))
    print("end_image",end_image)
    return end_image


def dc_encode(dc_coef):

    (size, binary_repr) = get_bin_repr(dc_coef)

    dc_coded = bin_string_to_arr(K3[size]) + binary_repr
    if(dc_coef == 0):
        dc_coded = dc_coded = bin_string_to_arr(K3[0])

    print("dc_encode size",size)
    return dc_coded

def dc_decode(dc_code, size, current_dc):
    new_dc = current_dc;
    if(size > 0):
        dc_diff = bit_array_to_int(dc_code, True)
        print("dc_decode", dc_diff, size)
        new_dc = current_dc + dc_diff
    return new_dc 

def ac_encode(ac_coef):
    zeroes_counter = 0;

    rlc_code_raw = []
    rlc_code_huffman = []

    for n in ac_coef:

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

    rlc_code_huffman = rlc_code_huffman + bin_string_to_arr(K5[(0, 0)])

    return rlc_code_huffman


def ac_decode(zigzag, current_dc):
    ac_decoded = np.array([current_dc])
    for l in range(0, len(zigzag), 3):
        [run_zero_length,size, amp] = zigzag[l:l+3]
        
        if(run_zero_length > 0):
            zeros = [0] * run_zero_length
            ac_decoded = np.append(ac_decoded,zeros)
        
        ac_decoded = np.append(ac_decoded,[amp])

    # Adds the remaining 0's to fill a 8x8 flattened array
    missing_zeroes = 64 - len(ac_decoded)
    zeros = [0] * missing_zeroes
    ac_decoded = np.append(ac_decoded,zeros)
    # Un-zigzag the array
    # matrix = ac_decoded[ind_O].reshape((8,8),order='F')
    # matrix = ac_decoded[ind_O].reshape((64,),order='F')
    # matrix = ac_decoded.reshape((64,))

    return ac_decoded

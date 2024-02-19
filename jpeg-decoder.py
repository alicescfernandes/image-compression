# https://d33wubrfki0l68.cloudfront.net/bdc1363abbd5744200ec5283d4154e55143df86c/8c624/images/decoding_jpeg/jpegrgb_dissected.png
# https://yasoob.me/posts/understanding-and-writing-jpeg-decoder-in-python/#decoding-the-quantization-table

from struct import unpack
import codecs
import numpy as np
# from HuffmanTable import HuffmanTable
from classes.stream import Stream
from blocks.encode import dc_encode, ac_encode,dc_decode, ac_decode
from blocks.tables import ind_O,ind_Z
from blocks.dct import calc_dct, calc_idct
from blocks.quant import quantize, dequantize_no_quality
from blocks.encode import dc_encode, ac_encode,dc_decode, ac_decode
from classes.stream import Stream
from bin_utils import int_to_bit_array

# todo: make a class out of this
# todo: only works for luma grayscale
# Markers & names
START_OF_FRAME = b'\xff\xc0'
APPLICATION_DEFAULT_HEADER = b'\xff\xe0'
QUANTIZATION_TABLE = b'\xff\xdb'
START_OF_IMAGE = b'\xff\xd8'
DEFINE_HUFFMAN_TABLE = b'\xff\xc4'
START_OF_SCAN = b'\xff\xda'
END_OF_IMAGE = b'\xff\xd9'

markers = {}
markers[START_OF_IMAGE] = "Start of Image"
markers[APPLICATION_DEFAULT_HEADER] = "Application Default Header"
markers[QUANTIZATION_TABLE] = "Quantization Table"
markers[START_OF_FRAME]= "Start of Frame"
markers[DEFINE_HUFFMAN_TABLE]= "Define Huffman Table"
markers[START_OF_SCAN]= "Start of Scan"
markers[END_OF_IMAGE]= "End of Image"

# Quantization constants
QUANT_DEST_LUMA = 0
QUANT_DEST_CHROMA = 1
quant_dest = {}
quant_dest[QUANT_DEST_LUMA] = "LUMA"
quant_dest[QUANT_DEST_CHROMA] = "CHROMA"

# Huffman Constants
HUFFMAN_DC_TABLE = 0
HUFFMAN_AC_TABLE = 1

# Start of frame Components indexes
COMPONENT_ID = 0
COMPONENT_SAMPLE_FACTOR = 1
COMPONENT_QUANT_TABLE = 2

# image shape constants
IMG_WIDTH = 0
IMG_HEIGHT = 1

#f = open("sources/flower-luma-gray.jpg", "rb")
#f = open("sources/house-rgb-gray.jpg", "rb")
f = open("sources/16x16.jpg", "rb")


quant_tables =  {}
huffman_tables =  {}
quant_tables_mapping = []
shape = ()
components = 0


def parse_quantization_table(quant):
    """ """
    table = "".join(['b'] * 65) # replicates "b" 64 times
    [destination, *quant_factors] = unpack(">"+table, quant[0:65])    

    # affect global variables
    quant_tables[destination] = np.array(quant_factors).reshape((8,8))
    

def parse_header(header):
    """ """
    unpacked = unpack(">ccccbbbbhhbb", header[0:14])

def parse_huffman(data):
    # 1 byte for header, 
    # 16 bytes for huffman. has the codes the amount of encoded codes per length, from length 1 to length 16
    # something like lengths[0] would be the amount of huffman codes of 1 bit  (x codes of this type)
    # something like lengths[2] would be the amount of huffman codes of 2 bits  (y codes of this type)
    [header, *lengths] = unpack(">bbbbbbbbbbbbbbbbb", data[0:17]) 
    # get bitstring of the header byte
    header_bitstring = "{:08b}".format(header)

    huffman_table_type = header_bitstring[3] # bit 4 is the type of table
    huffman_table_dest = header_bitstring[7] # bit 8 is the destination of table
    
    print(huffman_table_type)
    print(huffman_table_dest)
    # after the codes, we have the symbols used
    total_number = np.sum(lengths)
    symbols = unpack("B"*total_number, data[17:17+total_number])
    
    # todo: take the symbols and their lengths and rebuild the huffman tree
    # todo: not understanding this logic
    # hf = HuffmanTable()
    # hf.GetHuffmanBits(lengths, symbols)

    # affect global variables
    # huffman_tables[(huffman_table_type,huffman_table_dest)] = hf
    huffman_tables[(huffman_table_type,huffman_table_dest)] = []

def parse_start_of_frame(sof):
    hdr, height, width, components = unpack(">BHHB",sof[0:6])

    components_unpack_format = "".join(['b'] * components * 3) # replicates "b" 64 times
    components_unpacked = unpack(">"+components_unpack_format,sof[6:])  #  foramt: [id, sample,quant_table,id, sample,quant_table,id, sample,quant_table]
    quantization_tables_ids = components_unpacked[COMPONENT_QUANT_TABLE::3] # every the third element (index+) every three indexes we have the quant table for the component

    # Affect global variables
    global shape
    shape = (width,height)

    global quant_tables_mapping
    quant_tables_mapping = quantization_tables_ids


def parse_scan(sof):
    [components_sof] = unpack(">B", sof[0:1])

    global components 
    components = components_sof

def parse_image_data(image_data):
    
    # remove \x00 after \xff
    image_data = image_data.replace(b'\xff\x00',b'\xff')

    # remove end of image marker
    image_data = image_data[:-2]
    
    dpcm_luma, dpcm_cb, dpcm_cr = 0, 0, 0

    stream = Stream(image_data,0)

    (width, height) = shape
    total_blocks = (height // 8) * (width // 8)
    
    for y in range(height//8):
        for x in range(width//8):
            dpcm_luma = decode_block(stream,dpcm_luma,quant_tables[QUANT_DEST_LUMA], 'LUMA', 8)
            dpcm_cb = decode_block(stream,dpcm_cb,quant_tables[QUANT_DEST_CHROMA], 'LUMA', 4)
            #dpcm_cr = decode_block(stream,dpcm_cr,quant_tables[QUANT_DEST_CHROMA], 'LUMA', 4)

            print()
            exit()

    """
    dc_block = dc_decode(stream)

    ac_block1 = ac_decode(stream)
    ac_block2 = ac_decode(stream)

    
    print(huffman_tables)
    print(quant_tables)
    print(quant_tables_mapping)
    print("dc_block",dc_block)

    print("ac_block",ac_block1)
    print("ac_block",ac_block2)
    """

    #code = huffman_tables[('0','0')].GetCode(st)
    #bits = st.GetBitN(code)
    #print("code",code)
    #print("bits",bits)
    #dccoeff = DecodeNumber(code, bits)
    #print(dccoeff)

    """
    todo: For each 8x8 pixel
        - Decode the data into bits, or find a way to extract bits out of the bytes
        - For everybit, try to find the correct Huffman code
            - repeat the process 64 times everytime. Each iteration gets a single decoded huffman (and only after count)
            - the first huffman will be the DC component
        - Decode RLC and DCPM
        - Dequantize
        - Calculate an IDCT on the dequant data
    """


def decode_block(stream, dc_dpcm, quantization_table, block_type, block_size = 8):
    block_zigzag = []
    dc_detected = 0
    total_blocks = block_size*block_size
    while len(block_zigzag) < total_blocks:
        if(len(block_zigzag) < 1):
            dc_block = dc_decode(stream)
            dc_dpcm = dc_dpcm + dc_block
            block_zigzag += [dc_dpcm]
            continue; # first dc achieved, end the iteration here

        (zeroes_counter, ac_block) = ac_decode(stream)
        
        # Every AC block ends with (0,0) huffman code
        end_of_block = zeroes_counter == 0 and ac_block == 0
        print(zeroes_counter, ac_block)
        if(end_of_block is False):
            zeroes = [0] * zeroes_counter
            block_zigzag += zeroes + [ac_block]
            continue; # end the iteration here. its not end of block
        print(2)
        # end of block here. add the remaining zeroes and undo zigzag
        trailing_zeros_block = [0] * (total_blocks - len(block_zigzag))
        block_zigzag += trailing_zeros_block

        # Undo zigzag
        block_zigzag = np.array(block_zigzag).flatten(order='F')
        block_8x8 = block_zigzag[ind_O].reshape((block_size,block_size),order='F')

        # Undo quantization
        dequant = dequantize_no_quality(block_8x8, quantization_table)

        # reverse idct
        original_block = calc_idct(dequant)
        
        print(original_block)
    return dc_dpcm
        #return (original_block, dc_dpcm)
            

start_of_scan = 0
end_of_image = 0
while True:
    byte = f.read(2)

    if byte == b'':
        print("file finished")
        break;


    if byte in markers:
        print(markers[byte])

        if(byte == APPLICATION_DEFAULT_HEADER):
            application_header_size = int.from_bytes(f.read(2)) - 2            
            header = f.read(application_header_size)
            parse_header(header)

        if(byte == QUANTIZATION_TABLE):
            quant_luma_size = int.from_bytes(f.read(2)) - 2
            quant_luma_table = f.read(quant_luma_size)
            parse_quantization_table(quant_luma_table)

        if(byte == START_OF_FRAME):
            sof_size = int.from_bytes(f.read(2)) - 2
            sof_data = f.read(sof_size)
            parse_start_of_frame(sof_data)

        if(byte == DEFINE_HUFFMAN_TABLE):
            huffman_size = int.from_bytes(f.read(2)) - 2
            huffman_table = f.read(huffman_size)
            parse_huffman(huffman_table)
        
        if(byte == START_OF_SCAN):
            scan_size = int.from_bytes(f.read(2)) - 2
            scan_data = f.read(scan_size)
            parse_scan(scan_data)

            # reads the rest of the image. this is the image data
            image_data = f.read()
            parse_image_data(image_data)
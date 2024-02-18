from struct import unpack
import codecs
import numpy as np
# https://d33wubrfki0l68.cloudfront.net/bdc1363abbd5744200ec5283d4154e55143df86c/8c624/images/decoding_jpeg/jpegrgb_dissected.png
from HuffmanTable import HuffmanTable
from Stream import Stream

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

f = open("sources/flower-luma-gray.jpg", "rb")
#f = open("sources/house-rgb-gray.jpg", "rb")


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
    quant_tables[destination] = quant_factors
    

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
    hf = HuffmanTable()
    hf.GetHuffmanBits(lengths, symbols)

    # affect global variables
    huffman_tables[(huffman_table_type,huffman_table_dest)] = hf

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


def DecodeNumber(code, bits):
    l = 2**(code-1)
    if bits>=l:
        return bits
    else:
        return bits-(2*l-1)


def parse_image_data(image_data):
    
    # remove \x00 after \xff
    image_data = image_data.replace(b'\xff\x00',b'\xff')

    # remove end of image marker
    image_data = image_data[:-2]
    
    oldlumdccoeff, oldCbdccoeff, oldCrdccoeff = 0, 0, 0

    st = Stream(image_data)

    
    print(huffman_tables)
    print(quant_tables)
    print(quant_tables_mapping)



    code = huffman_tables[('0','0')].GetCode(st)
    bits = st.GetBitN(code)
    print("code",code)
    print("bits",bits)
    dccoeff = DecodeNumber(code, bits)
    print(dccoeff)

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


    for y in range(shape[IMG_HEIGHT] // 8):
        for x in range(shape[IMG_WIDTH] f// 8):
            """ """

            

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
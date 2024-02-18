import sys
import numpy as np
from bin_utils import convert_to_bin
    
# TODO: I dont think i need padded bytes where this is going
def write2file(bit_array, filename="binfile.bin"):
    padding_byte_count = 8 - len(bit_array) % 8  # Calculates the amount of padded bytes that will need
    padded_array = np.append(bit_array, [0] * padding_byte_count) # append padding bits at end

    padding_bytes = convert_to_bin(padding_byte_count)
    padded_msg = np.append(padding_bytes,padded_array) # append amount of padded bits at begining

    pack_bits = np.packbits(padded_msg)
    f = open(filename,"wb")
    f.write(pack_bits.tobytes())
    f.close()

def readfile(file):
    byte_file = open(file, "rb")
    
    # Read padded bits
    byte_content = np.frombuffer(byte_file.read(1),dtype=np.uint8)# padded bytes should be discarded
    padded_bits = byte_content[0]
    
    # Read content
    byte_content = np.frombuffer(byte_file.read(),dtype=np.uint8)# padded bytes should be discarded
    unpack_bits = np.unpackbits(byte_content)
    message_content = unpack_bits[0:len(unpack_bits)-padded_bits]

    return message_content
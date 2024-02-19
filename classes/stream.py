# Takes a stream of data and converts into individual bits
# to be used with huffman
# todo: check end of stream
import io

def bin_to_byte(value):
    out = 0
    for bit in value:
        out = (out << 1) | bit

    return out

def byte_to_bin(value):
    bit_repr = []

    while(value > 0):
        remainder = value % 2
        value = value // 2
        bit_repr = bit_repr + [remainder]
    return bit_repr[::-1]

BYTE_TO_BIT = 0
BIT_TO_BYTE = 1,
FILE_TO_BIT = 2

class Stream():
    def __init__(self, stream, mode = 0):
        self.stream = stream
        self.read_pointer = 0
        self.buffer = []
        self.buffer_pointer = None
        self.trailing_zeros = 0

        if type(stream) is not io.BufferedReader:
            self.stream = list(stream)
        
        if(mode == 0):
            self.load_bit()
        else:
            self.load_byte()

    def load_bit(self):      
        can_read = getattr(self.stream, 'read', None)

        value = None
        
        if(can_read != None):
            value = self.stream.read(1)
            value = int.from_bytes(value)
        else:
            value = self.stream.pop(0)

        self.convert_to_bin(value)

    def load_byte(self):
        value = self.stream[0:8]
        self.stream = self.stream[8:]
    
        self.convert_to_byte(value)
    
    def convert_to_bin(self, value):
        bit_repr = byte_to_bin(value)

        # pad the 0s to align to 8bits
        leading_zeroes =  [0] * (8 - len(bit_repr))
        self.buffer = leading_zeroes+bit_repr

    
    def convert_to_byte(self, value):

        trailing_zeros =  [0] * (8 - len(value))
        value = value + trailing_zeros
        self.trailing_zeros += len(trailing_zeros)

        out = bin_to_byte(value)

        self.buffer += [out]

    def get_bit(self):
        if(len(self.buffer) <= 0):
            self.load_bit()

        return self.buffer.pop(0)

    def get_byte(self):
        if(len(self.buffer) <= 0):
            self.load_byte()
        
        return self.buffer.pop(0)
    
    def eof(self):
        end_of_buffer = len(self.buffer) <= 0
        end_of_stream = len(self.stream) <= 0
        return end_of_buffer and end_of_stream


def test_bytearray():
    # byte array
    data = [65,2,64, 255] # abc, 8*3 = 24 bits
    byte_array = bytearray(data)

    bit_data = []
    bytes_to_bits = Stream(data)

    end = False    
    while(end is False):
        b = bytes_to_bits.get_bit()
        end = bytes_to_bits.eof()
        bit_data += [b]

    bits_to_bytes = Stream(bit_data, 1)
    
    end = False    
    while(end is False):
        print(bits_to_bytes.get_byte())
        end = bits_to_bytes.eof()

    
    
def test_normal():
    # normal ints
    data = [65,2,64] # abc, 8*3 = 24 bits

    bytes_to_bits = Stream(data)
    bit_data = []

    for k in range(0,24):
        b = bytes_to_bits.get_bit()
        bit_data += [b]

    bits_to_bytes = Stream(bit_data, 1)

    for k in range(0,3):
        print(bits_to_bytes.get_byte())


if __name__ == "__main__":
    #test_normal()
    test_bytearray()



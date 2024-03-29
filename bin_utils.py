import cv2
import numpy as np

def convert_to_bin(value, padding=8):
	bit_repr = []

	while(value > 0):
		remainder = value % 2
		value = value // 2
		bit_repr = bit_repr + [remainder]

	# pad the 0s to align to 8bits
	leading_zeroes =  [0] * (padding - len(bit_repr))
	return leading_zeroes + bit_repr[::-1]

def get_bin_repr(number):
	is_negative = number < 0
	number = abs(number)
	
	binary_repr = bin(number)[2::] # bin(int) give something like; 84 -> 0b1010111, so subtract the 0b from the repr

	bin_bit_arr = list(map(int,list(binary_repr)))

	size = len(bin_bit_arr) 

	if(is_negative):
		bin_bit_arr = [ abs(v-1) for v in bin_bit_arr]

	return (size,bin_bit_arr)

def bin_string_to_arr(binary_number):
        return list(map(int,list(binary_number)))

def int_to_bit_array(number, size=8):
        byte = [int(x) for x in format(number,'b')]

        padding_bytes = size - (len(byte) % size)   # Calculates the amount of padded bytes that will need

        if(padding_bytes == size):
                padding_bytes = 0
                
        padded_msg = [0] * padding_bytes + byte # np.concatenate((msg, np.zeros(padding_bytes, dtype=int)))   
        return padded_msg


# TODO: There is probably a better way to do this
# TODO: https://pypi.org/project/bitarray/ -> this is faster than this
def bit_array_to_int(bit_arr, with_negative=False):
        is_negative = False

        if(len(bit_arr) < 1):
                return 0

        if(with_negative is True and bit_arr[0] == 0 ):
                is_negative = True

                # 0 - 1 -> -1, abs(-1) -> 1
                # Cheap way to invert the binary ode
                bit_arr = [ abs(v-1) for v in bit_arr]

        reversed_bit_arr = bit_arr[::-1]
        bit_int = sum([ value * pow(2, count) for count, value in enumerate(reversed_bit_arr) ])

        return bit_int * -1 if is_negative else bit_int
if __name__ == '__main__':


	(size, bitarray) = get_bin_repr(-2)	
	assert bitarray == [0,1], f"expected {[1,0]}, got {bitarray}" 


	print(int_to_bit_array(8))
	print(convert_to_bin(8))
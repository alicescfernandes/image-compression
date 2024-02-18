# only encodes text

sample_histogram_2 = [(6, 55), (3, 32), (3, 13), (2, 0)]
sample_histogram_3 = [(6, 'a'), (3, 'b'), (3, 'c'), (2, 'd')]
sample_histogram_3 = [(1, 'a'), (1, 'b'), (1, 'c'), (1,'d'),(1,'e')]

from huffman_node import HuffmanNode
import numpy as np
import pprint
        
def gen_huff_table(histogram):
    priority_queue = [HuffmanNode(k[0], k[1]) for k in histogram]
    while len(priority_queue) > 1:
        priority_queue.sort(reverse=True)

        last_item = priority_queue.pop()    # Left
        prev_last_item = priority_queue.pop()    # Right

        new_item = prev_last_item.new_node_from_node(last_item)

        prev_last_item.update_bin_code(0) # updates left
        last_item.update_bin_code(1) # updates right

        new_item.insert(last_item) # adds right
        new_item.insert(prev_last_item) # adds left
        priority_queue.append(new_item)

    return priority_queue[0].get_bin_table()


if __name__ == '__main__':

    # Array of 16. Each index corresponds to the amount of codes with index+1 bits
    # index 0 -> amount of 1 bit codes
    # index 4 -> amount of 5 bit codes
    lengths = [0, 0, 7, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    elements = (4, 5, 3, 2, 6, 1, 0, 7, 8, 9, 10, 11)

    calculated_histogram = []
    pointer = 0
    for index,length in enumerate(lengths):
        symbols = elements[pointer:pointer+length]
        partial_hist = [(length, char, index+1) for char in symbols]
        calculated_histogram += partial_hist
        pointer += length
    
    dict_word = gen_huff_table(calculated_histogram)

    # test code. the symbol should have as many bits as required

    pp = pprint.PrettyPrinter(depth=20)
    pp.pprint(calculated_histogram)
    pp.pprint(dict_word)
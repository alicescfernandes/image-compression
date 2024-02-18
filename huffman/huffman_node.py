import numpy as np

class HuffmanNode:      
    def __init__(self, priority, value, depth=1):
        self.binCode = []
        self.value = value
        self.priority = priority
        self.depth = depth
        self.childNodes = []
        self.binCodeArray = []

    def __repr__(self):
        self_repr = f'Priority: {self.priority}, Value: {self.value}, Depth:{self.depth}, Bin:{self.binCode}'
        child_repr = ""
        child_repr = "".join(['\n\n' + str(k) for k in self.childNodes])

        return self_repr + child_repr + " |"

    def __lt__(self, other):
        return self.priority < other.priority

    def __add__(self, other):
        return self.priority + other.priority

    def insert(self, huffmanNode):
        self.childNodes.append(huffmanNode)

    def update_bin_code(self, binCode):
        if self.depth == 1:
            self.binCode += [binCode]
            self.binCodeArray.insert(0, binCode) # wip
        else: 
            for k in self.childNodes:
                k.update_bin_code(binCode)

    def join(self, other):
        return self.value + other.value

    def _get_bin_table(self, dictionary):
        if self.depth == 1:
            dictionary[self.value] = self.binCodeArray
        else:
            for k in self.childNodes:
                k._get_bin_table(dictionary)

        return dictionary

    # Calcula a tabela de huffman
    def get_bin_table(self):
        self._get_bin_table({})
        return self._get_bin_table({})

    def new_node_from_node(self, other):
        new_depth = self.depth + 1
        return HuffmanNode(self.priority + other.priority, self.join(other),
new_depth)


if __name__ == '__main__':
    node1 = HuffmanNode(1, 'node1')
    node2 = HuffmanNode(1, 'node2')
    node3 = HuffmanNode(1, 'node3')

    node1.insert(node2)
    node2.insert(node3)

    print(node3)
    

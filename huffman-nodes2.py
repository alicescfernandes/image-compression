import copy

class HuffmanNode:      
    def __init__(self, value, frequency, depth=1, childs = []):
        self.code = []
        self.val = value
        self.frequency = frequency
        self.depth = depth
        self.childs = childs

        for idx, k in enumerate(childs):
            self.childs[idx].update_code(idx)


    def __repr__(self):
        self_repr = f'({self.val},{self.code})'
        child_repr = "\n" + "".join([str(k) for k in self.childs])
        child_repr = "\n" + "".join([str(k) for k in self.childs])

        return self_repr + child_repr

    def __lt__(self, other):
        return self.frequency < other.frequency

    def __add__(self, other):
        return self.frequency + other.frequency

    def update_code(self,bit):
        if self.depth == 1:
            self.code = [bit] + self.code
        else: 
            for k in self.childs:
                k.update_code(bit)

    def increment_depth(self):
        self.depth+=1
    
    def _get_code_table(self, dictionary):
        if self.depth == 1:
            dictionary[self.val] = self.code
        else:
            for k in self.childs:
                k._get_code_table(dictionary)

        return dictionary
    
    def contains_code(self,val, arr):
        """ TODO """
        
    
class Huffman():
    def __init__(self, nodes):
        self.nodes = nodes
        self.order_nodes()
        self.current_node = None
        self.codes = {}
        self.root = None
    
        self.order_nodes()
        self._make_table()

    # Sort the nodes per frequency
    def order_nodes(self):
        self.nodes = sorted(self.nodes, key = lambda node: node.frequency)

    def _make_table(self):

        while(len(self.nodes) > 1):
            left = self.nodes.pop(0)
            right = self.nodes.pop(0)

            new_node = HuffmanNode(left.val+right.val, left+right, max(left.depth,right.depth)+1, [left,right])
            self.nodes.append(new_node)
            self.order_nodes()

        self.root = self.nodes[0]
        self.current_node = self.root
    
    def value_from_code(self, bit): # either 0 or 1
        next_node = self.current_node.childs[bit]

        if( next_node.depth > 1):   
            self.current_node = next_node
            return False

        val = next_node.val
        self.current_node = self.root
        return val

    def code_from_value(self, symbol, node = None): # either 0 or 1
        """ todo """
        print(self.root.contains_code('H', []))

    # Calcula a tabela de huffman
    def get_code_table(self):
        return self.root._get_code_table({})

def decode1():  
    data = [
        HuffmanNode("H", 1), 
        HuffmanNode("u", 1), 
        HuffmanNode("f", 2), 
        HuffmanNode("m", 1),
        HuffmanNode("a", 1),
        HuffmanNode("n", 1),
    ]
    

    hf = Huffman(data)
    print(hf.get_code_table())


    # Decode example   
    code = [1,0,0,1,0,1, 0,1,0,1,1,1,0,1,1,1, 0,0]
    string = []
    for k in code:
        val  = hf.value_from_code(k)
        if(val is not False):
            string.append(val)


    # Decode example n2   
    code = [1,0,0,1,0,1, 0,1,0,1,1,1,0,1,1,1, 0,0]
    string = []
    for k in code:
        val  = hf.value_from_code(k)
        if(val is not False):
            string.append(val)
    
    print(string)

if __name__ == "__main__":
    decode1()

    data = [
        HuffmanNode("H", 1), 
        HuffmanNode("u", 1), 
        HuffmanNode("f", 2), 
        HuffmanNode("m", 1),
        HuffmanNode("a", 1),
        HuffmanNode("n", 1),
    ]
    

    hf = Huffman(data)
    print(hf.get_code_table())
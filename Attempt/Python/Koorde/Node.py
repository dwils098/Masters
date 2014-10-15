# -*- coding: UTF-8 -*-

import hashlib
import time
import copy
from bitstring import BitArray, BitStream

k = 8
MAX = 2**k
bit_mask = BitArray('0x0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F')

class Node(object):
    def __init__ (self, node_id):
        
        self.id = BitArray(('0b' + node_id))
        #self.id = BitArray('0b'+ hex_2_binary(hashlib.sha1(node_id).hexdigest()))
        
        # This edge corresponds to, if current node is m, 2m mod 2^b
        # In other words consisting of left bit-wise shift and dropping the lower bit
        self.predecessor = None
        
        # This edge corresponds to, if the current node is m, 2m + 1 mod 2^b;
        # In other words consisting of left bit-wise shift and inserting 1 as the lower bit
        self.successor = None
        
        self.d = None


    def join (self, node):
        # if it is the first node to the Koorde DHT simply join itself
        if node == self:
            self.predecessor = self
            self.successor = self
            self.d = self
        else:
            print "------------------ JOIN ---------------------"
            # find a possible entry node
            print "Calling node = ", self.id.bin
            entry_node = node.find_successor(copy.deepcopy(self.id))
            print "Entry node :", entry_node.id.bin
            print "Node To Join: ", node.id.bin
            #print self.id.bin
            #entry_node.print_node()
            
            # insert yourself between that entry node and it predecessor
            self.successor = entry_node
            self.predecessor = entry_node.predecessor
            #print self.successor.id.bin
            #print self.predecessor.id.bin
            # update the two nodes for which youll be inserterd 
            # between to account for your arrival
            entry_node.predecessor.successor = self
            entry_node.predecessor = self
            
            # update your d pointer to account for 2m
            self.d = entry_node.find_successor((self.id << 1))
            
            # need a method to propagate the changes in the graph
            #self.updateOthers()
            print "----------------------- END OF JOIN -----------------------"
    def updateOthers(self):
        predecessor = self.predecessor.id + 1
        pred_node = predecessor >> 1
        #if (prede)
        
    
    def naive_lookup(self, key, shifted_key):
        
        if key == self.id:
            # then the caller node owns the looked up key
            print "FOUND THE KEY!"
            return self
        else:
            # shift to left
            temporary_node = Node('0')
            temporary_node.id = copy.deepcopy(self.id)
            
            
#            print "@------------------------@"
#            print "self: ",self.id.bin 
#            print "------------------------"
#            print "temp: ",temporary_node.id.bin 
#            print "------------------------"
#            print "key: ",key.id.bin
#            print "------------------------"
           
            # insert top bit of the key as being lowest bit of the temp_node ID
            # first shift the id
            temporary_node.id <<= 1
            # then write the value
#           print "@########################@"
#            print shifted_key.id[0]
#            print "@########################@"
            temporary_node.id.set(shifted_key[0], -1)
             
#            print "temp (A): ",temporary_node.id.bin 
#            print "@------------------------@"
            # shift the key (using a mask to simulate registers)
            shifted_key <<= 1

            # recursion
            temporary_node.naive_lookup(key, shifted_key)
            return self
            
            
             
             
    
    def find_successor(self, identifier):
        # as stated in the Chord paper, it is equivalent to asking the caller node to find
        # the predecessor of the id in parameters
        #successor = find_predecessor(identifier)
        
        #next hop
        next_node = copy.deepcopy(self)
        next_node.id <<= 1
        next_node.id.set(identifier[0], -1)
        
    
        succ = next_node.naive_lookup(identifier,identifier)
        
        print "<=== find_successor ===> "
        print "next_node: ", next_node.id.bin
        print "self: ", self.id.bin
        print "succ: ", succ.id.bin
        print "<=== end of find_successor ===>"
        
        #print succ.id
        #succ.print_node()
        return succ
    
    def find_predecessor(self, identifier):
        temp_node = copy.deepcopy(self)
        
        while(identifier != temp_node.id) or (identifier != temp_node.successor.id):
            temp_node
            
        
        
    def print_node (self):
        print "Node:"
        print "Id: ", self
        print "Id (binary): ", self.id.bin
        print "succ: ", self.successor.id.bin   
        print "predecessor: ", self.predecessor.id.bin
    
    

def hex_2_list_of_int (hex_string):
    int_list = []
    for char in hex_string:
        int_val = int(char, 16)
        int_list.append(int_val)
    print int_list
    
def hex_2_binary (hex_string):
    # the logic here is to parse an hexadecimal string one character at a time and concatenate the bytes
    binary_string = ""
    for char in hex_string:
        int_val = int(char, 16)    
        binary_val = format(int_val, '08b')
        binary_string += str(binary_val)
            
    return binary_string
    
def chunks(parse_string, n):
    
    # takes a string in and split it in chunks of size n
    b_list = []
    count = 0
    chunk = ""
    for elt in parse_string:
        if count < n :
            chunk += elt
            count += 1
        else:
            b_list.append(chunk)
            chunk = ""
            chunk += elt
            count = 1
    return b_list
    
def binary_2_hex (binary_string):
    
    #split string into byte sized strings
 
    byte_string = chunks(binary_string, 8)
    
    for elt in byte_string:
        int_val = int(elt, 2)
        hex_val = format(int_val, 'x')
        print hex_val,

    

node_1 = Node('00000001')
#node_1.print_node()

node_A  = Node('00010000')
node_B  = Node('01000000')
node_C  = Node('00001000')

key  = BitArray('0b00010010')
#print key.id
#node_A.naive_lookup(key,key)

node_A.join(node_A)
node_B.join(node_A)
node_C.join(node_A)

print "=== NODE A ==="
node_A.print_node()
print "=== NODE B ==="
node_B.print_node()
print "=== NODE C ==="
node_C.print_node()
from collections import namedtuple
import math
import numpy as np

class Node:

    def __init__(self, char):
        self.char = char
        self.left = None
        self.right = None
        self.nNodes = 1
    

    def get_position(self):
        return 1 + (self.left.nNodes if self.left else 0)
    

    def calculate_nNodes(self):
        self.nNodes = 1 # itself
        if self.left:
            self.nNodes += self.left.nNodes
        if self.right:
            self.nNodes += self.right.nNodes


    def update_left(self, left):
        self.left = left
        self.calculate_nNodes()
    

    def update_right(self, right):
        self.right = right
        self.calculate_nNodes()


    def update_left_right(self, left, right):
        self.left = left
        self.right = right
        self.calculate_nNodes()
    

    def remove_left(self):
        temp = self.left
        self.update_left(None)
        return temp


    def remove_right(self):
        temp = self.right
        self.update_right(None)
        return temp


class Pair:

    def __init__(self, first=None, second=None):
        self.first = first
        self.second = second


class Rope:

    def __init__(self):
        self.root = None
    

    def left_rotate(self, node):
        left_node = node
        node = node.right
        left_node.update_right(node.left)
        node.update_left(left_node)
        # left_node.right = node.left
        # node.left = left_node
        # left_node.nNodes = left_node.sum_of_nodes_of_sub_trees() + 1
        # node.nNodes = node.sum_of_nodes_of_sub_trees() + 1
        return node
    

    def right_rotate(self, node):
        right_node = node
        node = node.left
        right_node.update_left(node.right)
        node.update_right(right_node)
        # right_node.left = node.right
        # node.right = right_node
        # right_node.nNodes = right_node.sum_of_nodes_of_sub_trees() + 1
        # node.nNodes = node.sum_of_nodes_of_sub_trees() + 1
        return node


    def splay_util(self, node, index):

        if node == None:
            return node
        
        position = index + 1
        node_pos = node.get_position()
        # if position == node_pos:
        #     return node
        
        if position < node_pos:

            if node.left == None:
                return node

            node_pos = node.left.get_position()
            if position < node_pos:
                node.left.left = self.splay_util(node.left.left, index)
                node = self.right_rotate(node)
            elif position > node_pos:
                node.left.right = self.splay_util(node.left.right, index - node_pos)
                if node.left.right != None:
                    node.left = self.left_rotate(node.left) # we are rotating node.left so don't need to do nood.update_left() coz the same no of nodes will remain in the left side after rotating the left side
            
            if node.left != None:
                node = self.right_rotate(node)

        elif position > node_pos:

            if node.right == None:
                return node

            index -= node_pos
            position = index + 1
            node_pos = node.right.get_position()

            if position > node_pos:
                node.right.right = self.splay_util(node.right.right, index - node_pos)
                node = self.left_rotate(node)
            elif position < node_pos:
                node.right.left = self.splay_util(node.right.left, index)
                if node.right.left != None:
                    node.right = self.right_rotate(node.right)
            
            if node.right != None:
                node = self.left_rotate(node)

        return node  # position == node_pos  and reuturing after the if statement execution


    def splay(self, index):
        self.root = self.splay_util(self.root, index)


    def insert(self, char, index):
        
        if self.root == None:
            self.root = Node(char)
            return
        
        self.splay(index)

        position = index + 1
        node_pos = self.root.get_position()

        if position == node_pos:
            self.root.char = char  # return root
            return
        
        new_node = Node(char)
        if position < node_pos:
            # new_node.left = self.root.left
            # self.root.left = None
            # self.root.nNodes = self.root.sum_of_nodes_of_sub_trees() + 1
            # new_node.right = self.root
            left_node = self.root.remove_left()
            new_node.update_left_right(left_node, self.root)
        else:
            # new_node.right = self.root.right
            # self.root.right = None
            # self.root.nNodes = self.root.sum_of_nodes_of_sub_trees() + 1
            # new_node.left = self.root
            right_node = self.root.remove_right()
            new_node.update_left_right(self.root, right_node)
            
        # new_node.nNodes = new_node.sum_of_nodes_of_sub_trees() + 1
        self.root = new_node


    def split(self, node, index):

        if node == None:
            return Pair()
        
        position = index + 1
        node = self.splay_util(node, index)
        node_pos = node.get_position()

        # pair = Pair()
        if position <= node_pos:
            # pair.first = node.left
            # node.left = None
            # node.nNodes = node.sum_of_nodes_of_sub_trees() + 1
            # pair.second = node
            left_node = node.remove_left()
            pair = Pair(left_node, node)
        else:
            # pair.second = node.right
            # node.right = None
            # node.nNodes = node.sum_of_nodes_of_sub_trees() + 1
            # pair.first = node
            right_node = node.remove_right()
            pair = Pair(node, right_node)
        
        return pair


    def merge(self, left, right):
        if left == None:
            return right

        if right == None:
            return left

        # left = self.splay_util(left, math.inf)
        # node = left
        # node.right = right
        # node.nNodes = node.sum_of_nodes_of_sub_trees() + 1
        node = self.splay_util(left, math.inf-1)
        node.update_right(right)
        return node


    def cut(self, start, stop):

        pair1 = self.split(self.root, start)
        pair2 = self.split(pair1.second, stop - start) # + 1

        self.root = self.merge(pair1.first, pair2.second)
        node = pair2.first

        new_rope = Rope()
        new_rope.root = node

        return new_rope


    def paste(self, rope, index):
        if rope == None:
            return
        
        pair = self.split(self.root, index)

        pair.first = self.merge(pair.first, rope.root)
        self.root = self.merge(pair.first, pair.second)

        
    def inOrder(self, start, stop): # inclusive of start, exclusive of stop
        stack = []
        chars = []

        self.splay(start)
        if self.root.get_position()-1 < start:
            return ""

        n_chars = stop - start
        if n_chars == 0:
            return ""
        
        chars.append(self.root.char)
        len_chars = len(chars) # = 1
        curr = self.root.right
        
        while len_chars < n_chars and (len(stack) > 0 or curr != None):
            
            while curr != None:
                stack.append(curr)
                curr = curr.left
            
            curr = stack.pop()
            chars.append(curr.char)
            len_chars += 1
            curr = curr.right
        
        return chars

    def print_node(self, node): # inclusive of start, exclusive of stop
        stack = []
        chars = []
        
        curr = node
        while(len(stack) > 0 or curr != None):
            
            while curr != None:
                stack.append(curr)
                curr = curr.left
            
            curr = stack.pop()
            chars.append(curr.char)
            curr = curr.right
        
        print("".join(chars))

    # def search(self, index):
    #     self.splay(index)
    #     return self.root.char # return char # CHANGE THIS LATER
    # def get(self, index):
    #     self.splay(index)
    #     if index + 1 == self.root.get_position():
    #         return self.root.char
    #     else:
    #         return ""
        

    # def get(self, start, stop, step=1):
    #     chars = self.inOrder(start, stop)
    #     return "".join(chars[::step])
    def get(self, start, stop):
        chars = self.inOrder(start, stop)
        return "".join(chars)

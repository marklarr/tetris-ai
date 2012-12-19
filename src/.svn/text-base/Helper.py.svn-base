from tetris_tk import *
from copy import deepcopy


#Author: Zach O'Connor

# calculates coordinates of block if it were to rotate rot times

def calc_rotate( shape, rot ):
    blocks = []
    middle = shape.blocks[0]
    for block in shape.blocks:
        if rot == 0:
            x = block.x
            y = block.y
        elif rot == 1:
            x = middle.x - block.y + middle.y
            y = middle.y + block.x - middle.x
        elif rot == 2:
            x = 2*middle.x - block.x
            y = 2*middle.y - block.y
        elif rot == 3:
            x = middle.x + block.y - middle.y
            y = middle.y - block.x + middle.x
        blocks.append( (x, y) )
    return blocks

# returns manually determined values for the leftmost block in the given shape, if it hasn't been moved since spawning
def shape_left_side( shape, rot ):
    blocks = calc_rotate( shape, rot )
    left = 9
    for block in blocks:
        x = block[0]
        if x < left:
            left = x
    return left

# returns manually determined values for the rightmost block in the given shape, if it hasn't been moved since spawning
def shape_right_side( shape, rot ):
    blocks = calc_rotate( shape, rot )
    right = 0
    for block in blocks:
        x = block[0]
        if x > right:
            right = x
    return right

#uses shape_right_side and shape_left_side to determine the length of the shape horizontally
def shape_len( shape, rot ):
    return shape_right_side( shape, rot ) - shape_left_side( shape, rot ) + 1

# returns manually determined values for the bottom blocks in the given shape, as a list from left to right in the shape
def shape_bottom( shape, rot ):
    left = shape_left_side( shape, rot )
    l = shape_len( shape, rot )
    blocks = calc_rotate( shape, rot )
    bot = [0]*l
    for block in blocks:
        x, y = block
        if bot[x-left] < y:
            bot[x-left] = y
    return bot


def print_gridList(gridList): 
    r = ""
    for row in gridList:
        for x in row:
            if x == 0:
                r += "."
            else:
                r += "x"
        r += "\n"
    r += "\n"
    return r


#calculates the farthest a block could fall directly down in each column of the current board
def highest_legal_blocks( gridList ):
    highest_empty = [19]*10
    for i in range(10):
        for j in range(20):
            if gridList[j][i] == 1:
                highest_empty[i] = j-1
                break
    return highest_empty

#this object stores all information that is returned by the get_legal_moves operation
class Board_move( object ):
    def __init__( self, gridList, shape, dx, dy, rot ):
        self.gridList = deepcopy(gridList)
        self.shape = shape
        self.dx = dx
        self.dy = dy
        self.rot = rot


        blocks = calc_rotate( shape, rot )
        for block in blocks:
            x, y = block
            self.gridList[ y+dy ][ x+dx ] = 1	
	## some shapes don't seem to have the right dx values when rotates
	if shape.kind == "z" and rot == 1:
		self.dx = self.dx - 1	
	elif shape.kind == "s" and rot == 1:
		self.dx = self.dx + 1	
		
    def __repr__( self ):
        return "moved " + repr(type(self.shape)) + " by (dx, dy) = (" + str(self.dx) + ", " + str(self.dy) +") and rotated " + str(self.rot) + " times\n" + print_gridList(self.gridList)
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['shape']
        return state
            

#Main function in this file: calculates and returns all possible locations a block could be placed in the current board layout
def get_legal_moves( gridList, shape ):
    highest_empty = highest_legal_blocks( gridList )
    legal_moves = []
    for rot in range( shape.symmetry ):
        min_h = - shape_left_side( shape, rot )
        max_h = 9 - shape_right_side( shape, rot )
        bot = shape_bottom( shape, rot )
        for i in range( max_h - min_h + 1 ):
            falls = 20
            for j in range(len(bot)):
                dist = highest_empty[ i+j ] - bot[j]
                if dist < falls:
                    falls = dist
            legal_moves.append( Board_move(gridList, shape, i+min_h, falls, rot) )
    return legal_moves
           






#!/usr/bin/env python
"""
Tetris Tk - A tetris clone written in Python using the Tkinter GUI library.

Controls:
    Left Arrow      Move left
    Right Arrow     Move right
    Down Arrow      Move down
    Up Arrow        Drop Tetronimoe to the bottom
    'a'             Rotate anti-clockwise (to the left)
    's'             Rotate clockwise (to the right)
    'p'             Pause the game.
"""

from Tkinter import *
from time import sleep
from random import randint
import tkMessageBox
import sys
import os
import pickle
import copy

##AI is our written AI code ------ MARK LARSEN
import AI

SCALE = 35
OFFSET = 3
HEIGHT = 0
WIDTH = 0
MAXX = 10
MAXY = 20
BATCH_AMOUNT = 1
amount_played = 0
high_score = 0
total_score = 0
average = 0

NO_OF_LEVELS = 10

LEFT = "left"
RIGHT = "right"
DOWN = "down"

direction_d = { "left": (-1, 0), "right": (1, 0), "down": (0, 1) }

def level_thresholds( first_level, no_of_levels ):
    """
    Calculates the score at which the level will change, for n levels.
    """
    thresholds =[]
    for x in xrange( no_of_levels ):
        multiplier = 2**x

        thresholds.append( first_level * multiplier )
    
    return thresholds

class status_bar( Frame ):
    """
    Status bar to display the score and level
    """
    def __init__(self, parent):
        Frame.__init__( self, parent, width=WIDTH )
        self.label = Label( self, bd=1, relief=SUNKEN, anchor=W )
        self.label.pack( fill=X )
        
    def set( self, format, *args):
        self.label.config( text = format % args)
        self.label.update_idletasks()
        
    def clear( self ):
        self.label.config(test="")
        self.label.update_idletasks()

class Board( Frame ):
    """
    The board represents the tetris playing area. A grid of x by y blocks.
    """
    def __init__(self, parent, landed, scale=20, max_x=10, max_y=20, offset=3,):
        """
        Init and config the tetris board, default configuration:
        Scale (block size in pixels) = 20
        max X (in blocks) = 10
        max Y (in blocks) = 20
        offset (in pixels) = 3
        """
        Frame.__init__(self, parent)
	if landed == None:
		self.landed = {}
	else:	
		self.landed = landed
        
        # blocks are indexed by there corrdinates e.g. (4,5), these are
        self.parent = parent
        self.scale = scale
        self.max_x = max_x
        self.max_y = max_y
        self.offset = offset      

        ##create the 2d list, 10 long by 20 high
        self.gridList = []
        for x in range(self.max_y): #rows
                self.gridList.append( [0]*10 )
        self.canvas = Canvas(parent,
                             height= (max_y * scale) + offset,
                             width = (max_x * scale) + offset + 300)
	self.canvas.configure(highlightthickness=0)

        self.canvas.pack()
        
        ##MARK LARSEN, drawing frame.. or trying to. 
        #This is how it appears to work...
        #
        #self.canvas.create_rectangle(
        #            xstart, ystart, xend, yend, fill="color"
        #        )
        #
	##left side

	self.canvas.create_rectangle((max_x * scale)+offset, 0, 5000, 5000, fill="black")
        """self.canvas.create_rectangle(
            0, 0, 5, 520, fill="black"
        )
        #bottome edge
        self.canvas.create_rectangle(
            0, (max_y * scale)+offset -2, (max_x * scale)+offset, (max_y * scale)+offset + 5 / 20 * scale, fill="black"
        )
        #ridge side
        self.canvas.create_rectangle(
            (max_x * scale)+offset, 0, (max_x * scale)+offset + 5, (500 / 20) * scale, fill="black"
        )
	"""
    def check_for_complete_row( self, blocks ):
        """
        Look for a complete row of blocks, from the bottom up until the top row
        or until an empty row is reached.
        """
        rows_deleted = 0
        
        # Add the blocks to those in the grid that have already 'landed'
        for block in blocks:
            self.landed[ block.coord() ] = block.id
            ##add to our 2d matrix -- MARK LARSEN
            self.gridList[block.y][block.x] = 1
        
        empty_row = 0

        # find the first empty row
        for y in xrange(self.max_y -1, -1, -1):
            row_is_empty = True
            for x in xrange(self.max_x):
                if self.landed.get((x,y), None):
                    row_is_empty = False
                    break;
            if row_is_empty:
                empty_row = y
                break

        # Now scan up (from bottom line to first empty row) until a complete row is found. 
        y = self.max_y - 1
        while y > empty_row:
 
            complete_row = True
            for x in xrange(self.max_x):
                if self.landed.get((x,y), None) is None:
                    complete_row = False
                    break;

            if complete_row:
                rows_deleted += 1
                
                #delete the completed row
                for x in xrange(self.max_x):
                    block = self.landed.pop((x,y))
                    self.delete_block(block)
                    del block
		##deleting completed row of gridList
                self.gridList[y] = [0]*10
                    
                # move all the rows above it down
                for ay in xrange(y-1, empty_row, -1):
                    self.gridList[ay+1 ] = self.gridList[ay ]
                    for x in xrange(self.max_x):
                        block = self.landed.get((x,ay), None)
                        if block:
                            block = self.landed.pop((x,ay))
                            dx,dy = direction_d[DOWN]
                            
                            self.move_block(block, direction_d[DOWN])
                            self.landed[(x+dx, ay+dy)] = block

                # move the empty row down index down too
                empty_row +=1
		       #make sure this row is empty
                self.gridList[empty_row] = [0] * 10
                # y stays same as row above has moved down.
                
            else:
                y -= 1
                
        #self.output() # non-gui diagnostic
        
        # return the score, calculated by the number of rows deleted.        
        return (100 * rows_deleted) * rows_deleted
                
    def output( self ):
        for y in xrange(self.max_y):
            line = []
            for x in xrange(self.max_x):
                if self.landed.get((x,y), None):
                    line.append("X")
                else:
                    line.append(".")
            print "".join(line)
            
    def add_block( self, (x, y), colour):
        """
        Create a block by drawing it on the canvas, return
        it's ID to the caller.
        """
        rx = (x * self.scale) + self.offset
        ry = (y * self.scale) + self.offset
        
        return self.canvas.create_rectangle(
            rx, ry, rx+self.scale, ry+self.scale, fill=colour
        )
        
    def move_block( self, id, coord):
        """
        Move the block, identified by 'id', by x and y. Note this is a
        relative movement, e.g. move 10, 10 means move 10 pixels right and
        10 pixels down NOT move to position 10,10. 
        """
        x, y = coord
        self.canvas.move(id, x*self.scale, y*self.scale)
        
    def delete_block(self, id):
        """
        Delete the identified block
        """
        self.canvas.delete( id )
        
    def check_block( self, (x, y) ):
        """
        Check if the x, y coordinate can have a block placed there.
        That is; if there is a 'landed' block there or it is outside the
        board boundary, then return False, otherwise return true.
        """
        if x < 0 or x >= self.max_x or y < 0 or y >= self.max_y:
            return False
        elif self.landed.has_key( (x, y) ):
            return False
        else:
            return True



class Block(object):
    def __init__( self, id, (x, y)):
        self.id = id
        self.x = x
        self.y = y
        
    def coord( self ):
        return (self.x, self.y)
        
class Shape(object):
    """
    Shape is the  Base class for the game pieces e.g. square, T, S, Z, L,
    reverse L and I. Shapes are constructed of blocks. 
    """
    @classmethod        
    def check_and_create(cls, board, coords, colour ):
        """
        Check if the blocks that make the shape can be placed in empty coords
        before creating and returning the shape instance. Otherwise, return
        None.
        """
        for coord in coords:
            if not board.check_block( coord ):
                return None
        
        return cls( board, coords, colour)
    @classmethod
    def check_and_create_next(cls, board, coords, colour ):
        return cls( board, coords, colour)
    @classmethod
    def check_and_create_fake(cls, board, coords, colour):
        """
	Makes a fake block that shows up nowhere in the screen. Mark Larsen.
        """        
        return cls( board, coords, colour, True)
    def __init__(self, board, coords, colour, fake=False ):
        """
        Initialise the Shape base.
        """
        self.board = board
        self.blocks = []
        
        for coord in coords:
	    block = None
            if fake == False:
	            block = Block(self.board.add_block( coord, colour), coord)
            else:
		block = Block(None, coord)
            self.blocks.append( block )
            
    def move( self, direction ):
        """
        Move the blocks in the direction indicated by adding (dx, dy) to the
        current block coordinates
        """
        d_x, d_y = direction_d[direction]
        
        for block in self.blocks:


            x = block.x + d_x
            y = block.y + d_y
            
            if not self.board.check_block( (x, y) ):
                return False
            
        for block in self.blocks:
            
            x = block.x + d_x
            y = block.y + d_y
            
            self.board.move_block( block.id, (d_x, d_y) )
            
            block.x = x
            block.y = y
        
        return True
            
    def rotate(self, clockwise = True):
        """
        Rotate the blocks around the 'middle' block, 90-degrees. The
        middle block is always the index 0 block in the list of blocks
        that make up a shape.
        """
        # TO DO: Refactor for DRY
        middle = self.blocks[0]
        rel = []
        for block in self.blocks:
            rel.append( (block.x-middle.x, block.y-middle.y ) )

        # to rotate 90-degrees (x,y) = (-y, x)
        # First check that the there are no collisions or out of bounds moves.
        for idx in range(len(self.blocks)):
            rel_x, rel_y = rel[idx]
            if clockwise:
                x = middle.x+rel_y
                y = middle.y-rel_x
            else:
                x = middle.x-rel_y
                y = middle.y+rel_x
            
            if not self.board.check_block( (x, y) ):
                return False
            
        for idx in range(len(self.blocks)):
            rel_x, rel_y = rel[idx]
            if clockwise:
                x = middle.x+rel_y
                y = middle.y-rel_x
            else:
                x = middle.x-rel_y
                y = middle.y+rel_x
            
            
            diff_x = x - self.blocks[idx].x
            diff_y = y - self.blocks[idx].y
            
            self.board.move_block( self.blocks[idx].id, (diff_x, diff_y) )

            self.blocks[idx].x = x
            self.blocks[idx].y = y
           
        return True
    
class Shape_limited_rotate( Shape ):
    """
    This is a base class for the shapes like the S, Z and I that don't fully
    rotate (which would result in the shape moving *up* one block on a 180).
    Instead they toggle between 90 degrees clockwise and then back 90 degrees
    anti-clockwise.
    """
    def __init__( self, board, coords, colour, fake=False ):
        self.clockwise = True
        super(Shape_limited_rotate, self).__init__(board, coords, colour, fake)
    
    def rotate(self, clockwise=True):
        """
        Clockwise, is used to indicate if the shape should rotate clockwise
        or back again anti-clockwise. It is toggled.
        """
        super(Shape_limited_rotate, self).rotate(clockwise=self.clockwise)
        if self.clockwise:
            self.clockwise=False
        else:
            self.clockwise=True
        

class square_shape( Shape ):
    symmetry = 1
    kind = "square"
    @classmethod
    def check_and_create( cls, board ):
        coords = [(4,0),(5,0),(4,1),(5,1)]
        return super(square_shape, cls).check_and_create(board, coords, "red")
    @classmethod
    def check_and_create_next(cls, board ):
        coords = [(14,0),(15,0),(14,1),(15,1)]
        return super(square_shape, cls).check_and_create_next(board, coords, "red")
    @classmethod
    def check_and_create_fake(cls):
        coords = [(4,0),(5,0),(4,1),(5,1)]
	return super(square_shape, cls).check_and_create_fake(None, coords, "red")
    def rotate(self, clockwise=True):
        """
        Override the rotate method for the square shape to do exactly nothing!
        """
        pass
        
class t_shape( Shape ):
    kind = "t"
    symmetry = 4
    @classmethod
    def check_and_create( cls, board ):
        coords = [(4,0),(3,0),(5,0),(4,1)]
        return super(t_shape, cls).check_and_create(board, coords, "yellow" )
    @classmethod
    def check_and_create_next( cls, board ):
        coords = [(14,0),(13,0),(15,0),(14,1)]
        return super(t_shape, cls).check_and_create_next(board, coords, "yellow" )
    @classmethod
    def check_and_create_fake(cls):
        coords = [(4,0),(3,0),(5,0),(4,1)]
	return super(t_shape, cls).check_and_create_fake(None, coords, "yellow")
        
class l_shape( Shape ):
    kind = "l"
    symmetry = 4
    @classmethod
    def check_and_create( cls, board ):
        coords = [(4,0),(3,0),(5,0),(3,1)]
        return super(l_shape, cls).check_and_create(board, coords, "orange")
    @classmethod
    def check_and_create_next( cls, board ):
        coords = [(14,0),(13,0),(15,0),(13,1)]
        return super(l_shape, cls).check_and_create_next(board, coords, "orange")
    @classmethod
    def check_and_create_fake(cls):
        coords = [(4,0),(3,0),(5,0),(3,1)]
	return super(l_shape, cls).check_and_create_fake(None, coords, "orange")
        
class reverse_l_shape( Shape ):
    symmetry = 4
    kind = "reverse_l"
    @classmethod
    def check_and_create( cls, board ):
        coords = [(5,0),(4,0),(6,0),(6,1)]
        return super(reverse_l_shape, cls).check_and_create(
            board, coords, "green")
    @classmethod
    def check_and_create_next( cls, board ):
        coords = [(15,0),(14,0),(16,0),(16,1)]
        return super(reverse_l_shape, cls).check_and_create_next(
            board, coords, "green")
    @classmethod
    def check_and_create_fake(cls):
        coords = [(5,0),(4,0),(6,0),(6,1)]
	return super(reverse_l_shape, cls).check_and_create_fake(None, coords, "green")

class z_shape( Shape_limited_rotate ):
    symmetry = 2
    kind = "z"
    @classmethod
    def check_and_create( cls, board ):
        coords =[(5,0),(4,0),(5,1),(6,1)]
        return super(z_shape, cls).check_and_create(board, coords, "purple")
    @classmethod
    def check_and_create_next( cls, board ):
        coords =[(15,0),(14,0),(15,1),(16,1)]
        return super(z_shape, cls).check_and_create_next(board, coords, "purple")
    @classmethod
    def check_and_create_fake(cls):
        coords =[(5,0),(4,0),(5,1),(6,1)]
	return super(z_shape, cls).check_and_create_fake(None, coords, "purple")

                
class s_shape( Shape_limited_rotate ):
    kind = "s"
    symmetry = 2
    @classmethod
    def check_and_create( cls, board ):
        coords =[(5,1),(4,1),(5,0),(6,0)]
        return super(s_shape, cls).check_and_create(board, coords, "magenta")
    @classmethod
    def check_and_create_next( cls, board ):

        coords =[(15,1),(14,1),(15,0),(16,0)]
        return super(s_shape, cls).check_and_create_next(board, coords, "magenta")
    @classmethod
    def check_and_create_fake(cls):
        coords =[(5,1),(4,1),(5,0),(6,0)]
	return super(s_shape, cls).check_and_create_fake(None, coords, "magenta")
                
class i_shape( Shape_limited_rotate ):
    kind = "i"
    symmetry = 2
    @classmethod
    def check_and_create( cls, board ):
        coords =[(4,0),(3,0),(5,0),(6,0)]
        return super(i_shape, cls).check_and_create(board, coords, "blue")
    @classmethod
    def check_and_create_next( cls, board ):
        coords =[(14,0),(13,0),(15,0),(16,0)]
        return super(i_shape, cls).check_and_create_next(board, coords, "blue")
    @classmethod
    def check_and_create_fake(cls):
        coords =[(4,0),(3,0),(5,0),(6,0)]
	return super(i_shape, cls).check_and_create_fake(None, coords, "blue")

class fly_shape( Shape_limited_rotate ):
    kind = "fly"
    symmetry = 4
    @classmethod
    def check_and_create_fake(cls):
        coords =[(4,0),(3,0),(5,0),(6,0),(4,1),(5,1)]
	return super(fly_shape, cls).check_and_create_fake(None, coords, "blue")

class longT_shape( Shape_limited_rotate ):
    kind = "longT"
    symmetry = 4
    @classmethod
    def check_and_create_fake(cls):
        coords =[(4,0),(3,0),(5,0),(4,1),(4,2)]
	return super(longT_shape, cls).check_and_create_fake(None, coords, "blue")
        
class game_controller(object):
    """
    Main game loop and receives GUI callback events for keypresses etc...
    """
    def __init__(self, parent, landed):
        """
        Intialise the game...
        """
        self.parent = parent
        self.lose = False

        self.score = 0
        self.level = 0
	if BATCH_AMOUNT > 1:
		self.delay = 10#batch mode
	else:
		self.delay = 10    #ms
        
        #lookup table
        self.shapes = [square_shape,
                      t_shape,
                      l_shape,
                      reverse_l_shape,
                      z_shape,
                      s_shape,
                      i_shape ]
        
        self.thresholds = level_thresholds( 500, NO_OF_LEVELS )
        
        self.status_bar = status_bar( parent )
        self.status_bar.pack(side=TOP,fill=X)
        #print "Status bar width",self.status_bar.cget("width")
	print self.score
        self.status_bar.set("Rows Cleared: %d\t Level: %d \t Round: %d \t Avg: %d \t Highest: %d" % (
	    self.score / 100, self.level+1, amount_played + 1, average, high_score / 100)
        )
        
        self.board = Board(
            parent,
	    landed,
            scale=SCALE,
            max_x=MAXX,
            max_y=MAXY,
            offset=OFFSET
            )
	##load in previous game
	if self.board.landed != None:
		newlanded = copy.deepcopy(self.board.landed)
		for key, value in self.board.landed.iteritems():
			print value
			self.board.landed[key] = Block(self.board.add_block( key, "blue"), key ).id
		for key, value in self.board.landed.iteritems():
			print value
		#self.board.landed = newlanded
        
        self.board.pack(side=BOTTOM)
        
	self.parent.bind("p", self.p_callback)
        self.parent.bind("f", self.f_callback)
        self.parent.bind("<Up>", self.faster)
        self.parent.bind("<Down>", self.slower)
        #DISABLE KEY EVENT HANDLERS  ---- MARK LARSEN
        if len(sys.argv) > 1 and sys.argv[1] == 'human':
                self.parent.bind("<Left>", self.left_callback)
                self.parent.bind("<Right>", self.right_callback)
                self.parent.bind("<Up>", self.up_callback)
                self.parent.bind("<Down>", self.down_callback)
                self.parent.bind("a", self.a_callback)
                self.parent.bind("s", self.s_callback)
        #MAKE AI INSTEAD
	self.shapes = [square_shape, t_shape, l_shape, reverse_l_shape, z_shape, s_shape, i_shape ]
	self.badshapes = [fly_shape, longT_shape, square_shape]
	if sys.argv[1] == 'GBFS':
	        self.ai = AI.GBFS(self)
        elif sys.argv[1] == 'DLBFS':
	        self.ai = AI.DLBFS(self)
        elif sys.argv[1] == 'minimax1':
	        self.ai = AI.Minimax1(self)
		self.ai.shapeList = self.shapes
        elif sys.argv[1] == 'minimax2':
	        self.ai = AI.Minimax2(self)
		self.ai.shapeList = self.shapes
        elif sys.argv[1] == 'frankenminimax1':
	        self.ai = AI.Minimax1(self)
		self.ai.shapeList = self.badshapes
        elif sys.argv[1] == 'frankenminimax2':
	        self.ai = AI.Minimax2(self)
		self.ai.shapeList = self.badshapes        
        self.shape = self.get_next_shape()
        ##MARK LARSEN, store a class variable that holds the next shape.
        ##since get_next_shape() actually handled the drawing for the shape too, we should make a separate method for the self.nextShape that draws the piece off to the side of the grid. Get_next_shape() draws it at the top of the grid.
        ##We'll also need to update this class variable in the handle_move function where the piece meets the bottom and a the next piece starts to come.
        self.nextShape = self.get_next_next_shape() 
        self.board.output()

        self.after_id = self.parent.after( self.delay, self.move_my_shape )
        
        ##make the first move
        self.ai.make_and_time_move( self.board.gridList, self.shape, self.nextShape, first=True );

    def handle_move(self, direction):
        #if you can't move then you've hit something
        if not self.shape.move( direction ):
            
            # if your heading down then the shape has 'landed'
            if direction == DOWN:
                self.score += self.board.check_for_complete_row(
                    self.shape.blocks
                    )
                del self.shape


                #MARK LARSEN
                ##swap in 'next piece' for current piece, delete the old next-piece drawing ,then draw the current piece
                for b in self.nextShape.blocks:
                        self.board.delete_block(b.id)
                self.shape = self.nextShape
                self.nextShape = self.get_next_next_shape()
                self.shape = self.shape.check_and_create(self.board)

        
                
                # If the shape returned is None, then this indicates that
                # that the check before creating it failed and the
                # game is over!
                if self.shape is None:
                	self.lose = True
			global high_score
			global total_score
			global amount_played
			global average
			if self.score > high_score:
				high_score = self.score
			total_score += self.score
			amount_played = amount_played + 1
			average = (total_score / amount_played) / 100
			if BATCH_AMOUNT <= amount_played:		
		            tkMessageBox.showwarning(
		                title="Batch Run Finished for "+ sys.argv[1],
		                message ="Total Runs: %d\nAvg: %d\n Highest: %d " % (
		                    amount_played, average, high_score / 100),
		                parent=self.parent
		                )
			    Toplevel().destroy()
			    self.parent.destroy()
			    sys.exit(0)
                	#self.parent.destroy()

			start()			

                
                # do we go up a level?
                if (self.level < NO_OF_LEVELS and 
                    self.score >= self.thresholds[ self.level]):
                    self.level+=1
                    ##SET DELAY AT BEGINNING, IT'S CONSTANT ----MARK LARSEN
                    #self.delay-=100
                print self.score
                self.status_bar.set("Rows Cleared: %d\t Level: %d \t Round: %d \t Avg: %d \t Highest: %d" % (
		    self.score / 100, self.level+1, amount_played + 1, average, high_score / 100)
                )
         
                # make next move
                self.ai.make_and_time_move(self.board.gridList, self.shape, self.nextShape )
                
                # Signal that the shape has 'landed'
                return False
        return True

    def left_callback( self, event ):
        if self.shape:
            self.handle_move( LEFT )
        
    def right_callback( self, event ):
        if self.shape:
            self.handle_move( RIGHT )

    def up_callback( self, event ):
        if self.shape:
            # drop the tetrominoe to the bottom
            while self.handle_move( DOWN ):
                pass

    def down_callback( self, event ):
        if self.shape:
            self.handle_move( DOWN )
            
    def a_callback( self, event):
        if self.shape:
            self.shape.rotate(clockwise=True)
            
    def s_callback( self, event):
        if self.shape:
            self.shape.rotate(clockwise=False)
        
    def p_callback(self, event):
        self.parent.after_cancel( self.after_id )
        tkMessageBox.askquestion(
            title = "Paused!",
            message="Continue?",
            type=tkMessageBox.OK)
        self.after_id = self.parent.after( self.delay, self.move_my_shape )
    
    def f_callback( self, event ):
                if self.delay == 100:
                        self.delay = 2500
                else:
                        self.delay = 100
    def faster(self, event):
	if self.delay > 0:
		self.delay = self.delay - 10

    def slower(self, event):
	self.delay = self.delay + 10
    def move_my_shape( self ):
        if self.shape:
            self.handle_move( DOWN )
            self.after_id = self.parent.after( self.delay, self.move_my_shape )
        
    def get_next_shape( self ):
        """
        Randomly select which tetrominoe will be used next.
        """
        the_shape = self.shapes[ randint(0,len(self.shapes)-1) ]
        return the_shape.check_and_create(self.board)

    def get_next_next_shape(self):
        the_shape = self.shapes[ randint(0,len(self.shapes)-1) ]
        return the_shape.check_and_create_next(self.board)
        
def start(landed=None):
	global BATCH_AMOUNT
	if len(sys.argv) > 2:
 		BATCH_AMOUNT = int(sys.argv[2])
	root = Tk()
	root.configure(highlightthickness=0)
	global HEIGHT, WIDTH
	root.title(sys.argv[1])
	root.config(bg="red") 
	w, h = root.winfo_screenwidth(), root.winfo_screenheight()
	HEIGHT = h
	WIDTH = w	
	root.overrideredirect(1)
	root.geometry("%dx%d+0+0" % (w, h))
	theGame = game_controller( root, landed )
	root.mainloop()
if __name__ == "__main__":
    start()



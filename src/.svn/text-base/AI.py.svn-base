from Helper import *
from tetris_tk import *
from tree import *
import resource
from multiprocessing import Process, Queue
import time
from datetime import datetime
import threading

#'superclass' type object for all of our AI classes
class AI:
    #Constructor, whenever you see "self," you don't actually pass that parameter in. 
    #It's just a reference to this instance of AI. 
    def __init__(self, game_controller):
        self.game_controller = game_controller
	self.totalTime = datetime.now() - datetime.now()
	self.movesMade = 0
	self.shapes = [square_shape, t_shape, l_shape, reverse_l_shape, z_shape, s_shape, i_shape ]
	self.badshapes = [fly_shape, longT_shape, square_shape]
    def translateAndRotatePiece(self, best):
        #self.game_controller.p_callback(None)
        # now that we have selected our move, give instructions to the
	## we actually need to rotate before we shift, otherwise the boundaries will prevent some pieces from shifting where they need to go -- MARK L 
        if best.rot > 0:
            #except for the square piece, any piece rotated on the top row will 
            #move at least one block into the -2 row. Thus, move the piece 
            #down a row before rotating
            self.game_controller.down_callback(None)
            self.game_controller.down_callback(None)
            self.game_controller.down_callback(None)
            for r in range(best.rot):
                self.game_controller.s_callback(None)
        # game_controller to move the tetrominoe
        if best.dx < 0:
            for shift in range(-best.dx):
                self.game_controller.left_callback(None)
        else:
            for shift in range(best.dx):
                self.game_controller.right_callback(None)

    # a lower heuristic weight indicates a better result
    def heuristic(self, move):
        highest_empty = highest_legal_blocks( move.gridList )
        max_y = 20-min(highest_empty) ## highest block on the board
        max_ys = [20-y for y in highest_empty]

        blank_blocks = 0
        score = 0
        ##look at each landed block
	blank_chain = 0
        for j in range(10):
            for i in range( highest_empty[j]+2, 20 ):
                if move.gridList[i][j] == 0:
                    blank_blocks = blank_blocks+1
		    blank_chain = blank_chain + 1
		    if blank_chain > 5:
			blank_chain = 0
			break
	##see if there are any rows with all blocks (going to be cleared). If so, decrement max y and max y's
	clearedLines = 20 ##start with this, decrement each time a line isnt full
	for j in range(20):
		for i in range(10):
			if move.gridList[j][i] == 0:
				##not a full line
				clearedLines = clearedLines - 1
				break
	max_y -= clearedLines
	for idx in range(len(max_ys)):
		max_ys[idx] -= clearedLines
				
	##figure out how much the max_ys deviate, and what the min_y is
	max_y_equilibrium = 0
	min_y = float("inf") ## lowest row on the board. if rows are equal, add them together
	min_y_repitition = 0 ##used for multiple rows having equal min_y
	for y in  max_ys:
		if y < min_y:
			min_y = y
			min_y_repitition = 0
		elif y == min_y:
			min_y_repitition = min_y_repitition + 1
		deviation = max_y - y
		max_y_equilibrium += deviation
	## we want to keep wells under three pieces long (i piece would be required to fill it if larger than three)
	wells_length_cumulative = 0
	startCounting = False
	for j in range(10):
		for i in range(20):
			if j > 0 and j < 9:
				if move.gridList[i][j-1] == 1 and move.gridList[i][j+1] == 1: #somewhere in the middle
					startCounting = True
			elif j == 0:
				if move.gridList[i][j+1] == 1:
					startCounting = True
			else: 
				if move.gridList[i][j-1] == 1: #right wall case
					startCounting = True
			if move.gridList[i][j] == 1:
				##well is over
				count = 0
				startCounting = False
				break
			elif startCounting == True:
				wells_length_cumulative = wells_length_cumulative + 1
	
        ##set weights
        blank_block_weight = 15
	cleared_lines_weight = 8
        max_ys_weight = 5
        max_y_weight = 1
	max_y_equilibrium_weight = 0
	min_y_weight = 0
	min_y_repitition_weight = 0
	wells_weight = 10
	## don't lose
	if max_y >= 15:
		max_y_weight = 100
        #compute hueristic
        score = max_y_weight * (max_y **2)
        score += max_ys_weight * sum(i**1 for i in max_ys)
        score += blank_block_weight * (blank_blocks **1)
	score += max_y_equilibrium_weight * max_y_equilibrium
	score += min_y_weight * min_y
	score += min_y_repitition_weight + min_y_repitition
	score += wells_length_cumulative * wells_weight
	score += cleared_lines_weight * clearedLines
        return score
    def make_and_time_move(self,gridList, shape, nextShape, first=False):
	time = datetime.now()
	self.makeMove(gridList, shape, nextShape)
	self.totalTime += datetime.now() - time
	self.movesMade = self.movesMade + 1
	print "average time taken" +  str(self.totalTime / self.movesMade)
	 

    def make_first_move(self, gridList, shape):
        if shape.kind == "square":
            return Board_move( gridList, shape, -4, 18, 0 )
        if shape.kind == "i":
            return Board_move( gridList, shape, -3, 19, 0 )
        if shape.kind == "s":
            return Board_move( gridList, shape, -4, 18, 0 )
        if shape.kind == "z":
            return Board_move( gridList, shape, 3, 18, 0 )
        if shape.kind =="l":
            return Board_move( gridList, shape, 4, 18, 2 )
        if shape.kind == "reverse_l":
            return Board_move( gridList, shape, -4, 18, 2 )
        if shape.kind == "t":
            return Board_move( gridList, shape, -3, 18, 2 )


#inherits from AI superclass
class stupid_ai(AI):
    def makeMove( self, gridList, shape, nextShape, first=False ):
        ##just moves every piece over 3 times to the left... stupid ai :)
        self.game_controller.left_callback(None)
        self.game_controller.left_callback(None)
        self.game_controller.left_callback(None)
        # gridList is a 2d array, 20 x 10 array that has either a 0 
        # or 1 if a block is not present or is.
        # indexing starts with (0,0) being the top left hand corner

class GBFS(AI):
    title = "GBFS"
    def makeMove( self, gridList, shape, nextShape, first=False ):
        if first:
            best = self.make_first_move( [row[:] for row in gridList], shape )
        else:
            #board list is the list of legal moves
            board_list = get_legal_moves( gridList, shape )
            best = board_list[0]
            best_score = self.heuristic( best )
            for x in range(1, len( board_list )):
                next = board_list[x]
                next_score = self.heuristic( next )
                if next_score < best_score:
                    best_score = next_score
                    best = next
	self.translateAndRotatePiece(best)

class DLBFS(AI):
	title = "DLBFS"
	def makeMove(self,gridList, shape, nextShape, first=False):
		board_list = get_legal_moves(gridList, shape)
		self.shape = shape
		self.nextShape = nextShape
		##use multiple threads to search
		queue1 = Queue() #create a queue object

		length = len(board_list)
		best = self.createAndScanTree(board_list, 0, length, queue1)
		"""job1 = Process(target=self.createAndScanTree, args=(board_list,0, length/4, queue1,))
		job2 = Process(target=self.createAndScanTree, args=(board_list,length/4, length/2 , queue1,))
		job3 = Process(target=self.createAndScanTree, args=(board_list,length/2, int(length * (3.0/4.0)) , queue1,))
		job4 = Process(target=self.createAndScanTree, args=(board_list,int(length * (3.0/4.0)), length , queue1,))

		# Compute and retrieve answers for the jobs.
		job1.start()
		job2.start()
		job3.start()
		job4.start()
		#job1.join() 
		#job2.join() ##joins arent working...
		bests = [None,None,None,None]
		while bests[0] == None:		
			bests[0] = queue1.get()
		while bests[1] == None:		
			bests[1] = queue1.get()
		while bests[2] == None:		
			bests[2] = queue1.get()
		while bests[3] == None:		
			bests[3] = queue1.get()

		bestScore = float("inf")
 		best = None
		for node in bests:
			if node.heuristic < bestScore:
				bestScore = node.heuristic
				best = node
		"""


		self.translateAndRotatePiece(best.data)
	def createAndScanTree(self,board_list, bottom_bound, top_bound,queue):
		board_list = board_list[bottom_bound:top_bound]
		##create a tree
		root = Node()
		nodesAtDepth = [[],[],[]]
		nodesAtDepth[0].append(root)
		for board in board_list:
			child = Node()
			nodesAtDepth[1].append(child)
			root.children.append(child)
			child.depth = 1
			child.data = board
			child.parent = root
			##create children for this child
			legal_children = get_legal_moves(child.data.gridList, type(self.nextShape).check_and_create_fake())
			for board in legal_children:
				childOfChild = Node()
				nodesAtDepth[2].append(childOfChild)
				child.children.append(childOfChild)
				childOfChild.depth = 1
				childOfChild.data = board
				childOfChild.parent = child
				childOfChild.heuristic = self.heuristic(childOfChild.data)
		##find the best node at depth of 2
		bestScore = float("inf")
		best = None
		#print "bottom_bound" + str(bottom_bound)
		#print "top_bound" + str(top_bound)
		#print "length" + str(len(board_list))
		for node in nodesAtDepth[2]:
			if node.heuristic < bestScore:
				bestScore = node.heuristic
				best = node
		queue.put(best.parent)
		#print bestScore
		return best.parent
		
		
	
		

class Minimax1(AI):

    def makeMove(self, gridList, shape, nextShape, first=False):
        root = Node();
        self.MAX = 1 ##constants for min, max of a depth
        self.MIN = 0
        self.MAX_DEPTH = 2
        self.nodesAtDepth = [] ##list that stores lists of all of the nodes at a given depth. ie, nodeAtDepth[MAX_DEPTH] = all of the leaves
        self.nodesAtDepth.append([root]);
        self.nodesAtDepth.append([])
	move_list = get_legal_moves(gridList, shape)
        ##build first generation of the tree, representing the move for the next piece (which we know)
	dt = datetime.now()
        threadLock = threading.Lock()
        threads = []
        n = 1
        for grid in move_list:
            #firstGenChild = Node()
            #firstGenChild.data = grid
            #firstGenChild.depth = 1;
            #firstGenChild.parent = root;
            #root.children.append(firstGenChild)
            #self.buildMinimaxRound(firstGenChild, 2)
            #self.nodesAtDepth[1].append(firstGenChild)
            
            self.buildMinimaxTree(grid, root)

            ###lines for multithreading (works but no obvious speed boost)
            """thread = buildTreeThread(n, grid, root, self.nodesAtDepth)
            thread.start()
            threads.append(thread)
            n = n + 1
        for t in threads:
            t.join()"""
        ###tree is done
	#print "time taken to build minimax: "+ str(datetime.now() - dt)
	dt = datetime.now()
        for depth in range( 0, self.MAX_DEPTH - 1):
            depth = self.MAX_DEPTH - depth#go from bottom up, descending 
            maxNodes = self.nodesAtDepth[depth][self.MAX]
            minNodes = self.nodesAtDepth[depth][self.MIN]
            ##find max value for maxNodes (our move)
            maxScore = float("inf")
            currentParent = maxNodes[0].parent
            for maxNode in maxNodes:
                if currentParent != maxNode.parent:
                    currentParent.heuristic = maxScore
                    currentParent = maxNode.parent
                    maxScore = float("inf")
              	maxNode.heuristic = self.heuristic(maxNode.data)
                if   maxScore > maxNode.heuristic:
                    maxScore = maxNode.heuristic
            currentParent.heuristic = maxScore ## last parent
            ## find min value for minNodes(AI providing us piece)
            minScore = -1
            currentParent = minNodes[0].parent
            for minNode in minNodes:
                if currentParent != minNode.parent:
                    currentParent.heuristic = minScore
                    currentParent = minNode.parent
                    minScore = -1
                if minScore < minNode.heuristic:
                    minScore = minNode.heuristic
            currentParent.heuristic = minScore ##last parent
        ##special case for depth of 1
	best = None
	best_score = float("inf")
	for node in self.nodesAtDepth[1]:
		if node.heuristic == None:
			print "none"
		if node.heuristic < best_score:
			best_score = node.heuristic
		    	best = node
	#print "time taken to bubble: "+ str(datetime.now() - dt)
	self.translateAndRotatePiece(best.data)
	
            
            
            
    def buildMinimaxRound(self, node, currentDepth):
	if currentDepth > self.MAX_DEPTH:
		return
	elif len(self.nodesAtDepth) <= currentDepth:
		self.nodesAtDepth.append([])
		self.nodesAtDepth[currentDepth].append([]) #max
		self.nodesAtDepth[currentDepth].append([]) #min
        ###loop, putting all pieces into node's children
	for shape in self.shapeList:
		board_list = get_legal_moves(node.data.gridList, shape.check_and_create_fake())
		child = Node()
		#child.data = shape
		#node.children.append(child)
		child.parent = node
		self.nodesAtDepth[currentDepth][self.MIN].append(child)
		for board in board_list:
			childOfChild = Node()
			childOfChild.parent = child
			#child.children.append(childOfChild)
			childOfChild.data = board
			self.nodesAtDepth[currentDepth][self.MAX].append(childOfChild)
			##create children for this child
			self.buildMinimaxRound(childOfChild, currentDepth + 1)

    def buildMinimaxTree(self, grid, root):
            firstGenChild = Node()
            firstGenChild.data = grid
            firstGenChild.depth = 1;
            firstGenChild.parent = root;
            root.children.append(firstGenChild)
            self.buildMinimaxRound(firstGenChild, 2)
            self.nodesAtDepth[1].append(firstGenChild)


class buildTreeThread (threading.Thread):
    def __init__(self, threadID, grid, root, nodesAtDepth):
        self.threadID = threadID
        self.grid = grid
        self.root = root
        self.MAX = 1 ##constants for min, max of a depth
        self.MIN = 0
        self.MAX_DEPTH = 2
        self.nodesAtDepth = nodesAtDepth
        self.shapes = [square_shape, t_shape, l_shape, reverse_l_shape, z_shape, s_shape, i_shape ]
        self.badshapes = [fly_shape, longT_shape, square_shape]
        threading.Thread.__init__(self)
    def run(self):
        firstGenChild = Node()
        firstGenChild.data = self.grid
        firstGenChild.depth = 1;
        firstGenChild.parent = self.root;
        self.root.children.append(firstGenChild)
        self.buildMinimaxRound(firstGenChild, 2)
        self.nodesAtDepth[1].append(firstGenChild)

    def buildMinimaxRound(self, node, currentDepth):
	if currentDepth > self.MAX_DEPTH:
		return
	elif len(self.nodesAtDepth) <= currentDepth:
		self.nodesAtDepth.append([])
		self.nodesAtDepth[currentDepth].append([]) #max
		self.nodesAtDepth[currentDepth].append([]) #min
        ###loop, putting all pieces into node's children
	for shape in self.shapeList:
		board_list = get_legal_moves(node.data.gridList, shape.check_and_create_fake())
		child = Node()
		#child.data = shape
		#node.children.append(child)
		child.parent = node
		self.nodesAtDepth[currentDepth][self.MIN].append(child)
		for board in board_list:
			childOfChild = Node()
			childOfChild.parent = child
			#child.children.append(childOfChild)
			childOfChild.data = board
			self.nodesAtDepth[currentDepth][self.MAX].append(childOfChild)
			##create children for this child
			self.buildMinimaxRound(childOfChild, currentDepth + 1)
class Minimax2(AI):

    def makeMove(self, gridList, shape, nextShape,  first=False):
        root = Node();
	self.nextShape = nextShape
        self.MAX = 1 ##constants for min, max of a depth
        self.MIN = 0
        self.MAX_DEPTH = 3
        self.nodesAtDepth = [] ##list that stores lists of all of the nodes at a given depth. ie, nodeAtDepth[MAX_DEPTH] = all of the leaves
        self.nodesAtDepth.append([root]);
        self.nodesAtDepth.append([])
	move_list = get_legal_moves(gridList, shape)
        ##build first generation of the tree, representing the move for the next piece (which we know)
	dt = datetime.now()
        threadLock = threading.Lock()
        threads = []
        n = 1
        for grid in move_list:
            #firstGenChild = Node()
            #firstGenChild.data = grid
            #firstGenChild.depth = 1;
            #firstGenChild.parent = root;
            #root.children.append(firstGenChild)
            #self.buildMinimaxRound(firstGenChild, 2)
            #self.nodesAtDepth[1].append(firstGenChild)
            
            self.buildMinimaxTree(grid, root)

            ###lines for multithreading (works but no obvious speed boost)
            """thread = buildTreeThread(n, grid, root, self.nodesAtDepth)
            thread.start()
            threads.append(thread)
            n = n + 1
        for t in threads:
            t.join()"""
        ###tree is done
	print "time taken to build minimax: "+ str(datetime.now() - dt)
	dt = datetime.now()
        for depth in range( 0, self.MAX_DEPTH - 2):
            depth = self.MAX_DEPTH - depth#go from bottom up, descending 
            maxNodes = self.nodesAtDepth[depth][self.MAX]
            minNodes = self.nodesAtDepth[depth][self.MIN]
            ##find max value for maxNodes (our move)
            maxScore = float("inf")
            currentParent = maxNodes[0].parent
            for maxNode in maxNodes:
                if currentParent != maxNode.parent:
                    currentParent.heuristic = maxScore
                    currentParent = maxNode.parent
                    maxScore = float("inf")
              	maxNode.heuristic = self.heuristic(maxNode.data)
                if   maxScore > maxNode.heuristic:
                    maxScore = maxNode.heuristic
            currentParent.heuristic = maxScore ## last parent
            ## find min value for minNodes(AI providing us piece)
            minScore = -1
            currentParent = minNodes[0].parent
            for minNode in minNodes:
                if currentParent != minNode.parent:
                    currentParent.heuristic = minScore
                    currentParent = minNode.parent
                    minScore = -1
                if minScore < minNode.heuristic:
                    minScore = minNode.heuristic
            currentParent.heuristic = minScore ##last parent
        ##special case for depth of 2
	best = None
	best_score = float("inf")
	for node in self.nodesAtDepth[2]:
		if node.heuristic == None:
			print "none"
		if node.heuristic < best_score:
			best_score = node.heuristic
		    	best = node
	#print "time taken to bubble: "+ str(datetime.now() - dt)
	self.translateAndRotatePiece(best.parent.data)
	
            
            
            
    def buildMinimaxRound(self, node, currentDepth):
	if currentDepth > self.MAX_DEPTH:
		return
	elif len(self.nodesAtDepth) <= currentDepth:
		self.nodesAtDepth.append([])
		self.nodesAtDepth.append([])
		self.nodesAtDepth[currentDepth].append([]) #max
		self.nodesAtDepth[currentDepth].append([]) #min
        ###loop, putting all pieces into node's children
	for shape in self.shapeList:
		board_list = get_legal_moves(node.data.gridList, shape.check_and_create_fake())
		child = Node()
		#child.data = shape
		#node.children.append(child)
		child.parent = node
		self.nodesAtDepth[currentDepth][self.MIN].append(child)
		for board in board_list:
			childOfChild = Node()
			childOfChild.parent = child
			#child.children.append(childOfChild)
			childOfChild.data = board
			self.nodesAtDepth[currentDepth][self.MAX].append(childOfChild)
			##create children for this child
			self.buildMinimaxRound(childOfChild, currentDepth + 1)

    def buildMinimaxTree(self, grid, root):
            firstGenChild = Node()
            firstGenChild.data = grid
            firstGenChild.depth = 1;
            firstGenChild.parent = root;
            root.children.append(firstGenChild)
            self.nodesAtDepth[1].append(firstGenChild)
	    legal_children = get_legal_moves(grid.gridList, self.nextShape.check_and_create_fake())
	    for board in legal_children:
		    childOfChild = Node()
		    childOfChild.data = board
		    childOfChild.depth = 2;
		    childOfChild.parent = firstGenChild;
		    firstGenChild.children.append(childOfChild)
		    self.buildMinimaxRound(childOfChild, 3)
		    self.nodesAtDepth[2].append(childOfChild)
		

class buildTreeThread (threading.Thread):
    def __init__(self, threadID, grid, root, nodesAtDepth):
        self.threadID = threadID
        self.grid = grid
        self.root = root
        self.MAX = 1 ##constants for min, max of a depth
        self.MIN = 0
        self.MAX_DEPTH = 2
        self.nodesAtDepth = nodesAtDepth
        self.shapes = [square_shape, t_shape, l_shape, reverse_l_shape, z_shape, s_shape, i_shape ]
        self.badshapes = [fly_shape, longT_shape, square_shape]
        threading.Thread.__init__(self)
    def run(self):
        firstGenChild = Node()
        firstGenChild.data = self.grid
        firstGenChild.depth = 1;
        firstGenChild.parent = self.root;
        self.root.children.append(firstGenChild)
        self.buildMinimaxRound(firstGenChild, 2)
        self.nodesAtDepth[1].append(firstGenChild)

    def buildMinimaxRound(self, node, currentDepth):
	if currentDepth > self.MAX_DEPTH:
		return
	elif len(self.nodesAtDepth) <= currentDepth:
		self.nodesAtDepth.append([])
		self.nodesAtDepth[currentDepth].append([]) #max
		self.nodesAtDepth[currentDepth].append([]) #min
        ###loop, putting all pieces into node's children
	for shape in self.shapeList:
		board_list = get_legal_moves(node.data.gridList, shape.check_and_create_fake())
		child = Node()
		#child.data = shape
		#node.children.append(child)
		child.parent = node
		self.nodesAtDepth[currentDepth][self.MIN].append(child)
		for board in board_list:
			childOfChild = Node()
			childOfChild.parent = child
			#child.children.append(childOfChild)
			childOfChild.data = board
			self.nodesAtDepth[currentDepth][self.MAX].append(childOfChild)
			##create children for this child
			self.buildMinimaxRound(childOfChild, currentDepth + 1)

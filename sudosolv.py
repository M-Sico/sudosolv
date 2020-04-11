# Board will consist of a 2d list of tiles
# Groups:
#	g1	g2	g3
#	g4	g5	g6
#	g7	g8	g9
# To deduce group from row/col:
#	g1 = if r//3 == 0 and c//3 == 0
#	g2 = if r//3 == 0 and c//3 == 1
#	g3 = if r//3 == 0 and c//3 == 2
#	g4 = if r//3 == 1 and c//3 == 0
#	g5 = if r//3 == 1 and c//3 == 1
#	g6 = if r//3 == 1 and c//3 == 2
#	g7 = if r//3 == 2 and c//3 == 0
#	g8 = if r//3 == 2 and c//3 == 1
#	g9 = if r//3 == 2 and c//3 == 2
# Same group if r//3 == fr//3 and c//3 == fc//3
avg = lambda _list : sum(_list) / len(_list)

from os import system
from time import time
import weakref
clear = lambda : system("cls")

class Tile:
	"""
	:number: number the tile represents (1-9), 0 for empty
	:pencil: possible numbers of the tile, empty if tile is filled
	:probability: single value list for amount of possible numbers
	:undo_stack:
	:friend: influenced tiles
	"""
	def __init__(self, number_pen, row = None, col = None, string = None):
		self.number = str(number_pen)
		self.row = row
		self.col = col
		if string != None:
			self.pencil = string
		else:
			self.pencil = ""
		self.probability = [len(self.pencil)]
		self.undo_stack = []
		self.friends = []
		self.friend_group = []
		self.friend_row = []
		self.friend_col = []

	def addFriend(self, friend, rcg = ""):
		if "f" in rcg:
			#self.friends.append(friend)
			self.friends.append(weakref.proxy(friend))
		if "r" in rcg:
			#self.friend_row.append(friend)
			self.friend_row.append(weakref.proxy(friend))
		if "c" in rcg:
			#self.friend_col.append(friend)
			self.friend_col.append(weakref.proxy(friend))
		if "g" in rcg:
			#self.friend_group.append(friend)
			self.friend_group.append(weakref.proxy(friend))

	def removePencil(self, number):
		if number in self.pencil:
			self.pencil = self.pencil.replace(str(number), "")
			self.probability = [len(self.pencil)]
			self.undo_stack.append(number)
		return self

	def addPencil(self, number):
		self.pencil += str(number)
		self.probability = [len(self.pencil)]

	def undo(self, number):
		"""
		Checks friends', if the number is the same as the last value of undo_stack, then return it to pencil
		"""
		if len(self.undo_stack) > 0 and number == self.undo_stack[-1]:
			self.addPencil(self.undo_stack.pop())

	def updateProbability(self, number = -1):
		if number == -1:	
			self.probability = [len(self.pencil)]
		else:	
			self.probability = [number]
		return self

	def addNumber(self, number):
		self.number = number
		self.removePencil(number)

	def __str__(self):
		return self.number

	def __eq__(self, rhs):
		return self.number == str(rhs)

	def __ne__(self, rhs):
		return self.number != str(rhs)

	def __le__(self, rhs):
		return len(self.pencil) <= len(rhs.pencil)

	def __lt__(self, rhs):
		return len(self.pencil) < len(rhs.pencil)

	def __ge__(self, rhs):
		return len(self.pencil) >= len(rhs.pencil)

	def __gt__(self, rhs):
		return len(self.pencil) > len(rhs.pencil)

class Board:
	def __init__(self, tile_list = None, string_list = None, string = None, *args):
		self.table = []
		if tile_list != None:
			self.table = tile_list
		elif string != None:
			string_list = [string.strip()[index:index + 9].strip() for index in range(0,81,9)]
		elif string_list != None:
			for row in range(len(string_list)):
				self.table.append([Tile(number, row, col) for number, col in zip(string_list[row], range(9))])
		else:
			for arg in args:
				self.table.append(arg)
		self.probability_list = []
		self.backtrack = [0]
		self.iterations = [0]

	def printBoard(self, _clear = False, row = -1, col = -1):
		"""
		Prints the board!
		"""
		if _clear:
			clear()
		sep = lambda num : print("_"*num, end = "")
		sep(37)

		row_ct = 0
		for _row in self.table:
			col_ct = 0
			print("\n|", end = " ")
			for tile in _row:
				if row == row_ct and col == col_ct:
					print(tile.number, end = "*| ")
				else:
					print(tile.number, end = " | ")
				col_ct += 1
			row_ct += 1
		print()
		sep(37)
		print()

	def printPencil(self, _clear = False, row = -1, col = -1):
		"""
		Prints the board!
		"""
		if _clear:
			clear()
		sep = lambda num : print("_"*num, end = "")
		sep(118)

		row_ct = 0
		for _row in self.table:
			col_ct = 0
			print("\n|", end = " ")
			for tile in _row:
				if row == row_ct and col == col_ct:
					print(f"{tile.pencil:9}*", end = " | ")
				else:
					print(f"{tile.pencil:10}", end = " | ")
				col_ct += 1
			row_ct += 1
		print()
		sep(118)
		print()

	def __str__(self):
		string = ""
		for tile_list in self.table:
			for tile in tile_list:
				string += tile.number
		return string

	def generateFriendPencil(self):
		while (True):
			index = 0
			self.iterations[0] += 1
			if (self.backtrack != 0):
				self.backtrack[0] += 1
			flag = False
			self.probability_list = []
			for row in range(9):
				for col in range(9):
					# reset friend and pencil
					self.table[row][col].friends = []
					self.table[row][col].pencil = ""
					if self.table[row][col] != "0":
						continue
					# Initialize group start and end and reinitializes pencil
					start_row = 3 * (row // 3)
					start_col = 3 * (col // 3)
					end_row = start_row + 3
					end_col = start_col + 3
					self.table[row][col].pencil = "123456789"
					# Row check:
					for tile in self.table[row]:
						if id(tile) == id(self.table[row][col]):	continue # If same tile, skip
						elif tile == "0":	# if tile is empty, it's a friend
							self.table[row][col].addFriend(tile, "fr") # DELETE IF DELETING FRIEND_ROW
						else:	# if tile has number, remove from pencil
							self.table[row][col].removePencil(tile.number)
							if len(self.table[row][col].pencil) == 1:	# Hidden single
								self.table[row][col].number = self.table[row][col].pencil
								flag = True
								break
					if flag:
						break
					# Column check:
					for tile_list in self.table:
						if id(tile_list[col]) == id(self.table[row][col]):	continue # If same tile, skip
						elif tile_list[col] == "0":	# if tile is empty, it's a friend
							self.table[row][col].addFriend(tile, "fc") # DELETE IF DELETING FRIEND_ROW
						else:	# if tile has number, remove from pencil
							self.table[row][col].removePencil(tile_list[col].number)
							if len(self.table[row][col].pencil) == 1:	# Hidden single
								self.table[row][col].number = self.table[row][col].pencil
								flag = True
								break
					if flag:
						break
					# Group check:
					for group_row in range(start_row, end_row):
						for group_col in range(start_col, end_col):
							if row != group_row and col != group_col and self.table[group_row][group_col] == "0":# DELETE IF DELETING FRIEND_ROW
								self.table[row][col].addFriend(self.table[group_row][group_col], ("fg" if row != group_row or col != group_col else "g")) # DELETE IF DELETING FRIEND_ROW # DELETE IF DELETING FRIEND_ROW
							if row == group_row or col == group_col:	continue	# If same col/row, skip
							#elif self.table[group_row][group_col] == "0":	# if tile is empty, it's a friend
							#	self.table[row][col].friends.append(self.table[group_row][group_col])
							else:	# if tile has number, remove from pencil
								self.table[row][col].removePencil(self.table[group_row][group_col].number)
								if len(self.table[row][col].pencil) == 1:	# Hidden single
									self.table[row][col].number = self.table[row][col].pencil
									flag = True
									break
					if flag:
						break
					# reset undo_stack
					self.table[row][col].undo_stack = []
					# Probability
					self.probability_list.append([self.table[row][col].probability, weakref.proxy(self.table[row][col]), index])
					index += 1
				if flag == True:
						break
			if flag == True:
				continue
			break

	def nakedPair(self, row, col):
		# Algorithm
			# ONLY if len(pencil) == 2
			# Else return
			# Check to see if friend's len(pencil) == 2 and sorted(pencil) == friend's sorted(pencil)
			# If same row, remove all pencils from row
			# if same col, remove all pencils from col
			# if same group, remove all pencils from group
		flag = False
		if len(self.table[row][col]) == 2:
			for friend, type in [[_friend, "" + ("r" if _friend.row == row else "") + ("c" if _friend.col == row else "") + ("g" if _friend.row // 3 == row // 3 and _friend.col // 3 == col // 3 else "")] for _friend in self.table[row][col].friend]:
				if sorted(friend.pencil) == sorted(self.table[row][col].pencil):
					if "r" in type: 
						self.table[row][col].friend_row.removePencil(self.table[row][col].pencil[0]).removePencil(self.table[row][col].pencil[1])
						flag = True
					if "c" in type:
						self.table[row][col].friend_col.removePencil(self.table[row][col].pencil[0]).removePencil(self.table[row][col].pencil[1])
						flag = True
					if "g" in type:
						self.table[row][col].friend_group.removePencil(self.table[row][col].pencil[0]).removePencil(self.table[row][col].pencil[1])
						flag = True
		return flag

	# not done
	def nakedTriple(self, row, col):
		pass

	# not done
	def nakedQuads(self, row, col):
		pass

	def hiddenPair(self, row, col):
		# Algorithm
		# if len([num for num in pencil if gf1.pencil]) != 2
		# 
		pass

	# not done
	def hiddenTriple(self, row, col):
		pass

	# not done
	def hiddenQuads(self, row, col):
		pass

	def __recurSolve(self, flag = False, number = None):
		# self.printBoard(True)
		# self.printPencil(False)
		clrear()
		print(f"Iterations: {self.iterations[0]} | Backtracks: {self.backtrack[0]}")
		self.iterations[0] += 1
		for probability, tile, index in sorted(self.probability_list):	# Sort list of tiles by priority and loop
			# Pre-exit condition
			if tile != 0: # If lowest probability tile is not empty, exit
				flag = True
				return
			for number in tile.pencil:	# For all pencil in tile, else go to next tile
				# If pencil is not in friend's number, set number as pencil (guess algorithm)
				# else check other pencil
				if number not in tile.friends:
					tile.number = number
					# Remove number from friends' pencil
					for friend in tile.friends:
						friend.removePencil(number)
					self.probability_list[index][0] = [100]
					# Iterate
					self.__recurSolve(flag, number)
					# If you find a solution ####### I DUNNO IF NECESSARY
					if flag:
						break
					# Backtrack, reset tile, probability, and friend pencil
					tile.number = "0"
					#tile.updateProbability()
					self.probability_list[index][0] = [len(tile.pencil)]
					for friend in tile.friends:
						friend.undo(number)
			# Exit 2
			# If there is no pencil left and no number chosen, backtrack
			if tile == "0":
				self.backtrack[0] += 1
				return
		# Exit condition I don't know if this is Necessary
		if 0 not in [tile.number for probability, tile in self.probability_list]:
			return
		return

	def solve(self):
		"""
		Creates a pencil, then solves recursively
		"""
		self.generateFriendPencil()
		# Solve by guessing
		self.__recurSolve()
		print("Backtrack:", self.backtrack[0], "| Iterations:", self.iterations[0])

# Current average solve time: 189 ms (1000 tests)
# New average solve time: 10 ms (1000 tests)
#000105000140000670080002400063070010900000003010090520007200080026000035000409000
s_easy = "672145398145983672389762451263574819958621743714398526597236184426817935831459267"
u_easy = [
	"000105000",
	"140000670",
	"080002400",
	"063070010",
	"900000003",
	"010090520",
	"007200080",
	"026000035",
	"000409000"
	]
# Current average solve time: 3113 ms (100 tests)
# New average solve time: 2420 ms (100 tests)
#030605000600090002070100006090000000810050069000000080400003020900020005000908030
s_medium = "239645817641897352578132496796281543812354769354769281467513928983426175125978634"
u_medium = [
	"030605000",
	"600090002",
	"070100006",
	"090000000",
	"810050069",
	"000000080",
	"400003020",
	"900020005",
	"000908030"
	]

u_hard = [
	"002090300",
	"805000000",
	"100000000",
	"090060040",
	"000000058",
	"000000001",
	"070000200",
	"300500000",
	"000100000"
	]

unsolvable = [
	"781543926",
	"006179500",
	"954628731",
	"695837214",
	"148265379",
	"327914800",
	"413752698",
	"002000400",
	"579486103"
	]

if __name__ == "__main__":
	BOARD = u_medium
	SOLUTION = s_medium

	TIME = time()*1000
	board1 = Board(string_list = BOARD)
	board1.solve()
	print(board1)
	print(SOLUTION)
	board1.printBoard()
	print(time()*1000 - TIME)
	
	#time_list = []
	#for round in range(1000):
	#	TIME = time()*1000
	#	board1 = Board(string_list = BOARD)
	#	board1.solve()
	#	time_list.append(time()*1000 - TIME)
	#	#print(time_list[-1])
	#print("Average time:", avg(time_list))

	#def aPrint(test):
	#	for i in range(len(test.table)):
	#		print(test.table[i].number, end = " ")
	#	print()

	#tile1 = Tile(1)
	#tile2 = Tile(2)
	#tile3 = Tile(3)
	#tile4 = Tile(4)
	#tile5 = Tile(5)
	#tile6 = Tile(6)
	#tile7 = Tile(7)
	#tile8 = Tile(8)

	#test = Board([tile1, tile2, tile3, tile4])
	#test2 = Board([tile5, tile6, tile7, tile8])

	#print("Before Extend")
	#aPrint(test)
	#aPrint(test2)
	#print("After Extend")
	#test2.table.extend([tile for tile in test.table if id(tile) != id(tile4)])
	#aPrint(test)
	#aPrint(test2)
	#print("After Changes")
	#tile1.number = 100
	#test.table[1].number = 100
	#tile5.number = 100
	#test2.table[1].number = 100
	#aPrint(test)
	#aPrint(test2)

	#amount = 1
	#time_list = []
	#for x in range(amount):
	#	start = time()*1000000000
	#	test1 = "123456789"
	#	test2 = "149rtyuio"
	#	test3 = "bky6zt1ip"
	#	test4 = "9afq251cm"
	#	test5 = "v1lwej5sr"
	#	test6 = "r8p196w7b"
	#	test7 = "r9741uj3s"
	#	test8 = "5i12y39dc"
	#	test9 = "dobe2jya1"
	#	[num for num in test1 if num in test2 and num in test3 and num in test4 and num in test5 and num in test6 and num in test7 and num in test8 and num in test9]
	#	boop = []
	#	print(time()*1000 - start)
	#	time_list.append(time()*1000000000 - start)
	#print(f"Average: {avg(time_list)} ns")
	#print(f"Best: {sorted(time_list)[0]} ns")
	#print(f"Worst: {sorted(time_list)[-1]} ns")
	#time_list = []
	#for x in range(amount):
	#	start = time()*1000000000
	#	test1 = set("123456789")
	#	test2 = set("149rtyuio")
	#	test3 = set("bky6zt1ip")
	#	test4 = set("9afq251cm")
	#	test5 = set("v1lwej5sr")
	#	test6 = set("r8p196w7b")
	#	test7 = set("r9741uj3s")
	#	test8 = set("5i12y39dc")
	#	test9 = set("dobe2jya1")
	#	list(test1.intersection(test2,test3,test5,test6,test7,test8,test9))
	#	print(time()*1000 - start)
	#	time_list.append(time()*1000000000 - start)
	#print(f"Average: {avg(time_list)} ns")
	#print(f"Best: {sorted(time_list)[0]} ns")
	#print(f"Worst: {sorted(time_list)[-1]} ns")

	#class meow:
	#	def __init__(self):
	#		self.one = ""

	#	def addOne(self):
	#		self.one += "1"
	#		return self

	#teest = meow()
	#teest.addOne().addOne() # Only works if returns self
	#print(teest.one)

	#for x, y in [[1,2],[2,3],[4,5],[6,7]]:
	#	print(x, y)
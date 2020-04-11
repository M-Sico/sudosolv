import threading
import tkinter as tk
from functools import partial
from time import sleep
import sudosolv

sudoku_board = "000105000140000670080002400063070010900000003010090520007200080026000035000409000"

# Colors:
default_color1 = "#ffffff"
default_color2 = "#d9d9d9"
line_color = "#000000"
font_color = "#000000"
font_red = "#cc0000"
pen_color = "#0000cc"
highlight_color = "#ffff04"
softlight_color1 = "#ffffe6"
softlight_color2 = "#cccc99"

color_partition = lambda r, c, color1, color2 : (
										color1 
										if ((r // 3 == 0 or r // 3 == 2) and (c // 3 == 0 or c // 3 == 2)) 
										or (r // 3 == 1 and c // 3 == 1)
										else color2
									)

# Darkmode colors:
default_dark1 = "#000000"
default_dark2 = "#1a1a1a"
line_dark = "#000000"
font_dark = "#ffffff"
pen_dark = "#6666ff"
highlight_dark = "#4d4d4d"
softlight_dark1 = "#333333"

class Sudoku(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.grid_columnconfigure(0, weight = 1)
		self.master = master
		self.pack()
		self.createBoard()
		self.auto = False
		self.createControl()
		self.undo_counter = 0
		self.undo_stack = [0]
		self.setTiles("000105000140000670080002400063070010900000003010090520007200080026000035000409000")

	def penPencil(self):
		if self.pen["state"] == "disabled":
			self.pencil["state"] = "disabled"
			self.pen["state"] = "normal"
		else:
			self.pen["state"] = "disabled"
			self.pencil["state"] = "normal"
		pass

	def setTiles(self, string):
		string = [string[index:index + 9] for index in range(0,81,9)]
		for row, r in zip(string,range(9)):
			for number, c in zip(row, range(9)):
				if number not in "123456789":
					self.tile[r][c]["text"] = ""
					continue
				self.tile[r][c]["text"] = number
				self.tile[r][c]["font"] = ("", 50, "bold")

	def changePencil(self, element, row, col):
		if (element["text"] == "" or element["font"] != "{} 50") and (element["bg"] != softlight_color1 and element["bg"] != softlight_color2):
			print("HI")
			for i in range(9):
				if self.keys[i]["bg"] == highlight_color:
					self.undo_stack[0] += 1
					self.undo_stack.append([self.undo_stack[0], element["text"], row, col, element["font"], element["fg"], element["bg"]])
					if self.keys[i]["text"] not in element["text"]:
						element["fg"] = font_color
						element["font"] = ("", 18)
						pencil = self.keys[i]["text"]
						pencil += (" " if self.keys[i]["text"] != "9" else "")
						for index in range(len(element["text"])):
							if self.keys[i]["text"] < element["text"][index]:
								element["text"] = element["text"][:index] + pencil + element["text"][index:]
								break
						else:
							element["text"] += pencil
					else: 
						element["text"] = element["text"].replace(self.keys[i]["text"] + " ", "")

	def changeTile(self, element, row, col, event):
		if self.pen["state"] == "disabled" and element["font"] != "{} 50 bold":
			for i in range(9):
				if self.keys[i]["bg"] == highlight_color:
					if element["text"] == self.keys[i]["text"]:
						self.undo_stack[0] += 1
						self.undo_stack.append([self.undo_stack[0], element["text"], row, col, element["font"], element["fg"], element["bg"]])
						element["text"] = ""
					else:
						self.undo_stack[0] += 1
						self.undo_stack.append([self.undo_stack[0], element["text"], row, col, element["font"], element["fg"], element["bg"]])
						element["font"] = ("", 50)
						element["fg"] = pen_color
						element["text"] = self.keys[i]["text"]
					self.highlight(i, True)
					break
		elif element["font"] != "{} 50 bold":
			self.changePencil(element, row, col)

	def undoChange(self):
		# Undo stack stores: [undo_count/length, number, tile_row, tile_col, font, fg, bg]
		self.undo_counter += 1
		while len(self.undo_stack) > 1 and self.undo_stack[-1][0] == self.undo_stack[0]:
			undo = self.undo_stack.pop()
			number = undo[1]
			row = undo[2]
			col = undo[3]
			font = undo[4]
			fg = undo[5]
			bg = undo[6]
			self.tile[row][col]["text"] = number
			self.tile[row][col]["font"] = font
			self.tile[row][col]["fg"] = fg
			self.tile[row][col]["bg"] = bg
		self.undo_stack[0] -= 1
		for index in range(9):
			if self.keys[index]["bg"] != default_color1:
				self.highlight(index, True)
				break

	def createBoard(self):
		self.board = tk.Frame(self, width = 742, height = 711)
		self.board.grid(row = 0, column = 0, sticky = tk.E + tk.W)
		self.tile = []
		_r = _c = 0
		for r in range(9):
			_c = 0
			self.tile.append([])
			for c in range(9):
				self.tile[r].append(tk.Label(
										self.board, 
										height = 1, 
										width = 2, 
										text = f"{1 + r * 9 + c}", 
										bg = color_partition(r,c, default_color1, default_color2),
										fg = font_color,
										font = ("", 50),
										borderwidth = 1,
										relief = "groove",
										wraplength = 70
									))
				changeTile_arg = partial(self.changeTile, self.tile[r][c], r, c)
				self.tile[r][c].bind("<Button-1>", changeTile_arg)
				self.tile[r][c].grid(row = _r, column = _c, columnspan = 10, rowspan = 10, sticky = tk.N + tk.S + tk.E + tk.W)
				_c += 10
				if (c + 1) % 3 == 0 and c  < 7:
					spacer = tk.Frame(self.board, bg = line_color, height = 10, width = 2)
					spacer.grid(row = _r, column = _c, columnspan = 1, rowspan = 10, sticky = tk.N + tk.S + tk.E)
					_c += 2
			if (r) % 3 == 0 and r != 0:
				spacer = tk.Frame(self.board, bg = line_color, height = 2, width = 10)
				spacer.grid(row = _r, column = 0, columnspan = 96, rowspan = 2, sticky = tk.N + tk.E + tk.W)
				_r += 2
			_r += 10

	def highlight(self, index, _insert = False):
		row = []
		col = []
		if not _insert:
			if self.keys[index]["background"] == highlight_color:
				self.keys[index]["background"] = default_color1
			else:
				self.keys[index]["background"] = highlight_color
		for r in range(9):
			if r != index:
					self.keys[r]["background"] = default_color1
			for c in range(9):
				self.tile[r][c]["background"] = color_partition(r, c, default_color1, default_color2)
				if self.tile[r][c]["text"] == f"{index + 1}" and self.keys[index]["background"] == highlight_color:
					row.append(r)
					col.append(c)
					self.tile[r][c]["background"] = highlight_color
		finish_flag = True
		for r in range(9):
			for c in range(9):
				if self.tile[r][c]["background"] == default_color1 or self.tile[r][c]["background"] == default_color2:
					if [r // 3, c // 3] in [[_row // 3, _col // 3] for _row, _col in zip(row, col)]:
						self.tile[r][c]["background"] = color_partition(r, c, softlight_color1, softlight_color2)
					if r in row:
						self.tile[r][c]["background"] = color_partition(r, c, softlight_color1, softlight_color2)
					if c in col:
						self.tile[r][c]["background"] = color_partition(r, c, softlight_color1, softlight_color2)
					if self.tile[r][c]["background"] == default_color1 or self.tile[r][c]["background"] == default_color2:
						finish_flag = False
					if self.auto and (self.tile[r][c]["background"] == default_color1 or self.tile[r][c]["background"] == default_color2) and (self.tile[r][c]["text"] == "" or "50" not in self.tile[r][c]["font"]):
						for i in range(9):
							if self.keys[i]["bg"] == highlight_color and self.keys[i]["text"] not in self.tile[r][c]["text"]:
								self.tile[r][c]["fg"] = font_color
								self.tile[r][c]["font"] = ("", 18)
								pencil = self.keys[i]["text"]
								pencil += (" " if self.keys[i]["text"] != "9" else "")
								for index in range(len(self.tile[r][c]["text"])):
									if self.keys[i]["text"] < self.tile[r][c]["text"][index]:
										self.tile[r][c]["text"] = self.tile[r][c]["text"][:index] + pencil + self.tile[r][c]["text"][index:]
										break
								else:
									self.tile[r][c]["text"] += pencil
				if _insert and self.tile[r][c]["font"] != "{} 50" and self.tile[r][c]["background"] != default_color1 and self.tile[r][c]["background"] != default_color2:
					self.undo_stack.append([self.undo_stack[0], self.tile[r][c]["text"], r, c, self.tile[r][c]["font"], self.tile[r][c]["fg"], self.tile[r][c]["bg"]])
					self.tile[r][c]["text"] = self.tile[r][c]["text"].replace(self.keys[index]["text"] + " ", "")
		if finish_flag:
			self.keys[index]["fg"] = font_red
		else:
			self.keys[index]["fg"] = font_color

	def solve(self):
		pass

	def toggleAuto(self):
		if self.auto:
			self.auto = False
			return
		self.auto = True

	def createControl(self):
		self.control_frame = tk.Frame(self, width = 742, bg = "red")
		self.control_frame.grid_columnconfigure(0, weight = 1)
		self.control_frame.grid(row = 1, column = 0, sticky = tk.E + tk.W)
		#self.control_frame.pack(side = "bottom", fill = tk.Y, expand = 1)
		self.pen = tk.Button(self.control_frame, text = "Pen", command = self.penPencil, state = "disabled")
		self.pencil = tk.Button(self.control_frame, text = "Pencil", command = self.penPencil)
		self.auto_pencil = tk.Checkbutton(self.control_frame, text = "Auto-Pencil", variable = self.auto, command = self.toggleAuto)
		self.undo = tk.Button(self.control_frame, text = "Undo", command = self.undoChange)
		self.solve = tk.Button(self.control_frame, text = "Solve", command = self.solve)
		self.pen.grid(row = 0, column = 0, rowspan = 5, columnspan = 3, sticky = tk.E + tk.W)
		self.pencil.grid(row = 0, column = 3, rowspan = 5, columnspan = 2, sticky = tk.E + tk.W)
		self.auto_pencil.grid(row = 0, column = 5, rowspan = 5, columnspan = 1, sticky = tk.N + tk.S + tk.E + tk.W)
		self.undo.grid(row = 0, column = 6, rowspan = 5, columnspan = 2, sticky = tk.E + tk.W)
		self.solve.grid(row = 0, column = 8, rowspan = 5, columnspan = 2, sticky = tk.E + tk.W)
		self.keys = []
		for index in range(9):
			highlight_arg = partial(self.highlight, index)
			self.keys.append(tk.Button(
								self.control_frame, 
								text = f"{index + 1}", 
								bg = default_color1, 
								fg = font_color,
								font = ("", 35, "bold"),
								height = 1, 
								width = 2, 
								bd = 1, 
								relief = "groove", 
								command = highlight_arg
							))
			self.control_frame.grid_columnconfigure(index, weight = 1)
			self.keys[index].grid(row = 5, column = index, sticky = tk.E + tk.W)

if __name__ == "__main__":
	root = tk.Tk()
	gui = Sudoku(master=root)
	gui.mainloop()
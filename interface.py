"""Copyright 2010 Aydarkhanov Ruslan, Kurochkin Ilya, Rusinov Ivan

This file is part of CCA.

CCA is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published
by the Free Software Foundation, either version 2 of the License,
or (at your option) any later version.

CCA is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CCA. If not, see http://www.gnu.org/licenses/.
"""

import math
import pickle
import random
import tkColorChooser
import tkFileDialog
import tkMessageBox
import webbrowser
from Tkinter import *

from state import *
from automata import *


class Handlers(object):
	
	def __init__(self, cell_size=8, line_width=1 ,delay=8, dx=0, dy=0):
		self.cell_size = cell_size
		self.line_width = line_width
		self.delay = delay
		self.dx = dx
		self.dy = dy
		self.after_id = 0
		self.mouse_zoom = 0
		self.zoom_divisor = 1
		self.selected_state = None
		self.is_started = False
		self.char = None
		self.keys = {}
		for index, state in enumerate(automata.states):
			self.keys[state.key] = index
		self.draw()
	
	def start(self, event=None):
		if not self.is_started:
			self.is_started = True
			self.repeat()
			self.update_status()
	
	def repeat(self):
		self.draw_cell(automata.next_step())
		self.after_id = canvas.after(self.delay, self.repeat)
	
	def stop(self, event=None):
		canvas.after_cancel(self.after_id)
		self.is_started = False
		self.update_status()
	
	def next_step(self, event=None):
		if self.is_started:
			canvas.after_cancel(self.after_id)
			self.is_started = False
			self.update_status()
		else:
			self.draw_cell(automata.next_step())
	
	def save_file(self, event=None):
		file = tkFileDialog.asksaveasfile(defaultextension=".caf",
											title="Save automata as",
											filetypes=[('CCA File', '*.caf')],
											mode="wb")
		if file is not None:
			pickle.dump([automata.field, automata.states], file)
	
	def open_file(self, event=None):
		file = tkFileDialog.askopenfile(title="Open file",
										filetypes=[('CCA File', '*.caf')],
										mode="rb")
		if file is not None:
			from_file = pickle.load(file)
			automata.field = from_file[0]
			automata.height = len(automata.field)
			automata.width = len(automata.field[0])
			automata.states = from_file[1]
			self.selected_state = None
			self.refresh_dicts()
			self.refresh_list()
			self.hide_automata_window()
			self.draw()
	
	def new_file(self, event=None):
		if tkMessageBox.askyesno("Save?", 
									"Save current automata?"):
			self.save_file()
		new_automata = Automata()
		automata.field = new_automata.field
		automata.height = len(automata.field)
		automata.width = len(automata.field[0])
		automata.states = new_automata.states
		self.selected_state = None
		self.refresh_dicts()
		self.refresh_list()
		self.hide_automata_window()
		self.draw()
	
	def show_help_window(self):
		url = 'Help.html'
		webbrowser.open(url, new=1, autoraise=True)
	
	def zoom_in(self, event=None, zoom_rate=1):
		if self.cell_size < 50:
			self.cell_size = self.cell_size + zoom_rate
			self.draw()
			self.change_scroll_area()
	
	def zoom_out(self, event=None, zoom_rate=1):
		if self.cell_size > 1:
			self.cell_size = self.cell_size - zoom_rate
			self.draw()
			self.change_scroll_area()
	
	def slower(self, event=None, speed_rate=2):
		if self.delay <= 500:
			self.delay = self.delay * speed_rate
			self.update_status()
	
	def faster(self, event=None, speed_rate=2):
		self.delay = self.delay / speed_rate
		if self.delay == 0:
			self.delay = 1
		self.update_status()
	
	def change_size(self):
		try:
			dx = int(size_x.get()) - automata.width
			dy = int(size_y.get()) - automata.height
			position = side.get()
			if position == 0 or position == 3 or position == 6:
				automata.change_size(dx, 3)
			elif position == 1 or position == 4 or position == 7:
				automata.change_size(dx / 2, 3)
				automata.change_size(dx - dx / 2, 1)
			else:
				automata.change_size(dx, 1)
			if position == 0 or position == 1 or position == 2:
				automata.change_size(dy, 0)
			elif position == 3 or position == 4 or position == 5:
				automata.change_size(dy / 2, 0)
				automata.change_size(dy - dy / 2, 2)
			else:
				automata.change_size(dy, 2)
			self.draw()
			self.hide_size_window()
			self.change_scroll_area()
			self.update_status()
		except Exception:
			message.config(text="Operation is refused")
			message.after(2000, self.clear_message)
	
	def draw_cell(self, cells):
		for row, col in cells:
			index = automata.symbols[automata.field[row][col]]
			color = automata.states[index].color
			canvas.itemconfig(self.cells[row][col], fill=color)
	
	def draw(self):
		canvas.delete("all")
		self.cells = []
		shift = self.cell_size + self.line_width
		left = self.line_width
		top = self.line_width
		for row in range(automata.height):
			self.cells.append([])
			for col in range(automata.width):
				index = automata.symbols[automata.field[row][col]]
				color = automata.states[index].color
				cell = canvas.create_rectangle(left + col * shift,
								top + row * shift,
								left + col * shift + self.cell_size,
								top + row * shift + self.cell_size,
								fill=color, outline="", tag="cell")
				self.cells[row].append(cell)
	
	def draw_line(self, x1, y1, x2, y2, order=1):
		answer = []
		if abs(x1 - x2) > abs(y1 - y2):
			dx = x2 - x1
			abs_dx = abs(dx)
			dy = float(y2 - y1)
			while x1 != x2:
				x1 = x1 + dx / abs_dx
				y1 = y1 + dy / abs_dx
				answer.append((self.rounding(y1), x1))
		else:
			dx = float(x2 - x1)
			dy = y2 - y1
			abs_dy = abs(dy)
			while y1 != y2:
				x1 = x1 + dx / abs_dy
				y1 = y1 + dy / abs_dy
				answer.append((y1, self.rounding(x1)))
		self.new_state(answer, order)
	
	def rounding(self, num):
		return int(num + math.copysign(0.5, num))
	
	def new_state(self, cells, order=1):
		num_states = len(automata.states)
		changed_cells = []
		for row, col in cells:
			if col >= 0 and row >= 0:
				try:
					index = (automata.symbols[automata.field[row][col]] +
								num_states + order) % num_states
					if self.char is not None and self.char in self.keys:
						index = self.keys[self.char]
					automata.field[row][col] = automata.states[index].symbol
					changed_cells.append((row, col))
				except:
					pass
		self.draw_cell(changed_cells)
	
	def press1(self, event):
		scr_reg = canvas.cget("scrollregion").split()
		self.dx = int(scroll_x.get()[0] * int(scr_reg[2]))
		self.dy = int(scroll_y.get()[0] * int(scr_reg[3]))
		self.col1 = (event.x + self.dx) / (self.cell_size + self.line_width)
		self.row1 = (event.y + self.dy) / (self.cell_size + self.line_width)
		if self.col1 >= 0 and self.row1 >= 0:
			self.new_state([(self.row1, self.col1)])
	
	def motion1(self, event):
		col = (event.x + self.dx) / (self.cell_size + self.line_width)
		row = (event.y + self.dy) / (self.cell_size + self.line_width)
		if not (self.col1 == col and self.row1 == row):
			if abs(self.col1 - col) <= 1 and abs(self.row1 - row) <= 1:
				self.new_state([(row, col)])
			else:
				self.draw_line(self.col1, self.row1, col, row)
			self.col1 = col
			self.row1 = row
	
	def press3(self, event):
		scr_reg = canvas.cget("scrollregion").split()
		self.dx = int(scroll_x.get()[0] * int(scr_reg[2]))
		self.dy = int(scroll_y.get()[0] * int(scr_reg[3]))
		self.col3 = (event.x + self.dx) / (self.cell_size + self.line_width)
		self.row3 = (event.y + self.dy) / (self.cell_size + self.line_width)
		if self.col1 >= 0 and self.row1 >= 0:
			self.new_state([(self.row3, self.col3)], -1)
	
	def motion3(self, event):
		col = (event.x + self.dx) / (self.cell_size + self.line_width)
		row = (event.y + self.dy) / (self.cell_size + self.line_width)
		if not (self.col3 == col and self.row3 == row):
			if abs(self.col3 - col) <= 1 and abs(self.row3 - row) <= 1:
				self.new_state([(row, col)], -1)
			else:
				self.draw_line(self.col3, self.row3, col, row, -1)
			self.col3 = col
			self.row3 = row
	
	def press_key(self, event):
		self.char = event.char
	
	def release_key(self, event):
		self.char = None
	
	def to_top(self):
		selected = self.selected_state
		if selected is not None:
			index = selected
			state = automata.states[index]
			del automata.states[index]
			automata.states.insert(0, state)
			self.selected_state = 0
			self.refresh_dicts()
			self.refresh_list()
	
	def to_bottom(self):
		selected = self.selected_state
		if selected is not None:
			index = selected
			state = automata.states[index]
			del automata.states[index]
			automata.states.append(state)
			self.selected_state = len(automata.states) - 1
			self.refresh_dicts()
			self.refresh_list()
	
	def upwards(self):
		selected = self.selected_state
		if selected is not None:
			index = selected
			if index > 0:
				state = automata.states[index]
				del automata.states[index]
				automata.states.insert(index - 1, state)
				self.selected_state = index - 1
				self.refresh_dicts()
				self.refresh_list()
	
	def downwards(self):
		selected = self.selected_state
		if selected is not None:
			index = selected
			if index < state_list.size() - 1:
				state = automata.states[index]
				del automata.states[index]
				automata.states.insert(index + 1, state)
				self.selected_state = index + 1
				self.refresh_dicts()
				self.refresh_list()
	
	def delete_state(self):
		selected = self.selected_state
		if selected is not None and len(automata.states) != 1:
			index = selected
			symbol = automata.states[index].symbol
			del automata.states[index]
			self.refresh_dicts()
			if index in automata.states:
				self.selected_state = index
			else:
				self.selected_state = len(automata.states) - 1
			self.refresh_list()
			self.select_item(self.selected_state)
			self.draw_changed_state(symbol, automata.states[0].symbol)
		else:
			error.config(text="Operation is refused")
			error.after(2000, self.clear_error)
	
	def add(self):
		name = state_name.get()
		symbol = state_symbol.get()
		key = state_key.get().lower()
		color = state_color.cget("bg")
		nums = []
		for i, value in enumerate(ckeckbox_nums):
				if value.get() == 1:
					nums.append(i)
		if self.keys.has_key(key):
			error.config(text="State with such key has already existed")
			error.after(2000, self.clear_error)
			state_key.focus()
		elif len(key) != 1:
			error.config(text="Bad key for state")
			error.after(2000, self.clear_error)
			state_key.focus()
		elif automata.symbols.has_key(symbol):
			error.config(text="State with such symbol has already existed")
			error.after(2000, self.clear_error)
			state_symbol.focus()
		elif len(symbol) != 1:
			error.config(text="Bad symbol for state")
			error.after(2000, self.clear_error)
			state_symbol.focus()
		else:
			state = State(name, symbol, color, key, nums)
			automata.states.append(state)
			automata.symbols[symbol] = len(automata.states) - 1
			self.keys[key] = len(automata.states) - 1
			error.config(text="")
			self.selected_state = len(automata.states) - 1
			self.refresh_list()
			self.select_item(self.selected_state)
			automata.st_sym[symbol] = state
	
	def change(self):
		selected = self.selected_state
		if selected is not None:
			index = selected
			name = state_name.get()
			symbol = state_symbol.get()
			key = state_key.get().lower()
			color = state_color.cget("bg")
			nums = []
			for i, value in enumerate(ckeckbox_nums):
				if value.get() == 1:
					nums.append(i)
			if self.keys.has_key(key) and self.keys[key] != index:
				error.config(text="This key is already used")
				error.after(2000, self.clear_error)
				state_key.focus()
			elif len(key) != 1:
				error.config(text="Bad key for state")
				error.after(2000, self.clear_error)
				state_key.focus()
			elif (automata.symbols.has_key(symbol) and
					automata.symbols[symbol] != index):
				error.config(text="This symbol is already used")
				error.after(2000, self.clear_error)
				state_symbol.focus()
			elif len(symbol) != 1:
				error.config(text="Bad symbol for state")
				error.after(2000, self.clear_error)
				state_symbol.focus()
			else:
				state = State(name, symbol, color, key, nums)
				symbol_old = automata.states[index].symbol
				automata.states[index] = state
				self.refresh_dicts()
				self.draw_changed_state(symbol_old, symbol)
				self.refresh_list()
	
	def draw_changed_state(self, symbol_old, symbol_new):
		cells = []
		for row in range(automata.height):
			for col in range(automata.width):
				if automata.field[row][col] == symbol_old:
					automata.field[row][col] = symbol_new
					cells.append((row, col))
		self.draw_cell(cells)
	
	def show_size_window(self, event=None):
		sizes = str(len(automata.field[0])) + " x " + str(len(automata.field))
		size_label.config(text=sizes)
		size_window.deiconify()
	
	def hide_size_window(self, event=None):
		size_window.withdraw()
	
	def show_automata_window(self):
		self.select_item(self.selected_state)
		self.refresh_list
		automata_window.deiconify()
	
	def hide_automata_window(self):
		automata_window.withdraw()
	
	def refresh_list(self):
		state_list.delete(0, "end")
		for state in automata.states:
			state_list.insert("end", state)
		if self.selected_state is not None:
			state_list.selection_set(self.selected_state)
	
	def select_item(self, index):
		if index is not None:
			state = automata.states[index]
			state_name.delete(0, "end")
			state_name.insert(0, state.name)
			state_symbol.delete(0, "end")
			state_symbol.insert(0, state.symbol)
			for key in self.keys.keys():
				if self.keys[key] == index:
					state_key.delete(0, "end")
					state_key.insert(0, key)
			state_color.config(bg=state.color)
			for i in range(9):
				ckeckbox_nums[i].set(i in state.nums)
		else:
			state_name.delete(0, "end")
			state_symbol.delete(0, "end")
			state_key.delete(0, "end")
			state_color.config(bg="white")
			for i in range(9):
				ckeckbox_nums[i].set(False)
	
	def list_mouse_release(self, event):
		selected = state_list.curselection()
		self.selected_state = int(selected[0])
		if selected:
			self.select_item(self.selected_state)
	
	def choose_color(self, event):
		state_color.config(bg=tkColorChooser.askcolor()[1])
	
	def clear_error(self):
		error.config(text="")
	
	def clear_message(self):
		message.config(text="")
	
	def clean_field(self, event=None):
		symbol = automata.states[0].symbol
		cells = []
		for row in range(automata.height):
			for col in range(automata.width):
				if automata.field[row][col] != symbol:
					automata.field[row][col] = symbol
					cells.append((row, col))
		self.draw_cell(cells)
	
	def fill_randomly(self, event=None):
		cells = []
		for row in range(automata.height):
			for col in range(automata.width):
				rand_index = random.randint(0, len(automata.states) - 1)
				automata.field[row][col] = automata.states[rand_index].symbol
				cells.append((row, col))
		self.draw_cell(cells)
	
	def refresh_dicts(self):
		automata.symbols = {}
		automata.st_sym = {}
		self.keys = {}
		for index, state in enumerate(automata.states):
			automata.symbols[state.symbol] = index
			automata.st_sym[state.symbol] = state
			self.keys[state.key] = index
	
	def exit(self, event=None):
		if tkMessageBox.askyesno("Save?", "Save current automata?"):
			self.save_file()
		root.destroy()
	
	def change_scroll_area(self):
		step = self.cell_size + self.line_width
		width = automata.width * step + self.line_width
		height = automata.height * step + self.line_width
		canvas.config(scrollregion=(0, 0, width, height))
	
	def update_status(self):
		size = str(len(automata.field[0])) + " x " + str(len(automata.field))
		status_size.config(text="size: " + size)
		state = "paused"
		speed = 0
		if self.is_started:
			state = "running"
			speed = 512 / self.delay
		status_state.config(text="status: " + state)
		status_speed.config(text="speed: " + str(speed))


root = Tk()
root.title("Cyclic Cellular Automata")

canvas = Canvas(root, background="grey")
canvas.config(width=500, height=400)

automata = Automata()
handlers = Handlers()

canvas.tag_bind("cell", "<1>", handlers.press1)
canvas.tag_bind("cell", "<B1-Motion>", handlers.motion1)
canvas.tag_bind("cell", "<3>", handlers.press3)
canvas.tag_bind("cell", "<B3-Motion>", handlers.motion3)
canvas.bind_all("<KeyPress>", handlers.press_key)
canvas.bind_all("<KeyRelease>", handlers.release_key)

scroll_x = Scrollbar(root, orient="horizontal")
scroll_y = Scrollbar(root, orient="vertical")
statusline = Frame(root)
status_size = Label(statusline)
status_state = Label(statusline)
status_speed = Label(statusline)

handlers.update_status()

canvas.grid(row=0, column=0, sticky="nsew")
scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")
statusline.grid(row=2, column=0, sticky="ew")
status_size.grid(row=0, column=0, sticky="w")
status_state.grid(row=0, column=1, sticky="w")
status_speed.grid(row=0, column=2, sticky="w")

handlers.change_scroll_area()
canvas.config(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
scroll_x.config(command=canvas.xview)
scroll_y.config(command=canvas.yview)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
statusline.columnconfigure(0, weight=1)
statusline.columnconfigure(1, weight=1)
statusline.columnconfigure(2, weight=1)

automata_window = Toplevel(root)
automata_window.title("Automaton")
automata_window.withdraw()
automata_window.resizable(False, False)
automata_window.protocol("WM_DELETE_WINDOW", handlers.hide_automata_window)

headline = Label(automata_window, text="Automaton Panel", font=16)
headline.pack(side="top",fill="both", expand="no")

Label(automata_window, text="State Box:").pack(side="top", fill="x")

list_frame = Frame(automata_window)
scrollbar = Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")
state_list = Listbox(list_frame, yscrollcommand=scrollbar.set,
						activestyle="none", selectmode="single")
handlers.refresh_list()
state_list.bind("<ButtonRelease-1>", handlers.list_mouse_release)
state_list.pack(side="top", fill="y")
scrollbar.config(command=state_list.yview)
list_frame.pack(side="top")

manip_frame1 = Frame(automata_window, padx=10, pady=5)
up = Button(manip_frame1, text="Up", command=handlers.upwards, width=10)
to_top = Button(manip_frame1, text="To Top",
					command=handlers.to_top, width=10)
up.pack(side="left", fill="x")
to_top.pack(side="right", fill="x")
manip_frame1.pack(side="top", fill="x")

manip_frame2 = Frame(automata_window, padx=10, pady=5)
down = Button(manip_frame2, text="Down",
					command=handlers.downwards, width=10)
to_bottom = Button(manip_frame2, text="To Bottom",
					command=handlers.to_bottom, width=10)
down.pack(side="left", fill="x")
to_bottom.pack(side="right", fill="x")
manip_frame2.pack(side="top", fill="x")

delete = Button(automata_window, text="Delete",
				command=handlers.delete_state, width=10)
delete.pack(side="top")

information = Label(automata_window, text="Information of State")
information.pack(side="top", fill="x")
info_frame = Frame(automata_window)
Label(info_frame, text="Name").grid(row=0, column=0)
state_name = Entry(info_frame)
state_name.grid(row=0, column=1)
Label(info_frame, text="Symbol").grid(row=1, column=0)
state_symbol = Entry(info_frame)
state_symbol.grid(row=1, column=1)
Label(info_frame, text="Key").grid(row=2, column=0)
state_key = Entry(info_frame)
state_key.grid(row=2, column=1)
Label(info_frame, text="Color").grid(row=3, column=0)
state_color = Label(info_frame, background="white", cursor="plus")
state_color.grid(row=3, column=1, sticky="ew")
state_color.bind('<1>', handlers.choose_color)
info_frame.pack(side="top")

ckeckbox_nums = [IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), 
							IntVar(), IntVar(), IntVar(), IntVar()]

condition = Label(automata_window, text="Condition of conversion")
condition.pack(side="top", fill="x")
condition_frame = Frame(automata_window)
Label(condition_frame, text="0: ").grid(row=0, column=0)
c_button_0 = Checkbutton(condition_frame, variable=ckeckbox_nums[0])
c_button_0.grid(row=0, column=1)
Label(condition_frame, text="1: ").grid(row=0, column=2)
c_button_1 = Checkbutton(condition_frame, variable=ckeckbox_nums[1])
c_button_1.grid(row=0, column=3)
Label(condition_frame, text="2: ").grid(row=0, column=4)
c_button_2 = Checkbutton(condition_frame, variable=ckeckbox_nums[2])
c_button_2.grid(row=0, column=5)
Label(condition_frame, text="3: ").grid(row=1, column=0)
c_button_3 = Checkbutton(condition_frame, variable=ckeckbox_nums[3])
c_button_3.grid(row=1, column=1)
Label(condition_frame, text="4: ").grid(row=1, column=2)
c_button_4 = Checkbutton(condition_frame, variable=ckeckbox_nums[4])
c_button_4.grid(row=1, column=3)
Label(condition_frame, text="5: ").grid(row=1, column=4)
c_button_5 = Checkbutton(condition_frame, variable=ckeckbox_nums[5])
c_button_5.grid(row=1, column=5)
Label(condition_frame, text="6: ").grid(row=2, column=0)
c_button_6 = Checkbutton(condition_frame, variable=ckeckbox_nums[6])
c_button_6.grid(row=2, column=1)
Label(condition_frame, text="7: ").grid(row=2, column=2)
c_button_7 = Checkbutton(condition_frame, variable=ckeckbox_nums[7])
c_button_7.grid(row=2, column=3)
Label(condition_frame, text="8: ").grid(row=2, column=4)
c_button_8 = Checkbutton(condition_frame, variable=ckeckbox_nums[8])
c_button_8.grid(row=2, column=5)
condition_frame.pack(side="top")

add_frame = Frame(automata_window, padx=10, pady=5)
add_state = Button(add_frame, text="Add", command=handlers.add, width=10)
change_state = Button(add_frame, text="Change",
						command=handlers.change, width=10)
add_state.pack(side="left", fill="x")
change_state.pack(side="right", fill="x")
add_frame.pack(side="top", fill="x")

error = Label(automata_window)
error.pack(side="top", fill="x")

side = IntVar()

size_window = Toplevel(root)
size_window.title("")
size_window.withdraw()
size_window.resizable(False, False)
size_window.protocol("WM_DELETE_WINDOW", handlers.hide_size_window)
Label(size_window, text="Current window size:").pack(side="top", fill="x")
size_label = Label(size_window)
size_label.pack(side="top", fill="x")
Label(size_window, text="New size:").pack(side="top", fill="x")
new_size = Frame(size_window)
size_x = Entry(new_size, width=5)
size_x.grid(row=0, column=0)
Label(new_size, text=" x ").grid(row=0, column=1)
size_y = Entry(new_size, width=5)
size_y.grid(row=0, column=2)
new_size.pack(side="top")
Label(size_window, text="Expansion of window:").pack(side="top", fill="x")
expansion = Frame(size_window)
r0 = Radiobutton(expansion, variable=side, value=0, indicatoron=0,
													width=2, height=1)
r0.select()
r0.grid(row=0, column=0)
r1 = Radiobutton(expansion, variable=side, value=1, indicatoron=0,
													width=2, height=1)
r1.grid(row=0, column=1)
r2 = Radiobutton(expansion, variable=side, value=2, indicatoron=0,
													width=2, height=1)
r2.grid(row=0, column=2)
r3 = Radiobutton(expansion, variable=side, value=3, indicatoron=0,
													width=2, height=1)
r3.grid(row=1, column=0)
r4 = Radiobutton(expansion, variable=side, value=4, indicatoron=0,
													width=2, height=1)
r4.grid(row=1, column=1)
r5 = Radiobutton(expansion, variable=side, value=5, indicatoron=0,
													width=2, height=1)
r5.grid(row=1, column=2)
r6 = Radiobutton(expansion, variable=side, value=6, indicatoron=0,
													width=2, height=1)
r6.grid(row=2, column=0)
r7 = Radiobutton(expansion, variable=side, value=7, indicatoron=0,
													width=2, height=1)
r7.grid(row=2, column=1)
r8 = Radiobutton(expansion, variable=side, value=8, indicatoron=0,
													width=2, height=1)
r8.grid(row=2, column=2)
expansion.pack(side="top")
Label(size_window).pack(side="top", fill="x")
apply_frame = Frame(size_window, padx=10, pady=5)
apply_size = Button(apply_frame, text="Apply", width=6,
										command=handlers.change_size)
apply_size.pack(side="left", fill="x")
close_size = Button(apply_frame, text="Close", width=6,
										command=handlers.hide_size_window)
close_size.pack(side="right", fill="x")
apply_frame.pack(side="top", fill="x")
message = Label(size_window, text="")
message.pack(side="top", fill="x")
menubar = Menu(root)
root.config(menu=menubar)

menu_file = Menu(menubar)
menu_file.add_command(label="New", command=handlers.new_file,
													accelerator="Ctrl+N")
menu_file.bind_all("<Control-n>", handlers.new_file)
menu_file.add_command(label="Open...", command=handlers.open_file,
													accelerator="Ctrl+O")
menu_file.bind_all("<Control-o>", handlers.open_file)
menu_file.add_command(label="Save...", command=handlers.save_file,
													accelerator="Ctrl+S")
menu_file.bind_all("<Control-s>", handlers.save_file)
menu_file.add_separator()
menu_file.add_command(label="Exit", command=handlers.exit,
													accelerator="Ctrl+Q")
menu_file.bind_all("<Control-q>", handlers.exit)
menubar.add_cascade(label="File", menu=menu_file)

menu_action = Menu(menubar)
menu_action.add_command(label="Start", command=handlers.start,
													accelerator="Ctrl+G")
menu_action.bind_all("<Control-g>", handlers.start)
menu_action.add_command(label="Stop", command=handlers.stop,
													accelerator="Ctrl+F")
menu_action.bind_all("<Control-f>", handlers.stop)
menu_action.add_command(label="Next Step", command=handlers.next_step,
													accelerator="Space")
menu_action.bind_all("<space>", handlers.next_step)
menu_action.add_separator()
menu_action.add_command(label="Increase speed", command=handlers.faster,
													accelerator="Alt+F")
menu_action.bind_all("<Alt-f>", handlers.faster)
menu_action.add_command(label="Decrease speed", command=handlers.slower,
													accelerator="Alt+S")
menu_action.bind_all("<Alt-s>", handlers.slower)
menu_action.add_separator()
menu_action.add_command(label="Zoom In", command=handlers.zoom_in,
													accelerator="Ctrl+Z")
menu_action.bind_all("<Control-z>", handlers.zoom_in)
menu_action.add_command(label="Zoom Out", command=handlers.zoom_out,
													accelerator="Ctrl+X")
menu_action.bind_all("<Control-x>", handlers.zoom_out)
menu_action.add_separator()
menu_action.add_command(label="Clean field", command=handlers.clean_field,
													accelerator="Ctrl+C")
menu_action.bind_all("<Control-c>", handlers.clean_field)
menu_action.add_command(label="Fill randomly",
													command=handlers.fill_randomly,
													accelerator="Ctrl+R")
menu_action.bind_all("<Control-r>", handlers.fill_randomly)
menu_action.add_separator()
menu_action.add_command(label="Change size",
													command=handlers.show_size_window,
													accelerator="Ctrl+D")
menu_action.bind_all("<Control-d>", handlers.show_size_window)
menubar.add_cascade(label="Action", menu=menu_action)

menubar.add_command(label="Automaton", command=handlers.show_automata_window)

menubar.add_command(label="Help", command=handlers.show_help_window)

root.mainloop()

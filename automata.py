"""Copyright 2010 Aydarkhanov Ruslan, Kurochkin Ilya, Rusinov Ivan

This file is part of Foobar.

Foobar is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published
by the Free Software Foundation, either version 2 of the License,
or (at your option) any later version.

Foobar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar. If not, see http://www.gnu.org/licenses/.
"""

from state import *

class Automata(object):
	def __init__(self, width=150, height=70, states=None):
		self.width = width
		self.height = height
		if states == None:
			self.states = [State("Dead", '-', "white", '0', [5]),
					State("Alive", '+', "black", '1', [0, 1] + range(4, 9))]
		else:
			self.states = states
		self.symbols = {}
		self.st_sym = {}
		for num, st in enumerate(self.states):
			self.symbols[st.symbol] = num
			self.st_sym[st.symbol] = st
		self.field = []
		for row in range(height):
			self.field.append([])
			for col in range(width):
				self.field[row].append(self.states[0].symbol)

	def next_step(self):
		changed = []
		for row in range(1, self.height - 1):
			for col in range(1, self.width - 1):
				symbol = self.field[row][col]
				num = 0
				for vert in range(row - 1, row + 2):
					for horiz in range(col - 1, col + 2):
						if self.field[vert][horiz] == symbol:
							num += 1
				if self.st_sym[symbol].next_state(num - 1):
					changed.append((row, col))
					
		for row in range(1, self.height - 1):
			symbol1 = self.field[row][0]
			symbol2 = self.field[row][self.width - 1]
			num1 = 0
			num2 = 0
			for vert in range(row - 1, row + 2):
				for horiz in [0, 1, self.width - 1]:
					if self.field[vert][horiz] == symbol1:
						num1 += 1
				for horiz in [self.width - 2, self.width - 1, 0]:
					if self.field[vert][horiz] == symbol2:
						num2 += 1
			if self.st_sym[symbol1].next_state(num1 - 1):
				changed.append((row, 0))
			if self.st_sym[symbol2].next_state(num2 - 1):
				changed.append((row, self.width - 1))
				
		for col in range(1, self.width - 1):
			symbol1 = self.field[0][col]
			symbol2 = self.field[self.height - 1][col]
			num1 = 0
			num2 = 0
			for horiz in range(col - 1, col + 2):
				for vert in [0, 1, self.height - 1]:
					if self.field[vert][horiz] == symbol1:
						num1 += 1
				for vert in [self.height - 2, self.height - 1, 0]:
					if self.field[vert][horiz] == symbol2:
						num2 += 1
			if self.st_sym[symbol1].next_state(num1 - 1):
				changed.append((0, col))
			if self.st_sym[symbol2].next_state(num2 - 1):
				changed.append((self.height - 1, col))
				
		for row, col in [(0, 0), (self.height - 1, self.width - 1),
						(0, self.width - 1), (self.height - 1, 0)]:
			symbol = self.field[row][col]
			num = 0
			for vert_long in range(row + self.height - 1, 
									row + self.height + 2):
				for horiz_long in range(col + self.width - 1, 
										col + self.width + 2):
					vert = vert_long % self.height
					horiz = horiz_long % self.width
					if self.field[vert][horiz] == symbol:
						num += 1
			if self.st_sym[symbol].next_state(num - 1):
				changed.append((row, col))
						
		for row, col in changed:
			index = (self.symbols[self.field[row][col]] + 
														1) %  len(self.states)
			self.field[row][col] = self.states[index].symbol
		return changed

	def change_size(self, value, side):
		"0-up, 1-right, 2-down, 3-left"
		new_field = []
		
		if side == 0:
			self.height += value
			for row in range(value):
				new_field.append([])
				for col in range(self.width):
					new_field[row].append(self.states[0].symbol)
			init = value
			if value < 0:
				init = 0
			for row in range(init, self.height):
				new_field.append([])
				for col in range(self.width):
					new_field[row].append(self.field[row - value][col])
					
		if side == 2:
			self.height += value
			term = value
			if value < 0:
				term = 0
			for row in range(self.height - term):
				new_field.append([])
				for col in range(self.width):
					new_field[row].append(self.field[row][col])
			for row in range(self.height - term, self.height):
				new_field.append([])
				for col in range(self.width):
					new_field[row].append(self.states[0].symbol)
					
		if side == 1:
			self.width += value
			term = value
			if value < 0:
				term = 0
			for row in range(self.height):
				new_field.append([])
				for col in range(self.width - term):
					new_field[row].append(self.field[row][col])
			for row in range(self.height):
				for col in range(self.width - term, self.width):
					new_field[row].append(self.states[0].symbol)
					
		if side == 3:
			self.width += value
			for row in range(self.height):
				new_field.append([])
				for col in range(value):
					new_field[row].append(self.states[0].symbol)
			init = value
			if value < 0:
				init = 0
			for row in range(self.height):
				for col in range(init, self.width):
					new_field[row].append(self.field[row][col - value])
		self.field = new_field
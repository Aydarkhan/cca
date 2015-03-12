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


class State(object):

	def __init__(self, name, symbol, color, key, nums):
		self.name = name
		self.symbol = symbol
		self.color = color
		self.key = key
		self.nums = nums

	def next_state(self, num):
		return num in self.nums

	def __repr__(self):
		return self.symbol + " " + self.name

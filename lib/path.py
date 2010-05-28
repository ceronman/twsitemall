# -*- coding: utf-8 -*-

# Twist'em All !
# Author: Manuel Cerón <ceronman@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import math

class Path:
	def __init__(self, mode='loop'):
		self.path = []
		self.index = 0
		self.index_incrementator = 1
		self.change_mode(mode)
		
	def next(self):
		self._next()
		return self.path[self.index]

	def next_loop(self):
		self.index = self.index + 1
		if self.index >= len(self.path)-1:
			self.index = 0

	def next_bounce(self):
		self.index = self.index + self.index_incrementator
		if self.index == 0 or self.index == len(self.path) - 1:
			self.index_incrementator = self.index_incrementator * -1
			
	def change_mode(self, mode):
		if mode == 'bounce':
			self._next = self.next_bounce
		elif mode == 'loop':
			self._next = self.next_loop
		else:
			raise Exception('wrong mode')
			
class EllipsePath(Path):
	def __init__(self, rx, ry, interval, mode='loop'):
		Path.__init__(self, mode)
		for theta in range(0, 361, interval):
			x = int(rx * math.cos(math.radians(theta)))
			y = int(ry * math.sin(math.radians(theta)))
			self.path.append((x, y))
			
class HorizontalLinePath(Path):
	def __init__(self, size, mode='loop'):
		Path.__init__(self, mode)
		for x in range(size):
			self.path.append((x, 0))
			
if __name__ == '__main__':
	import main
	main.main()

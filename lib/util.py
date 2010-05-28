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

class TrigonometricTable:
	def __init__(self, interval):
		self.cos_table = {}
		self.sin_table = {}
		self.tan_table = {}
		for i in range(0, 360+interval, interval):
			self.cos_table[i] = math.cos(math.radians(i))
			self.sin_table[i] = math.sin(math.radians(i))
			self.tan_table[i] = math.tan(math.radians(i))
	def sin(self, degrees):
		return self.sin_table[degrees]
	def cos(self, degrees):
		return self.cos_table[degrees]
	def tan(self, degrees):
		return self.tan_table[degrees]

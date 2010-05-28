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

import os
import pygame

from locals import *

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, '..', 'data'))

def filepath(prefix, filename):
	'''Determine the path to a file in the data directory.
	'''
	return os.path.join(data_dir, prefix, filename)

def load(filename, mode='rb'):
	'''Open a file in the data directory.

	"mode" is passed as the second arg to open().
	'''
	return open(os.path.join(data_dir, filename), mode)

def load_image(filename):
	image = pygame.image.load(filepath('images', filename))
	image = image.convert()
	image.set_colorkey(COLORKEY)
	return image

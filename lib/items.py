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

import pygame
from pygame.sprite import Sprite

import data
from character import Character

class Item(Character):
	def __init__(self, world_map):
		Character.__init__(self, world_map, world_map.group, world_map.items_group)
		
	def kill(self):
		Sprite.kill(self)

class TwisterUpItem(Item):
	def __init__(self, world_map):
		Item.__init__(self, world_map)
		
	def load_graphics(self):
		self.image = data.load_image('twister_up.png')
		self.rect = self.image.get_rect()
		
	def use(self, tman):
		tman.jump_energy_max += 1
		tman.jump_energy = tman.jump_energy_max
		
class LifeButterflyItem(Item):
	def __init__(self, world_map):
		Item.__init__(self, world_map)
		
	def load_graphics(self):
		self.image = data.load_image('life_butterfly.png')
		self.rect = self.image.get_rect()
		
	def use(self, tman):
		tman.life_max += 1
		tman.life = tman.life_max
		
class LifeTankItem(Item):
	def __init__(self, world_map):
		Item.__init__(self, world_map)
		
	def load_graphics(self):
		self.image = data.load_image('life_tank.png')
		self.rect = self.image.get_rect()
		
	def use(self, tman):
		tman.life = tman.life_max
		
class SpecialItem(Character):
	def __init__(self, world_map):
		Character.__init__(self, world_map, world_map.group, world_map.special_items_group)
		
	def kill(self):
		Sprite.kill(self)
		
class KeyItem(SpecialItem):
	def __init__(self, world_map):
		SpecialItem.__init__(self, world_map)
		
	def load_graphics(self):
		self.image = data.load_image('key.png')
		self.rect = self.image.get_rect()
		
	def use(self):
		self.world_map.got_key = True
		
class LockItem(SpecialItem):
	def __init__(self, world_map):
		SpecialItem.__init__(self, world_map)
		
	def load_graphics(self):
		self.image = data.load_image('lock.png')
		self.rect = self.image.get_rect()
		
	def use(self):
		self.world_map.try_won()

if __name__ == '__main__':
	import main
	main.main()

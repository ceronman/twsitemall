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
from pygame import Surface
from pygame import Rect
from pygame.sprite import Sprite, Group
from pygame.font import Font

import data
from locals import *
from items import KeyItem

class Panel:
	def __init__(self, world_map):
		self.world_map = world_map
		self.group = Group()
		self.energy_bar = EnergyBar(world_map.main_character, 15, 10, self.group)
		self.energy_bar.put(75, 13)
		self.energy_bar = LifeBar(world_map.main_character, 15, 10, self.group)
		self.energy_bar.put(75, 30)
		
		self.rect = Rect(0, 0, SCREEN_W, 40)
		self.background = data.load_image('panel.png')
		font = Font(data.filepath('fonts', 'vera.ttf'), 12)
		#font.set_bold(True)
		self.twister_text = font.render("Twister:", True, (0,0,0))
		self.life_text = font.render("Life:", True, (0,0,0))
		self.world_text = font.render("World: %s" % world_map.name, True, (0,0,0))
		
		class TimeText(Sprite):
			def __init__(self, world_map, *groups):
				Sprite.__init__(self, *groups)
				self.world_map = world_map
			def update(self, *args):
				time = self.world_map.time
				time_str = self.world_map.get_time()
				if time < 60:
					color = (170, 0, 0)
				elif time < 120:
					color = (255, 100, 0)
				else:
					color = (0, 0, 0) 
				self.image = font.render("Time: %s"% time_str , True, color)
				self.rect = self.image.get_rect()
				self.rect.move_ip(500, 0)
				
		TimeText(world_map, self.group)
		self.key = KeyItem(world_map)
		self.key.put(620, 20)
		self.key.remove(self.key.groups())
		
		
	def draw(self, screen):
		if self.world_map.got_key:
			self.key.add(self.group)
		screen.set_clip(self.rect)
		self.group.clear(screen, self.background)
		self.group.update()
		self.group.draw(screen)
		
	def draw_background(self, screen):
		screen.blit(self.background, (0,0))
		screen.blit(self.twister_text, (10, 0))
		screen.blit(self.life_text, (10, 17))
		screen.blit(self.world_text, (500, 17))
		
class Bar(Sprite):
	def __init__(self, factor, height, *groups):
		Sprite.__init__(self, *groups)
		self.factor = factor
		self.height = height
		self.put(0, 0)
		self.create_image()
		
	def update(self, *args):
		self.create_image()
		self.update_color()
		self.update_size()
		self.create_bar()
		self.fill_image()
		
	def get_max_value(self):
		pass
		
	def get_value(self):
		pass
		
	def create_image(self):
		self.size = (self.get_max_value() * self.factor)
		self.image = Surface((self.size, self.height))
		self.image = self.image.convert()
		self.image.set_colorkey(COLORKEY)
		self.rect = self.image.get_rect()
		self.rect.left = self.x
		self.rect.bottom = self.y
		
	def update_color(self):
		color_value = int(255 * self.get_value() / self.get_max_value() )
		if 200 <= color_value <= 255:
			self.color = (0, color_value, 0)
		elif 90 <= color_value < 200:
			self.color = (255, color_value + 55, 0)
		else:
			self.color = (255-color_value, 0, 0)
		
		
	def update_size(self):
		self.size = int(self.size * self.get_value() / self.get_max_value() )
		
	def create_bar(self):
		self.bar = Surface((self.size, 10))
		self.bar.fill(self.color)
	
	def fill_image(self):
		self.image.fill(COLORKEY)
		rect = self.bar.get_rect()
		rect.bottom = self.image.get_rect().bottom
		self.image.blit(self.bar, rect)
		self.draw_border()
	
	def put(self, x, y):
		self.x = x
		self.y = y
		
	def draw_border(self):
		rect = self.image.get_rect()
		pygame.draw.rect(self.image, (0, 0, 0), rect, 1)
		
class EnergyBar(Bar):
	def __init__(self, tman, factor, height, *groups):
		self.tman = tman
		Bar.__init__(self, factor, height, *groups)
		
	def get_max_value(self):
		return self.tman.jump_energy_max
		
	def get_value(self):
		return self.tman.jump_energy
		
		
class LifeBar(Bar):
	def __init__(self, tman, factor, height, *groups):
		self.tman = tman
		Bar.__init__(self, factor, height, *groups)
		
	def get_max_value(self):
		return self.tman.life_max
		
	def get_value(self):
		return self.tman.life
		
if __name__ == '__main__':
	import main
	main.main()

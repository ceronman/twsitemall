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

from locals import *
import data

class Character(Sprite):
	def __init__(self, world_map, *groups):
		Sprite.__init__(self, *groups)
		self.load_graphics()
		self.configure()
		self.world_map = world_map
		self.death_animation = DeathAnimation(self)
		
	def load_graphics(self):
		pass
	
	def configure(self):
		self.speed_y = 0
		self.speed_x = 0
		self.MAX_SPEED_X = 10
		self.MIN_SPEED_X = -10
		self.MAX_SPEED_Y = 30
		self.MIN_SPEED_Y = -30
		
	def limit_speed(self):
		self.speed_x = min(self.speed_x, self.MAX_SPEED_X)
		self.speed_x = max(self.speed_x, self.MIN_SPEED_X)
		self.speed_y = min(self.speed_y, self.MAX_SPEED_Y)
		self.speed_y = max(self.speed_y, self.MIN_SPEED_Y)
		
	def kill(self):
		self.death_animation.die()
		
	def on_death(self):
		Sprite.kill(self)
	
	def put(self, x, y):
		self.rect.centerx = x
		self.rect.centery = y
		
	def map_collision_left(self, stop=True):
		points = [self.rect.centery+5, self.rect.centery, self.rect.centery-5]
		tiles = [self.world_map.tile_at(self.rect.left, point) for point in points ]
		for tile, rect in tiles:
			if tile is not None:
				if stop:
					self.rect.left = rect.right+1
				return True
		return False
		
	def map_collision_right(self, stop=True):
		points = [self.rect.centery+5, self.rect.centery, self.rect.centery-5]
		tiles = [self.world_map.tile_at(self.rect.right, point) for point in points ]
		for tile, rect in tiles:
			if tile is not None:
				if stop:
					self.rect.right = rect.left-1
				return True
		return False
		
	def map_collision_top(self, stop=True):
		tile, rect = self.world_map.tile_at(self.rect.centerx, self.rect.top-1)
		if tile is not None:
			if stop:
				self.rect.top = rect.bottom+1
			return True
		return False
		
	def map_collision_bottom(self, stop=True):
		tile, rect = self.world_map.tile_at(self.rect.centerx, self.rect.bottom+1)
		if tile is not None:
			if stop:
				self.rect.bottom = rect.top-1
			return True
		return False
		
class BasicBullet(Sprite):
	image = None
	def __init__(self, world_map, x, y, *groups):
		Sprite.__init__(self, *groups)
		self.startx = x
		self.starty = y
		self.put(x, y)
		self.world_map = world_map
		
	def put(self, x, y):
		self.rect.centerx = x
		self.rect.centery = y
		
	def check_bounds(self):
		tile, rect = self.world_map.tile_at(self.rect.centerx, self.rect.centery)
		
		death = (self.rect.centerx < 0 or self.rect.centerx > self.world_map.rect.right
				or self.rect.centery < 0 or self.rect.centery > self.world_map.rect.bottom
				or (tile is not None and tile != 0))
				
		if death:
			self.kill()

class DeathAnimation:
	def __init__(self, sprite):
		self.sprite = sprite
		self.dying = False
		self.generate_images()
		
	def generate_images(self):
		image = self.sprite.image
		self.images = []
		self.rects = []
		for angle in range(0, 361, 36):
			new_image = pygame.transform.rotate(image, angle)
			new_image = new_image.convert()
			new_image.set_colorkey(COLORKEY)
			self.images.append(new_image)
			self.rects.append(new_image.get_rect())
			
		self.index = 0
		self.size = len(self.images)-1
		
	def update(self):
		self.sprite.image = self.images[self.index]
		self.sprite.rect = self.rects[self.index]
		self.index += 1
		if self.index >= self.size:
			self.sprite.on_death()
			
	def die(self):
		for rect in self.rects:
			rect.centerx = self.sprite.rect.centerx
			rect.centery = self.sprite.rect.centery
		self.dying = True

class SpecialTile(Character):
	def __init__(self, world_map, tile_index):
		self.image = data.load_image('special_block.png')
		self.rect = self.image.get_rect()
		Character.__init__(self, world_map, world_map.group, world_map.special_block_group)
		self.tile_index = tile_index
		
	def put_on_tile(self, tilex, tiley):
		self.rect.x, self.rect.y = self.world_map.tile_to_pixel(tilex, tiley)
		
	def on_death(self):
		self.world_map.tiles[self.tile_index] = None
		Sprite.kill(self)
		
	def update(self, *args):
		if self.death_animation.dying:
			self.death_animation.update()
			return
	
if __name__ == '__main__':
	import main
	main.main()
	

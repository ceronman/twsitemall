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

import random

import pygame
from pygame import Surface
from pygame import Rect
from pygame.sprite import AbstractGroup, Group

import data
from character import SpecialTile
from enemies import Fly, SpikeSpawn, Defender
from path import EllipsePath, HorizontalLinePath
from items import TwisterUpItem, LifeButterflyItem, LifeTankItem, KeyItem, LockItem
from tman import TMan
from locals import *

class Map:
	TILE_SIZE = (30, 30)
	def __init__(self, view_size):
		self.view_rect = Rect((0,0), view_size)
		self.update_rects = []
		self.previous_rects = []
		self.actual_rects = []
		self.group = MapGroup(self)
		self.special_block_group = Group()
		self.bullet_group = Group()
		self.enemies_group = Group()
		self.items_group = Group()
		self.enemy_bullet_group = Group()
		self.special_items_group = Group()
		self.main_character = TMan(self, self.group)
		
		self.got_key = False
		self.won = False
		self.finish = False
		
	def try_won(self):
		if self.got_key:
			self.won = True
		
	def load(self, map_name):
		tile1 = data.load_image('tile-solid-1.png')
		tile2 = data.load_image('tile-solid-2.png')
		tilenull = data.load_image('tile-null.png')
		
		mapfile = open(data.filepath('maps', map_name))
		
		self.name = mapfile.readline().strip()
		
		self.time = float(mapfile.readline().strip())
		
		bg = mapfile.readline().strip()
		self.background = data.load_image('background-%s.png' % bg)

		def append_tile(code, tilex, tiley):
			def add(c, tile,*args):
				obj = c(self, *args)
				x, y = self.tile_center(tilex, tiley)
				obj.put(x, y)
				self.tiles.append(tile)

			if code == '1':
				self.tiles.append(tile1)
			elif code == '2':
				self.tiles.append(tile2)
			elif code == 'S':
				add(SpecialTile, 0, len(self.tiles))
			elif code == 'a':
				add(Fly, None, EllipsePath(20, 20, 10), random.randint(25, 75))
			elif code == 'b':
				add(SpikeSpawn, None, 4, 50)
			elif code == 'c':
				add(Defender, None, HorizontalLinePath(100, 'bounce'), random.randint(50, 100))
			elif code == 't':
				add(TwisterUpItem, None)
			elif code == 'L':
				add(LifeButterflyItem, None)
			elif code == 'l':
				add(LifeTankItem, None)
			elif code == 'z':
				add(KeyItem, None)
			elif code == 'Z':
				add(LockItem, None)
			elif code == 'X':
				self.tiles.append(None)
				x, y = self.tile_center(tilex, tiley)
				self.main_character.put(x, y)
			else:
				self.tiles.append(None)
	
		
		height = 0
		width = 0
		self.tiles = []
		for line in mapfile:
			line = line.strip()
			width = len(line)
			for char, i in zip(line, range(len(line))):
				append_tile(char, i, height)
			height += 1

		self.width = width
		self.height = height
		
		tw, th = self.TILE_SIZE
		right, bottom = tw*width, th*height
		
		self.rect = Rect((0, 0), (right, bottom))
		
	def get_time(self):
		return '%d:%d' % (int(self.time/60), int(self.time%60))
		
	def get_tile(self, x, y): 
		if x<0 or y<0 or x>=self.width or y>=self.height:
			return None
		return self.tiles[y*self.width+x]
		
	def pixel_to_tile(self, x, y):
		tw, th = self.TILE_SIZE
		tile_x = x / tw
		tile_y = y / th
		return (tile_x, tile_y)
		
	def tile_to_pixel(self, tilex, tiley):
		tw, th = self.TILE_SIZE
		return tilex * tw, tiley * th
		
	def tile_center(self, tilex, tiley):
		tw, th = self.TILE_SIZE
		x, y = self.tile_to_pixel(tilex, tiley)
		return (x+tw/2, y+th/2)
		
	def tile_rect(self, tilex, tiley):
		x, y = self.tile_to_pixel(tilex, tiley)
		return Rect((x, y), self.TILE_SIZE)
		
	def tile_at(self, x, y):
		tile_x, tile_y = self.pixel_to_tile(x, y)
		return self.get_tile(tile_x, tile_y), self.tile_rect(tile_x, tile_y)
	
	def scroll(self):
		spritex = self.main_character.rect.centerx
		spritey = self.main_character.rect.centery
		width_space = self.view_rect.width * 1 / 3
		height_space = self.view_rect.height * 1 / 3
		
		scroll_right_point = self.view_rect.right - width_space
		if spritex > scroll_right_point:
			self.move_view(spritex - scroll_right_point, 0)
			
		scroll_left_point = self.view_rect.left + width_space
		if spritex < scroll_left_point:
			self.move_view(spritex - scroll_left_point, 0)
			
		scroll_top_point = self.view_rect.top + height_space
		if spritey < scroll_top_point:
			self.move_view(0, spritey - scroll_top_point)
			
		scroll_bottom_point = self.view_rect.bottom - height_space
		if spritey > scroll_bottom_point:
			self.move_view(0, spritey - scroll_bottom_point)

	def update(self, *args):
		self.group.update(*args)
		self.scroll()
		self.check_collisions()
		self.time = self.time - (1.0/FPS)
		self.check_status()
		
	def check_status(self):
		self.finish = self.main_character.death() or self.won or self.time <= 0

	def check_collisions(self):
		tman = self.main_character
		pygame.sprite.groupcollide(self.bullet_group, self.enemies_group, True, True)
		pygame.sprite.groupcollide(self.special_block_group, self.bullet_group, True, True)
		pygame.sprite.groupcollide(self.special_block_group, self.enemy_bullet_group, False, True)
		pygame.sprite.groupcollide(self.enemy_bullet_group, self.bullet_group, True, True)
		enemies = pygame.sprite.spritecollide(tman, self.enemies_group, not tman.blinking)
		bullets = pygame.sprite.spritecollide(tman, self.enemy_bullet_group, not tman.blinking)
		items = pygame.sprite.spritecollide(tman, self.items_group, True)
		special_items = pygame.sprite.spritecollide(tman, self.special_items_group, True)
		
		for enemy in enemies:
			tman.enemy_touched(enemy)
		
		for bullet in bullets:
			tman.bullet_touched()
			
		for item in items:
			tman.item_touched(item)
			
		for item in special_items:
			item.use()
	
	
	def draw(self, surface, draw_position):
		tw, th = self.TILE_SIZE
		tile_x1, tile_y1 = self.pixel_to_tile(self.view_rect.left, self.view_rect.top)
		tile_x2, tile_y2 = self.pixel_to_tile(self.view_rect.right, self.view_rect.bottom)
		
		dx, dy = draw_position
		
		clip_rect = Rect(draw_position, (self.view_rect.width, self.view_rect.height))
		surface.set_clip(clip_rect)
				
		self.actual_rects = []
		self.update_rects = self.previous_rects
		
		if len(self.previous_rects) == 0:
			self.previous_rects.append(clip_rect)
		
		for rect in self.previous_rects:
			area = rect.move(-dx, -dy)
			surface.blit(self.background, rect, area)

		for x in range(tile_x1, tile_x2 + 1):
			for y in range(tile_y1, tile_y2 + 1):
				
				pos_x = dx + x * tw - self.view_rect.left
				pos_y = dy + y * th - self.view_rect.top
				image = self.get_tile(x, y)
				if image is not None and image != 0:
					surface.blit(image, (pos_x, pos_y))
					self.actual_rects.append(image.get_rect().move(pos_x, pos_y))
					
		self.actual_rects += self.group.draw(surface, draw_position)
					
		surface.set_clip(None)
		
		self.update_rects += self.actual_rects
		self.previous_rects = self.actual_rects
		
	def move_view(self, x, y):
		self.view_rect.move_ip(x, y)
		
		self.view_rect.top = max(self.rect.top, self.view_rect.top)
		self.view_rect.left = max(self.rect.left, self.view_rect.left)
		self.view_rect.right = min(self.rect.right, self.view_rect.right)
		self.view_rect.bottom = min(self.rect.bottom, self.view_rect.bottom)
		
	def goto_bottom(self):
		self.view_rect.bottom = self.rect.bottom
		
	def goto_left(self):
		self.view_rect.left = self.rect.left
		
	def goto_right(self):
		self.view_rect.right = self.rect.right

	def goto_top(self):
		self.view_rect.right = self.rect.right
		
	def set_main_character(self, sprite):
		self.main_character = sprite

class MapGroup(AbstractGroup):
	def __init__(self, owner_map, *sprites):
		AbstractGroup.__init__(self)
		self.add(*sprites)
		self.owner_map = owner_map
		owner_map.group = self
		
	def draw(self, surface, dpos):
		dx, dy = dpos
		rects = []
		sprites = self.sprites()
		surface_blit = surface.blit
		for spr in sprites:
			newrect = spr.rect.move(-self.owner_map.view_rect.x+dx, -self.owner_map.view_rect.y+dy)
			self.spritedict[spr] = surface_blit(spr.image, newrect)
			rects.append(newrect)
		return rects

if __name__ == '__main__':
	import main
	main.main()


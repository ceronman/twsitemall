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
import random

import pygame

import data
from character import Character, BasicBullet
from locals import *

class Fly(Character):
	def __init__(self, world_map, path, shoottime):
		Character.__init__(self, world_map, world_map.group, world_map.enemies_group)
		self.path = path
		self.x = 0
		self.y = 0
		self.shoottime = shoottime
		self.frame_counter = 0
		
	def configure(self):
		Character.configure(self)
		self.frame_incrementator = 1
	
	def put(self, x, y):
		self.x = x
		self.y = y

	def load_graphics(self):
		self.frames = []
		self.actual_frame = 0
		for i in range(3):
			self.frames.append(data.load_image('fly-%d.png' % (i+1)))
		self.image = self.frames[self.actual_frame]
		self.rect = self.image.get_rect()
	def update(self, *args):
		if self.death_animation.dying:
			self.death_animation.update()
			return
		self.change_frame()
		self.move_to_path()
		if self.time_to_shoot():
			self.shoot()
		self.image = self.frames[self.actual_frame]
		
	def change_frame(self):
		self.actual_frame = self.actual_frame + self.frame_incrementator
		if self.actual_frame == 0 or self.actual_frame == 2:
			self.frame_incrementator = self.frame_incrementator * -1
			
	def move_to_path(self):
		px, py = self.path.next()
		self.rect.centerx = self.x + px
		self.rect.centery = self.y + py
	
	def time_to_shoot(self):
		self.frame_counter += 1
		if self.frame_counter % self.shoottime == 0:
			return True
		return False
		
	def shoot(self):
		FlyDribble(self.world_map, self.rect.centerx, self.rect.bottom)
		
class FlyDribble(BasicBullet):
	image = None
	def __init__(self, world_map, x, y):
		if FlyDribble.image is None:
			FlyDribble.image = data.load_image("bullet-2.png")
		self.rect = self.image.get_rect()	
		BasicBullet.__init__(self, world_map, x, y, world_map.group, world_map.enemy_bullet_group)
		
		self.speed = 5
		
	def update(self, *args):
		self.rect.move_ip(0, self.speed)
		self.check_bounds()
		
class Laser(BasicBullet):
	image = None
	def __init__(self, world_map, defender, side):
		if Laser.image is None:
			Laser.image = data.load_image("bullet-3.png")
		self.rect = self.image.get_rect()	
		
		x = defender.rect.centerx
		y = defender.rect.centery - 10
		self.side = side
		BasicBullet.__init__(self, world_map, x, y, world_map.group, world_map.enemy_bullet_group)
		self.speed = 8 * self.side
		
	def update(self, *args):
		self.rect.move_ip(self.speed, 0)
		self.check_bounds()
		
class Defender(Fly):
	def __init__(self, world_map, path, shoottime):
		Fly.__init__(self, world_map, path, shoottime)
		self.life = 3
		
	def load_graphics(self):
		self.frames = []
		self.actual_frame = 0
		for i in range(2):
			self.frames.append(data.load_image('defender-%d.png' % (i+1)))
		self.image = self.frames[self.actual_frame]
		self.rect = self.image.get_rect()
	
	def change_frame(self):
		self.actual_frame = self.actual_frame + 1
		if self.actual_frame == 2:
			self.actual_frame = 0
			
	def shoot(self):
		Laser(self.world_map, self, -1)
		Laser(self.world_map, self, 1)
		
	def update(self, *args):
		if self.death_animation.dying:
			self.death_animation.update()
			return
		Fly.update(self)
		self.image = self.frames[self.actual_frame].copy()
		self.image.blit(self.frames[self.actual_frame], (0,0))
		self.draw_life(self.image)
		
	def draw_life(self, surface):
		start_pos = 10, self.rect.height - 8
		end_pos = start_pos[0] + self.life*(self.rect.width-20)/3, start_pos[1]
		pygame.draw.line(surface, (100, 0, 0), start_pos, end_pos, 3)
		
	def kill(self):
		self.life -= 1
		if self.life == 0:
			Character.kill(self)
			
		
class Spike(Character):
	def __init__(self, world_map, energy, side):
		self.side = side
		self.energy = energy
		Character.__init__(self, world_map, world_map.group, world_map.enemies_group)

	def load_graphics(self):
		self.frames = []
		self.actual_frame = 0
		for i in range(4):
			self.frames.append(data.load_image('spike-%d.png' % (i+1)))
		self.image = self.frames[self.actual_frame]
		self.rect = self.image.get_rect()

	def change_frame(self):
		self.actual_frame = self.actual_frame + 1
		if self.actual_frame == 4:
			self.actual_frame = 0
			
	def configure(self):
		Character.configure(self)
		self.speed_x = 5 * self.side
		self.side
		self.speed_y = 0
		self.gravity = 1
			
	def update(self, *args):
		if self.death_animation.dying:
			self.death_animation.update()
			return
		self.change_frame()
		self.move()
		self.image = self.frames[self.actual_frame]
		
	def move(self):
		self.speed_y = self.speed_y + self.gravity
		self.rect.move_ip(self.speed_x, self.speed_y)
		self.check_map_collisions()
		
	def check_map_collisions(self):
		if self.map_collision_bottom():
			self.speed_y = self.energy
		if self.map_collision_top():
			self.speed_y = 0
		
		if self.map_collision_left() or self.map_collision_right():
			self.speed_x = self.speed_x * -1
			
class SpikeSpawn(Character):
	def __init__(self, world_map, number, frames):
		self.spikes = [None]*number
		self.frame_count = 0
		self.frames = frames
		self.number = number
		Character.__init__(self, world_map, world_map.group)
		
	def load_graphics(self):
		self.image = data.load_image('hole.png')
		self.rect = self.image.get_rect()
		
	def update(self, *args):
		self.frame_count += 1
		room = self.room()
		if self.frame_count % self.frames == 0 and room >= 0:
			side = [-1, 1][random.randint(0,1)]
			energy = random.randint(-20, -10)
			wmap = self.world_map
			spike = Spike(wmap, energy, side)
			spike.put(self.rect.centerx, self.rect.centery)
			self.spikes[room] = spike
		
	def room(self):
		for i in range(self.number):
			spike = self.spikes[i]
			if spike is None or not spike.alive():
				return i
		return -1
if __name__ == '__main__':
	import main
	main.main()

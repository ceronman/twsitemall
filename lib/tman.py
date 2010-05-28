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

import pygame
from pygame.locals import *
from pygame.sprite import Sprite, Group
from pygame import Surface

import data
from character import Character, BasicBullet
from locals import *

class TMan(Character):

	def __init__(self, world_map, *groups):
		Character.__init__(self, world_map, *groups)

	def configure(self):
		Character.configure(self)
		self.rect.x, self.rect.y = 10, 1000
		self.gravity = 1
		self.acceleration_x = 0
		self.jumping = False
		self.blinking = False
		
		self.jump_energy_max = 3
		self.jump_energy = self.jump_energy_max
		self.life_max = 5
		self.life = self.life_max
		
		self.weapon = Weapon(self)
		
		self.JUMP_SPEED = 10
		
	def load_graphics(self):
				
		degrees = [-90, -65, -45, -20, 0, 20, 45, 65, 90]
		degree_images = []
		for degree in degrees:
			image = data.load_image('tman_arm_%d.png' % degree)
			degree_images.append(image)
			
		twisters = range(4)
		twister_images = []
		for twister in twisters:
			image = data.load_image('tman_twister_%d.png' % (twister + 1))
			twister_images.append(image)
			
		torso_image = data.load_image('tman_torso.png')
		size = torso_image.get_rect().width, torso_image.get_rect().height
		
		self.frames = {}
		for degree_image, degree in zip(degree_images, degrees):
			self.frames[degree] = {}
			for twister_image, twister in zip(twister_images, twisters):
				self.frames[degree][twister] = {}
				image = Surface(size)
				image = image.convert()
				image.fill(COLORKEY)
				image.set_colorkey(COLORKEY)
				image.blit(torso_image, (0,0))
				image.blit(twister_image, (0,0))
				image.blit(degree_image, (0,0))      
				self.frames[degree][twister]['right'] = image
				image = pygame.transform.flip(image, True, False)
				self.frames[degree][twister]['left'] = image
		
		self.degree = 0
		self.side = 'right'
		self.twister = 0
		self.image = self.frames[self.degree][self.twister][self.side]
		self.rect = self.image.get_rect()
		
	def death(self):
		death = (self.rect.right < 0 or self.rect.left > self.world_map.rect.width
				or self.rect.bottom < 0 or self.rect.top > self.world_map.rect.height
				or self.life <= 0)
		return death
		
	def update(self, *args):
		self.keys_actions(args[0])
		self.frame_actions()
		self.move()
		self.weapon.aim()
		
	def frame_actions(self):
		
		if self.blinking:
			self.blink()
			return 

		if self.speed_x != 0:
			self.swap_twister()
		self.image = self.frames[self.degree][self.twister][self.side]
		
	def keys_actions(self, keys):
		if keys[K_LEFT]:
			self.move_left()
		if keys[K_RIGHT]:
			
			self.move_right()
		if not keys[K_RIGHT] and not keys[K_LEFT]:
			self.stop()
		if keys[K_UP]:
			self.weapon.move_aim_up()
		if keys[K_DOWN]:
			self.weapon.move_aim_down()
		if keys[K_SPACE]:
			self.start_jump()
		else:
			self.stop_jump()
			
		if keys[K_b]:
			self.weapon.shoot()
		else:
			self.weapon.reload_shoot()
		if keys[K_w]:
			self.start_blink(100)
			
		if keys[K_q]:
			self.world_map.won = True
		
	def move(self):
		if self.jumping:
			self.jump()
		else:
			self.speed_y = self.speed_y + self.gravity
		
		if self.on_ground():
			self.increase_jump_energy()
		self.speed_x = self.speed_x + self.acceleration_x
		self.limit_speed()
		self.rect.move_ip(self.speed_x, self.speed_y)
		
		self.check_map_collisions()
		
	def check_map_collisions(self):
		if self.map_collision_bottom():
			self.apply_friction()
			self.jumping = False
			self.speed_y = 0
		if self.map_collision_top():
			self.apply_friction()
			self.speed_y = 0
		
		if self.map_collision_left() or self.map_collision_right():
			self.speed_x = 0
		
	def apply_friction(self):
		if self.speed_x == 0:
			return 
		if self.speed_x > 0:
			self.speed_x = self.speed_x - 1
		else:
			self.speed_x = self.speed_x + 1
		
	def swap_twister(self):
		self.twister = self.twister + 1
		if self.twister > 3:
			self.twister = 1
			
	def change_to_left(self):
		self.side = 'left'
	
	def change_to_right(self):
		self.side = 'right'
			
	def move_left(self):
		self.change_to_left()
		self.acceleration_x = -2
		
	def move_right(self):
		self.change_to_right()
		self.acceleration_x = 2
		
	def stop(self):
		self.acceleration_x = 0
		
	def start_jump(self):
		if self.can_jump():
			self.jumping = True
	
	def stop_jump(self):
		self.jumping = False
		
	def can_jump(self):
		return (not self.jumping) and (self.jump_energy > 0) 
		
	def jump(self):
		self.speed_y = -self.JUMP_SPEED
		self.decrease_jump_energy()
		if self.jump_energy == 0:
			self.stop_jump()
		
	def increase_jump_energy(self):
		self.jump_energy = min(self.jump_energy + 1, self.jump_energy_max)
		
	def decrease_jump_energy(self):
		self.jump_energy = max(self.jump_energy - 1, 0)
			
	def on_ground(self):
		tile, rect = self.world_map.tile_at(self.rect.centerx, self.rect.bottom+1)
		return tile is not None
		
	def bullet_touched(self):
		if self.blinking: 
			return
		self.life = max(self.life -1, 0)
		self.start_blink(50)
		
	def item_touched(self, item):
		if self.blinking: 
			self.blinking = False
		
		item.use(self)
		
	def enemy_touched(self, enemy):
		if self.blinking: 
			return
		self.life = max(self.life -1, 0)
		
		if enemy.rect.centerx > self.rect.centerx:
			self.rect.right = enemy.rect.left-1
			self.speed_x = -5
		else:
			self.rect.left = enemy.rect.right+1
			self.speed_x = -5
		self.start_blink(50)
			
	def start_blink(self, time):
		self.aceleration_x = 0
		self.blinking = True
		self.blank_image = self.image.copy()
		self.blank_image.fill(COLORKEY)
		self.frame_counter = 0
		self.blink_time  = time
		
	def blink(self):
		self.frame_counter += 1
		if self.frame_counter % 2 == 0:
			self.image = self.blank_image
		else:
			self.image = self.frames[self.degree][self.twister][self.side]
		
		if self.frame_counter > self.blink_time:
			self.blinking = False

class Weapon(Sprite):
	
	def __init__(self, owner):
		Sprite.__init__(self, *owner.groups())
		self.owner = owner
		self.image = data.load_image('aim.png')
		self.rect = self.image.get_rect()
		self.angle = 0
		self.interval = 10
		self.distance = 40
		self.shooting = False

	def aim(self, *args):
		if self.owner.side == 'left':
			side_factor = -1
		else:
			side_factor = 1
		dy = math.sin(math.radians(self.angle)) * self.distance * -1
		dx = math.cos(math.radians(self.angle)) * self.distance * side_factor
		r = self.owner.rect
		self.rect.centerx = r.centerx + dx
		self.rect.centery = (r.centery-7) + dy #7 as a small offset
		
	def move_aim_up(self):
		self.angle = min(self.angle + self.interval, 90)
		self.change_degree()
	
	def move_aim_down(self):
		self.angle = max(self.angle - self.interval, -90)
		self.change_degree()

	def change_degree(self):
		if -90<=self.angle<-80:
			self.owner.degree = -90
		if -80<=self.angle<-55:
			self.owner.degree = -65
		if -55<=self.angle<-35:
			self.owner.degree = -45
		if -35<=self.angle<-10:
			self.owner.degree = -20
		if -10<=self.angle<10:
			self.owner.degree = 0
		if 10<=self.angle<35:
			self.owner.degree = 20
		if 35<=self.angle<55:
			self.owner.degree = 45
		if 55<=self.angle<80:
			self.owner.degree = 65
		if 80<=self.angle<=90:
			self.owner.degree = 90
			
	def shoot(self):
		if not self.shooting:
			x, y = self.rect.centerx, self.rect.centery
			
			Bullet(self.owner.world_map, x, y, self.angle, self.owner.side)
			self.shooting = True
		
	def reload_shoot(self):
		self.shooting = False

class Bullet(BasicBullet):
	image = None
	def __init__(self, world_map, x, y, angle, side):
		if Bullet.image is None:
			Bullet.image = data.load_image("bullet-1.png")
		
		self.rect = self.image.get_rect()
		BasicBullet.__init__(self, world_map, x, y, world_map.group, world_map.bullet_group)
		
		self.side = side
		
		self.vector_x = math.cos(math.radians(angle))
		self.vector_y = math.sin(math.radians(angle))
		self.distance = 1
		self.speed = 20
		
	def update(self, *args):
		self.distance = self.distance + self.speed
		if self.side == 'left':
			side_factor = -1
		else:
			side_factor = 1
		x = self.startx + int(self.vector_x * self.distance) * side_factor
		y = self.starty + int(self.vector_y * self.distance) * -1
		self.put(x, y)
		self.check_bounds()
		

if __name__ == '__main__':
	import main
	main.main()

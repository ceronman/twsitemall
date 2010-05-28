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

import sys

import pygame
from pygame.locals import *
from pygame.sprite import Group
from pygame.font import Font
from pygame import Rect

import data
from locals import *
from map import Map
from panel import Panel

maps = ['world-%d.map' % (i+1) for i in range(4)] 

class Application:
	def init(self):
		pygame.init()
		self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
		self.clock = pygame.time.Clock()
		pygame.display.set_caption("Twist'em All !")
		pygame.time.set_timer(USEREVENT, 1000)
		self.font = Font(data.filepath('fonts', 'vera.ttf'), 48)
		self.font.set_bold(True)

	def run(self):
		option = 0
		items = ['Play', 'Quit', 'Help']
		menu = Menu(400, 200, 25, 40, (255,0,0), (0, 0,0), 'title-background.png', items)
		menu.init()
		map_number = 0
		won = False
		while option != 1 and map_number < 4:
			self.screen.set_clip(Rect(0, 0, SCREEN_W, SCREEN_H))
			if not won:
				option = menu.run(self.screen)
			if option == 0:
				w_map = Map((640, 440))
				w_map.load(maps[map_number])
				panel =  Panel(w_map)
				won = self.run_map(w_map, panel)
				if won:
					map_number += 1
		if map_number >= 4:
			menu = Menu(300, 200, 18, 40, (255,0,0), (0, 0,0), 'title-background.png', ['You finished the game', 'More levels comming soon...'])
			menu.init()
			menu.run(self.screen)
	
	def run_map(self, world_map, panel):
		panel.draw_background(self.screen)
		while not world_map.finish:
			for event in pygame.event.get():
				if event.type == QUIT:
					sys.exit()
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						return False
				if event.type == USEREVENT:
					print 'Frames per second:', self.clock.get_fps()
			keys = pygame.key.get_pressed()

			world_map.update(keys)
			world_map.draw(self.screen, (0, 40))
			
			panel.draw(self.screen)

			pygame.display.update(world_map.update_rects)
			pygame.display.update(panel.rect)
			
			self.clock.tick(FPS)
		
		if world_map.won:
			aditional = ''
			if world_map.main_character.life == world_map.main_character.life_max:
				aditional = ' (Perfect)'
			text = self.font.render('You Won !%s' % aditional , True, (0, 170, 0))
		else:
			text = self.font.render('You Lost !', True, (170, 0, 0))
		
		rect = text.get_rect()
		rect.centerx = SCREEN_W / 2
		rect.centery = SCREEN_H / 2
		
		self.screen.set_clip(Rect(0, 0, SCREEN_W, SCREEN_H))
		self.screen.blit(text, rect)
		pygame.display.update()
		
		done = False
		pygame.time.wait(2000)
		
		return world_map.won

class Menu:
	def __init__(self, x, y, fontsize, space, color_fg, color_bg, background, titles):
		self.titles = titles
		self.images = []
		self.rects = []
		self.himages = []
		self.color_fg = color_fg
		self.color_bg = color_bg
		self.space = space
		self.background = data.load_image(background)
		self.index = 0
		self.x = x
		self.y = y
		self.font = Font(data.filepath('fonts', 'vera.ttf'), fontsize)
		self.font.set_bold(True)
		self.fonth = Font(data.filepath('fonts', 'vera.ttf'), fontsize+5)
		self.fonth.set_bold(True)
		
	def init(self):
		
		dy = 0
		for title in self.titles:
			image = self.font.render(title, True, self.color_bg)
			himage = self.fonth.render(title, True, self.color_fg)
			rect = image.get_rect()
			rect.move_ip(self.x, self.y + dy)
			dy += rect.height + self.space
			self.images.append(image)
			self.himages.append(himage)
			self.rects.append(rect)
				
	def run(self, screen):
		def blit(screen):
			screen.blit(self.background, (0,0))
			for image, rect in zip(self.images, self.rects):
				if image != self.images[self.index]:
					screen.blit(image, rect)
			screen.blit(self.himages[self.index], self.rects[self.index])
			pygame.display.update()
		
		done = False
		blit(screen)
		while not done:
			for event in pygame.event.get():
				if event.type == QUIT:
					sys.quit()
				if event.type == KEYDOWN:
					if event.key == K_DOWN:
						self.index = min(self.index+1, len(self.images)-1)
						blit(screen)
					if event.key == K_UP:
						self.index = max(self.index-1, 0)
						blit(screen)
					if event.key == K_RETURN:
						done = True
		return self.index

if __name__ == '__main__':
	import main
	main.main()

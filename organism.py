from entity import Entity
from pygame import Surface, Rect
from random import randint

import pygame
from pygame import sprite

DIRECTIONS = {
	(-1, -1), (0, -1), (1, -1),
	(-1, 0), (1, 0),
	(-1, 1), (0, 1), (1, 1)
}

class Organism(Entity):
	def __init__(self, x, y, level, color = None):
		Entity.__init__(self)
		self.image = Surface((16, 16))
		if color: self.image.fill(color)
		self.image.convert()
		self.rect = Rect(x, y, 16, 16)
		self.level = level

	def random_adjacent_coords(self, clear = False):
		x, y = self.tile_coords()
		off_x, off_y = 0, 0
		while (off_x == 0 and off_y == 0) or not self.level.clear_at_tile(x + off_x, y + off_y):
			off_x = 1 - randint(0, 2)
			off_y = 1 - randint(0, 2)
		return x + off_x, y + off_y

	def adjacent_entities(self):
		adjacent_entities = []
		x, y = self.tile_coords()
		for d in DIRECTIONS:
			entity = self.level.entity_at(x + d[0], y + d[1])
			if entity: adjacent_entities.append(entity)
		return adjacent_entities
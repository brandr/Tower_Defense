import pygame
from pygame import *
#from pygame import Surface, Color, Rect

import os
import math

DEFAULT_COLORKEY = Color("#FF00FF")

class Entity(pygame.sprite.Sprite):
	def __init__(self, level, entity_key):
		pygame.sprite.Sprite.__init__(self)
		self.level = level
		self.time_counter = -10.0
		self.entity_key = entity_key
		self.init_attributes()
		start_x, start_y = level.track.coordinates(self.time_counter)
		self.width, self.height = self.image.get_width(), self.image.get_height()
		self.rect = self.image.get_bounding_rect()
		self.float_x, self.float_y = start_x, start_y
		self.image.set_colorkey(DEFAULT_COLORKEY)
		self.active_effects = []

	def init_attributes(self):
		attribute_map = ENEMY_ATTRIBUTE_MAP[self.entity_key]
		for attribute in ATTRIBUTE_LIST:
			if attribute in attribute_map: value = attribute_map[attribute]
			else: value = ENEMY_ATTRIBUTE_MAP[DEFAULT][attribute]
			init_method = INIT_METHOD_MAP[attribute]
			init_method(self, value)

	def init_image(self, value):
		self.image = load_image(value, "./images")
		if IMAGE_TRANSPARENCY in ENEMY_ATTRIBUTE_MAP[self.entity_key]: alpha = ENEMY_ATTRIBUTE_MAP[self.entity_key][IMAGE_TRANSPARENCY]
		else: alpha = ENEMY_ATTRIBUTE_MAP[DEFAULT][IMAGE_TRANSPARENCY]
		self.image.set_alpha(alpha)

	def init_hitpoints(self, value):
		self.hitpoints = [value, value]

	def init_speed(self, value):
		self.speed = value

	def init_damage(self, value):
		self.damage = value

	def init_resistances(self, value):
		self.resistances = value

	def update(self, track):
		speed = self.calculate_speed()
		for i in xrange(speed):
			x, y = self.float_x, self.float_y
			dest_x, dest_y = track.coordinates(self.time_counter)
			vec_x, vec_y = dest_x - x, dest_y - y
			length = math.pow( math.pow(vec_x, 2) + math.pow(vec_y, 2), 0.5)
			if length == 0: 
				self.time_counter += 0.1
				continue
			add_x, add_y = vec_x/length, vec_y/length
			self.float_x += add_x
			self.float_y += add_y 
			self.rect.center = self.float_x + 8, self.float_y + 8
			self.time_counter += 1/length
		self.effects_update()

	def effects_update(self):
		for e in reversed(self.active_effects):
			e.duration -= 1
			if e.duration <= 0: self.active_effects.remove(e)

	def calculate_speed(self):
		speed = self.speed
		for e in self.active_effects:
			if e.effect_key == "slow":
				speed = max(1, speed - e.slow_value)
		return speed

	def add_effect(self, effect):
		for e in self.active_effects:
			if e == effect: e.reset_duration()
			return
		self.active_effects.append(effect)

	def set_coordinates(self, x, y):
		self.float_x, self.float_y = x, y
		self.rect.topleft = x, y

	def take_damage(self, damage):
		self.hitpoints[0] -= damage
		if self.hitpoints[0] <= 0: self.die()

	def die(self):
		self.level.remove_entity(self)

def load_image(name, path = "./", colorkey = DEFAULT_COLORKEY):
	fullname = os.path.join(path, name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print 'Cannot load image:', name
		raise SystemExit, message
	image = image.convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0, 0))
		image.set_colorkey(colorkey, RLEACCEL)
	return image

# enemy keys

DEFAULT = "default"
BASIC_ENEMY = "basic_enemy"
KNIGHT = "knight"
BARBARIAN = "barbarian"
TROLL = "troll"
HORSE_RIDER = "horse_rider"
DEMON = "demon"
GHOST = "ghost"
WRAITH = "wraith"
LICH = "lich"
WYVERN = "wyvern"

# attributes

IMAGE = "image"
IMAGE_TRANSPARENCY = "image_transparency"
HITPOINTS = "hitpoints"
SPEED = "speed"
DAMAGE = "damage"
RESISTANCES = "resistances"

# elements

IMPACT = "impact"
FIRE = "fire"
HOLY = "holy"

ATTRIBUTE_LIST = [IMAGE, HITPOINTS, SPEED, DAMAGE, RESISTANCES]

INIT_METHOD_MAP = {
	IMAGE:Entity.init_image,
	HITPOINTS:Entity.init_hitpoints,
	SPEED:Entity.init_speed,
	DAMAGE:Entity.init_damage,
	RESISTANCES:Entity.init_resistances
}

ENEMY_ATTRIBUTE_MAP = {
	DEFAULT:{
		IMAGE:"test_enemy_1.bmp", IMAGE_TRANSPARENCY:255, HITPOINTS:2, SPEED:2, DAMAGE:1, RESISTANCES:[HOLY]
	},
	BASIC_ENEMY:{},
	KNIGHT:{
		IMAGE:"knight_1.bmp", HITPOINTS:5, SPEED:1, DAMAGE:2
	},
	BARBARIAN:{
		IMAGE:"barbarian_1.bmp", DAMAGE:3
	},
	TROLL:{
		IMAGE:"troll_1.bmp", HITPOINTS:50, SPEED:1, DAMAGE:15
	},
	HORSE_RIDER:{
		IMAGE:"horse_rider_1.bmp", HITPOINTS:4, SPEED:3, DAMAGE:2
	},
	DEMON:{
		IMAGE:"demon_1.bmp", HITPOINTS:6, SPEED:2, DAMAGE:10, RESISTANCES:[FIRE]
	},
	GHOST:{
		IMAGE:"ghost_1.bmp", IMAGE_TRANSPARENCY:128, HITPOINTS:1, SPEED:3, DAMAGE:2, RESISTANCES:[IMPACT, FIRE]
	},
	WRAITH:{
		IMAGE:"wraith_1.bmp", IMAGE_TRANSPARENCY:128, HITPOINTS:6, SPEED:2, DAMAGE:5, RESISTANCES:[IMPACT, FIRE]
	},
	LICH:{
		IMAGE:"lich_1.bmp", IMAGE_TRANSPARENCY:128, HITPOINTS:30, SPEED:2, DAMAGE:45, RESISTANCES:[IMPACT, FIRE]
	},
	WYVERN:{
		IMAGE:"wyvern_1.bmp", HITPOINTS:100, SPEED:3, DAMAGE:45, RESISTANCES:[HOLY, FIRE]
	}
} 
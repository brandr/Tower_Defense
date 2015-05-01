from entity import load_image, DEFAULT_COLORKEY
from projectile import Projectile
from effect import build_effect, SLOW, POISON
from entity import FIRE, HOLY, FIRE_ELEMENTAL
import pygame
from pygame import Rect, Surface, Color
import math 

MAX_UPGRADE_LEVELS = 3#4
#BALLISTA_BOLT_SPEED_1 = 15.0
RED = Color("#FF0000")


def build_tower(level, tower_key):
	constructor = TOWER_DATA_MAP[tower_key][CONSTRUCTOR]
	return constructor(level)

class Tower(pygame.sprite.Sprite):
	def __init__(self, level, tower_key):
		self.tower_key = tower_key
		tower_map = TOWER_DATA_MAP[tower_key]
		pygame.sprite.Sprite.__init__(self)
		self.rect = Rect(0, 0, 32, 32)
		self.default_image = load_image(tower_map[IMAGE_FILENAME], "./images", DEFAULT_COLORKEY)
		self.image = load_image(tower_map[IMAGE_FILENAME], "./images", DEFAULT_COLORKEY)
		self.mask = pygame.mask.from_surface(self.image)
		self.load_transparent_image()
		self.purchase_cost = tower_map[PURCHASE_COST]
		self.upgrade_levels = [0, 0]
		self.damage = tower_map[DAMAGE]
		self.range = tower_map[RANGE]
		self.attack_speed = tower_map[ATTACK_SPEED]
		self.projectile_speed = 0
		self.pierce = 1
		self.range_effect = None
		if PROJECTILE_IMAGE_FILENAME in tower_map: self.projectile_image_filename = tower_map[PROJECTILE_IMAGE_FILENAME]
		if PROJECTILE_SPEED in tower_map: self.projectile_speed = tower_map[PROJECTILE_SPEED]
		if PIERCE in tower_map: self.pierce = tower_map[PIERCE]
		self.level = level
		self.stun_counter = 0

	def create_copy(self):
		constructor = TOWER_DATA_MAP[self.tower_key][CONSTRUCTOR]
		return constructor(self.level)

	def load_transparent_image(self):
		image = Surface((32, 32))
		image.fill(DEFAULT_COLORKEY)
		image.set_colorkey(DEFAULT_COLORKEY)
		image.blit(self.image, (0, 0))
		image.set_alpha(120)
		self.transparent_image = image

	def get_name(self):
		return TOWER_DATA_MAP[self.tower_key][NAME]

	def get_description(self):
		if DESCRIPTION in TOWER_DATA_MAP[self.tower_key]: return TOWER_DATA_MAP[self.tower_key][DESCRIPTION]
		else: return []
	
	def activate(self, level): # called when the tower is placed on the field
		self.level = level

	def deal_damage(self, enemy):
		enemy.take_damage(self.damage)
		self.level.give_money(self.damage)
		if enemy.stun: self.stun(enemy.stun)
		if enemy.entity_key == FIRE_ELEMENTAL: self.remove_all_upgrades()

	def update(self, level, screen):
		pass

	def enemies_in_range(self, level):
		enemies = []
		for e in level.entities:
			if self.pixel_dist_from(e) < self.range: enemies.append(e)
		return enemies

	def is_in_range(self, other):
		return self.pixel_dist_from(other) < self.range

	def pixel_dist_from(self, other):
		x1, y1 = self.rect.center
		x2, y2 = other.rect.center
		return math.pow(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2), .5)

	def refresh_projectile_image(self):
		self.projectile_image = load_image(self.projectile_image_filename, "./images", DEFAULT_COLORKEY)

	def generate_projectile(self, image, xvel, yvel, frag_filename = None):
		projectile = Projectile(self, self.level, image, self.damage, self.pierce, xvel, yvel, self.rect.left, self.rect.top, frag_filename)
		return projectile

	def apply_effect(self, other):
		if self.range_effect: other.add_effect(self.range_effect)

	def sell_value(self):
		value = TOWER_DATA_MAP[self.tower_key][PURCHASE_COST]
		for i in xrange(self.upgrade_levels[0]): value += TOWER_DATA_MAP[self.tower_key][UPGRADE_MAP][LEFT][i + 1][COST]
		for j in xrange(self.upgrade_levels[1]): value += TOWER_DATA_MAP[self.tower_key][UPGRADE_MAP][RIGHT][j + 1][COST]
		return value/2

	def sell(self):
		if self.stun_counter > 0: return
		self.level.give_money(self.sell_value())
		self.level.remove_tower(self)

	def attempt_left_upgrade(self):
		if self.upgrade_levels[0] + 1 > MAX_UPGRADE_LEVELS: return
		cost = self.get_left_upgrade_cost()
		data_map = self.get_left_upgrade_data_map()
		if self.attempt_upgrade(cost, data_map): self.upgrade_levels[0] += 1

	def attempt_right_upgrade(self):
		if self.upgrade_levels[1] + 1 > MAX_UPGRADE_LEVELS: return
		cost = self.get_right_upgrade_cost()
		data_map = self.get_right_upgrade_data_map()
		if self.attempt_upgrade(cost, data_map): self.upgrade_levels[1] += 1

	def attempt_upgrade(self, cost, data_map):
		if self.level.money < cost or self.stun_counter > 0: return False
		self.level.money -= cost
		if METHOD in data_map: 
			method, arg = data_map[METHOD][0], data_map[METHOD][1]
			method(self, arg)
		if DAMAGE in data_map: self.damage = data_map[DAMAGE]
		if RANGE in data_map: self.range = data_map[RANGE]
		if ATTACK_SPEED in data_map: self.attack_speed = data_map[ATTACK_SPEED]
		if PROJECTILE_SPEED in data_map: self.projectile_speed = data_map[PROJECTILE_SPEED]
		if PIERCE in data_map: self.pierce = data_map[PIERCE]
		if IMAGE_FILENAME in data_map:
			self.image = load_image(data_map[IMAGE_FILENAME], "./images", DEFAULT_COLORKEY)
			self.default_image = load_image(data_map[IMAGE_FILENAME], "./images", DEFAULT_COLORKEY)
		if PROJECTILE_IMAGE_FILENAME in data_map: 
			self.projectile_image_filename = data_map[PROJECTILE_IMAGE_FILENAME]
			self.refresh_projectile_image()
		if RANGE_EFFECT in data_map:
			range_effect_data = data_map[RANGE_EFFECT]
			self.range_effect = build_effect(range_effect_data[0], range_effect_data[1])
		return True 

	def remove_all_upgrades(self):
		tower_map = TOWER_DATA_MAP[self.tower_key]
		self.default_image = load_image(tower_map[IMAGE_FILENAME], "./images", DEFAULT_COLORKEY)
		self.image = load_image(tower_map[IMAGE_FILENAME], "./images", DEFAULT_COLORKEY)
		self.mask = pygame.mask.from_surface(self.image)
		self.load_transparent_image()
		self.upgrade_levels = [0, 0]
		self.damage = tower_map[DAMAGE]
		self.range = tower_map[RANGE]
		self.attack_speed = tower_map[ATTACK_SPEED]
		self.projectile_speed = 0
		self.pierce = 1
		self.range_effect = None
		if PROJECTILE_IMAGE_FILENAME in tower_map: 
			self.projectile_image_filename = tower_map[PROJECTILE_IMAGE_FILENAME]
			self.refresh_projectile_image()
		if PROJECTILE_SPEED in tower_map: self.projectile_speed = tower_map[PROJECTILE_SPEED]
		if PIERCE in tower_map: self.pierce = tower_map[PIERCE]

	def get_left_upgrade_data_map(self):
		return TOWER_DATA_MAP[self.tower_key][UPGRADE_MAP][LEFT][self.upgrade_levels[0] + 1]

	def get_right_upgrade_data_map(self):
		return TOWER_DATA_MAP[self.tower_key][UPGRADE_MAP][RIGHT][self.upgrade_levels[1] + 1]

	def get_left_upgrade_cost(self):
		return self.get_left_upgrade_data_map()[COST]

	def get_right_upgrade_cost(self):
		return self.get_right_upgrade_data_map()[COST]

	def get_left_upgrade_image(self):
		if self.upgrade_levels[0] + 1 > MAX_UPGRADE_LEVELS: return None
		return load_image(self.tower_key + "_upgrade_left_" + str(self.upgrade_levels[0] + 1) + ".bmp", "./images", DEFAULT_COLORKEY)

	def get_right_upgrade_image(self):
		if self.upgrade_levels[1] + 1 > MAX_UPGRADE_LEVELS: return None
		return load_image(self.tower_key + "_upgrade_right_" + str(self.upgrade_levels[1] + 1) + ".bmp", "./images", DEFAULT_COLORKEY)

	def stun(self, stun):
		self.stun_counter = stun
		
class FireTower(Tower):
	def __init__(self, level):
		Tower.__init__(self, level, FIRE_TOWER)
		self.fire_width = 2
		self.fire_color = RED

	def activate(self, level):
		Tower.activate(self, level)
		self.generate_fire_sprite()
		self.hit_enemy_list = []

	def generate_fire_sprite(self):
		if self.upgrade_levels[0] >= 3:
			self.set_fire_ring(None)
			return
		fire_width = self.fire_width
		fire_effect_image = Surface((92, 92))
		fire_effect_image.fill(DEFAULT_COLORKEY)
		fire_effect_image.set_colorkey(DEFAULT_COLORKEY)
		pygame.draw.line(fire_effect_image, self.fire_color, (46, 30), (46, 0), fire_width)
		pygame.draw.line(fire_effect_image, self.fire_color, (30, 46), (0, 46), fire_width)
		pygame.draw.line(fire_effect_image, self.fire_color, (62, 46), (92, 46), fire_width)
		pygame.draw.line(fire_effect_image, self.fire_color, (46, 62), (46, 92), fire_width)
		fire_effect_image.set_alpha(225)
		self.fire_sprite = pygame.sprite.Sprite()		
		self.fire_sprite.image = fire_effect_image
		self.fire_sprite.rect = Rect(self.rect.left - 30, self.rect.top - 30, 92, 92)
		self.fire_sprite.mask = pygame.mask.from_surface(self.fire_sprite.image)

	def set_flame_width(self, width):
		self.fire_width = 6
		self.generate_fire_sprite()

	def set_fire_color(self, color_code):
		self.fire_color = Color(color_code)
		self.generate_fire_sprite()

	def set_fire_ring(self, arg):
		self.fire_sprite.image = Surface((self.range*2, self.range*2))
		self.fire_sprite.image.set_colorkey(DEFAULT_COLORKEY)
		self.fire_sprite.image.fill(DEFAULT_COLORKEY)
		pygame.draw.circle(self.fire_sprite.image, self.fire_color, (self.range, self.range), self.range)
		self.fire_sprite.rect = Rect(self.rect.centerx - self.range, self.rect.centery - self.range, self.range*2, self.range*2)
		self.fire_sprite.mask = pygame.mask.from_surface(self.fire_sprite.image)

	def update(self, level, screen):
		screen.blit(self.fire_sprite.image, (self.fire_sprite.rect.left, self.fire_sprite.rect.top))
		Tower.update(self, level, screen)
		for hit in reversed(self.hit_enemy_list):
			hit[1] -= 1
			if hit[1] <= 0: self.hit_enemy_list.remove(hit)
		for e in level.entities:
			if FIRE in e.resistances: continue
			if self.is_in_range(e): self.apply_effect(e)
			if pygame.sprite.collide_mask(self.fire_sprite, e):
				check = False
				for hit in self.hit_enemy_list:
					if hit[0] == e:
						check = True
						break
				if not check:
					self.hit_enemy_list.append([e, self.attack_speed])
					self.deal_damage(e)


class BallistaTower(Tower):
	def __init__(self, level):
		Tower.__init__(self, level, BALLISTA_TOWER)
		self.default_image = Surface((32, 32))
		self.default_image.fill(DEFAULT_COLORKEY)
		self.default_image.set_colorkey(DEFAULT_COLORKEY)
		self.default_image.blit(self.image, (0, 0))
		self.projectile_image = load_image(self.projectile_image_filename, "./images", DEFAULT_COLORKEY)
		self.attack_counter = 0

	def activate(self, level):
		Tower.activate(self, level)

	def update(self, level, screen):
		Tower.update(self, level, screen)
		if self.attack_counter > 0: self.attack_counter -= 1
		reachable_enemies = self.enemies_in_range(level)
		if reachable_enemies: self.fire_at(level, reachable_enemies[0])

	def fire_at(self, level, target):
		if self.attack_counter > 0: return
		x1, y1 = self.rect.center
		x2, y2 = target.rect.center
		xdist = x2 - x1
		ydist = y2 - y1
		magnitude = math.pow(math.pow(xdist, 2) + math.pow(ydist, 2), .5)
		xvel, yvel = self.projectile_speed*xdist/magnitude, self.projectile_speed*ydist/magnitude
		if ydist == 0: angle = 90
		elif xdist == 0: angle = 0
		else: angle = abs((math.atan(xdist/ydist))*180/(math.pi))%90
		if x2 <= x1 and y2 <= y1: pass
		elif x2 <= x1 and y2 > y1: angle = 180 - angle
		elif x2 > x1 and y2 > y1: angle = 180 + angle
		elif x2 > x1 and y2 <= y1: angle = -1*angle
		self.image = pygame.transform.rotate(self.default_image, angle) 
		bolt = self.generate_projectile(self.rotated_bolt_image(angle), xvel, yvel) 
		level.add_projectile(bolt)
		self.attack_counter = self.attack_speed

	def rotated_bolt_image(self, angle):
		image = Surface((32, 32))
		image.set_colorkey(DEFAULT_COLORKEY)
		image.fill(DEFAULT_COLORKEY)
		image.blit(self.projectile_image, (0, 0))
		image = pygame.transform.rotate(image, angle)
		return image

	def refresh_projectile_image(self):
		self.projectile_image = load_image(self.projectile_image_filename, "./images", DEFAULT_COLORKEY)

class CatapultTower(Tower):
	def __init__(self, level):
		Tower.__init__(self, level, CATAPULT_TOWER)
		self.default_image = Surface((32, 32))
		self.default_image.fill(DEFAULT_COLORKEY)
		self.default_image.set_colorkey(DEFAULT_COLORKEY)
		self.default_image.blit(self.image, (0, 0))
		self.projectile_image = load_image(self.projectile_image_filename, "./images", DEFAULT_COLORKEY)
		self.attack_counter = 0

	def update(self, level, screen):
		Tower.update(self, level, screen)
		if self.attack_counter > 0: self.attack_counter -= 1
		reachable_enemies = self.enemies_in_range(level)
		if reachable_enemies: 
			strongest = reachable_enemies[0]
			for e in reachable_enemies:
				if e.hitpoints[0] > strongest.hitpoints[0]: strongest = e
			self.fire_at(level, strongest)

	def fire_at(self, level, target):
		if self.attack_counter > 0: return
		x1, y1 = self.rect.center
		x2, y2 = target.rect.center
		xdist = x2 - x1
		ydist = y2 - y1
		magnitude = math.pow(math.pow(xdist, 2) + math.pow(ydist, 2), .5)
		xvel, yvel = self.projectile_speed*xdist/magnitude, self.projectile_speed*ydist/magnitude
		if ydist == 0: angle = 90
		elif xdist == 0: angle = 0
		else: angle = abs((math.atan(xdist/ydist))*180/(math.pi))%90
		if x2 <= x1 and y2 <= y1: pass
		elif x2 <= x1 and y2 > y1: angle = 180 - angle
		elif x2 > x1 and y2 > y1: angle = 180 + angle
		elif x2 > x1 and y2 <= y1: angle = -1*angle
		self.image = pygame.transform.rotate(self.default_image, angle) 
		frag_filename = None
		if self.upgrade_levels[1] >= 3: 
			if self.upgrade_levels[0] >= 3: frag_filename = "lightning_frag.bmp"
			else: frag_filename = "catapult_stone_frag.bmp" 
		rock = self.generate_projectile(self.projectile_image, xvel, yvel, frag_filename)
		level.add_projectile(rock)
		self.attack_counter = self.attack_speed

class ChapelTower(Tower):
	def __init__(self, level):
		Tower.__init__(self, level, CHAPEL_TOWER)
		self.hit_enemy_list = []

	def update(self, level, screen):
		Tower.update(self, level, screen)
		for hit in reversed(self.hit_enemy_list):
			hit[1] -= 1
			if hit[1] <= 0: self.hit_enemy_list.remove(hit)
		for e in level.entities:
			if self.is_in_range(e):
				self.apply_effect(e)
				if HOLY in e.resistances: continue
				check = False
				for hit in self.hit_enemy_list:
					if hit[0] == e:
						check = True
						break
				if not check:
					self.hit_enemy_list.append([e, self.attack_speed])
					self.deal_damage(e)	

class CannonTower(Tower):
	"""CannonTower( Level, Surface ) -> CannonTower

	TODO: docstrings
	"""
	def __init__(self, level):
		Tower.__init__(self, level, CANNON_TOWER)
		self.default_image = Surface((32, 32))
		self.default_image.fill(DEFAULT_COLORKEY)
		self.default_image.set_colorkey(DEFAULT_COLORKEY)
		self.default_image.blit(self.image, (0, 0))
		self.projectile_image = load_image(self.projectile_image_filename, "./images", DEFAULT_COLORKEY)
		self.attack_counter = 0
		self.explosion_image = load_image("cannon_ball_explosion.bmp", "./images", DEFAULT_COLORKEY)
			
	def update(self, level, screen):
		Tower.update(self, level, screen)
		if self.attack_counter > 0: self.attack_counter -= 1
		reachable_enemies = self.enemies_in_range(level)
		if reachable_enemies: self.fire_at(level, reachable_enemies[0])

	def fire_at(self, level, target):
		if self.attack_counter > 0: return
		x1, y1 = self.rect.center
		x2, y2 = target.rect.center
		xdist = x2 - x1
		ydist = y2 - y1
		magnitude = math.pow(math.pow(xdist, 2) + math.pow(ydist, 2), .5)
		xvel, yvel = self.projectile_speed*xdist/magnitude, self.projectile_speed*ydist/magnitude
		if ydist == 0: angle = 90
		elif xdist == 0: angle = 0
		else: angle = abs((math.atan(xdist/ydist))*180/(math.pi))%90
		if x2 <= x1 and y2 <= y1: pass
		elif x2 <= x1 and y2 > y1: angle = 180 - angle
		elif x2 > x1 and y2 > y1: angle = 180 + angle
		elif x2 > x1 and y2 <= y1: angle = -1*angle
		self.image = pygame.transform.rotate(self.default_image, angle) 
		frag_filename = None
		if self.upgrade_levels[1] >= 2: 
			frag_filename = "cannon_ball_frag.bmp"
			
		ball = self.generate_projectile(self.projectile_image, xvel, yvel, frag_filename)
		level.add_projectile(ball)
		self.attack_counter = self.attack_speed

	def generate_projectile(self, image, xvel, yvel, frag_filename = None):
		explosion_data = None
		if self.upgrade_levels[1] >= 3: explosion_data = [self.explosion_image, self.damage]
		projectile = Projectile(self, self.level, image, self.damage, self.pierce, xvel, yvel, self.rect.left, self.rect.top, frag_filename, explosion_data)
		return projectile


FIRE_TOWER = "fire_tower"
BALLISTA_TOWER = "ballista_tower"
CATAPULT_TOWER = "catapult_tower"
CHAPEL_TOWER = "chapel_tower"
CANNON_TOWER = "cannon_tower"

NAME = "name"
DESCRIPTION = "description"
CONSTRUCTOR = "constructor"
IMAGE_FILENAME = "image_filename"
METHOD = "method"
PROJECTILE_IMAGE_FILENAME = "projectile_image_filename"
PURCHASE_COST = "purchase_cost"
DAMAGE = "damage"
RANGE = "range"
ATTACK_SPEED = "attack_speed"
PROJECTILE_SPEED = "projectile_speed"
PIERCE = "pierce"
RANGE_EFFECT = "range_effect"

UPGRADE_MAP = "upgrade_map"
LEFT = "left"
RIGHT = "right"
COST = "cost"

TOWER_DATA_MAP = {
	FIRE_TOWER:{
		NAME:"Fire Tower",
		DESCRIPTION:[
			"An AOE tower with expensive but",
			"powerful upgrades."
		],
		CONSTRUCTOR:FireTower,
		IMAGE_FILENAME:"fire_tower_1.bmp",
		PURCHASE_COST:150,
		DAMAGE:1,
		RANGE:0,
		ATTACK_SPEED:18,
		UPGRADE_MAP:{
			LEFT:{
				1:{
					NAME:"Thicker Strips",
					COST:50,
					METHOD:[FireTower.set_flame_width, 6]
				},
				2:{
					NAME:"Smoky Flames",
					COST:125,
					RANGE:60,
					RANGE_EFFECT:[SLOW, 2]
				},
				3:{
					NAME:"Engulfing Flames",
					COST:1000,
					METHOD:[FireTower.set_fire_ring, None]
				}
			},
			RIGHT:{
				1:{
					NAME:"Hotter Flames",
					COST:175,
					DAMAGE:2
				},
				2:{
					NAME:"Red Hot Flames",
					COST:350,
					DAMAGE:4
				},
				3:{
					NAME:"Blue Hot Flames",
					COST:850,
					DAMAGE:8,
					METHOD:[FireTower.set_fire_color, "#49D5EB"]
				}
			}
		}		
	},
	BALLISTA_TOWER:{
		NAME:"Ballista",
		DESCRIPTION:[
			"A basic medium-speed tower",
			"with good upgrades."
		],
		CONSTRUCTOR:BallistaTower,
		IMAGE_FILENAME:"ballista_1.bmp",
		PROJECTILE_IMAGE_FILENAME:"ballista_bolt_1.bmp",
		PURCHASE_COST:100,
		DAMAGE:1,
		RANGE:225,
		ATTACK_SPEED:90,
		PROJECTILE_SPEED:15,
		PIERCE:1,
		UPGRADE_MAP:{
			LEFT:{
				1:{
					NAME:"Stronger Bolts",
					COST:75,
					DAMAGE:2,
					PIERCE:2
				},
				2:{
					NAME:"Flaming Bolts",
					COST:75,
					DAMAGE:3,
					PROJECTILE_IMAGE_FILENAME:"flaming_ballista_bolt_1.bmp"
				},
				3:{
					NAME:"Steel Bolts",
					COST:225,
					PROJECTILE_IMAGE_FILENAME:"steel_ballista_bolt_1.bmp"
				}	
			},
			RIGHT:{
				1:{
					NAME:"Taut String",
					COST:50,
					RANGE:300,
					PROJECTILE_SPEED:18
				},
				2:{
					NAME:"Slick Bolts",
					COST:100,
					PIERCE:4
				},
				3:{
					NAME:"S.A.B.",
					IMAGE_FILENAME:"ballista_1_sab.bmp",
					COST:800,
					ATTACK_SPEED:25
				}
			}
		}	
	},
	CATAPULT_TOWER:{
		NAME:"Catapult",
		DESCRIPTION:[
			"A slow-firing but powerful tower",
			 "meant mainly for boss enemies."
		],
		CONSTRUCTOR:CatapultTower,
		IMAGE_FILENAME:"catapult_1.bmp",
		PROJECTILE_IMAGE_FILENAME:"catapult_stone_1.bmp",
		PURCHASE_COST:125,
		DAMAGE:10,
		RANGE:175,
		ATTACK_SPEED:250,
		PROJECTILE_SPEED:12,
		UPGRADE_MAP:{
			LEFT:{
				1:{
					NAME:"Custom Wood",
					COST:50,
					RANGE:200,
					PROJECTILE_SPEED:13
				},
				2:{
					NAME:"Swift Stones",
					COST:150,
					PROJECTILE_SPEED:15,
					ATTACK_SPEED:150
				},
				3:{
					NAME:"Thunderpult",
					COST:800,
					DAMAGE:35,
					ATTACK_SPEED:70,
					PROJECTILE_IMAGE_FILENAME:"lightning.bmp"		
				}				
			},
			RIGHT:{
				1:{
					NAME:"Faster Reloading",
					COST:25,
					ATTACK_SPEED:220
				},
				2:{
					NAME:"Heavy Stones",
					COST:80,
					DAMAGE:20
				},
				3:{
					NAME:"Frag Rocks",
					COST:400		
				}	
			}
		}
	},
	CHAPEL_TOWER:{
		NAME:"Chapel",
		DESCRIPTION:[
			"A holy place that inflicts the might of", 
			"the lord upon those who despise it."
		],
		CONSTRUCTOR:ChapelTower,
		IMAGE_FILENAME:"chapel_1.bmp",
		PURCHASE_COST:50,
		DAMAGE:1,
		RANGE:100,
		ATTACK_SPEED:45,
		UPGRADE_MAP:{
			LEFT:{
				1:{
					NAME:"Taller Chapel",
					COST:60,
					IMAGE_FILENAME:"chapel_2.bmp",
					RANGE:175
				},
				2:{
					NAME:"Holy Frame",
					COST:100,
					ATTACK_SPEED:30
				},
				3:{
					NAME:"Godspeed",
					COST:400,
					ATTACK_SPEED:10,
					RANGE:200
				}
			},
			RIGHT:{
				1:{
					NAME:"Holy Light",
					COST:100,
					RANGE_EFFECT:[SLOW, 1]
				},
				2:{
					NAME:"Bright Light",
					COST:150,
					DAMAGE:3
				},
				3:{
					NAME:"Lord's Wrath",
					COST:500,
					DAMAGE:10
				}
			}
		}
	},
	CANNON_TOWER:{
		NAME:"Cannon",
		DESCRIPTION:[
			"Extremely expensive but very", 
			"powerful and good for hordes."
		],
		CONSTRUCTOR:CannonTower,
		IMAGE_FILENAME:"cannon_1.bmp",
		PROJECTILE_IMAGE_FILENAME:"cannon_ball_1.bmp",
		PURCHASE_COST:350,
		DAMAGE:15,
		RANGE:125,
		ATTACK_SPEED:100,
		PROJECTILE_SPEED:18,
		UPGRADE_MAP:{
			LEFT:{
				1:{
					NAME:"Rigid Balls",
					COST:250,
					PIERCE:1
				},
				2:{
					NAME:"More Gunpowder",
					COST:325,
					PROJECTILE_SPEED:20,
					RANGE:150,
					ATTACK_SPEED:90
				},
				3:{
					NAME:"Autocannon",
					COST:3250,
					PROJECTILE_SPEED:25,
					RANGE:175,
					ATTACK_SPEED:5,
					IMAGE_FILENAME:"autocannon.bmp"	
				}
			},
			RIGHT:{
				1:{
					NAME:"Bigger Balls",
					COST:100,
					DAMAGE:20,
					PROJECTILE_IMAGE_FILENAME:"cannon_ball_2.bmp"				
				},
				2:{
					NAME:"Frag Balls",
					COST:400
				},
				3:{
					NAME:"Gunpowder Filling",
					COST:1100
				}
			}
		}
	}
}
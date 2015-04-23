from entity import load_image, DEFAULT_COLORKEY, IMPACT
import pygame
from pygame import Rect
import math

class Projectile(pygame.sprite.Sprite):
	def __init__(self, owner, level, image, damage, pierce, xvel, yvel, xpos, ypos, frag_filename = None, explosion_data = None):
		pygame.sprite.Sprite.__init__(self)
		self.level = level
		self.owner = owner
		self.image = image
		self.rect = Rect(xpos, ypos, self.image.get_width(), self.image.get_height())
		self.mask = pygame.mask.from_surface(self.image)
		self.damage = damage
		self.pierce = pierce
		self.xvel, self.yvel = xvel, yvel
		self.frag_filename = frag_filename
		self.hit_targets = []
		self.init_explosion(explosion_data)
		#self.explosion_data = explosion_data # [ Surface image, int damage ]

	def init_explosion(self, explosion_data):
		if not explosion_data:
			self.explosion = None
			return
		self.explosion = Explosion(explosion_data[0], explosion_data[1])

	def collide_with(self, other):
		if other in self.hit_targets: return
		if IMPACT in other.resistances: return
		self.level.give_money(self.damage)
		other.take_damage(self.damage)
		self.pierce -= 1
		if self.pierce <= 0:
			if self.explosion: self.level.add_explosion(self.explosion, self.rect.centerx, self.rect.centery)
			self.level.remove_projectile(self) #Might not be true for all projectiles
			if self.frag_filename: self.generate_fragments()
			return
		self.hit_targets.append(other)
		
	def generate_fragments(self):
		frag_damage = max(1, self.damage/2)
		frag_image = load_image(self.frag_filename, "./images", DEFAULT_COLORKEY)
		velocity = math.pow( math.pow( self.xvel, 2 ) + math.pow( self.yvel, 2 ), .5)
		frag_up = Projectile(self.owner, self.level, frag_image, frag_damage, False, 0, -1*velocity, self.rect.left, self.rect.top )
		frag_down = Projectile(self.owner, self.level, frag_image, frag_damage, False, 0, velocity, self.rect.left, self.rect.top )
		frag_left = Projectile(self.owner, self.level, frag_image, frag_damage, False, -1*velocity, 0, self.rect.left, self.rect.top )
		frag_right = Projectile(self.owner, self.level, frag_image, frag_damage, False, velocity, 0, self.rect.left, self.rect.top )
		self.level.add_projectile(frag_up)
		self.level.add_projectile(frag_down)
		self.level.add_projectile(frag_left)
		self.level.add_projectile(frag_right)

class Explosion(pygame.sprite.Sprite):
	def __init__(self, image, damage):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = Rect(0, 0, 32, 32)
		self.mask = pygame.mask.from_surface(image)
		self.damage = damage
		self.count = 70
		self.hit_targets = []

	def update(self, level):
		self.count -= 1
		if self.count <= 0: level.remove_explosion(self)

	def collide_with(self, other):
		if not other in self.hit_targets:
			self.hit_targets.append(other)
			other.take_damage(self.damage)
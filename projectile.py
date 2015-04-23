from entity import load_image, DEFAULT_COLORKEY, IMPACT
import pygame
from pygame import Rect
import math

class Projectile(pygame.sprite.Sprite):
	def __init__(self, owner, level, image, damage, pierce, xvel, yvel, xpos, ypos, frag_filename = None):
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

	def collide_with(self, other):
		if other in self.hit_targets: return
		if IMPACT in other.resistances: return
		self.level.give_money(self.damage)
		other.take_damage(self.damage)
		self.pierce -= 1
		if self.pierce <= 0:
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
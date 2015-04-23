from entity import DEFAULT_COLORKEY
import pygame
from pygame import Surface, Rect, Color
from camera import WIN_WIDTH, WIN_HEIGHT
import math

MAX_OUTSIDE_DISTANCE = 32

class Track(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.equation = test_equation
		self.color = Color("#C98C57")
		self.generate_track_image()
		self.rect = Rect(0, 0, WIN_WIDTH, WIN_HEIGHT)
		self.mask = pygame.mask.from_surface(self.image)

	def generate_track_image(self):
		self.image = Surface((WIN_WIDTH, WIN_HEIGHT))
		self.image.fill(DEFAULT_COLORKEY)
		self.image.set_colorkey(DEFAULT_COLORKEY)
		track_painter = Surface((32, 32))
		track_painter.fill(self.color)
		x, y = self.coordinates(0)
		for i in xrange(1000):
			dest_x, dest_y = self.coordinates(i)
			while(abs(x - dest_x) > 1 or abs(y - dest_y) > 1):
				vec_x, vec_y = dest_x - x, dest_y - y
				length = math.pow( math.pow(vec_x, 2) + math.pow(vec_y, 2), 0.5)
				add_x, add_y = vec_x/length, vec_y/length
				x += add_x
				y += add_y
				self.image.blit(track_painter, (x, y))
			if x < -1*MAX_OUTSIDE_DISTANCE or x > WIN_WIDTH + MAX_OUTSIDE_DISTANCE or y < -1*MAX_OUTSIDE_DISTANCE or y > WIN_HEIGHT + MAX_OUTSIDE_DISTANCE: break

	def coordinates(self, t):
		return self.equation(t)

def test_equation(t):
	x, y = t, 60.0*math.sin(t/60.0) + WIN_WIDTH/2.0
	#x, y = t, math.pow(t/1.2, 3)/60.0
	#x, y = 2*t, t
	#x, y = 60*math.sin(t/60.0) + WIN_WIDTH/2.0, math.pow(abs(t), 1.2)
	#x, y = 200*math.cos(t)*(1 - math.cos(t)) + 120, 200*math.sin(t)*(1 - math.cos(t)) + WIN_HEIGHT/2.0
	return x, y
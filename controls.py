from pygame import *

class Controls():
	def __init__(self, level):
		self.level = level

	def process_event(self, event):
		if event.type == MOUSEMOTION: self.level.update_mouse_position(event.pos)
		elif event.type == MOUSEBUTTONDOWN: 
			if event.button == 1: self.level.left_click(event.pos)
			elif event.button == 3: self.level.right_click(event.pos)
		elif event.type == KEYDOWN:
			if event.key == K_SPACE: self.level.round_toggle()
			elif event.key == K_LEFT: self.level.tower_toggle(-1)
			elif event.key == K_RIGHT: self.level.tower_toggle(1)

#! /usr/bin/python

import pygame
from pygame import *
from entity import Entity
from level import Level
from controls import Controls

WIN_WIDTH = 800
WIN_HEIGHT = 640
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = 0
CAMERA_SLACK = 30

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

LEOPARD_SEAL_MOVE_TIME = 20

def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
    pygame.display.set_caption("Use arrows to move!")
    timer = pygame.time.Clock()

    up = down = left = right = running = False
    bg = Surface((16,16))
    bg.convert()
    bg.fill(Color("#FFFFFF"))
    entities = pygame.sprite.Group()

    x = y = 0
    start_level = Level(30, 30)
    controls = Controls(start_level)

    while 1:
        timer.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT: raise SystemExit, "QUIT"
            controls.process_event(e)
        start_level.update(screen)
        pygame.display.update()

if __name__ == "__main__":
    main()
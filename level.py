from random import randint, gauss
import pygame
from organism import Organism, DIRECTIONS
from entity import Entity, DEFAULT_COLORKEY, load_image
from camera import Camera, complex_camera
from track import Track, MAX_OUTSIDE_DISTANCE
from tower import Tower, build_tower, FIRE_TOWER, BALLISTA_TOWER, CATAPULT_TOWER, CHAPEL_TOWER, NAME
from roundmanager import RoundManager
from pygame import Surface, Color, Rect, font, sprite
import math

TOWER_SELECT_LIST = [BALLISTA_TOWER, CATAPULT_TOWER, FIRE_TOWER, CHAPEL_TOWER]

BLACK = Color("#000000")
WHITE = Color("#FFFFFF")
RED = Color("#FF0000")
YELLOW = Color("#FFFF00")

WIN_WIDTH = 800
WIN_HEIGHT = 640
DEFAULT_BACKGROUND_COLOR = Color("#00FF00")
UI_WIDTH, UI_HEIGHT = WIN_WIDTH/3, WIN_HEIGHT/5
UI_X, UI_Y = WIN_WIDTH - UI_WIDTH, 0
ROUND_LABEL_X, ROUND_LABEL_Y = WIN_WIDTH - 148, WIN_HEIGHT - 32
ACTIVE_TOWER_UI_X, ACTIVE_TOWER_UI_Y = WIN_WIDTH/3, WIN_HEIGHT - 100
ACTIVE_TOWER_UI_WIDTH, ACTIVE_TOWER_UI_HEIGHT = WIN_WIDTH/3, 100
SELL_TOWER_X, SELL_TOWER_Y = 80, 8

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Level():
    def __init__(self, width, height):
        self.controls = None
        self.round_manager = RoundManager(self)
        self.ui_font = font.Font("./fonts/FreeSansBold.ttf", 12)
        self.round_label_font = font.Font("./fonts/FreeSansBold.ttf", 20)
        self.mouse_position = (0, 0)
        self.selected_place_tower = build_tower(self, BALLISTA_TOWER)
        self.selected_active_tower = None
        self.ui_tower_image = build_tower(self, BALLISTA_TOWER).image
        self.generate_tower_placement_sprite()
        self.tower_select_index = 0
        self.money = 20000
        self.lives = 50
        self.start_tile = 16, 16
        self.width, self.height = width, height
        self.entities = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        total_level_width  = width*16
        total_level_height = height*16
        self.generate_background_image()
        self.track = Track()
        self.camera = Camera(complex_camera, total_level_width, total_level_height)

    def generate_background_image(self):
        self.background_image = Surface((WIN_WIDTH, WIN_HEIGHT))
        self.background_image.fill(DEFAULT_BACKGROUND_COLOR)

    def generate_tower_placement_sprite(self):
        self.tower_placement_sprite = pygame.sprite.Sprite()
        if not self.selected_place_tower: return
        self.tower_placement_sprite.image = self.selected_place_tower.image #self.placing_tower.image
        self.tower_placement_sprite.mask = pygame.mask.from_surface(self.selected_place_tower.image)

    def add_entity(self, entity):
        x, y = self.track.coordinates(0)
        entity.set_coordinates(x, y)
        self.entities.add(entity)

    def lose_game(self):
        raise(SystemExit, "GAME OVER")

    def update(self, screen):
        screen.blit(self.background_image, ( 0, 0 ))
        screen.blit(self.track.image, ( 0, 0))
        self.update_towers(screen)
        if self.round_manager.round_active: 
            self.round_manager.update()
            self.update_entities(screen)
        self.update_projectiles(screen)
        self.update_tower_placement(screen)
        self.update_ui(screen) 
        self.update_round_label(screen)

    def update_towers(self, screen):
        for t in self.towers:
            t.update(self, screen)
            screen.blit(t.image, (t.rect.left, t.rect.top))

    def update_entities(self, screen):
        for e in self.entities:
            e.update(self.track)
            screen.blit(e.image, (e.rect.left, e.rect.top))
            x, y = e.rect.center
            if x < -1*MAX_OUTSIDE_DISTANCE or x > WIN_WIDTH + MAX_OUTSIDE_DISTANCE or y < -1*MAX_OUTSIDE_DISTANCE or y > WIN_HEIGHT + MAX_OUTSIDE_DISTANCE: 
                self.lives -= e.damage
                if self.lives <= 0: self.lose_game()
                self.remove_entity(e)

    def update_projectiles(self, screen):
        for p in self.projectiles:
            if p.rect.right < 0 or p.rect.left > WIN_WIDTH or p.rect.bottom < 0 or p.rect.top > WIN_HEIGHT:
                self.remove_projectile(p)
                return
            screen.blit(p.image, (p.rect.left, p.rect.top))
            p.rect.left += p.xvel
            p.rect.top += p.yvel
            for e in self.entities:
                if pygame.sprite.collide_mask(p, e):
                    p.collide_with(e)

    def update_tower_placement(self, screen):
        if not self.selected_place_tower: return
        width, height = self.selected_place_tower.rect.width/2, self.selected_place_tower.rect.height/2
        screen.blit(self.selected_place_tower.transparent_image, (self.mouse_position[0] - width, self.mouse_position[1] - height))
        radius = self.selected_place_tower.range
        if radius <= 0: return
        self.draw_range_circle(screen, radius)

    def draw_range_circle(self, screen, radius, pos = None):
        if pos == None: pos = self.mouse_position
        if radius <= 0: return
        range_circle_image = Surface((radius*2, radius*2))
        range_circle_image.fill(DEFAULT_COLORKEY)
        range_circle_image.set_colorkey(DEFAULT_COLORKEY)
        pygame.draw.circle(range_circle_image, RED, (radius, radius), radius - 1, 2)
        screen.blit(range_circle_image, (pos[0] - radius, pos[1] - radius))

    def update_ui(self, screen):
        ui_pane = Surface((UI_WIDTH, UI_HEIGHT))
        self.update_display_money(ui_pane)
        self.update_display_lives(ui_pane)
        self.update_tower_select(ui_pane)
        if self.selected_active_tower: 
            self.draw_range_circle(screen, self.selected_active_tower.range, self.selected_active_tower.rect.center)
            self.update_active_tower_ui(screen)
        screen.blit(ui_pane, (UI_X, UI_Y))

    def update_display_money(self, pane):
        text = "Money: " + str(self.money)
        text_image = self.ui_font.render(text, True, WHITE)
        pane.blit(text_image, (32, 8))

    def update_display_lives(self, pane):
        text = "Lives: " + str(self.lives)
        text_image = self.ui_font.render(text, True, WHITE)
        pane.blit(text_image, (32, 32))

    def update_tower_select(self, pane):
        tower_bg = Surface((32, 32))
        tower_bg.fill(WHITE)
        pane.blit(tower_bg, (32, 54))
        pane.blit(self.ui_tower_image, (32, 54))

    def update_round_label(self, screen):
        round_label = self.round_label_font.render("Round: " + str(self.round_manager.round_number), False, BLACK)
        screen.blit(round_label, (ROUND_LABEL_X, ROUND_LABEL_Y))

    def update_active_tower_ui(self, screen):
        active_tower_pane = Surface((ACTIVE_TOWER_UI_WIDTH, ACTIVE_TOWER_UI_HEIGHT))
        tower_bg = Surface((32, 32))
        tower_bg.fill(WHITE)
        active_tower_pane.blit(tower_bg, (8, 60))
        active_tower_pane.blit(self.selected_active_tower.image, (8, 60))
        active_tower_pane.blit( self.ui_font.render(self.selected_active_tower.get_name(), False, WHITE), ( 8, 8 ))
        left_upgrade_image = self.selected_active_tower.get_left_upgrade_image()
        right_upgrade_image = self.selected_active_tower.get_right_upgrade_image()
        if left_upgrade_image: 
            upgrade_name = self.selected_active_tower.get_left_upgrade_data_map()[NAME]
            text = self.ui_font.render(upgrade_name, False, WHITE)
            active_tower_pane.blit(text, (64, ACTIVE_TOWER_UI_HEIGHT - 58))
            active_tower_pane.blit(left_upgrade_image, ( 64, ACTIVE_TOWER_UI_HEIGHT - 40 ) )
        if right_upgrade_image: 
            upgrade_name = self.selected_active_tower.get_right_upgrade_data_map()[NAME]
            text = self.ui_font.render(upgrade_name, False, WHITE)
            active_tower_pane.blit(text, (168, ACTIVE_TOWER_UI_HEIGHT - 58))
            active_tower_pane.blit(right_upgrade_image, ( 168, ACTIVE_TOWER_UI_HEIGHT - 40 ) )       
        sell_tower_button = self.draw_sell_tower_button()
        active_tower_pane.blit(sell_tower_button, (SELL_TOWER_X, SELL_TOWER_Y))
        screen.blit(active_tower_pane, (ACTIVE_TOWER_UI_X, ACTIVE_TOWER_UI_Y))

    def draw_sell_tower_button(self):
        sell_tower_bg = Surface(( 120, 16))
        sell_tower_bg.fill(YELLOW)
        sell_text = "Sell Tower for $" + str(self.selected_active_tower.sell_value())
        sell_tower_bg.blit(self.ui_font.render(sell_text, False, BLACK, YELLOW), (0, 0))
        return sell_tower_bg

    def tower_toggle(self, directon):
        self.tower_select_index = (self.tower_select_index + directon) % len(TOWER_SELECT_LIST)
        current_tower = build_tower(self, TOWER_SELECT_LIST[self.tower_select_index])
        self.ui_tower_image = current_tower.image
        if self.selected_place_tower: self.selected_place_tower = build_tower(self, TOWER_SELECT_LIST[self.tower_select_index])

    def round_toggle(self):
        self.round_manager.toggle()

    def left_click(self, pos):
        if pos[0] > UI_X and pos[1] < UI_HEIGHT: 
            self.ui_left_click(pos)
            return
        if not self.selected_place_tower:
            if self.selected_active_tower and pos[0] > ACTIVE_TOWER_UI_X and pos[0] < ACTIVE_TOWER_UI_X + ACTIVE_TOWER_UI_WIDTH and pos[1] > ACTIVE_TOWER_UI_Y:
                self.active_tower_ui_left_click(pos)
                return
            self.selected_active_tower = None
            check_sprite = pygame.sprite.Sprite()
            check_sprite.rect = Rect(pos[0] - 8, pos[1] - 8, 16, 16)
            for t in self.towers:
                t.mask = pygame.mask.from_surface(t.image)
                if pygame.sprite.collide_rect(t, check_sprite):
                    self.selected_active_tower = t
                    return
        elif self.can_place_tower(pos): self.place_tower(pos)

    def ui_left_click(self, pos):
        print "UI"

    def active_tower_ui_left_click(self, pos):
        if pos[1] > ACTIVE_TOWER_UI_Y + ACTIVE_TOWER_UI_HEIGHT - 40 and pos[1] < ACTIVE_TOWER_UI_Y + ACTIVE_TOWER_UI_HEIGHT - 8:
            if pos[0] > ACTIVE_TOWER_UI_X + 64 and pos[0] < ACTIVE_TOWER_UI_X + 96: self.selected_active_tower.attempt_left_upgrade()
            elif pos[0] > ACTIVE_TOWER_UI_X + 168 and pos[0] < ACTIVE_TOWER_UI_X + 200: self.selected_active_tower.attempt_right_upgrade()
        elif pos[0] > ACTIVE_TOWER_UI_X + SELL_TOWER_X and pos[0] < ACTIVE_TOWER_UI_X + SELL_TOWER_X + 120: 
            if pos[1] > ACTIVE_TOWER_UI_Y + SELL_TOWER_Y and pos[1] < ACTIVE_TOWER_UI_Y + SELL_TOWER_Y + 16: self.selected_active_tower.sell() 

    def right_click(self, pos):
        self.selected_active_tower = None
        if self.selected_place_tower: self.selected_place_tower = None
        else: self.selected_place_tower = build_tower(self, TOWER_SELECT_LIST[self.tower_select_index])

    def update_mouse_position(self, pos):
        self.mouse_position = pos

    def place_tower(self, pos):
        self.money -= self.selected_place_tower.purchase_cost
        built_tower = self.selected_place_tower.create_copy()
        width, height = built_tower.rect.width, built_tower.rect.height
        built_tower.rect.topleft = pos[0] - width/2, pos[1] - height/2
        self.towers.add(built_tower)
        built_tower.activate(self)

    def can_place_tower(self, pos):
        if not self.selected_place_tower: return False
        width, height = self.selected_place_tower.rect.width, self.selected_place_tower.rect.height
        check_rect = Rect(pos[0] - width/2, pos[1] - height/2, width, height )
        if check_rect.right > UI_X and check_rect.top < UI_HEIGHT: return False
        self.tower_placement_sprite.rect = check_rect
        if pygame.sprite.collide_mask(self.tower_placement_sprite, self.track): return False
        if self.money < self.selected_place_tower.purchase_cost: return False
        for t in self.towers:
            if pygame.sprite.collide_mask(t, self.tower_placement_sprite): return False 
        return True

    def send_enemy(self, enemy_key):
        enemy = Entity(self, enemy_key)
        self.add_enemy(enemy)

    def add_enemy(self, enemy):
        self.entities.add(enemy)

    def remove_tower(self, tower):
        if tower == self.selected_active_tower: self.selected_active_tower = None
        self.towers.remove(tower)

    def remove_entity(self, entity):
        self.entities.remove(entity)

    def remove_projectile(self, projectile):
        self.projectiles.remove(projectile)

    def give_money(self, money):
        self.money += money

    def add_projectile(self, projectile):
        self.projectiles.add(projectile)
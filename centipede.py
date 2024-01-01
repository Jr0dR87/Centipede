import pgzero, pgzrun, pygame, sys
from random import choice, randint, random
from enum import Enum

if sys.version_info < (3,5):
    print("This game requires at least version 3.5 of Python.")
    sys.exit()

pgzero_version = [int(s) if s.isnumeric() else s for s in pgzero.__version__.split('.')]

if pgzero_version < [1,2]:
    print("This game requires at least version 1.2 of Pygame Zero.")
    sys.exit()

WIDTH = 480
HEIGHT = 800
TITLE = "Centipede"

DEBUG_TEST_RANDOM_POSITIONS = False
CENTRE_ANCHOR = ("center", "center")

num_grid_rows = 25
num_grid_cols = 14

def pos2cell(x,y):
    return ((int(x)-16)//32, int(y)//32)

def cell2pos(cell_x, cell_y, x_offset=0, y_offset=0):
    return ((cell_x * 32) + 32 + x_offset, (cell_y * 32) + 16 + y_offset)

class Explosion(Actor):
    def __init__(self, pos, type):
        super().__init__("blank",pos)
        self.type = type
        self.timer = 0

    def update(self):
        self.timer += 1
        self.image = "exp" + str(self.type) + str(self.timer // 4)

class Player(Actor):
    INVULNERABILITY_TIME = 100
    RESPAWN_TIME = 100
    RELOAD_TIME = 10

    def __init__(self, pos):
        super().__init__("blank",pos)

        self.direction = 0
        self.frame = 0
        self.lives = 3
        self.alive = True
        self.timer = 0
        self.fire_timer = 0
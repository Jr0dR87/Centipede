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
    
    def move(self, dx, dy, speed):
        for i in range(speed):
            if game.allow_movement(self.x + dx, self.y + dy):
                self.x += dx
                self.y += dy
    
    def update(self):
        self.timer += 1

        if self.alive:
            dx = 0
            if keyboard.left:
                dx = -1
            elif keyboard.right:
                dx = 1
            
            dy = 0
            if keyboard.up:
                dy = -1
            elif keboard.down:
                dy = 1

            self.move(dx, 0, 3 - abs(dy))
            self.move(0, dy, 3 - abs(dx))
            directions = [7,0,1,6,-1,2,5,4,3]
            dir = directions[dx+3*dy+4]

            if self.timer % 2 == 0 and dir >= 0:
                difference = (dir - self.direction)
                rotation_table = [0, 1, 1, -1]
                rotation = rotation_table[difference % 4]
                self.direction = (self.direction + rotation) % 4

            self.fire_timer -= 1

            if self.fire_timer < 0 and (self.frame > 0 or keyboard.space):
                if self.frame == 0:
                    game.play_sound("laster")
                    game.bullets.append(Bullet((self.x, self.y - 8)))
                self.frame = (self.frame + 1) % 3
                self.fire_timer = Player.RELOAD_TIME

            all_enemies = game.segments + [game.flying_enemy]

            for enemy in all_enemies:
                if enemy and enemy.collidepoint(self.pos):
                    if self.timer > Player.INVULNERABILITY_TIM:
                        game.play_sound("player_explode")
                        game.explosions.append(Explosion(self.pos, 1))
                        self.alive = False
                        self.timer = 0
                        self.lives -= 1

        else:
            if self.timer > Player.RESPAWN_TIME:
                self.alive = True
                self.timer = 0
                self.pos = (240, 768)
                game.clear_rocks_for_respawn(*self.pos)
        
        invulnerable = self.timer > Player.INVULNERABILITY_TIME
        if self.alive and (invulnerable or self.timer % 2 == 0):
            self.image = "player" + str(self.direction) + str(self.frame)
        else:
            self.image = "blank"

class FlyingEnemy(Actor):
    def __init__(self, player_x):
        side = 1 if player_x < 160 else 0 if player_x > 320 else randint(0, 1)
        super().__init__("blank", (550*side-35, 688))
        self.moving_x = 1
        self.dx = 1 - 2 * side
        self.dy = choice([-1, 1])
        self.type = randint(0, 2)
        self.health = 1
        self.timer = 0
    
    def update(self):
        self.timer += 1
        self.x += self.dx * self.moving_x * (3 - abs(self.dy))
        self.y += self.dy * (3 - abs(self.dx * self.moving_x))

        if self.y < 592 or self.y > 784:
            self.moving_x = randint(0, 1)
            self.dy = -self.dy

        anim_frame = str([0, 2, 1, 2][(self.timer // 4) % 4])
        self.image = "meanie" + str(self.type) + anim_frame

class Rock(Actor):
    def __init__(self, x, y, totem=False):
        anchor = (24, 60) if totem else CENTRE_ANCHOR
        super().__init__("blank", cell2pos(x,y), anchor=anchor)
        self.type = randint(0, 3)
        
        if totem:
            game.play_sound("totem_create")
            self.health = 5
            self.show_health = 5
        else:
            self.health = randint(3,4)
            self.show_health = 1

        self.timer = 1

        def damage(self, amount, damage_by_bullet=False):
            if damage_by_bullet and self.health == 5:
                game.play_sound('totem_destroy')
                game.score += 100
            else:
                if amount > self.health - 1:
                    game.play_sound('rock_destroy')
                else:
                    game.play_sound("hit", 4)

            game.explosions.append(Explosion(self.pos, 2 * self.health == 5))
            self.health -= amount
            self.show_health = self.health
            self.anchor, self.pos = CENTRE_ANCHOR, self.pos


            return self.health < 1 
        
        def update(self):
            self.timer += 1

            if self.timer % 2 == 1 and self.show_health < self.health:
                self.show_health += 1 

            if self.health == 5 and self.timer > 200:
                self.damage(1)

            color = str(max(game.wave, 0) % 3)
            health = str(max(self.show_health - 1, 0))
            self.image = "rock" + color + str(self.type) + health
                
import pygame as pg
import json
import os
from math import ceil
from copy import copy


DEBUG = 0

horizontal_borders = pg.sprite.Group()
vertical_borders = pg.sprite.Group()
all_sprites = pg.sprite.Group()
player_group = pg.sprite.Group()
border_group = pg.sprite.Group()
enemy_group = pg.sprite.Group()
platforms_group = pg.sprite.Group()
hearts_group = pg.sprite.Group()


without_drawing = pg.sprite.Group()
uppart_platforms_group = pg.sprite.Group()

downpart_platforms_group = pg.sprite.Group()
leftpart_platforms_group = pg.sprite.Group()

rightpart_platforms_group = pg.sprite.Group()

player_down = pg.sprite.Group()

dead_group = pg.sprite.Group()

draw_on_screen = pg.sprite.Group()

coins_group = pg.sprite.Group()

pg.init()

cfg = open("cfg.json", "r")
data = json.load(cfg)
cfg.close()

SIZE = WIDTH, HEIGHT = 960, 540
FPS = int(data['fps'])

screen = pg.display.set_mode(SIZE)
screen.fill((0, 0, 0))
clock = pg.time.Clock()

GAME_OVER = False


def load_image(name, color_key=None, x=0, y=0):
    fullname = os.path.join('data', name)
    image = pg.image.load(fullname).convert()
    if color_key is not None:
        if color_key == -1:
            if x == 1 and y == 1:
                color_key = image.get_at((image.get_width() - 1, image.get_height() - 1))
            elif x == 1:
                color_key = image.get_at((0, image.get_height() - 1))
            else:
                color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def trans(img, width, height, by_x, by_y):
    return pg.transform.flip(pg.transform.scale(img, (width if width != -1 else img.get_width(), height if height != -1 else img.get_height())), by_x, by_y)


def any_colide_mask(first, group):
    for el in group:
        if pg.sprite.collide_mask(first, el):
            return True
    return False


tile_width = tile_height = 60


class Border(pg.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(border_group, all_sprites)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pg.Surface([5, y2 - y1])
            self.rect = pg.Rect(x1, y1, 5, y2 - y1)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pg.Surface([x2 - x1, 5])
            self.rect = pg.Rect(x1, y1, x2 - x1, 5)
        self.mask = pg.mask.from_surface(self.image)


width_platform = ceil(WIDTH // 16)
height_platform = ceil(HEIGHT // 9)

platform_images = {
    'l': trans(load_image('platform1.png', -1, 1), width_platform, height_platform, 0, 0),
    'm': trans(load_image('platform2.png'), width_platform, height_platform, 0, 0),
    "r": trans(load_image('platform3.png', -1, 1, 1), width_platform, height_platform, 0, 0)
}


class Score():
    def __init__(self):
        self.text = "0000000000"
        self.print()

    def print(self):    
        font = pg.font.Font(None, 30)
        font.set_bold(True)
        text_coord = 5
        
        string_rendered = font.render(self.text, 1, (34, 139, 34))
        text_rect = string_rendered.get_rect()
        text_coord += 10
        text_rect.top = text_coord
        text_rect.x = WIDTH - text_rect.width - 15
        screen.blit(string_rendered, text_rect)
    
    def add_score(self, add):
        self.text = str(int(self.text) + add).rjust(10, '0')
        self.print()
    
    def add_coin(self, x, y):
        Coin(x, y, self)


class Coin(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y, score):
        super().__init__(all_sprites, coins_group)
        self.score = score
        self.images = {
            0: trans(load_image('coin/coin_01.png', -1), -1, -1, 0, 0),
            1: trans(load_image('coin/coin_02.png', -1), -1, -1, 0, 0),
            2: trans(load_image('coin/coin_03.png', -1), -1, -1, 0, 0),
            3: trans(load_image('coin/coin_04.png', -1), -1, -1, 0, 0),
            4: trans(load_image('coin/coin_05.png', -1), -1, -1, 0, 0),
            5: trans(load_image('coin/coin_06.png', -1), -1, -1, 0, 0),
            6: trans(load_image('coin/coin_07.png', -1), -1, -1, 0, 0),
            7: trans(load_image('coin/coin_08.png', -1), -1, -1, 0, 0)
        }

        self.pos_x = pos_x
        self.pos_y = pos_y

        self.image = self.images[0]
        self.rect = self.image.get_rect().move(width_platform * pos_x + width_platform // 2 - self.image.get_width() // 2, height_platform * pos_y)
        self.mask = pg.mask.from_surface(self.image)

        self.cur_frame = 0
        self.period = 10

    def update(self):
        self.mask = pg.mask.from_surface(self.image)
        self.cur_frame = (self.cur_frame + 1) % (len(self.images) * self.period)
        self.image = self.images[self.cur_frame // self.period]
        if pg.sprite.spritecollide(self, player_group, False, pg.sprite.collide_mask):
            self.kill()
            self.score.add_score(100)


class Object(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y, tile_type):
        super().__init__(all_sprites)
        self.images = {
            'g': trans(load_image('grass1.png', -1), width_platform, height_platform // 2, 0, 0),
            'G': trans(load_image('grass2.png', -1), width_platform, height_platform // 2, 0, 0),
            'B': trans(load_image('bush.png', -1), width_platform, height_platform, 0, 0),
            'x': trans(load_image('big-crate.png'), width_platform, height_platform, 0, 0),
            'o': trans(load_image('rock.png', -1), width_platform, height_platform // 2, 0, 0)
        }
        
        self.image = self.images[tile_type]
        self.rect = self.image.get_rect().move(width_platform * pos_x, height_platform * (pos_y + 1) - self.image.get_height())


class Platform(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__()
        if tile_type in ["R", "L"]:
            self.add(without_drawing)
            self.image = trans(load_image("blank.png", -1), width_platform, height_platform, 0, 0)
            self.image.fill((255, 0, 255))
        else:
            self.add(platforms_group, all_sprites)
            self.image = platform_images[tile_type]
        self.rect = self.image.get_rect().move(width_platform * pos_x, height_platform * pos_y)
        self.mask = pg.mask.from_surface(self.image)
        self.up_sprite = pg.sprite.Sprite(uppart_platforms_group, without_drawing)
        self.up_sprite.image = trans(load_image("blank.png", -1), width_platform - 4, 5, 0, 0)
        self.up_sprite.image.fill((0, 255, 0))
        self.up_sprite.rect = self.up_sprite.image.get_rect().move(width_platform * pos_x + 2, height_platform * pos_y)

        self.down_sprite = pg.sprite.Sprite(downpart_platforms_group, without_drawing)
        self.down_sprite.image = trans(load_image("blank.png", -1), width_platform - 4, 5, 0, 0)
        self.down_sprite.image.fill((0, 0, 255))
        self.down_sprite.rect = self.down_sprite.image.get_rect().move(width_platform * pos_x + 2, height_platform * pos_y + self.image.get_height())

        if tile_type in ['l', 'L']:
            self.left_sprite = pg.sprite.Sprite(leftpart_platforms_group, without_drawing)
            self.left_sprite.image = trans(load_image("blank.png", -1), 5, height_platform, 0, 0)
            self.left_sprite.image.fill((255, 0, 255))
            self.left_sprite.rect = self.left_sprite.image.get_rect().move(width_platform * pos_x, height_platform * pos_y + 3)

        if tile_type in ['r', 'R']:
            self.right_sprite = pg.sprite.Sprite(rightpart_platforms_group, without_drawing)
            self.right_sprite.image = trans(load_image("blank.png", -1), 5, height_platform, 0, 0)
            self.right_sprite.image.fill((255, 0, 0))
            self.right_sprite.rect = self.right_sprite.image.get_rect().move(width_platform * pos_x + self.image.get_width(), height_platform * pos_y + 3)


class Skelet(pg.sprite.Sprite):
    def __init__(self, x, y, score):
        super().__init__(all_sprites, enemy_group)
        self.score = score
        img = load_image("Skeleton Walk.png", -1)
        h = 111
        img = trans(img, 858, h, 0, 0)
        self.frames_right = self.cut_sheet(img, 13, 1)
        self.frames_left = self.cut_sheet(img, 13, 1, 1)

        img_attack = load_image("Skeleton Attack.png", -1)

        self.attack_right = self.cut_sheet(trans(img_attack, 66 * 35, h, 0, 0), 18, 1)
        self.attack_left = self.cut_sheet(trans(img_attack, 66 * 35, h, 0, 0), 18, 1, 1)

        img_death = load_image("Skeleton Dead.png", -1)

        self.death_right = self.cut_sheet(trans(img_death, 66 * 20, h, 0, 0), 15, 1)
        self.death_left = self.cut_sheet(trans(img_death, 66 * 20, h, 0, 0), 15, 1, 1)

        self.cur_frame = 0
        self.image = self.frames_left[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)
        self.mask = pg.mask.from_surface(self.image)
        self.iteration = 0
        self.speed = 150 / FPS

        self.down_sprite = pg.sprite.Sprite(without_drawing)
        self.down_sprite.image = trans(load_image("blank.png", -1), width_platform - 10, 5, 0, 0)
        self.down_sprite.image.fill((0, 255, 255))
        self.down_sprite.rect = self.down_sprite.image.get_rect().move(tile_width * x - 5, tile_height * y + self.image.get_height() - 4)

        self.left_down_sprite = pg.sprite.Sprite(without_drawing)
        self.left_down_sprite.image = trans(load_image("blank.png", -1), 5, 5, 0, 0)
        self.left_down_sprite.image.fill((0, 0, 255))
        self.left_down_sprite.rect = self.left_down_sprite.image.get_rect().move(tile_width * x - 3, tile_height * y + self.image.get_height())

        self.right_down_sprite = pg.sprite.Sprite(without_drawing)
        self.right_down_sprite.image = trans(load_image("blank.png", -1), 5, 5, 0, 0)
        self.right_down_sprite.image.fill((0, 0, 255))
        self.right_down_sprite.rect = self.right_down_sprite.image.get_rect().move(tile_width * x + self.image.get_width() // 2 + 20, tile_height * y + self.image.get_height())

        self.attack_counter = 0

        self.right = False

        self.attack = False

        self.moved_for_left_attack = False

        self.left_attack_sprite = pg.sprite.Sprite(without_drawing)
        self.left_attack_sprite.image = trans(load_image("blank.png", -1), self.image.get_width() * 1 // 3, self.image.get_height(), 0, 0)
        self.left_attack_sprite.image.fill((0, 0, 255))
        self.left_attack_sprite.image.set_alpha(50)
        self.left_attack_sprite.rect = self.left_attack_sprite.image.get_rect().move(tile_width * x - self.image.get_width() * 1 // 3, tile_height * y)

        self.right_attack_sprite = pg.sprite.Sprite(without_drawing)
        self.right_attack_sprite.image = trans(load_image("blank.png", -1), self.image.get_width() * 1 // 3, self.image.get_height(), 0, 0)
        self.right_attack_sprite.image.fill((255, 255, 0))
        self.right_attack_sprite.image.set_alpha(50)
        self.right_attack_sprite.rect = self.left_attack_sprite.image.get_rect().move(tile_width * x + self.image.get_width(), tile_height * y)
        
        self.dead = False
        self.dead_counter = 0
    
    def is_attacking(self):
        return self.attack

    def take_damage(self):
        self.dead = True
        # print("DEAD SKELET")

    def cut_sheet(self, sheet, columns, rows, reverse=0):
        frames = []
        self.rect = pg.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frame = sheet.subsurface(pg.Rect(frame_location, self.rect.size))
                frame = trans(frame, frame.get_width(), frame.get_height(), reverse, 0)
                frames.append(frame)
        return frames

    def update(self, *args):
        if self.dead and self.iteration % 10 == 0:
            if self.right:
                self.image = self.death_right[self.dead_counter]
            else:
                self.image = self.death_left[self.dead_counter]
            
            self.dead_counter = self.dead_counter + 1

            if self.dead_counter == len(self.death_right):
                self.kill()
                self.score.add_score(200)
                self.add(dead_group)
            return

        left_part_collide = pg.sprite.spritecollide(self.left_down_sprite, uppart_platforms_group, False)
        right_part_collide = pg.sprite.spritecollide(self.right_down_sprite, uppart_platforms_group, False)
        if not left_part_collide:
            self.right = True
        elif not right_part_collide:
            self.right = False
        if not pg.sprite.spritecollide(self.down_sprite, platforms_group, False):
            self.move_all(0, 4)
        else:
            if not self.attack:
                self.move_all(self.speed if self.right else -self.speed, 0)
                self.attack_counter = 0
        if (pg.sprite.spritecollide(self.left_attack_sprite, player_group, False, pg.sprite.collide_mask) and not self.right) or \
                (pg.sprite.spritecollide(self.right_attack_sprite, player_group, False, pg.sprite.collide_mask) and self.right):
            if self.iteration % 3 == 0:
                self.attack = True
                if not self.right:
                    if not self.moved_for_left_attack:
                        self.rect = self.rect.move(-55, 0)
                        self.moved_for_left_attack = True
                    self.image = self.attack_left[self.attack_counter]
                else:
                    self.image = self.attack_right[self.attack_counter]
                self.attack_counter = (self.attack_counter + 1) % 18
        else:
            if self.moved_for_left_attack:
                self.rect = self.rect.move(55, 0)
                self.moved_for_left_attack = False
            if self.right:
                self.image = self.frames_right[self.cur_frame]
            else:
                self.image = self.frames_left[self.cur_frame]
            self.attack = False
            self.attack_counter = 0
        if self.iteration % 7 == 0 and not self.attack:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames_right)
            if self.right:
                self.image = self.frames_right[self.cur_frame]
            else:
                self.image = self.frames_left[self.cur_frame]
        self.iteration = (self.iteration + 1) % 40
        self.mask = pg.mask.from_surface(self.image)

    def move_all(self, x, y):
        self.rect = self.rect.move(x, y)
        self.left_down_sprite.rect = self.left_down_sprite.rect.move(x, y)
        self.right_down_sprite.rect = self.right_down_sprite.rect.move(x, y)
        self.down_sprite.rect = self.down_sprite.rect.move(x, y)
        self.left_attack_sprite.rect = self.left_attack_sprite.rect.move(x, y)
        self.right_attack_sprite.rect = self.right_attack_sprite.rect.move(x, y)


class Heart(pg.sprite.Sprite):
    def __init__(self):
        super().__init__(hearts_group)
        self.hearts = [trans(load_image(f'fulllife/h{i}.png', -1), 2 * 64, 2 * 16, 0, 0) for i in range(1, 14)]
        self.image = self.hearts[0]
        self.rect = self.image.get_rect().move(15, 5)

        self.col = 4

        self.iteration = 0

        self.counter = 0

        self.mod = 13

        self.damage_just_taken = False

        self.col_blinks = 0

        self.die = False
        self.after_death_iterations_counter = 0

    def is_dead(self):
        return self.die

    def take_damage(self):
        self.col = max(0, self.col - 1)
        self.damage_just_taken = True
        self.set_images()

    def set_images(self):
        if self.col == 3:
            self.mod = 13
            self.hearts = [trans(load_image(f'almosthalflife/h{i}.png', -1), 2 * 64, 2 * 16, 0, 0) for i in range(1, 14)]
        if self.col == 2:
            self.mod = 13
            self.hearts = [trans(load_image(f'halflife/h{i}.png', -1), 2 * 64, 2 * 16, 0, 0) for i in range(1, 14)]
        if self.col == 1:
            self.mod = 13
            self.hearts = [trans(load_image(f'onelife/h{i}.png', -1), 2 * 64, 2 * 16, 0, 0) for i in range(1, 14)]
        if self.col == 0:
            self.hearts = [trans(load_image(f'death/death{i}.png', -1), 2 * 64, 2 * 16, 0, 0) for i in range(1, 3)]
            self.mod = 2
            self.die = True
            print("DEATH!")

    def update(self):
        if self.die:
            self.after_death_iterations_counter += 1
            if self.after_death_iterations_counter == 80:
                global GAME_OVER
                GAME_OVER = True
        self.iteration = (self.iteration + 1) % 40
        # print(self.col_blinks)
        if self.damage_just_taken and self.iteration % 5 == 0:
            if self.col_blinks != 8:
                self.counter = self.counter % self.mod
                img = copy(self.hearts[self.counter])
                if self.col_blinks % 2 == 0:
                    img.set_alpha(0)
                self.image = img
                self.col_blinks += 1
            else:
                self.damage_just_taken = False
                self.col_blinks = 0
        elif self.iteration % 10 == 0:
            self.counter = (self.counter + 1) % self.mod
            self.image = self.hearts[self.counter]


class Player(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.hearts = Heart()
        self.idle_right = {
            0: trans(load_image('adventurer-idle-00.png', -1), 150, 111, 0, 0),
            1: trans(load_image('adventurer-idle-01.png', -1), 150, 111, 0, 0),
            2: trans(load_image('adventurer-idle-02.png', -1), 150, 111, 0, 0)
        }

        self.image = self.idle_right[0]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

        self.idle_counter = 0

        self.idle_left = {
            0: trans(load_image('adventurer-idle-00.png', -1), 150, 111, 1, 0),
            1: trans(load_image('adventurer-idle-01.png', -1), 150, 111, 1, 0),
            2: trans(load_image('adventurer-idle-02.png', -1), 150, 111, 1, 0)
        }

        self.run_right = {
            0: trans(load_image('adventurer-run-00.png', -1), 150, 111, 0, 0),
            1: trans(load_image('adventurer-run-01.png', -1), 150, 111, 0, 0),
            2: trans(load_image('adventurer-run-02.png', -1), 150, 111, 0, 0),
            3: trans(load_image('adventurer-run-03.png', -1), 150, 111, 0, 0),
            4: trans(load_image('adventurer-run-04.png', -1), 150, 111, 0, 0),
            5: trans(load_image('adventurer-run-05.png', -1), 150, 111, 0, 0)
        }

        self.run_left = {
            0: trans(load_image('adventurer-run-00.png', -1), 150, 111, 1, 0),
            1: trans(load_image('adventurer-run-01.png', -1), 150, 111, 1, 0),
            2: trans(load_image('adventurer-run-02.png', -1), 150, 111, 1, 0),
            3: trans(load_image('adventurer-run-03.png', -1), 150, 111, 1, 0),
            4: trans(load_image('adventurer-run-04.png', -1), 150, 111, 1, 0),
            5: trans(load_image('adventurer-run-05.png', -1), 150, 111, 1, 0)
        }

        self.run_counter = 0

        self.attack_right = {
            0: trans(load_image('adventurer-attack1-00.png', -1), 150, 111, 0, 0),
            1: trans(load_image('adventurer-attack1-01.png', -1),  150,  111, 0, 0),
            2: trans(load_image('adventurer-attack1-02.png', -1),  150, 111, 0, 0),
            3: trans(load_image('adventurer-attack1-03.png', -1), 150, 111, 0, 0),
            4: trans(load_image('adventurer-attack1-04.png', -1), 150, 111, 0, 0)
        }

        self.attack_left = {
            0: trans(load_image('adventurer-attack1-00.png', -1), 150, 111, 1, 0),
            1: trans(load_image('adventurer-attack1-01.png', -1), 150, 111, 1, 0),
            2: trans(load_image('adventurer-attack1-02.png', -1), 150, 111, 1, 0),
            3: trans(load_image('adventurer-attack1-03.png', -1), 150, 111, 1, 0),
            4: trans(load_image('adventurer-attack1-04.png', -1), 150, 111, 1, 0)
        }

        self.attack_counter = 0

        self.croach_right = {
            0: trans(load_image('adventurer-crouch-00.png', -1), 150, 111, 0, 0),
            1: trans(load_image('adventurer-crouch-01.png', -1), 150, 111, 0, 0),
            2: trans(load_image('adventurer-crouch-02.png', -1), 150, 111, 0, 0),
            3: trans(load_image('adventurer-crouch-03.png', -1), 150, 111, 0, 0)
        }

        self.croach_left = {
            0: trans(load_image('adventurer-crouch-00.png', -1), 150, 111, 1, 0),
            1: trans(load_image('adventurer-crouch-01.png', -1), 150, 111, 1, 0),
            2: trans(load_image('adventurer-crouch-02.png', -1), 150, 111, 1, 0),
            3: trans(load_image('adventurer-crouch-03.png', -1), 150, 111, 1, 0)
        }

        self.croach_counter = 0

        self.die_right = {
            0: trans(load_image('adventurer-die-00.png', -1), 150, 111, 0, 0),
            1: trans(load_image('adventurer-die-01.png', -1), 150, 111, 0, 0),
            2: trans(load_image('adventurer-die-02.png', -1), 150, 111, 0, 0),
            3: trans(load_image('adventurer-die-03.png', -1), 150, 111, 0, 0),
            4: trans(load_image('adventurer-die-04.png', -1), 150, 111, 0, 0),
            5: trans(load_image('adventurer-die-05.png', -1), 150, 111, 0, 0),
            6: trans(load_image('adventurer-die-06.png', -1), 150, 111, 0, 0)
        }

        self.die_left = {
            0: trans(load_image('adventurer-die-00.png', -1), 150, 111, 1, 0),
            1: trans(load_image('adventurer-die-01.png', -1), 150, 111, 1, 0),
            2: trans(load_image('adventurer-die-02.png', -1), 150, 111, 1, 0),
            3: trans(load_image('adventurer-die-03.png', -1), 150, 111, 1, 0),
            4: trans(load_image('adventurer-die-04.png', -1), 150, 111, 1, 0),
            5: trans(load_image('adventurer-die-05.png', -1), 150, 111, 1, 0),
            6: trans(load_image('adventurer-die-06.png', -1), 150, 111, 1, 0)
        }

        self.die_counter = 0

        self.speed = 300 / FPS

        self.iteration = 0

        self.is_staying = True

        self.last_right = True

        self.mask = pg.mask.from_surface(self.image)

        self.on_ground = True

        self.jump_speed = self.speed * 6

        self.counter_for_take_damage = 0

        self.several_damage_in_row = False

        self.iteration_attack = 0

        self.down_sprite = pg.sprite.Sprite(without_drawing, player_down)
        self.down_sprite.image = trans(load_image("blank.png", -1), width_platform - 25, 10, 0, 0)
        self.down_sprite.image.fill((0, 0, 255))
        self.down_sprite.rect = self.down_sprite.image.get_rect().move(self.rect.x + width_platform - 10, self.rect.y + self.image.get_height() - 5)

        self.add_dead_group = False

    def set_speed(self, new_speed):
        self.speed = new_speed

    def is_enemy_attack(self, group):
        for enemy in group:
            if enemy.is_attacking():
                return True
        return False

    def update(self, *args):
        self.iteration = (self.iteration + 1) % 40
        if self.hearts.is_dead():
            if self.iteration % 10 == 0:
                if self.last_right:
                    self.image = self.die_right[self.die_counter]
                else:
                    self.image = self.die_left[self.die_counter]
                self.die_counter = self.die_counter + 1
                if self.die_counter == len(self.die_right):
                    self.kill()
                    self.add(dead_group)
                    self.add_dead_group = True
            return
        collide = pg.sprite.spritecollide(self.down_sprite, uppart_platforms_group, False, pg.sprite.collide_mask)
        if not collide:
            self.rect = self.rect.move(0, self.speed * 2)
            self.on_ground = False
        else:
            self.jump_speed = 6 * self.speed
            self.on_ground = True

        collide_with_enemys = pg.sprite.spritecollide(self, enemy_group, False, pg.sprite.collide_mask)
        if args:
            if args[0][pg.K_g] and self.iteration % 5 == 0:
                self.hearts.take_damage()

            self.mask = pg.mask.from_surface(self.image)
            if args[0][pg.K_f]:
                self.iteration_attack = (self.iteration_attack + 1) % 10
                # print(self.attack_counter)
                if self.iteration % 3 == 0:
                    if self.last_right:
                        self.image = self.attack_right[self.attack_counter]
                    else:
                        self.image = self.attack_left[self.attack_counter]
                    self.attack_counter = (self.attack_counter + 1) % 5
                    if self.attack_counter == 3:
                        for enemy in collide_with_enemys:
                            enemy.take_damage()
            else:
                self.iteration_attack = 0
            if self.is_enemy_attack(collide_with_enemys):
                self.counter_for_take_damage += 1
                if self.counter_for_take_damage == 20 * (2 if self.several_damage_in_row else 1):
                    self.several_damage_in_row = True
                    self.hearts.take_damage()
                    self.counter_for_take_damage = 0
            else:
                self.several_damage_in_row = False
                self.counter_for_take_damage = 0
            if args[0][pg.K_SPACE]:
                if pg.sprite.spritecollide(self, downpart_platforms_group, False, pg.sprite.collide_mask):
                    self.jump_speed = 0
                self.is_staying = False

                self.rect = self.rect.move(0, -self.jump_speed)
                self.jump_speed -= self.speed // 3
                self.jump_speed = max(self.jump_speed, 0)
            elif not collide:
                self.jump_speed = 0

            if args[0][pg.K_DOWN] and self.iteration % 5 == 0:
                # if args[0][pg.K_SPACE]:
                #     self.rect = self.rect.move(0, 50)
                self.is_staying = False
                if self.iteration % 15 == 0:
                    if self.last_right:
                        self.image = self.croach_right[self.croach_counter]
                    else:
                        self.image = self.croach_left[self.croach_counter]
                    self.croach_counter = (self.croach_counter + 1) % 4
            if args[0][pg.K_LEFT] and not pg.sprite.spritecollide(self, rightpart_platforms_group, False, pg.sprite.collide_mask):
                self.is_staying = False
                self.last_right = False

                if self.iteration % 5 == 0:
                    self.image = self.run_left[self.run_counter]
                    self.run_counter = (self.run_counter + 1) % 6

                self.rect = self.rect.move(-self.speed, 0)
            if args[0][pg.K_RIGHT] and not pg.sprite.spritecollide(self, leftpart_platforms_group, False, pg.sprite.collide_mask):
                self.is_staying = False
                self.last_right = True

                if self.iteration % 5 == 0:
                    self.image = self.run_right[self.run_counter]
                    self.run_counter = (self.run_counter + 1) % 6

                self.rect = self.rect.move(self.speed, 0)
            if self.is_staying and not args[0][pg.K_DOWN] and self.iteration % 20 == 0:
                self.run_counter = 0
                self.attack_counter = 0
                if self.last_right:
                    self.image = self.idle_right[self.idle_counter]
                else:
                    self.image = self.idle_left[self.idle_counter]
                self.idle_counter = (self.idle_counter + 1) % 3
        self.is_staying = True
        self.mask = pg.mask.from_surface(self.image)
        
        self.down_sprite.rect = self.down_sprite.image.get_rect().move(self.rect.x + width_platform - 10, self.rect.y + self.image.get_height() - 10)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.first_it = False

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj, tp=None):

        if tp == "under_player":
            if self.first_it:
                self.first_it = True
            else:
                obj.rect.x -= self.dx
            # obj.rect.y -= self.dy
        else:
            obj.rect.x += self.dx

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class Game:
    def __init__(self):
        self.running = True
        self.win_screen_was = False
        self.timer_for_win = 0
        self.start()

    def load_level(self, filename):
        filename = "data/" + filename
        # читаем уровень, убирая символы перевода строки
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]

        # и подсчитываем максимальную длину
        self.max_width = max(map(len, level_map))

        # дополняем каждую строку пустыми клетками ('.')
        return list(map(lambda x: x.ljust(self.max_width, '.'), level_map))

    def generate_level(self, level, score):
        # new_player, x, y = None, None, None
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] in ['l', 'm', 'r', 'R', 'L']:
                    Platform(level[y][x], x, y)
                elif level[y][x] in ['G', 'g', 'B', 'x', 'o']:
                    Object(x, y, level[y][x])
                elif level[y][x] == 'C':
                    score.add_coin(x, y)
                elif level[y][x] == '@':
                    # Player(x, y)
                    self.player = Player(x, y)
                    self.player_x = x
                    self.player_y = y
                elif level[y][x] == 'E':
                    Skelet(x, y, score)
    # вернем игрока, а также размер поля в клетках
        # return new_player, x, y

    def start_screen(self):
        intro_text = ["ЗАСТАВКА", "",
                    "Нажмите кнопку мыши для начала!"]

        fon = pg.transform.scale(load_image('back.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        font = pg.font.Font(None, 30)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pg.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.terminate()
                elif event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN:
                    return  # начинаем игру
            pg.display.flip()
            clock.tick(FPS)
    
    def pause(self):
        fon = pg.transform.scale(load_image('back.png', -1), (WIDTH, HEIGHT))

        on_pause = pg.sprite.Group()

        screen.blit(fon, (0, 0))

        cont = pg.sprite.Sprite(on_pause)
        image = load_image("continue.png")
        cont.image = trans(image, image.get_width() // 2, image.get_height() // 2, 0, 0)
        cont.rect = cont.image.get_rect().move(WIDTH // 2 - cont.image.get_width() // 2, HEIGHT // 2 - cont.image.get_height() // 2)
        
        ext = pg.sprite.Sprite(on_pause)
        image = load_image("exit.png")
        ext.image = trans(image, image.get_width() // 2, image.get_height() // 2, 0, 0)
        ext.rect = ext.image.get_rect().move(WIDTH // 2 - ext.image.get_width() // 2, HEIGHT // 2 + cont.image.get_height())

        on_pause.draw(screen)

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.terminate()
                elif event.type == pg.KEYDOWN:
                    return  # продолжаем игру
                if event.type == pg.MOUSEBUTTONUP:
                    if cont.rect.collidepoint(event.pos):
                        return
                    if ext.rect.collidepoint(event.pos):
                        self.terminate()
            pg.display.flip()
            clock.tick(FPS)

    def game_over(self):
        screen.fill((0, 0, 0))
        fon = pg.transform.scale(load_image('death.jpg', -1), (WIDTH, HEIGHT))
        
        on_death = pg.sprite.Group()
        
        ext = pg.sprite.Sprite(on_death)
        image = load_image("des.png")
        ext.image = trans(image, image.get_width() // 2, image.get_height() // 2, 0, 0)
        ext.rect = ext.image.get_rect().move(WIDTH // 2 - ext.image.get_width() // 2, HEIGHT - ext.image.get_height() * 2)
        
        img = trans(load_image('grob.png', -1), 400, 400, 0, 0)
        player = pg.sprite.Sprite(on_death)
        player.image = img

        player.rect = ext.image.get_rect().move(WIDTH // 2 - player.image.get_width() // 2, HEIGHT // 2 - player.image.get_height() // 2)
        screen.blit(fon, (0, 0))

        on_death.draw(screen)
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.terminate()
                elif event.type == pg.KEYDOWN:
                    return
                if event.type == pg.MOUSEBUTTONUP:
                    if ext.rect.collidepoint(event.pos):
                        self.terminate()
            pg.display.flip()
            clock.tick(FPS)

    def win(self):
        fon = pg.transform.scale(load_image('back.png', -1), (WIDTH, HEIGHT))

        on_pause = pg.sprite.Group()

        screen.blit(fon, (0, 0))

        win = load_image('win.jpg', -1)

        win = trans(win, win.get_width() // 4, win.get_height() // 4, 0, 0)

        screen.blit(win, (WIDTH // 2 - win.get_width() // 2, 20))

        cont = pg.sprite.Sprite(on_pause)
        image = load_image("continue.png")
        cont.image = trans(image, image.get_width() // 2, image.get_height() // 2, 0, 0)
        cont.rect = cont.image.get_rect().move(WIDTH // 2 - cont.image.get_width() // 2, HEIGHT - cont.image.get_height() * 2 - 20)
        
        ext = pg.sprite.Sprite(on_pause)
        image = load_image("exit.png")
        ext.image = trans(image, image.get_width() // 2, image.get_height() // 2, 0, 0)
        ext.rect = ext.image.get_rect().move(WIDTH // 2 - ext.image.get_width() // 2, HEIGHT - ext.image.get_height() - 10)

        on_pause.draw(screen)

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.terminate()
                if event.type == pg.MOUSEBUTTONUP:
                    if cont.rect.collidepoint(event.pos):
                        return
                    if ext.rect.collidepoint(event.pos):
                        self.terminate()
            pg.display.flip()
            clock.tick(FPS)

    def terminate(self):
        pg.quit()
        exit()

    def start(self):
        # self.start_screen()
        self.game()

    def game(self):
        self.camera = Camera()
        self.score = Score()
        back_ground = trans(load_image("back.png"), WIDTH, HEIGHT, 0, 0)
        screen.blit(back_ground, (0, 0))
        self.generate_level(self.load_level("map.txt"), self.score)
        while self.running:
            if not enemy_group and not self.win_screen_was:
                self.timer_for_win = (self.timer_for_win + 1) % 121
                if self.timer_for_win == 120:
                    self.win()
                    self.win_screen_was = True
            if GAME_OVER:
                self.game_over()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.pause()
            pressed = pg.key.get_pressed()
            player_group.update(pressed)

            self.camera.update(self.player)
            for sprite in all_sprites:
                self.camera.apply(sprite)
            for sprite in without_drawing:
                self.camera.apply(sprite)
            for sprite in dead_group:
                self.camera.apply(sprite)
            coins_group.update()
            hearts_group.update()
            enemy_group.update(pressed)
            clock.tick(FPS)
            all_sprites.draw(screen)
            enemy_group.draw(screen)
            hearts_group.draw(screen)
            dead_group.draw(screen)
            self.score.print()
            if DEBUG:
                without_drawing.draw(screen)
            player_group.draw(screen)
            pg.display.flip()
            screen.blit(back_ground, (0, 0))


if __name__ == "__main__":
    Game()

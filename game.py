import pygame as pg
import json
import os
from math import ceil
from copy import copy


DEGUG = 1

horizontal_borders = pg.sprite.Group()
vertical_borders = pg.sprite.Group()
all_sprites = pg.sprite.Group()
player_group = pg.sprite.Group()
border_group = pg.sprite.Group()
enemy_group = pg.sprite.Group()
platforms_group = pg.sprite.Group()
hearts_group = pg.sprite.Group()
draw_test = pg.sprite.Group()

without_drawing = pg.sprite.Group()
uppart_platforms_group = pg.sprite.Group()

downpart_platforms_group = pg.sprite.Group()
leftpart_platforms_group = pg.sprite.Group()

rightpart_platforms_group = pg.sprite.Group()

pg.init()

cfg = open("cfg.json", "r")
data = json.load(cfg)
cfg.close()

SIZE = WIDTH, HEIGHT = tuple(map(int, data['resolution'].split(';')))
FPS = int(data['fps'])

screen = pg.display.set_mode(SIZE)
screen.fill((0, 0, 0))
clock = pg.time.Clock()


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
    return pg.transform.flip(pg.transform.scale(img, (width, height)), by_x, by_y)


def any_colide_mask(first, group):
    for el in group:
        if pg.sprite.collide_mask(first, el):
            return True
    return False


# player_image = trans(load_image('adventurer-run-00.png'), 50, 37, 1, 0)

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

tile_images = {
    'box': trans(load_image('box.png'), width_platform, height_platform, 0, 0), 
    'grass': trans(load_image('box.png'), width_platform, height_platform, 0, 0)
}
platform_images = {
    'l': trans(load_image('platform1.png', -1, 1), width_platform, height_platform, 0, 0), 
    'm': trans(load_image('platform2.png'), width_platform, height_platform, 0, 0), 
    "r": trans(load_image('platform3.png', -1, 1, 1), width_platform, height_platform, 0, 0)
}


class Part(pg.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = trans(load_image("blank.png", -1), width, height, 0, 0)


class Platform(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(platforms_group, all_sprites)
        self.image = platform_images[tile_type]
        self.rect = self.image.get_rect().move(width_platform * pos_x, height_platform * pos_y)
        self.mask = pg.mask.from_surface(self.image)
        self.up_sprite = pg.sprite.Sprite(uppart_platforms_group, draw_test, without_drawing)
        self.up_sprite.image = trans(load_image("blank.png", -1), width_platform - 4, 5, 0, 0)
        self.up_sprite.image.fill((0, 255, 0))
        if not DEGUG:
            self.up_sprite.image.set_alpha(0)
        self.up_sprite.rect = self.up_sprite.image.get_rect().move(width_platform * pos_x + 2, height_platform * pos_y)

        self.down_sprite = pg.sprite.Sprite(downpart_platforms_group, draw_test, without_drawing)
        self.down_sprite.image = trans(load_image("blank.png", -1), width_platform - 4, 5, 0, 0)
        self.down_sprite.image.fill((0, 0, 255))
        if not DEGUG:
            self.down_sprite.image.set_alpha(0)
        self.down_sprite.rect = self.down_sprite.image.get_rect().move(width_platform * pos_x + 2, height_platform * pos_y + self.image.get_height())

        if tile_type == 'l':
            self.left_sprite = pg.sprite.Sprite(leftpart_platforms_group, draw_test, without_drawing)
            self.left_sprite.image = trans(load_image("blank.png", -1), 5, height_platform, 0, 0)
            self.left_sprite.image.fill((255, 0, 255))
            if not DEGUG:
                self.left_sprite.image.set_alpha(0)
            self.left_sprite.rect = self.left_sprite.image.get_rect().move(width_platform * pos_x, height_platform * pos_y + 3)
        
        if tile_type == 'r':
            self.right_sprite = pg.sprite.Sprite(rightpart_platforms_group, draw_test, without_drawing)
            self.right_sprite.image = trans(load_image("blank.png", -1), 5, height_platform, 0, 0)
            self.right_sprite.image.fill((255, 0, 0))
            if not DEGUG:
                self.right_sprite.image.set_alpha(0)
            self.right_sprite.rect = self.right_sprite.image.get_rect().move(width_platform * pos_x + self.image.get_width(), height_platform * pos_y + 3)


class Skelet(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, enemy_group)
        img = load_image("Skeleton Walk.png", -1)
        h = 111
        img = trans(img, img.get_width() * 3, h, 0, 0)
        self.frames_right = self.cut_sheet(img, 13, 1)
        self.frames_left = self.cut_sheet(trans(img, img.get_width(), h, 1, 0), 13, 1)
        self.cur_frame = 0
        self.image = self.frames_left[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * x + 15, tile_height * y + 5)
        self.mask = pg.mask.from_surface(self.image)
        self.iteration = 0
    
    def cut_sheet(self, sheet, columns, rows):
        frames = []
        self.rect = pg.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frames.append(sheet.subsurface(pg.Rect(
                    frame_location, self.rect.size)))
        return frames

    def update(self):
        if not pg.sprite.spritecollide(self, platforms_group, False, pg.sprite.collide_mask):
            self.rect = self.rect.move(0, 1)
        if self.iteration % 10 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames_right)
            self.image = self.frames_right[self.cur_frame]
        self.iteration = (self.iteration + 1) % 40


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

    def take_damage(self):
        self.col -= 1
        print(1)
        self.damage_just_taken = True
        if self.col == 3:
            self.hearts = [trans(load_image(f'almosthalflife/h{i}.png', -1), 2 * 64, 2 * 16, 0, 0) for i in range(1, 14)]
        if self.col == 2:
            self.hearts = [trans(load_image(f'halflife/h{i}.png', -1), 2 * 64, 2 * 16, 0, 0) for i in range(1, 14)]
        if self.col == 1:
            self.hearts = [trans(load_image(f'onelife/h{i}.png', -1), 2 * 64, 2 * 16, 0, 0) for i in range(1, 14)]
        if self.col == 0:
            self.hearts = [trans(load_image(f'death/death{i}.png', -1), 2 * 64, 2 * 16, 0, 0) for i in range(1, 3)]
            self.mod = 2
            print("DEATH!")

    def update(self):
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
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)

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

        # self.falling_right = {
        #     0: trans(load_image('adventurer-fall-00.png', -1), 150, 111, 0, 0),
        #     1: trans(load_image('adventurer-fall-01.png', -1), 150, 111, 0, 0)
        # }

        # self.falling_left = {
        #     0: trans(load_image('adventurer-jump-03.png', -1), 150, 111, 1, 0)
        #     # 1: trans(load_image('adventurer-fall-01.png', -1), 150, 111, 1, 0)
        # }

        # self.falling_counter = 0

        self.speed = 300 / FPS

        self.iteration = 0

        self.is_staying = True

        self.last_right = True

        self.mask = pg.mask.from_surface(self.image)

        self.on_ground = True

        self.jump_speed = self.speed * 6

        self.group = pg.sprite.Group()

    def set_speed(self, new_speed):
        self.speed = new_speed
    
    def update(self, *args):
        self.iteration = (self.iteration + 1) % 40
        # ref
        collide = pg.sprite.spritecollide(self, uppart_platforms_group, False, pg.sprite.collide_mask)
        # print(collide)
        # for el in collide:
            # print(el.rect.x, el.rect.y, el.rect.x + el.rect.width, el.rect.y + el.rect.height, 'our:', self.rect.x, self.rect.y)
        if not collide:
            self.rect = self.rect.move(0, self.speed * 2)
            self.on_ground = False
        else:
            self.jump_speed = 6 * self.speed
            self.on_ground = True
        #
        # if not self.on_ground and self.iteration % 4 == 0:
        #     if self.last_right:
        #         self.image = self.falling_right[self.falling_counter]
        #     else:
        #         self.image = self.falling_left[self.falling_counter]
        #     self.falling_counter = (self.falling_counter + 1) % 1
        #     self.is_staying = False
        if args:
            if args[0][pg.K_g] and self.iteration % 5 == 0:
                self.hearts.take_damage()

            self.mask = pg.mask.from_surface(self.image)
            if args[0][pg.K_f] and self.iteration % 3 == 0:
                if self.last_right:
                    self.image = self.attack_right[self.attack_counter]
                else:
                    self.image = self.attack_left[self.attack_counter]
                self.attack_counter = (self.attack_counter + 1) % 5
            if args[0][pg.K_SPACE]:
                if pg.sprite.spritecollide(self, downpart_platforms_group, False, pg.sprite.collide_mask):
                    self.jump_speed = 0
                self.is_staying = False
                
                self.rect = self.rect.move(0, -self.jump_speed)
                self.jump_speed -= self.speed // 3
                self.jump_speed = max(self.jump_speed, 0)

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
            # print(pg.sprite.spritecollide(self, leftpart_platforms_group, False, pg.sprite.collide_mask))
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
                # print(self.idle_counter)
        self.is_staying = True
        self.mask = pg.mask.from_surface(self.image)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0
        
    # сдвинуть объект obj на смещение камеры
    def apply(self, obj, tp=None):
        obj.rect.x += self.dx
        # if tp == "under_player":
        #     obj.rect.y += self.dy
    
    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class Game:
    def __init__(self):
        self.running = True
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
    
    def generate_level(self, level):
        # new_player, x, y = None, None, None
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] in ['l', 'm', 'r']:
                    Platform(level[y][x], x, y)
                elif level[y][x] == '@':
                    # Player(x, y)
                    self.player = Player(x, y)
                    self.player_x = x
                    self.player_y = y
                elif level[y][x] == 'E':
                    Skelet(x, y)
    # вернем игрока, а также размер поля в клетках            
        # return new_player, x, y

    def start_screen(self):
        intro_text = ["ЗАСТАВКА", "",
                    "Нажмите кнопку мыши для начала!"]

        fon = pg.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
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

    def terminate(self):
        pg.quit()
        exit()

    def start(self):
        # self.start_screen()
        self.game()

    def game(self):
        self.camera = Camera()
        back_ground = trans(load_image("back.png"), WIDTH, HEIGHT, 0, 0)
        screen.blit(back_ground, (0, 0))
        self.generate_level(self.load_level("map.txt"))
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                # if event.type == pg.KEYDOWN:
            pressed = pg.key.get_pressed()
            player_group.update(pressed)
            
            self.camera.update(self.player)
            for sprite in all_sprites:
                self.camera.apply(sprite )
            for sprite in without_drawing:
                self.camera.apply(sprite)
            hearts_group.update()
            enemy_group.update()
            clock.tick(FPS)
            all_sprites.draw(screen)
            hearts_group.draw(screen)
            draw_test.draw(screen)
            player_group.draw(screen)
            # print(player_group)
            pg.display.flip()
            screen.blit(back_ground, (0, 0))


if __name__ == "__main__":
    Game()
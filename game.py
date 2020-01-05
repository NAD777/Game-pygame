import pygame as pg
import json
import os


horizontal_borders = pg.sprite.Group()
vertical_borders = pg.sprite.Group()
all_sprites = pg.sprite.Group()
player_group = pg.sprite.Group()
border_group = pg.sprite.Group()
enemy_group = pg.sprite.Group()

pg.init()

cfg = open("cfg.json", "r")
data = json.load(cfg)
cfg.close()

SIZE = WIDTH, HEIGHT = tuple(map(int, data['resolution'].split(';')))
FPS = int(data['fps'])

screen = pg.display.set_mode(SIZE)
screen.fill((0, 0, 0))
clock = pg.time.Clock()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    image = pg.image.load(fullname).convert()
    if color_key is not None: 
        if color_key == -1:
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


"""
index:
0 - our class righter than other with wich he collide
1 - downer
2 - lefter
3 - upper
"""

LEFTER = 0
UPPER = 1
RIGHTER = 2
DOWNER = 3


def where_collide(cls, dif):    
    arr = [0, 0, 0, 0]
    for el in dif:
        if el.rect.x + el.rect.width >= cls.rect.x >= el.rect.x and (el.rect.y <= cls.rect.y <= el.rect.y + el.rect.height):
            arr[0] = 1
        if el.rect.x + el.rect.width >= cls.rect.x + cls.rect.width >= el.rect.x and (el.rect.y <= cls.rect.y <= el.rect.y + el.rect.height):
            arr[2] = 1
        if el.rect.y + el.rect.height >= cls.rect.y + cls.rect.height >= el.rect.y and (el.rect.x <= cls.rect.x <= el.rect.x + el.rect.width):
            arr[3] = 1
        if el.rect.y + el.rect.height >= cls.rect.y >= el.rect.y and (el.rect.x <= cls.rect.x <= el.rect.x + el.rect.width):
            arr[1] = 1
    return arr


tile_images = {'wall': load_image('box.png'), 'empty': load_image('grass.png')}
k = int(WIDTH / 960)
# player_image = trans(load_image('adventurer-run-00.png'), k * 50, k * 37, 1, 0)

tile_width = tile_height = 100


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


class Enemy(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, enemy_group)
        self.image = load_image('adventurer-idle-00.png', -1)
        self.rect = self.image.get_rect().move(tile_width * x + 15, tile_height * y + 5)
        self.mask = pg.mask.from_surface(self.image)


class Player(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        
        self.idle_right = {
            0: trans(load_image('adventurer-idle-00.png', -1), k * 150, k * 111, 0, 0),
            1: trans(load_image('adventurer-idle-01.png', -1), k * 150, k * 111, 0, 0),
            2: trans(load_image('adventurer-idle-02.png', -1), k * 150, k * 111, 0, 0)
        }

        self.image = self.idle_right[0]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)

        self.idle_counter = 0

        self.idle_left = {
            0: trans(load_image('adventurer-idle-00.png', -1), k * 150, k * 111, 1, 0),
            1: trans(load_image('adventurer-idle-01.png', -1), k * 150, k * 111, 1, 0),
            2: trans(load_image('adventurer-idle-02.png', -1), k * 150, k * 111, 1, 0)
        }
        
        self.run_right = {
            0: trans(load_image('adventurer-run-00.png', -1), k * 150, k * 111, 0, 0),
            1: trans(load_image('adventurer-run-01.png', -1), k * 150, k * 111, 0, 0),
            2: trans(load_image('adventurer-run-02.png', -1), k * 150, k * 111, 0, 0),
            3: trans(load_image('adventurer-run-03.png', -1), k * 150, k * 111, 0, 0),
            4: trans(load_image('adventurer-run-04.png', -1), k * 150, k * 111, 0, 0),
            5: trans(load_image('adventurer-run-05.png', -1), k * 150, k * 111, 0, 0)
        }

        self.run_left = {
            0: trans(load_image('adventurer-run-00.png', -1), k * 150, k * 111, 1, 0),
            1: trans(load_image('adventurer-run-01.png', -1), k * 150, k * 111, 1, 0),
            2: trans(load_image('adventurer-run-02.png', -1), k * 150, k * 111, 1, 0),
            3: trans(load_image('adventurer-run-03.png', -1), k * 150, k * 111, 1, 0),
            4: trans(load_image('adventurer-run-04.png', -1), k * 150, k * 111, 1, 0),
            5: trans(load_image('adventurer-run-05.png', -1), k * 150, k * 111, 1, 0)
        }

        self.run_counter = 0

        self.attack_right = {
            0: trans(load_image('adventurer-attack1-00.png', -1), k * 150, k * 111, 0, 0),
            1: trans(load_image('adventurer-attack1-01.png', -1), k * 150, k * 111, 0, 0),
            2: trans(load_image('adventurer-attack1-02.png', -1), k * 150, k * 111, 0, 0),
            3: trans(load_image('adventurer-attack1-03.png', -1), k * 150, k * 111, 0, 0),
            4: trans(load_image('adventurer-attack1-04.png', -1), k * 150, k * 111, 0, 0)
        }
        
        self.attack_left = {
            0: trans(load_image('adventurer-attack1-00.png', -1), k * 150, k * 111, 1, 0),
            1: trans(load_image('adventurer-attack1-01.png', -1), k * 150, k * 111, 1, 0),
            2: trans(load_image('adventurer-attack1-02.png', -1), k * 150, k * 111, 1, 0),
            3: trans(load_image('adventurer-attack1-03.png', -1), k * 150, k * 111, 1, 0),
            4: trans(load_image('adventurer-attack1-04.png', -1), k * 150, k * 111, 1, 0)
        }

        self.attack_counter = 0

        self.croach_right = {
            0: trans(load_image('adventurer-crouch-00.png', -1), k * 150, k * 111, 0, 0),
            1: trans(load_image('adventurer-crouch-01.png', -1), k * 150, k * 111, 0, 0),
            2: trans(load_image('adventurer-crouch-02.png', -1), k * 150, k * 111, 0, 0),
            3: trans(load_image('adventurer-crouch-03.png', -1), k * 150, k * 111, 0, 0)
        }

        self.croach_left = {
            0: trans(load_image('adventurer-crouch-00.png', -1), k * 150, k * 111, 1, 0),
            1: trans(load_image('adventurer-crouch-01.png', -1), k * 150, k * 111, 1, 0),
            2: trans(load_image('adventurer-crouch-02.png', -1), k * 150, k * 111, 1, 0),
            3: trans(load_image('adventurer-crouch-03.png', -1), k * 150, k * 111, 1, 0)
        }

        self.croach_counter = 0

        self.speed = 200 * k / FPS

        self.iteration = 0

        self.is_staying = True

        self.last_right = True

        self.mask = pg.mask.from_surface(self.image)

        self.on_ground = True
    
    def set_speed(self, new_speed):
        self.speed = new_speed
    
    def update(self, *args):
        self.iteration = (self.iteration + 1) % 40
        print(where_collide(self, pg.sprite.spritecollide(self, enemy_group, False, pg.sprite.collide_mask)))

        # ref
        collide = pg.sprite.spritecollide(self, border_group, False)
        # print(collide)
        # for el in collide:
            # print(el.rect.x, el.rect.y, el.rect.x + el.rect.width, el.rect.y + el.rect.height, 'our:', self.rect.x, self.rect.y)
        if not collide:
            # self.rect = self.rect.move(0, self.speed * 2)
            self.on_ground = False
        else:
            self.on_ground = True
        #
        if args:
            self.mask = pg.mask.from_surface(self.image)
            if args[0][pg.K_f] and self.iteration % 3 == 0:
                if self.last_right:
                    self.image = self.attack_right[self.attack_counter]
                else:
                    self.image = self.attack_left[self.attack_counter]
                self.attack_counter = (self.attack_counter + 1) % 5
            if args[0][pg.K_UP]:
                self.is_staying = False
                
                self.rect = self.rect.move(0, -self.speed)
            if args[0][pg.K_DOWN] and self.iteration % 5 == 0:
                if args[0][pg.K_SPACE]:
                    self.rect = self.rect.move(0, 50)
                self.is_staying = False
                if self.iteration % 15 == 0:
                    if self.last_right:
                        self.image = self.croach_right[self.croach_counter]
                    else:
                        self.image = self.croach_left[self.croach_counter]
                    self.croach_counter = (self.croach_counter + 1) % 4
            if args[0][pg.K_LEFT]:
                self.is_staying = False
                self.last_right = False
                
                if self.iteration % 5 == 0:
                    self.image = self.run_left[self.run_counter]
                    self.run_counter = (self.run_counter + 1) % 6
                
                self.rect = self.rect.move(-self.speed, 0)
            if args[0][pg.K_RIGHT]:
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


class Game:
    def __init__(self):
        self.running = True
        self.start()
    
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
        Border(5, 5, WIDTH - 5, 5)
        Border(5, HEIGHT - 5, WIDTH - 5, HEIGHT - 5)
        Border(5, 5, 5, HEIGHT)
        Border(WIDTH - 5, 5, WIDTH - 5, HEIGHT - 5)
        
        self.game()
        # self.start_screen()

    def game(self):

        back_ground = trans(load_image("back.png"), WIDTH, HEIGHT, 0, 0)
        screen.blit(back_ground, (0, 0))
    
        enemy = Enemy(2, 2)
        self.player = Player(4, 4)
        while self.running:
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                # if event.type == pg.KEYDOWN:
            pressed = pg.key.get_pressed()
            player_group.update(pressed)
            clock.tick(FPS)
            all_sprites.draw(screen)
            player_group.draw(screen)
            # print(player_group)
            pg.display.flip()
            screen.blit(back_ground, (0, 0))


if __name__ == "__main__":
    Game()
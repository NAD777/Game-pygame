import pygame as pg
import json
import os


horizontal_borders = pg.sprite.Group()
vertical_borders = pg.sprite.Group()
all_sprites = pg.sprite.Group()
player_group = pg.sprite.Group()


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
        pass
        # image = image.convert_alpha()
    return image


def trans(img, width, height, by_x, by_y):
    return pg.transform.flip(pg.transform.scale(img, (width, height)), by_x, by_y)


tile_images = {'wall': load_image('box.png'), 'empty': load_image('grass.png')}
k = 3
player_image = trans(load_image('adventurer-run-00.png'), k * 50, k * 37, 1, 0)

tile_width = tile_height = 50


class Border(pg.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pg.Surface([1, y2 - y1])
            self.rect = pg.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pg.Surface([x2 - x1, 1])
            self.rect = pg.Rect(x1, y1, x2 - x1, 1)


class Player(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)
        
        self.idle_right = {
            0: trans(load_image('adventurer-idle-00.png'), k * 50, k * 37, 0, 0),
            1: trans(load_image('adventurer-idle-01.png'), k * 50, k * 37, 0, 0),
            2: trans(load_image('adventurer-idle-02.png'), k * 50, k * 37, 0, 0)
        }

        self.idle_counter = 0

        self.idle_left = {
            0: trans(load_image('adventurer-idle-00.png', -1), k * 50, k * 37, 1, 0),
            1: trans(load_image('adventurer-idle-01.png', -1), k * 50, k * 37, 1, 0),
            2: trans(load_image('adventurer-idle-02.png', -1), k * 50, k * 37, 1, 0)
        }
        
        self.run_right = {
            0: trans(load_image('adventurer-run-00.png'), k * 50, k * 37, 0, 0),
            1: trans(load_image('adventurer-run-01.png'), k * 50, k * 37, 0, 0),
            2: trans(load_image('adventurer-run-02.png'), k * 50, k * 37, 0, 0),
            3: trans(load_image('adventurer-run-03.png'), k * 50, k * 37, 0, 0),
            4: trans(load_image('adventurer-run-04.png'), k * 50, k * 37, 0, 0),
            5: trans(load_image('adventurer-run-05.png'), k * 50, k * 37, 0, 0)
        }

        self.run_left = {
            0: trans(load_image('adventurer-run-00.png'), k * 50, k * 37, 1, 0),
            1: trans(load_image('adventurer-run-01.png'), k * 50, k * 37, 1, 0),
            2: trans(load_image('adventurer-run-02.png'), k * 50, k * 37, 1, 0),
            3: trans(load_image('adventurer-run-03.png'), k * 50, k * 37, 1, 0),
            4: trans(load_image('adventurer-run-04.png'), k * 50, k * 37, 1, 0),
            5: trans(load_image('adventurer-run-05.png'), k * 50, k * 37, 1, 0)
        }

        self.run_counter = 0
        
        self.speed = 200 / FPS

        self.iteration = 0

        self.is_staying = True

        self.last_right = True
    
    def set_speed(self, new_speed):
        self.speed = new_speed
    
    def update(self, *args):
        self.iteration = (self.iteration + 1) % 40
        if args:
            if args[0][pg.K_UP]:
                self.is_staying = False
                self.rect = self.rect.move(0, -self.speed)
            if args[0][pg.K_DOWN]:
                self.is_staying = False
                self.rect = self.rect.move(0, self.speed)
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
            if self.is_staying and self.iteration % 20 == 0:
                self.run_counter = 0

                if self.last_right:
                    self.image = self.idle_right[self.idle_counter]
                else:
                    self.image = self.idle_left[self.idle_counter]
                self.idle_counter = (self.idle_counter + 1) % 3
                print(self.idle_counter)
        self.is_staying = True


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
        Border(0, 0, WIDTH, 0)
        Border(0, HEIGHT, WIDTH, HEIGHT)
        Border(0, 0, 0, HEIGHT)
        Border(WIDTH, 0, WIDTH, HEIGHT)
        
        self.game()
        # self.start_screen()

    def game(self):
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
            print(player_group)
            pg.display.flip()
            screen.fill((255, 255, 255))


if __name__ == "__main__":
    Game()
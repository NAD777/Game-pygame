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
        image = image.convert_alpha()
    return image


tile_images = {'wall': load_image('box.png'), 'empty': load_image('grass.png')}
player_image = load_image('mario.png')

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
        
        self.speed = 200 / FPS
    
    def set_speed(self, new_speed):
        self.speed = new_speed
    
    def update(self, *args):
        if args:
            if args[0][pg.K_UP]:
                self.rect = self.rect.move(0, -self.speed)
            if args[0][pg.K_DOWN]:
                self.rect = self.rect.move(0, self.speed)
            if args[0][pg.K_LEFT]:
                self.rect = self.rect.move(-self.speed, 0)
            if args[0][pg.K_RIGHT]:
                self.rect = self.rect.move(self.speed, 0)


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
        Border(5, 5, 5, HEIGHT - 5)
        Border(WIDTH - 5, 5, WIDTH - 5, HEIGHT - 5)
        
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
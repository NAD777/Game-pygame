import pygame as pg
import json
import os


class Game:
    def __init__(self):
        cfg = open("cfg.json", "r")
        data = json.load(cfg)
        self.size = self.width, self.height = tuple(map(int, data['resolution'].split(';')))
        self.FPS = int(data['fps'])
        cfg.close()

        # start pygame
        pg.init()
        self.screen = pg.display.set_mode(self.size)
        self.screen.fill((0, 0, 0))
        self.clock = pg.time.Clock()

        self.start()
    
    def load_image(self, name, color_key=None):
        fullname = os.path.join('data', name)
        image = pg.image.load(fullname).convert()
        if color_key is not None: 
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        else:
            image = image.convert_alpha()
        return image

    def start_screen(self):
        intro_text = ["ЗАСТАВКА", "",
                    "Нажмите кнопку мыши для начала!"]

        fon = pg.transform.scale(self.load_image('fon.jpg'), (self.width, self.height))
        self.screen.blit(fon, (0, 0))
        font = pg.font.Font(None, 30)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pg.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            self.screen.blit(string_rendered, intro_rect)

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.terminate()
                elif event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN:
                    return  # начинаем игру
            pg.display.flip()
            self.clock.tick(self.FPS)

    def terminate(self):
        pg.quit()
        exit()

    def start(self):
        self.start_screen()


if __name__ == "__main__":
    Game()
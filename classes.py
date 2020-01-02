import pygame as pg

horizontal_borders = pg.sprite.Group()
vertical_borders = pg.sprite.Group()
all_sprites = pg.sprite.Group()
player_group = pg.sprite.Group()


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


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)
        
        self.speed = None
    
    def set_speed(self, new_speed):
        self.speed = new_speed
    
    def update(self, *args):
        if args and args[0].type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.rect = self.rect.move(0, -50)
            if event.key == pygame.K_DOWN:
                self.rect = self.rect.move(0, 50)
            if event.key == pygame.K_LEFT:
                self.rect = self.rect.move(-50, 0)
            if event.key == pygame.K_RIGHT:
                self.rect = self.rect.move(50, 0)
import pygame
import os


all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
border_group = pygame.sprite.Group()

pygame.init()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if color_key is not None: 
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


tile_width = tile_height = 50
FPS = 60

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(player_group, all_sprites)
        self.image = load_image('adventurer-idle-00.png', -1)
        self.rect = self.image.get_rect().move(tile_width * x + 15, tile_height * y + 5)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 200 / FPS
    
    def update(self, *args):
        print(pygame.sprite.spritecollide(self, border_group, False, pygame.sprite.collide_mask))
        if args:
            if args[0][pygame.K_LEFT]:
                self.rect = self.rect.move(-self.speed, 0)
            if args[0][pygame.K_RIGHT]:
                self.rect = self.rect.move(self.speed, 0)

            if args[0][pygame.K_UP]:
                self.rect = self.rect.move(0, -self.speed)

            if args[0][pygame.K_DOWN]:
                self.rect = self.rect.move(0, self.speed)

            
class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x, y):
        super().__init__(all_sprites, border_group)
        self.image = load_image('adventurer-idle-00.png', -1)
        self.rect = self.image.get_rect().move(tile_width * x + 15, tile_height * y + 5)
        self.mask = pygame.mask.from_surface(self.image)

class Border1(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(border_group, all_sprites)
        if x1 == x2:  # вертикальная стенка
            self.image = pygame.Surface([5, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 5, y2 - y1)
        else:  # горизонтальная стенка
            self.image = pygame.Surface([x2 - x1, 5])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 5)
        self.mask = pygame.mask.from_surface(self.image)


running = True
size = width, height = 1280, 720
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
player = Player(4, 4)
obj = Border(2, 2)
bor = Border1(5, 5, width - 5, 5)
while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # if event.type == pg.KEYDOWN:
            pressed = pygame.key.get_pressed()
            player_group.update(pressed)
            clock.tick(FPS)
            all_sprites.draw(screen)
            # print(player_group)
            pygame.display.flip()
            screen.fill((0, 255, 0))
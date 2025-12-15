import os
import pygame
import config
from core.tiles import tile_image


class BaseSprite(pygame.sprite.Sprite):
    _images: dict[str, pygame.Surface] = {}

    def __init__(self, row: int, col: int, file_name: str, transparent_color=None):
        super().__init__()

        if file_name in BaseSprite._images:
            img = BaseSprite._images[file_name]
        else:
            path = os.path.join(config.IMG_FOLDER, file_name)
            img = pygame.image.load(path).convert()
            img = pygame.transform.scale(img, (config.TILE_SIZE, config.TILE_SIZE))
            BaseSprite._images[file_name] = img

        self.image = img.copy()
        if transparent_color is not None:
            self.image.set_colorkey(transparent_color)

        self.rect = self.image.get_rect()
        self.row = row
        self.col = col
        self.rect.topleft = (col * config.TILE_SIZE, row * config.TILE_SIZE)

    def place_to(self, row: int, col: int) -> None:
        self.row = row
        self.col = col
        self.rect.x = col * config.TILE_SIZE
        self.rect.y = row * config.TILE_SIZE

    def move_towards_cell(self, target_row: int, target_col: int) -> None:
        # 1px-per-tick motion (exactly like your original style)
        dx = target_col * config.TILE_SIZE - self.rect.x
        dy = target_row * config.TILE_SIZE - self.rect.y
        if dx != 0:
            self.rect.x += 1 if dx > 0 else -1
        if dy != 0:
            self.rect.y += 1 if dy > 0 else -1


class TileSprite(BaseSprite):
    def __init__(self, row: int, col: int, kind: str):
        super().__init__(row, col, tile_image(kind))


class GoalSprite(BaseSprite):
    def __init__(self, row: int, col: int):
        super().__init__(row, col, "x.png", config.DARK_GREEN)


class TrailSprite(BaseSprite):
    def __init__(self, row: int, col: int, num: int):
        super().__init__(row, col, "trail.png", config.DARK_GREEN)
        self.num = num

    def draw_number(self, screen: pygame.Surface) -> None:
        text = config.GAME_FONT.render(str(self.num), True, config.WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class AgentSprite(BaseSprite):
    def __init__(self, row: int, col: int, file_name: str):
        super().__init__(row, col, file_name, config.DARK_GREEN)

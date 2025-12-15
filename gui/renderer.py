import pygame
import config
from gui.sprites import TrailSprite


class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        self.tiles = pygame.sprite.Group()
        self.trails = pygame.sprite.Group()
        self.agents = pygame.sprite.Group()

        self.path_cost = 0
        self.game_over = False

    def clear_trails(self) -> None:
        self.trails = pygame.sprite.Group()

    def add_trail(self, row: int, col: int, num: int) -> None:
        self.trails.add(TrailSprite(row, col, num))

    def draw(self) -> None:
        # ribbon background
        self.screen.fill(config.BLACK, rect=(0, config.HEIGHT, config.WIDTH, config.RIBBON_HEIGHT))

        self.tiles.draw(self.screen)
        self.trails.draw(self.screen)
        for t in self.trails:
            t.draw_number(self.screen)
        self.agents.draw(self.screen)

        score = config.GAME_FONT.render(f"Score: {self.path_cost}", True, config.GREEN)
        self.screen.blit(score, (10, config.HEIGHT + config.RIBBON_HEIGHT // 5))

        if self.game_over:
            over = config.GAME_FONT.render("GAME OVER", True, config.RED)
            rect = over.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2))
            self.screen.blit(over, rect)

        pygame.display.flip()

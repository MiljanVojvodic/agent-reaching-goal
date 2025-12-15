import pygame
import config

from core.map_loader import load_map
from core.grid import Grid
from core.path import Path
from core.agents import create_agent

from gui.sprites import TileSprite, GoalSprite, AgentSprite
from gui.renderer import Renderer


class EndGame(Exception):
    pass


class Game:
    def __init__(self, map_path: str, agent_name: str, agent_sprite_png: str | None = None):
        pygame.display.set_caption("StepPy")

        loaded = load_map(map_path)
        self.grid = Grid(loaded.tile_map)
        self.start = loaded.start
        self.goal = loaded.goal

        # compute scaling
        config.TILE_SIZE = min(config.MAX_HEIGHT // self.grid.rows, config.MAX_WIDTH // self.grid.cols)
        config.HEIGHT = config.TILE_SIZE * self.grid.rows
        config.WIDTH = config.TILE_SIZE * self.grid.cols
        config.GAME_SPEED = int(config.TILE_SIZE * 2)

        pygame.font.init()
        config.GAME_FONT = pygame.font.Font(None, max(12, config.TILE_SIZE // 3))
        config.RIBBON_HEIGHT = int(config.GAME_FONT.size("")[1] * 1.5)

        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT + config.RIBBON_HEIGHT))
        self.clock = pygame.time.Clock()

        self.renderer = Renderer(self.screen)

        # build tile sprites
        for r in range(self.grid.rows):
            for c in range(self.grid.cols):
                kind = self.grid.get(r, c).kind
                self.renderer.tiles.add(TileSprite(r, c, kind))

        # goal sprite
        gr, gc = self.goal
        self.renderer.tiles.add(GoalSprite(gr, gc))

        # agent algorithm (core)
        self.agent = create_agent(agent_name)

        # agent sprite (gui)
        sr, sc = self.start
        if agent_sprite_png is None:
            agent_sprite_png = f"{agent_name}.png"
        self.agent_sprite = AgentSprite(sr, sc, agent_sprite_png)
        self.renderer.agents.add(self.agent_sprite)

        self.running = True
        self.playing = False
        self.game_over = False

        self._path: list[tuple[int, int]] = []
        self._path_index = 0
        self._target: tuple[int, int] | None = None
        self._step_num = 1

    def compute_path(self) -> Path:
        p = self.agent.find_path(self.grid, self.start, self.goal)
        if not p.nodes:
            raise ValueError("Agent returned empty path (goal unreachable or bug).")
        p.validate_adjacent_4(self.grid.rows, self.grid.cols)
        if p.nodes[0] != self.start:
            raise ValueError("Path must start at the start position.")
        return p

    def path_cost(self, nodes: list[tuple[int, int]]) -> int:
        return sum(self.grid.get(r, c).cost for (r, c) in nodes)

    def run(self) -> None:
        # compute path once
        path = self.compute_path()
        self._path = path.nodes[:]  # list[(r,c)]
        print(f"Agent: {self.agent.name}")
        print("Path:", ", ".join(str(p) for p in self._path))
        print("Path length:", len(self._path))
        print("Path cost:", self.path_cost(self._path))

        # init render state
        self.renderer.path_cost = self.grid.get(*self._path[0]).cost
        self._path_index = 0
        self._target = self._path[0]

        # main loop
        while self.running:
            try:
                self.events()
                if self.playing and not self.game_over:
                    self.tick()
                self.draw()
                self.clock.tick(config.GAME_SPEED)
            except EndGame:
                self.finish()
            except Exception:
                self.game_over = True
                self.renderer.game_over = True
                raise

    def tick(self) -> None:
        # if we're exactly on target cell -> advance to next
        if self._target is None:
            raise EndGame()

        tr, tc = self._target
        if self.agent_sprite.row == tr and self.agent_sprite.col == tc and \
           self.agent_sprite.rect.x == tc * config.TILE_SIZE and self.agent_sprite.rect.y == tr * config.TILE_SIZE:
            # place trail + advance
            self.renderer.add_trail(tr, tc, self._step_num)
            self._step_num += 1

            self._path_index += 1
            if self._path_index >= len(self._path):
                raise EndGame()

            self._target = self._path[self._path_index]
            nr, nc = self._target
            self.renderer.path_cost += self.grid.get(nr, nc).cost

        # move 1px towards current target cell
        tr, tc = self._target
        self.agent_sprite.move_towards_cell(tr, tc)

        # update logical row/col when we snap to cell boundary
        if self.agent_sprite.rect.x % config.TILE_SIZE == 0 and self.agent_sprite.rect.y % config.TILE_SIZE == 0:
            self.agent_sprite.row = self.agent_sprite.rect.y // config.TILE_SIZE
            self.agent_sprite.col = self.agent_sprite.rect.x // config.TILE_SIZE

    def finish(self) -> None:
        self.game_over = True
        self.playing = False
        self.renderer.game_over = True

        # redraw trails perfectly from path (deterministic end-state)
        self.renderer.clear_trails()
        for i, (r, c) in enumerate(self._path, start=1):
            self.renderer.add_trail(r, c, i)
        gr, gc = self._path[-1]
        self.agent_sprite.place_to(gr, gc)

        self.renderer.path_cost = self.path_cost(self._path)

    def draw(self) -> None:
        self.screen.fill(config.BLACK)
        self.renderer.draw()

    def quit(self) -> None:
        self.running = False

    def events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.quit()

            if self.game_over:
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.playing = not self.playing
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                raise EndGame()

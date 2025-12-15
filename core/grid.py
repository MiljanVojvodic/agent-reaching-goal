from __future__ import annotations
from dataclasses import dataclass
from core.tiles import Tile


@dataclass(slots=True)
class Grid:
    tiles: list[list[Tile]]
    rows: int = 0
    cols: int = 0

    def __post_init__(self) -> None:
        if not self.tiles or not self.tiles[0]:
            raise ValueError("Grid cannot be empty.")
        self.rows = len(self.tiles)
        self.cols = len(self.tiles[0])

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def get(self, r: int, c: int) -> Tile:
        return self.tiles[r][c]

    def neighbors4(self, r: int, c: int):
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if self.in_bounds(nr, nc):
                neighbors.append(self.tiles[nr][nc])
        return neighbors

    @staticmethod
    def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

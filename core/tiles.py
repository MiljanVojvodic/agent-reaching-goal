from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Tile:
    row: int
    col: int
    kind: str
    cost: int

    @property
    def pos(self) -> tuple[int, int]:
        return (self.row, self.col)


# Costs and kinds (keep same semantics as your original)
TILE_DEFS: dict[str, tuple[str, int]] = {
    "r": ("road.png", 2),
    "g": ("grass.png", 3),
    "s": ("snow.png", 5),
    "d": ("dune.png", 7),
    "m": ("mud.png", 21),
    "w": ("water.png", 101),
}

DEFAULT_KIND = "g"


def tile_image(kind: str) -> str:
    return TILE_DEFS.get(kind, TILE_DEFS[DEFAULT_KIND])[0]


def tile_cost(kind: str) -> int:
    return TILE_DEFS.get(kind, TILE_DEFS[DEFAULT_KIND])[1]

from __future__ import annotations
from dataclasses import dataclass
from core.tiles import Tile, tile_cost, DEFAULT_KIND


@dataclass(frozen=True, slots=True)
class LoadedMap:
    char_map: list[list[str]]
    start: tuple[int, int]
    goal: tuple[int, int]
    tile_map: list[list[Tile]]


def load_map(path: str) -> LoadedMap:
    with open(path, "r", encoding="utf-8") as f:
        sr, sc = [int(x) for x in f.readline().strip().split(",")]
        gr, gc = [int(x) for x in f.readline().strip().split(",")]

        matrix: list[list[str]] = []
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                break
            matrix.append([c for c in line])

    if not matrix:
        raise ValueError("Map file has no matrix data.")

    # build tile objects
    tiles: list[list[Tile]] = []
    for r, row in enumerate(matrix):
        tile_row: list[Tile] = []
        for c, ch in enumerate(row):
            kind = ch if ch else DEFAULT_KIND
            tile_row.append(Tile(r, c, kind, tile_cost(kind)))
        tiles.append(tile_row)

    return LoadedMap(
        char_map=matrix,
        start=(sr, sc),
        goal=(gr, gc),
        tile_map=tiles
    )

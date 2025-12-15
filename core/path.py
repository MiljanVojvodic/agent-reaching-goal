from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class Path:
    nodes: list[tuple[int, int]]  # list of (row, col)

    def __iter__(self) -> Iterable[tuple[int, int]]:
        return iter(self.nodes)

    def __len__(self) -> int:
        return len(self.nodes)

    def validate_adjacent_4(self, rows: int, cols: int) -> None:
        if not self.nodes:
            raise ValueError("Empty path.")
        for (r, c) in self.nodes:
            if not (0 <= r < rows and 0 <= c < cols):
                raise ValueError(f"Out of bounds node: {(r, c)}")
        for i in range(1, len(self.nodes)):
            r1, c1 = self.nodes[i-1]
            r2, c2 = self.nodes[i]
            if abs(r1 - r2) + abs(c1 - c2) != 1:
                raise ValueError(f"Non-adjacent moves: {(r1, c1)} -> {(r2, c2)}")

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

from core.grid import Grid
from core.path import Path


@dataclass(slots=True)
class Agent:
    name: str

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        raise NotImplementedError


class ExampleAgent(Agent):

    def __init__(self):
        super().__init__("Example")

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        nodes = [start]
        while nodes[-1] != goal:
            r, c = nodes[-1]
            neighbors = grid.neighbors4(r, c)

            min_dist = min(grid.manhattan(t.pos, goal) for t in neighbors)
            best_tiles = [
                tile for tile in neighbors
                if grid.manhattan(tile.pos, goal) == min_dist
            ]
            best_tile = best_tiles[random.randint(0, len(best_tiles) - 1)]

            nodes.append(best_tile.pos)

        return Path(nodes)


class DFSAgent(Agent):
    def __init__(self):
        super().__init__("DFS")
    
    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        stack = [start]
        visited = {start}
        parent = {start: None}
        
        def sort_neighbors(current_pos, neighbors):
            def get_priority(neighbor_tile):
                cr, cc = current_pos
                nr, nc = neighbor_tile.pos
                
                if nr == cr and nc == cc + 1:
                    direction_priority = 0
                elif nr == cr + 1 and nc == cc:
                    direction_priority = 1
                elif nr == cr and nc == cc - 1:
                    direction_priority = 2
                elif nr == cr - 1 and nc == cc:
                    direction_priority = 3
                else:
                    direction_priority = 999
                
                cost = neighbor_tile.cost
                
                return (cost, direction_priority)
            
            return sorted(neighbors, key=get_priority)
        
        while stack:
            current = stack[-1]
            
            if current == goal:
                path_nodes = []
                node = goal
                while node is not None:
                    path_nodes.append(node)
                    node = parent[node]
                path_nodes.reverse()
                return Path(path_nodes)
            
            r, c = current
            neighbors = grid.neighbors4(r, c)
            
            sorted_neighbors = sort_neighbors(current, neighbors)
            
            found_unvisited = False
            for neighbor_tile in sorted_neighbors:
                neighbor_pos = neighbor_tile.pos
                if neighbor_pos not in visited:
                    visited.add(neighbor_pos)
                    stack.append(neighbor_pos)
                    parent[neighbor_pos] = current
                    found_unvisited = True
                    break
            
            if not found_unvisited:
                stack.pop()
        
        return Path(stack)
    
import heapq

class BranchAndBoundAgent(Agent):
    def __init__(self):
        super().__init__("BranchAndBound")
    
    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        counter = 0
        pq = [(0, counter, start, [start])]
        counter += 1
        
        best_cost = {start: 0}
        
        best_solution = None
        best_solution_cost = float('inf')
        
        while pq:
            current_cost, _, current_pos, path = heapq.heappop(pq)
            
            if current_cost >= best_solution_cost:
                continue
            
            if current_pos == goal:
                if current_cost < best_solution_cost:
                    best_solution_cost = current_cost
                    best_solution = path
                continue
            
            r, c = current_pos
            neighbors = grid.neighbors4(r, c)
            
            sorted_neighbors = self._sort_neighbors(current_pos, neighbors)
            
            for neighbor_tile in sorted_neighbors:
                neighbor_pos = neighbor_tile.pos
                new_cost = current_cost + neighbor_tile.cost
                
                if neighbor_pos not in best_cost or new_cost < best_cost[neighbor_pos]:
                    if new_cost < best_solution_cost:
                        best_cost[neighbor_pos] = new_cost
                        new_path = path + [neighbor_pos]
                        heapq.heappush(pq, (new_cost, counter, neighbor_pos, new_path))
                        counter += 1
        
        if best_solution:
            return Path(best_solution)
        else:
            return Path([start])
    
    def _sort_neighbors(self, current_pos, neighbors):
        """Sortira susede po ceni, pa po pravcu (Istok, Jug, Zapad, Sever)"""
        def get_priority(neighbor_tile):
            cr, cc = current_pos
            nr, nc = neighbor_tile.pos
            
            if nr == cr and nc == cc + 1:
                direction_priority = 0
            elif nr == cr + 1 and nc == cc:
                direction_priority = 1
            elif nr == cr and nc == cc - 1:
                direction_priority = 2
            elif nr == cr - 1 and nc == cc:
                direction_priority = 3
            else:
                direction_priority = 999
            
            cost = neighbor_tile.cost
            return (cost, direction_priority)
        
        return sorted(neighbors, key=get_priority)


class AStar(Agent):

    def __init__(self):
        super().__init__("AStar")

    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        raise NotImplementedError


AGENTS: dict[str, Callable[[], Agent]] = {
    "Example": ExampleAgent,
    "DFS": DFSAgent,
    "BranchAndBound": BranchAndBoundAgent,
    "AStar": AStar
}


def create_agent(name: str) -> Agent:
    if name not in AGENTS:
        raise ValueError(f"Unknown agent '{name}'. Available: {', '.join(AGENTS.keys())}")
    return AGENTS[name]()

from __future__ import annotations

import random
import heapq
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
        
        return Path([start])

class BranchAndBoundAgent(Agent):
    def __init__(self):
        super().__init__("BranchAndBound")
    
    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        counter = 0
        pq = [(0, 1, counter, start, [start])]
        counter += 1
        
        best_cost = {start: 0}
        best_solution = None
        best_solution_cost = float('inf')
        
        while pq:
            current_cost, num_nodes, _, current_pos, path = heapq.heappop(pq)
            
            if current_cost >= best_solution_cost:
                continue
            
            if current_pos == goal:
                if current_cost < best_solution_cost:
                    best_solution_cost = current_cost
                    best_solution = path
                continue
            
            r, c = current_pos
            neighbors = grid.neighbors4(r, c)
            
            for neighbor_tile in neighbors:
                neighbor_pos = neighbor_tile.pos
                new_cost = current_cost + neighbor_tile.cost
                
                if neighbor_pos not in best_cost or new_cost < best_cost[neighbor_pos]:
                    if new_cost < best_solution_cost:
                        best_cost[neighbor_pos] = new_cost
                        new_path = path + [neighbor_pos]
                        new_num_nodes = len(new_path)

                        heapq.heappush(pq, (new_cost, new_num_nodes, counter, neighbor_pos, new_path))
                        counter += 1
        
        if best_solution:
            return Path(best_solution)
        else:
            return Path([start])

class AStar(Agent):
    def __init__(self):
        super().__init__("AStar")
    
    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        counter = 0
        
        def heuristic(pos):
            return grid.manhattan(pos, goal) * 2
        
        g_score = {start: 0}
        
        f_score = {start: heuristic(start)}
        
        pq = [(f_score[start], 1, counter, start)]
        counter += 1
        
        parent = {start: None}
        
        closed_set = set()
        
        while pq:
            current_f, num_nodes, _, current_pos = heapq.heappop(pq)
            
            if current_pos in closed_set:
                continue
            
            closed_set.add(current_pos)
            
            if current_pos == goal:
                path_nodes = []
                node = goal
                while node is not None:
                    path_nodes.append(node)
                    node = parent[node]
                path_nodes.reverse()
                return Path(path_nodes)
            
            r, c = current_pos
            neighbors = grid.neighbors4(r, c)
            
            for neighbor_tile in neighbors:
                neighbor_pos = neighbor_tile.pos
                
                if neighbor_pos in closed_set:
                    continue
                
                tentative_g = g_score[current_pos] + neighbor_tile.cost
                
                if neighbor_pos not in g_score or tentative_g < g_score[neighbor_pos]:
                    parent[neighbor_pos] = current_pos
                    
                    g_score[neighbor_pos] = tentative_g
                    
                    f = tentative_g + heuristic(neighbor_pos)
                    f_score[neighbor_pos] = f
                    
                    new_num_nodes = num_nodes + 1
                    
                    heapq.heappush(pq, (f, new_num_nodes, counter, neighbor_pos))
                    counter += 1
        
        return Path([start])


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

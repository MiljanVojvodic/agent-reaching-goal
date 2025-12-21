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
        
        while stack:
            curr = stack[-1] # uzimamo prvi element
            
            if curr == goal:
                path = []
                node = goal
                while node is not None: # rekonstrukcija putanje
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return Path(path)
            
            r, c = curr # uzimamo trenutni element
            neighbors = grid.neighbors4(r, c) # uzimamo njegove susede

            sorted_neighbors = []
            for tile in neighbors:
                nr, nc = tile.pos

                if nr == r and nc == c + 1: # istok
                    dir_prio = 0
                elif nr == r + 1 and nc == c: # jug
                    dir_prio = 1
                elif nr == r and nc == c - 1: # zapad
                    dir_prio = 2
                elif nr == r - 1 and nc == c: # sever
                    dir_prio = 3
                else:
                    dir_prio = 999

                sorted_neighbors.append((tile.cost, dir_prio, tile))

            sorted_neighbors.sort(key=lambda x: (x[0], x[1]))  # sortiramo susede
            
            moved = False
            for _, _, tile in sorted_neighbors:
                nxt = tile.pos
                if nxt not in visited: # proveravamo da li smo ga vec posetili
                    visited.add(nxt)
                    stack.append(nxt)
                    parent[nxt] = curr
                    moved = True
                    break
            
            if not moved: # backtracking, ako nemamo vise gde da idemo
                stack.pop()
        
        return Path([start])

class BranchAndBoundAgent(Agent):
    def __init__(self):
        super().__init__("BranchAndBound")
    
    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        cnt = 0
        
        pq = [(0, 1, cnt, start, [start])] # cena putanje, broj cvorova na putanji, counter, trenutna pozicija, path
        cnt += 1
        
        best_cost = {start: 0}
        best_path = None
        best_total = float('inf')
        
        while pq:
            cost, _, _, curr, path = heapq.heappop(pq) # heappop uzima element sa najmanjom cenom iz pq po redosledu kako smo naveli u pq
            
            if cost >= best_total: # pruning - ogranicavamo ga da bude brzi
                continue
            
            if curr == goal:
                if cost < best_total:
                    best_total = cost
                    best_path = path
                continue
            
            r, c = curr
            neighbors = grid.neighbors4(r, c)
            
            for tile in neighbors: # grananje
                nxt = tile.pos
                new_cost = cost + tile.cost
                
                if nxt not in best_cost or new_cost < best_cost[nxt]:
                    if new_cost < best_total:
                        best_cost[nxt] = new_cost
                        new_path = path + [nxt]
                        
                        heapq.heappush(
                            pq,
                            (new_cost, len(new_path), cnt, nxt, new_path)
                        )
                        cnt += 1
        
        if best_path:  # gledamo da li smo pronasli putanju do cilja
            return Path(best_path)
        return Path([start])

class AStar(Agent):
    def __init__(self):
        super().__init__("AStar")
    
    def find_path(self, grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> Path:
        cnt = 0
        
        def h(pos):
            return grid.manhattan(pos, goal) * 2  # *2 da heuristika ne precenjuje
        
        g = {start: 0}  # stvarna cena od starta
        f = {start: h(start)}  # g + h
        
        pq = [(f[start], 1, cnt, start)]  
        # procenjena ukupna cena, broj cvorova, counter, pozicija cvora
        cnt += 1
        
        parent = {start: None}
        closed = set()  # obradjeni cvorovi
        
        while pq:
            _, depth, _, curr = heapq.heappop(pq)
            
            if curr in closed:  # obradjujemo putanju do cvora samo jednom
                continue
            
            closed.add(curr)
            
            if curr == goal:
                path = []
                node = goal
                while node is not None:  # rekonstrukcija putanje
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return Path(path)
            
            r, c = curr
            neighbors = grid.neighbors4(r, c)
            
            for tile in neighbors:
                nxt = tile.pos
                
                if nxt in closed:
                    continue
                
                new_g = g[curr] + tile.cost
                
                if nxt not in g or new_g < g[nxt]:
                    parent[nxt] = curr
                    g[nxt] = new_g
                    f[nxt] = new_g + h(nxt)
                    
                    heapq.heappush(
                        pq,
                        (f[nxt], depth + 1, cnt, nxt)
                    )
                    cnt += 1
        
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

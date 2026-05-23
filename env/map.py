# env/map.py

import os
from dataclasses import dataclass

import numpy as np


@dataclass
class MapData:
    map_name: str
    grid: np.ndarray
    agent_pos: tuple
    enemy_pos: tuple
    enemy_path: list
    weapon_pos: tuple
    targets: list
    ice_positions: frozenset
    crate_positions: frozenset


class MapLoader:
    SYMBOLS = {
        'AGENT': 'A',
        'ENEMY': 'E',
        'TARGET': 'T',
        'ICE': 'B',
        'CRATE': 'R',
        'WEAPON': 'W'
    }

    def __init__(self):
        self._map_name = None

    def load(self, map_name):
        self._map_name = map_name
        path = f"env/src/maps/{map_name}.txt"

        if not os.path.exists(path):
            raise FileNotFoundError(path)

        with open(path, "r") as f:
            content = f.read().strip()

        return self._parse(content)

    def _parse(self, content):
        parts = content.split("\n\n")
        grid_lines = [line for line in parts[0].split("\n") if line.strip()]
        path_str = parts[1] if len(parts) > 1 else ""

        grid = np.array([list(row) for row in grid_lines])

        agent_pos = None
        enemy_pos = None
        weapon_pos = None
        targets = []
        ice_positions = []
        crate_positions = []

        rows, cols = grid.shape

        for r in range(rows):
            for c in range(cols):
                cell = grid[r, c]

                if cell == self.SYMBOLS['AGENT']:
                    agent_pos = (r, c)
                elif cell == self.SYMBOLS['ENEMY']:
                    enemy_pos = (r, c)
                elif cell == self.SYMBOLS['TARGET']:
                    targets.append((r, c))
                elif cell == self.SYMBOLS['ICE']:
                    ice_positions.append((r, c))
                elif cell == self.SYMBOLS['CRATE']:
                    crate_positions.append((r, c))
                elif cell == self.SYMBOLS['WEAPON']:
                    weapon_pos = (r, c)

        enemy_path = self._parse_enemy_path(path_str, enemy_pos, grid)

        return MapData(
            map_name=self._map_name,
            grid=grid,
            agent_pos=agent_pos,
            enemy_pos=enemy_pos,
            enemy_path=enemy_path,
            weapon_pos=weapon_pos,
            targets=targets,
            ice_positions=frozenset(ice_positions),
            crate_positions=frozenset(crate_positions)
        )

    def _parse_enemy_path(self, path_str, start_pos, grid):
        if start_pos is None or not path_str:
            return None

        directions = {
            'U': (-1, 0),
            'D': (1, 0),
            'L': (0, -1),
            'R': (0, 1)
        }

        path = [start_pos]
        current = start_pos

        for move in path_str:
            dr, dc = directions[move]
            nr, nc = current[0] + dr, current[1] + dc

            if 0 <= nr < grid.shape[0] and 0 <= nc < grid.shape[1]:
                if grid[nr, nc] != 'R':
                    current = (nr, nc)
                    path.append(current)

        return path

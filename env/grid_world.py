# env/grid_world.py

from env.domain import GameState
from env.game import ScoreCalculator
from env.map import MapLoader
from env.rendering import Renderer


class GridWorld:
    def __init__(self, map_name):
        self.map_data = MapLoader().load(map_name)

        self.initial_state = GameState(
            self.map_data.agent_pos,
            self.map_data.targets,
            0,
            self.map_data.grid.shape,
            self.map_data.enemy_path,
            self.map_data.grid,
            self,
            weapon_pos=self.map_data.weapon_pos,
            has_weapon=False,
            is_enemy_alive=True,
            crate_positions=self.map_data.crate_positions
        )

        self.renderer = Renderer(self.map_data)
        self.scorer = ScoreCalculator(len(self.map_data.targets))

        self.total_cost = 0
        self.expanded_nodes = 0

    def get_icees_positions(self):
        return self.map_data.ice_positions

    def get_crates_positions(self):
        return self.map_data.crate_positions

    def get_original_grid(self):
        return self.map_data.grid

    def get_weapon_pos(self):
        return self.map_data.weapon_pos

    def get_enemy_path(self):
        return self.map_data.enemy_path

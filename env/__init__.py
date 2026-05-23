# env/__init__.py

from env.grid_world import GridWorld
from env.game import GameRunner


_current_game = None


def play(map_name, search_algorithm, delay=500):
    world = GridWorld(map_name)
    game_runner = GameRunner(world, delay=delay)

    return game_runner.run(search_algorithm)
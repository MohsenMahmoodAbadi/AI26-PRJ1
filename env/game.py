# env/game.py

import time

import pygame

from env.instrumentation import CallCounter, CountingGameState
from env.rendering import Renderer
from env.constants import *


class GameRunner:
    def __init__(self, grid_world, delay=500):
        self.grid_world = grid_world
        self.delay = delay

        self.renderer = Renderer(grid_world.map_data)
        self.scorer = ScoreCalculator(
            len(grid_world.map_data.targets)
        )

        self.total_cost = 0
        self.expanded_nodes = 0
        self.action_delay = delay

    def _run_search(self, algorithm):
        start = time.time()

        counted_state = CountingGameState(
            self.grid_world.initial_state,
            CallCounter()
        )

        actions = algorithm(counted_state)

        self.expanded_nodes = counted_state.get_expanded_nodes()

        print(f"Map Name: {self.grid_world.map_data.map_name}")
        print(f"Search completed in {time.time() - start: .2f}s")


        return actions

    def _execute_actions(self, actions):
        state = self.grid_world.initial_state
        clock = pygame.time.Clock()

        for action in actions:

            # ✔ ESC FIX (added only this block)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return state
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return state

            state = self._apply_action(state, action)

            self.renderer.draw(state)

            # stable timing
            clock.tick(1000 // self.action_delay)

            if state.is_goal_state() or state.is_collision_state():
                break

        return state

    def _apply_action(self, state, action):
        for act, cost, next_state in state.get_successors(
                toward_walls=True
        ):
            if act == action:
                self.total_cost += cost
                return next_state

        raise ValueError("Invalid action")

    def run(self, search_algorithm):
        self.renderer.initialize()

        actions = self._run_search(search_algorithm)

        final_state = self._execute_actions(actions)

        score = self.scorer.calculate(
            final_state,
            self.total_cost
        )

        self.renderer.show_results(
            score,
            self.expanded_nodes,
            final_state.get_step_count(),
            self.total_cost
        )

        pygame.quit()

        return score


class ScoreCalculator:
    def __init__(self, target_count):
        self.target_count = target_count

    def calculate(self, state, total_cost):
        score = 0

        if state.is_goal_state():
            score += self.target_count * TARGET_REWARD

        if state.is_collision_state():
            score -= ENEMY_COLLISION_PENALTY

        if not state.is_enemy_alive():
            score += ENEMY_KILL_REWARD

        score -= total_cost

        return score

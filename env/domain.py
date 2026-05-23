# env/domain.py

from env.constants import *


class GameState:
    __slots__ = (
        "_agent_pos",
        "_targets",
        "_step",
        "_cycle",
        "_grid_shape",
        "_enemy_path",
        "_original_grid",
        "_weapon_pos",
        "_has_weapon",
        "_enemy_alive",
        "_ice_positions",
        "_crate_positions"
    )

    PASSABLE_TILES = {'T', 'A', 'G', 'R', 'E', 'W'}

    def __init__(
        self,
        agent_position,
        targets,
        step,
        grid_shape,
        enemy_path,
        original_grid,
        ice_positions,
        crate_positions,
        weapon_pos=None,
        has_weapon=False,
        is_enemy_alive=True
    ):
        self._agent_pos = agent_position
        self._targets = frozenset(targets)
        self._step = step
        self._grid_shape = grid_shape
        self._enemy_path = enemy_path
        self._original_grid = original_grid

        self._weapon_pos = weapon_pos
        self._has_weapon = has_weapon
        self._enemy_alive = is_enemy_alive

        self._ice_positions = ice_positions
        self._crate_positions = crate_positions

        self._cycle = (
            step % len(enemy_path)
            if enemy_path else None
        )

    # -------------------
    # Hash / Equality
    # -------------------
    def __hash__(self):
        return hash((
            self._agent_pos,
            self._targets,
            self._cycle,
            self._has_weapon,
            self._enemy_alive
        ))

    def __eq__(self, other):
        return (
            self._agent_pos == other._agent_pos
            and self._targets == other._targets
            and self._cycle == other._cycle
            and self._has_weapon == other._has_weapon
            and self._enemy_alive == other._enemy_alive
        )

    # -------------------
    # Getters
    # -------------------
    def get_agent_position(self):
        return self._agent_pos

    def get_targets_positions(self):
        return self._targets

    def get_step_count(self):
        return self._step

    def has_weapon(self):
        return self._has_weapon

    def is_enemy_alive(self):
        return self._enemy_alive

    def get_weapon_position(self):
        return self._weapon_pos

    def get_grid_size(self):
        return self._grid_shape

    def get_enemy_cycle(self):
        return self._cycle

    def action_to_position(self, action):
        dr, dc = DIRECTIONS[action]
        return (
            self._agent_pos[0] + dr,
            self._agent_pos[1] + dc
        )

    def get_crates_positions(self):
        return self._crate_positions

    def get_enemy_path(self):
        return self._enemy_path
    # -------------------
    # Enemy logic
    # -------------------
    def get_enemy_position(self):
        if not self._enemy_path:
            return None

        return self._enemy_path[
            self._step % len(self._enemy_path)
        ]

    def get_enemy_previous_position(self):
        if not self._enemy_path or self._step == 0:
            return None

        return self._enemy_path[
            (self._step - 1) % len(self._enemy_path)
        ]

    def get_enemy_next_position(self):
        if not self._enemy_path:
            return None

        return self._enemy_path[
            (self._step + 1) % len(self._enemy_path)
        ]

    def get_enemy_positions(self):
        return (
            self.get_enemy_position(),
            self.get_enemy_previous_position()
        )

    # -------------------
    # Goal / Collision
    # -------------------
    def is_goal_state(self):
        return (
            len(self._targets) == 0
            and not self.is_collision_state()
        )

    def is_collision_state(self):
        if not self._enemy_alive or not self._enemy_path:
            return False

        enemy_pos, enemy_prev_pos = self.get_enemy_positions()

        overlap = (
            self._agent_pos == enemy_pos
            or self._agent_pos == enemy_prev_pos
        )

        if overlap and self._has_weapon:
            return False

        return overlap

    # -------------------
    # Terrain cost
    # -------------------
    def get_terrain_cost(self, position):
        r, c = position

        if (
            r < 0 or r >= self._grid_shape[0]
            or c < 0 or c >= self._grid_shape[1]
        ):
            return SNOW_PASSING_COST

        cell = self._original_grid[r, c]

        if cell in self.PASSABLE_TILES:
            return SNOW_PASSING_COST

        if cell == 'B':
            return ICE_PASSING_COST

        return SNOW_PASSING_COST

    # -------------------
    # Successor generation
    # -------------------
    def get_successors(self, toward_walls=False):
        successors = []

        for action in DIRECTIONS:
            new_pos = self._compute_new_position(
                action,
                toward_walls
            )

            if new_pos is None:
                continue

            new_state = self._build_next_state(new_pos)
            cost = self._compute_transition_cost(
                new_pos,
                new_state
            )

            successors.append(
                (action, cost, new_state)
            )

        return successors

    def _compute_new_position(
        self,
        action,
        toward_walls
    ):
        dr, dc = DIRECTIONS[action]

        new_r = self._agent_pos[0] + dr
        new_c = self._agent_pos[1] + dc

        in_bounds = (
            0 <= new_r < self._grid_shape[0]
            and 0 <= new_c < self._grid_shape[1]
        )

        if (
            not in_bounds
            or self._original_grid[new_r, new_c] == 'R'
        ):
            return self._agent_pos if toward_walls else None

        return new_r, new_c

    def _build_next_state(self, new_pos):
        new_targets = self._update_targets(new_pos)

        new_has_weapon = (
            self._has_weapon
            or (
                self._weapon_pos
                and new_pos == self._weapon_pos
            )
        )

        new_enemy_alive = self._should_enemy_survive(
            new_pos,
            new_has_weapon
        )

        return GameState(
            agent_position=new_pos,
            targets=new_targets,
            step=self._step + 1,
            grid_shape=self._grid_shape,
            enemy_path=self._enemy_path,
            original_grid=self._original_grid,
            ice_positions=self._ice_positions,
            crate_positions=self._crate_positions,
            weapon_pos=self._weapon_pos,
            has_weapon=new_has_weapon,
            is_enemy_alive=new_enemy_alive
        )

    def _update_targets(self, new_pos):
        if new_pos not in self._targets:
            return self._targets

        updated = set(self._targets)
        updated.remove(new_pos)

        return frozenset(updated)

    def _should_enemy_survive(
        self,
        new_pos,
        has_weapon
    ):
        if (
            not has_weapon
            or not self._enemy_alive
            or not self._enemy_path
        ):
            return self._enemy_alive
        
        next_enemy_pos = self.get_enemy_next_position()
        current_enemy_pos = self.get_enemy_position()

        if new_pos == next_enemy_pos or new_pos == current_enemy_pos:
            return False
        
        return True

    def _compute_transition_cost(
        self,
        new_pos,
        new_state
    ):
        cost = self.get_terrain_cost(new_pos)

        if (
            not new_state.has_weapon()
            and new_state.is_collision_state()
        ):
            cost += ENEMY_COLLISION_PENALTY

        return cost

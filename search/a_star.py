import heapq
from functools import lru_cache

SAFE_DISTANCE = 3
ENEMY_PENALTY = 8
WEAPON_BONUS = 6

def a_star(initial_state):

    targets_count = len(
        initial_state.get_targets_positions()
    )

    use_hierarchical = targets_count > 2

    def manhattan(a, b):
        return (
            abs(a[0] - b[0]) +
            abs(a[1] - b[1])
        )

    def weighted_distance(state, a, b):

        base = manhattan(a, b)

        ice_penalty = 0

        ax, ay = a
        bx, by = b

        x1, x2 = sorted([ax, bx])
        y1, y2 = sorted([ay, by])

        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):

                pos = (x, y)

                try:
                    if state.is_ice_position(pos):
                        ice_penalty += 2
                except:
                    pass

        return base + ice_penalty


    @lru_cache(maxsize=None)
    def mst_cost(targets_tuple):

        targets = list(targets_tuple)

        if len(targets) <= 1:
            return 0

        visited = {targets[0]}
        remaining = set(targets[1:])

        total = 0

        while remaining:

            best_dist = float("inf")
            best_node = None

            for v in visited:
                for r in remaining:

                    d = (
                        abs(v[0] - r[0]) +
                        abs(v[1] - r[1])
                    )

                    if d < best_dist:
                        best_dist = d
                        best_node = r

            total += best_dist

            visited.add(best_node)
            remaining.remove(best_node)

        return total

    @lru_cache(maxsize=None)
    def heuristic_cached(
        agent_pos,
        targets_tuple,
        enemy_alive,
        has_weapon,
        enemy_pos
    ):

        if not targets_tuple:
            return 0

        nearest = min(
            (
                abs(agent_pos[0] - t[0]) +
                abs(agent_pos[1] - t[1])
            )
            for t in targets_tuple
        )

        mst = mst_cost(targets_tuple)

        h = nearest + mst

        # enemy-aware
        if enemy_alive:

            dist_enemy = (
                abs(agent_pos[0] - enemy_pos[0]) +
                abs(agent_pos[1] - enemy_pos[1])
            )

            if not has_weapon:

                if dist_enemy < SAFE_DISTANCE:

                    h += (
                        SAFE_DISTANCE - dist_enemy
                    ) * ENEMY_PENALTY

            else:
                h -= WEAPON_BONUS

        return max(h, 0)


    def heuristic(state):

        targets = tuple(sorted(
            state.get_targets_positions()
        ))

        if not targets:
            return 0

        targets_count = len(targets)

        agent_pos = state.get_agent_position()

   

        if targets_count <= 2:

            return min(
                (
                    abs(agent_pos[0] - t[0]) +
                    abs(agent_pos[1] - t[1])
                )
                for t in targets
            )


        try:
            enemy_alive = state.is_enemy_alive()
        except:
            enemy_alive = True

        try:
            has_weapon = state.has_weapon()
        except:
            has_weapon = False

        try:
            enemy_pos = state.get_enemy_position()
        except:
            enemy_pos = (-1, -1)

        return heuristic_cached(
            agent_pos,
            targets,
            enemy_alive,
            has_weapon,
            enemy_pos
        )


    def choose_target(state):

        targets = state.get_targets_positions()

        if not targets:
            return None

        best_target = None
        best_score = float("inf")

        for t in targets:

            dist = weighted_distance(
                state,
                state.get_agent_position(),
                t
            )

            risk = 0

            try:

                if (
                    state.is_enemy_alive()
                    and
                    not state.has_weapon()
                ):

                    enemy_pos = (
                        state.get_enemy_position()
                    )

                    d = manhattan(
                        t,
                        enemy_pos
                    )

                    if d < SAFE_DISTANCE:
                        risk += (
                            SAFE_DISTANCE - d
                        ) * ENEMY_PENALTY

            except:
                pass

            score = dist + risk

            if score < best_score:
                best_score = score
                best_target = t

        return best_target

    if not use_hierarchical:

        path, _ = global_a_star(
            initial_state,
            heuristic
        )

        return path

    total_path = []

    current_state = initial_state

    while not current_state.is_goal_state():

        target = choose_target(current_state)

        if target is None:
            break

        path_segment, current_state = local_a_star(
            current_state,
            target,
            heuristic
        )

        if not path_segment:
            return total_path

        total_path.extend(path_segment)

    return total_path



def global_a_star(start_state, heuristic):

    frontier = []

    counter = 0

    heapq.heappush(
        frontier,
        (
            heuristic(start_state),
            0,
            counter,
            start_state,
            []
        )
    )

    best_g = {}

    enemy_cycle_len = 1

    try:
        enemy_cycle_len = len(
            start_state.get_enemy_path()
        )
    except:
        pass

    while frontier:

        f, neg_g, _, state, path = heapq.heappop(frontier)

        g = -neg_g

        if state.is_goal_state():
            return path, state

        if state.is_collision_state():
            continue


        step_phase = (
            len(path) % enemy_cycle_len
        )

        key = (
            state.get_agent_position(),
            tuple(sorted(
                state.get_targets_positions()
            )),
            step_phase
        )


        if key in best_g and best_g[key] <= g:
            continue

        best_g[key] = g


        for action, cost, next_state in (
            state.get_successors()
        ):

            if next_state.is_collision_state():
                continue

            if (
                next_state.get_agent_position()
                ==
                state.get_agent_position()
            ):
                continue

            if len(path) >= 1:

                prev = path[-1]

                reverse_pairs = {
                    ("UP", "DOWN"),
                    ("DOWN", "UP"),
                    ("LEFT", "RIGHT"),
                    ("RIGHT", "LEFT")
                }

                if (prev, action) in reverse_pairs:
                    continue

            if len(path) >= 4:

                recent = path[-4:] + [action]

                if (
                    recent ==
                    ["UP", "RIGHT", "DOWN", "LEFT", "UP"]
                ) or (
                    recent ==
                    ["RIGHT", "DOWN", "LEFT", "UP", "RIGHT"]
                ) or (
                    recent ==
                    ["DOWN", "LEFT", "UP", "RIGHT", "DOWN"]
                ) or (
                    recent ==
                    ["LEFT", "UP", "RIGHT", "DOWN", "LEFT"]
                ):
                    continue

            new_g = g + cost

            h = heuristic(next_state)

            counter += 1

            heapq.heappush(
                frontier,
                (
                    new_g + h,
                    -new_g,
                    counter,
                    next_state,
                    path + [action]
                )
            )

    return [], start_state



def local_a_star(start_state, target, heuristic):

    frontier = []

    counter = 0

    heapq.heappush(
        frontier,
        (
            heuristic(start_state),
            0,
            counter,
            start_state,
            []
        )
    )

    best_g = {}

    enemy_cycle_len = 1

    try:
        enemy_cycle_len = len(
            start_state.get_enemy_path()
        )
    except:
        pass

    while frontier:

        f, neg_g, _, state, path = heapq.heappop(frontier)

        g = -neg_g


        if (
            state.get_agent_position()
            ==
            target
        ):
            return path, state


        if state.is_collision_state():
            continue

        step_phase = (
            len(path) % enemy_cycle_len
        )

        try:
            enemy_alive = (
                state.is_enemy_alive()
            )
        except:
            enemy_alive = True

        try:
            has_weapon = (
                state.has_weapon()
            )
        except:
            has_weapon = False

        key = (
            state.get_agent_position(),
            tuple(sorted(
                state.get_targets_positions()
            )),
            enemy_alive,
            has_weapon,
            step_phase
        )

        if key in best_g and best_g[key] <= g:
            continue

        best_g[key] = g


        for action, cost, next_state in (
            state.get_successors()
        ):

            if next_state.is_collision_state():
                continue

            if (
                next_state.get_agent_position()
                ==
                state.get_agent_position()
            ):
                continue

            if len(path) >= 1:

                prev = path[-1]

                reverse_pairs = {
                    ("UP", "DOWN"),
                    ("DOWN", "UP"),
                    ("LEFT", "RIGHT"),
                    ("RIGHT", "LEFT")
                }

                if (prev, action) in reverse_pairs:
                    continue

            if len(path) >= 4:

                recent = path[-4:] + [action]

                if (
                    recent ==
                    ["UP", "RIGHT", "DOWN", "LEFT", "UP"]
                ) or (
                    recent ==
                    ["RIGHT", "DOWN", "LEFT", "UP", "RIGHT"]
                ) or (
                    recent ==
                    ["DOWN", "LEFT", "UP", "RIGHT", "DOWN"]
                ) or (
                    recent ==
                    ["LEFT", "UP", "RIGHT", "DOWN", "LEFT"]
                ):
                    continue

            new_g = g + cost

            h = heuristic(next_state)

            counter += 1

            heapq.heappush(
                frontier,
                (
                    new_g + h,
                    -new_g,
                    counter,
                    next_state,
                    path + [action]
                )
            )

    return [], start_state
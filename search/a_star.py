import heapq
from functools import lru_cache

SAFE_DISTANCE = 3
ENEMY_PENALTY = 8
WEAPON_BONUS = 6


def a_star(initial_state):
    targets = tuple(sorted(initial_state.get_targets_positions()))
    targets_count = len(targets)

    if targets_count <= 2:
        wa_weight = 2.2      
    elif targets_count <= 5:
        wa_weight = 1.8       
    else:
        wa_weight = 1.6      

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @lru_cache(maxsize=None)
    def mst_cost(targets_tuple):
        targets_list = list(targets_tuple)
        if len(targets_list) <= 1:
            return 0
        visited = {targets_list[0]}
        remaining = set(targets_list[1:])
        total = 0
        while remaining:
            best_dist = float("inf")
            best_node = None
            for v in visited:
                for r in remaining:
                    d = abs(v[0] - r[0]) + abs(v[1] - r[1])
                    if d < best_dist:
                        best_dist = d
                        best_node = r
            total += best_dist
            visited.add(best_node)
            remaining.remove(best_node)
        return total

    def choose_target(state):
        targets_list = state.get_targets_positions()
        if not targets_list:
            return None

        agent_pos = state.get_agent_position()
        enemy_alive = False
        has_weapon = False
        enemy_pos = (-1, -1)
        
        try:
            enemy_alive = state.is_enemy_alive()
        except:
            pass
        try:
            has_weapon = state.has_weapon()
        except:
            pass
        try:
            enemy_pos = state.get_enemy_position()
        except:
            pass

        best_target = None
        best_score = float("inf")

        for t in targets_list:
            dist = manhattan(agent_pos, t)

            risk = 0
            if enemy_alive and not has_weapon:
                d = manhattan(t, enemy_pos)
                if d < SAFE_DISTANCE:
                    risk += (SAFE_DISTANCE - d) * ENEMY_PENALTY

            remaining = tuple(sorted(r for r in targets_list if r != t))
            future = mst_cost(remaining) if remaining else 0

            score = dist + risk + future
            if score < best_score:
                best_score = score
                best_target = t

        return best_target

    total_path = []
    current_state = initial_state

    while not current_state.is_goal_state():
        target = choose_target(current_state)
        if target is None:
            break
        path_segment, current_state = local_a_star(current_state, target, wa_weight)
        if not path_segment:
            successors = current_state.get_successors()
            if successors:
                for succ_data in successors:
                    action, cost, next_state = None, 0, None
                    for item in succ_data:
                        if isinstance(item, (int, float)): cost = item
                        elif isinstance(item, str): action = item
                        else: next_state = item
                    if next_state and not next_state.is_collision_state():
                        total_path.append(action)
                        current_state = next_state
                        break
                else:
                    break
            else:
                break
        else:
            total_path.extend(path_segment)

    return total_path


def local_a_star(start_state, target, weight=1.0):
    frontier = []
    counter = 0
    init_pos = start_state.get_agent_position()
    init_h = abs(init_pos[0] - target[0]) + abs(init_pos[1] - target[1])
    
    heapq.heappush(frontier, (weight * init_h, 0, counter, start_state, []))

    best_g = {}
    visited_positions = {} 
    
    enemy_cycle_len = 1
    try:
        enemy_cycle_len = max(1, len(start_state.get_enemy_path()))
    except:
        pass

    while frontier:
        f, neg_g, _, state, path = heapq.heappop(frontier)
        g = -neg_g

        current_pos = state.get_agent_position()

        if current_pos == target:
            return path, state

        if state.is_collision_state():
            continue

        step_phase = len(path) % enemy_cycle_len
        key = (current_pos, step_phase)
        
        if key in best_g and best_g[key] <= g:
            continue
        best_g[key] = g

        if current_pos in visited_positions and visited_positions[current_pos] + enemy_cycle_len <= g:
            continue
        if current_pos not in visited_positions:
            visited_positions[current_pos] = g

        for successor_data in state.get_successors():
            action, cost, next_state = None, 0, None
            for item in successor_data:
                if isinstance(item, (int, float)):
                    cost = item
                elif isinstance(item, str):
                    action = item
                else:
                    next_state = item

            if next_state is None or next_state.is_collision_state():
                continue

            next_pos = next_state.get_agent_position()

            if next_pos == current_pos:
                continue

            if path:
                prev_action = path[-1]
                if (prev_action == "UP"    and action == "DOWN")  or \
                   (prev_action == "DOWN"  and action == "UP")    or \
                   (prev_action == "LEFT"  and action == "RIGHT") or \
                   (prev_action == "RIGHT" and action == "LEFT"):
                    continue

            new_g = g + cost
            h = abs(next_pos[0] - target[0]) + abs(next_pos[1] - target[1])
            counter += 1
            
            heapq.heappush(
                frontier,
                (new_g + weight * h, -new_g, counter, next_state, path + [action]),
            )

    return [], start_state


def global_a_star(start_state, heuristic, weight=1.0):
    
    frontier = []
    counter = 0
    h0 = heuristic(start_state)
    heapq.heappush(frontier, (weight * h0, 0, counter, start_state, []))
    best_g = {}

    enemy_cycle_len = 1
    try:
        enemy_cycle_len = max(1, len(start_state.get_enemy_path()))
    except:
        pass

    while frontier:
        f, neg_g, _, state, path = heapq.heappop(frontier)
        g = -neg_g

        if state.is_goal_state():
            return path, state

        if state.is_collision_state():
            continue

        step_phase = len(path) % enemy_cycle_len
        try:
            targets_pos = tuple(sorted(state.get_target_positions()))
        except:
            targets_pos = tuple(sorted(state.get_targets_positions()))

        key = (
            state.get_agent_position(),
            targets_pos,
            step_phase,
        )

        if key in best_g and best_g[key] <= g:
            continue
        best_g[key] = g

        for successor_data in state.get_successors():
            action, cost, next_state = None, 0, None
            for item in successor_data:
                if isinstance(item, (int, float)):
                    cost = item
                elif isinstance(item, str):
                    action = item
                else:
                    next_state = item

            if next_state is None or next_state.is_collision_state():
                continue

            current_pos = state.get_agent_position()
            next_pos = next_state.get_agent_position()

            if next_pos == current_pos:
                continue

            if path:
                prev_action = path[-1]
                if (prev_action == "UP"    and action == "DOWN")  or \
                   (prev_action == "DOWN"  and action == "UP")    or \
                   (prev_action == "LEFT"  and action == "RIGHT") or \
                   (prev_action == "RIGHT" and action == "LEFT"):
                    continue

            new_g = g + cost
            h = heuristic(next_state)
            counter += 1
            heapq.heappush(
                frontier,
                (new_g + weight * h, -new_g, counter, next_state, path + [action]),
            )

    return [], start_state
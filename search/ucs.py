import heapq


def ucs(initial_state):
    frontier = []
    counter = 0

    heapq.heappush(frontier, (0, counter, initial_state, []))
    visited = {}
    visited[initial_state] = 0

    while frontier:
        current_cost, _, current_state, actions = heapq.heappop(frontier)

        if current_state.is_goal_state():
            return actions

        if current_cost > visited.get(current_state, float('inf')):
            continue

        for next_action, step_cost, next_state in current_state.get_successors():
            new_cost = current_cost + step_cost

            if next_state not in visited or new_cost < visited[next_state]:
                visited[next_state] = new_cost
                counter += 1
                heapq.heappush(frontier, (new_cost, counter,
                               next_state, actions + [next_action]))

    return []

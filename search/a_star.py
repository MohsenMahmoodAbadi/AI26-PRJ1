import heapq

def a_star(initial_state):
    def heuristic(state):
        agent_pos = state.get_agent_position()
        targets = state.get_target_positions()
        
        if not targets:
            return 0
        max_dist = 0
        for target in targets:
            dist = abs(agent_pos[0] - target[0]) + abs(agent_pos[1] - target[1])
            if dist > max_dist:
                max_dist = dist
                
        return max_dist

    frontier = []
    counter = 0
    
    g_score = {initial_state: 0}
    f_score = g_score[initial_state] + heuristic(initial_state)
    
    heapq.heappush(frontier, (f_score, counter, g_score[initial_state], initial_state, []))
    closed_set = set()
    
    while frontier:
        _, _, current_g, current_state, actions = heapq.heappop(frontier)
        
        if current_state.is_goal_state():
            return actions
            
        if current_state in closed_set:
            continue
            
        closed_set.add(current_state)
        
        for next_action, step_cost, next_state in current_state.get_successors():
            tentative_g = current_g + step_cost
            
            if next_state not in g_score or tentative_g < g_score[next_state]:
                g_score[next_state] = tentative_g
                next_f = tentative_g + heuristic(next_state)
                counter += 1
                heapq.heappush(frontier, (next_f, counter, tentative_g, next_state, actions + [next_action]))
                
    return []
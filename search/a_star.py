import heapq

def a_star(initial_state):
    
    def get_state_key(state):
        agent_pos = state.get_agent_position()
        targets = tuple(sorted(state.get_targets_positions()))
        return (agent_pos, targets)

    def heuristic(state):
        agent_pos = state.get_agent_position()
        targets = state.get_targets_positions()
        
        if not targets:
            return 0
            
        nodes = [agent_pos] + list(targets)
        num_nodes = len(nodes)
        
        mst_weight = 0
        visited_mst = [False] * num_nodes
        min_edge = [float('inf')] * num_nodes
        min_edge[0] = 0
        
        for _ in range(num_nodes):
            u = -1
            for i in range(num_nodes):
                if not visited_mst[i] and (u == -1 or min_edge[i] < min_edge[u]):
                    u = i
            
            mst_weight += min_edge[u]
            visited_mst[u] = True
            
            for v in range(num_nodes):
                if not visited_mst[v]:
                    dist = abs(nodes[u][0] - nodes[v][0]) + abs(nodes[u][1] - nodes[v][1])
                    if dist < min_edge[v]:
                        min_edge[v] = dist
                        
        return mst_weight

    frontier = []
    counter = 0
    
    start_key = get_state_key(initial_state)
    g_score = {start_key: 0}
    f_score = g_score[start_key] + heuristic(initial_state)
    
    heapq.heappush(frontier, (f_score, counter, g_score[start_key], initial_state, []))
    closed_set = set()
    
    while frontier:
        _, _, current_g, current_state, actions = heapq.heappop(frontier)
        
        current_key = get_state_key(current_state)
        
        if current_state.is_goal_state():
            return actions
            
        if current_key in closed_set:
            continue
            
        closed_set.add(current_key)
        
        for next_action, step_cost, next_state in current_state.get_successors():
            next_key = get_state_key(next_state)
            tentative_g = current_g + step_cost
            
            if next_key not in g_score or tentative_g < g_score[next_key]:
                g_score[next_key] = tentative_g
                next_f = tentative_g + heuristic(next_state)
                counter += 1
                heapq.heappush(frontier, (next_f, counter, tentative_g, next_state, actions + [next_action]))
                
    return []
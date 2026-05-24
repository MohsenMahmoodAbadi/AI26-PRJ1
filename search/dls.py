def dls():
    global initial_state 
    
    def depth_limited_search(state, limit, visited_states):
        if state.is_goal_state():
            return []
            
        if limit <= 0:
            return "cutoff"
            
        cutoff_occurred = False
        
        for next_action, cost, next_state in state.get_successors():
            if next_state in visited_states:
                continue
                
            visited_states.add(next_state)
            
            result = depth_limited_search(next_state, limit - 1, visited_states)
            
            visited_states.remove(next_state)
            
            if result == "cutoff":
                cutoff_occurred = True
            elif result is not None:
                return [next_action] + result
                
        return "cutoff" if cutoff_occurred else None

    depth = 0
    while True:
        visited = set([initial_state])
        result = depth_limited_search(initial_state, depth, visited)
        
        if result != "cutoff":
            return result if result is not None else []
            
        depth += 1
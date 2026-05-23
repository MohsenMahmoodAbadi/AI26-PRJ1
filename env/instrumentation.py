# env/instrumentation.py

class CallCounter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

    def get_count(self):
        return self.count


class CountingGameState:
    __slots__ = ('_state', '_counter')

    def __init__(self, state, counter):
        self._state = state
        self._counter = counter

    def get_successors(self, toward_walls=False):
        successors = self._state.get_successors(toward_walls=toward_walls)
        self._counter.increment()

        counted_successors = []
        for action, cost, state in successors:
            counted_state = CountingGameState(state, self._counter)
            counted_successors.append((action, cost, counted_state))
        return counted_successors

    def get_expanded_nodes(self):
        return self._counter.get_count()

    def __getattr__(self, name):
        return getattr(self._state, name)

    def __hash__(self):
        return self._state.__hash__()

    def __eq__(self, other):
        return self._state == other

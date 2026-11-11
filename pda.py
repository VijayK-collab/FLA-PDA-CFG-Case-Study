"""A small pushdown-automaton simulator.

A PDA move is  delta[(state, input_symbol, stack_top)] = {(new_state, push), ...}
  * input_symbol "" means an epsilon move (read nothing)
  * push is the string/tuple that replaces the popped top; its FIRST symbol becomes the new top
  * the machine accepts by FINAL STATE after the whole input is read
A configuration (instantaneous description) is (state, remaining input, stack), written with |- between moves.
"""

from collections import deque


class Result:
    def __init__(self, accepted, explored, trace):
        self.accepted, self.explored, self.trace = accepted, explored, trace


class PDA:
    def __init__(self, name, delta, start, accepts, bottom="Z", prune=True):
        self.name, self.start, self.accepts, self.bottom = name, start, set(accepts), bottom
        self.prune = prune          # drop configurations whose stack is hopelessly tall (see run)
        self.delta = {key: {(p, tuple(push)) for p, push in moves} for key, moves in delta.items()}
        self.states = {start} | self.accepts | {k[0] for k in self.delta} | {p for v in self.delta.values() for p, _ in v}

    # ------------------------------------------------------------------ running
    def run(self, word, max_configs=200000):
        """Breadth-first search over configurations. Returns a Result (accepted, configs explored, trace)."""
        w = list(word)
        n = len(w)
        first = (self.start, 0, (self.bottom,))
        parent, queue = {first: None}, deque([first])
        while queue:
            cfg = queue.popleft()
            q, i, stack = cfg
            if i == n and q in self.accepts:
                return Result(True, len(parent), self._path(parent, cfg, w))
            if not stack or len(parent) > max_configs:
                continue
            top, rest = stack[0], stack[1:]
            options = [("", i)]
            if i < n:
                options.append((w[i], i + 1))
            for sym, ni in options:
                for p, push in self.delta.get((q, sym, top), ()):
                    new_stack = push + rest
                    # every symbol above the bottom marker still needs at least one input symbol
                    if self.prune and len(new_stack) - 1 > n - ni:
                        continue
                    nxt = (p, ni, new_stack)
                    if nxt not in parent:
                        parent[nxt] = cfg
                        queue.append(nxt)
        return Result(False, len(parent), [])

    def accepts_string(self, word):
        return self.run(word).accepted

    # ------------------------------------------------------------------ tracing
    def _path(self, parent, cfg, w):
        path = []
        while cfg is not None:
            path.append(cfg)
            cfg = parent[cfg]
        path.reverse()
        return [self.show(c, w) for c in path]

    @staticmethod
    def show(cfg, w):
        q, i, stack = cfg
        rest = "".join(map(str, w[i:])) if all(len(str(x)) == 1 for x in w) else " ".join(map(str, w[i:]))
        stk = "".join(stack) if all(len(s) == 1 for s in stack) else " ".join(stack)
        return f"({q}, {rest or 'ε'}, {stk or 'ε'})"

    # ------------------------------------------------------------------ determinism
    def is_deterministic(self):
        """A PDA is deterministic if no configuration has two possible moves.
        Returns (True/False, reason)."""
        for (q, sym, top), moves in self.delta.items():
            if len(moves) > 1:
                return False, f"two moves for ({q}, {sym or 'ε'}, {top})"
            if sym == "":
                for (q2, s2, t2) in self.delta:
                    if (q2, t2) == (q, top) and s2 != "":
                        return False, f"epsilon-move competes with reading {s2!r} in ({q}, {top})"
        return True, "no configuration has a choice"

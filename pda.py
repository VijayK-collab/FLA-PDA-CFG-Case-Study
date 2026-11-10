"""Task 3 - nondeterministic PDA simulator + CFG->PDA conversion.
Stack is a tuple with the TOP at index 0.  A transition is
    (state, input_symbol_or_'', stack_top) -> [(new_state, push_tuple), ...]
where push_tuple replaces the popped top (leftmost symbol ends up on top)."""
from collections import deque


class PDA:
    def __init__(self, delta, start, z0, finals, accept_by="final"):
        self.delta, self.start, self.z0 = delta, start, z0
        self.finals, self.accept_by = set(finals), accept_by

    def accepts(self, w, trace=False, prune=None):
        init = (self.start, 0, (self.z0,))
        parent = {init: None}
        queue = deque([init])
        while queue:
            cfg = queue.popleft()
            q, i, st = cfg
            if i == len(w) and self._is_accepting(q, st):
                return (True, self._path(parent, cfg)) if trace else True
            if not st:
                continue
            top, rest = st[0], st[1:]
            moves = [(q2, push, i) for q2, push in self.delta.get((q, "", top), [])]
            if i < len(w):
                moves += [(q2, push, i + 1) for q2, push in self.delta.get((q, w[i], top), [])]
            for q2, push, j in moves:
                nxt = (q2, j, tuple(push) + rest)
                if prune and prune(nxt, w):
                    continue
                if nxt not in parent:
                    parent[nxt] = cfg
                    queue.append(nxt)
        return (False, []) if trace else False

    def _is_accepting(self, q, st):
        return (q in self.finals) if self.accept_by == "final" else (len(st) == 0)

    @staticmethod
    def _path(parent, cfg):
        out = []
        while cfg is not None:
            out.append(cfg)
            cfg = parent[cfg]
        return out[::-1]


def show_trace(w, path):
    lines = []
    for q, i, st in path:
        lines.append(f"({q}, {w[i:] or 'ε'}, {''.join(st) or 'ε'})")
    return "  ⊢  ".join(lines)


# ------------------------------------------------------------------ PDAs
def balanced_parens_dpda():
    """Deterministic PDA for balanced parentheses, accept by final state q0."""
    d = {
        ("q0", "(", "Z0"): [("q1", ("X", "Z0"))],
        ("q1", "(", "X"):  [("q1", ("X", "X"))],
        ("q1", ")", "X"):  [("q1", ())],
        ("q1", "", "Z0"):  [("q0", ("Z0",))],
    }
    return PDA(d, "q0", "Z0", {"q0"})


def palindrome_pda():
    """NPDA for all palindromes over {a,b} (even and odd length), accept by final state q2."""
    d = {}
    for top in ("Z0", "A", "B"):
        d[("q0", "a", top)] = [("q0", ("A", top)), ("q1", (top,))]   # push a  | a is the middle symbol
        d[("q0", "b", top)] = [("q0", ("B", top)), ("q1", (top,))]   # push b  | b is the middle symbol
        d[("q0", "", top)] = [("q1", (top,))]                         # guess: middle reached (even length)
    d[("q1", "a", "A")] = [("q1", ())]
    d[("q1", "b", "B")] = [("q1", ())]
    d[("q1", "", "Z0")] = [("q2", ("Z0",))]
    return PDA(d, "q0", "Z0", {"q2"})


# ------------------------------------------------------------------ CFG -> PDA
def cfg_to_pda(grammar, start):
    """Standard construction: one state; expand non-terminals, match terminals."""
    d = {}
    for A, rhss in grammar.items():
        d[("q", "", A)] = [("q", tuple(r)) for r in rhss]
    terminals = {s for rhss in grammar.values() for r in rhss for s in r if s not in grammar}
    for a in terminals:
        d[("q", a, a)] = [("q", ())]
    d[("q", "", "Z0")] = [("qf", ("Z0",))]
    pda = PDA(d, "q", "Z0", {"qf"})
    pda.start_stack = (start, "Z0")
    return pda


def accepts_cfg_pda(pda, start, w, trace=False):
    """Epsilon-free grammars only: prune configs whose stack holds more symbols than input left."""
    pda.z0 = None  # we seed the stack manually below
    init_stack = (start, "Z0")

    class _Seed(PDA):
        pass

    seeded = PDA(pda.delta, pda.start, "Z0", pda.finals)
    # run with custom initial stack
    from collections import deque as dq
    init = (pda.start, 0, init_stack)
    parent = {init: None}
    queue = dq([init])
    while queue:
        cfg = queue.popleft()
        q, i, st = cfg
        if i == len(w) and q == "qf":
            return (True, PDA._path(parent, cfg)) if trace else True
        if not st:
            continue
        top, rest = st[0], st[1:]
        moves = [(q2, p, i) for q2, p in pda.delta.get((q, "", top), [])]
        if i < len(w):
            moves += [(q2, p, i + 1) for q2, p in pda.delta.get((q, w[i], top), [])]
        for q2, p, j in moves:
            nxt = (q2, j, tuple(p) + rest)
            if len(nxt[2]) - 1 > len(w) - j:      # each stack symbol needs >= 1 input char
                continue
            if nxt not in parent:
                parent[nxt] = cfg
                queue.append(nxt)
    return (False, []) if trace else False

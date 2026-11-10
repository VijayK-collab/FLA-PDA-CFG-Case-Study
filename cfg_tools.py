"""Parse-tree counting and leftmost-derivation enumeration for epsilon-free CFGs.
Used to PROVE ambiguity (more than one leftmost derivation) and to print derivations."""
from functools import lru_cache

# Tokens: i = identifier, + * ( )
AMBIGUOUS = {"E": [("E", "+", "E"), ("E", "*", "E"), ("(", "E", ")"), ("i",)]}
UNAMBIGUOUS = {
    "E": [("E", "+", "T"), ("T",)],
    "T": [("T", "*", "F"), ("F",)],
    "F": [("(", "E", ")"), ("i",)],
}


class CFG:
    def __init__(self, productions, start="E"):
        self.P, self.S = productions, start
        self.nts = set(productions)

    def count_trees(self, w):
        @lru_cache(None)
        def seq(form, i, j):
            if not form:
                return 1 if i == j else 0
            if i >= j:
                return 0
            first, rest = form[0], form[1:]
            if first not in self.nts:
                return seq(rest, i + 1, j) if w[i] == first else 0
            if not rest:
                return sum(seq(p, i, j) for p in self.P[first])
            return sum(sym(first, i, k) * seq(rest, k, j) for k in range(i + 1, j))

        def sym(nt, i, j):
            return sum(seq(p, i, j) for p in self.P[nt])

        return seq((self.S,), 0, len(w)), seq

    def leftmost_derivations(self, w, limit=10):
        _, seq = self.count_trees(w)
        out = []

        def go(form, steps):
            if len(out) >= limit:
                return
            idx = next((k for k, s in enumerate(form) if s in self.nts), None)
            if idx is None:
                if "".join(form) == w:
                    out.append(steps)
                return
            for p in self.P[form[idx]]:
                new = form[:idx] + p + form[idx + 1:]
                if seq(new, 0, len(w)):
                    go(new, steps + [" ".join(new)])

        go((self.S,), [self.S])
        return out


if __name__ == "__main__":
    w = "i+i*i"
    for name, g in (("ambiguous", AMBIGUOUS), ("unambiguous", UNAMBIGUOUS)):
        cfg = CFG(g)
        n, _ = cfg.count_trees(w)
        print(f"{name}: {n} parse tree(s) for {w}")
        for k, d in enumerate(cfg.leftmost_derivations(w), 1):
            print(f"  LMD {k}: " + "  =>  ".join(d))

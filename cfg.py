"""Context-free grammars: parsing, string generation, parse trees, ambiguity counting, CFG -> PDA."""

from itertools import islice
from .pda import PDA

EPS = ("ε", "eps", "epsilon")


class CFG:
    def __init__(self, name, text, start="S"):
        """text: one rule per line, e.g.  'S -> S S | ( S ) | ( )'  (symbols separated by spaces)."""
        self.name, self.start, self.rules = name, start, {}
        for line in text.strip().splitlines():
            left, right = line.split("->")
            for alt in right.split("|"):
                body = tuple(t for t in alt.split() if t not in EPS)
                self.rules.setdefault(left.strip(), []).append(body)
        self.nonterminals = set(self.rules)
        self.terminals = {s for prods in self.rules.values() for p in prods for s in p} - self.nonterminals

    def __str__(self):
        return "\n".join(f"{a} -> " + " | ".join(" ".join(p) or "ε" for p in ps) for a, ps in self.rules.items())

    def has_epsilon_rules(self):
        return any(len(p) == 0 for ps in self.rules.values() for p in ps)

    # ------------------------------------------------------------------ generating strings
    def generate(self, max_len):
        """All strings (tuples of terminals) of length <= max_len that the grammar derives."""
        lang = {a: set() for a in self.rules}
        changed = True
        while changed:
            changed = False
            for a, prods in self.rules.items():
                for prod in prods:
                    cur = {()}
                    for sym in prod:
                        nxt = set()
                        for c in cur:
                            if sym in self.nonterminals:
                                nxt.update(c + t for t in lang[sym] if len(c) + len(t) <= max_len)
                            elif len(c) < max_len:
                                nxt.add(c + (sym,))
                        cur = nxt
                    new = cur - lang[a]
                    if new:
                        lang[a] |= new
                        changed = True
        return lang[self.start]

    # ------------------------------------------------------------------ counting parse trees
    def count_trees(self, word):
        """Number of different parse trees of word (a string of single-char tokens or a list of tokens)."""
        toks, memo, active = list(word), {}, set()

        def sym_count(sym, i, j):
            if sym not in self.nonterminals:
                return 1 if j == i + 1 and toks[i] == sym else 0
            key = (sym, i, j)
            if key in memo:
                return memo[key]
            if key in active:                       # a cycle that derives nothing new
                return 0
            active.add(key)
            total = sum(seq_count(p, 0, i, j) for p in self.rules[sym])
            active.discard(key)
            memo[key] = total
            return total

        def seq_count(prod, k, i, j):
            if k == len(prod):
                return 1 if i == j else 0
            first = prod[k]
            if first not in self.nonterminals:
                return seq_count(prod, k + 1, i + 1, j) if i < j and toks[i] == first else 0
            return sum(sym_count(first, i, m) * seq_count(prod, k + 1, m, j) for m in range(i, j + 1))

        return sym_count(self.start, 0, len(toks))

    def accepts_string(self, word):
        return self.count_trees(word) > 0

    # ------------------------------------------------------------------ building parse trees
    def parse_trees(self, word, limit=5):
        """Up to `limit` parse trees. A tree is (nonterminal, [children]); a leaf child is a terminal string."""
        toks = list(word)
        active = set()

        def sym_trees(sym, i, j):
            if sym not in self.nonterminals:
                if j == i + 1 and toks[i] == sym:
                    yield sym
                return
            key = (sym, i, j)
            if key in active:
                return
            active.add(key)
            for prod in self.rules[sym]:
                for kids in seq_trees(prod, 0, i, j):
                    yield (sym, kids)
            active.discard(key)

        def seq_trees(prod, k, i, j):
            if k == len(prod):
                if i == j:
                    yield []
                return
            first = prod[k]
            if first not in self.nonterminals:
                if i < j and toks[i] == first:
                    for rest in seq_trees(prod, k + 1, i + 1, j):
                        yield [first] + rest
                return
            for m in range(i, j + 1):
                for t in sym_trees(first, i, m):
                    for rest in seq_trees(prod, k + 1, m, j):
                        yield [t] + rest

        return list(islice(sym_trees(self.start, 0, len(toks)), limit))

    # ------------------------------------------------------------------ CFG -> PDA
    def to_pda(self):
        """Standard construction: expand a non-terminal on top of the stack, or match a terminal with the input."""
        delta = {("q0", "", "Z"): {("q1", (self.start, "Z"))},
                 ("q1", "", "Z"): {("qf", ("Z",))}}
        for a, prods in self.rules.items():
            delta[("q1", "", a)] = {("q1", tuple(p)) for p in prods}
        for t in self.terminals:
            delta[("q1", t, t)] = {("q1", ())}
        return PDA(f"PDA({self.name})", delta, "q0", {"qf"}, prune=not self.has_epsilon_rules())


# ---------------------------------------------------------------------- helpers for trees
def tree_text(tree, indent=0):
    """Indented text drawing of a parse tree."""
    pad = "  " * indent
    if isinstance(tree, str):
        return f"{pad}{tree}"
    sym, kids = tree
    lines = [f"{pad}{sym}"]
    lines += [tree_text(k, indent + 1) for k in kids]
    return "\n".join(lines)


def tree_value(tree, ids):
    """Evaluate an expression parse tree; `ids` are the numbers for the 'id' leaves, left to right."""
    values = iter(ids)

    def ev(t):
        if isinstance(t, str):
            return next(values) if t == "id" else t
        _, kids = t
        if len(kids) == 1:
            return ev(kids[0])
        if len(kids) == 3 and kids[0] == "(":
            return ev(kids[1])
        left, op, right = ev(kids[0]), kids[1], ev(kids[2])
        return left + right if op == "+" else left * right

    return ev(tree)

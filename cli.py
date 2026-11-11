"""Command-line demo.

    python -m pda_cfg.cli                          accept/reject tables for the three case studies
    python -m pda_cfg.cli trace brackets "{[()]}"  stack trace of one string
    python -m pda_cfg.cli trace marked abcba       (names: brackets | marked | even | expr)
    python -m pda_cfg.cli trees "id+id*id"         every parse tree in the ambiguous expression grammar, with values
    python -m pda_cfg.cli ambiguity                count parse trees of every short string
    python -m pda_cfg.cli determinism              which machines are deterministic
"""

import sys
from .cfg import tree_text, tree_value
from .machines import (BRACKETS_AMBIGUOUS, BRACKETS_FIXED, EXPR_AMBIGUOUS, EXPR_FIXED, PALINDROMES,
                       balanced_reference, bracket_dpda, palindrome_even_npda, palindrome_marked_dpda,
                       tokenize)
from .parsers import parse_expression

BRACKET_TESTS = (["()", "[]{}", "([]{})", "{[()]}", "(((())))", "()[]{}([])"],
                 ["(", ")(", "([)]", "(()", "{]}", "())(()", ""])
EXPR_TESTS = (["id", "id+id*id", "(id+id)*id", "id*(id+id)*id", "((id))", "id+id+id"],
              ["", "id+", "+id", "id id", "(id+id", "id*)id(", "id+*id"])
MARKED_TESTS = (["c", "aca", "abcba", "abbcbba", "babcbab"], ["", "ab", "abcab", "abcb", "acca", "abcbaa"])
EVEN_TESTS = (["", "aa", "abba", "baab", "abbbba"], ["a", "ab", "aba", "abab", "aabb", "abbaa"])


def mark(ok):
    return "ACCEPT" if ok else "REJECT"


def table(title, rows):
    print(f"\n=== {title} ===")
    print(f"  {'string':<18}{'PDA':<9}{'CFG':<9}")
    for text, pda_ok, cfg_ok in rows:
        print(f"  {text or 'ε':<18}{mark(pda_ok):<9}{mark(cfg_ok) if cfg_ok is not None else '-':<9}")


def show_tables():
    dpda = bracket_dpda()
    rows = []
    for s in BRACKET_TESTS[0] + BRACKET_TESTS[1]:
        cfg_ok = BRACKETS_FIXED.accepts_string(s) if s else None      # the bracket grammar has no epsilon rule
        rows.append((s, dpda.accepts_string(s), cfg_ok))
    table("Case study 1: balanced brackets (DPDA vs unambiguous CFG)", rows)

    pda = EXPR_FIXED.to_pda()
    rows = []
    for s in EXPR_TESTS[0] + EXPR_TESTS[1]:
        toks = tokenize(s)
        rows.append((s, pda.accepts_string(toks), EXPR_FIXED.accepts_string(toks)))
    table("Case study 2: arithmetic expressions (PDA built from the CFG)", rows)

    for title, pda, tests in (("Case study 3a: w c w^R (deterministic PDA)", palindrome_marked_dpda(), MARKED_TESTS),
                              ("Case study 3b: w w^R (nondeterministic PDA)", palindrome_even_npda(), EVEN_TESTS)):
        rows = [(s, pda.accepts_string(s), PALINDROMES.accepts_string(s) if title.startswith("Case study 3b") else None)
                for s in tests[0] + tests[1]]
        table(title, rows)


MACHINES = {"brackets": bracket_dpda, "marked": palindrome_marked_dpda,
            "even": palindrome_even_npda, "expr": EXPR_FIXED.to_pda}


def show_trace(name, text):
    if name not in MACHINES:
        sys.exit(f"unknown machine {name!r}; choose from: {', '.join(MACHINES)}")
    pda = MACHINES[name]()
    word = tokenize(text) if name == "expr" else text
    if word is None:
        sys.exit("unknown symbol in the expression (use id + * ( ))")
    result = pda.run(word)
    print(f"{pda.name} on {text!r}")
    if result.accepted:
        print("  " + "\n  |- ".join(result.trace))
    print(f"result: {mark(result.accepted)}   ({result.explored} configurations explored)")


def show_trees(text):
    toks = tokenize(text)
    if toks is None:
        sys.exit("unknown symbol in the expression (use id + * ( ))")
    ids = list(range(2, 2 + toks.count("id")))
    for name, grammar in (("ambiguous grammar", EXPR_AMBIGUOUS), ("precedence grammar", EXPR_FIXED)):
        trees = grammar.parse_trees(toks, limit=10)
        print(f"\n{name}: {len(trees)} parse tree(s) for {text!r}   (id values {ids})")
        for k, t in enumerate(trees, 1):
            print(f"--- tree {k}: value = {tree_value(t, ids)}")
            print(tree_text(t, 1))
    ok, value = parse_expression(toks, ids)
    print(f"\nrecursive-descent parser: {mark(ok)}, value = {value}")


def show_ambiguity(max_len=8):
    print(f"{'grammar':<34}{'strings':>9}{'ambiguous':>11}{'max trees':>11}   example")
    for grammar, n in ((BRACKETS_AMBIGUOUS, max_len), (BRACKETS_FIXED, max_len),
                       (EXPR_AMBIGUOUS, 7), (EXPR_FIXED, 7)):
        words = grammar.generate(n)
        counts = {w: grammar.count_trees(list(w)) for w in words}
        ambiguous = [w for w, c in counts.items() if c > 1]
        best = max(counts, key=counts.get)
        example = f"{''.join(best) if grammar.name.startswith('brackets') else ' '.join(best)} has {counts[best]} trees" \
            if ambiguous else "none"
        print(f"{grammar.name + f' (len<={n})':<34}{len(words):>9}{len(ambiguous):>11}{max(counts.values()):>11}   {example}")
    print("\n(Grammar ambiguity is undecidable in general; this counts trees for every short string, so it is evidence, not a proof.)")


def show_determinism():
    for pda in (bracket_dpda(), palindrome_marked_dpda(), palindrome_even_npda(), EXPR_FIXED.to_pda()):
        ok, why = pda.is_deterministic()
        print(f"{pda.name:<40}{'deterministic' if ok else 'nondeterministic':<18}{why}")


def main(argv):
    if not argv:
        show_tables()
    elif argv[0] == "trace" and len(argv) == 3:
        show_trace(argv[1], argv[2])
    elif argv[0] == "trees" and len(argv) == 2:
        show_trees(argv[1])
    elif argv[0] == "ambiguity":
        show_ambiguity()
    elif argv[0] == "determinism":
        show_determinism()
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])

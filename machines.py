"""The three case studies: balanced brackets, arithmetic expressions, palindromes."""

import re
from .cfg import CFG
from .pda import PDA

OPEN, CLOSE = "([{", ")]}"
PAIR = dict(zip(CLOSE, OPEN))

# ====================================================== case study 1: balanced brackets
def bracket_dpda():
    """Two-state DPDA. q0 = stack holds only Z (accepting), q1 = some opener is waiting."""
    delta = {}
    for o in OPEN:
        delta[("q0", o, "Z")] = {("q1", (o, "Z"))}
        for top in OPEN:
            delta[("q1", o, top)] = {("q1", (o, top))}
    for c in CLOSE:
        delta[("q1", c, PAIR[c])] = {("q1", ())}
    delta[("q1", "", "Z")] = {("q0", ("Z",))}          # everything matched: back to the accepting state
    return PDA("bracket DPDA", delta, "q0", {"q0"})

BRACKETS_AMBIGUOUS = CFG("brackets (ambiguous)", """
S -> S S | ( S ) | [ S ] | { S } | ( ) | [ ] | { }
""")

BRACKETS_FIXED = CFG("brackets (unambiguous)", """
S -> B S | B
B -> ( S ) | [ S ] | { S } | ( ) | [ ] | { }
""")

def balanced_reference(s):
    """Independent check with an ordinary Python list used as a stack."""
    stack = []
    for ch in s:
        if ch in OPEN:
            stack.append(ch)
        elif not stack or stack.pop() != PAIR[ch]:
            return False
    return not stack

# ====================================================== case study 2: arithmetic expressions
EXPR_AMBIGUOUS = CFG("expressions (ambiguous)", "E -> E + E | E * E | ( E ) | id", start="E")

EXPR_FIXED = CFG("expressions (precedence levels)", """
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
""", start="E")

TOKEN = re.compile(r"\s*(id|\+|\*|\(|\))")

def tokenize(text):
    """'id+id*id' -> ['id','+','id','*','id']; returns None if the text has an unknown symbol."""
    text, out, pos = text.strip(), [], 0
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m:
            return None
        out.append(m.group(1))
        pos = m.end()
    return out

# ====================================================== case study 3: palindromes
def palindrome_marked_dpda():
    """w c w^R over {a,b,c}: the marker c tells the machine where the middle is -> deterministic."""
    delta = {}
    for top in ("Z", "a", "b"):
        for x in "ab":
            delta[("q0", x, top)] = {("q0", (x, top))}
        delta[("q0", "c", top)] = {("q1", (top,))}
    for x in "ab":
        delta[("q1", x, x)] = {("q1", ())}
    delta[("q1", "", "Z")] = {("q2", ("Z",))}
    return PDA("w c w^R DPDA", delta, "q0", {"q2"})

def palindrome_even_npda():
    """w w^R over {a,b}: nothing marks the middle, so the machine GUESSES it with an epsilon-move."""
    delta = {}
    for top in ("Z", "a", "b"):
        for x in "ab":
            delta[("q0", x, top)] = {("q0", (x, top))}
        delta[("q0", "", top)] = {("q1", (top,))}      # the guess
    for x in "ab":
        delta[("q1", x, x)] = {("q1", ())}
    delta[("q1", "", "Z")] = {("q2", ("Z",))}
    return PDA("w w^R NPDA", delta, "q0", {"q2"})

PALINDROMES = CFG("palindromes over {a,b}", "S -> a S a | b S b | a | b | ε")

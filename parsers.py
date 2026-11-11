"""A deterministic recursive-descent parser for the expression grammar.

Removing left recursion from  E -> E+T | T,  T -> T*F | F  gives the loop form
    E -> T ( + T )*      T -> F ( * F )*      F -> ( E ) | id
Each function only looks at ONE next token to decide what to do (an LL(1) grammar),
so unlike the CFG -> PDA machine no guessing is needed.
"""


def parse_expression(tokens, ids=None):
    """Return (accepted, value). `ids` are numbers for the 'id' tokens (default 1,2,3,...)."""
    numbers = iter(ids) if ids is not None else iter(range(1, len(tokens) + 2))
    pos = 0

    class Reject(Exception):
        pass

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def eat(tok):
        nonlocal pos
        if peek() != tok:
            raise Reject
        pos += 1

    def E():
        v = T()
        while peek() == "+":
            eat("+")
            v += T()
        return v

    def T():
        v = F()
        while peek() == "*":
            eat("*")
            v *= F()
        return v

    def F():
        if peek() == "(":
            eat("(")
            v = E()
            eat(")")
            return v
        eat("id")
        return next(numbers)

    try:
        value = E()
        if pos != len(tokens):
            raise Reject
        return True, value
    except Reject:
        return False, None

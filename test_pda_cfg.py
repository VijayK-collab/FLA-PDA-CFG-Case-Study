import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pda import *
from cfg_tools import *

BAL_OK  = ["", "()", "(())", "()()", "(()())()", "((()))"]
BAL_BAD = [")(", "(()", "())", "(()))(", "(", ")"]
PAL_OK  = ["", "a", "b", "aa", "aba", "abba", "babab", "abbbba"]
PAL_BAD = ["ab", "abb", "abab", "aab", "baaba", "abbaa"]
EXP_OK  = ["i", "i+i", "i*i", "i+i*i", "(i+i)*i", "i*(i+i)", "((i))", "i+i+i"]
EXP_BAD = ["+i", "i+", "ii", "i++i", "(i", "i)", "()", "i*+i"]

def test_all():
    bal, pal = balanced_parens_dpda(), palindrome_pda()
    for s in BAL_OK:  assert bal.accepts(s), s
    for s in BAL_BAD: assert not bal.accepts(s), s
    for s in PAL_OK:  assert pal.accepts(s), s
    for s in PAL_BAD: assert not pal.accepts(s), s
    for g in (AMBIGUOUS, UNAMBIGUOUS):
        p = cfg_to_pda(g, "E")
        for s in EXP_OK:  assert accepts_cfg_pda(p, "E", s), s
        for s in EXP_BAD: assert not accepts_cfg_pda(p, "E", s), s
    assert CFG(AMBIGUOUS).count_trees("i+i*i")[0] == 2
    assert CFG(UNAMBIGUOUS).count_trees("i+i*i")[0] == 1
    assert CFG(AMBIGUOUS).count_trees("i+i+i")[0] == 2   # associativity ambiguity too
    assert CFG(UNAMBIGUOUS).count_trees("i+i+i")[0] == 1

if __name__ == "__main__":
    test_all(); print("Task 3: all test cases passed")

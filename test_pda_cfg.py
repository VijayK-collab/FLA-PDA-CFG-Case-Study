"""Tests for Task 3.  Run:  python3 -m unittest discover -s tests -v

Every machine is compared with an independently written check on many strings, and the two kinds of
description (PDA and CFG) are compared with each other.
"""

import itertools
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pda_cfg.cfg import tree_value
from pda_cfg.machines import (BRACKETS_AMBIGUOUS, BRACKETS_FIXED, EXPR_AMBIGUOUS, EXPR_FIXED, PALINDROMES,
                              balanced_reference, bracket_dpda, palindrome_even_npda, palindrome_marked_dpda,
                              tokenize)
from pda_cfg.parsers import parse_expression


def all_strings(alphabet, max_len):
    for n in range(max_len + 1):
        for tup in itertools.product(alphabet, repeat=n):
            yield list(tup) if isinstance(alphabet, (list, tuple)) else "".join(tup)


class BalancedBrackets(unittest.TestCase):
    def test_dpda_matches_stack_checker_on_every_short_string(self):
        pda = bracket_dpda()
        for s in all_strings("()[]{}", 5):
            self.assertEqual(pda.accepts_string(s), balanced_reference(s), repr(s))

    def test_dpda_is_deterministic(self):
        self.assertTrue(bracket_dpda().is_deterministic()[0])

    def test_unambiguous_grammar_agrees_with_dpda(self):
        pda = bracket_dpda()
        for s in all_strings("()[]{}", 5):
            if s:
                self.assertEqual(BRACKETS_FIXED.accepts_string(s), pda.accepts_string(s), repr(s))

    def test_original_grammar_is_ambiguous_with_catalan_counts(self):
        counts = [BRACKETS_AMBIGUOUS.count_trees("()" * k) for k in range(1, 6)]
        self.assertEqual(counts, [1, 1, 2, 5, 14])          # Catalan numbers: k blocks in a row -> C(k-1) trees

    def test_fixed_grammar_has_one_tree_for_every_short_string(self):
        for w in BRACKETS_FIXED.generate(8):
            self.assertEqual(BRACKETS_FIXED.count_trees(list(w)), 1, "".join(w))


class Expressions(unittest.TestCase):
    def test_tokenizer(self):
        self.assertEqual(tokenize("id+id*(id)"), ["id", "+", "id", "*", "(", "id", ")"])
        self.assertIsNone(tokenize("id+x"))

    def test_cfg_to_pda_agrees_with_recursive_descent_parser(self):
        pda = EXPR_FIXED.to_pda()
        for toks in all_strings(["id", "+", "*", "(", ")"], 4):
            expected = parse_expression(toks)[0]
            self.assertEqual(pda.accepts_string(toks), expected, " ".join(toks))
            self.assertEqual(EXPR_FIXED.accepts_string(toks), expected, " ".join(toks))

    def test_both_grammars_describe_the_same_language(self):
        for toks in all_strings(["id", "+", "*", "(", ")"], 4):
            self.assertEqual(EXPR_AMBIGUOUS.accepts_string(toks), EXPR_FIXED.accepts_string(toks), " ".join(toks))

    def test_ambiguous_grammar_gives_two_different_values(self):
        trees = EXPR_AMBIGUOUS.parse_trees(tokenize("id+id*id"), limit=10)
        self.assertEqual(sorted(tree_value(t, [2, 3, 4]) for t in trees), [14, 20])

    def test_precedence_grammar_has_one_tree_and_correct_value(self):
        trees = EXPR_FIXED.parse_trees(tokenize("id+id*id"), limit=10)
        self.assertEqual([tree_value(t, [2, 3, 4]) for t in trees], [14])
        self.assertEqual(parse_expression(tokenize("id+id*id"), [2, 3, 4]), (True, 14))
        self.assertEqual(parse_expression(tokenize("(id+id)*id"), [2, 3, 4]), (True, 20))

    def test_precedence_grammar_is_unambiguous_on_every_short_string(self):
        for w in EXPR_FIXED.generate(7):
            self.assertEqual(EXPR_FIXED.count_trees(list(w)), 1, " ".join(w))

    def test_cfg_to_pda_is_nondeterministic(self):
        self.assertFalse(EXPR_FIXED.to_pda().is_deterministic()[0])


class Palindromes(unittest.TestCase):
    def test_marked_dpda(self):
        pda = palindrome_marked_dpda()
        for s in all_strings("abc", 6):
            w, _, rest = s.partition("c")
            expected = s.count("c") == 1 and rest == w[::-1]
            self.assertEqual(pda.accepts_string(s), expected, repr(s))
        self.assertTrue(pda.is_deterministic()[0])

    def test_even_npda(self):
        pda = palindrome_even_npda()
        for s in all_strings("ab", 8):
            self.assertEqual(pda.accepts_string(s), s == s[::-1] and len(s) % 2 == 0, repr(s))
        self.assertFalse(pda.is_deterministic()[0])

    def test_palindrome_grammar(self):
        for s in all_strings("ab", 8):
            self.assertEqual(PALINDROMES.accepts_string(s), s == s[::-1], repr(s))
        for w in PALINDROMES.generate(8):
            self.assertEqual(PALINDROMES.count_trees(list(w)), 1, "".join(w))


if __name__ == "__main__":
    unittest.main()

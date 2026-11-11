# Task 3 – Case Study Analysis and Design using PDA and CFG

**Course:** 21CSC301T Formal Language and Automata · CLA-2 · CO2, CO3, CO4
**Student:** Vijay Bharath Simha Kollati (RA2411026050040) · **SDG 9** (Level 2 – Design alignment)

Three case studies are analysed: **(1) balanced brackets, (2) arithmetic expressions, (3) palindromes.**
Notation: a PDA is (Q, Σ, Γ, δ, q₀, Z, F); a move is written ⊢; stacks are written top first; ε is the empty string.
Every claim below can be reproduced with the commands in the README.

**SDG 9 link.** Compilers, IDEs and linters check exactly these structures. A parser is a pushdown automaton, and
a grammar with no ambiguity is what makes a language tool give one meaning to every program.

---

## 0. Why a finite automaton is not enough

All three languages need to remember an unbounded amount of information.
Take balanced brackets and suppose a DFA with p states accepted them. Read s = (ᵖ)ᵖ. While reading the first p symbols
the DFA visits p+1 states, so two of them repeat; the loop between them consists only of "(" symbols.
Going round that loop once more gives a string with more "(" than ")", which the DFA still accepts although it is not
balanced. This is a contradiction, so brackets are not regular. The same argument with s = aᵖ b aᵖ rules out palindromes,
and nested parentheses do the same for expressions. A **stack** gives exactly the last-in, first-out memory that
nesting needs.

---

## 1. Case study: balanced brackets (a syntax checker)

**Language.** Strings over ( ) [ ] { } in which every bracket is closed by its own kind, in the right order.

**First grammar (ambiguous):**
```
S -> S S | ( S ) | [ S ] | { S } | ( ) | [ ] | { }
```
The rule `S -> S S` does not say how a row of blocks is grouped. `()()()` has **2** parse trees and `()()()()` has **5**
(the counts follow the Catalan numbers: k blocks in a row give C(k−1) trees).

**Fixed grammar (unambiguous):**
```
S -> B S | B
B -> ( S ) | [ S ] | { S } | ( ) | [ ] | { }
```
A list of blocks is now built one way only (first block, then the rest), so every string has exactly one tree.

**Pushdown automaton (2 states, deterministic).** q₀ means "nothing is waiting" (stack = Z, accepting);
q₁ means "some opener is waiting".

| Move | Meaning |
|------|---------|
| δ(q₀, opener, Z) = (q₁, opener Z) | first opener |
| δ(q₁, opener, any opener) = (q₁, opener · top) | push |
| δ(q₁, closer, matching opener) = (q₁, ε) | pop only when the kinds match |
| δ(q₁, ε, Z) = (q₀, Z) | everything matched, go back to the accepting state |

Because q₁ never reads input while Z is on top, the ε-move never competes with an input move: the machine is a **DPDA**.

Trace for `{[()]}`  (`python3 -m pda_cfg.cli trace brackets "{[()]}"`):
```
(q0, {[()]}, Z) ⊢ (q1, [()]}, {Z) ⊢ (q1, ()]}, [{Z) ⊢ (q1, )]}, ([{Z) ⊢ (q1, ]}, [{Z) ⊢ (q1, }, {Z) ⊢ (q1, ε, Z) ⊢ (q0, ε, Z)  accept
```
For `([)]` the machine has `)` to read but `[` on top, no move exists, so it rejects.

---

## 2. Case study: arithmetic expressions

**Ambiguous grammar:** `E -> E + E | E * E | ( E ) | id`.
The string `id+id*id` has two parse trees. With id = 2, 3, 4 one tree evaluates 2+(3×4) = **14** and the other
(2+3)×4 = **20**, so the ambiguity is a real bug: a compiler would not know which to choose
(`python3 -m pda_cfg.cli trees "id+id*id"` prints both trees).

**Fixed grammar (precedence levels):**
```
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
```
`*` is now built below `+`, so `id+id*id` has one tree and the value 14.

**CFG → PDA.** The standard construction uses one working state: push the start symbol, then either replace a
non-terminal on top of the stack by one of its right-hand sides, or match a terminal on top with the next input
symbol. This PDA is **nondeterministic** (several rules exist for E, T and F) – the simulator explores 50 configurations
before it accepts `id+id*id`.

**Deterministic alternative.** Removing the left recursion gives `E -> T (+ T)*`, `T -> F (* F)*`,
`F -> ( E ) | id`, an LL(1) grammar: one look-ahead token always decides the next step. `pda_cfg/parsers.py` is a
recursive-descent parser for it, and the tests check that it accepts exactly the same strings as the PDA.

---

## 3. Case study: palindromes

**Grammar:** `S -> a S a | b S b | a | b | ε` generates every palindrome over {a, b} and is unambiguous, because each
step fixes the outer pair of symbols.

| Language | Machine | Why |
|----------|---------|-----|
| w c wᴿ (marked centre) | **deterministic** PDA: push until `c`, then pop and compare | the marker tells the machine where the middle is |
| w wᴿ (no marker) | **nondeterministic** PDA | it must *guess* the middle with an ε-move; the language has no DPDA |

Trace for `abba` on the w wᴿ machine (`python3 -m pda_cfg.cli trace even abba`): the guess is the move from q₀ to q₁
after two symbols have been pushed.
```
(q0, abba, Z) ⊢ (q0, bba, aZ) ⊢ (q0, ba, baZ) ⊢ (q1, ba, baZ) ⊢ (q1, a, aZ) ⊢ (q1, ε, Z) ⊢ (q2, ε, Z)  accept
```

---

## 4. Summary

| Case study | Ambiguous grammar? | Fix | Deterministic machine? |
|------------|--------------------|-----|------------------------|
| Balanced brackets | yes (`S → S S`) | `S → B S \| B` | yes (DPDA) |
| Expressions | yes (`E → E+E \| E*E`) | precedence levels E / T / F | CFG→PDA no; LL(1) parser yes |
| Palindromes | no | – | marked: yes; unmarked: no (no DPDA exists) |

**Ambiguity check.** Whether a grammar is ambiguous is undecidable in general, so the tool counts the parse trees
of every short string it generates (`python3 -m pda_cfg.cli ambiguity`):

| Grammar | Strings checked | Ambiguous | Most trees for one string |
|---------|-----------------|-----------|---------------------------|
| brackets, original (length ≤ 8) | 1290 | 432 | 5 |
| brackets, fixed (length ≤ 8) | 1290 | 0 | 1 |
| expressions, original (length ≤ 7) | 60 | 28 | 5 |
| expressions, fixed (length ≤ 7) | 60 | 0 | 1 |

This is evidence, not a proof: no ambiguity was found in the fixed grammars for strings up to these lengths.

**Limitations.** The bracket checker looks only at the bracket characters, not at strings or comments in a real
program. The expression grammar has only `+` and `*`. The ambiguity check covers short strings only.

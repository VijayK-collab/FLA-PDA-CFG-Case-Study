# Task 3 – Case-Study Analysis and Design using PDA and CFG

**Course:** 21CSC301T Formal Language and Automata | **CO:** CO2, CO3, CO4 | **SDG 9 (Level 2)**
**Student:** _<Name, Reg. No.>_

Case studies: **(1) balanced parentheses, (2) palindrome checker, (3) arithmetic-expression validation.** Notation: PDA = (Q, Σ, Γ, δ, q₀, Z₀, F); stack written **top-first**; ⊢ is one move; ε is the empty string.

**SDG 9 link.** Compilers, IDEs and linters rely on exactly these models (parsers = PDAs); a correct grammar means reliable software infrastructure.

## 0. Why finite automata are insufficient
All three languages need **unbounded counting / matching**.
*Pumping-lemma sketch for balanced parentheses.* Assume a pumping length p. Take s = (ᵖ)ᵖ. Since |xy| ≤ p, y consists only of `(`. Pumping up (xy²z) gives more `(` than `)` – not balanced. Contradiction ⇒ not regular. The same argument with s = aᵖ b aᵖ works for palindromes, and nested parentheses inside expressions make expression syntax non-regular too. A finite state set cannot remember an unbounded depth; a **stack** can.

---
## 1. Case study – Balanced parentheses
**Language.** L₁ = { w ∈ {(, )}\* : every prefix has #( ≥ #), and #( = #) overall }.

**CFG.** `S → ( S ) S | ε`  (unambiguous – every balanced string has exactly one parse tree).

**Leftmost derivation of `(())()`:**
S ⇒ (S)S ⇒ ((S)S)S ⇒ (()S)S ⇒ (())S ⇒ (())(S)S ⇒ (())()S ⇒ (())()

**PDA (deterministic, accept by final state q₀).** Q = {q0, q1}, Γ = {X, Z₀}, F = {q0}.
| δ | meaning |
|---|---------|
| δ(q0, (, Z₀) = (q1, X Z₀) | first `(` |
| δ(q1, (, X) = (q1, X X) | push for every `(` |
| δ(q1, ), X) = (q1, ε) | pop for every `)` |
| δ(q1, ε, Z₀) = (q0, Z₀) | stack back to bottom ⇒ balanced so far, accept if input over |

**Successful run on `(())()` (program output):**
(q0, (())(), Z0) ⊢ (q1, ())(), XZ0) ⊢ (q1, ))(), XXZ0) ⊢ (q1, )(), XZ0) ⊢ (q1, (), Z0) ⊢ (q0, (), Z0) ⊢ (q1, ), XZ0) ⊢ (q1, ε, Z0) ⊢ (q0, ε, Z0) → **ACCEPT**

**Unsuccessful run on `(()`:** after reading all input the machine is in (q1, ε, XZ0): q1 is not final and ε-move needs Z₀ on top ⇒ **REJECT**. For `())` the second `)` finds Z₀ on top in q1 where only the ε-move exists, so the input cannot be consumed ⇒ REJECT.

**Determinism.** DPDA – at most one move in every configuration. Hence L₁ is a **deterministic CFL**.

| Accepted | Rejected |
|----------|----------|
| `` (ε), `()`, `(())`, `()()`, `(()())()`, `((()))` | `)(`, `(()`, `())`, `(()))(`, `(`, `)` |

---
## 2. Case study – Palindrome checker
**Language.** L₂ = { w ∈ {a,b}\* : w = wᴿ }.

**CFG.** `S → a S a | b S b | a | b | ε`  (unambiguous).
Derivation of `abba`: S ⇒ aSa ⇒ abSba ⇒ abba.  Derivation of `aba`: S ⇒ aSa ⇒ aba.
`abab` has **no** derivation: first and last symbol of every non-trivial derived string are equal (a…a or b…b), but `abab` starts with a and ends with b.

**PDA (nondeterministic, accept by final state q2).** Q = {q0,q1,q2}, Γ = {A,B,Z₀}.
* q0 – *push phase*: read `a` ⇒ push A, read `b` ⇒ push B.
* Guess the middle (nondeterministic): ε-move to q1 (even length), or read the centre symbol and move to q1 without pushing (odd length).
* q1 – *match phase*: read `a` with A on top ⇒ pop; read `b` with B on top ⇒ pop.
* δ(q1, ε, Z₀) = (q2, Z₀) ⇒ accept.

**Accepting run on `abba`:** (q0, abba, Z0) ⊢ (q0, bba, AZ0) ⊢ (q0, ba, BAZ0) ⊢ (q1, ba, BAZ0) ⊢ (q1, a, AZ0) ⊢ (q1, ε, Z0) ⊢ (q2, ε, Z0) → ACCEPT
**Accepting run on `aba`:** (q0, aba, Z0) ⊢ (q0, ba, AZ0) ⊢ (q1, a, AZ0) ⊢ (q1, ε, Z0) ⊢ (q2, ε, Z0) → ACCEPT
**Rejected `abab`:** every guess of the middle fails – e.g. after pushing `ab` and guessing the middle, the machine must read `a` with B on top ⇒ no move; other guesses fail similarly ⇒ REJECT.

**Determinism.** The machine must *guess* where the middle is, and **no DPDA** accepts L₂ (without a centre marker). L₂ is a CFL that is **not deterministic** – this is the case that shows NPDA ≠ DPDA.

| Accepted | Rejected |
|----------|----------|
| ε, `a`, `b`, `aa`, `aba`, `abba`, `babab`, `abbbba` | `ab`, `abb`, `abab`, `aab`, `baaba`, `abbaa` |

---
## 3. Case study – Arithmetic-expression validation
Tokens: `i` = identifier/number, `+`, `*`, `(`, `)`.

### 3.1 Naïve grammar G_amb (ambiguous)
`E → E + E | E * E | ( E ) | i`

**Ambiguity proof for `i+i*i` – two different leftmost derivations (program output):**
* LMD 1: E ⇒ E+E ⇒ i+E ⇒ i+E\*E ⇒ i+i\*E ⇒ i+i\*i  → parse i + (i \* i)
* LMD 2: E ⇒ E\*E ⇒ E+E\*E ⇒ i+E\*E ⇒ i+i\*E ⇒ i+i\*i  → parse (i + i) \* i

Two leftmost derivations ⇒ two parse trees ⇒ **ambiguous**. Consequence: a compiler cannot tell whether `*` binds tighter than `+`; `i+i+i` is also ambiguous (associativity: 2 trees).

### 3.2 Revised grammar G (unambiguous, precedence + left-associativity)
```
E → E + T | T        (lowest precedence, left-assoc)
T → T * F | F        (higher precedence, left-assoc)
F → ( E ) | i
```
Unique derivation of `i+i*i` (program output):
E ⇒ E+T ⇒ T+T ⇒ F+T ⇒ i+T ⇒ i+T\*F ⇒ i+F\*F ⇒ i+i\*F ⇒ i+i\*i → exactly **1** parse tree, with `*` binding tighter.

### 3.3 PDA obtained from the CFG (standard construction)
Single state q, stack alphabet = N ∪ Σ ∪ {Z₀}, start stack = E Z₀.
* **Expand:** for every production A → α: δ(q, ε, A) ∋ (q, α)
* **Match:** for every terminal a: δ(q, a, a) = (q, ε)
* **Accept:** δ(q, ε, Z₀) = (qf, Z₀)
This PDA is **nondeterministic** (several productions per non-terminal) and the left-recursive rules `E → E+T` can grow the stack without reading input – the simulator prunes configurations whose stack holds more symbols than the remaining input. Real compilers use an **LR(1) parser**, which is a *deterministic* PDA for this grammar: the language of expressions is a DCFL even though the top-down PDA is not deterministic.

| Accepted | Rejected |
|----------|----------|
| `i`, `i+i`, `i*i`, `i+i*i`, `(i+i)*i`, `i*(i+i)`, `((i))`, `i+i+i` | `+i`, `i+`, `ii`, `i++i`, `(i`, `i)`, `()`, `i*+i` |

Both grammars accept the same set (verified by program for all 16 strings); only G gives a unique structure.

---
## 4. Summary table
| Case | Class | CFG ambiguous? | PDA | Why not FA |
|------|-------|----------------|-----|-----------|
| Balanced `()` | DCFL | No | DPDA | unbounded nesting depth |
| Palindromes | CFL, not DCFL | No | NPDA | must compare to the first half |
| Expressions | DCFL | G_amb **yes**, revised G **no** | NPDA from CFG / LR(1) DPDA | nested parentheses |

## 5. Reproduce
```bash
python3 demo.py            # stack traces + ambiguity demo
python3 test_pda_cfg.py    # all accepted/rejected strings
```

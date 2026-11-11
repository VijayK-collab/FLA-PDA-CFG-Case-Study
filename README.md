# Task 3 – Case Study using PDA and CFG

**Course:** 21CSC301T Formal Language and Automata · CLA-2 · SRM IST Tiruchirappalli · B.Tech AIML, Sem V
**Student:** Vijay Bharath Simha Kollati (RA2411026050040)
**Faculty:** Dr. C. Gunasundari · **SDG 9** (Level 2 – Design alignment)

Pushdown automata (PDAs) and context-free grammars (CFGs) for three case studies. Pure Python 3.8+, no dependencies.
The full write-up is [`docs/CASE_STUDY.md`](docs/CASE_STUDY.md).

| # | Case study | Grammar | Machine |
|---|------------|---------|---------|
| 1 | Balanced brackets `( ) [ ] { }` | ambiguous `S → S S …`, fixed `S → B S \| B` | 2-state DPDA |
| 2 | Arithmetic expressions | ambiguous `E → E+E \| E*E …`, fixed with E / T / F levels | PDA built from the CFG (nondeterministic) + LL(1) recursive-descent parser |
| 3 | Palindromes | `S → aSa \| bSb \| a \| b \| ε` | `w c wᴿ` DPDA and `w wᴿ` nondeterministic PDA |

## Run it

```bash
python3 -m pda_cfg.cli                              # accept/reject tables for every case study
python3 -m pda_cfg.cli trace brackets "{[()]}"      # stack trace (machines: brackets | marked | even | expr)
python3 -m pda_cfg.cli trace expr "id+id*id"
python3 -m pda_cfg.cli trees "id+id*id"             # all parse trees in both grammars, with values
python3 -m pda_cfg.cli ambiguity                    # parse-tree counts for every short string
python3 -m pda_cfg.cli determinism                  # which machines are deterministic
python3 -m unittest discover -s tests -v            # run the tests
```

## How it works

- `pda.py` simulates any PDA by searching over configurations *(state, remaining input, stack)* and can print the
  trace of moves for an accepted string. It also checks whether a machine is deterministic.
- `cfg.py` reads a grammar written as text, generates all short strings, counts parse trees (to detect ambiguity),
  builds the trees themselves, and converts a grammar into a PDA.
- `machines.py` holds the grammars and machines of the three case studies; `parsers.py` has the deterministic
  expression parser.

## Tests

`tests/test_pda_cfg.py` compares every machine with an independent check: a plain stack checker for brackets, Python's
string reversal for palindromes, and the recursive-descent parser for expressions. It also checks that the PDA and the
CFG agree on every short string, that the original grammars are ambiguous (parse-tree counts follow the Catalan
numbers), and that the fixed grammars give exactly one tree per string.

## Layout

```
pda_cfg/pda.py        PDA simulator (configurations, traces, determinism check)
pda_cfg/cfg.py        grammars: generate, count/build parse trees, CFG -> PDA
pda_cfg/machines.py   grammars and machines for the three case studies
pda_cfg/parsers.py    recursive-descent expression parser
pda_cfg/cli.py        command-line demo
tests/                unit tests
docs/CASE_STUDY.md    the case-study report
```

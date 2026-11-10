import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pda import *
from cfg_tools import *

if __name__ == "__main__":
    for name, p, strings in (("Balanced parentheses DPDA", balanced_parens_dpda(), ["(())()", "(()"]),
                             ("Palindrome NPDA", palindrome_pda(), ["abba", "aba", "abab"])):
        print("\n##", name)
        for w in strings:
            ok, path = p.accepts(w, trace=True)
            print(f"  {w!r}: {'ACCEPT' if ok else 'REJECT'}")
            if ok: print("   ", show_trace(w, path))
    print("\n## Ambiguity")
    os.system(f"python3 {os.path.dirname(os.path.abspath(__file__))}/cfg_tools.py")

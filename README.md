<p align="center">
  <img src="assets/logo.png" alt="AUTOMETA LAB logo" width="40"/>
</p>

<h1 align="center">AUTOMETA LAB — DFA / NFA Engines</h1>

<p align="center">
  A Python implementation of Deterministic Finite Automata (DFA) and Nondeterministic Finite Automata (NFA) with full regex-to-automaton compilation, subset construction conversion, and a Streamlit web UI.
</p>

---

## UI Preview

<p align="center">
  <img src="assets/Screenshot 2026-06-09 021228.png" alt="UI Screenshot 1" width="100%"/>
</p>

<p align="center">
  <img src="assets/Screenshot 2026-06-09 021307.png" alt="UI Screenshot 2" width="100%"/>
</p>

<p align="center">
  <img src="assets/Screenshot 2026-06-09 021329.png" alt="UI Screenshot 3" width="100%"/>
</p>

---

## What It Does

1. **Parses a regular expression** into postfix notation using a shunting-yard algorithm.
2. **Builds an NFA** from the postfix expression via Thompson's construction, supporting concatenation (`.`), union (`|`), Kleene star (`*`), one-or-more (`+`), and optional (`?`).
3. **Converts the NFA to a DFA** using the subset construction (powerset) algorithm with ε-closure computation.
4. **Simulates both engines** — run strings directly against the NFA or the minimised DFA.
5. **Generates and tests strings** — auto-enumerates all strings up to a configurable length and classifies each as accepted or rejected.
6. **Displays a transition table** for the constructed DFA.
7. **Streamlit UI** (`app.py`) — branded AUTOMETA LAB interface for interactive simulation.

---

## File Structure

```
DFA-NFA-engines/
├── nfa.py          # NFA state/class, Thompson's construction, regex parser, NFA simulator
├── dfa.py          # DFA state/class, subset construction (NFA→DFA), DFA simulator, transition table printer
├── app.py          # Streamlit web application (UI shell)
├── presets.py      # Preset regex examples
├── tokenizer.py    # Tokenizer utilities
├── utils.py        # Shared helper functions
├── assets/
│   ├── logo.png
│   ├── Screenshot 2026-06-09 021228.png
│   ├── Screenshot 2026-06-09 021307.png
│   └── Screenshot 2026-06-09 021329.png
└── tests/          # Test cases
```

---

## How the Pipeline Works

```
Regex (infix)
     │
     ▼
add_concat()          ← inserts explicit '.' concat operator
     │
     ▼
infix_to_postfix()    ← shunting-yard
     │
     ▼
regex_to_nfa()        ← Thompson's construction
     │
     ▼
nfa_to_dfa()          ← subset construction + ε-closure
     │
     ▼
dfa_accepts() / accepts()   ← simulation
```

---

## Supported Regex Operators

| Operator | Meaning       | Example      |
|----------|---------------|--------------|
| `\|`     | Union / OR    | `a\|b`       |
| `*`      | Kleene star   | `a*`         |
| `+`      | One or more   | `a+`         |
| `?`      | Zero or one   | `a?`         |
| `()`     | Grouping      | `(ab)*`      |
| implicit | Concatenation | `ab` → `a.b` |

> Only alphanumeric characters are treated as symbols. The alphabet is inferred automatically from the regex.

---

## Installation

```bash
git clone https://github.com/Abdullahkhan2809/DFA-NFA-engines.git
cd DFA-NFA-engines
pip install streamlit
```

No other dependencies — the core engines use only Python's standard library (`itertools`, `copy`).

---

## Usage

### Run the NFA engine (CLI)

```bash
python nfa.py
```

```
Enter Regular expression: a(b|c)*
Postfix: abc|*.a.

Accepted: ['ε', 'a', 'ab', 'ac', 'abb', 'abc', 'acb', 'acc', ...]
Rejected: ['b', 'c', 'ba', ...]
```

### Run the DFA engine with transition table (CLI)

```bash
python dfa.py
```

```
Enter Regular Expression: a(b|c)*
Postfix: abc|*.a.

DFA States : 3
Start State : q0
Accept States: q1

--- DFA Transition Table ---
State     a         b         c
--------------------------------------
->q0      q1        ∅         ∅
->*q1     ∅         q1        q1

--- Manual Test ---
Test a string (or 'q' to quit): abc
  'abc' -> ACCEPTED ✓
```

### Run the Streamlit UI

```bash
streamlit run app.py
```

Opens the **AUTOMETA LAB** web interface in your browser.

---

## Key Algorithms

**Thompson's Construction** (`nfa.py`): converts each regex operator into a small NFA fragment using ε-transitions, then composes fragments bottom-up from the postfix stack.

**Subset Construction** (`dfa.py`): treats sets of NFA states as single DFA states. Computes ε-closure for each reachable state set, then transitions via the `move` function for each alphabet symbol. Runs until no new DFA states are discovered.

**ε-closure**: BFS/DFS over epsilon edges to find all NFA states reachable without consuming input.

---

## Limitations

- Only alphanumeric symbols are supported as alphabet characters (no whitespace, special chars, or Unicode in the regex).
- String enumeration is brute-force up to `max_len = 5`; combinatorial explosion occurs for large alphabets or longer lengths.
- The Streamlit UI (`app.py`) is currently a layout shell — full simulation wiring is in progress.
- No DFA minimisation (Hopcroft's algorithm) is implemented; the output DFA may not be the minimal equivalent.

---

## License

This project does not currently include a license file. All rights reserved by the author unless otherwise stated.

import itertools


# ---------- DFA ----------
class DFAState:
    def __init__(self, name):
        self.name = name
        self.transitions = {}   # symbol -> DFAState

class DFA:
    def __init__(self, start, accept_states, states, alphabet):
        self.start = start
        self.accept_states = accept_states  # set of DFAState
        self.states = states                # list of all DFAState
        self.alphabet = alphabet


# ---------- BUILDER: NFA -> DFA (Subset Construction) ----------
def epsilon_closure(nfa_states):
    stack = list(nfa_states)
    closure = set(nfa_states)
    while stack:
        state = stack.pop()
        for s in state.epsilon:
            if s not in closure:
                closure.add(s)
                stack.append(s)
    return frozenset(closure)


def move(nfa_states, symbol):
    result = set()
    for state in nfa_states:
        if symbol in state.edges:
            result.update(state.edges[symbol])
    return result


def nfa_to_dfa(nfa, alphabet):
    start_closure = epsilon_closure([nfa.start])

    # Map: frozenset of NFA states -> DFAState
    state_map = {}
    counter = [0]

    def get_or_create(closure):
        if closure not in state_map:
            name = f"q{counter[0]}"
            counter[0] += 1
            state_map[closure] = DFAState(name)
        return state_map[closure]

    start_dfa = get_or_create(start_closure)

    queue = [start_closure]
    visited = set()

    while queue:
        current_closure = queue.pop(0)
        if current_closure in visited:
            continue
        visited.add(current_closure)

        current_dfa = get_or_create(current_closure)

        for symbol in alphabet:
            next_nfa = move(current_closure, symbol)
            if not next_nfa:
                continue
            next_closure = epsilon_closure(next_nfa)
            next_dfa = get_or_create(next_closure)
            current_dfa.transitions[symbol] = next_dfa

            if next_closure not in visited:
                queue.append(next_closure)

    # Determine accept states
    accept_states = set()
    for closure, dfa_state in state_map.items():
        if nfa.accept in closure:
            accept_states.add(dfa_state)

    all_states = list(state_map.values())

    return DFA(start_dfa, accept_states, all_states, alphabet)


# ---------- SIMULATION ----------
def dfa_accepts(dfa, string):
    current = dfa.start
    for char in string:
        if char not in current.transitions:
            return False
        current = current.transitions[char]
    return current in dfa.accept_states


# ---------- DISPLAY ----------
def print_transition_table(dfa):
    print("\n--- DFA Transition Table ---")

    # Sort states by name for clean output
    states = sorted(dfa.states, key=lambda s: int(s.name[1:]))
    alphabet = sorted(dfa.alphabet)

    # Header
    header = f"{'State':<10}" + "".join(f"{sym:<10}" for sym in alphabet)
    print(header)
    print("-" * len(header))

    for state in states:
        marker = ""
        if state == dfa.start and state in dfa.accept_states:
            marker = "->*"
        elif state == dfa.start:
            marker = "->"
        elif state in dfa.accept_states:
            marker = "*"

        row = f"{marker + state.name:<10}"
        for sym in alphabet:
            target = state.transitions.get(sym, None)
            row += f"{(target.name if target else 'phi'):<10}"
        print(row)


# ---------- STRING GENERATOR ----------
def generate_strings(alphabet, max_len):
    for length in range(max_len + 1):
        for p in itertools.product(alphabet, repeat=length):
            yield ''.join(p)


# ---------- CLI ENTRY POINT ----------
# Only runs when you do `python dfa.py` directly. Importing this file from
# Streamlit never triggers any prompts.
def main():
    from nfa import add_concat, infix_to_postfix, regex_to_nfa

    regex = input("Enter Regular Expression: ").strip()

    # Step 1: Parse regex -> NFA
    regex_concat = add_concat(regex)
    postfix = infix_to_postfix(regex_concat)
    print(f"Postfix: {postfix}")

    nfa = regex_to_nfa(postfix)

    # Step 2: Extract alphabet from regex
    alphabet = sorted(set(c for c in regex if c.isalnum()))

    # Step 3: NFA -> DFA (Subset Construction)
    dfa = nfa_to_dfa(nfa, alphabet)

    print(f"\nDFA States   : {len(dfa.states)}")
    print(f"Start State  : {dfa.start.name}")
    print(f"Accept States: {', '.join(s.name for s in sorted(dfa.accept_states, key=lambda x: x.name))}")

    # Step 4: Print transition table
    print_transition_table(dfa)

    # Step 5: Test strings
    max_len = 5
    accepted = []
    rejected = []

    for s in generate_strings(alphabet, max_len):
        label = s if s else "epsilon"
        if dfa_accepts(dfa, s):
            accepted.append(label)
        else:
            rejected.append(label)

    print("\n--- String Testing Table ---")
    print(f"\nAccepted: {accepted if accepted else 'None'}")
    print(f"Rejected: {rejected if rejected else 'None'}")

    # Step 6: Manual string test
    print("\n--- Manual Test ---")
    while True:
        test = input("Test a string (or 'q' to quit): ").strip()
        if test == 'q':
            break
        result = dfa_accepts(dfa, test)
        print(f"  '{test}' -> {'ACCEPTED' if result else 'REJECTED'}")


if __name__ == "__main__":
    main()
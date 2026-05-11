import itertools  # Used for generating all possible strings from the alphabet


# ---------- DFA ----------
class DFAState:
    def __init__(self, name):
        # Name/label of the DFA state (example: q0, q1, q2)
        self.name = name
        
        # Dictionary to store transitions
        # Format: symbol -> DFAState
        self.transitions = {}


class DFA:
    def __init__(self, start, accept_states, states, alphabet):
        # Starting state of the DFA
        self.start = start
        
        # Set of accepting/final DFA states
        self.accept_states = accept_states
        
        # List of all DFA states
        self.states = states
        
        # Input alphabet used by the DFA
        self.alphabet = alphabet


# ---------- BUILDER: NFA -> DFA (Subset Construction) ----------
def epsilon_closure(nfa_states):
    """
    Finds the epsilon-closure of a set of NFA states.
    
    Epsilon-closure means:
    All states reachable using ONLY epsilon transitions.
    """

    # Stack used for DFS traversal
    stack = list(nfa_states)

    # Closure initially contains the given states
    closure = set(nfa_states)

    # Continue until all reachable epsilon states are explored
    while stack:
        state = stack.pop()

        # Check all epsilon-connected states
        for s in state.epsilon:

            # Add unseen states to closure
            if s not in closure:
                closure.add(s)
                stack.append(s)

    # frozenset is immutable and can be used as dictionary keys
    return frozenset(closure)


def move(nfa_states, symbol):
    """
    Returns all NFA states reachable from the given states
    using the given input symbol.
    """

    result = set()

    # Check transitions from every NFA state
    for state in nfa_states:

        # If transition exists for the symbol
        if symbol in state.edges:

            # Add all reachable states
            result.update(state.edges[symbol])

    return result


def nfa_to_dfa(nfa, alphabet):
    """
    Converts an NFA into a DFA using Subset Construction.
    """

    # Start DFA state = epsilon closure of NFA start state
    start_closure = epsilon_closure([nfa.start])

    # Maps:
    # frozenset of NFA states -> DFAState object
    state_map = {}

    # Counter used for naming DFA states (q0, q1, ...)
    counter = [0]

    def get_or_create(closure):
        """
        Creates a DFA state if this closure does not already exist.
        Otherwise returns the existing DFA state.
        """

        if closure not in state_map:

            # Create new DFA state name
            name = f"q{counter[0]}"
            counter[0] += 1

            # Store DFA state
            state_map[closure] = DFAState(name)

        return state_map[closure]

    # Create DFA start state
    start_dfa = get_or_create(start_closure)

    # Queue for BFS traversal of DFA states
    queue = [start_closure]

    # Keep track of processed closures
    visited = set()

    # Process each DFA state
    while queue:

        # Get next closure
        current_closure = queue.pop(0)

        # Skip if already processed
        if current_closure in visited:
            continue

        visited.add(current_closure)

        # Current DFA state
        current_dfa = get_or_create(current_closure)

        # Try every symbol in alphabet
        for symbol in alphabet:

            # Move using the symbol
            next_nfa = move(current_closure, symbol)

            # Ignore empty transitions
            if not next_nfa:
                continue

            # Compute epsilon closure of result
            next_closure = epsilon_closure(next_nfa)

            # Create/get DFA state for this closure
            next_dfa = get_or_create(next_closure)

            # Add DFA transition
            current_dfa.transitions[symbol] = next_dfa

            # Add unvisited state to queue
            if next_closure not in visited:
                queue.append(next_closure)

    # Determine DFA accept states
    accept_states = set()

    for closure, dfa_state in state_map.items():

        # If NFA accept state exists in closure,
        # corresponding DFA state becomes accepting
        if nfa.accept in closure:
            accept_states.add(dfa_state)

    # List of all DFA states
    all_states = list(state_map.values())

    # Return complete DFA object
    return DFA(start_dfa, accept_states, all_states, alphabet)


# ---------- SIMULATION ----------
def dfa_accepts(dfa, string):
    """
    Simulates the DFA on a given input string.
    
    Returns True if accepted, otherwise False.
    """

    # Start from DFA start state
    current = dfa.start

    # Process each character
    for char in string:

        # Reject if transition doesn't exist
        if char not in current.transitions:
            return False

        # Move to next state
        current = current.transitions[char]

    # Accept if final state is accepting
    return current in dfa.accept_states


# ---------- DISPLAY ----------
def print_transition_table(dfa):
    """
    Prints the DFA transition table in a readable format.
    """

    print("\n--- DFA Transition Table ---")

    # Sort states numerically (q0, q1, q2...)
    states = sorted(dfa.states, key=lambda s: int(s.name[1:]))

    # Sort alphabet symbols
    alphabet = sorted(dfa.alphabet)

    # Create table header
    header = f"{'State':<10}" + "".join(f"{sym:<10}" for sym in alphabet)

    print(header)

    # Print separator line
    print("-" * len(header))

    # Print each DFA state's transitions
    for state in states:

        marker = ""

        # Mark start + accept state
        if state == dfa.start and state in dfa.accept_states:
            marker = "->*"

        # Mark start state
        elif state == dfa.start:
            marker = "->"

        # Mark accept state
        elif state in dfa.accept_states:
            marker = "*"

        # Start row with state name
        row = f"{marker + state.name:<10}"

        # Add transitions for each symbol
        for sym in alphabet:

            target = state.transitions.get(sym, None)

            # Print destination state or phi if no transition
            row += f"{(target.name if target else 'phi'):<10}"

        print(row)


# ---------- STRING GENERATOR ----------
def generate_strings(alphabet, max_len):
    """
    Generates all possible strings from the alphabet
    up to length max_len.
    """

    # Generate strings of length 0 to max_len
    for length in range(max_len + 1):

        # itertools.product creates all combinations
        for p in itertools.product(alphabet, repeat=length):

            # Convert tuple into string
            yield ''.join(p)


# ---------- CLI ENTRY POINT ----------
# Only runs when you execute:
# python dfa.py
#
# Importing this file elsewhere will NOT execute main().
def main():

    # Import regex->NFA helper functions
    from nfa import add_concat, infix_to_postfix, regex_to_nfa

    # Take regex input from user
    regex = input("Enter Regular Expression: ").strip()

    # Step 1: Convert regex into NFA

    # Add explicit concatenation operators
    regex_concat = add_concat(regex)

    # Convert infix regex to postfix notation
    postfix = infix_to_postfix(regex_concat)

    print(f"Postfix: {postfix}")

    # Build NFA from postfix regex
    nfa = regex_to_nfa(postfix)

    # Step 2: Extract alphabet symbols from regex
    alphabet = sorted(set(c for c in regex if c.isalnum()))

    # Step 3: Convert NFA to DFA using subset construction
    dfa = nfa_to_dfa(nfa, alphabet)

    # Display DFA information
    print(f"\nDFA States   : {len(dfa.states)}")
    print(f"Start State  : {dfa.start.name}")

    print(
        f"Accept States: "
        f"{', '.join(s.name for s in sorted(dfa.accept_states, key=lambda x: x.name))}"
    )

    # Step 4: Print DFA transition table
    print_transition_table(dfa)

    # Step 5: Automatically test generated strings

    # Maximum length of generated strings
    max_len = 5

    accepted = []
    rejected = []

    # Generate all strings
    for s in generate_strings(alphabet, max_len):

        # Display epsilon instead of empty string
        label = s if s else "epsilon"

        # Check acceptance
        if dfa_accepts(dfa, s):
            accepted.append(label)
        else:
            rejected.append(label)

    # Print results
    print("\n--- String Testing Table ---")

    print(f"\nAccepted: {accepted if accepted else 'None'}")
    print(f"Rejected: {rejected if rejected else 'None'}")

    # Step 6: Manual string testing
    print("\n--- Manual Test ---")

    while True:

        # User enters a string to test
        test = input("Test a string (or 'q' to quit): ").strip()

        # Exit loop
        if test == 'q':
            break

        # Simulate DFA
        result = dfa_accepts(dfa, test)

        # Print result
        print(f"  '{test}' -> {'ACCEPTED' if result else 'REJECTED'}")


# Program starts here
if __name__ == "__main__":
    main()
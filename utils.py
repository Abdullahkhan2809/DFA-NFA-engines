"""
functions used across the project.
small utilities that support the main NFA/DFA logic without being tied to a specific automaton implementation
"""

import itertools


# STRING GENERATION 
def generate_strings(alphabet, max_len):
    """
    Yield every possible string built from the alphabet, up to max_len characters.

    Example: alphabet = ['a', 'b'], max_len = 2
    Yields: '', 'a', 'b', 'aa', 'ab', 'ba', 'bb'

    'yield' makes this a generator - it produces strings one at a time
    instead of building a huge list in memory all at once.
    """
    for length in range(max_len + 1):
        for combo in itertools.product(alphabet, repeat=length):
            yield ''.join(combo)


# INPUT VALIDATION 
def validate_test_string(string, alphabet):
    """
    Make sure the user's test string only uses characters that the
    automaton actually knows about.

    Returns (True, "") if valid, or (False, error_message) if not.

    Example: alphabet = ['a', 'b'], string = "abc"
    Result: (False, "Character 'c' is not in the alphabet {'a', 'b'}")
    """
    if string == "":
        return (True, "")   # empty string is always a valid test input

    alphabet_set = set(alphabet)
    for ch in string:
        if ch not in alphabet_set:
            return (False, f"Character '{ch}' is not in the alphabet {sorted(alphabet_set)}")
    return (True, "")


# RESULT FORMATTING 
def format_string_for_display(s):
    """
    Show empty strings as the epsilon symbol so they're visible in output.
    """
    return s if s else "ε"


def split_accepted_rejected(automaton, accept_func, alphabet, max_len):
    """
    Run every possible string (up to max_len) through the automaton and
    sort them into two lists: accepted and rejected.

    Parameters:
        automaton    : the NFA or DFA object
        accept_func  : the function that checks acceptance
                       (use 'accepts' from nfa.py or 'dfa_accepts' from dfa.py)
        alphabet     : list of input symbols
        max_len      : largest string length to test

    Returns: (accepted_list, rejected_list)
    """
    accepted = []
    rejected = []

    for s in generate_strings(alphabet, max_len):
        label = format_string_for_display(s)
        if accept_func(automaton, s):
            accepted.append(label)
        else:
            rejected.append(label)

    return accepted, rejected


# DFA EXPORT 
def dfa_to_text(dfa):
    """
    Build a clean text description of the DFA.
    Useful for printing, logging, or saving to a file.
    """
    lines = []
    lines.append("=" * 50)
    lines.append("DFA SUMMARY")
    lines.append("=" * 50)

    states_sorted = sorted(dfa.states, key=lambda s: int(s.name[1:]))
    accept_names = sorted(s.name for s in dfa.accept_states)

    lines.append(f"Total states : {len(dfa.states)}")
    lines.append(f"Alphabet     : {dfa.alphabet}")
    lines.append(f"Start state  : {dfa.start.name}")
    lines.append(f"Accept states: {accept_names}")
    lines.append("")
    lines.append("Transitions:")

    for state in states_sorted:
        for sym in sorted(dfa.alphabet):
            target = state.transitions.get(sym)
            if target:
                lines.append(f"  {state.name} --{sym}--> {target.name}")

    lines.append("=" * 50)
    return "\n".join(lines)


# PRETTY-PRINT RESULTS 
def print_results(accepted, rejected, max_show=20):
    """
    Print the accepted/rejected lists nicely, cutting off long lists.
    """
    print("\n--- Accepted Strings ---")
    if not accepted:
        print("  (none)")
    else:
        shown = accepted[:max_show]
        print(" ", ", ".join(shown))
        if len(accepted) > max_show:
            print(f"  ...and {len(accepted) - max_show} more")

    print("\n--- Rejected Strings ---")
    if not rejected:
        print("  (none)")
    else:
        shown = rejected[:max_show]
        print(" ", ", ".join(shown))
        if len(rejected) > max_show:
            print(f"  ...and {len(rejected) - max_show} more")


if __name__ == "__main__":
    print("Demo: generate_strings(['a','b'], 2)")
    print(list(generate_strings(['a', 'b'], 2)))

    print("\nDemo: validate_test_string('abc', ['a','b'])")
    print(validate_test_string('abc', ['a', 'b']))

    print("\nDemo: validate_test_string('aab', ['a','b'])")
    print(validate_test_string('aab', ['a', 'b']))

    print("\nDemo: format_string_for_display('')")
    print(repr(format_string_for_display('')))
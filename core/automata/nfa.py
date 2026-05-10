import itertools
import copy


# ---------- NFA ----------
class State:
    def __init__(self):
        self.edges = {}
        self.epsilon = []

class NFA:
    def __init__(self, start, accept):
        self.start = start
        self.accept = accept


# ---------- BUILDERS ----------
def symbol_nfa(symbol):
    s0 = State()
    s1 = State()
    s0.edges.setdefault(symbol, []).append(s1)
    return NFA(s0, s1)

def concat_nfa(nfa1, nfa2):
    nfa1.accept.epsilon.append(nfa2.start)
    return NFA(nfa1.start, nfa2.accept)

def union_nfa(nfa1, nfa2):
    start = State()
    accept = State()
    start.epsilon += [nfa1.start, nfa2.start]
    nfa1.accept.epsilon.append(accept)
    nfa2.accept.epsilon.append(accept)
    return NFA(start, accept)

def star_nfa(nfa):
    start = State()
    accept = State()
    start.epsilon += [nfa.start, accept]
    nfa.accept.epsilon += [nfa.start, accept]
    return NFA(start, accept)


# ---------- INFIX -> POSTFIX ----------
def add_concat(regex):
    result = ""
    for i in range(len(regex)):
        c1 = regex[i]
        result += c1

        if i + 1 < len(regex):
            c2 = regex[i + 1]

            if ((c1.isalnum() or c1 in ')*+?') and
                (c2.isalnum() or c2 == '(')):
                result += '.'

    return result


def precedence(op):
    if op in ['*', '+', '?']: return 3
    if op == '.': return 2
    if op == '|': return 1
    return 0


def infix_to_postfix(regex):
    output = []
    stack = []

    for c in regex:
        if c.isalnum():
            output.append(c)

        elif c == '(':
            stack.append(c)

        elif c == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()

        elif c in ['*', '+', '?', '.', '|']:
            while stack and precedence(stack[-1]) >= precedence(c):
                output.append(stack.pop())
            stack.append(c)

    while stack:
        output.append(stack.pop())

    return ''.join(output)


# ---------- REGEX -> NFA ----------
def regex_to_nfa(regex):
    stack = []

    for c in regex:
        if c.isalnum():
            stack.append(symbol_nfa(c))

        elif c == '*':
            stack.append(star_nfa(stack.pop()))

        elif c == '+':
            nfa = stack.pop()
            stack.append(concat_nfa(nfa, star_nfa(copy.deepcopy(nfa))))

        elif c == '?':
            nfa = stack.pop()
            empty_start = State()
            empty_accept = State()
            empty_start.epsilon.append(empty_accept)
            stack.append(union_nfa(nfa, NFA(empty_start, empty_accept)))

        elif c == '|':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(union_nfa(nfa1, nfa2))

        elif c == '.':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(concat_nfa(nfa1, nfa2))

    return stack.pop()


# ---------- SIMULATION ----------
def epsilon_closure(states):
    stack = list(states)
    closure = set(states)

    while stack:
        state = stack.pop()
        for s in state.epsilon:
            if s not in closure:
                closure.add(s)
                stack.append(s)

    return closure

def move(states, symbol):
    result = set()
    for state in states:
        if symbol in state.edges:
            result.update(state.edges[symbol])
    return result

def accepts(nfa, string):
    current = epsilon_closure([nfa.start])

    for char in string:
        current = epsilon_closure(move(current, char))

    return nfa.accept in current


# ---------- STRING GENERATOR ----------
def generate_strings(alphabet, max_len):
    for length in range(max_len + 1):
        for p in itertools.product(alphabet, repeat=length):
            yield ''.join(p)


# ---------- CLI ENTRY POINT ----------
# Guarded behind __main__ so importing this module never triggers input().
# Run `python nfa.py` directly to use the terminal interface.
def _cli():
    regex = input("Enter Regular expression  ")

    regex = add_concat(regex)
    postfix = infix_to_postfix(regex)
    print("Postfix:", postfix)

    nfa = regex_to_nfa(postfix)
    alphabet = sorted(set([c for c in regex if c.isalnum()]))
    max_len = 5

    print("\n--- String Testing Table ---")

    accepted = []
    rejected = []

    for s in generate_strings(alphabet, max_len):
        if accepts(nfa, s):
            accepted.append(s if s else "ε")
        else:
            rejected.append(s if s else "ε")

    print("\nAccepted:", accepted if accepted else "None (try larger max_len)")
    print("Rejected:", rejected if rejected else "None")


if __name__ == "__main__":
    _cli()
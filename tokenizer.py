r"""
Tokenizer for the regex input.
takes a raw regex string from the user and produces a clean list of tokens
that the parser (in nfa.py) can use to build the NFA.

A token is just a small dictionary with two keys:
    - 'type'  : 'SYMBOL'or 'OP' operator
    - 'value' : the actual character ('a', '*', '|', '(', ')')

we need this:
  - The user might type "a | b" with spaces  -> we strip them out
  - The user might type "\*" to mean a literal star -> we mark it as SYMBOL, not OP
  - The user might type "[a-z]" as shorthand -> we expand it to (a|b|c|...|z)
  - The user might type something invalid -> we catch it early with a clear error
"""


# ERROR TYPE
class TokenizerError(Exception):
    """Raised when the input regex is invalid in some way."""
    pass


# WHAT COUNTS AS WHAT 
OPERATORS = {'|', '*', '+', '?', '(', ')', '.'}
# These are the characters that have special meaning in our regex.

ESCAPABLE = OPERATORS | {'\\', '[', ']', '-'}
# These are the characters you are ALLOWED to escape with a backslash.
# For example "\*" gives you a literal star, "\\" gives you a literal backslash.


# HELPER: EXPAND ONE CHARACTER CLASS 
def expand_char_class(content):
    """
    Takes the inside of a [...] and returns a list of characters.

    Examples:
        "abc"   -> ['a', 'b', 'c']
        "a-c"   -> ['a', 'b', 'c']
        "a-cx"  -> ['a', 'b', 'c', 'x']
        "0-9"   -> ['0', '1', '2', ..., '9']

    The trick for ranges: we use Python's ord() to get the character's number,
    then loop from the start number to the end number, and use chr() to turn
    each number back into a character.
    """
    if not content:
        raise TokenizerError("Empty character class '[]' is not allowed")

    chars = []
    i = 0
    while i < len(content):
        # Check if this is a range like "a-z"
        # A range needs THREE things: a start char, a dash, and an end char.
        # So we need at least 2 more characters after position i.
        if i + 2 < len(content) and content[i + 1] == '-':
            start = content[i]
            end = content[i + 2]

            if not (start.isalnum() and end.isalnum()):
                raise TokenizerError(
                    f"Character class range '{start}-{end}' must use letters or digits"
                )
            if ord(start) > ord(end):
                raise TokenizerError(
                    f"Character class range '{start}-{end}' is backwards (start > end)"
                )

            # ord('a') = 97, ord('c') = 99, so range gives us 97, 98, 99
            # chr(97) = 'a', chr(98) = 'b', chr(99) = 'c'
            for code in range(ord(start), ord(end) + 1):
                chars.append(chr(code))
            i += 3   # skip past start, dash, end
        else:
            # Just a single character (not part of a range)
            ch = content[i]
            if not ch.isalnum():
                raise TokenizerError(
                    f"Character class can only contain letters/digits, got '{ch}'"
                )
            chars.append(ch)
            i += 1

    # Remove duplicates while keeping order. dict.fromkeys is a neat trick:
    # it builds a dict where keys are unique and ordered by first appearance.
    chars = list(dict.fromkeys(chars))
    return chars


# THE MAIN TOKENIZER 
def tokenize(regex):
    """
    Convert a raw regex string into a list of tokens.

    Returns a list of dicts like:
        [{'type': 'SYMBOL', 'value': 'a'}, {'type': 'OP', 'value': '*'}]
    """
    if regex is None or regex == "":
        raise TokenizerError("Regex cannot be empty")

    tokens = []
    i = 0
    paren_depth = 0   # counts open parens, so we can detect unmatched ones

    while i < len(regex):
        ch = regex[i]

        # 1. SKIP WHITESPACE 
        if ch.isspace():
            i += 1
            continue

        # 2. ESCAPE CHARACTER 
        # If we see a backslash, the NEXT character is treated as a literal symbol,
        # even if it would normally be an operator.
        if ch == '\\':
            if i + 1 >= len(regex):
                raise TokenizerError("Backslash at end of regex has nothing to escape")
            next_ch = regex[i + 1]
            if next_ch not in ESCAPABLE:
                raise TokenizerError(
                    f"Cannot escape character '{next_ch}' (only operators and brackets)"
                )
            tokens.append({'type': 'SYMBOL', 'value': next_ch})
            i += 2   # skip both the backslash and the escaped character
            continue

        # 3. CHARACTER CLASS [a-z] 
        if ch == '[':
            # Find the matching closing bracket
            close_idx = regex.find(']', i + 1)
            if close_idx == -1:
                raise TokenizerError("Opening '[' has no matching ']'")

            inside = regex[i + 1:close_idx]
            expanded = expand_char_class(inside)

            # Now we turn [abc] into the equivalent (a|b|c) using tokens.
            # If there's only one character, no need for parens or pipes.
            if len(expanded) == 1:
                tokens.append({'type': 'SYMBOL', 'value': expanded[0]})
            else:
                tokens.append({'type': 'OP', 'value': '('})
                for idx, c in enumerate(expanded):
                    if idx > 0:
                        tokens.append({'type': 'OP', 'value': '|'})
                    tokens.append({'type': 'SYMBOL', 'value': c})
                tokens.append({'type': 'OP', 'value': ')'})

            i = close_idx + 1   # skip past the closing ]
            continue

        # 4. STRAY CLOSING BRACKET
        if ch == ']':
            raise TokenizerError("Closing ']' has no matching '['")

        # 5. OPERATORS
        if ch in OPERATORS:
            if ch == '(':
                paren_depth += 1
            elif ch == ')':
                paren_depth -= 1
                if paren_depth < 0:
                    raise TokenizerError("Closing ')' has no matching '('")
            tokens.append({'type': 'OP', 'value': ch})
            i += 1
            continue

        # 6. NORMAL SYMBOL (letter or digit)
        if ch.isalnum():
            tokens.append({'type': 'SYMBOL', 'value': ch})
            i += 1
            continue

        # 7. ANYTHING ELSE = ERROR
        raise TokenizerError(f"Unexpected character '{ch}' in regex")

    # FINAL CHECKS
    if paren_depth > 0:
        raise TokenizerError(f"{paren_depth} opening '(' has no matching ')'")
    if not tokens:
        raise TokenizerError("Regex contains no usable characters")

    # Check for empty parens like "()"
    for idx in range(len(tokens) - 1):
        if (tokens[idx]['value'] == '(' and
                tokens[idx + 1]['value'] == ')'):
            raise TokenizerError("Empty parentheses '()' are not allowed")

    return tokens


# ADAPTER: TOKEN LIST -> STRING FOR EXISTING PARSER 
def tokens_to_string(tokens):
    """
    Convert the token list back into a plain string that the existing
    add_concat() and infix_to_postfix() functions in nfa.py can use.

    This way we don't have to change any of your group's existing code!
    """
    return ''.join(t['value'] for t in tokens)


# HELPER: EXTRACT THE ALPHABET 
def get_alphabet(tokens):
    """
    Get the set of all symbols (input characters) used in the regex.
    Used later to know which characters to test against the DFA.
    """
    return sorted(set(t['value'] for t in tokens if t['type'] == 'SYMBOL'))


# QUICK DEMO 
if __name__ == "__main__":
    test_cases = [
        "a*b",
        "(a|b)*abb",
        "[a-c]*",
        "[0-9]+",
        "a | b",          # whitespace
        "\\*\\|",         # escaped operators
        "[abc]|x",
    ]

    for tc in test_cases:
        print(f"\nInput : {tc!r}")
        try:
            toks = tokenize(tc)
            print(f"Tokens: {toks}")
            print(f"String: {tokens_to_string(toks)!r}")
            print(f"Alpha : {get_alphabet(toks)}")
        except TokenizerError as e:
            print(f"ERROR : {e}")

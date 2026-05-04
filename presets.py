"""
regex examples for the simulator.

preset is a dictionary with:
    - 'name'
    - 'regex'
    - 'description'
    - 'examples'
"""


PRESETS = [
    {
        'name': 'Strings ending in b',
        'regex': '(a|b)*b',
        'description': 'Any string of a and b that ends with the letter b',
        'examples': ['b', 'ab', 'abb', 'bab', 'aaab'],
    },
    {
        'name': 'Strings starting with a',
        'regex': 'a(a|b)*',
        'description': 'Any string of a and b that starts with the letter a',
        'examples': ['a', 'ab', 'aa', 'abba', 'aaab'],
    },
    {
        'name': 'Contains substring "ab"',
        'regex': '(a|b)*ab(a|b)*',
        'description': 'Any string that contains "ab" somewhere inside it',
        'examples': ['ab', 'aab', 'abb', 'bab', 'aabb'],
    },
    {
        'name': 'Even number of zeros',
        'regex': '(1*01*0)*1*',
        'description': 'Binary strings with an even count of 0s (zero is even)',
        'examples': ['', '1', '11', '00', '0110', '1001'],
    },
    {
        'name': 'Binary numbers',
        'regex': '[0-1]+',
        'description': 'One or more binary digits (uses character class)',
        'examples': ['0', '1', '10', '101', '1100'],
    },
    {
        'name': 'Lowercase letters',
        'regex': '[a-z]+',
        'description': 'One or more lowercase letters (uses character class)',
        'examples': ['a', 'hello', 'cat', 'xyz'],
    },
    {
        'name': 'Optional sign with digits',
        'regex': '(\\+|-)?[0-9]+',
        'description': 'Digits with an optional + or - sign in front',
        'examples': ['5', '+5', '-5', '123', '-99'],
    },
    {
        'name': 'a followed by zero or more b',
        'regex': 'ab*',
        'description': 'A single a, then any number of b (including zero)',
        'examples': ['a', 'ab', 'abb', 'abbb'],
    },
    {
        'name': 'One or more a',
        'regex': 'a+',
        'description': 'At least one a, with no other characters',
        'examples': ['a', 'aa', 'aaa', 'aaaa'],
    },
    {
        'name': 'Strings of length 3',
        'regex': '(a|b)(a|b)(a|b)',
        'description': 'Exactly three characters, each being a or b',
        'examples': ['aaa', 'aab', 'bab', 'bbb'],
    },
]


def get_preset_names():
    """Return just the names, useful for building a dropdown menu."""
    return [p['name'] for p in PRESETS]


def get_preset_by_name(name):
    """Look up a preset by its name. Returns None if not found."""
    for p in PRESETS:
        if p['name'] == name:
            return p
    return None


if __name__ == "__main__":
    print(f"Total presets available: {len(PRESETS)}\n")
    for p in PRESETS:
        print(f"  {p['name']}")
        print(f"    Regex      : {p['regex']}")
        print(f"    Description: {p['description']}")
        print(f"    Examples   : {p['examples']}")
        print()
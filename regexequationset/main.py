example = {
    'S': ['0A', '1S', 'e'],
    'A': ['0B', '1A'],
    'B': ['0S', '1B'],
}

class Rule():
    def __init__(self, name: str, body: list):
        self.name = name

class RegEquations():
    epsilon = 'e'

    def __init__(self, grammar: dict = {}):
        pass
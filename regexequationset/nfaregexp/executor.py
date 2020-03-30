from .tokenizer import to_postfix
from .compiler import State, SplitState, Match, compile_regex

from typing import Union

class Regex:
    def __init__(self, pattern: str):
        self.pattern = pattern
        self.start_state = compile_regex(to_postfix(pattern))

    def match(self, s: str) -> bool:
        current_state_s = set()

        update_states(current_state_s, self.start_state)

        for char in s:
            current_state_s = make_step(current_state_s, char)

        return Match in current_state_s

    @staticmethod
    def compile(pattern: str):
        return Regex(pattern)

def update_states(current_state_s: set, state) -> None:
    if state in current_state_s: return

    elif isinstance(state, State) or state is Match:
        current_state_s.add(state)

    elif isinstance(state, SplitState):
        update_states(current_state_s, state.outs[0])
        update_states(current_state_s, state.outs[1])

def make_step(current_state_s: set, char: str) -> set:
    new_states = set()

    for state in current_state_s:
        if state is not Match and state.char == char:
            update_states(new_states, state.outs[0])

    return new_states

def match(pattern: str, s: str) -> bool:
    postfix = to_postfix(pattern)
    state = compile_regex(postfix)

    current_state_s = set()
    update_states(current_state_s, state)

    for char in s:
        current_state_s = make_step(current_state_s, char)

    return Match in current_state_s

if __name__ == "__main__":
    regex = Regex.compile('^a|b$')
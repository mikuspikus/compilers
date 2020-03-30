from .tokenizer import Character, Concatenation, Disjunction, Operator
from typing import List, Union

class State:
    __slots__ = ('char', 'outs')

    def __init__(self, char: str):
        self.char = char
        self.outs = []

    def __str__(self) -> str:
        return f'State<{self.char}> -> {self.outs[0]}'

class SplitState:
    __slots__ = ('outs')

    def __init__(self):
        self.outs = []

    def __str__(self) -> str:
        return f'SplitState<{self.outs}>'

class _Match:
    def __str__(self) -> str:
        return 'Match'

Match = _Match()

class Arrow:
    __slots__ = ('state', 'out_index')

    def __init__(self, state: State, out_index: int):
        self.state = state
        self.out_index = out_index

class Fragment:
    __slots__ = ('start', 'arrow_s')

    def __init__(self, start, arrow_s: List[Arrow]):
        self.start = start
        self.arrow_s = arrow_s

def connect(fragment: Fragment, state) -> None:
    '''Connects all fragment's arrow_s to given state 
    '''
    while fragment.arrow_s:
        arrow = fragment.arrow_s.pop()
        arrow.state.outs[arrow.out_index] = state

def is_character(obj): return isinstance(obj, Character)
def is_operator(obj): return isinstance(obj, Operator)
def is_concatenation(obj): return isinstance(obj, Concatenation)
def is_disjunction(obj): return isinstance(obj, Disjunction)

def compile_regex(pattern: list) -> State:
    '''Compiles postfix form (like 'ab+') into NFA'''
    stack = []

    for token in pattern:
        if is_character(token):
            state = State(token)
            state.outs.append(None)

            arrow_s = [Arrow(state, 0)]
            fragment = Fragment(state, arrow_s)

            stack.append(fragment)

        elif is_concatenation(token):
            right_frag = stack.pop()
            left_frag = stack.pop()

            connect(left_frag, right_frag.start)
            fragment = Fragment(left_frag.start, right_frag.arrow_s)

            stack.append(fragment)

        elif is_disjunction(token):
            right_frag = stack.pop()
            left_frag = stack.pop()

            state = SplitState()

            state.outs.append(right_frag.start)
            state.outs.append(left_frag.start)

            arrow_s = right_frag.arrow_s + left_frag.arrow_s

            fragment = Fragment(state, arrow_s)

            stack.append(fragment)

        # if we are here then token is operator 
        elif token.op == '+':
            prev_frag = stack.pop()
            state = SplitState()

            # cycle over state
            state.outs.append(prev_frag.start)
            # arrow for the next fragment
            state.outs.append(None)

            connect(prev_frag, state)
            arrow_s = [Arrow(state, 1)]
            fragment = Fragment(prev_frag.start, arrow_s)

            stack.append(fragment)

        elif token.op == '*':
            prev_frag = stack.pop()
            state = SplitState()

            state.outs.append(prev_frag.start)
            connect(prev_frag, state)

            state.outs.append(None)
            arrow_s = [Arrow(state, 1)]

            fragment = Fragment(state, arrow_s)

            stack.append(fragment)

        elif token.op == '?':
            prev_frag = stack.pop()

            state = SplitState()
            state.outs.append(prev_frag.start)

            connect(prev_frag, state)

            state.outs.append(None)
            arrow_s = [Arrow(state, 1)]

            fragment = Fragment(state, arrow_s)

            stack.append(fragment)

    if stack:
        fragment = stack.pop()
        connect(fragment, Match)
        return fragment.start

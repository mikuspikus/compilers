
from .nfaregexp.tokenizer import Character, Concatenation, Disjunction, Operator, Variable, BadRegexError
from .expressiontree import ExpressionTreeNode

def equation_to_postfix(delta: set, equation: str) -> list:
    stack = []
    natoms = 0
    in_parenthesis = False
    buffer = []
    nalt = 0
    escape = False
    caret = False
    nonpenparenthesis = 0

    for character in equation:

        if character == '\\':
            if in_parenthesis:
                buffer.append(character)

            else:
                escape = True
        
        elif escape:
            # like '^\"$'
            # just add wahtever follows escape
            if in_parenthesis:
                buffer.append(character)
            
            else:
                if natoms > 1:
                    stack.append(Concatenation())
                    natoms = -1

                stack.append(Character(character, caret))
                caret = False
                natoms += 1
            
            escape = False
            continue

        elif in_parenthesis and character != ')':
            # accumulate symbols in parenthesis
            # before applying to postfix

            if character == '(':
                nonpenparenthesis += 1

            buffer.append(character)
            continue

        elif character == '^':
            caret = True

        elif character in '+*?':
            if natoms == 0:
                raise BadRegexError(f'No arguments for operator {character}')

            if isinstance(stack[-1], Operator):
                raise BadRegexError(f'Two operators second operator {character}')

            stack.append(Operator(character))

        elif character == '|':
            if natoms == 0:
                raise BadRegexError(f'No arguments for operator {character}')

            natoms -= 1
            while natoms:
                stack.append(Concatenation())
                natoms -= 1

            nalt += 1
        elif character == '(':
            # group in parenthesis starts
            in_parenthesis = True
            nonpenparenthesis += 1

        elif character == ')':
            nonpenparenthesis -= 1

            # if nested parenthesis
            if nonpenparenthesis != 0:
                buffer.append(')')
                continue

            in_parenthesis = False
            expression = equation_to_postfix(''.join(buffer), delta)

            if expression is None:
                raise BadRegexError('Incorrect expression in parenthesis')

            buffer = []
            if natoms > 1:
                stack.append(Concatenation())
                natoms -= 1

            stack.extend(expression)
            natoms += 1

        else:
            # regular character
            if natoms > 1:
                stack.append(Concatenation())
                natoms -= 1

            if character in delta:
                variable = Variable(character)
                stack.append(variable)

            else:
                character_ = Character(character, caret, character == '.')
                stack.append(character_)

            caret = False
            natoms += 1

    if natoms > 1:
        stack.append(Concatenation())

    while nalt:
        stack.append(Disjunction())
        nalt -= 1

    return stack

def replace_variable(equation: list, variable: str, variable_expression: list) -> list:
    position_s = []
    result = equation[:]

    for index, item in enumerate(equation):
        if isinstance(item, Variable) and item == variable:
            position_s.append(index)

    for index in reversed(position_s):
        result = result[:index] + variable_expression + result[index + 1:]

    return result

class RegexEquation:
    
    def __init__(self, var: str, delta: set, equation: str):
        '''
        param delta -- set of variables of regex equations set
        '''
        self.delta = delta
        self.variable = var
        self.__eq = equation
        self.__postfix_form = equation_to_postfix(delta, equation)
        self.__tree_form = ExpressionTreeNode.build(self.__postfix_form)

    def express_variable(self):
        '''Должна делать копию, а не менять оригинал
        '''
        return self.__tree_form.evaluate_var_copy(self.variable)

    def replace_variable(self, var: str, replace_node: ExpressionTreeNode) -> None:
        self.__tree_form.replace_var_all(var, replace_node)

    def to_postfix(self) -> list:
        return self.__tree_form.to_postfix()

    def __str__(self) -> str:
        return str(self.__tree_form)

    def __repr__(self) -> str:
        return str(self)


class SetRegexEquation:

    def __init__(self, equation_set: dict):
        self.delta = self.__delta(equation_set)

        self.equations = []

        for key in equation_set:
            self.equations.append(RegexEquation(key, self.delta, equation_set[key]))


    def __delta(self, equation_set: dict) -> set:
        return set(equation_set.keys())

    def solve(self):
        
        for index, equation in enumerate(self.equations):
            expressed_variable = equation.express_variable()

            for nex_eq in self.equations[index + 1:]:
                nex_eq.replace_variable(equation.variable, expressed_variable)

        last_equation = self.equations[-1]
        last_expressed_variable = last_equation.express_variable()
        last_variable = last_equation.variable

        for index, equation in enumerate(reversed(self.equations)):
            index = len(self.equations) - index
            for prev_eq in self.equations[:index]:
                prev_eq.replace_variable(last_variable, last_expressed_variable)

        return self.equations[0].to_postfix()

if __name__ == "__main__":
    set_data = {
        'S' : '0A|1S|e',
        'A' : '0B|1A',
        'B' : '0S|1B'
    }

    set_ = SetRegexEquation(set_data)
    result = set_.solve()
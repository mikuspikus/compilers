from typing import Tuple, Union
# add exceptions


class OpPrecError(Exception):
    pass


class OpPrecParser:
    rel_op = ['==', '<>', '<', '<=', '>', '>=']
    add_op = ['+', '-', 'or']
    mul_op = ['*', '/', 'div', 'mod', 'and']
    unary_op = ['~']
    numbers = [str(i) for i in range(10)]
    dollar = '$'
    expression = 'E'

    def __init__(self):
        pass

    def __precedence(self, stack_token: str, next_token: str) -> Union[None, str]:
        if stack_token in self.unary_op:
            if next_token in self.add_op + self.rel_op + self.mul_op + [')', self.dollar]:
                return '>'
            else:
                return '<'

        if stack_token in self.add_op:
            if next_token in self.add_op + self.rel_op + [')', self.dollar]:
                return '>'
            else:
                return '<'

        if stack_token in self.mul_op:
            if next_token in self.add_op + self.mul_op + self.rel_op + [')', self.dollar]:
                return '>'
            else:
                return '<'

        if stack_token in self.rel_op:
            if next_token in self.rel_op + [')', self.dollar]:
                return '>'
            else:
                return '<'

        if stack_token in self.numbers:
            if next_token in self.add_op + self.mul_op + self.rel_op + [')', self.dollar]:
                return '>'
            else:
                return None

        if stack_token == '(':
            if next_token in self.unary_op + self.add_op + self.mul_op + self.rel_op + self.numbers + ['(', ')']:
                return '<'
            else:
                return None

        if stack_token == ')':
            if next_token in self.unary_op + self.add_op + self.mul_op + self.rel_op + [')', self.dollar]:
                return '>'
            else:
                return None

        if stack_token == '$':
            if next_token in self.unary_op + self.add_op + self.mul_op + self.rel_op + self.numbers + ['(']:
                return '<'
            else:
                return None

        return None

    def parse(self, input: str) -> list:
        stack = [self.dollar]
        string = ''.join(input.split(' ')) + self.dollar
        stpostfix = []
        stnumbers = []
        while stack != [self.dollar, self.expression] or string != self.dollar:
            string, current_token = self.__next_token(string)

            if current_token in self.numbers:
                stnumbers.append(current_token)

            last_token = [x for x in stack if x != self.expression][-1]
            priority = self.__precedence(last_token, current_token)
            if priority is None:
                # raise exception -- priority not found
                # return None
                raise OpPrecError(
                    f"Precedence not found for pair ({last_token}, {current_token})")

            if priority == '>':
                string = current_token + string
                # reduction
                for i in range(1, len(stack)):
                    #  try reduction from the end
                    slice_ = stack[-i:]
                    # reduction result
                    lhs_nterm = self.__rule_reduction(slice_)

                    if lhs_nterm is not None:
                        stack = stack[:-i]
                        stack.append(lhs_nterm)

                        # [~ E] case
                        if len(slice_) == 2 and slice_[0] in self.unary_op:
                            while len(stnumbers) > 0:
                                stpostfix.append(stnumbers.pop(0))

                            stpostfix.append(slice_[0])

                        # [E +/*/... E] case
                        if len(slice_) == 3 and slice_[0] != '(':
                            while len(stnumbers) > 0:
                                stpostfix.append(stnumbers.pop(0))

                            stpostfix.append(slice_[1])
                        break
                else:
                    # raise exception -- stack is empty
                    # return None
                    raise OpPrecError(
                        f"Stack is empty for token {current_token} and string {string}")
            else:
                stack.append(current_token)

        return stpostfix

        while not stack == ['$', 'E'] and string != '$':
            next_roken = self.__peek_next_token()

    def __next_token(self, string: str) -> Tuple[str, str]:
        current_token = string[0]

        if current_token in ('>', '=') and len(string) > 1 and string[1] == '=':
            current_token += string[1]
            string = string[2:]

        elif current_token in ('<', ) and len(string) > 1 and string[1] in ('=', '>'):
            current_token += string[1]
            string = string[2:]

        else:
            string = string[1:]

        return string, current_token

    def __rule_reduction(self, stack: list):
        """
        ( E ) -> E
        E +/*/... E -> E
        ~ E -> E
        """
        if len(stack) == 3:
            # ( E ) reduction case
            if stack == ['(', self.expression, ')']:
                return self.expression
            # E +/*/... E reduction case
            if stack[0] == stack[2] == self.expression and stack[1] in self.add_op + self.rel_op + self.mul_op:
                return self.expression

        # ~ E reduction case
        elif len(stack) == 2 and stack[0] in self.unary_op and stack[1] == self.expression:
            return self.expression
        # number reduction case
        elif len(stack) == 1 and stack[0] in self.numbers:
            return self.expression

        return None


if __name__ == "__main__":
    cases = [
        ('1 + 2 * 3', ['1', '2', '3', '*', '+']),
        ('( 1 + 2 ) * 3', ['1', '2', '+', '3', '*']),
        ('~ 1 + 2 * 3', ['1', '~', '2', '3', '*', '+']),
        ('~ ( 1 + 2 ) * 3', ['1', '2', '+', '~', '3', '*']),
        ('~ ( 1 * 2 * 3)', ['1', '2', '*', '3', '*', '~']),
        ('1 * ~ ( 2 + 3 )', ['1', '2', '3', '+', '~', '*']),
        ('1 >= 2 <= 3 * 4', ['1', '2', '>', '3', '4', '*', '>']),
        ('( 1 > 2 ) + 3 * 4', ['1', '2', '>', '3', '4', '*', '+']),
        ('1 <> 2', ['1', '2', '<>']),
    ]

    parser = OpPrecParser()

    for string, _ in cases:
        print(parser.parse(string))

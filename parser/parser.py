from typing import Tuple, Any, Union

class ParseError(Exception):
    pass

class RDParser:
    # <expr> -> <simple_expr> | <simple_expr> <rel_op> <simple_expr>

    # <simple_expr> -> <term> | <sign><term> | <simple_expr> <add_op> <term>

    # <term> -> <factor> | <term> <mul_op> <factor>

    # <factor> -> <identifier> | <constant> | (<simple_expr) | not <factor>

    # <rel_op> -> == | <> | < | <= | > | >=
    # <sign> -> + | -
    # <add_op> -> + | - | or
    # <mul_op> -> * | / | div | mod | and

    left_par = '('
    right_par = ')'
    left_curly_br = '{'
    right_curly_br = '}'

    keywords = {'or', 'div', 'mod', 'and', 'not'}

    rel_ops = {'==', '<>' ,'<', '<=', '>', '>='}
    add_ops = {'+', '-', 'or'}
    mul_ops = {'*', '/', 'div', 'mod', 'and'}
    negation = 'not'

    signs = {'+', '-'}
    identifiers = {'a'}
    constants = {'const', '123'}
    assign = {'='}
    semicolon = {';'}

    def __init__(self, s: str):
        self.input = s.strip()
        self.col = 1
        self.row = 1
        self.i = 0

    def __msg(self, exp: str) -> str:
        return f"{exp} expected at ({self.row}, {self.col})"

    def next_char(self, i):
        ws = {' ', '\n'}

        while True:
            if i >= len(self.input): return len(self.input)

            if self.input[i] == ' ':
                self.col += 1

            elif self.input[i] == '\n':
                self.col = 1
                self.row += 1

            else:
                self.col += 1
                return i
            
            i += 1

    def accept(self, symbol: str) -> bool:
        oldCol, oldRow, i = self.col, self.row, self.i
        
        for char in symbol:
            i = self.next_char(i)

            if i >= len(self.input): return False

            if char != self.input[i]:
                self.col = oldCol
                self.row = oldRow
                return False

            i += 1

        self.i = i
        return True


    def __generic_accept(self, kws: set, name: str) -> Tuple[bool, Union[None, Tuple[str, str]]]:
        for kw in kws:
            if self.accept(kw):
                return True, (name, kw)
 
        return False, None

    def mul_op(self) -> Tuple[bool, Union[None, Tuple[str, str]]]:
        return self.__generic_accept(self.mul_ops, 'mul_ops')

    def add_op(self) -> Tuple[bool, Union[None, Tuple[str, str]]]:
        return self.__generic_accept(self.add_ops, 'add_op')

    def rel_op(self) -> Tuple[bool, Union[None, Tuple[str, str]]]:
        return self.__generic_accept(self.rel_ops, 'rel_op')

    def sign(self) -> Tuple[bool, Union[None, Tuple[str, str]]]:
        return self.__generic_accept(self.signs, 'sign')

    def identifier(self):
        return self.__generic_accept(self.identifiers, 'identifier')

    def constant(self):
        return self.__generic_accept(self.constants, 'constant')

    def not_factor(self):
        '''not <factor>'''
        has_negotion = self.accept(self.negation)
        if not has_negotion:
            # msg = self.__msg(f"{self.negation} keyword")
            # raise ParseError(msg)
            return False, None

        has_factor, factor = self.factor()
        if not has_factor:
            msg = self.__msg(f"<factor> expression")
            raise ParseError(msg)

        return True, ('not', factor)


    def simple_expr_brackets(self):
        '''(<simple_expr)'''
        has_left_par = self.accept(self.left_par)
        if not has_left_par:
            # msg = self.__msg(f"{self.left_par}")
            # raise ParseError(msg)
            return False, None

        has_simple_expr, simple_expr = self.simple_expr()
        if not has_simple_expr:
            msg = self.__msg(f"<simple expression>")
            raise ParseError(msg)

        has_right_par = self.accept(self.right_par)
        if not has_right_par:
            msg = self.__msg(f"{self.right_par}")
            raise ParseError(msg)

        return True, ('brackets', simple_expr)

    def factor(self):
        '''<factor> -> <identifier> | <constant> | (<simple_expr) | not <factor>'''

        has_ident, ident = self.identifier()
        if has_ident: return True, ('factor', ident)

        has_constant, constant = self.constant()
        if has_constant: return True, ('factor', constant)

        has_simple_expr_in_brackets, simple_expr_br = self.simple_expr_brackets()
        if has_simple_expr_in_brackets: return True, ('factor', simple_expr_br)

        has_not_factor, not_factor = self.not_factor()
        if has_not_factor: return True, ('factor', not_factor)

        return False, None

    def term_mul_factor(self):
        '''<term> <mul_op> <factor>'''
        # has_term, term = self.term()
        # if not has_term:
        #     # msg = self.msg(f"<term>")
        #     # raise ParseError(msg)
        #     return False, None

        has_mul, mul = self.mul_op()
        if not has_mul:
            # msg = self.__msg(f"<mul_op>")
            # raise ParseError(msg)
            return False, None

        has_factor, factor = self.factor()
        if not has_factor:
            msg = self.__msg(f"<factor>")
            raise ParseError(msg)
            # return False, None

        return True, ('mul_op', mul, factor)
        

    def term(self):
        '''<term> -> <factor> | <term> <mul_op> <factor>'''
        has_factor, factor = self.factor()
        if has_factor:
            has_term_mul_factor, term_mul_factor = self.term_mul_factor()
            if has_term_mul_factor: return True, ('term', term_mul_factor)

            return ('term', factor)

        return False, None

    def term_with_sign(self):
        '''<sign><term>'''
        has_sign, sign = self.sign()
        if not has_sign:
            # msg = self.__msg("<sign>")
            # raise ParseError(msg)
            return False, None

        has_term, term = self.term()
        if not has_term:
            msg = self.__msg("<term>")

        return True, ('sign', sign, term)

    def simple_expr_add_term(self):
        '''<simple_expr> <add_op> <term>'''
        # has_simple_expr, simple_expr = self.simple_expr()
        # if not has_simple_expr:
        #     msg = self.__msg('<simple_expr')
        #     raise ParseError(msg)

        has_add_op, add = self.add_op()
        if not has_add_op:
            # msg = self.__msg('<add_op')
            return False, None

        has_term, term = self.term()
        if not has_term:
            msg = self.__msg('<term>')
            raise ParseError(msg)

        return True, ('add_op', add, term)

    def simple_expr(self):
        '''<term> | <sign><term> | <simple_expr> <add_op> <term>'''

        has_term_with_sign, term = self.term_with_sign()
        if has_term_with_sign: return True, ('simple_expr', term_with_sign)

        has_term, term = self.term()
        if has_term or has_term_with_sign:
            has_simple_expr_add_term, simple_expr_add_term = self.simple_expr_add_term()
            if has_simple_expr_add_term: return True, ('simple_expr', term, simple_expr_add_term)

            return True, ('simple_expr', term)

        return False, None

    def simple_expr_rel_simple_expr(self):
        '''<simple_expr> <rel_op> <simple_expr>'''
        # has_simple_expr, simple_expr = self.simple_expr()
        # if not has_simple_expr:
        #     msg = self.__msg('<simple_expr>')
        #     raise ParseError(msg)

        has_rel_op, rel = self.rel_op()
        if not has_rel_op:
            # msg = self.__msg('<rel_op>')
            # raise ParseError(msg)
            return False, None

        has_simple_expr, simple_expr2 = self.simple_expr()
        if not has_simple_expr:
            msg = self.__msg('<simple_expr>')
            raise ParseError(msg)

        return True, ('rel_op', rel, simple_expr2)

    def expr(self):
        '''<expr> -> <simple_expr> | <simple_expr> <rel_op> <simple_expr>'''
        has_simple_expr, simple_expr = self.simple_expr()
        if has_simple_expr: 
            has_simple_expr_rel, simple_expr_rel = self.simple_expr_rel_simple_expr()
            if has_simple_expr_rel: return True, ('expr', simple_expr, simple_expr_rel)

        return True, ('expr', simple_expr)

    def assignment(self):
        return self.__generic_accept(self.assign, 'assignment')

    def operator(self):
        '''<operator> -> <identifier> <assignment> <expr> | <unit>'''
        has_identifier, identifier = self.identifier()
        has_assignment, assignment = self.assignment()
        if has_identifier and has_assignment:
            has_expr, expr = self.expr()
            # raise error?
            if not has_expr: return False, None

            return True, ('operator', assignment, identifier, expr)

        has_unit, unit = self.unit()
        if not has_unit: return False, None
            # msg = self.__msg('<expr>')
            # raise ParseError(msg)

        return True, ('operator', unit)

    def tail(self):
        ''';'''
        has_tail = self.accept(self.semicolon)
        if has_tail: return True, ('tail', self.semicolon)

        return False, None

    def operator_tail(self):
        '''<tail> -> ; <operator> <tail> | epsilon'''
        has_tail, tail = self.tail()
        if has_tail:
            has_operator, operator = self.operator()
            if not has_operator:
                msg = self.__msg('<operator>')
                raise ParseError(msg)

            has_tail, tail = self.operator_tail()
            return True, ('operator_tail', operator, tail)

        return True, ('operator_tail')

    def operator_list(self):
        '''<operator_list> -> <operator> <operator_tail>''' 
        has_operator, operator = self.operator()
        if not has_operator: return False, None

        has_tail, tail = self.operator_tail()
        if not has_tail: return False, None

        return True, ('operator_list', operator, tail)

    def unit(self):
        '''<unit> -> { <operator_list> }'''
        if not self.accept(self.left_curly_br): return False, None
        
        has_op_list, op_list = self.operator_list()
        if not has_op_list: return False, None

        if not self.accept(self.right_curly_br):
            msg = self.__msg(f'<{self.right_curly_br}>')
            raise ParseError(msg)

        return True, ('unit', op_list)

    def program(self):
        '''<program> -> <unit>'''
        has_unit, unit = self.unit()
        if not has_unit:
            msg = f'program failed at ({self.row}, {self.col})'
            raise ParseError(msg)

        return True, ('program', unit)

    def run(self):
        _, program = self.program()

        return self.i == len(self.input), program

if __name__ == "__main__":
    filename = 'parser/tests/good.txt'
    with open(filename) as f:
        s = f.read()

    parser = RDParser(s)
    print(parser.run())

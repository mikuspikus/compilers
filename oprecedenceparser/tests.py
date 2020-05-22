from unittest import TestCase
from oprecedenceparser.opprecparser import OpPrecParser


class OpPrecParserTestCase(TestCase):

    def test_op_prec_parser(self):
        cases = [
            ('1 + 2 * 3', ['1', '2', '3', '*', '+']),
            ('( 1 + 2 ) * 3', ['1', '2', '+', '3', '*']),
            ('~ 1 + 2 * 3', ['1', '~', '2', '3', '*', '+']),
            ('~ ( 1 + 2 ) * 3', ['1', '2', '+', '~', '3', '*']),
            ('~ ( 1 * 2 * 3)', ['1', '2', '*', '3', '*', '~']),
            ('1 * ~ ( 2 + 3 )', ['1', '2', '3', '+', '~', '*']),
            ('1 > 2 > 3 * 4', ['1', '2', '>', '3', '4', '*', '>']),
            ('( 1 > 2 ) + 3 * 4', ['1', '2', '>', '3', '4', '*', '+']),
        ]

        parser = OpPrecParser()

        for string, answer in cases:
            self.assertEqual(parser.parse(string), answer)

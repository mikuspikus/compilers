from unittest import TestCase
from parser.parser import RDParser, ParseError

import os

class Test(TestCase):

    def test_good(self):
        filename = 'parser/tests/good.txt'
        with open(filename) as f:
            s = f.read()

        parser = RDParser(s)
        result, tuple_ = parser.run()

        self.assertEqual(result, True)

    def test_fst_bad(self):
        filename = 'parser/tests/fst_bad.txt'
        with open(filename) as f:
            s = f.read()

        parser = RDParser(s)
        self.assertRaises(ParseError, parser.run)

    def test_snd_bad(self):
        filename = 'parser/tests/snd_bad.txt'
        with open(filename) as f:
            s = f.read()

        parser = RDParser(s)
        self.assertRaises(ParseError, parser.run)
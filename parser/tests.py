from unittest import TestCase
from parser import RDParser

import os

class Test(TestCase):

    def test_good(self):
        filename = 'tests/good.txt'
        with open(filename) as f:
            s = f.read()

        parser = RDParser(s)
        parser.run()
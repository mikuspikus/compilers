from .executor import Regex
from unittest import TestCase

class Test(TestCase):

    def test_matched(self):
        pattern = '^(a|b)*$'
        regex = Regex.compile(pattern)

        string_s = ['a', 'b', 'aa', 'bb', 'ab', 'abab', 'aab']

        for string in string_s:
            self.assertEqual(regex.match(string), True, f'string \'{string}\' must match with pattern {pattern}')

    def test_not_matched(self):
        pattern = '^(a|b)*$'
        regex = Regex.compile(pattern)

        string = 'x'

        self.assertEqual(regex.match(string), False, f'string \'{string}\' must not match with {pattern}')

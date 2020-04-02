from unittest import TestCase

from .grammar import Grammar, readJson
from unittest import TestCase

class TestGrammar(TestCase):

    def setUp(self):
        folder = 'grammar/testjson'
        self.reachable = f'{folder}/reachable.json'
        self.factorization = f'{folder}/factorization.json'
        self.recursion = f'{folder}/recursion.json'

    def test_build(self):
        cases = {
            self.reachable: {'t': 3, 'nt': 2, 'pr': 2},
            self.factorization: {'t': 6, 'nt': 2, 'pr': 4},
            self.recursion: {'t': 5, 'nt': 2, 'pr': 5},
        }

        for path, info in cases.items():
            grammar = Grammar.build(readJson(path))

            self.assertEqual(len(grammar.terminals), info['t'], f"Unequal terminals count for '{path}'")
            self.assertEqual(len(grammar.nonterminals), info['nt'], f"Unequal nonterminals count for '{path}'")
            self.assertEqual(len(grammar.productions), info['pr'], f"Unequal productions count for '{path}'")

    def test_recursion(self):
        cases = {
            self.recursion: {'t': 5, 'nt': 3, 'pr': 7},
        }

        for path, info in cases.items():
            r_grammar = Grammar.build(readJson(path))
            r_grammar.removeLeftRecursion()

            self.assertEqual(len(r_grammar.terminals), info['t'], f"Unequal terminals count for '{path}'")
            self.assertEqual(len(r_grammar.nonterminals), info['nt'], f"Unequal nonterminals count for '{path}'")
            self.assertEqual(len(r_grammar.productions), info['pr'], f"Unequal productions count for '{path}'")

    def test_factorization(self):
        cases = {
            self.factorization: {'t': 6, 'nt': 3, 'pr': 5},
        }

        for path, info in cases.items():
            r_grammar = Grammar.build(readJson(path))
            r_grammar.leftFactorization()

            self.assertEqual(len(r_grammar.terminals), info['t'], f"Unequal terminals count for '{path}'")
            self.assertEqual(len(r_grammar.nonterminals), info['nt'], f"Unequal nonterminals count for '{path}'")
            self.assertEqual(len(r_grammar.productions), info['pr'], f"Unequal productions count for '{path}'")

    def test_reachable(self):
        cases = {
            self.reachable : {'t': 3, 'nt': 2, 'pr': 2},
        }

        for path, info in cases.items():
            r_grammar = Grammar.build(readJson(path))
            r_grammar.removeUnreachableDFS()

            self.assertEqual(len(r_grammar.terminals), info['t'], f"Unequal terminals count for '{path}'")
            self.assertEqual(len(r_grammar.nonterminals), info['nt'], f"Unequal nonterminals count for '{path}'")
            self.assertEqual(len(r_grammar.productions), info['pr'], f"Unequal productions count for '{path}'")

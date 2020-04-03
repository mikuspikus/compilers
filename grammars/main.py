from .grammar.grammar import Grammar
import json

def readJson(path: str) -> dict:
    with open(path) as file:
        result = json.load(file)

    return result

def _testRecursion():
    import os

    folder = 'grammar/testjson/'
    filename = folder + 'recursion.json'
    dirname = os.path.dirname(__file__)
    lr_path = os.path.join(dirname, filename)
    

    json = readJson(lr_path)

    grammar = Grammar.build(json)
    print(f'{lr_path} grammar', {'t' : len(grammar.terminals), 'nt' : len(grammar.nonterminals), 'pr' : len(grammar.productions)})
    grammar.removeLeftRecursion()
    print(f'{lr_path} clean grammar', {'t' : len(grammar.terminals), 'nt' : len(grammar.nonterminals), 'pr' : len(grammar.productions)})

    filename = folder + 'factorization.json'
    lf_path = os.path.join(dirname, filename)
    json = readJson(lf_path)
    lf_grammar = Grammar.build(json)

    print(f'{lf_path} grammar', {'t' : len(lf_grammar.terminals), 'nt' : len(lf_grammar.nonterminals), 'pr' : len(lf_grammar.productions)})
    lf_grammar.leftFactorization()
    print(f'{lf_path} cleaned grammar', {'t' : len(lf_grammar.terminals), 'nt' : len(lf_grammar.nonterminals), 'pr' : len(lf_grammar.productions)})

    filename = folder + 'reachable.json'
    r_path = os.path.join(dirname, filename)
    json = readJson(r_path)
    r_grammar = Grammar.build(json)

    print(f'{r_path} grammar', {'t' : len(r_grammar.terminals), 'nt' : len(r_grammar.nonterminals), 'pr' : len(r_grammar.productions)})
    new_r_grammar = r_grammar.removeUnreachableDFS()
    print(f'{r_path} cleaned grammar', {'t' : len(r_grammar.terminals), 'nt' : len(r_grammar.nonterminals), 'pr' : len(r_grammar.productions)})


if __name__ == "__main__":
    _testRecursion()

from grammar.grammar import Grammar
from jsonconverter.converter import JsonConvert
import json

def _from_json(path: str) -> dict:
    with open(path) as file:
        result = json.load(file)

    return result

def _testRecursion():
    import os
    filename = 'recursion.json'
    dirname = os.path.dirname(__file__)
    lr_path = os.path.join(dirname, filename)

    json = _from_json(lr_path)

    grammar = Grammar.build(json)

    grammar.removeLeftRecursion()
    grammar.clean()
    asJson = JsonConvert.toJSON(grammar)
    print(asJson)


    lf_path = os.path.join(dirname, 'factorization.json')
    json = _from_json(lf_path)
    lf_grammar = Grammar.build(json)
    lf_grammar.leftFactorization()
    asJson = JsonConvert.toJSON(lf_grammar)
    print(asJson)


if __name__ == "__main__":
    _testRecursion()

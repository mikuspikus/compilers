from grammar.grammar import Grammar
from jsonconverter.converter import JsonConvert
import json

def _from_json(path: str) -> dict:
    with open(path) as file:
        result = json.load(file)

    return result

def _testRecursion():
    import os
    filename = 'test.json'
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, filename)

    json = _from_json(path)

    grammar = Grammar.build(json)

    grammar.removeLeftRecursion()

    grammar.clean()

    asJson = JsonConvert.toJSON(grammar)
    print(asJson)


if __name__ == "__main__":
    _testRecursion()

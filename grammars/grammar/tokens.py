from collections import namedtuple
from jsonconverter.converter import JsonConvert
from typing import Union, List


ProductionSymbol = namedtuple('ProductionSymbol', ['index', 'value'])


@JsonConvert.register
class Terminal:
    # __slots__ = ('name', 'spell')

    def __init__(self, name: str = '', spell: str = ''):
        self.name = name
        self.spell = spell

    def __str__(self) -> str:
        return f"T <'{self.name}' [{self.spell}]>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def build(json: dict):
        assert set(('name', 'spell')) <= json.keys()

        return Terminal(name=json['name'], spell=json['spell'])


@JsonConvert.register
class NonTerminal:
    # __slots__ = ('name', )

    def __init__(self, name: str = ''):
        self.name = name

    def __str__(self) -> str:
        return f"NT <{self.name}>"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, value: Union[str, "Nonterminal"]):
        if isinstance(value, str):
            return self.name == value

        else:
            return self.name == value.name

    @staticmethod
    def build(json: dict):
        assert set(('name', )) <= json.keys()

        return NonTerminal(name=json['name'])


@JsonConvert.register
class StartSymbol:
    # __slots__ = ('name', )

    def __init__(self, name: str = ''):
        self.name = name

    def __str__(self) -> str:
        return f"Ssym <{self.name}>"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def build(json: dict):
        assert set(('name', )) <= json.keys()

        return StartSymbol(name=json['name'])


@JsonConvert.register
class ProductionElement:
    # __slots__ = ('name', 'is_terminal')

    def __init__(self, name: str = '', is_terminal: bool = False):
        self.name = name
        self.is_terminal = is_terminal

    def __str__(self) -> str:
        return f"PE <'{self.name}' [{self.is_terminal}]>"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, value: Union[NonTerminal, "ProductionElement"]):
        if isinstance(value, NonTerminal):
            return self.name == value.name

        else:
            return self.name == value.name and self.is_terminal == value.is_terminal

    @staticmethod
    def build(json: dict):
        assert set(('name', 'is_terminal')) <= json.keys()

        return ProductionElement(name=json['name'], is_terminal=json['is_terminal'])


@JsonConvert.register
class Production:
    # __slots__ = ('name', 'elements')

    def __init__(self, name: str = '', elements: List[ProductionElement] = None):
        self.name = name
        self.elements = elements if elements else []

    def __str__(self) -> str:
        return f"P <{self.name} [{len(self.elements)}]>"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, value):

        if isinstance(value, NonTerminal):
            return self.name == value.name

        else:
            return self.name == value.name and self.elements == value.elements

    def clean(self, epsilon: Terminal) -> None:
        self._removeEmpty(epsilon)

    def _removeEmpty(self, epsilon: Terminal) -> None:
        for element in self.elements:
            if element.name == epsilon.name and len(self.elements) > 1:
                self.elements.remove(element)

    def tupilize(self) -> List[ProductionSymbol]:
        return [ProductionSymbol(index, value.value) for index, value in enumerate(self.elements)]

    @staticmethod
    def build(json: dict):
        assert set(('name', 'elements')) <= json.keys()

        elements = [ProductionElement.build(
            el_json) for el_json in json['elements']]
        return Production(name=json['name'], elements=elements)

import json
from typing import List, FrozenSet, Union, Set
from .tokens import NonTerminal, Terminal, ProductionSymbol, Production, ProductionElement, StartSymbol
from jsonconverter.converter import JsonConvert


def _key(symbol: ProductionSymbol):
    return symbol.index

def _listize(cet: FrozenSet[ProductionSymbol], nonterminals: List["NonTerminal"]):
    symbols = list(cet)
    symbols.sort(key=_key)

    return [ProductionElement(symbol.value, not symbol.value in nonterminals) for symbol in symbols]

EMPTY = 'EMPTY'

@JsonConvert.register
class Grammar:
    # __slots__ = ('terminals', 'nonterminals', 'productions', 'startsymbol')

    def __init__(self, terminals: List[Terminal] = None, nonterminals: List[NonTerminal] = None, productions: List[Production] = None, startsymbol: StartSymbol = None):
        self.terminals = terminals if terminals else []
        self.nonterminals = nonterminals if nonterminals else []
        self.productions = productions if productions else []
        self.startsymbol = startsymbol if startsymbol else None

    @staticmethod
    def build(json: dict):
        assert set(('terminals', 'nonterminals', 'productions',
                    'startsymbol')) <= json.keys()

        terminals = [Terminal.build(t_json) for t_json in json['terminals']]
        nonterminals = [NonTerminal.build(nt_json)
                        for nt_json in json['nonterminals']]
        productions = [Production.build(p_json)
                       for p_json in json['productions']]
        startsymbol = StartSymbol.build(json['startsymbol'])

        return Grammar(terminals=terminals, nonterminals=nonterminals, productions=productions, startsymbol=startsymbol)

    def removeLeftRecursion(self) -> None:
        for i, a_i in enumerate(self.nonterminals):
            for a_j in self.nonterminals[:i]:
                productions = self._findProduction(a_i, a_j)
                left_productions = self._findProductionsByName(a_j)

                for production in productions:
                    self.productions.remove(production)

                    for left_production in left_productions:
                        self.productions.append(
                            self._createProduction(
                                production,
                                a_j,
                                left_production
                            )
                        )

                productions = self._findProduction(a_i, a_i)

                if productions:
                    left_productions = self._findProductionsByName(a_i)

                    self.nonterminals.append(
                        NonTerminal(name=f"{a_i.name}'"))

                    for production in left_productions:
                        if production not in productions:
                            production.elements.append(
                                ProductionElement(
                                    name=f"{a_i.name}'",
                                    is_terminal=False
                                )
                            )

                        else:
                            self.productions.remove(production)
                            self.productions.append(
                                self._createWithApostrophe(production, a_i))

                    self.productions.append(
                        Production(
                            name=f"{a_i.name}'",
                            elements=[ProductionElement(
                                name='e', is_terminal=True)]
                        )
                    )

        # self.clean()
    
    def _findEpsilon(self):
        epsilons = [terminal for terminal in self.terminals if terminal.spell == EMPTY]

        return epsilons[0]

    def clean(self):
        epsilon = self._findEpsilon()

        for production in self.productions:
            production.clean(epsilon)


    def _createWithApostrophe(self, production: Production, nonterminal=NonTerminal) -> Production:
        new_name = f"{nonterminal.name}'"
        new_production = Production(
            name=new_name, elements=production.elements)

        for element in new_production.elements:
            if element.name == nonterminal.name:
                new_production.elements.remove(element)

                new_production.elements.append(
                    ProductionElement(name=new_name, is_terminal=False)
                )

        return new_production

    def _createProduction(self, production: Production, r_nonterminal: NonTerminal, r_production: Production) -> Production:
        new_elements = []
        for element in production.elements:
            if element.name == r_nonterminal.name:
                new_elements.extend(r_production.elements)

            else:
                new_elements.append(element)

        return Production(name=production.name, elements=new_elements)

    def _findProduction(self, left: NonTerminal, right: NonTerminal) -> List[Production]:
        result = []

        buffer = ProductionElement(name=right.name, is_terminal=False)

        for production in self.productions:
            if production.name == left.name and production.elements[0] == buffer:
                result.append(production)

        return result

    def _findProductionsByName(self, left: NonTerminal) -> List[Production]:
        #result = [production for production in self.productions if production == left]

        result = []

        for production in self.productions:
            if production.name == left.name:
                result.append(production)

        return result

    def leftFactorization(self) -> None:
        for nonterminal in self.nonterminals.copy():
            productions = self._findProductionsByName(nonterminal)

            for production in productions.copy():
                buffer = ProductionElement(nonterminal.name, False)

                if buffer not in production.elements:
                    productions.remove(production)

            if not productions: continue

            alpha = frozenset(productions[0].tupilize())

            for production in productions:
                alpha = alpha.intersection(
                    frozenset(production.tupilize())
                )

            if not alpha:
                continue

            new_elements = _listize(alpha, self.nonterminals)
            new_nonterminal = f"{nonterminal.name}^"
            new_elements.append(ProductionElement(new_nonterminal, False))

            self.productions.append(
                Production(nonterminal.name, new_elements)
            )

            for production in productions:
                self.productions.remove(production)

                for new_element in new_elements[:-1]:
                    production.elements.remove(new_element)

                if not production.elements:
                    production.elements.append(
                        ProductionElement(self._findEpsilon().name, True)
                    )

                self.productions.append(
                    Production(
                        new_nonterminal,
                        production.elements
                    )
                )


            self.nonterminals.append(NonTerminal(new_nonterminal))

    def removeUnreachableDFS(self):
        reachable_nt_s = self._reachableNonTerminals()

        new_nt_s = [NonTerminal(nt) for nt in reachable_nt_s]
        new_production_s = [production for production in self.productions if production.name in reachable_nt_s]
        
        reachable_terminals = self._reachableTerminals(new_production_s)
        new_terminals = [t for t in self.terminals if t.name in reachable_terminals]

        return Grammar(
            terminals=new_terminals,
            nonterminals=new_nt_s,
            productions=new_production_s,
            startsymbol=self.startsymbol
        )

    def _reachableTerminals(self, r_productions: List[Production]) -> Set[str]:
        reachable_t_s = set()

        for production in r_productions:
            for element in production.elements:
                if element.is_terminal and element.name not in reachable_t_s:
                    reachable_t_s.add(element.name)

        return reachable_t_s

    def _reachableNonTerminals(self) -> Set[str]:
        reachable = set()

        def dfs(nonterminal: str) -> None:
            reachable.add(nonterminal)

            for rnt_element in filter(lambda pr : pr.name == nonterminal, self.productions):
                if rnt_element.name not in reachable:
                    dfs(rnt_element.name)

        dfs(self.startsymbol.name)

        return reachable

    def removeUnreachable(self):
        v = frozenset(self.startsymbol.name)

        nonterminals = set(map(lambda nt : nt.name, self.nonterminals))
        new_productions = []

        for nonterminal in self.nonterminals:
            productions = filter(lambda p : p.name == nonterminal.name, self.productions)
            new_productions += productions

            reachable = []
            for production in productions:
                reachable += [element.name for element in production.elements if element.name in nonterminals]

            new_v = frozenset(reachable + list(v))

            # new_v is subset of v
            if new_v <= v:
                v = new_v

            else:
                break
        

        return Grammar(
            terminals = self.terminals,
            nonterminals=[NonTerminal(nt_name) for nt_name in v],
            productions=new_productions,
            startsymbol=self.startsymbol
        )
        


            
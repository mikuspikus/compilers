def remove_recursion(self):
    for i in range(0, len(self.nonterminals)):
        for j in range(0, i):
            prods = self.__findProduction(
                self.nonterminals[i], self.nonterminals[j])
            left_prods = self.__findProductionsByLeft(self.nonterminals[j])
            for pr in prods:
                self.productions.remove(pr)
                for lpr in left_prods:
                    self.productions.append(self.__createProduction(
                        pr, self.nonterminals[j], lpr))

        prods = self.__findProduction(
            self.nonterminals[i], self.nonterminals[i])
        if prods:
            left_prods = self.__findProductionsByLeft(self.nonterminals[i])
            self.nonterminals.append(f'{self.nonterminals[i]}\'')
            for pr in left_prods:
                if pr not in prods:
                    pr['right'].append(
                        {
                            'isTerminal': 'False',
                            'name': f'{self.nonterminals[i]}\''
                        })
                else:
                    self.productions.remove(pr)
                    prod = {
                        'left': f'{self.nonterminals[i]}\'', 'right': pr['right']}
                    for r in pr['right']:
                        if r['name'] == self.nonterminals[i]:
                            prod['right'].remove(r)
                            prod['right'].append(
                                {
                                    'isTerminal': 'False',
                                    'name': f'{self.nonterminals[i]}\''
                                })

                    self.productions.append(prod)

            self.productions.append({
                'left': f'{self.nonterminals[i]}\'',
                'right': [
                    {
                        'isTerminal': 'True',
                        'name': 'e'
                    }
                ]
            })

from nfaregexp.tokenizer import Character, Concatenation, Disjunction, Operator, Variable
from typing import Union, Tuple

import copy

class ExpressionTreeNode:

    def __init__(self, value: Union[Character, Concatenation, Disjunction, Operator, Variable]):
        self.value = value
        self.left = None
        self.right = None

    def __str__(self) -> str:
        left, center, right = 'None', 'None', 'None'

        if self.left:
            left = str(self.left)

        center = self.value

        if right:
            right = str(self.right)

        return f'Node ({center}) <{left}, {right}>'


    def __repr__(self):
        return str(self)

    def __copy(self):
        new = ExpressionTreeNode(self.value)

        if self.left:
            new.left = self.left.__copy()

        if self.right:
            new.right = self.right.__copy()

        return new

    def __is_character(self) -> bool:
        return isinstance(self.value, Character)

    def __is_variable(self) -> bool:
        return isinstance(self.value, Variable)

    def __is_operator(self) -> bool:
        return isinstance(self.value, Operator)

    def __is_concatenation(self) -> bool:
        return isinstance(self.value, Concatenation)

    def __is_disjunction(self) -> bool:
        return isinstance(self.value, Disjunction)

    def __find_var_operator(self, variable: str) -> Union[None, Tuple[Concatenation, Union[Concatenation, Disjunction, Operator, Character, Variable]]]:
        #if isinstance(self.value, Concatenation):
        if self.left  and self.left.__is_variable() and self.left.value == variable:
            return self, self.right

        elif self.right and self.right.__is_variable() and self.right.value == variable:
            return self, self.left

        buf = None
        if self.left: 
            buf = self.left.__find_var_operator(variable)

        if not buf and self.right:
            buf = self.right.__find_var_operator(variable)

        return buf

    def __find_parent(self, node):
        if self.left is node or self.right is node:
            return self

        buf = None

        if self.left is not None:
            buf = self.left.__find_parent(node)
        if buf is None and self.right is not None:
            buf = self.right.__find_parent(node)

        return buf

    def replace_var_all(self, variable: str, replace_node):
        while self.find_var(variable):
            operator_node, var_free_operand_node = self.__find_var_operator(variable)

            if operator_node.left is not var_free_operand_node:
                operator_node.left = replace_node

            else:
                operator_node.right = replace_node

    def find_var(self, variable: str):
        smth = self.__find_var_operator(variable)

        if smth is None: return None

        operator_node, operand_node = smth
        return operator_node.left if operator_node.right is operand_node else operator_node.right

    def evaluate_var_copy(self, variable: str):
        copy_ = self.__copy()

        smth = copy_.__find_var_operator(variable)
        if not smth: return copy_

        operator_node, var_free_operand_node = smth
        copy_.__delete_node(operator_node)

        new_tree = ExpressionTreeNode(Concatenation)
        star_node = ExpressionTreeNode(Operator('*'))
        star_node.left = var_free_operand_node

        new_tree.left, new_tree.right = star_node, copy_

        return new_tree

    def evaluate_var(self, variable: str):
        smth = self.__find_var_operator(variable)

        # variable is absent
        if smth is None: return self

        operator_node, variable_free_operand_node = smth

        self.__delete_node(operator_node)
        
        tree = ExpressionTreeNode(Concatenation)
        
        star_node = ExpressionTreeNode(Operator('*'))
        star_node.left = variable_free_operand_node
        tree.left = star_node
        tree.right = self
        # self = tree
        
        return tree

    def insert_node(self, replace_node, insert_node) -> bool:
        if self is replace_node:
            self = insert_node
            return True
        
        buf = False
        if self.left is not None:
            buf = self.left.insert_node(replace_node, insert_node)
        
        if buf == False and self.right is not None:
            buf = self.right.insert_node(replace_node, insert_node)

        return buf


    def __delete_node(self, node):
        parent = self.__find_parent(node)

        if parent is None:  return

        parent_parent = self.__find_parent(parent)

        replace = parent.right if parent.left is node else parent.left
        
        if parent_parent is not None:
            if parent_parent.left is parent:
                parent_parent.left = replace

            else:
                parent_parent.right = replace

        else:
            self.left = replace.left
            self.right = replace.right
            self.value = replace.value

    def inorder(self) -> str:
        left, center, right = '', '', ''
        if self.left is not None: left = self.left.inorder()
        
        center = str(self.value)

        if self.right is not None: right = self.right.inorder()

        return left + '|' + center + '|' + right

    def to_postfix(self) -> list:
        stack = []
        self.__to_postfix(stack)

        return stack

    def __to_postfix(self, stack: list) -> None:
        if self.left:
            self.left.__to_postfix(stack)

        if self.right:
            self.right.__to_postfix(stack)

        stack.append(self.value)

    @staticmethod
    def build(postfix_expression: list):
        stack = []
        for item in postfix_expression:

            if isinstance(item, (Character, Variable)):
                node = ExpressionTreeNode(item)
                stack.append(node)

            elif isinstance(item, (Concatenation, Disjunction)):
                node = ExpressionTreeNode(item)
                right = stack.pop()
                left = stack.pop()

                node.left, node.right = left, right

                stack.append(node)

            elif isinstance(item, Operator):
                node = ExpressionTreeNode(item)
                operand = stack.pop()

                node.left = operand

                stack.append(node)

        root = stack.pop()
        return root

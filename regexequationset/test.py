from regexequations import __equation_to_postfix, __replace_variable
from expressiontree import ExpressionTreeNode

if __name__ == "__main__":
    delta = set(('A', 'B', 'S'))

    equation = __equation_to_postfix(delta, '0S|B|e')
    print(equation)

    root = ExpressionTreeNode.build(equation)
    root.inorder()

    eval_exp = root.evaluate_var('S')

    variable_expression = __equation_to_postfix(delta, '01*0A')
    print(variable_expression)

    replaced = __replace_variable(equation, 'S', variable_expression)
    print(replaced)

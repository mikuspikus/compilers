import os
from cparser import c_parser, c_ast
from cparser.plyparser import ParseError, Coord
import sys

class stt():
    __slots__ = (
        'isFuncDecl',
        'isFuncDef',
        'isDecl',
        'isId',
        'isBinaryOp',
        'isAssignment',
        'isFuncCall',
        'isCompound')
    
    def __init__(self):
        self.isFuncDecl = False
        self.isFuncDef = False
        self.isDecl = False
        self.isId = False
        self.isBinaryOp = False
        self.isAssignment = False
        self.isFuncCall = False
        self.isCompound = False

global_scope = []
compound_scope = []
def check_variable_scopes(root, state):
    global global_scope, compound_scope

    if type(root) == c_ast.FuncDef:
        state.isFuncDef = True
        new_scope = global_scope[:]
        global_scope[:] = []
        check_children_scopes(root, state)
        state.isFuncDef = False
        global_scope = new_scope[:]
    
    elif type(root) == c_ast.Compound:
        if state.isFuncDef:
            state.isFuncDef = False
            check_children_scopes(root, state)
        
        else:
            state.isCompound = True
            
            old_global = global_scope[:]
            old_compound = compound_scope[:]

            for item in compound_scope:
                global_scope.append(item)

            compound_scope[:] = []
            check_children_scopes(root, state)

            global_scope = old_global[:]
            compound_scope = old_compound[:]

        state.isCompound = False

    elif type(root) == c_ast.Decl:
        state.isDecl = True
        #state.variable = root.name

        #if state.isFuncDef:
        #    define(global_scope, root.name)
            #state.variable = root.name
        if state.isCompound:
            if is_defined_local(compound_scope, root.name):
                error("redeclaration of \'" + str(root.name) + "\'", root.coord)

            else:
                define(compound_scope, root.name)

        else:
            if is_defined_local(global_scope, root.name):
                error("redeclaration of \'" + str(root.name) + "\'", root.coord)

            else:
                define(global_scope, root.name)
            #state.variable = root.name

            #if state.isParamList:
            #    initialize(global_scope, root.name)
            
        check_children_scopes(root, state)
        state.isDecl = False

    elif type(root) == c_ast.ID:
        state.isId = True

        if root.name == 'NULL':
            pass

        elif state.isCompound:
            if not (is_defined_local(global_scope, root.name) or is_defined_local(compound_scope, root.name)):
                error("undeclared \'" + str(root.name) + "\'", root.coord)

        elif not is_defined_local(global_scope, root.name):
            error("undeclared \'" + str(root.name) + "\'", root.coord)

        state.isId = False

    elif type(root) == c_ast.BinaryOp:
        state.isBinaryOp = True
        check_children_scopes(root, state)
        state.isBinaryOp = False
    
    elif type(root) == c_ast.Assignment:
        state.isAssignment = True
        check_children_scopes(root, state)
        state.isAssignment = False

    else:
        check_children_scopes(root, state)


def check_children_scopes(root, state):
    for child in root:
        check_variable_scopes(child, state)

def define(scope, var_name):
    scope.insert(0, var_name)

def is_defined_local(scope, var_name):
    for var in scope:
        if var_name == var:
            return True
    
    return False

def error(msg, coord):
    raise ParseError('{}: {}'.format(coord, msg))

if __name__ == '__main__':
    file_name = 'example.c'
    path = os.path.join(os.path.dirname(__file__), file_name)

    code = '''typedef int Node, Hash;
unsigned int i;
void HashPrint(Hash* hash, void (*PrintFunc)(char*, char*))
{
    unsigned int i;
    if (i)
    {
        int c = 0;
        PrintFunc(i, c);
        if (c)
        {
            float c;
        }
    }
    float c;
    float i;
    if (hash == NULL || hash->heads == NULL)
        return;
    for (i = 0; i < hash->table_size; ++i)
    {
        Node* temp = hash->heads[i];
        while (temp != NULL)
        {
            PrintFunc(temp->entry->key, temp->entry->value);
            temp = temp->next;
        }
    }
}'''

    #with open(path, 'r') as f:
    #    code = f.read()

    cparser = c_parser.CParser()
    ast = cparser.parse(code, filename='<main>')
    ast.show()

    sys.setrecursionlimit(1000)
    state = stt()
    check_children_scopes(ast, state)

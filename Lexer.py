from ply import lex
from ply import yacc

# List of token names.   This is always required
tokens = (
    # Types
    'INT',
    'FLOAT',
    'STRING',
    'ID',
    # Keywords
    'LET',
    'IF',
    'ELSE',
    'OUTPUT',
    'INPUT',
    'FUNC',
    # Equals
    'EQ',
    'DBEQ',
    'EXEQ',
    # Operations
    'PLUS',
    'MINUS',
    'MULTIPLY',
    'DIVIDE',
    'INTDIV',
    # Brackets
    'LPAREN',
    'RPAREN',
    'LCURLY',
    'RCURLY',
    # Colons
    'COLON',
    'COMMA',
    # Signs
    'DBLT',
    'LT',
    'GT',
    'EX',
    # Others
    'LINE',
)

##########
# LEXER #
##########

# Regular expression rules for simple tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_INTDIV = r'//'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LCURLY = r'{'
t_RCURLY = r'}'
t_DBEQ = r'=='
t_EXEQ = r'!='
t_EQ = r'\='
t_COLON = r':'
t_COMMA = r","
t_LT = r'<'
t_GT = r'>'
t_DBLT = r'<<'
t_EX = r'!'
t_LINE = r'\|'


def t_FLOAT(t):
    r"""\d+\.\d+"""
    t.value = float(t.value)
    return t


def t_INT(t):
    r"""\d+"""
    t.value = int(t.value)
    return t


def t_STRING(t):
    r""""[a-zA-Z_ 0-9!?]*\""""
    t.value = str(t.value)[1:-1]
    return t


def t_LET(t):
    r"""let"""
    t.type = "LET"
    return t


def t_IF(t):
    r"""if"""
    t.type = "IF"
    return t


def t_ELSE(t):
    r"""else"""
    t.type = "ELSE"
    return t


def t_FUNC(t):
    r"""func"""
    t.type = "FUNC"
    return t


def t_OUTPUT(t):
    r"""cout"""
    t.type = 'OUTPUT'
    return t


def t_INPUT(t):
    r"""cin"""
    t.type = 'INPUT'
    return t


def t_ID(t):
    r"""[a-zA-Z_][a-zA-Z_0-9]*"""
    t.type = "ID"
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()

precedence = (
    ('left', 'LPAREN', 'RPAREN'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE', 'INTDIV'),
    ('left', 'DBEQ', 'EXEQ', 'LT', 'GT'),
    ('left', 'EX'),
)


##########
# PARSER #
##########


def p_error(p):
    print("Syntax Error: '%s'" % p)
    try:
        p.lexer.skip(1)
    except:
        pass


def p_calc(p):
    """
    calc : expr
         | var_assign
         | func_assign
         | cout
         | empty
    """
    # run(("calc", p[1]))
    p[0] = ("calc", p[1])


def p_expr(p):
    """
    expr : LPAREN expr PLUS expr RPAREN
         | LPAREN expr MINUS expr RPAREN
         | LPAREN expr MULTIPLY expr RPAREN
         | LPAREN expr DIVIDE expr RPAREN
         | LPAREN expr INTDIV expr RPAREN

         | LPAREN expr DBEQ expr RPAREN
         | LPAREN expr EXEQ expr RPAREN
         | LPAREN expr LT expr RPAREN
         | LPAREN expr GT expr RPAREN
         | LPAREN EX expr RPAREN
    """
    if len(p) == 6:
        p[0] = (p[3], p[2], p[4])
    else:
        p[0] = (p[2], ("num", 0), p[3])


def p_multi_calc(p):
    """
    multi_calc : multi_calc LINE calc
               | calc
    """
    if len(p) == 4:
        p[0] = ("multi", p[1], p[3])
    else:
        p[0] = ("single", p[1])


def p_bin_op(p):
    """
    expr : expr MULTIPLY expr
         | expr DIVIDE expr
         | expr INTDIV expr
         | expr PLUS expr
         | expr MINUS expr

         | expr DBEQ expr
         | expr EXEQ expr
         | expr LT expr
         | expr GT expr
         | EX expr
    """
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = (p[1], ("num", 0), p[2])


def p_unary_op(p):
    """
    expr : PLUS expr
         | MINUS expr
    """
    p[0] = ("unary", p[1], p[2])


def p_factor(p):
    """
    expr : INT
         | FLOAT
    """
    p[0] = ("num", p[1])


def p_multi_expr(p):
    """
    multi_expr : multi_expr COMMA expr
               | expr
               | empty
    """
    if len(p) == 4:
        p[0] = ("multi_expr", p[1], p[3])
    elif p[1] is None:
        p[0] = ()
    else:
        p[0] = ("single_expr", p[1])


def p_string(p):
    """
    expr : STRING
    """
    p[0] = ("str", p[1])


def p_multi_id(p):
    """
    multi_id : multi_id COMMA ID
             | ID
             | empty
    """
    if len(p) == 4:
        p[0] = ("multi_id", p[1], p[3])
    elif p[1] is None:
        p[0] = ()
    else:
        p[0] = ("single_id", p[1])


def p_if_else(p):
    """
    calc : IF LPAREN expr RPAREN LCURLY multi_calc ELSE multi_calc RCURLY
    """
    p[0] = ("flow_else", p[3], p[6], p[8])


def p_if(p):
    """
    calc : IF LPAREN expr RPAREN LCURLY multi_calc RCURLY
    """
    p[0] = ("flow_if", p[3], p[6])


def p_var_assign(p):
    """
    var_assign : LET ID EQ expr
    """
    p[0] = ("var_assign", p[2], p[4])


def p_func_assign(p):
    """
    func_assign : FUNC ID LPAREN multi_id RPAREN LCURLY multi_calc RCURLY
    """
    p[0] = ("func_assign", p[2], p[4], p[7])


def p_cout(p):
    """
    cout : OUTPUT DBLT expr
    """
    p[0] = ("cout", p[3])


def p_cin(p):
    """
    expr : INPUT
    var_assign : ID DBLT INPUT
    """
    if len(p) == 2:
        p[0] = ("cin", None)
    else:
        p[0] = ("var_assign", p[1], ("cin", None))


def p_func_access(p):
    """
    calc : ID LPAREN multi_expr RPAREN
    """
    p[0] = ("func_access", p[1], p[3])


def p_var_access(p):
    """
    expr : ID
    """
    p[0] = ("var_access", p[1])


def p_empty(_):
    """empty :"""
    pass


parser = yacc.yacc()

############
# Compiler #
############
global_var_tree = {}


def check(p):
    if p[1]:
        return p[1]
    return p[0]


def bin_op(p, var_tree):
    op = p[0]
    left = check(run(p[1], var_tree=var_tree))
    if left is None:
        return None, left
    right = check(run(p[2], var_tree=var_tree))
    if right is None:
        return None, right

    if op == "+":
        return (left + right), None
    if op == "-":
        return (left - right), None
    if op == "*":
        return (left * right), None
    if op == "/":
        if right == 0:
            return None, "ZeroDivisionError: Cannot divide by 0"
        return (left / right), None
    if op == "//":
        if right == 0:
            return None, "ZeroDivisionError: Cannot divide by 0"
        return (left // right), None
    if op == "==":
        return int(left == right), None
    if op == "!=":
        return int(left != right), None
    if op == ">":
        return int(left > right), None
    if op == "<":
        return int(left < right), None
    if op == "!":
        return int(not right), None

    return op, None


def run(p, var_tree=None):
    if var_tree is None:
        var_tree = global_var_tree
    if p[0] == "calc":
        try:
            res, err = run(p[1], var_tree=var_tree)
            if err:
                print(err)
            elif res is not None:
                if res is not True:
                    print(res)
            else:
                pass
        except:
            pass
    # Multi
    if p[0] == "multi":
        r = run(p[1], var_tree=var_tree)
        if r[1]:
            return None, r[1]
        r = run(p[2], var_tree=var_tree)
        if r[1]:
            return None, r[1]
        return True, None
    if p[0] == "single":
        r = run(p[1], var_tree=var_tree)
        if r[1]:
            return None, r[1]
        return True, None

    # Types
    if p[0] == "num":
        return p[1], None
    if p[0] == "str":
        return p[1], None
    if p[0] == "unary":
        if p[1] == "+":
            return bin_op(("*", p[2], ("num", 1)), var_tree=var_tree)
        if p[1] == "-":
            return bin_op(("*", p[2], ("num", -1)), var_tree=var_tree)

    # Operators
    if p[0] in ["+", "-", "*", "/", "//", "==", "!=", "<", ">", "!"]:
        return bin_op(p, var_tree=var_tree)

    # Var
    def sep(ids):
        lst = []
        if len(ids) == 0:
            return lst
        if ids[0].startswith("multi"):
            left = ids[1]
            right = ids[2]
            lst.append(right)
            for s in sep(left):
                lst.append(s)
        else:
            lst.append(ids[1])
        return lst

    if p[0] == "var_access":
        v_name = p[1]
        if v_name in var_tree:
            r = var_tree[v_name]
            if r[0] == "var":
                return r[1], None
            else:
                return None, "accessing a function"
        else:
            return None, f"NameError: {v_name} is not defined"

    if p[0] == "func_access":
        local_tree = global_var_tree.copy()
        f_name = p[1]
        if f_name in var_tree:
            r = var_tree[f_name]
            if r[0] == "func":
                local_vars = sep(p[2])
                body = r[2]
                if len(local_vars) != len(r[1]):
                    return None, "ArgumentError: too many or too less arguments"
                for i, v in enumerate(local_vars):
                    x = run(v, var_tree=local_tree)
                    if x[1]:
                        return None, x[1]
                    local_tree[r[1][i]] = ("var", x[0])
                res = run(body, var_tree=local_tree)
                if res[1]:
                    return None, res[1]
                return True, None
            else:
                return None, "accessing a var"
        else:
            return None, f"NameError: {f_name} is not defined"

    if p[0] == "var_assign":
        r = run(p[2], var_tree=var_tree)
        if r[1]:
            return None, r[1]
        var_tree[p[1]] = ("var", r[0])
        return True, None

    if p[0] == "func_assign":
        var_tree[p[1]] = ("func", sep(p[2]), p[3])
        return True, None

    # Flow
    if p[0].startswith("flow"):
        cond = p[1]
        do = p[2]
        r = run(cond, var_tree=var_tree)
        if r[1]:
            return None, r[1]
        if r[0] == 1:
            r = run(do, var_tree=var_tree)
            if r[1]:
                return None, r[1]
        else:
            if p[0].endswith("else"):
                r = run(p[3], var_tree=var_tree)
                if r[1]:
                    return None, r[1]
            # return r[0], None
        return True, None

    # IO
    if p[0] == 'cout':
        r = run(p[1], var_tree=var_tree)
        if r[1]:
            return None, r[1]
        print(r[0])
        return None, None

    if p[0] == 'cin':
        r = ('num', int(input()))
        r = run(r, var_tree=var_tree)
        if r[1]:
            return None, r[1]
        return r[0], None

    # Else
    return None, None


# Test it output
def test(data):
    p = parser.parse(data)
    return run(p)


if __name__ == "__main__":
    # Build the lexer and try it out
    test("let a = 1")  # Test it
    test("a")

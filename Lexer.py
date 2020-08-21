from ply import lex
from ply import yacc

# List of token names.   This is always required
tokens = (
    # Types
    'INT',
    'FLOAT',
    'ID',
    # Keywords
    'LET',
    'IF',
    'OUTPUT',
    'INPUT',
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
    # Colons
    'SEMI',
    # Signs
    'DBLT',
    'LT',
    'GT',
    'EX',
)

# Regular expression rules for simple tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_INTDIV = r'//'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_DBEQ = r'=='
t_EXEQ = r'!='
t_EQ = r'\='
t_SEMI = r':'
t_LT = r'<'
t_GT = r'>'
t_DBLT = r'<<'
t_EX = r'!'


# A regular expression rule with some action code
# Note addition of self parameter since we're in a class

##########
# LEXER #
##########

def t_FLOAT(t):
    r"""\d+\.\d+"""
    t.value = float(t.value)
    return t


def t_INT(t):
    r"""\d+"""
    t.value = int(t.value)
    return t


def t_LET(t):
    r"""let"""
    t.type = "LET"
    return t


def t_IF(t):
    r"""if"""
    t.type = "IF"
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
    ('left', 'EX')
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
         | cout
    """
    try:
        res, err = run(p[1])
        if err:
            print(err)
        elif res is not None:
            if res is not True:
                print(res)

        else:
            pass
    except:
        pass


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


def p_flow(p):
    """
    cout : IF LPAREN expr RPAREN SEMI cout
    """
    p[0] = ("flow", p[3], p[6])


def p_var_assign(p):
    """
    var_assign : LET ID EQ expr
    """
    p[0] = ("var_assign", p[2], p[4])


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


def p_var_access(p):
    """
    expr : ID
    """
    p[0] = ("var_access", p[1])


parser = yacc.yacc()

############
# Compiler #
############
var_tree = {}


def check(p):
    if p[1]:
        return p[1]
    return p[0]


def bin_op(p):
    op = p[0]
    left = check(run(p[1]))
    if left is None:
        return None, left
    right = check(run(p[2]))
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


def run(p):
    # Types
    if p[0] == "num":
        return p[1], None
    if p[0] == "unary":
        if p[1] == "+":
            return bin_op(("*", p[2], ("num", 1)))
        if p[1] == "-":
            return bin_op(("*", p[2], ("num", -1)))
    # Operators
    if p[0] in ["+", "-", "*", "/", "//", "==", "!=", "<", ">", "!"]:
        return bin_op(p)

    # Var
    if p[0] == "var_access":
        v_name = p[1]
        if v_name in var_tree:
            r = var_tree[v_name]
            return r, None
        else:
            return None, f"NameError: {v_name} is not defined"
    if p[0] == "var_assign":
        r = run(p[2])
        if r[1]:
            return None, r[1]
        var_tree[p[1]] = r[0]
        return True, None

    # Flow
    if p[0] == "flow":
        cond = p[1]
        do = p[2]
        r = run(cond)
        if r[1]:
            return None, r[1]
        if r[0] == 1:
            r = run(do)
            if r[1]:
                return None, r[1]
            # return r[0], None
        return True, None

    # IO
    if p[0] == 'cout':
        r = run(p[1])
        if r[1]:
            return None, r[1]
        print(r[0])
        return None, None

    if p[0] == 'cin':
        r = ('num', int(input()))
        r = run(r)
        if r[1]:
            return None, r[1]
        return r[0], None

    # Else
    return None, None


# Test it output
def test(data):
    parser.parse(data)


if __name__ == "__main__":
    # Build the lexer and try it out
    test("let a = 1")  # Test it
    test("a")

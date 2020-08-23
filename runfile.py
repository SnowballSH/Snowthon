import Lexer


def run(filename):
    with open(filename, 'r') as f:
        code = f.read().split(";")
        for c in code:
            c = c.strip()
            if c != "" and not c.startswith("#"):
                a = Lexer.test(c)
                if a[1]:
                    print(a[1])


run("test.snow")

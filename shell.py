import Lexer

prefix = "Snow> "

run = True
while run:
    try:
        code = input(prefix)
    except EOFError:
        run = False
        continue

    if len(code) > 0:
        Lexer.test(code)  # Test it

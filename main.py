from vm import interpret
from parsing import parse
from tokenization import tokenize

def repl():
    try:
        while True:
            s = input("> ")
            print(interpret(parse(tokenize(s))))

    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    repl()
from vm import interpret
from parsing import parse
from tokenization import tokenize

def repl():
    try:
        while True:
            s = input("> ")
            interpret(parse(tokenize(s)))
    except KeyboardInterrupt:
        return

def run_file(file_path):
    with open(filePath) as file:
        try:
            interpret(parse(tokenize(file.read())))
        except RuntimeError as e:
            print("Runtime error:", e)

if __name__ == '__main__':
    filePath = 'test-scripts/test.txt'
    # filePath = None

    if filePath != None:
        run_file(filePath)
    else:
        repl()
from vm import VM
from parsing import parse
from tokenization import tokenize
import sys

def run_file(filePath):
    try:
        with open(filePath) as file:
            VM(parse(tokenize(file.read()))).run()
    except FileNotFoundError:
        print(f"Could not open file `{filePath}`.")

def usage():
    print('Usage: interpreter.py <filename>')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
        sys.exit(0)
    filePath = sys.argv[1]
    if filePath != None:
        run_file(filePath)

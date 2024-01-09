from vm import VM
from parsing import parse
from tokenization import tokenize

def run_file(file_path):
    with open(filePath) as file:
        VM(parse(tokenize(file.read()))).run()

if __name__ == '__main__':
    filePath = 'test-scripts/test.txt'
    if filePath != None:
        run_file(filePath)
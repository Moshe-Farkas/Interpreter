from vm import VM
from parsing import parse
from tokenization import tokenize


import time

def run_file(file_path):
    with open(filePath) as file:
        VM(parse(tokenize(file.read()))).run()

if __name__ == '__main__':
    filePath = 'test-scripts/test.txt'

    # UP = '\033[3A'
    # CLEAR = '\x1b[2K'
    # mat = [['.','.','.','.',], ['.','.','.','.',], ['.','.','.','.',]]
    # for i in range(3):
    #     mat[i][0] = '?'
    #     for row in mat:
    #         print(row)
    #     print(UP, end=CLEAR)
    #     time.sleep(1)

    if filePath != None:
        run_file(filePath)
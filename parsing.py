from instructions import OpCode
from tokenization import Tokens
import sys

class _Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.index = 0
        self.code = []
    
    def emit_op(self, op):
        self.code.append(op)

    def at_end(self):
        return self.match(Tokens.EOF)

    def parse(self):
        while not self.at_end():
            self.statement()

    def statement(self):
        if self.match(Tokens.IF):
            self.if_statement()
        elif self.match(Tokens.PRINT):
            self.expression()
            self.emit_op(OpCode.PRINT)

        else:
            print("Unexpected statement type.", file=sys.stderr)
            sys.exit(0)
    
    def if_statement(self):
        self.expression()
        
        self.emit_op(OpCode.JUMP_FALSE)
        self.emit_op(-1)        # placeholder offset
        start_index = len(self.code)

        if self.match(Tokens.ARROW):
            self.statement()
            self.back_patch(start_index)

    def patch_loop(self, condition_index):
        # need to patch the offset after jump to point to the start of the condition
        
        end_index = len(self.code)
        self.code[end_index - (end_index - condition_index) - 1] = -(end_index - condition_index)
            
    def back_patch(self, start_index):
        end_index = len(self.code)
        self.code[end_index - (end_index - start_index) - 1] = end_index - start_index

    def match(self, *args):
        if self.index >= len(self.tokens):
            return False
        for arg in args:
            if self.tokens[self.index] == arg:
                self.index += 1
                return True
        return False

    def expression(self):
        self.Or()
    
    def Or(self):
        self.And()
        while self.match(Tokens.OR):
            self.And()
            self.emit_op(OpCode.OR)

    def And(self):
        self.equality()
        while self.match(Tokens.AND):
            self.equality()
            self.emit_op(OpCode.AND)
    
    def equality(self):
        self.comparision()
        while self.match(Tokens.EQUAL_EQUAL, Tokens.NOT_EQUAL):
            operator = self.tokens[self.index - 1]
            self.comparision()
            op = None
            match operator:
                case Tokens.EQUAL_EQUAL:
                    op = OpCode.EQUAL_EQUAL
                case Tokens.NOT_EQUAL:
                    op = OpCode.NOT_EQUAL
            self.emit_op(op)
    
    def comparision(self):
        self.term()
        while self.match(Tokens.GREATER, Tokens.GREATER_EQUAL,
                         Tokens.LESS, Tokens.LESS_EQUAL):
            operator = self.tokens[self.index - 1]
            self.term()
            op = None
            match operator:
                case Tokens.GREATER:
                    op = OpCode.GREATER
                case Tokens.GREATER_EQUAL:
                    op = OpCode.GREATER_EQUAL
                case Tokens.LESS:
                    op = OpCode.LESS
                case Tokens.LESS_EQUAL:
                    op = OpCode.LESS_EQUAL

            self.emit_op(op)
    
    def term(self):
        self.factor()
        while self.match(Tokens.PLUS, Tokens.MINUS):
            operator = self.tokens[self.index - 1]
            self.factor()

            op = None
            match operator:
                case Tokens.PLUS: 
                    op = OpCode.ADD
                case Tokens.MINUS: 
                    op = OpCode.SUB
            
            self.emit_op(op)
        
    def factor(self):
        self.unary()
        while self.match(Tokens.STAR, Tokens.SLASH, Tokens.PERCENT):
            operator = self.tokens[self.index - 1]
            self.unary()
            op = None
            match operator:
                case Tokens.SLASH:
                    op = OpCode.DIV
                case Tokens.STAR:
                    op = OpCode.MUL
                case Tokens.PERCENT:
                    op = OpCode.MODULO

            self.emit_op(op)
    
    def unary(self):
        while self.match(Tokens.MINUS):
            operator = self.tokens[self.index - 1]
            self.unary()
            op = None
            match operator:
                case Tokens.MINUS:
                    op = OpCode.NEGATION

            self.emit_op(op)
            return
        self.primary()
            
    def primary(self):
        if self.match(Tokens.LEFT_PAREN):
            self.expression()
            self.index += 1
            # self.consume(')', "Expect ')' after grouping.")
        if self.index >= len(self.tokens):
            return
        
        if self.match(Tokens.FALSE):
            self.emit_op(OpCode.FALSE)
        elif self.match(Tokens.TRUE):
            self.emit_op(OpCode.TRUE)
        elif isinstance(self.tokens[self.index], float):
            self.emit_op(OpCode.NUM)
            self.emit_op(self.tokens[self.index])
            self.index += 1

        else:
            print('Expected somthing.')
    
    def print_code(self):
        for op in self.code:
            print(op)


def parse(tokens: list):
    parser = _Parser(tokens)
    parser.parse()

    # parser.print_code()
    # print('*' * 50)
    # print('\n')

    return parser.code

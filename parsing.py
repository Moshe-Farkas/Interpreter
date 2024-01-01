from instructions import OpCode
from tokenization import Tokens

class _Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.index = 0
        self.code = []
    
    def emit_op(self, op):
        self.code.append(op)

    def parse(self):
        self.expression()

    def match(self, *args):
        if self.index >= len(self.tokens):
            return False
        for arg in args:
            if self.tokens[self.index] == arg:
                self.index += 1
                return True
        return False

    def expression(self):
        self.term()
    
    def term(self):
        self.factor()
        while self.match(Tokens.PLUS, Tokens.MINUS):
            operator = self.tokens[self.index - 1]
            self.factor()

            op = None
            match operator:
                case Tokens.PLUS: 
                    op = OpCode.OP_ADD
                case Tokens.MINUS: 
                    op = OpCode.OP_SUB
            
            self.emit_op(op)
        
    def factor(self):
        self.unary()
        while self.match(Tokens.STAR, Tokens.SLASH, Tokens.PERCENT):
            operator = self.tokens[self.index - 1]
            self.unary()
            op = None
            match operator:
                case Tokens.SLASH:
                    op = OpCode.OP_DIV
                case Tokens.STAR:
                    op = OpCode.OP_MUL
                case Tokens.PERCENT:
                    op = OpCode.OP_MODULO

            self.emit_op(op)
    
    def unary(self):
        while self.match(Tokens.MINUS):
            operator = self.tokens[self.index - 1]
            self.unary()
            op = None
            match operator:
                case Tokens.MINUS:
                    op = OpCode.OP_NEGATION

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

        if isinstance(self.tokens[self.index], float):
            self.emit_op(OpCode.OP_NUM)
            self.emit_op(self.tokens[self.index])
            self.index += 1


def parse(tokens: list):
    parser = _Parser(tokens)
    parser.parse()
    return parser.code

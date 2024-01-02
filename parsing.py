from instructions import OpCode
from tokenization import TokenType
import sys

class _Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.index = 0
        self.code = []
    
    def emit_op(self, op):
        self.code.append(op)

    def at_end(self):
        return self.match(TokenType.EOF)
    
    def check(self, tok_type):
        if self.at_end():
            return False
        return self.tokens[self.index].tok_type == tok_type

    def parse(self):
        while not self.at_end():
            self.statement()

    def statement(self):
        if self.match(TokenType.IF):
            self.if_statement()
        elif self.match(TokenType.PRINT):
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

        # if self.match(TokenType.ARROW):
        self.consume(TokenType.ARROW, "Expected '->' after if.")
        self.statement()
        self.back_patch(start_index)
            
    def back_patch(self, start_index):
        end_index = len(self.code)
        self.code[end_index - (end_index - start_index) - 1] = end_index - start_index

    def match(self, *token_types):
        if self.index >= len(self.tokens):
            return False
        for tok_type in token_types:
            if self.tokens[self.index].tok_type == tok_type:
                self.index += 1
                return True
        return False
    
    def consume(self, tok_type: TokenType, err_msg):
        if not self.check(tok_type):
            print(err_msg, file=sys.stderr)
        self.match(tok_type)
        
        # if not self.match(tok_type):
        #     print(err_msg, file=sys.stderr)
        #     sys.exit(0)

    def expression(self):
        self.Or()
    
    def Or(self):
        self.And()
        while self.match(TokenType.OR):
            self.And()
            self.emit_op(OpCode.OR)

    def And(self):
        self.equality()
        while self.match(TokenType.AND):
            self.equality()
            self.emit_op(OpCode.AND)
    
    def equality(self):
        self.comparision()
        while self.match(TokenType.EQUAL_EQUAL, TokenType.NOT_EQUAL):
            operator = self.tokens[self.index - 1]
            self.comparision()
            op = None
            match operator.tok_type:
                case TokenType.EQUAL_EQUAL:
                    op = OpCode.EQUAL_EQUAL
                case TokenType.NOT_EQUAL:
                    op = OpCode.NOT_EQUAL
            self.emit_op(op)
    
    def comparision(self):
        self.term()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL,
                         TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.tokens[self.index - 1]
            self.term()
            op = None
            match operator.tok_type:
                case TokenType.GREATER:
                    op = OpCode.GREATER
                case TokenType.GREATER_EQUAL:
                    op = OpCode.GREATER_EQUAL
                case TokenType.LESS:
                    op = OpCode.LESS
                case TokenType.LESS_EQUAL:
                    op = OpCode.LESS_EQUAL

            self.emit_op(op)
    
    def term(self):
        self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.tokens[self.index - 1]
            self.factor()

            op = None
            match operator.tok_type:
                case TokenType.PLUS: 
                    op = OpCode.ADD
                case TokenType.MINUS: 
                    op = OpCode.SUB
            
            self.emit_op(op)
        
    def factor(self):
        self.unary()
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self.tokens[self.index - 1]
            self.unary()
            op = None
            match operator.tok_type:
                case TokenType.SLASH:
                    op = OpCode.DIV
                case TokenType.STAR:
                    op = OpCode.MUL
                case TokenType.PERCENT:
                    op = OpCode.MODULO

            self.emit_op(op)
    
    def unary(self):
        while self.match(TokenType.MINUS):
            operator = self.tokens[self.index - 1]
            self.unary()
            op = None
            match operator.tok_type:
                case TokenType.MINUS:
                    op = OpCode.NEGATION

            self.emit_op(op)
            return
        self.primary()
            
    def primary(self):
        if self.match(TokenType.LEFT_PAREN):
            self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after grouping.")
        if self.index >= len(self.tokens):
            return
        
        if self.match(TokenType.FALSE):
            self.emit_op(OpCode.FALSE)
        elif self.match(TokenType.TRUE):
            self.emit_op(OpCode.TRUE)
        elif self.match(TokenType.NUMBER):
            token = self.tokens[self.index - 1]
            self.emit_op(OpCode.NUMBER)
            self.emit_op(token.value)
        elif self.match(TokenType.EOF):
            return

        else:
            print(self.tokens[self.index])
            print('Exression expected.')
            # sys.exit(0)
    
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

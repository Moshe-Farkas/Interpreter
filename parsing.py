from instructions import OpCode
from tokenization import TokenType
import sys

class _Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.index = 0
        self.code = []
        self.had_err = False

    def parse_error(self, error_msg):
        self.had_err = True
        print(error_msg, ' ------ Line:', self.peek().line)
        raise RuntimeError()
    
    def emit_op(self, op):
        self.code.append(op)

    def at_end(self):
        return self.peek().tok_type == TokenType.EOF
    
    def check(self, tok_type):
        if self.at_end():
            return False
        return self.peek().tok_type == tok_type
    
    def expect_newline(self):
        self.consume(TokenType.NEWLINE, 'Expect newline after statement.')

    def parse(self):
        while not self.at_end():
            if self.match(TokenType.NEWLINE):
                continue
            try:
                self.statement()
            except RuntimeError:
                self.synchronize()
    
    def synchronize(self):
        self.advance()
        while not self.at_end():
            # if self.previous().tok_type == TokenType.NEWLINE:
            #     return
            # if self.peek().tok_type == TokenType.NEWLINE:
            #     return

            self.advance()

    def statement(self):
        if (self.match(TokenType.NEWLINE)):
            return
        if self.match(TokenType.IF):
            self.if_statement()
        elif self.match(TokenType.PRINT):
            self.print_statement()
        elif self.match(TokenType.WHILE):
            self.while_statement()
        elif self.match(TokenType.IDENTIFIER):
            self.assignment()


        else:
            self.parse_error(f'Unexpected token `{self.peek().lexeme}`. Expected statement.')


        if not self.at_end():
            self.expect_newline()
    
    def if_statement(self):
        # compile condition
        self.expression()
        
        self.emit_op(OpCode.JUMP_FALSE)
        self.emit_op(-1)        # placeholder offset
        start_index = len(self.code)

        self.consume(TokenType.LEFT_BRACE, "Expect '{' after if.")
        self.block()

        self.emit_op(OpCode.JUMP)
        self.emit_op(-1)
        after_if = len(self.code)

        if self.match(TokenType.ELSE):
            self.back_patch(start_index)
            if self.match(TokenType.LEFT_BRACE):
                self.block()
            else:
                self.consume(TokenType.IF, "Expect '{' or if.")
                self.if_statement()
        else:
            self.back_patch(start_index)
        self.back_patch(after_if)
            
    def back_patch(self, start_index):
        end_index = len(self.code)
        self.code[end_index - (end_index - start_index) - 1] = end_index - start_index

    def block(self):
        while not self.at_end() and not self.check(TokenType.RIGHT_BRACE):
            self.statement()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close block.")
    
    def print_statement(self):
        self.expression()
        self.emit_op(OpCode.PRINT)

    def assignment(self):
        identifier = self.previous()

        self.consume(TokenType.EQUAL, f"Expect `=` after identifier `{identifier.lexeme}`.")

        if self.match(TokenType.LEFT_BRACKET):
            # parse list
            self.list()    
        else:
            self.expression()

        self.emit_op(OpCode.IDENTIFIER)            
        self.emit_op(identifier.lexeme)
        self.emit_op(OpCode.ASSIGNMENT)


        # identifier = self.previous()
        # self.consume(TokenType.EQUAL, f"Expect `=` after identifier `{identifier.lexeme}`.")
        # self.expression()
        # self.emit_op(OpCode.IDENTIFIER)            
        # self.emit_op(identifier.lexeme)
        # self.emit_op(OpCode.ASSIGNMENT)
    
    def list(self):
        list_items_count = 0
        while not self.at_end():
            self.expression()
            list_items_count += 1
            if self.match(TokenType.RIGHT_BRACKET):
                break
            if self.match(TokenType.NEWLINE):
                self.parse_error("Expect `]` to close list initializer.")
            self.consume(TokenType.COMMA, "Expected `,` to seperate values.")

        if self.at_end():
            if self.previous().tok_type != TokenType.RIGHT_BRACKET:
                self.parse_error("Expect `]` after list creation.")
            
    
        self.emit_op(OpCode.LIST)
        self.emit_op(list_items_count)


    def while_statement(self):
        condition_index = len(self.code)    
        self.expression()
        self.consume(TokenType.LEFT_BRACE, "Expect `{` after while keyword.")

        self.emit_op(OpCode.JUMP_FALSE)
        self.emit_op(-1)    # placeholder
        jump_false_index = len(self.code)

        self.block()
        self.emit_op(OpCode.LOOP)

        self.emit_op(len(self.code) - condition_index)        



        self.back_patch(jump_false_index)
    
    def match(self, *token_types):
        for tok_type in token_types:
            if self.check(tok_type):
                self.advance()
                return True
        return False
    
    def consume(self, tok_type: TokenType, err_msg):
        if not self.check(tok_type):
            self.parse_error(err_msg)
        self.match(tok_type)

    def advance(self):
        if not self.at_end():
            self.index += 1
        return self.previous()
    
    def previous(self):
        return self.tokens[self.index - 1]
        
    def peek(self):
        return self.tokens[self.index]

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
            operator = self.previous()
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
            operator = self.previous()
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
            operator = self.previous()
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
            operator = self.previous()
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
        while self.match(TokenType.MINUS, TokenType.NOT):
            operator = self.previous()
            self.unary()
            op = None
            match operator.tok_type:
                case TokenType.MINUS:
                    op = OpCode.NEGATION
                case TokenType.NOT:
                    op = OpCode.NOT

            self.emit_op(op)
            return
        self.primary()
            
    def primary(self):
        if self.match(TokenType.LEFT_PAREN):
            self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after grouping.")
        
        elif self.match(TokenType.FALSE):
            self.emit_op(OpCode.FALSE)
        elif self.match(TokenType.TRUE):
            self.emit_op(OpCode.TRUE)
        elif self.match(TokenType.NUMBER):
            token = self.previous()
            self.emit_op(OpCode.NUMBER)
            self.emit_op(token.value)
        elif self.match(TokenType.STRING):
            token = self.previous()
            self.emit_op(OpCode.STRING)
            self.emit_op(token.lexeme)
        elif self.match(TokenType.IDENTIFIER):
            # check if match left bracket
            iden = self.previous()
            self.emit_op(OpCode.IDENTIFIER)
            self.emit_op(iden.lexeme)
            self.emit_op(OpCode.RESOLVE)

        elif self.match(TokenType.EOF):
            return

        else:
            self.parse_error(f'Unexpected token `{self.peek().lexeme}`')
    
    def print_code(self):
        for op in self.code:
            print(op)


def parse(tokens: list):
    parser = _Parser(tokens)
    parser.parse()

    print('*' * 50)
    parser.print_code()
    print('*' * 50)
    print('\n')

    if parser.had_err:
        sys.exit(0)

    return parser.code

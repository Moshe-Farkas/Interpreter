from instructions import OpCode
from tokenization import TokenType
import sys

class FunctionDeclaration:
    def __init__(self, params, code_segment):
        self.params = params
        self.code_segment = code_segment


class _Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.index = 0
        self.function_declarations = {}
        self.current_function: list
        self.had_err = False

    def parse_error(self, error_msg):
        self.had_err = True
        print(error_msg, ' ------ Line:', self.peek().line)
        raise RuntimeError()
    
    def emit_op(self, op):
        self.current_function.append(op)

    def at_end(self):
        return self.peek().tok_type == TokenType.EOF
    
    def check(self, tok_type):
        if self.at_end():
            return False
        return self.peek().tok_type == tok_type
    
    def expect_newline(self):
        self.consume(TokenType.NEWLINE, f"Expect newline after statement. Not `{self.peek().lexeme}`.")

    def parse(self):
        while not self.at_end():
            if self.match(TokenType.NEWLINE):
                continue
            try:
                self.function_declaration()
            except RuntimeError:
                self.synchronize()
    
    def synchronize(self):
        self.advance()
        while not self.at_end():
            if self.check(TokenType.FUNC):
                return

            self.advance()
        
    def function_declaration(self):
        self.consume(TokenType.FUNC, "Expect all toplevel code to be function declarations.")
        if not self.match(TokenType.IDENTIFIER):
            self.parse_error("Expect function name after `func` keyword.")

        iden = self.previous().lexeme
        self.current_function = []
        params = []
        if not self.check(TokenType.LEFT_BRACE):
            params = self.parameters()

        self.consume(TokenType.LEFT_BRACE, "Expect `{` after after function name.")
        self.block()

        self.function_declarations[iden] = FunctionDeclaration(params, self.current_function)
    
    def parameters(self):
        params = []
        while True:
            if not self.match(TokenType.IDENTIFIER):
                self.parse_error("Expect identifers.")

            params.append(self.previous().lexeme)
            if self.check(TokenType.COMMA):
                self.consume(TokenType.COMMA, "")

            elif self.check(TokenType.LEFT_BRACE):
                break
            else:
                self.parse_error("Expect `,` to seperate paramerters or `{` to start function body.")

        return params

    def statement(self):
        if (self.match(TokenType.NEWLINE)):
            return
        if self.match(TokenType.IF):
            self.if_statement()
        elif self.match(TokenType.PRINT, TokenType.PRINTLN):
            self.print_statement()
        elif self.match(TokenType.WHILE):
            self.while_statement()
        elif self.match(TokenType.IDENTIFIER):
            iden = self.previous()
            if self.match(TokenType.LEFT_PAREN):
                self.call(iden.lexeme)
            else:
                self.assignment()
        elif self.match(TokenType.RETURN):
            self.return_statement()
        elif self.match(TokenType.SLEEP):
            self.sleep_statement()
        elif self.match(TokenType.APPEND):
            self.append_statement()
        elif self.match(TokenType.CLRSCRN):
            self.emit_op(OpCode.CLRSCRN)

        else:
            self.parse_error(f'Unexpected token `{self.peek().lexeme}`. Expected statement.')


        if not self.at_end():
            self.expect_newline()
    
    def if_statement(self):
        self.expression()
        
        self.emit_op(OpCode.JUMP_FALSE)
        self.emit_op(-1)        # placeholder offset
        start_index = len(self.current_function)

        self.consume(TokenType.LEFT_BRACE, "Expect '{' after if.")
        self.block()

        self.emit_op(OpCode.JUMP)
        self.emit_op(-1)
        after_if = len(self.current_function)

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
        end_index = len(self.current_function)
        self.current_function[end_index - (end_index - start_index) - 1] = end_index - start_index

    def block(self):
        while not self.at_end() and not self.check(TokenType.RIGHT_BRACE):
            self.statement()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close body.")
    
    def print_statement(self):
        print_type = self.previous()
        self.expression()
        match print_type.tok_type:
            case TokenType.PRINT:
                self.emit_op(OpCode.PRINT)         
            case TokenType.PRINTLN:
                self.emit_op(OpCode.PRINTLN)         

    def assignment(self):
        identifier = self.previous()
        subscript_level = 0
        while self.match(TokenType.LEFT_BRACKET):
            self.subscript()
            subscript_level += 1
        self.consume(TokenType.EQUAL, f"Expect `=` after identifier `{identifier.lexeme}`.")

        if self.match(TokenType.LEFT_BRACKET):
            self.list()    
        else:
            self.expression()

        self.emit_op(OpCode.IDENTIFIER)            
        self.emit_op(identifier.lexeme)
        self.emit_op(OpCode.ASSIGNMENT)
        while subscript_level > 0:
            self.emit_op(OpCode.SUBSCRIPT)
            subscript_level -= 1
    
    def list(self):
        list_items_count = 0
        def parse_list():
            nonlocal list_items_count
            if self.match(TokenType.NEWLINE):
                parse_list()
            elif self.match(TokenType.COMMA):
                parse_list()
            elif self.match(TokenType.RIGHT_BRACKET):
                return
            else:
                self.list_item()
                list_items_count += 1
                parse_list()
        
        parse_list()
        self.emit_op(OpCode.LIST)
        self.emit_op(list_items_count)

    def list_item(self):
        if self.match(TokenType.LEFT_BRACKET):
            self.list()
        else:
            self.expression()

    def while_statement(self):
        condition_index = len(self.current_function)    
        self.expression()
        self.consume(TokenType.LEFT_BRACE, "Expect `{` after while keyword.")

        self.emit_op(OpCode.JUMP_FALSE)
        self.emit_op(-1)    # placeholder
        jump_false_index = len(self.current_function)

        self.block()
        self.emit_op(OpCode.LOOP)

        self.emit_op(len(self.current_function) - condition_index)        
        self.back_patch(jump_false_index)
    
    def return_statement(self):
        if self.check(TokenType.NEWLINE) or self.check(TokenType.RIGHT_BRACE):
            self.emit_op(OpCode.NULL)
        else:
            self.expression()
        self.emit_op(OpCode.RET)
    
    def sleep_statement(self):
        self.expression()
        self.emit_op(OpCode.SLEEP)
    
    def append_statement(self):
        self.consume(TokenType.IDENTIFIER, "Expect identifier after append.")
        iden = self.previous()
        self.expression()
        self.emit_op(OpCode.IDENTIFIER)
        self.emit_op(iden.lexeme)
        self.emit_op(OpCode.APPEND)
    
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
    
    def call(self, iden: str):
        list_items_count = 0 
        while not self.check(TokenType.RIGHT_PAREN):
            self.expression()
            list_items_count += 1
            if self.check(TokenType.RIGHT_PAREN):
                break
            self.consume(TokenType.COMMA, "Expect `,` to seperate arguments.")

        self.emit_op(OpCode.LIST) 
        self.emit_op(list_items_count)

        self.consume(TokenType.RIGHT_PAREN, "Expect `)` after function call.")
        self.emit_op(OpCode.IDENTIFIER)
        self.emit_op(iden)
        self.emit_op(OpCode.CALL)

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
        elif self.match(TokenType.NULL):
            self.emit_op(OpCode.NULL)
        elif self.match(TokenType.NUMBER):
            token = self.previous()
            self.emit_op(OpCode.NUMBER)
            self.emit_op(token.value)
        elif self.match(TokenType.STRING):
            token = self.previous()
            self.emit_op(OpCode.STRING)
            self.emit_op(token.lexeme)
        elif self.match(TokenType.IDENTIFIER):
            if self.check(TokenType.LEFT_PAREN):
                iden = self.previous().lexeme
                self.consume(TokenType.LEFT_PAREN, "")
                self.call(iden)
            else:
                self.resolve_var()

        elif self.match(TokenType.EOF):
            return

        else:
            self.parse_error(f'Unexpected token `{self.peek().lexeme}`')
        
    def resolve_var(self):
        iden = self.previous()
        subcript_level = 0
        while self.match(TokenType.LEFT_BRACKET):
            self.subscript()
            subcript_level += 1

        self.emit_op(OpCode.IDENTIFIER)
        self.emit_op(iden.lexeme)


        self.emit_op(OpCode.RESOLVE)
        
        while subcript_level > 0:
            self.emit_op(OpCode.SUBSCRIPT)
            subcript_level -= 1 
        
    def subscript(self):
        self.expression()
        self.consume(TokenType.RIGHT_BRACKET, "Expect `]` after subscript.")
    
    def print_code(self):
        for func_name in self.function_declarations:
            print(func_name + ":")
            print("params:", self.function_declarations[func_name].params)
            for op in self.function_declarations[func_name].code_segment:
                print('\t', op)
            print('-' * 60)


def parse(tokens: list):
    parser = _Parser(tokens)
    parser.parse()

    # print('*' * 50)
    # parser.print_code()
    # print('*' * 50)
    # print('\n')
    # sys.exit(0)


    if parser.had_err:
        sys.exit(0)

    return parser.function_declarations

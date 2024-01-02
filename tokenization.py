from enum import Enum, auto
import sys

class TokenType(Enum):
    PLUS            = auto()
    MINUS           = auto()
    STAR            = auto()
    SLASH           = auto()
    OR              = auto()
    AND             = auto()
    EQUAL_EQUAL     = auto()
    EQUAL           = auto()
    NOT_EQUAL       = auto()
    GREATER_EQUAL   = auto()
    GREATER         = auto()
    LESS            = auto()
    LESS_EQUAL      = auto()
    NUMBER          = auto()
    LEFT_PAREN      = auto()
    RIGHT_PAREN     = auto()
    PERCENT         = auto()
    TRUE            = auto()
    FALSE           = auto()
    IF              = auto()
    IDENTIFIER      = auto()
    NEWLINE         = auto()
    EOF             = auto()

    # temp 
    ARROW           = auto()
    PRINT           = auto()


class Token:
    def __init__(self, tok_type: TokenType, lexeme: str, line: int, value=None):
        self.tok_type = tok_type
        self.lexeme = lexeme
        self.line = line
        self.value = value
    
    def __repr__(self) -> str:
        to_string = f'''
    TokenType : {self.tok_type}, 
    lexeme    : `{self.lexeme}`, 
    line      : {self.line}, 
    '''
        if self.value != None:
            to_string += f'value     : {self.value},'
        return to_string + '\n'

class _Lexer:
    keywords = {
        "print": TokenType.PRINT,
        "if":    TokenType.IF,
        "false": TokenType.FALSE,
        "true":  TokenType.TRUE,
    }

    def __init__(self, source: str):
        self.source = source
        self.index = 0
        self.tokens = []
        self.error_msg = ''
        self.current_line = 1
    
    def advance(self):
        self.index += 1
    
    def current(self):
        return self.source[self.index]
    
    def peek_next(self):
        self.advance()
        if self.at_end():
            return '\0'
        c = self.source[self.index]
        self.index -= 1
        return c
    
    def at_end(self):
        return self.index >= len(self.source)

    def consume_white_space(self):
        def is_white_space():
            c = self.current()
            return c == ' ' or c == '\t'

        while not self.at_end() and is_white_space():
            self.advance()

    def number(self):
        num = ''
        while not self.at_end() and self.current().isnumeric():
            num += self.current()
            self.advance()

        self.index -= 1 
        return self.new_token(TokenType.NUMBER, num, float(num))

    def keyword_or_identifier(self):
        iden = ''
        while not self.at_end() and self.current().isalpha():
            iden += self.current()
            self.advance()

        self.index -= 1     
        if iden in self.keywords:
            return self.new_token(self.keywords[iden], iden)
        else:
            print('should not be here')
            return TokenType.IDENTIFIER
    
    def tokenize(self):
        token = self.scan_token()
        while token != TokenType.EOF:
            self.tokens.append(token)
            token = self.scan_token()
        self.tokens.append(self.new_token(TokenType.EOF, ''))

    def string_literal(self):
        self.advance()
        literal = ''
        while not self.at_end() and self.current() != '"':
            literal += self.current()
            self.advance()
        return literal
    
    def new_token(self, tok_type, lexeme, value=None):
        return Token(tok_type, lexeme, self.current_line, value)

    def scan_token(self):
        if self.at_end():
            return TokenType.EOF
        token = None
        c = self.current()
        if c.isnumeric():
            token = self.number()
        elif c.isalpha():
            token = self.keyword_or_identifier()
        
        match c:
            case '\n':
                token = self.new_token(TokenType.NEWLINE, '\\n')
                self.current_line += 1
            case ' ' | '\t':
                self.consume_white_space()
                return self.scan_token()
            case '"':
                token = self.string_literal()
            case '+':
                token = self.new_token(TokenType.PLUS, '+')
            case '-':
                if self.peek_next() == '>':
                    self.advance()
                    token = self.new_token(TokenType.ARROW, '->')
                else:
                    token = self.new_token(TokenType.MINUS, '-')
            case '*':
                token = self.new_token(TokenType.STAR, '*')
            case '/':
                token = self.new_token(TokenType.SLASH, '/')
            case '(':
                token = self.new_token(TokenType.LEFT_PAREN, '(')
            case ')':
                token = self.new_token(TokenType.RIGHT_PAREN, ')')
            case '=':
                if self.peek_next() == '=':
                    self.advance()
                    token = self.new_token(TokenType.EQUAL_EQUAL, '==')
                else:
                    token = self.new_token(TokenType.EQUAL, '=')
            case '>':
                if self.peek_next() == '=':
                    self.advance()
                    token = self.new_token(TokenType.GREATER_EQUAL, '>=')
                else:
                    token = self.new_token(TokenType.GREATER, '>')

            case '<':
                if self.peek_next() == '=':
                    self.advance()
                    token = self.new_token(TokenType.LESS_EQUAL, '<=')
                else:
                    token = self.new_token(TokenType.LESS, '<')

        self.advance()
        return token 


def tokenize(s: str) -> list[TokenType]:
    lexer = _Lexer(s)
    try:
        lexer.tokenize()
    except RuntimeError:
        print(lexer.error_msg, file=sys.stderr)
        sys.exit(0)
    
    # print(lexer.tokens)

    return lexer.tokens
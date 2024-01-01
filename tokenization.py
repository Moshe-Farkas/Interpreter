from enum import Enum, auto
import sys

class Tokens(Enum):
    PLUS        = auto()
    MINUS       = auto()
    STAR        = auto()
    SLASH       = auto()
    NUMBER      = auto()
    LEFT_PAREN  = auto()
    RIGHT_PAREN = auto()
    PERCENT     = auto()
    TRUE        = auto()
    FALSE       = auto()
    EOF         = auto()

class _Lexer:
    def __init__(self, source: str):
        self.source = source
        self.index = 0
        self.tokens = []
        self.error_msg = ''
    
    def advance(self):
        self.index += 1
    
    def current(self):
        return self.source[self.index]

    def at_end(self):
        return self.index >= len(self.source)
    
    def peek_next(self):
        # assumes not at end
        return self.source[self.index + 1]
    
    def at_end(self):
        return self.index >= len(self.source)

    def consume_white_space(self):
        def is_white_space():
            c = self.current()
            return c == ' ' or c == '\t' or c == '\n'

        while not self.at_end() and is_white_space():
            self.advance()

    def number(self):
        num = ''
        while not self.at_end() and self.current().isnumeric():
            num += self.current()
            self.advance()

        self.index -= 1 
        return float(num)
        

    def keyword_or_identifier(self):
        pass
    
    def tokenize(self):
        token = self.scan_token()
        while token != Tokens.EOF:
            self.tokens.append(token)
            token = self.scan_token()

    def string_literal(self):
        self.advance()
        literal = ''
        while not self.at_end() and self.current() != '"':
            literal += self.current()
            self.advance()
        return literal

    def scan_token(self):
        if self.at_end():
            return Tokens.EOF
        token = None
        c = self.current()
        if c.isnumeric():
            token = self.number()
        elif c.isalpha():
            token = self.keyword_or_identifier()
        
        match c:
            case ' ' | '\n' | '\t':
                self.consume_white_space()
                return self.scan_token()
            case '"':
                token = self.string_literal()
            case '+':
                token = Tokens.PLUS
            case '-':
                token = Tokens.MINUS
            case '*':
                token = Tokens.STAR
            case '/':
                token = Tokens.SLASH
            case '(':
                token = Tokens.LEFT_PAREN
            case ')':
                token = Tokens.RIGHT_PAREN

            case _:
                self.error_msg = f"Unexpected char '{c}'"
                raise RuntimeError


        self.advance()
        return token 


def tokenize(s: str) -> list[Tokens]:
    lexer = _Lexer(s)
    try:
        lexer.tokenize()
    except RuntimeError:
        print(lexer.error_msg, file=sys.stderr)
        sys.exit(0)
    return lexer.tokens
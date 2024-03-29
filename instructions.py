from enum import Enum, auto

class OpCode(Enum):
    ADD           = auto()
    SUB           = auto()
    MUL           = auto()
    DIV           = auto()
    NUMBER        = auto()
    STRING        = auto()
    TRUE          = auto()
    FALSE         = auto()
    NULL          = auto()
    MODULO        = auto()
    NEGATION      = auto()
    NOT           = auto()
    EQUAL_EQUAL   = auto()
    GREATER       = auto()
    GREATER_EQUAL = auto()
    LESS          = auto()
    LESS_EQUAL    = auto()
    IDENTIFIER    = auto()
    JUMP_FALSE    = auto()
    JUMP          = auto()
    LOOP          = auto()
    PRINT         = auto()
    PRINTLN       = auto()
    ASSIGNMENT    = auto()
    LIST          = auto()
    SUBSCRIPT     = auto()
    RESOLVE       = auto()
    RET           = auto()
    CALL          = auto()
    SLEEP         = auto()
    APPEND        = auto()
    CLRSCRN       = auto()
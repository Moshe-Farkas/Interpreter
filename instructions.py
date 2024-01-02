from enum import Enum, auto

class OpCode(Enum):
    ADD           = auto()
    SUB           = auto()
    MUL           = auto()
    DIV           = auto()
    NUM           = auto()
    MODULO        = auto()
    NEGATION      = auto()
    EQUAL_EQUAL   = auto()
    GREATER       = auto()
    GREATER_EQUAL = auto()
    LESS          = auto()
    LESS_EQUAL    = auto()
    IDENTIFIER    = auto()
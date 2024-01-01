from enum import Enum, auto

class OpCode(Enum):
    OP_ADD =        auto()
    OP_SUB =        auto()
    OP_MUL =        auto()
    OP_DIV =        auto()
    OP_NUM =        auto()
    OP_MODULO =     auto()
    OP_IDENTIFIER = auto()
    OP_NEGATION =   auto()
from instructions import OpCode

def interpret(code: list) -> float:
    stack = []

    for i in range(len(code)):
        op = code[i]
        match op:
            case OpCode.OP_NUM: 
                stack.append(code[i + 1])
                i += 1
            case OpCode.OP_SUB:
                b = stack.pop()
                a = stack.pop()
                stack.append(a - b)
            case OpCode.OP_ADD:
                b = stack.pop()
                a = stack.pop()
                stack.append(a + b)
            case OpCode.OP_MUL:
                b = stack.pop()
                a = stack.pop()
                stack.append(a * b)
            case OpCode.OP_DIV:
                b = stack.pop()
                a = stack.pop()
                stack.append(a / b)
            case OpCode.OP_MODULO:
                b = stack.pop()
                a = stack.pop()
                stack.append(a % b)
            case OpCode.OP_NEGATION:
                a = stack.pop()
                stack.append(-a)
    
    return stack.pop()
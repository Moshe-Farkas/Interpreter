from instructions import OpCode

def interpret(code: list) -> float:
    stack = []

    for i in range(len(code)):
        op = code[i]
        match op:
            case OpCode.NUM: 
                stack.append(code[i + 1])
                i += 1
            case OpCode.SUB:
                b = stack.pop()
                a = stack.pop()
                stack.append(a - b)
            case OpCode.ADD:
                b = stack.pop()
                a = stack.pop()
                stack.append(a + b)
            case OpCode.MUL:
                b = stack.pop()
                a = stack.pop()
                stack.append(a * b)
            case OpCode.DIV:
                b = stack.pop()
                a = stack.pop()
                stack.append(a / b)
            case OpCode.MODULO:
                b = stack.pop()
                a = stack.pop()
                stack.append(a % b)
            case OpCode.NEGATION:
                a = stack.pop()
                stack.append(-a)
            case OpCode.EQUAL_EQUAL:
                stack.append(stack.pop() == stack.pop())
            case OpCode.GREATER:
                b = stack.pop()
                a = stack.pop()
                stack.append(a > b)
            case OpCode.GREATER_EQUAL:
                b = stack.pop()
                a = stack.pop()
                stack.append(a >= b)
            case OpCode.LESS:
                b = stack.pop()
                a = stack.pop()
                stack.append(a < b)
            case OpCode.LESS_EQUAL:
                b = stack.pop()
                a = stack.pop()
                stack.append(a <= b)
    
    return stack.pop()
from instructions import OpCode

def interpret(code: list):
    stack = []
    i = 0
    while i < len(code):
        op = code[i]
        match op:
            case OpCode.NUMBER: 
                stack.append(code[i + 1])
                i += 1
            case OpCode.TRUE:
                stack.append(True)
            case OpCode.FALSE:
                stack.append(False)
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
            case OpCode.JUMP_FALSE:
                if stack.pop() == True:
                    i += 1
                else:
                    i += code[i + 1] + 1

            case OpCode.PRINT:
                print(stack.pop())

        i += 1 
from instructions import OpCode

import sys

def interpret(code: list):
    stack = []
    variables = {}
    i = 0

    def peek_code(distance):
        if i + distance >= len(code):
            return None
        return code[i + distance]

    while i < len(code):
        op = code[i]
        match op:
            case OpCode.NUMBER: 
                i += 1
                stack.append(code[i])
            case OpCode.STRING: 
                i += 1
                stack.append(code[i])
            case OpCode.IDENTIFIER: 
                i += 1
                stack.append(code[i])
            case OpCode.TRUE:
                stack.append(True)
            case OpCode.FALSE:
                stack.append(False)
            case OpCode.SUB:
                b = stack.pop()
                a = stack.pop()
                stack.append(sub(a, b))
            case OpCode.ADD:
                b = stack.pop()
                a = stack.pop()
                stack.append(add(a, b))
            case OpCode.MUL:
                b = stack.pop()
                a = stack.pop()
                stack.append(mul(a, b))
            case OpCode.DIV:
                b = stack.pop()
                a = stack.pop()
                stack.append(div(a, b))
            case OpCode.MODULO:
                b = stack.pop()
                a = stack.pop()
                stack.append(mod(a, b))
            case OpCode.NEGATION:
                a = stack.pop()
                stack.append(negate(a))
            case OpCode.EQUAL_EQUAL:
                stack.append(stack.pop() == stack.pop())
            case OpCode.NOT:
                operand = stack.pop()
                if not isinstance(operand, bool):
                    raise RuntimeError(f"Can't logic negate instance of type `{type(operand).__name__}`.")
                else:
                    stack.append(not operand)

            case OpCode.GREATER:
                b = stack.pop()
                a = stack.pop()
                stack.append(comparision(a, b, '>'))
            case OpCode.GREATER_EQUAL:
                b = stack.pop()
                a = stack.pop()
                stack.append(comparision(a, b, '>='))
            case OpCode.LESS:
                b = stack.pop()
                a = stack.pop()
                stack.append(comparision(a, b, '<'))
            case OpCode.LESS_EQUAL:
                b = stack.pop()
                a = stack.pop()
                stack.append(comparision(a, b, '<='))
            case OpCode.JUMP_FALSE:
                condition = stack.pop()
                if not isinstance(condition, bool):
                    raise RuntimeError(f"Condition can't be of type `{type(condition).__name__}`.")
                if condition == True:
                    i += 1
                else:
                    i += code[i + 1] + 1
            case OpCode.JUMP:
                i += code[i + 1] + 1
            case OpCode.LOOP:
                i -= code[i + 1]
            case OpCode.ASSIGNMENT:
                iden = stack.pop()
                value = stack.pop()
                variables[iden] = value

            case OpCode.RESOLVE:
                iden = stack.pop()
                if iden not in variables:
                    raise RuntimeError(f"Undefined variable `{iden}`.")
                else:
                    if peek_code(1) == OpCode.SUBSCRIPT:
                        index = stack.pop()
                        if not isinstance(index, float):
                            raise RuntimeError(f"Can't use exression of type `{type(index).__name__}` \
to subscript `{iden}`.")

                        index = int(index) 
                        if index >= len(variables[iden]) or index < 0:
                            raise RuntimeError(f"Index `{index}` out of bounds \
for list of length `{len(variables[iden])}`.")
                        stack.append(variables[iden][index])
                    else:
                        stack.append(variables[iden])
                
            case OpCode.LIST:
                i += 1
                list_items_count = code[i]
                list_object = [stack.pop() for i in range(list_items_count)]
                list_object.reverse()
                stack.append(list_object)

            case OpCode.PRINT:
                print(stack.pop())

        i += 1 
    

def comparision(a, b, op):
    if not (isinstance(a, float) and isinstance(b, float)):
        raise RuntimeError(f"Can't compare instance of type `{type(a).__name__}` to type `{type(b).__name__}`.")
    match op:
        case '>': 
            return a > b
        case '>=': 
            return a >= b
        case '<': 
            return a < b
        case '<=': 
            return a <= b

def add(a, b):
    if isinstance(a, str) and isinstance(b, str):
        return a + b
    if isinstance(a, float) and isinstance(b, float):
        return a + b
    
    raise RuntimeError(f"Can't add instance of type `{type(a).__name__}` to type `{type(b).__name__}`.")

def sub(a, b):
    if isinstance(a, float) and isinstance(b, float):
        return a - b
    raise RuntimeError(f"Can't subtract instance of type `{type(a).__name__}` to type `{type(b).__name__}`.")

def mul(a, b):
    if isinstance(a, float) and isinstance(b, float):
        return a * b
    raise RuntimeError(f"Can't mutilply instance of type `{type(a).__name__}` to type `{type(b).__name__}`.")

def div(a, b):
    if isinstance(a, float) and isinstance(b, float):
        if b == 0:
            raise RuntimeError('Division by zero error.')
        return a / b
    raise RuntimeError(f"Can't divide instance of type `{type(a).__name__}` to type `{type(b).__name__}`.")
    
def mod(a, b):
    if isinstance(a, float) and isinstance(b, float):
        return a % b
    raise RuntimeError(f"Can't modulo instance of type `{type(a).__name__}` to type `{type(b).__name__}`.")

def negate(a):
    if isinstance(a, float):
        return -a
    raise RuntimeError(f"Can't negate instance of type `{type(a).__name__}`.")
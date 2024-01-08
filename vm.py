from instructions import OpCode
from tokenization import TokenType

import sys

class Func_obj:
    def __init__(self, func_name: str, code_segment: list):
        self.code_segment = code_segment
        self.func_name = func_name
        self.ip = 0
        self.locals = {}
        self.operand_stack = []

    def reset(self):
        self.__init__(self.func_name, self.code_segment)

    def inc_pointer(self, distance: int):
        self.ip += distance
    
    def peek_code(self, distance):
        self.inc_pointer(distance)
        if self.at_end():
            return None
        instruction = self.current()
        self.ip -= distance
        return instruction
    
    def current(self):
        return self.code_segment[self.ip]

    def at_end(self):
        return self.ip >= len(self.code_segment)
    
    def ret(self):
        ret_value = self.operand_stack.pop()
        self.reset()
        return ret_value
    
    def binary_op(self, op):
        b = self.operand_stack.pop()
        a = self.operand_stack.pop()
        match op:
            case '+':
                self.operand_stack.append(add(a, b))
            case '-':
                self.operand_stack.append(sub(a, b))
            case '*':
                self.operand_stack.append(mul(a, b))
            case '/':
                self.operand_stack.append(div(a, b))
            case '%':
                self.operand_stack.append(mod(a, b))
    
    def add(self):
        b = self.operand_stack.pop()
        a = self.operand_stack.pop()
        add(a, b)
    
    def sub(self):
        b = self.operand_stack.pop()
        a = self.operand_stack.pop()
        sub(a, b)
    
    def print(self):
        print(self.operand_stack.pop())
    
    def call(self):
        return self.operand_stack.pop()

    def push_next(self):
        self.inc_pointer(1)
        self.operand_stack.append(self.current())
    
    def resolve(self):
        iden = self.operand_stack.pop()
        if iden not in self.locals:
            raise RuntimeError(f"Undefined variable `{iden}`.")
        else:
            if self.peek_code(1) == OpCode.SUBSCRIPT:
                if not isinstance(self.locals[iden], list):
                    raise RuntimeError(f"Can't subscript expression " +
                                       f"of type `{type(self.locals[iden]).__name__}`")
                index = self.operand_stack.pop()
                if not isinstance(index, float):
                    raise RuntimeError(f"Can't use exression of type `{type(index).__name__}` " +
                                        f"to subscript `{iden}`.")
                index = int(index) 
                if index >= len(self.locals[iden]) or index < 0:
                    raise RuntimeError(f"Index `{index}` out of bounds " + 
                                       f"for list of length `{len(self.locals[iden])}`.")
                self.operand_stack.append(self.locals[iden][index])
            else:
                self.operand_stack.append(self.locals[iden])
    
    def assignment(self):
        iden = self.operand_stack.pop()
        value = self.operand_stack.pop()
        self.locals[iden] = value

    def list(self):
        self.inc_pointer(1)
        list_items_count = self.current()
        list_object = [self.operand_stack.pop() for i in range(list_items_count)]
        list_object.reverse()
        self.operand_stack.append(list_object)
    
    def negate(self):
        self.operand_stack.append(negate(self.operand_stack.pop()))

    def Not(self):
        operand = self.operand_stack.pop()
        if not isinstance(operand, bool):
            raise RuntimeError(f"Can't logic negate instance of type `{type(operand).__name__}`.")
        else:
            self.operand_stack.append(not operand)
    
    def keyword_value(self):
        keyword = self.current()
        value = None
        match keyword:
            case OpCode.FALSE:
                value = False
            case OpCode.TRUE:
                value = True
            case OpCode.NULL:
                value = None
        self.operand_stack.append(value)
    
    def equal_equal(self):
        self.operand_stack.append(self.operand_stack.pop() == self.operand_stack.pop())
    
    def comparision(self):
        keyword = self.current()
        value = None
        b = self.operand_stack.pop()
        a = self.operand_stack.pop()
        match keyword:
            case OpCode.GREATER:
                value = comparision(a, b, ">")
            case OpCode.GREATER_EQUAL:
                value = comparision(a, b, ">=")
            case OpCode.LESS:
                value = comparision(a, b, "<")
            case OpCode.LESS_EQUAL:
                value = comparision(a, b, "<=")
        
        self.operand_stack.append(value)

    def jump_false(self):
        condition = self.operand_stack.pop()
        if not isinstance(condition, bool):
            raise RuntimeError(f"Condition can't be of type `{type(condition).__name__}`.")
        if condition == True:
            self.inc_pointer(1)
        else:
            self.ip += self.code_segment[self.ip + 1] + 1
    
    def jump(self):
        self.ip += self.code_segment[self.ip + 1] + 1

    def loop(self):
        self.ip -= self.code_segment[self.ip + 1]

class VM:
    def __init__(self, func_segments):
        self.func_segments = func_segments

        # self.func_objs = {}
        # for func_name in func_segments:
        #     self.func_objs[func_name] = Func_obj(func_name, func_segments[func_name])

        self.call_trace_stack = []
    
    def run(self):
        try:
            self.run_stack_frame('main')
        except RuntimeError as e:
            print("Runtime error: ", e)
            print('-' * 50)
            print(self.call_trace_stack)


        print('\n::: finished.')

    def run_stack_frame(self, func_name: str):
        if func_name not in self.func_segments:
            raise RuntimeError("undefined function.")

        func_obj = Func_obj(func_name, self.func_segments[func_name])

        self.call_trace_stack.append(func_obj.func_name)

        while not func_obj.at_end():
            op = func_obj.current()
            match op:
                case OpCode.ADD:
                    func_obj.binary_op('+')
                case OpCode.SUB:
                    func_obj.binary_op('-')
                case OpCode.MUL:
                    func_obj.binary_op('*')
                case OpCode.DIV:
                    func_obj.binary_op('/')
                case OpCode.MODULO:
                    func_obj.binary_op('%')
                case OpCode.EQUAL_EQUAL:
                    func_obj.equal_equal()
                case OpCode.GREATER | OpCode.GREATER_EQUAL | OpCode.LESS | OpCode.LESS_EQUAL:
                    func_obj.comparision()
                case OpCode.TRUE | OpCode.FALSE | OpCode.NULL:
                    func_obj.keyword_value()
                case OpCode.NEGATION:
                    func_obj.negate()
                case OpCode.NOT:
                    func_obj.Not()
                case OpCode.STRING | OpCode.IDENTIFIER | OpCode.NUMBER:
                    func_obj.push_next()
                case OpCode.PRINT:
                    func_obj.print()
                case OpCode.RESOLVE:
                    func_obj.resolve()
                case OpCode.ASSIGNMENT:
                    func_obj.assignment()


                case OpCode.LIST:
                    func_obj.list()





                case OpCode.JUMP_FALSE:
                    func_obj.jump_false()
                case OpCode.JUMP:
                    func_obj.jump()
                case OpCode.LOOP:
                    func_obj.loop()
                case OpCode.CALL:
                    func_name = func_obj.call()
                    ret_value = self.run_stack_frame(func_name)
                    func_obj.operand_stack.append(ret_value)
                    
                case OpCode.RET:
                    return func_obj.ret()

            func_obj.inc_pointer(1)


def interpret(code_segment: list):
    stack = []
    globals = {}
    i = 0

    def peek_code(distance):
        if i + distance >= len(code_segment):
            return None
        return code_segment[i + distance]

    while i < len(code_segment):
        op = code_segment[i]
        match op:
            case OpCode.NUMBER: 
                i += 1
                stack.append(code_segment[i])
            case OpCode.STRING: 
                i += 1
                stack.append(code_segment[i])
            case OpCode.IDENTIFIER: 
                i += 1
                stack.append(code_segment[i])
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
                    i += code_segment[i + 1] + 1
            case OpCode.JUMP:
                i += code_segment[i + 1] + 1
            case OpCode.LOOP:
                i -= code_segment[i + 1]
            case OpCode.ASSIGNMENT:
                iden = stack.pop()
                value = stack.pop()
                globals[iden] = value

            case OpCode.RESOLVE:
                iden = stack.pop()
                if iden not in globals:
                    raise RuntimeError(f"Undefined variable `{iden}`.")
                else:
                    if peek_code(1) == OpCode.SUBSCRIPT:
                        index = stack.pop()
                        if not isinstance(index, float):
                            raise RuntimeError(f"Can't use exression of type `{type(index).__name__}` " +
                                                "to subscript `{iden}`.")
                        index = int(index) 
                        if index >= len(globals[iden]) or index < 0:
                            raise RuntimeError(f"Index `{index}` out of bounds " + 
                                                "for list of length `{len(globals[iden])}`.")
                        stack.append(globals[iden][index])
                    else:
                        stack.append(globals[iden])
                
            case OpCode.LIST:
                i += 1
                list_items_count = code_segment[i]
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
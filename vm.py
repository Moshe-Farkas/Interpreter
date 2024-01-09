from instructions import OpCode
from parsing import FunctionDeclaration
import time

import os

class Func_obj:
    def __init__(self, code_segment: list, params: list):
        self.code_segment = code_segment
        self.params = params
        self.ip = 0
        self.locals = {}
        self.operand_stack = []

    def reset(self):
        self.__init__(self.code_segment, self.params)

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
    
    def set_args(self, args: list):
        if len(args) != len(self.params):
            raise RuntimeError(f"function expects `{len(self.params)}` # of params " +
                               f"but got `{len(args)}`.")

        for i in range(len(args)):
            param = self.params[i]
            arg = args[i]
            self.locals[param] = arg
    
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
        match self.current():
            case OpCode.PRINT:
                print(self.operand_stack.pop(), end='')
            
            case OpCode.PRINTLN:
                print(self.operand_stack.pop())
    
    def call(self):
        iden = self.operand_stack.pop()
        args = self.operand_stack.pop()
        return (iden, args)

    def push_next(self):
        self.inc_pointer(1)
        self.operand_stack.append(self.current())

    def subscript(self, iden):
        indeces = []
        while self.peek_code(1) == OpCode.SUBSCRIPT:
            index = self.operand_stack.pop() 
            if not isinstance(index, float):
                raise RuntimeError(f"Can't use exression of type `{type(index).__name__}` " +
                                   f"to subscript `{iden}`.")
            index = int(index)
            indeces.insert(0, index) 
            self.inc_pointer(1)
        
        list_obj = self.locals[iden]
        if not isinstance(list_obj, list):
            raise RuntimeError(f"Can't subscript expression " +
                               f"of type `{type(list_obj).__name__}`")

        for index in indeces[:-1]:
            if index >= len(list_obj) or index < 0:
                raise RuntimeError(f"Index `{index}` out of bounds " + 
                                   f"for list of length `{len(list_obj)}`.")
            list_obj = list_obj[index]
            if not isinstance(list_obj, list):
                raise RuntimeError(f"Can't subscript expression " +
                                   f"of type `{type(list_obj).__name__}`")
        index = indeces[-1]        
        if index >= len(list_obj) or index < 0:
            raise RuntimeError(f"Index `{index}` out of bounds " + 
                                f"for list of length `{len(list_obj)}`.")
        return list_obj, index

    def resolve(self):
        iden = self.operand_stack.pop()
        if iden not in self.locals:
            raise RuntimeError(f"Undefined variable `{iden}`.")
        else:
            if self.peek_code(1) == OpCode.SUBSCRIPT:
                list_obj, index = self.subscript(iden)
                self.operand_stack.append(list_obj[index])
            else:
                self.operand_stack.append(self.locals[iden])
    
    def assignment(self):
        iden = self.operand_stack.pop()
        if self.peek_code(1) == OpCode.SUBSCRIPT:
            value = self.operand_stack.pop()
            list_obj, index = self.subscript(iden)
            list_obj[index] = value
        else:
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
    
    def sleep(self):
        amount = self.operand_stack.pop()
        if not isinstance(amount, float):
            raise RuntimeError(f"Sleep duration must by of type `number` not `{type(amount).__name__}`.")
        time.sleep(amount)
    
    def append(self):
        iden = self.operand_stack.pop()
        value = self.operand_stack.pop()
        if iden not in self.locals:
            raise RuntimeError(f"Undefined variable `{iden}`.")
        list_obj = self.locals[iden]
        if not isinstance(list_obj, list):
            raise RuntimeError(f"Can't subscript expression " +
                               f"of type `{type(list_obj).__name__}`")
        list_obj.append(value)


class VM:
    def __init__(self, func_decls: {}):
        self.func_decls = func_decls
        self.call_trace_stack = []
    
    def run(self):
        try:
            self.run_stack_frame('main', [])
        except RuntimeError as e:
            print("Runtime error: ", e)
            self.print_stack_trace()
    
    def print_stack_trace(self):
        print("Stack trace:")
        for frame in self.call_trace_stack:
            print(f"\t <{frame}>")

    def run_stack_frame(self, func_name: str, func_args: list):
        if func_name not in self.func_decls:
            raise RuntimeError("undefined function.")

        func_decl = self.func_decls[func_name]
        func_obj = Func_obj(func_decl.code_segment, func_decl.params)
        func_obj.set_args(func_args)

        self.call_trace_stack.append(func_name)

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
                case OpCode.PRINT | OpCode.PRINTLN:
                    func_obj.print()
                case OpCode.CLRSCRN:
                    os.system('clear')    
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
                    func_name, func_args = func_obj.call()
                    ret_value = self.run_stack_frame(func_name, func_args)
                    func_obj.operand_stack.append(ret_value)
                case OpCode.SLEEP:
                    func_obj.sleep()
                case OpCode.APPEND:
                    func_obj.append()
                case OpCode.RET:
                    return func_obj.ret()

            func_obj.inc_pointer(1)


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
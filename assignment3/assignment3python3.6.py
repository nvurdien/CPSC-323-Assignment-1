# works with python3.6

from enum import Enum
import string

# %% start of lexer
keyword = ['while', 'if', 'for', 'else', 'get', 'int', 'endif', 'return', 'put', 'function', 'real', 'boolean']

separator = ['(', ')', '[', ']', '{', '}', '!', ';', ',', ':']

regex = ['==', '^=', '>', '<', '=>', '<=']


class State(Enum):
    REJECT = 0, 'REJECT'
    INTEGER = 1, 'INTEGER'
    REAL = 2, 'REAL'
    OPERATOR = 3, 'OPERATOR'
    SEPARATOR = 4, 'SEPARATOR'
    IDENTIFIER = 5, 'IDENTIFIER'
    KEYWORD = 6, 'KEYWORD'
    UNKNOWN = 7, 'UNKNOWN'
    SPACE = 8, 'SPACE'
    BOOLEAN = 9, 'BOOLEAN'

    def __new__(cls, value, name):
        member = object.__new__(cls)
        member._value_ = value
        member.fullname = name
        return member

    def __int__(self):
        return self.value


# still working on the states    
stateTable = [
    [0, State.INTEGER, State.REAL, State.OPERATOR, State.SEPARATOR, State.IDENTIFIER, State.KEYWORD, State.UNKNOWN,
     State.SPACE],
    [State.INTEGER, State.INTEGER, State.REAL, State.REJECT, State.REJECT, State.IDENTIFIER, State.REJECT, State.REJECT,
     State.REJECT],
    [State.REAL, State.REAL, State.UNKNOWN, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT,
     State.REJECT],
    [State.OPERATOR, State.REJECT, State.REJECT, State.OPERATOR, State.REJECT, State.REJECT, State.REJECT, State.REJECT,
     State.REJECT],
    [State.SEPARATOR, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT,
     State.REJECT],
    [State.IDENTIFIER, State.IDENTIFIER, State.REJECT, State.REJECT, State.REJECT, State.IDENTIFIER, State.REJECT,
     State.REJECT, State.REJECT],
    [State.KEYWORD, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT,
     State.REJECT],
    [State.UNKNOWN, State.UNKNOWN, State.UNKNOWN, State.UNKNOWN, State.UNKNOWN, State.UNKNOWN, State.UNKNOWN,
     State.UNKNOWN, State.REJECT],
    [State.SPACE, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT,
     State.REJECT],
]


def checkToken(token):
    # print("Check Token", token)
    if token.isdigit():
        # print("is digit")
        return State.INTEGER
    elif token.isspace():
        # print("is space")
        return State.SPACE
    elif token == '$':
        return State.IDENTIFIER
    elif token == '.':
        # print("is real")
        return State.REAL
    for i in string.punctuation:
        if token == i:
            if token in separator:
                # print("is separator")
                return State.SEPARATOR
            # print("is punc")
            return State.OPERATOR
    if token.isalpha():
        # print("is alpha")
        return State.IDENTIFIER
    else:
        # print("is unknown")
        return State.UNKNOWN


comment = False
past_line = 0


def Lexer(expression, line_num):
    global col, comment
    tokens = []
    col = State.REJECT
    currentState = State.REJECT
    prevState = State.REJECT
    currentToken = ""
    for token in expression:
        col = checkToken(token)
        currentState = stateTable[int(currentState)][int(col)]
        # print("currentToken is ", currentToken, "currentState is ", currentState.fullname)
        if currentState == State.REJECT:
            currentToken = currentToken.replace(" ", "")
            if prevState != State.SPACE and currentToken:
                if currentToken == '!':
                    if comment:
                        comment = False
                    else:
                        comment = True
                elif not comment:
                    if currentToken in keyword:
                        tokens.append({'token': currentToken, 'lexeme': State.KEYWORD, 'line_num': line_num})
                    elif prevState == State.IDENTIFIER and (currentToken[len(currentToken) - 1].isdigit()):
                        tokens.append({'token': currentToken, 'lexeme': State.UNKNOWN, 'line_num': line_num})
                    elif currentToken == '%%':
                        tokens.append({'token': currentToken, 'lexeme': State.SEPARATOR, 'line_num': line_num})
                    elif prevState == State.REAL and (
                            currentToken.index(".") == 0 or currentToken.index(".") == len(currentToken) - 1):
                        tokens.append({'token': currentToken, 'lexeme': State.UNKNOWN, 'line_num': line_num})
                    elif currentToken == 'true' or currentToken == 'false':
                        tokens.append({'token': currentToken, 'lexeme': State.BOOLEAN, 'line_num': line_num})
                    else:
                        tokens.append({'token': currentToken, 'lexeme': prevState, 'line_num': line_num})
            currentToken = token
            currentState = checkToken(token)
        else:
            currentToken = currentToken.replace(" ", "")
            currentToken += token
        prevState = currentState
    if currentState != State.SPACE and currentToken and currentState != State.REJECT:
        tokens.append({'token': currentToken, 'lexeme': prevState, 'line_num': line_num})
    return tokens


# %% end of lexer

# %% start of syntaxanalyzer
def printToken(fn, index, output):
    print("Token: ", fn[index]['lexeme'], "\tLexeme:", fn[index]['token'], file=output)


def I(fn, index, output):
    if fn[index]['token'] == 'if':
        addr = len(assemblyStack)
        index += 1
        if fn[index]['token'] == '(':
            index += 1
            index = C(fn, index, output)
            if fn[index]['token'] == ')':
                index += 1
                index = S(fn, index, output)
                back_patch(len(assemblyStack))
                if fn[index]['token'] == 'else':
                    index += 1
                    index = S(fn, index, output)
                if fn[index]['token'] == 'endif':
                    return index + 1
                else:
                    print("endif expected at line ", fn[index]['line_num'], file=output)
            else:
                print(") expected at line ", fn[index]['line_num'], file=output)
        else:
            print(") expected at line ", fn[index]['line_num'], file=output)
    else:
        print("if expected at line ", fn[index]['line_num'], file=output)


def S(fn, index, output):
    if fn[index]['token'] == '{':
        index += 1
        while index < len(fn) and fn[index]['token'] != '}':
            index = S(fn, index, output)
        if index > len(fn):
            print("expected } at line ", fn[len(fn) - 1]['line_num'], file=output)
        else:
            return index + 1
    elif fn[index]['token'] == 'int':
        index += 1
        while fn[index]['lexeme'] == State.IDENTIFIER:
            if fn[index]['token'] not in symbolTable:
                symbolTable[fn[index]['token']] = [fn[index]['token'], 2000 + len(symbolTable), 'integer', None]
            else:
                print("identifier reinitialization at line ", fn[index]['line_num'], file=output)
                return None
            index += 1
            if fn[index]['token'] == ',':
                index += 1
            elif fn[index]['token'] == ';':
                return index + 1
    elif fn[index]['token'] == 'boolean':
        index += 1
        while fn[index]['lexeme'] == State.IDENTIFIER:
            if fn[index]['token'] not in symbolTable:
                symbolTable[fn[index]['token']] = [fn[index]['token'], 2000 + len(symbolTable), 'boolean', None]
            else:
                print("identifier reinitialization at line ", fn[index]['line_num'], file=output)
                return None
            index += 1
            if fn[index]['token'] == ',':
                index += 1
            elif fn[index]['token'] == ';':
                return index + 1
    elif fn[index]['token'] == 'if':
        return I(fn, index, output)
    elif fn[index]['token'] == 'while':
        return whileStatements(fn, index, output)
    elif fn[index]['token'] == 'put':
        index += 1
        if fn[index]['token'] == '(':
            index += 1
            if fn[index]['lexeme'] in [State.IDENTIFIER, State.INTEGER]:
                if fn[index]['lexeme'] == State.IDENTIFIER:
                    index = E(fn, index, fn[index]['token'], output)
                else:
                    index = E(fn, index, "", output)
                gen_instr("STDOUT", "")
                if fn[index]['token'] == ')':
                    index += 1
                    if fn[index]['token'] == ';':
                        return index + 1
                    else:
                        print("; expected at line ", fn[index]['line_num'], file=output)
                else:
                    print(") expected at line ", fn[index]['line_num'], file=output)
            else:
                print("identifier or integer expected at line ", fn[index]['line_num'], file=output)
        else:
            print("( expected at line ", fn[index]['line_num'], file=output)
    elif fn[index]['token'] == 'get':
        index += 1
        if fn[index]['token'] == '(':
            index += 1
            while index < len(fn) and fn[index]['lexeme'] == State.IDENTIFIER:
                gen_instr("STDIN", "")
                gen_instr("POPM", symbolTable[fn[index]['token']][1])
                index += 1
                if fn[index]['token'] == ',':
                    index += 1
            if fn[index]['token'] == ')':
                index += 1
                if fn[index]['token'] == ';':
                    return index + 1
                else:
                    print("; expected at line ", fn[index]['line_num'], file=output)
            else:
                print(") expected at line ", fn[index]['line_num'], file=output)
        else:
            print("( expected at line ", fn[index]['line_num'], file=output)
    elif fn[index]['lexeme'] == State.IDENTIFIER or fn[index]['lexeme'] == State.INTEGER:
        if index+1 < len(fn) and fn[index+1]['token'] == '=':
            return A(fn, index, output)
        index = E(fn, index, "", output)
        if fn[index]['token'] == ';':
            return index + 1
    elif fn[index]['token'] == '%%':
        return S(fn, index+1, output)
    else:
        print("identifier, if, while, put or get expected at line ", fn[index]['line_num'], file=output)


def C(fn, index, output):
    if fn[index]['lexeme'] == State.IDENTIFIER:
        index = E(fn, index, fn[index]['token'], output)
    else:
        index = E(fn, index, "", output)
    if fn[index]['token'] in regex:
        op = fn[index]['token']
        index += 1
        if fn[index]['lexeme'] == State.IDENTIFIER:
            index = E(fn, index, fn[index]['token'], output)
        else:
            index = E(fn, index, "", output)
        if op == '<':
            gen_instr("LES", "")
            jumpStack.append(len(assemblyStack))
            gen_instr("JUMPZ", "")
        elif op == '>':
            gen_instr("GRT", "")
            jumpStack.append(len(assemblyStack))
            gen_instr("JUMPZ", "")
        elif op == '^=':
            gen_instr("NEQ", "")
            jumpStack.append(len(assemblyStack))
            gen_instr("JUMPZ", "")
        elif op == '==':
            gen_instr("EQU", "")
            jumpStack.append(len(assemblyStack))
            gen_instr("JUMPZ", "")
        elif op == '=>':
            gen_instr("GEQ", "")
            jumpStack.append(len(assemblyStack))
            gen_instr("JUMPZ", "")
        elif op == '<=':
            gen_instr("LEQ", "")
            jumpStack.append(len(assemblyStack))
            gen_instr("JUMPZ", "")
        return index
    elif fn[index]['token'] == ')' and fn[index-1]['token'] in ['true', 'false']:
        if fn[index-1]['token'] == 'true':
            gen_instr("PUSHI", 1)
            gen_instr("EQU", "")
            jumpStack.append(len(assemblyStack))
            gen_instr("JUMPZ", "")
        else:
            gen_instr("PUSHI", 1)
            gen_instr("EQU", "")
            jumpStack.append(len(assemblyStack))
            gen_instr("JUMPZ", "")
        return index
    else:
        print("boolean operator expected at line ", fn[index]['line_num'], file=output)


def whileStatements(fn, index, output):
    if fn[index]['token'] == 'while':
        addr = len(assemblyStack)
        gen_instr("LABEL", "")
        index += 1
        if fn[index]['token'] == '(':
            index += 1
            index = C(fn, index, output)
            if fn[index]['token'] == ')':
                index += 1
                index = S(fn, index, output)
                gen_instr("JUMP", addr + 1)
                back_patch(len(assemblyStack))
                return index
            else:
                print(") expected at line ", fn[index]['line_num'], file=output)
        else:
            print("( expected at line ", fn[index]['line_num'], file=output)
    else:
        print("while expected at line ", fn[index]['line_num'], file=output)


def F(fn, index, save, output):
    global symbolTable
    if fn[index]['lexeme'] == State.IDENTIFIER:
        gen_instr("PUSHM", symbolTable[fn[index]['token']][1])
        return index + 1
    elif fn[index]['lexeme'] == State.INTEGER:
        gen_instr("PUSHI", fn[index]['token'])
        return index + 1
    elif fn[index]['token'] == 'true':
        gen_instr("PUSHI", 1)
        return index + 1
    elif fn[index]['token'] == 'false':
        gen_instr("PUSHI", 0)
        return index + 1
    else:
        print("identifier expected at line ", fn[index]['line_num'], file=output)


def T_prime(fn, index, save, output):
    if fn[index]['token'] == '/':
        index += 1
        index = F(fn, index, save, output)
        gen_instr("DIV", "")
        return T_prime(fn, index, save, output)
    elif fn[index]['token'] == "*":
        index += 1
        index = F(fn, index, save, output)
        gen_instr("MUL", "")
        return T_prime(fn, index, save, output)
    return index


def T(fn, index, save, output):
    index = F(fn, index, save, output)
    return T_prime(fn, index, save, output)


def E_prime(fn, index, save, output):
    if fn[index]['token'] == '-':
        index += 1
        index = T(fn, index, save, output)
        gen_instr("SUB", "")
        return E_prime(fn, index, save, output)
    elif fn[index]['token'] == '+':
        index += 1
        index = T(fn, index, save, output)
        gen_instr("ADD", "")
        return E_prime(fn, index, save, output)
    return index


def E(fn, index, save, output):
    index = T(fn, index, save, output)
    return E_prime(fn, index, save, output)


def A(fn, index, output):
    if fn[index]['lexeme'] == State.IDENTIFIER:
        save = fn[index]['token']
        index += 1
        if fn[index]['token'] == '=':
            index += 1
            if fn[index]['lexeme'] == State.IDENTIFIER:
                index = E(fn, index, fn[index]['token'], output)
            else:
                index = E(fn, index, State.INTEGER, output)
            gen_instr("POPM", symbolTable[save][1])
            if fn[index]['token'] == ';':
                return index + 1
        else:
            print(" = expected at line ", fn[index]["line_num"], file=output)
    else:
        print("identifier expected at line ", fn[index]['line_num'], file=output)
    return index


def syntaxAnalyzer(fn, output):
    global past_line
    index = 0
    while index < len(fn):
        index = S(fn, index, output)
        if index is None:
            break
    return True


# end of syntaxAnalyzer


memLoc = 2000
#
# Symbol Table Structure Example
#   {
#       "A": [
#               tokenItself ("A"),
#               memoryLocation starts at 2000,
#               Value type (State.IDENTIFIER),
#               Value (int, real, boolean)
#            ]
#   }
#
# symbolTable["A"][0] = (identifier string)
# symbolTable["A"][1] = (memorylocation int)
# symbolTable["A"][2] = (currentState State.___)
# symbolTable["A"][3] = (value of object)
#
symbolTable = {}
#
# Assembly Stack Structure Example
#   [
#       {
#           address: (1),
#           operation: "",
#           operand: ""
#       }
#    ]
#
# assemblyStack[0]["address"] = (address int)
# assemblyStack[0]["operation"] = (operation string)
# assemblyStack[0]["operand"] = (address string (can be nil))
#
assemblyStack = []
#
# Jump stack
#
jumpStack = []


def back_patch(jump_addr):
    addr = jumpStack[len(jumpStack) - 1]
    assemblyStack[addr]["operand"] = jump_addr + 1


def gen_instr(op, oprnd):
    global assemblyStack
    instruction = {"address": len(assemblyStack), "operation": op, "operand": oprnd}
    assemblyStack.append(instruction)


# outputs assemblystack
def assemblyCode(output):
    for code in assemblyStack:
        print(code["address"] + 1, "\t", code["operation"], "\t", code["operand"], file=output)
    print("", file=output)
    print("Symbol Table", file=output)
    print("Identifier\tMemoryLocation\tType", file=output)
    for sym in symbolTable:
        print(symbolTable[sym][0], '\t\t', symbolTable[sym][1], '\t\t', symbolTable[sym][2], file=output)


filename = input('Enter a input filename: ')

results = []
line_n = 1

with open(filename) as inputfile:
    for line in inputfile:
        results += Lexer(line, line_n)
        line_n += 1

filename = input('Enter a output filename: ')
try:
    with open(filename, "w+") as outputfile:
        syntaxAnalyzer(results, outputfile)
        assemblyCode(outputfile)
except KeyError or TypeError:
    print(symbolTable)
    print(assemblyStack)

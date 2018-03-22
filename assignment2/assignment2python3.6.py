# works with python3.6

from enum import Enum
import string

keyword = ['while', 'if', 'for', 'else', 'get', 'int', 'endif', 'return', 'put', 'function', 'real']
# %% checked later for separators
separator = ['(', ')', '[', ']', '{', '}', '!', ';', ',', ':']


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
    EXPRESSION = 9, 'EXPRESSION'
    T_EXPRESSION = 10, 'T_EXPRESSION'
    E_NEXT = 11, 'E_NEXT'

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


def Lexer(expression):
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
                        tokens.append({'token': currentToken, 'lexeme': State.KEYWORD})
                    elif prevState == State.IDENTIFIER and currentToken.find('$') > -1 and currentToken[
                        len(currentToken) - 1] != '$':
                        tokens.append({'token': currentToken, 'lexeme': State.UNKNOWN})
                    elif currentToken == '%%':
                        tokens.append({'token': currentToken, 'lexeme': State.SEPARATOR})
                    elif prevState == State.REAL and (
                            currentToken.index(".") == 0 or currentToken.index(".") == len(currentToken) - 1):
                        tokens.append({'token': currentToken, 'lexeme': State.UNKNOWN})
                    else:
                        tokens.append({'token': currentToken, 'lexeme': prevState})
            currentToken = token
            currentState = checkToken(token)
        else:
            currentToken = currentToken.replace(" ", "")
            currentToken += token
        prevState = currentState
    if currentState != State.SPACE and currentToken and currentState != State.REJECT:
        tokens.append({'token': currentToken, 'lexeme': prevState})
    return tokens


def syntaxAnalyzer(fn):
    result = ""
    status = []
    error = False
    assignment = False
    operation = False
    with open(fn) as inputfile:
        for line in inputfile:
            temp = Lexer(line)
            index = 0
            while index < len(temp):
                print('T')
                if temp[index]['lexeme'] is State.IDENTIFIER:
                    status.append(temp[index])
                    if not operation and not assignment:
                        print(1)
                        result += "Token: Identifier\tLexeme: " + temp[index]['token'] + "\n"
                        result += "<Statement> -> <Assign>\n"
                        result += "<Assign> -> <Identifier> = <Expression>;\n"
                    elif assignment and not operation:
                        print(2)
                        result += "Token: Identifier\tLexeme: " + temp[index]['token'] + "\n"
                        result += "<Expression> -> <Term><Expression Prime>\n"
                        result += "<Term> -> <Factor><Term Prime>\n"
                        result += "<Factor> -> <Identifier>\n"
                    else:
                        print("next")
                        result += "Token: Identifier\tLexeme: " + temp[index]['token'] + "\n"
                        result += "<Term> -> <Factor><Term Prime>\n"
                        result += "<Factor> -> <Identifier>\n"
                else:
                    print(3)
                    result += "ID expected"
                    error = True
                if error:
                    return result
                index += 1
                print("E_next")
                if temp[index]['token'] is '=':
                    if operation:
                        print(4)
                        result += "you cannot assign an operation"
                        error = True
                    print(5)
                    assignment = True
                    result += "Token: Operator\tLexeme: " + temp[index]['token'] + "\n"
                elif temp[index]['token'] is '+' or temp[index]['token'] is '-' or temp[index]['token'] is '*' or temp[index]['token'] is '/':
                    print(6)
                    operation = True
                    result += "Token: Operator\tLexeme: " + temp[index]['token'] + "\n"
                    result += "<Term Prime> -> epsilon\n"
                    result += "<Expression Prime> -> " + temp[index]['token'] + " <Term><Expression Prime>\n"
                elif temp[index]['token'] is ';':
                    print(7)
                    operation = False
                    assignment = False
                    result += "Token: Operator\tLexeme: " + temp[index]['token'] + "\n"
                    result += "<Term Prime> -> epsilon\n"
                    result += "<Expression Prime> -> epsilon\n"
                else:
                    error = True
                    result += "There is an error"
                if error:
                    return result
                index += 1
    return result


filename = input('Enter a input filename: ')

results = syntaxAnalyzer(filename)

print(results)

# include output file
# filename = input('Enter a output filename: ')
# with open(filename, "w+") as outputfile:
#     print("Token\t\t=\tLexeme", file=outputfile)
#     for val in results:
#         for r in val:
#             if r['lexeme'].fullname == 'REAL':
#                 print(r['lexeme'].fullname, "\t\t=\t", r['token'], file=outputfile)
#             else:
#                 print(r['lexeme'].fullname, "\t=\t", r['token'], file=outputfile)

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

    def __new__(cls, value, name):
        member = object.__new__(cls)
        member._value_ = value
        member.fullname = name
        return member

    def __int__(self):
        return self.value


# still working on the states    
stateTable = [
    [0,                State.INTEGER,    State.REAL,    State.OPERATOR, State.SEPARATOR, State.IDENTIFIER, State.KEYWORD, State.UNKNOWN, State.SPACE],
    [State.INTEGER,    State.INTEGER,    State.REAL,    State.REJECT,   State.REJECT,    State.IDENTIFIER, State.REJECT,  State.REJECT,  State.REJECT],
    [State.REAL,       State.REAL,       State.UNKNOWN, State.REJECT,   State.REJECT,    State.REJECT,     State.REJECT,  State.REJECT,  State.REJECT],
    [State.OPERATOR,   State.REJECT,     State.REJECT,  State.OPERATOR, State.REJECT,    State.REJECT,     State.REJECT,  State.REJECT,  State.REJECT],
    [State.SEPARATOR,  State.REJECT,     State.REJECT,  State.REJECT,   State.REJECT,    State.REJECT,     State.REJECT,  State.REJECT,  State.REJECT],
    [State.IDENTIFIER, State.IDENTIFIER, State.REJECT,  State.REJECT,   State.REJECT,    State.IDENTIFIER, State.REJECT,  State.REJECT,  State.REJECT],
    [State.KEYWORD,    State.REJECT,     State.REJECT,  State.REJECT,   State.REJECT,    State.REJECT,     State.REJECT,  State.REJECT,  State.REJECT],
    [State.UNKNOWN,    State.UNKNOWN,    State.UNKNOWN, State.UNKNOWN,  State.UNKNOWN,   State.UNKNOWN,    State.UNKNOWN, State.UNKNOWN, State.REJECT],
    [State.SPACE,      State.REJECT,     State.REJECT,  State.REJECT,   State.REJECT,    State.REJECT,     State.REJECT,  State.REJECT,  State.REJECT],
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
                    elif prevState == State.IDENTIFIER and currentToken.find('$') > -1 and currentToken[len(currentToken)-1] != '$':
                        tokens.append({'token': currentToken, 'lexeme': State.UNKNOWN})
                    elif currentToken == '%%':
                        tokens.append({'token': currentToken, 'lexeme': State.SEPARATOR})
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


filename = input('Enter a input filename: ')

results = []
with open(filename) as inputfile:
    for line in inputfile:
        results.append(Lexer(line))
# print("Token\t\t=\tLexeme")
# for val in results:
#     for r in val:
#         if r['lexeme'].fullname == 'REAL':
#             print(r['lexeme'].fullname, "\t\t=\t", r['token'])
#         else:
#             print(r['lexeme'].fullname, "\t=\t", r['token'])

# include output file
filename = input('Enter a output filename: ')
with open(filename, "w+") as outputfile:
    print("Token\t\t=\tLexeme", file=outputfile)
    for val in results:
        for r in val:
            if r['lexeme'].fullname == 'REAL':
                print(r['lexeme'].fullname, "\t\t=\t", r['token'], file=outputfile)
            else:
                print(r['lexeme'].fullname, "\t=\t", r['token'], file=outputfile)

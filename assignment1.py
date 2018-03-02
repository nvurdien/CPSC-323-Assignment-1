from enum import Enum
import string

keyword = ['while']
separator = ['(', ')', '[', ']', '{', '}']


class State(Enum):
    REJECT = 0, 'REJECT'
    INTEGER = 1, 'INTEGER'
    REAL = 2, 'REAL'
    OPERATOR = 3, 'OPERATOR'
    SEPARATOR = 4, 'SEPARATOR'
    IDENTIFIER = 5, 'IDENTIFIER'
    UNKNOWN = 6, 'UNKNOWN'
    SPACE = 7, 'SPACE'

    def __new__(cls, value, name):
        member = object.__new__(cls)
        member._value_ = value
        member.fullname = name
        return member

    def __int__(self):
        return self.value


# still working on the states    
stateTable = [
    [0, State.INTEGER, State.REAL, State.OPERATOR, State.SEPARATOR, State.IDENTIFIER, State.UNKNOWN, State.SPACE],
    [State.INTEGER, State.INTEGER, State.REAL, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT],
    [State.REAL, State.REAL, State.UNKNOWN, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT],
    [State.OPERATOR, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT],
    [State.SEPARATOR, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT],
    [State.IDENTIFIER, State.UNKNOWN, State.REJECT, State.REJECT, State.REJECT, State.IDENTIFIER, State.REJECT,
     State.REJECT],
    [State.UNKNOWN, State.UNKNOWN, State.UNKNOWN, State.UNKNOWN, State.UNKNOWN, State.UNKNOWN, State.UNKNOWN,
     State.REJECT],
    [State.SPACE, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT, State.REJECT],
]


def checkToken(token):
    if token.isdigit():
        return State.INTEGER
    elif token.isspace():
        return State.SPACE
    elif token.alpha():
        return State.IDENTIFIER
    elif token == '.':
        return State.REAL
    for i in string.punctuation:
        if token == i:
            if token in separator:
                return State.SEPARATOR
            return State.OPERATOR
    else:
        return State.UNKNOWN


def Lexer(expression):
    global col
    tokens = []
    col = State.REJECT
    currentState = State.REJECT
    prevState = State.REJECT
    currentToken = ""
    for token in expression:
        col = checkToken(token)
        currentState = stateTable[currentState][col._value_]
        if currentState == State.REJECT:
            if prevState != State.SPACE:
                tokens.append({'token': currentToken, 'lexemme': prevState})
            currentToken = ""
        else:
            currentToken += token
        prevState = currentState
    if currentState != State.SPACE and currentToken != "":
        tokens.append({'token': currentToken, 'lexemme': prevState})
    return tokens


filename = input('Enter a filename: ')

results = []
with open(filename) as inputfile:
    for line in inputfile:
        results.append(Lexer(line))

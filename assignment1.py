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
    [State.INTEGER,    State.INTEGER,    State.REAL,    State.REJECT,   State.REJECT,    State.REJECT,     State.REJECT,  State.REJECT,  State.REJECT],
    [State.REAL,       State.REAL,       State.UNKNOWN, State.REJECT,   State.REJECT,    State.REJECT,     State.REJECT,  State.REJECT,  State.REJECT],
    [State.OPERATOR,   State.REJECT,     State.REJECT,  State.REJECT,   State.REJECT,    State.REJECT,     State.REJECT,  State.REJECT,  State.REJECT],
    [State.SEPARATOR,  State.REJECT,     State.REJECT,  State.REJECT,   State.REJECT,    State.REJECT,     State.REJECT,  State.REJECT,  State.REJECT],
    [State.IDENTIFIER, State.IDENTIFIER, State.REJECT,  State.REJECT,   State.REJECT,    State.IDENTIFIER, State.REJECT, State.REJECT,  State.REJECT],
    [State.KEYWORD,    State.REJECT,     State.REJECT,  State.REJECT,   State.REJECT,    State.REJECT,     State.REJECT, State.REJECT,  State.REJECT],
    [State.UNKNOWN,    State.UNKNOWN,    State.UNKNOWN, State.UNKNOWN,  State.UNKNOWN,   State.UNKNOWN,    State.UNKNOWN, State.UNKNOWN, State.REJECT],
    [State.SPACE,      State.REJECT,     State.REJECT,  State.REJECT,   State.REJECT,    State.REJECT,     State.REJECT,  State.REJECT,  State.REJECT],
]


def checkToken(token):
    if token.isdigit():
        return State.INTEGER
    elif token.isspace():
        return State.SPACE
    elif token.isalpha():
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
        currentState = stateTable[int(currentState)][int(col)]
        if currentState == State.REJECT:
            if currentToken in keyword:
                tokens.append({'token': currentToken, 'lexeme': State.KEYWORD})
            elif prevState != State.SPACE:
                tokens.append({'token': currentToken, 'lexeme': prevState})
            currentToken = ""
        else:
            currentToken += token
        prevState = currentState
    if currentState != State.SPACE and currentToken != "":
        tokens.append({'token': currentToken, 'lexeme': prevState})
    return tokens


filename = input('Enter a filename: ')

results = []
with open(filename) as inputfile:
    for line in inputfile:
        results.append(Lexer(line))
print("Token\t\t\tLexeme")
for val in results:
    for r in val:
        print(r['lexeme'].fullname, "\t\t", r['token'])

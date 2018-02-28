from enum import Enum

class State(Enum):
    REJECT = 0,
    INTEGER = 1,
    REAL = 2,
    OPERATOR = 3,
    STRING = 4,
    UNKNOWN = 5,
    SPACE = 6
    
    
# still working on the states    
stateTable = [[]]

def checkToken(token):
    if token.isdigit():
        return State.INTEGER
    elif token.isspace():
        return State.SPACE
    elif token.alpha():
        return State.STRING
    elif token == '.':
        return State.REAL
    elif token.ispunct():
        return State.OPERATOR
    else:
        return State.UNKNOWN

def Lexer(expression):
    tokens = []
    col = State.REJECT
    currentState = State.REJECT
    prevState = State.REJECT
    currentToken = ""
    for token in expression:
        value_type = checkToken(token)
        if currentState == State.REJECT:
            if prevState != State.SPACE:
                temp = {'token': currentToken, 'lexemme': prevState}
                tokens.push(temp)
            currentToken = ""
        else:
            currentToken += token
        prevState = currentState
    if currentState != State.SPACE and currentToken != "":
        temp = {'token': currentToken, 'lexemme': prevState}
        tokens.push(temp)
    return tokens


filename = input('Enter a filename: ')

results = []
with open(filename) as inputfile:
    for line in inputfile:
        results.push(Lexer(line))

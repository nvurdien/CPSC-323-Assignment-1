# works with python3.6

from enum import Enum
import string

keyword = ['while', 'if', 'for', 'else', 'get', 'int', 'endif', 'return', 'put', 'function', 'real', 'boolean']
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


def printToken(fn, index, output):
    print("Token: ", fn[index]['lexeme'], "\tLexeme:", fn[index]['token'], file=output)


def body_state(fn, index, output):
    index -= 1
    global past_line
    if index is None:
        print("Unexpected expression at line", past_line, file=output)
        return None
    if fn[index]['token'] == '{':
        printToken(fn, index, output)
        print("<Body> -> { <Statement_List> }", file=output)
        index += 1
        while True:
            if len(fn) > index and fn[index]['token'] != '}':
                index = statement(fn, index, output)
            elif len(fn) < index:
                past_line = fn[index]['line_num']
                print("Expecting closing brace at line", past_line, file=output)
                return None
            else:
                printToken(fn, index, output)
                return index + 1
    else:
        print("<Statement_List> -> ", file=output)
        return statement(fn, index, output)


def expression_tail(fn, index, output):
    if fn[index]['token'] in ['+', '-']:
        printToken(fn, index, output)
        if fn[index]['token'] in ['+']:
            print("<Expression Prime> -> + <Expression>", file=output)
        else:
            print("<Expression Prime> -> - <Expression>", file=output)
        return express(fn, index + 1, output)
    else:
        print("<Expression Prime> -> epsilon", file=output)
        return index


def factor(fn, index, output):
    if fn[index]['lexeme'] in [State.BOOLEAN, State.INTEGER, State.REAL, State.IDENTIFIER]:
        print("<Factor> -> <Identifier>", end="", file=output)
        if len(fn) > index and fn[index+1]['token'] == '(':
            print("( <Identifiers> )", file=output)
            return factor(fn, index+1, output)
        print("", file=output)
        return index + 1
    elif fn[index]['token'] in ['+', '-'] and len(fn) > index + 1:
        printToken(fn, index, output)
        if fn[index]['token'] in ['-']:
            print("<Factor> -> - <Factor>", file=output)
        else:
            print("<Factor> -> + <Factor>", file=output)
        printToken(fn, index+1, output)
        return factor(fn, index + 1, output)
    elif fn[index]['token'] == '(':
        index += 1
        printToken(fn, index, output)
        print("<Factor> -> ( <Expression> )", file=output)
        while len(fn) > index and fn[index]['token'] != ')':
            index = express(fn, index, output)
        if len(fn) > index and fn[index]['token'] == ')':
            printToken(fn, index, output)
            return index + 1
        else:
            return None
    return index


def term_tail(fn, index, output):
    if fn[index]['token'] in ['*', '/']:
        if fn[index]['token'] in ['*']:
            print("<Term Prime> -> * <Term>", file=output)
        else:
            print("<Term Prime> -> / <Term>", file=output)
        return term(fn, index + 1, output)
    else:
        print("<Term Prime> -> epsilon", file=output)
        return index


def term(fn, index, output):
    printToken(fn, index, output)
    print("<Term> -> <Factor><Term Prime>", file=output)
    index = factor(fn, index, output)
    if None:
        return index
    return term_tail(fn, index, output)


def express(fn, index, output):
    global past_line
    if index is None:
        print("Unexpected expression at line", past_line, file=output)
        return None
    print("<Expression> -> <Term><Expression Prime>;", file=output)
    index = term(fn, index, output)
    return expression_tail(fn, index, output)


def condition(fn, index, output):
    global past_line
    if index is None:
        print("Unexpected expression at line", past_line, file=output)
        return None
    print("<Condition> -> <Expression> <Relop> <Expression>", file=output)
    index = express(fn, index, output)
    if fn[index]['token'] in ['==', '^=', '>', '<', '=>', '=<']:
        printToken(fn, index, output)
        print("<Relop> -> ", end="", file=output)
        print(fn[index]['token'], file=output)
        return express(fn, index + 1, output)
    else:
        past_line = fn[index]['line_num']
        print("Expected relop token at line", past_line, file=output)
        return None


def statement(fn, index, output):
    global past_line
    if index is None:
        print("Unexpected expression at line", past_line, file=output)
        return None
    if fn[index]['lexeme'] == State.IDENTIFIER and len(fn) > index + 1 and fn[index+1]['token'] == '=':
        printToken(fn, index, output)
        print("<Assign> ->  <Identifier> = <Expression>;", file=output)
        printToken(fn, index+1, output)
        index = express(fn, index + 2, output)
    elif fn[index]['token'] == 'if':
        printToken(fn, index, output)
        print("<If> -> if (<Condition>) <Statement> endif", file=output)
        printToken(fn, index+1, output)
        index = condition(fn, index+2, output)
        if len(fn) > index and fn[index]['token'] == ')':
            printToken(fn, index, output)
            index = statement_list(fn, index+1, output)
            if len(fn) > index and fn[index]['token'] == 'endif':
                print("<If> -> if (<Condition>) <Statement> endif", file=output)
                printToken(fn, index, output)
                return index + 1
            elif len(fn) > index and fn[index]['token'] == 'else':
                print("<If> -> if (<Condition>) <Statement> else <Statement> endif", file=output)
                printToken(fn, index, output)
                index = statement_list(fn, index + 1, output)
                if len(fn) > index and fn[index]['token'] == 'endif':
                    printToken(fn, index, output)
                    return index + 1
                else:
                    past_line = fn[index]['line_num']
                    print("Expecting endif at line", past_line, file=output)
                    return None
            else:
                past_line = fn[index]['line_num']
                print("Expecting endif at line", past_line, file=output)
                return None
        else:
            past_line = fn[index]['line_num']
            print("Expecting ) at line", past_line, file=output)
            return None
    elif fn[index]['token'] == 'return':
        printToken(fn, index, output)
        print("<Return> -> return <Expression>;", file=output)
        index = express(fn, index + 1, output)
    elif fn[index]['token'] == 'put' and len(fn) > index + 1 and fn[index+1]['token'] == '(':
        printToken(fn, index, output)
        print("<Print> -> put (<Expression>);", file=output)
        index += 1
        printToken(fn, index, output)
        index = express(fn, index + 1, output)
        printToken(fn, index, output)
        index += 1
    elif fn[index]['token'] == 'get' and len(fn) > index + 1 and fn[index+1]['token'] == '(':
        printToken(fn, index, output)
        print("<Scan> -> get (<Identifiers>);", file=output)
        index += 1
        printToken(fn, index, output)
        index += 1
        while True:
            if len(fn) > index and fn[index]['lexeme'] == State.IDENTIFIER:
                printToken(fn, index, output)
                index += 1
                if fn[index]['token'] == ')':
                    printToken(fn, index, output)
                    print("<Identifiers> -> <Identifier>", file=output)
                    break
                elif fn[index]['token'] == ',':
                    printToken(fn, index, output)
                    print("<Identifiers> -> <Identifier>, <Identifiers>", file=output)
                    index += 1
                else:
                    past_line = fn[index]['line_num']
                    print("Expecting comma or parentheses at line", past_line, file=output)
                    return None
            else:
                past_line = fn[index]['line_num']
                print("Expecting identifier at line", past_line, file=output)
                return None
        index += 1
    elif fn[index]['token'] == 'while' and len(fn) > index + 1 and fn[index + 1]['token'] == '(':
        printToken(fn, index, output)
        print("<While> -> while(<Condition>) <Statement>", file=output)
        printToken(fn, index+1, output)
        index = condition(fn, index + 2, output)
        if fn[index]['token'] == ')':
            printToken(fn, index, output)
            index = statement_list(fn, index + 1, output)
            if index >= len(fn):
                return index + 1
            elif fn[index]['token'] == '}':
                printToken(fn, index, output)
                return index + 1
    if fn[index]['token'] == ';':
        printToken(fn, index, output)
        return index + 1
    else:
        past_line = fn[index]['line_num']
        print("Expecting semicolon at line", past_line, file=output)
        return None


def statement_list(fn, index, output):
    global past_line
    if index is None:
        print("Unexpected expression at line", past_line, file=output)
        return None
    if fn[index]['token'] == '{':
        printToken(fn, index, output)
        print("<Statement> -> { <Statement_List> }", file=output)
        index += 1
        while True:
            if len(fn) > index and fn[index]['token'] != '}':
                index = statement(fn, index, output)
            elif len(fn) < index:
                past_line = fn[index]['line_num']
                print("Expecting closing brace at line", past_line, file=output)
                return None
            else:
                printToken(fn, index, output)
                return index + 1
    else:
        print("<Statement_List> -> ", file=output)
        return statement(fn, index, output)


def dec_list(fn, index, output):
    global past_line
    if index is None:
        print("Unexpected expression at line", past_line, file=output)
        return None
    if fn[index]['token'] in ['int', 'real', 'boolean']:
        printToken(fn, index, output)
        print("<Declaration List> -> <Declaration>;", file=output)
        print("<Declaration> -> <Identifiers>", file=output)
        index += 1
        while True:
            if len(fn) > index + 1 and fn[index]['lexeme'] == State.IDENTIFIER:
                printToken(fn, index, output)
                index += 1
                if fn[index]['token'] in [';']:
                    print("<Identifiers> -> <Identifier>", file=output)
                    printToken(fn, index, output)
                    return index
                elif fn[index]['token'] == ',':
                    printToken(fn, index, output)
                    print("<Identifiers> -> <Identifier>, <Identifiers>", file=output)
                    index += 1
                else:
                    past_line = fn[index]['line_num']
                    print("Expecting comma or semicolon at line", past_line, file=output)
                    return None
            else:
                past_line = fn[index]['line_num']
                print("Expecting identifier at line", past_line, file=output)
                return None
    else:
        past_line = fn[index]['line_num']
        print("Expecting variable type at line", past_line, file=output)
        return None


def parm_list(fn, index, output):
    global past_line
    if index is None:
        print("Unexpected expression at line", past_line, file=output)
        return None
    if fn[index]['lexeme'] == State.IDENTIFIER:
        printToken(fn, index, output)
        if len(fn) > index + 1 and fn[index + 1]['token'] == ':':
            printToken(fn, index+1, output)
            if len(fn) > index + 2 and fn[index+2]['token'] in ['int', 'boolean', 'real']:
                printToken(fn, index+2, output)
                if len(fn) > index + 3 and fn[index + 3]['token'] == ',':
                    printToken(fn, index+3, output)
                    print("<Parameter> -> <Identifier>:<Qualifier>, ", file=output)
                    return parm_list(fn, index + 4, output)
                else:
                    print("<Parameter> -> <Identifier>:<Qualifier>", file=output)
                    return index + 3
            else:
                past_line = fn[index]['line_num']
                print("Expecting variable type at line", past_line, file=output)
                return None
        else:
            past_line = fn[index]['line_num']
            print("Expecting colon at line", past_line, file=output)
            return None
    past_line = fn[index]['line_num']
    print("Expecting identifier at line", past_line, file=output)
    return None


def func_def(fn, index, output):
    global past_line
    if index is None:
        print("Unexpected expression at line", past_line, file=output)
        return None
    if fn[index]['lexeme'] == State.IDENTIFIER:
        printToken(fn, index, output)
        if len(fn) > index+1 and fn[index+1]['token'] == '[':
            printToken(fn, index+1, output)
            if len(fn) > index+2 and fn[index+1]['token'] != ']':
                printToken(fn, index+2, output)
                print("<Opt Parameter List> -> <Parameter List>", file=output)
                index = parm_list(fn, index+2, output)
            if fn[index]['token'] != ']':
                past_line = fn[index]['line_num']
                print("Expecting closing bracket at line", past_line, file=output)
                return None
            print("<Opt Parameter List> -> epsilon", file=output)
        index += 1
        if len(fn) > index and fn[index]['token'] != '{':
            printToken(fn, index, output)
            print("<Opt Declaration List> -> <Declaration List>", file=output)
            index = dec_list(fn, index+1, output)
        else:
            print("<Opt Declaration List> -> epsilon,", file=output)
        index = body_state(fn, index+1, output)
        return index
    else:
        past_line = fn[index]['line_num']
        print("Expecting identifier at line", past_line, file=output)
        return None


# have it search for %%
def start(fn, index, output):
    global past_line
    if index is None:
        print("Unexpected expression at line", past_line, file=output)
        return None
    if fn[index]['token'] == 'function':
        while fn[index]['token'] == 'function':
            printToken(fn, index, output)
            print("<Function Definition> -> <Function>", file=output)
            print("<Function> -> function <Identifier> [Opt Parameter List] <Opt Declaration List> <Body>", file=output)
            index = func_def(fn, index+1, output)
        if fn[index]['token'] == '%%':
            printToken(fn, index, output)
            index += 1
            while fn[index]['token'] in ['int', 'real', 'boolean']:
                index = dec_list(fn, index, output)
                index += 1
        index = statement_list(fn, index, output)
        index -= 1
    elif fn[index]['token'] in ['int', 'real', 'boolean']:
        index = dec_list(fn, index, output)
    elif fn[index]['token'] == '{':
        printToken(fn, index, output)
        index = body_state(fn, index+1, output)
    elif fn[index]['token'] in ['if', 'return', 'print', 'scan', 'while', 'get']:
        index = statement(fn, index, output)
        index -= 1
    elif fn[index]['lexeme'] == State.IDENTIFIER:
        printToken(fn, index, output)
        if len(fn) > index+1 and fn[index+1]['token'] == '=':
            print("<Assign> ->  <Identifier> = <Expression>", file=output)
            printToken(fn, index+1, output)
            index = express(fn, index + 2, output)
        else:
            index = express(fn, index + 1, output)
    return index + 1


def syntaxAnalyzer(fn, output):
    index = 0
    new_arr = []
    result = []
    while index < len(fn):
        index = start(fn, index, output)


filename = input('Enter a input filename: ')

results = []
line_n = 1

with open(filename) as inputfile:
    for line in inputfile:
        results += Lexer(line, line_n)
        line_n += 1

print(results)

filename = input('Enter a output filename: ')

with open(filename, "w+") as outputfile:
    syntaxAnalyzer(results, outputfile)

# include output file
# filename = input('Enter a output filename: ')
# with open(filename, "w+") as outputfile:
#     print("Token\t\t=\tLexeme", file=outputfile)
#     for r in results:
#         if r['lexeme'].fullname == 'REAL':
#             print(r['lexeme'].fullname, "\t\t=\t", r['token'], file=outputfile)
#         else:
#             print(r['lexeme'].fullname, "\t=\t", r['token'], file=outputfile)

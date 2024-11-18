import sys
import Lexer
import todot


class Parser:
    """Parser for the Jack programming language."""

    def __init__(self, file):
        self.lexer = Lexer.Lexer(file)

    def jackclass(self):
        """
        class: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        self.process({'token': 'class'})
        class_name = self.className()
        self.process({'token': '{'})

        # Process class variables
        while True:
            token = self.lexer.peek()
            if token is None or token['token'] not in ['static', 'field']:
                break
            self.classVarDec()

        # Process subroutines
        while True:
            token = self.lexer.peek()
            if token is None or token['token'] not in ['constructor', 'function', 'method']:
                break
            self.subroutineDec()

        self.process({'token': '}'})
        return {'class_name': class_name}

    def classVarDec(self):
        """
        classVarDec: ('static'| 'field') type varName (',' varName)* ';'
        """
        var_kind = self.process({'token': 'static'}) or self.process({'token': 'field'})
        var_type = self.type()
        var_names = [self.varName()]

        # Handle additional variable names
        while True:
            token = self.lexer.peek()
            if token and token['token'] == ',':
                self.process({'token': ','})
                var_names.append(self.varName())
            else:
                break

        self.process({'token': ';'})
        return {'var_type': var_type, 'var_kind': var_kind, 'var_names': var_names}

    def type(self):
        """
        type: 'int'|'char'|'boolean'|className
        """
        token = self.lexer.next()
        if token['token'] in ['int', 'char', 'boolean']:
            return token['token']
        else:
            return self.className()

    def subroutineDec(self):
        """
        subroutineDec: ('constructor'| 'function'|'method') ('void'|type) subroutineName '(' parameterList ')'
        subroutineBody
        """
        subroutine_kind = self.process({'token': 'constructor'}) or \
                          self.process({'token': 'function'}) or \
                          self.process({'token': 'method'})
        return_type = self.type()
        subroutine_name = self.subroutineName()
        self.process({'token': '('})
        self.parameterList()
        self.process({'token': ')'})
        self.subroutineBody()
        return {'subroutine_kind': subroutine_kind, 'return_type': return_type, 'subroutine_name': subroutine_name}

    def parameterList(self):
        """
        parameterList: ((type varName) (',' type varName)*)?
        """
        if self.lexer.peek() is None or self.lexer.peek()['token'] == ')':
            return []

        parameters = []
        parameters.append({'type': self.type(), 'name': self.varName()})

        while self.lexer.peek() and self.lexer.peek()['token'] == ',':
            self.process({'token': ','})
            parameters.append({'type': self.type(), 'name': self.varName()})

        return parameters

    def subroutineBody(self):
        """
        subroutineBody: '{' varDec* statements '}'
        """
        self.process({'token': '{'})
        while True:
            token = self.lexer.peek()
            if token is None or token['token'] not in ['var']:
                break
            self.varDec()
        self.statements()
        self.process({'token': '}'})

    def varDec(self):
        """
        varDec: 'var' type varName (',' varName)* ';'
        """
        self.process({'token': 'var'})
        var_type = self.type()
        var_names = [self.varName()]

        while True:
            token = self.lexer.peek()
            if token and token['token'] == ',':
                self.process({'token': ','})
                var_names.append(self.varName())
            else:
                break

        self.process({'token': ';'})
        return {'var_type': var_type, 'var_names': var_names}

    def className(self):
        """
        className: identifier
        """
        return self.process({'token': 'identifier'})['value']

    def subroutineName(self):
        """
        subroutineName: identifier
        """
        return self.process({'token': 'identifier'})['value']

    def varName(self):
        """
        varName: identifier
        """
        return self.process({'token': 'identifier'})['value']

    def statements(self):
        """
        statements : statement*
        """
        while self.lexer.peek() and self.lexer.peek()['token'] in ['let', 'if', 'while', 'do', 'return']:
            self.statement()

    def statement(self):
        """
        statement : letStatement|ifStatement|whileStatement|doStatement|returnStatement
        """
        token = self.lexer.peek()
        if token['token'] == 'let':
            self.letStatement()
        elif token['token'] == 'if':
            self.ifStatement()
        elif token['token'] == 'while':
            self.whileStatement()
        elif token['token'] == 'do':
            self.doStatement()
        elif token['token'] == 'return':
            self.returnStatement()

    def letStatement(self):
        """
        letStatement : 'let' varName ('[' expression ']')? '=' expression ';'
        """
        self.process({'token': 'let'})
        var_name = self.varName()
        if self.lexer.peek() and self.lexer.peek()['token'] == '[':
            self.process({'token': '['})
            self.expression()
            self.process({'token': ']'})
        self.process({'token': '='})
        self.expression()
        self.process({'token': ';'})

    def ifStatement(self):
        """
        ifStatement : 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        self.process({'token': 'if'})
        self.process({'token': '('})
        self.expression()
        self.process({'token': ')'})
        self.process({'token': '{'})
        self.statements()
        self.process({'token': '}'})
        if self.lexer.peek() and self.lexer.peek()['token'] == 'else':
            self.process({'token': 'else'})
            self.process({'token': '{'})
            self.statements()
            self.process({'token': '}'})

    def whileStatement(self):
        """
        whileStatement : 'while' '(' expression ')' '{' statements '}'
        """
        self.process({'token': 'while'})
        self.process({'token': '('})
        self.expression()
        self.process({'token': ')'})
        self.process({'token': '{'})
        self.statements()
        self.process({'token': '}'})

    def doStatement(self):
        """
        doStatement : 'do' subroutineCall ';'
        """
        self.process({'token': 'do'})
        self.subroutineCall()
        self.process({'token': ';'})

    def returnStatement(self):
        """
        returnStatement : 'return' expression? ';'
        """
        self.process({'token': 'return'})
        if self.lexer.peek() and self.lexer.peek()['token'] != ';':
            self.expression()
        self.process({'token': ';'})

    def expression(self):
        """
        expression : term (op term)*
        """
        self.term()
        while self.lexer.peek() and self.lexer.peek()['token'] in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            self.op()
            self.term()

    def term(self):
        """
        term : integerConstant|stringConstant|keywordConstant
              |varName|varName '[' expression ']'|subroutineCall
              | '(' expression ')' | unaryOp term
        """
        token = self.lexer.peek()
        if token['token'] in ['integerConstant', 'stringConstant', 'keywordConstant']:
            self.process({'token': token['token']})
        elif token['token'] == 'identifier':
            self.varName()
            if self.lexer.peek() and self.lexer.peek()['token'] == '[':
                self.process({'token': '['})
                self.expression()
                self.process({'token': ']'})
            elif self.lexer.peek() and self.lexer.peek()['token'] == '(':
                self.subroutineCall()
        elif token['token'] == '(':
            self.process({'token': '('})
            self.expression()
            self.process({'token': ')'})
        elif token['token'] in ['-', '~']:
            self.unaryOp()
            self.term()

    def subroutineCall(self):
        """
        subroutineCall : subroutineName '(' expressionList ')'
                        | (className|varName) '.' subroutineName '(' expressionList ')'
        """
        self.subroutineName()
        self.process({'token': '('})
        self.expressionList()
        self.process({'token': ')'})

    def expressionList(self):
        """
        expressionList : (expression (',' expression)*)?
        """
        if self.lexer.peek() and self.lexer.peek()['token'] != ')':
            self.expression()
            while self.lexer.peek() and self.lexer.peek()['token'] == ',':
                self.process({'token': ','})
                self.expression()

    def op(self):
        """
        op : '+'|'-'|'*'|'/'|'&'|'|'|'<'|'>'|'='
        """
        self.process({'token': self.lexer.next()['token']})

    def unaryOp(self):
        """
        unaryOp : '-'|'~'
        """
        self.process({'token': self.lexer.next()['token']})

    def KeywordConstant(self):
        """
        KeywordConstant : 'true'|'false'|'null'|'this'
        """
        self.process({'token': self.lexer.next()['token']})

    def process(self, expected_token):
        token = self.lexer.next()
        if token is None or token['token'] != expected_token['token']:
            self.error(token)
        return token

    def error(self, token):
        if token is None:
            print("Syntax error: end of file")
        else:
            print(f"SyntaxError (line={token['line']}, col={token['col']}): {token['token']}")
        exit()


if __name__ == "__main__":
    file = sys.argv[1]
    print('-----debut')
    parser = Parser(file)
    arbre = parser.jackclass()
    todot = todot.Todot(file)
    todot.todot(arbre)
    print('-----fin')

import sys
import Lexer


class ParserXML:
    """No comment"""

    def __init__(self, file):
        self.lexer = Lexer.Lexer(file)
        self.xml = open(file[0:-5] + ".xml", "w")
        self.xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')

    def jackclass(self):
        """
        class: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        self.xml.write("<class>\n")
        self.process('class')
        self.className()
        self.process('{')
        while self.lexer.hasNext() and self.lexer.look()['token'] in {'static', 'field'}:
            self.classVarDec()
        while self.lexer.hasNext() and self.lexer.look()['token'] in {'constructor', 'function', 'method'}:
            self.subroutineDec()
        self.process('}')
        self.xml.write("</class>\n")

    def classVarDec(self):
        """
        classVarDec: ('static'| 'field') type varName (',' varName)* ';'
        """
        self.xml.write("<classVarDec>\n")
        self.process(self.lexer.look()['token'])  # 'static' or 'field'
        self.type()
        self.varName()
        while self.lexer.hasNext() and self.lexer.look()['token'] == ',':
            self.process(',')
            self.varName()
        self.process(';')
        self.xml.write("</classVarDec>\n")

    def type(self):
        """
        type: 'int'|'char'|'boolean'|className
        """
        token = self.lexer.look()
        if token['token'] in {'int', 'char', 'boolean'}:
            self.process(token['token'])
        else:
            self.className()

    def subroutineDec(self):
        """
        subroutineDec: ('constructor'| 'function'|'method') ('void'|type)
        subroutineName '(' parameterList ')' subroutineBody
        """
        self.xml.write("<subroutineDec>\n")
        self.process(self.lexer.look()['token'])  # 'constructor', 'function', or 'method'
        token = self.lexer.look()
        if token['token'] == 'void':
            self.process('void')
        else:
            self.type()
        self.subroutineName()
        self.process('(')
        self.parameterList()
        self.process(')')
        self.subroutineBody()
        self.xml.write("</subroutineDec>\n")

    def parameterList(self):
        """
        parameterList: ((type varName) (',' type varName)*)?
        """
        self.xml.write("<parameterList>\n")
        if self.lexer.look()['token'] not in {')'}:  # Non-empty parameter list
            self.type()
            self.varName()
            while self.lexer.hasNext() and self.lexer.look()['token'] == ',':
                self.process(',')
                self.type()
                self.varName()
        self.xml.write("</parameterList>\n")

    def subroutineBody(self):
        """
        subroutineBody: '{' varDec* statements '}'
        """
        self.xml.write("<subroutineBody>\n")
        self.process('{')
        while self.lexer.hasNext() and self.lexer.look()['token'] == 'var':
            self.varDec()
        self.statements()
        self.process('}')
        self.xml.write("</subroutineBody>\n")

    def varDec(self):
        """
        varDec: 'var' type varName (',' varName)* ';'
        """
        self.xml.write("<varDec>\n")
        self.process('var')
        self.type()
        self.varName()
        while self.lexer.hasNext() and self.lexer.look()['token'] == ',':
            self.process(',')
            self.varName()
        self.process(';')
        self.xml.write("</varDec>\n")

    def className(self):
        """
        className: identifier
        """
        self.xml.write("<className>")
        self.processIdentifier()
        self.xml.write("</className>\n")

    def subroutineName(self):
        """
        subroutineName: identifier
        """
        self.xml.write("<subroutineName>")
        self.processIdentifier()
        self.xml.write("</subroutineName>\n")

    def varName(self):
        """
        varName: identifier
        """
        self.xml.write("<varName>")
        self.processIdentifier()
        self.xml.write("</varName>\n")

    def statements(self):
        """
        statements: statement*
        """
        self.xml.write("<statements>\n")
        while self.lexer.look()['token'] in {'let', 'if', 'while', 'do', 'return'}:
            self.statement()
        self.xml.write("</statements>\n")

    def statement(self):
        """
        statement: letStatement | ifStatement | whileStatement | doStatement | returnStatement
        """
        token = self.lexer.look()['token']
        if token == 'let':
            self.letStatement()
        elif token == 'if':
            self.ifStatement()
        elif token == 'while':
            self.whileStatement()
        elif token == 'do':
            self.doStatement()
        elif token == 'return':
            self.returnStatement()

    def letStatement(self):
        self.xml.write("<letStatement>\n")
        self.process('let')
        self.varName()
        if self.lexer.look()['token'] == '[':
            self.process('[')
            self.expression()
            self.process(']')
        self.process('=')
        self.expression()
        self.process(';')
        self.xml.write("</letStatement>\n")

    def ifStatement(self):
        self.xml.write("<ifStatement>\n")
        self.process('if')
        self.process('(')
        self.expression()
        self.process(')')
        self.process('{')
        self.statements()
        self.process('}')
        if self.lexer.look()['token'] == 'else':
            self.process('else')
            self.process('{')
            self.statements()
            self.process('}')
        self.xml.write("</ifStatement>\n")

    def whileStatement(self):
        self.xml.write("<whileStatement>\n")
        self.process('while')
        self.process('(')
        self.expression()
        self.process(')')
        self.process('{')
        self.statements()
        self.process('}')
        self.xml.write("</whileStatement>\n")

    def doStatement(self):
        self.xml.write("<doStatement>\n")
        self.process('do')
        self.subroutineCall()
        self.process(';')
        self.xml.write("</doStatement>\n")

    def returnStatement(self):
        self.xml.write("<returnStatement>\n")
        self.process('return')
        if self.lexer.look()['token'] != ';':
            self.expression()
        self.process(';')
        self.xml.write("</returnStatement>\n")

    def expression(self):
        self.xml.write("<expression>\n")
        self.term()
        while self.lexer.look()['token'] in {'+', '-', '*', '/', '&', '|', '<', '>', '='}:
            self.op()
            self.term()
        self.xml.write("</expression>\n")

    def term(self):
        self.xml.write("<term>\n")
        token = self.lexer.look()
        if token['type'] == 'integerConstant':
            self.process(token['token'])
        elif token['type'] == 'stringConstant':
            self.process(token['token'])
        elif token['type'] == 'identifier':
            self.processIdentifier()
        elif token['token'] in {'-', '~'}:
            self.unaryOp()
            self.term()
        elif token['token'] == '(':
            self.process('(')
            self.expression()
            self.process(')')
        self.xml.write("</term>\n")

    def subroutineCall(self):
        token = self.lexer.look()
        if token['type'] == 'identifier':
            self.processIdentifier()
            if self.lexer.look()['token'] == '(':
                self.process('(')
                self.expressionList()
                self.process(')')
            elif self.lexer.look()['token'] == '.':
                self.process('.')
                self.subroutineName()
                self.process('(')
                self.expressionList()
                self.process(')')
        else:
            self.error(token)

    def expressionList(self):
        self.xml.write("<expressionList>\n")
        if self.lexer.look()['token'] != ')':
            self.expression()
            while self.lexer.look()['token'] == ',':
                self.process(',')
                self.expression()
        self.xml.write("</expressionList>\n")

    def op(self):
        self.process(self.lexer.look()['token'])

    def unaryOp(self):
        self.process(self.lexer.look()['token'])

    def process(self, str):
        token = self.lexer.next()
        print(f"Processing token: {token}")  # Debug
        if token is not None and token['token'] == str:
            self.xml.write(f"""<{token['type']}>{token['token']}</{token['type']}>\n""")
        else:
            self.error(token)

    def processIdentifier(self):
        token = self.lexer.next()
        if token['type'] != 'identifier':
            self.error(token)
        self.xml.write(f"<identifier>{token['token']}</identifier>\n")

    def error(self, token):
        if token is None:
            print("Syntax error: unexpected end of file")
        else:
            print(f"Syntax error at line {token['line']}, col {token['col']}: {token['token']}")
        exit()


if __name__ == "__main__":
    file = sys.argv[1]
    print("----- Start Parsing -----")
    parser = ParserXML(file)
    parser.jackclass()
    print("----- Parsing Completed -----")

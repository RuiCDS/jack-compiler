import sys
import Lexer


class ParserXML:
    """No comment"""

    def __init__(self, file):
        self.lexer = Lexer.Lexer(file)
        self.xml = open(file[0:-5] + ".xml", "w")
        self.xml.write('<?xml version="1.0" encoding="UTF-8"?>')

    def jackclass(self):
        """
        class: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        self.xml.write(f"""<class>\n""")
        """todo"""
        self.xml.write(f"""</class>\n""")

    def classVarDec(self):
        """
        classVarDec: ('static'| 'field') type varName (',' varName)* ';'
        """
        self.xml.write(f"""<classVarDec>\n""")
        """todo"""
        self.xml.write(f"""</classVarDec>\n""")

    def type(self):
        """
        type: 'int'|'char'|'boolean'|className
        """
        self.xml.write(f"""<type>\n""")
        """todo"""
        self.xml.write(f"""</type>\n""")

    def subroutineDec(self):
        """
        subroutineDec: ('constructor'| 'function'|'method') ('void'|type)
        subroutineName '(' parameterList ')' subroutineBody
        """
        self.xml.write(f"""<subroutineDec>\n""")
        """todo"""
        self.xml.write(f"""</subroutineDec>\n""")

    def parameterList(self):
        """
        parameterList: ((type varName) (',' type varName)*)?
        """
        self.xml.write(f"""<parameterList>\n""")
        """todo"""
        self.xml.write(f"""</parameterList>\n""")

    def subroutineBody(self):
        """
        subroutineBody: '{' varDec* statements '}'
        """
        self.xml.write(f"""<subroutineBody>\n""")
        """todo"""
        self.xml.write(f"""</subroutineBody>\n""")

    def varDec(self):
        """
        varDec: 'var' type varName (',' varName)* ';'
        """
        self.xml.write(f"""<varDec>\n""")
        """todo"""
        self.xml.write(f"""</varDec>\n""")

    def className(self):
        """
        className: identifier
        """
        self.xml.write(f"""<className>""")
        """todo"""
        self.xml.write(f"""</className>""")

    def subroutineName(self):
        """
        subroutineName: identifier
        """
        self.xml.write(f"""<subroutineName>""")
        """todo"""
        self.xml.write(f"""</subroutineName>""")

    def varName(self):
        """
        varName: identifier
        """
        self.xml.write(f"""<varName>\n""")
        """todo"""
        self.xml.write(f"""</varName>\n""")

    def statements(self):
        """
        statements : statements*
        """
        self.xml.write(f"""<statements>\n""")
        """todo"""
        self.xml.write(f"""</statements>\n""")

    def statement(self):
        """
        statement : letStatements|ifStatement|whileStatement|doStatement|returnStatement
        """
        self.xml.write(f"""<statement>\n""")
        """todo"""
        self.xml.write(f"""</statement>\n""")

    def letStatement(self):
        """
        letStatement : 'let' varName ('[' expression ']')? '=' expression ';'
        """
        self.xml.write(f"""<letStatement>\n""")
        """todo"""
        self.xml.write(f"""</letStatement>\n""")

    def ifStatement(self):
        """
        ifStatement : 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        self.xml.write(f"""<ifStatement>\n""")
        """todo"""
        self.xml.write(f"""</ifStatement>\n""")

    def whileStatement(self):
        """
        whileStatement : 'while' '(' expression ')' '{' statements '}'
        """
        self.xml.write(f"""<whileStatement>\n""")
        """todo"""
        self.xml.write(f"""</whileStatement>\n""")

    def doStatement(self):
        """
        doStatement : 'do' subroutineCall ';'
        """
        self.xml.write(f"""<doStatement>\n""")
        """todo"""
        self.xml.write(f"""</doStatement>\n""")

    def returnStatement(self):
        """
        returnStatement : 'return' expression? ';'
        """
        self.xml.write(f"""<returnStatement>\n""")
        """todo"""
        self.xml.write(f"""</returnStatement>\n""")

    def expression(self):
        """
        expression : term (op term)*
        """
        self.xml.write(f"""<expression>\n""")
        """todo"""
        self.xml.write(f"""</expression>\n""")

    def term(self):
        """
        term : integerConstant|stringConstant|keywordConstant
                |varName|varName '[' expression ']'|subroutineCall
                | '(' expression ')' | unaryOp term
        """
        self.xml.write(f"""<term>\n""")
        """todo"""
        self.xml.write(f"""</term>\n""")

    def subroutineCall(self):
        """
        subroutineCall : subroutineName '(' expressionList ')'
                | (className|varName) '.' subroutineName '(' expressionList ')'
        Attention : l'analyse syntaxique ne peut pas distingué className et varName.
            Nous utiliserons la balise <classvarName> pour (className|varName)
        """
        self.xml.write(f"""<subroutineCall>\n""")
        """todo"""
        self.xml.write(f"""</subroutineCall>\n""")

    def expressionList(self):
        """
        expressionList : (expression (',' expression)*)?
        """
        self.xml.write(f"""<expressionList>\n""")
        """todo"""
        self.xml.write(f"""</expressionList>\n""")

    def op(self):
        """
        op : '+'|'-'|'*'|'/'|'&'|'|'|'<'|'>'|'='
        """
        self.xml.write(f"""<op>\n""")
        """todo"""
        self.xml.write(f"""</op>\n""")

    def unaryOp(self):
        """
        unaryop : '-'|'~'
        """
        self.xml.write(f"""<unaryop>\n""")
        """todo"""
        self.xml.write(f"""</unaryop>\n""")

    def KeywordConstant(self):
        """
        KeyWordConstant : 'true'|'false'|'null'|'this'
        """
        self.xml.write(f"""<KeyWordConstant>\n""")
        """todo"""
        self.xml.write(f"""</KeyWordConstant>\n""")

    def process(self, str):
        token = self.lexer.next()
        if (token is not None and token['token'] == str):
            self.xml.write(f"""<{token['type']}>{token['token']}</{token['type']}>\n""")
        else:
            self.error(token)

    def error(self, token):
        if token is None:
            print("Syntax error: end of file")
        else:
            print(f"SyntaxError (line={token['line']}, col={token['col']}): {token['token']}")
        exit()


if __name__ == "__main__":
    file = sys.argv[1]
    print('-----debut')
    parser = ParserXML(file)
    parser.jackclass()
    print('-----fin')

import sys
import Lexer
import todot


class Parser:
    """No comment"""

    def __init__(self, file):
        self.lexer = Lexer.Lexer(file)

    def jackclass(self):
        """
        class: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        return 'Todo'

    def classVarDec(self):
        """
        classVarDec: ('static'| 'field') type varName (',' varName)* ';'
        """
        return 'Todo'

    def type(self):
        """
        type: 'int'|'char'|'boolean'|className
        """
        return 'Todo'


    def subroutineDec(self):
        """
        subroutineDec: ('constructor'| 'function'|'method') ('void'|type)
        subroutineName '(' parameterList ')' subroutineBody
        """
        return 'Todo'

    def parameterList(self):
        """
        parameterList: ((type varName) (',' type varName)*)?
        """
        return 'Todo'

    def subroutineBody(self):
        """
        subroutineBody: '{' varDec* statements '}'
        """
        return 'Todo'

    def varDec(self):
        """
        varDec: 'var' type varName (',' varName)* ';'
        """

    def className(self):
        """
        className: identifier
        """
        return 'Todo'

    def subroutineName(self):
        """
        subroutineName: identifier
        """
        return 'Todo'

    def varName(self):
        """
        varName: identifier
        """
        return 'Todo'

    def statements(self):
        """
        statements : statements*
        """
        return 'Todo'

    def statement(self):
        """
        statement : letStatements|ifStatement|whileStatement|doStatement|returnStatement
        """
        return 'Todo'

    def letStatement(self):
        """
        letStatement : 'let' varName ('[' expression ']')? '=' expression ';'
        """
        return 'Todo'

    def ifStatement(self):
        """
        ifStatement : 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        return 'Todo'

    def whileStatement(self):
        """
        whileStatement : 'while' '(' expression ')' '{' statements '}'
        """
        return 'Todo'

    def doStatement(self):
        """
        doStatement : 'do' subroutineCall ';'
        """
        return 'Todo'

    def returnStatement(self):
        """
        returnStatement : 'return' expression? ';'
        """
        return 'Todo'

    def expression(self):
        """
        expression : term (op term)*
        """
        return 'Todo'

    def term(self):
        """
        term : integerConstant|stringConstant|keywordConstant
                |varName|varName '[' expression ']'|subroutineCall
                | '(' expression ')' | unaryOp term
        """
        return 'Todo'

    def subroutineCall(self):
        """
        subroutineCall : subroutineName '(' expressionList ')'
                | (className|varName) '.' subroutineName '(' expressionList ')'
        Attention : l'analyse syntaxique ne peut pas distingué className et varName.
            Nous utiliserons la balise <classvarName> pour (className|varName)
        """
        return 'Todo'

    def expressionList(self):
        """
        expressionList : (expression (',' expression)*)?
        """
        return 'Todo'

    def op(self):
        """
        op : '+'|'-'|'*'|'/'|'&'|'|'|'<'|'>'|'='
        """

    def unaryOp(self):
        """
        unaryop : '-'|'~'
        """
        return 'Todo'

    def KeywordConstant(self):
        """
        KeyWordConstant : 'true'|'false'|'null'|'this'
        """

    def process(self, str):
        token = self.lexer.next()
        if (token is not None and token['token'] == str):
            return token
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
    parser = Parser(file)
    arbre = parser.jackclass()
    todot = todot.Todot(file)
    todot.todot(arbre)
    print('-----fin')

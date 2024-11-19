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
        self.process('class')
        self.className()
        self.process('{')

        while self.lexer.hasNext() and self.lexer.look()['token'] in {'static', 'field'}:
            self.classVarDec()

        while self.lexer.hasNext() and self.lexer.look()['token'] in {'constructor','function','method'}:
            self.subroutineDec()
        self.process('}')

    def classVarDec(self):
        """
        classVarDec: ('static' | 'field') type varName (',' varName)* ';'
        """
        class_varDec = []


        if self.lexer.look()['token'] in {'static', 'field'}:
            statField = self.lexer.next()['token']
        else:
            self.error(self.lexer.next())

        # Vérifier le type de la variable
        if self.lexer.look()['token'] in {'int', 'char', 'boolean'}:
            var_type = self.lexer.next()['token']
        else:
            self.error(self.lexer.next())


        var_name = self.varName()


        class_varDec.append((statField, var_type, var_name))



        while self.lexer.look()['token'] == ',':
            self.process(',')
            var_name = self.varName()
            class_varDec.append((statField, var_type, var_name))


        self.process(';')


        return class_varDec

    def type(self):
        """
        type: 'int'|'char'|'boolean'|className
        """

        if self.lexer.hasNext() and self.lexer.look()['token'] in {'int','char','boolean','className'}:
            return self.lexer.next()
        else:
            self.error(self.lexer.next())



    def subroutineDec(self):
        """
        subroutineDec: ('constructor'| 'function'|'method') ('void'|type)
        subroutineName '(' parameterList ')' subroutineBody
        """
        subRoutineType = self.lexer.look()['token']
        if subRoutineType not in {'constructor','function','method'}:
            self.error(self.lexer.next())
        else:
            subRoutineType = self.lexer.next()

        subReturnType = self.lexer.look()['token']
        if subReturnType not in {'void','char','int','boolean'}:
            self.error(self.lexer.next())
        else:
            subReturnType = self.lexer.next()

        subRoutineName = self.lexer.next()['token']

        self.process('(')
        parametre = self.parameterList()
        self.process(')')
        subRtBody = self.subroutineBody()

        return subRoutineType, subReturnType ,subRoutineName, parametre, subRtBody



    def parameterList(self):
        """
        parameterList: ((type varName) (',' type varName)*)?
        """
        parameterList = []
        while self.lexer.hasNext() and self.lexer.look()['token'] and self.lexer.look()['token'] != ')':
            if self.lexer.look()['type'] in {'void','char','int','boolean'}:
                ParamType = self.lexer.next()['token']
                ParamName = self.lexer.next()['token']

                parameterList.append((ParamType,ParamName))

            if self.lexer.look()['token'] != ',':
                self.error(self.lexer.next())
            else:
                self.process(',')

        return parameterList

    def subroutineBody(self):
        """
        subroutineBody: '{' varDec* statements '}'
        """

        self.process('{')


        while self.lexer.hasNext() and self.lexer.look()['token'] == 'var':
            self.varDec()


        while self.lexer.hasNext() and self.lexer.look()['token'] in {'let', 'if', 'while', 'do', 'return'}:

            self.statement()



        self.process('}')

    def varDec(self):
        """
        varDec: 'var' type varName (',' varName)* ';'
        """
        listVarDec = []

        self.process('var')

        typeVar = self.lexer.look()['token']
        if typeVar not in {'int', 'char', 'boolean'}:
            self.error(self.lexer.look())
        else:
            typeVar = self.lexer.next()

        name = self.varName()

        listVarDec.append((typeVar, name))

        while self.lexer.hasNext() and self.lexer.look()['token'] == ',':
            self.process(',')

            name = self.varName()

            listVarDec.append((typeVar, name))

        self.process(';')

        return listVarDec

    def className(self):
        """
        className: identifier
        """
        if self.lexer.hasNext() and self.lexer.look()['type'] == 'identifier':
           return self.lexer.next()['token']
        else:
            self.error(self.lexer.next())


    def subroutineName(self):
        """
        subroutineName: identifier
        """
        if self.lexer.look() is not None and self.lexer.look()['type'] == 'identifier':
            return self.lexer.next()['token']
        else:
            self.error(self.lexer.next())

    def varName(self):
        """
        varName: identifier
        """

        if self.lexer.look() is not None and self.lexer.look()['type'] == 'identifier':

            return self.lexer.next()['token']
        else:
            self.error(self.lexer.next())


    def statements(self):
        """
        statements : statements*
        """
        while self.lexer.hasNext() and self.lexer.look()['token'] in {'let', 'if', 'while', 'do', 'return'}:
            token = self.lexer.next()['token']

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
            else:
                self.error(self.lexer.next())



    def statement(self):
        """
        statement : letStatements|ifStatement|whileStatement|doStatement|returnStatement
        """
        token = self.lexer.next()['token']

        if token == 'let':

            return self.letStatement()
        elif token == 'if':
            return self.ifStatement()
        elif token == 'while':
            return self.whileStatement()
        elif token == 'do':
            return self.doStatement()
        elif token == 'return':
            return self.returnStatement()
        else:
            self.error(self.lexer.next())

    def letStatement(self):
        """
        letStatement : 'let' varName ('[' expression ']')? '=' expression ';'
        """

        self.process('let')
        LetVarName = self.varName()


        arrayExpression = None
        if self.lexer.look()['token'] == '[':
            self.process('[')
            arrayExpression = self.expression()
            self.process(']')


        self.process('=')
        valueExpression = self.expression()
        self.process(';')


        return {
            'type': 'letStatement',
            'varName': LetVarName,
            'arrayExpression': arrayExpression,
            'valueExpression': valueExpression
        }

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
        # Analyse du premier terme de l'expression
        first_term = self.term()
        expression_parts = [first_term]  # Stocker l'expression pour la construction

        # Analyser les opérations suivantes et leurs termes
        while self.lexer.hasNext() and self.lexer.look()['token'] in {'+', '-', '*', '/', '&', '|', '<', '>', '='}:
            operator = self.lexer.next()['token']  # Récupérer l'opérateur
            next_term = self.term()  # Analyser le terme suivant
            expression_parts.append((operator, next_term))  # Ajouter l'opérateur et le terme à l'expression

        # Retourner une structure représentant l'expression
        return {
            'type': 'expression',
            'parts': expression_parts
        }

    def term(self):
        """
        term : integerConstant | stringConstant | keywordConstant
               | varName | varName '[' expression ']' | subroutineCall
               | '(' expression ')' | unaryOp term
        """
        token = self.lexer.look()  # Regarder le prochain token

        # Integer constant
        if token['type'] == 'integerConstant':
            self.lexer.next()  # Consommer le token
            return {'type': 'integerConstant', 'value': token['token']}

        # String constant
        elif token['type'] == 'stringConstant':
            self.lexer.next()  # Consommer le token
            return {'type': 'stringConstant', 'value': token['token']}

        # Keyword constant (true, false, null, this)
        elif token['type'] == 'keyword' and token['token'] in {'true', 'false', 'null', 'this'}:
            self.lexer.next()  # Consommer le token
            return {'type': 'keywordConstant', 'value': token['token']}

        # Parenthesized expression: '(' expression ')'
        elif token['token'] == '(':
            self.process('(')
            expression = self.expression()
            self.process(')')
            return {'type': 'expression', 'value': expression}

        # Unary operation: unaryOp term
        elif token['token'] in {'-', '~'}:  # '-' for negation, '~' for bitwise NOT
            unary_op = self.lexer.next()['token']  # Consommer l'opérateur unaire
            term = self.term()  # Appeler récursivement term
            return {'type': 'unaryOp', 'operator': unary_op, 'term': term}

        # Variable name, array access, or subroutine call
        elif token['type'] == 'identifier':
            identifier = self.lexer.next()['token']  # Récupérer le nom

            # Array access: varName '[' expression ']'
            if self.lexer.look()['token'] == '[':
                self.process('[')
                expression = self.expression()
                self.process(']')
                return {'type': 'arrayAccess', 'varName': identifier, 'index': expression}

            # Subroutine call: subroutineName '(' expressionList ')' or (className | varName) '.' subroutineName '(' expressionList ')'
            elif self.lexer.look()['token'] in {'(', '.'}:
                return self.subroutineCall(identifier)

            # Simple variable
            else:
                return {'type': 'varName', 'value': identifier}

        # Si aucun des cas ne correspond, lever une erreur
        else:
            self.error(token)

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

    #def process(self, expected_token):
        #token = self.lexer.next()  # Consomme le prochain token
        #print(f"Expected: {expected_token}, Got: {token['token']}")  # Affiche ce que tu reçois
        #if token is not None and token['token'] == expected_token:
        #    return token
        #else:
        #    print(f"Error: Expected {expected_token} but got {token['token']}")
        #    self.error(token)

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

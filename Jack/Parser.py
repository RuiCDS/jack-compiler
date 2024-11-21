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
        class_name = self.className()  # Nom de la classe
        self.process('{')

        class_vars = []
        while self.lexer.hasNext() and self.lexer.look()['token'] in {'static', 'field'}:
            class_vars += self.classVarDec()

        subroutines = []
        while self.lexer.hasNext() and self.lexer.look()['token'] in {'constructor', 'function', 'method'}:
            subroutines.append(self.subroutineDec())

        self.process('}')

        # Retourne une structure correcte

        return [{
            'type': 'class',
            'name': class_name,
            'class_vars': class_vars,
            'subroutines': subroutines
        }]

    def classVarDec(self):
        """
        classVarDec: ('static' | 'field') type varName (',' varName)* ';'
        """
        if self.lexer.look()['token'] in {'static', 'field'}:
            kind = self.lexer.next()['token']
        else:
            self.error(self.lexer.next())

        # Vérifier le type de la variable

        if self.lexer.look()['token'] in {'int', 'char', 'boolean'}:

            var_type = self.lexer.next()['token']

        elif self.lexer.look()['type'] == 'identifier':
            var_type = self.lexer.next()['token']
        else:
            self.error(self.lexer.next())

        name = self.varName()  # Liste de noms de variables

        res = [{
            'type': var_type,
            'kind': kind,  # 'static' ou 'field'
            'name': name  # Liste des noms
        }]


        # Ajouter les noms de variables supplémentaires
        while self.lexer.look()['token'] == ',':
            self.process(',')
            res.append({
            'type': var_type,
            'kind': kind,  # 'static' ou 'field'
            'var_names': self.varName()  # Liste des noms
        })

        self.process(';')

        return res

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
        subroutine_type = self.lexer.next()['token']  # constructor, function ou method
        return_type = self.lexer.next()['token']  # void ou type
        name = self.lexer.next()['token']  # Nom de la sous-routine

        self.process('(')
        parameters = self.parameterList()  # Liste des paramètres
        self.process(')')
        body = self.subroutineBody()  # Corps de la sous-routine

        return {
            'type': 'subroutineDec',
            'subroutine_type': subroutine_type,
            'return_type': return_type,
            'name': name,
            'parameters': parameters,
            'body': body
        }

    def parameterList(self):
        """
        parameterList: ((type varName) (',' type varName)*)?
        """
        parameters = []

        while self.lexer.hasNext() and self.lexer.look()['token'] != ')':
            if self.lexer.look()['token'] in {'void', 'char', 'int', 'boolean'}:
                param_type = self.lexer.next()['token']
                param_name = self.varName()
                parameters.append({'type': param_type, 'kind': 'argument','name': param_name})

            if self.lexer.look()['token'] == ',':
                self.process(',')

        return {
            'type': 'parameterList',
            'parameters': parameters
        }

    def subroutineBody(self):
        """
        subroutineBody: '{' varDec* statements '}'
        """

        self.process('{')  # Traiter le caractère '{'

        # Analyser les déclarations de variables locales
        local_vars = []
        while self.lexer.hasNext() and self.lexer.look()['token'] == 'var':
            local_vars+=self.varDec()  # Appel à varDec pour analyser les variables locales

        # Analyser les instructions dans le corps de la sous-routine
        statements = []
        while self.lexer.hasNext() and self.lexer.look()['token'] in {'let', 'if', 'while', 'do', 'return'}:
            statements.append(self.statement())  # Appel à statement pour analyser chaque instruction

        self.process('}')  # Traiter le caractère '}'

        # Retourner les informations du corps de la sous-routine
        return {
            'local_vars': local_vars,  # Les variables locales
            'statements': statements  # Les instructions
        }

    def varDec(self):
        """
        varDec: 'var' type varName (',' varName)* ';'
        """
        self.process('var')

        if self.lexer.look()['token'] in {'int', 'char', 'boolean'}:
            var_type = self.lexer.next()['token']
        elif self.lexer.look()['type'] == 'identifier':
            var_type = self.lexer.next()['token']
        else:
            self.error(self.lexer.next())

        name = self.varName() # Liste des noms de variables
        res = [{
            'type': var_type,
            'kind': 'local',
            'name': name  # Liste des noms
        }]

        # Ajouter les noms de variables supplémentaires
        while self.lexer.look()['token'] == ',':
            self.process(',')
            name = self.varName()  # Liste des noms de variables
            res.append({
                'type': var_type,
                'kind': 'local',
                'name': name  # Liste des noms
            })

        self.process(';')

        return res

    def className(self):
        """
        className: identifier
        """
        if self.lexer.hasNext() and self.lexer.look()['type'] == 'identifier':
            print(self.lexer.look())
            return self.lexer.next()['token']
        else:
            self.error(self.lexer.next())


    def subroutineName(self):
        """
        subroutineName: identifier
        """
        if self.lexer.look() is not None and self.lexer.look()['type'] == 'identifier':
            print(self.lexer.look())
            return self.lexer.next()['token']
        else:
            self.error(self.lexer.next())

    def varName(self):
        """
        varName: identifier
        """

        if self.lexer.look() is not None and self.lexer.look()['type'] == 'identifier':
            print(self.lexer.look())
            return self.lexer.next()['token']
        else:
            self.error(self.lexer.next())


    def statements(self):
        """
        statements : statements*
        """
        statements=[]
        while self.lexer.hasNext() and self.lexer.look()['token'] in {'let', 'if', 'while', 'do', 'return'}:
            statements.append(self.statement())
        return statements


    def statement(self):
        """
        statement : letStatements|ifStatement|whileStatement|doStatement|returnStatement
        """
        token = self.lexer.look()['token']

        if token == 'let':
            return self.letStatement
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

    @property
    def letStatement(self):
        """
        letStatement : 'let' varName ('[' expression ']')? '=' expression ';'
        """
        self.process('let')
        var_name = self.varName()

        array_expression = None
        if self.lexer.look()['token'] == '[':
            self.process('[')
            array_expression = self.expression()
            self.process(']')


        if self.lexer.look2()['type'] == 'identifier':
            self.process('=')
            if self.lexer.look2()['token'] in {'+', '-', '*', '/', '&', '|', '<', '>', '='}:
                value_expression = self.expression()
                self.process(';')

            elif self.lexer.look2()['token'] == ';':
                value_expression = self.varName()
                self.process(';')

            else:
                print("RUII", self.lexer.look())
                value_expression = self.subroutineCall()
                self.process(';')
        else:
            self.process('=')
            value_expression = self.expression()
            self.process(';')


        return {
            'type': 'letStatement',
            'var_name': var_name,
            'array_expression': array_expression,
            'value_expression': value_expression
        }

    def ifStatement(self):
        """
        ifStatement : 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        self.process('if')
        self.process('(')

        exp = self.expression()

        self.process(')')
        self.process('{')

        if_statements = self.statements()

        self.process('}')

        else_statements = None
        if self.lexer.look()['token'] == 'else':
            self.process('else')
            self.process('{')
            else_statements = self.statements()
            self.process('}')

        return {
            'type': 'ifStatement',
            'condtion': exp,
            'if_statements': if_statements,
            'else_statements': else_statements

        }

    def whileStatement(self):
        """
        whileStatement : 'while' '(' expression ')' '{' statements '}'
        """
        self.process('while')
        self.process('(')
        condition = self.expression()
        self.process(')')
        self.process('{')
        while_statements = self.statements()
        self.process('}')

        return {
            'type': 'whileStatement',
            'condtion': condition,
            'statements': while_statements

        }

    def doStatement(self):
        """
        doStatement : 'do' subroutineCall ';'
        """

        self.process('do')  # Consommer 'do'

        subroutine = self.subroutineCall()  # Appeler la sous-routine


        # Consommer ';'
        if self.lexer.look()['token'] != ';':
            raise SyntaxError(f"Expected ';' after do statement, found {self.lexer.look()}")
        self.process(';')

        return {
            'type': 'doStatement',
            'subroutine': subroutine
        }

    def returnStatement(self):
        """
        returnStatement : 'return' expression? ';'
        """
        self.process('return')

        if self.lexer.look()['token'] != ';':
            valeur = self.expression()

        else:
            valeur = None

        self.process(';')

        if valeur != None:
            return {
                'type': 'return',
                'value': valeur
            }
        else:
            return {
                'type': 'return'
            }


    def expression(self):
        """
        expression : term (op term)*
        """
        # Analyse du premier terme de l'expression
        first_term = self.term()
        expression_parts = [first_term]  # Stocker l'expression pour la construction

        # Analyser les opérations suivantes et leurs termes
        while self.lexer.hasNext() and self.lexer.look()['token'] in {'+', '-', '*', '/', '&', '|', '<', '>', '='}:
            operator = self.op()  # Récupérer l'opérateur
            next_term = self.term()  # Analyser le terme suivant
            expression_parts.append((operator['token'], next_term))  # Ajouter l'opérateur et le terme à l'expression

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
        if token['type'] == 'IntegerConstant':
            self.lexer.next()
            return {
                'type': 'integerConstant',
                'value': token['token']
            }

        # String constant
        elif token['type'] == 'StringConstant':
            self.lexer.next()
            return {
                'type': 'stringConstant',
                'value': token['token']
            }

        # Keyword constant (true, false, null, this)
        elif token['type'] == 'keyword' and token['token'] in {'true', 'false', 'null', 'this'}:
            self.lexer.next()
            return token['token']

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
                return self.subroutineCall()

            # Simple variable
            else:
                return {'type': 'varName', 'value': identifier}

        # Si aucun des cas ne correspond, lever une erreur
        else:
            self.error(token)


    def subroutineCall(self):


        # Récupérer le premier identifiant (le nom de la classe ou méthode)
        identifier = self.lexer.look()

        if identifier['type'] != 'identifier':
            raise SyntaxError(f"Expected identifier, found {identifier}")
        self.process(identifier['token'])  # Consommer l'identifiant (en fonction de sa valeur, pas de son type)

        # Vérifier le type d'appel (direct ou qualifié par un objet/une classe)
        if self.lexer.look()['token'] == '.':
            self.process('.')  # Consommer le symbole '.'
            subroutine_name = self.lexer.look()
            if subroutine_name['type'] != 'identifier':
                raise SyntaxError(f"Expected subroutine name after '.', found {subroutine_name}")
            self.process(subroutine_name['token'])  # Consommer le nom de la sous-routine
        else:
            subroutine_name = identifier

        # Vérifier l'ouverture de parenthèse
        if self.lexer.look()['token'] != '(':
            raise SyntaxError(f"Expected '(', found {self.lexer.look()}")
        self.process('(')  # Consommer '('

        # Récupérer la liste des expressions (arguments)
        expression_list = self.expressionList()

        # Vérifier la fermeture de parenthèse
        if self.lexer.look()['token'] != ')':
            raise SyntaxError(f"Expected ')', found {self.lexer.look()}")
        self.process(')')  # Consommer ')'

        # Retourner les informations de l'appel
        return {
            'type': 'subroutineCall',
            'classOrVar': identifier['token'],
            'subroutineName': subroutine_name['token'],
            'arguments': expression_list
        }

    def expressionList(self):
        """
        expressionList : (expression (',' expression)*)?
        """
        expression_list = []
        if self.lexer.look()['token'] != ')':
            expression_list.append(self.expression())
            while self.lexer.look()['token'] == ',':
                self.process(',')
                expression_list.append(self.expression())
        return expression_list


    def op(self):
        """
        op : '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
        """
        valid_ops = {'+', '-', '*', '/', '&', '|', '<', '>', '='}
        token = self.lexer.look()

        # Vérifie si le token est un opérateur valide
        if token['token'] in valid_ops:
            return self.lexer.next()  # Consomme et retourne l'opérateur
        else:
            self.error(token)  # Lève une erreur si le token n'est pas un opérateur

    def unaryOp(self):
        """
        unaryop : '-'|'~'
        """
        op = self.lexer.look()['token']
        if op in {'-', '~'}:
            return self.lexer.next()['token']  # Consomme et retourne l'opérateur
        else:
            self.error(f"Expected unary operator, found {op}")

    def KeywordConstant(self):
        """
        KeyWordConstant : 'true'|'false'|'null'|'this'
        """
        token = self.lexer.look()['token']

        if token == 'true':
            self.lexer.next()
            return True
        elif token == 'false':
            self.lexer.next()
            return False
        elif token == 'null':
            self.lexer.next()
            return None  #
        elif token == 'this':
            self.lexer.next()
            return 'this'
        else:
            self.error(f"Expected keyword constant, found {token}")

    def process(self, str):
        token = self.lexer.next()
        if (token is not None and token['token'] == str):
            print(token)
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

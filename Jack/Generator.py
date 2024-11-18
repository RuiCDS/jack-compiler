import sys
import Parser

class Generator:
    """Générateur de code VM à partir de l'arbre de syntaxe abstraite"""

    def __init__(self, file=None):
        if file is not None:
            self.parser = Parser.Parser(file)
            self.arbre = self.parser.jackclass()
            self.vmfile = open(self.arbre['name'] + '.vm', "w")  # Ouvre un fichier pour le code VM
            self.symbolClassTable = []  # Table des symboles pour la classe
            self.symbolRoutineTable = []  # Table des symboles pour la routine

    def jackclass(self, arbre):
        """Traite la classe entière."""
        # Exemple d'arbre de la classe : {'name': 'ClassName', 'varDec': [...], 'subroutine': [...] }
        self.writeLine(f"// Classe {arbre['name']}")
        self.writeLine(f"function {arbre['name']}.main 0")  # Fonction principale (0 argument)

        for var in arbre['varDec']:
            self.variable(var)  # Déclare les variables

        for routine in arbre['subroutine']:
            self.subroutineDec(routine)  # Déclare chaque sous-programme

    def variable(self, var):
        """Traite la déclaration d'une variable."""
        # Exemple de var : {'name': 'varName', 'kind': 'var', 'type': 'int'}
        self.symbolRoutineTable.append(var)  # Ajouter à la table des symboles locaux ou de classe
        self.writeLine(f"// Déclaration de la variable {var['name']}")

    def subroutineDec(self, routine):
        """Traite la déclaration d'une sous-routine."""
        # Exemple de routine : {'type': 'method', 'name': 'methodName', 'return': 'int', 'arguments': [...] }
        self.writeLine(f"// Déclaration de la sous-routine {routine['name']}")
        self.writeLine(f"{routine['type']} {routine['name']} 0")  # Ex. : function MyClass.method 0

        for var in routine['local']:
            self.variable(var)  # Déclare les variables locales

        for inst in routine['instructions']:
            self.statement(inst)  # Gère les instructions dans la sous-routine

    def statement(self, inst):
        """Traite une instruction."""
        match inst['type']:
            case 'let':
                self.letStatement(inst)
            case 'if':
                self.ifStatement(inst)
            case 'while':
                self.whileStatement(inst)
            case 'do':
                self.doStatement(inst)
            case 'return':
                self.returnStatement(inst)

    def letStatement(self, inst):
        """Traite une instruction de type let."""
        # Exemple d'instruction : {'type': 'let', 'variable': 'x', 'indice': expr, 'valeur': expr}
        self.writeLine(f"// Let statement: {inst['variable']}")
        self.expression(inst['indice'])  # Évalue l'indice si nécessaire
        self.writeLine(f"pop pointer 1")  # Stocke dans le segment local
        self.expression(inst['valeur'])  # Évalue la valeur à affecter
        self.writeLine(f"pop temp 0")  # Pop dans un registre temporaire
        self.writeLine(f"push temp 0")  # Push la valeur sur la pile
        self.writeLine(f"pop pointer 1")  # Affectation à l'indice donné

    def ifStatement(self, inst):
        """Traite une instruction de type if."""
        # Exemple : {'type': 'if', 'condition': expr, 'true': [instructions], 'false': [instructions]}
        self.writeLine(f"// If statement")
        self.expression(inst['condition'])
        self.writeLine(f"if-goto TRUE_{inst['line']}")
        self.writeLine(f"goto FALSE_{inst['line']}")
        self.writeLine(f"label TRUE_{inst['line']}")
        for i in inst['true']:
            self.statement(i)  # Exécute les instructions du bloc true
        self.writeLine(f"label FALSE_{inst['line']}")
        for i in inst['false']:
            self.statement(i)  # Exécute les instructions du bloc false

    def whileStatement(self, inst):
        """Traite une instruction de type while."""
        # Exemple : {'type': 'while', 'condition': expr, 'instructions': [...]}
        self.writeLine(f"// While statement")
        self.writeLine(f"label WHILE_{inst['line']}")
        self.expression(inst['condition'])
        self.writeLine(f"if-goto END_WHILE_{inst['line']}")
        for i in inst['instructions']:
            self.statement(i)  # Exécute les instructions du bloc while
        self.writeLine(f"goto WHILE_{inst['line']}")
        self.writeLine(f"label END_WHILE_{inst['line']}")

    def doStatement(self, inst):
        """Traite une instruction de type do."""
        # Exemple : {'type': 'do', 'classvar': 'className', 'name': 'methodName', 'argument': [expr]}
        self.writeLine(f"// Do statement")
        self.subroutineCall(inst)

    def returnStatement(self, inst):
        """Traite une instruction de type return."""
        # Exemple : {'type': 'return', 'valeur': expr}
        self.writeLine(f"// Return statement")
        if 'valeur' in inst:
            self.expression(inst['valeur'])
            self.writeLine(f"pop temp 0")
            self.writeLine(f"push temp 0")
        self.writeLine(f"return")

    def expression(self, exp):
        """Gère une expression (terme et opérateurs)."""
        for t in exp:
            self.term(t)

    def term(self, t):
        """Traite un terme dans une expression."""
        match t['type']:
            case 'int':
                self.writeLine(f"push constant {t['value']}")
            case 'string':
                self.writeLine(f"push constant {len(t['value'])}")
                for c in t['value']:
                    self.writeLine(f"push constant {ord(c)}")
                    self.writeLine(f"call String.appendChar 2")
            case 'constant':
                self.writeLine(f"push constant {t['value']}")
            case 'varName':
                self.writeLine(f"push local {t['name']}")  # ou class, depending on the scope
            case 'subroutineCall':
                self.subroutineCall(t)
            case 'expression':
                self.writeLine(f"// Sub-expression")
                self.expression(t['value'])

    def subroutineCall(self, call):
        """Traite un appel de sous-routine."""
        self.writeLine(f"// Subroutine call: {call['name']}")
        self.writeLine(f"call {call['classvar']}.{call['name']} {len(call['argument'])}")

    def writeLine(self, line):
        """Écrit une ligne dans le fichier VM."""
        self.vmfile.write(line + "\n")

    def error(self, message=''):
        """Gestion des erreurs."""
        print(f"SyntaxError: {message}")
        exit()

if __name__ == '__main__':
    file = sys.argv[1]  # Récupère le fichier source de la ligne de commande
    print('-----debut')
    generator = Generator(file)
    generator.jackclass(generator.arbre)  # Génère le code VM pour la classe entière
    print('-----fin')

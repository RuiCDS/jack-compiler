import sys
import Parser


class Generator:
    """Générateur de code VM à partir de l'arbre de syntaxe abstraite (AST)."""

    def __init__(self, file=None):
        if file is not None:
            self.parser = Parser.Parser(file)
            self.arbre = self.parser.jackclass()

            print("RUI")
            if not self.arbre or not isinstance(self.arbre, dict):
                self.error("L'arbre syntaxique (AST) n'a pas été correctement généré.")

            self.vmfile = open(self.arbre['name'] + '.vm', "w")  # Ouvre un fichier pour le code VM
            self.symbolClassTable = []  # Table des symboles pour la classe
            self.symbolRoutineTable = []  # Table des symboles pour la routine

    def jackclass(self, arbre):
        """Traite la classe entière."""
        if 'name' not in arbre or 'varDec' not in arbre or 'subroutine' not in arbre:
            self.error("Structure de classe invalide dans l'AST.")

        self.writeLine(f"// Classe {arbre['name']}")
        print(f"Début de la traduction de la classe : {arbre['name']}")

        for var in arbre['varDec']:
            self.variable(var)  # Déclare les variables

        for routine in arbre['subroutine']:
            self.subroutineDec(routine)  # Déclare chaque sous-programme

    def variable(self, var):
        """Traite la déclaration d'une variable."""
        if 'name' not in var or 'kind' not in var or 'type' not in var:
            self.error(f"Variable mal formée : {var}")

        self.symbolRoutineTable.append(var)  # Ajouter à la table des symboles locaux ou de classe
        self.writeLine(f"// Déclaration de la variable {var['name']}")

    def subroutineDec(self, routine):
        """Traite la déclaration d'une sous-routine."""
        if 'type' not in routine or 'name' not in routine or 'return' not in routine or 'local' not in routine or 'instructions' not in routine:
            self.error(f"Sous-routine mal formée : {routine}")

        self.writeLine(f"// Déclaration de la sous-routine {routine['name']}")
        self.writeLine(f"function {routine['name']} {len(routine['local'])}")  # Ex. : function MyClass.method 2

        for var in routine['local']:
            self.variable(var)  # Déclare les variables locales

        for inst in routine['instructions']:
            self.statement(inst)  # Gère les instructions dans la sous-routine

    def statement(self, inst):
        """Traite une instruction."""
        if 'type' not in inst:
            self.error(f"Instruction mal formée : {inst}")

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
            case _:
                self.error(f"Instruction inconnue : {inst['type']}")

    def letStatement(self, inst):
        """Traite une instruction de type let."""
        if 'variable' not in inst or 'valeur' not in inst:
            self.error(f"Let statement mal formé : {inst}")

        self.writeLine(f"// Let statement: {inst['variable']}")
        if 'indice' in inst:
            self.expression(inst['indice'])  # Évalue l'indice si nécessaire
            self.writeLine(f"pop pointer 1")  # Stocke dans le segment local
        self.expression(inst['valeur'])  # Évalue la valeur à affecter
        self.writeLine(f"pop local {inst['variable']}")  # Affecte à la variable

    def ifStatement(self, inst):
        """Traite une instruction de type if."""
        if 'condition' not in inst or 'true' not in inst or 'false' not in inst:
            self.error(f"If statement mal formé : {inst}")

        self.writeLine(f"// If statement")
        self.expression(inst['condition'])
        self.writeLine(f"if-goto TRUE_{inst['line']}")
        self.writeLine(f"goto FALSE_{inst['line']}")
        self.writeLine(f"label TRUE_{inst['line']}")
        for i in inst['true']:
            self.statement(i)
        self.writeLine(f"label FALSE_{inst['line']}")
        for i in inst['false']:
            self.statement(i)

    def whileStatement(self, inst):
        """Traite une instruction de type while."""
        if 'condition' not in inst or 'instructions' not in inst:
            self.error(f"While statement mal formé : {inst}")

        self.writeLine(f"// While statement")
        self.writeLine(f"label WHILE_{inst['line']}")
        self.expression(inst['condition'])
        self.writeLine(f"if-goto END_WHILE_{inst['line']}")
        for i in inst['instructions']:
            self.statement(i)
        self.writeLine(f"goto WHILE_{inst['line']}")
        self.writeLine(f"label END_WHILE_{inst['line']}")

    def doStatement(self, inst):
        """Traite une instruction de type do."""
        if 'classvar' not in inst or 'name' not in inst or 'argument' not in inst:
            self.error(f"Do statement mal formé : {inst}")

        self.writeLine(f"// Do statement")
        self.subroutineCall(inst)

    def returnStatement(self, inst):
        """Traite une instruction de type return."""
        self.writeLine(f"// Return statement")
        if 'valeur' in inst:
            self.expression(inst['valeur'])
        self.writeLine(f"return")

    def expression(self, exp):
        """Gère une expression (terme et opérateurs)."""
        if not isinstance(exp, list):
            self.error(f"Expression mal formée : {exp}")
        for t in exp:
            self.term(t)

    def term(self, t):
        """Traite un terme dans une expression."""
        if 'type' not in t:
            self.error(f"Terme mal formé : {t}")

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
                self.writeLine(f"push local {t['name']}")
            case 'subroutineCall':
                self.subroutineCall(t)
            case 'expression':
                self.writeLine(f"// Sub-expression")
                self.expression(t['value'])
            case _:
                self.error(f"Type de terme inconnu : {t['type']}")

    def subroutineCall(self, call):
        """Traite un appel de sous-routine."""
        if 'classvar' not in call or 'name' not in call or 'argument' not in call:
            self.error(f"Subroutine call mal formé : {call}")

        self.writeLine(f"// Subroutine call: {call['name']}")
        self.writeLine(f"call {call['classvar']}.{call['name']} {len(call['argument'])}")

    def writeLine(self, line):
        """Écrit une ligne dans le fichier VM."""
        self.vmfile.write(line + "\n")

    def close(self):
        """Ferme le fichier VM proprement."""
        self.vmfile.close()

    def error(self, message=''):
        """Gestion des erreurs."""
        print(f"Erreur : {message}")
        sys.exit(1)


if __name__ == '__main__':
    file = sys.argv[1]
    print('----- Début de la traduction -----')
    generator = Generator(file)
    generator.jackclass(generator.arbre)
    generator.close()
    print('----- Fin de la traduction -----')

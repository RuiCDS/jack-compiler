"""No comment"""
import sys
import Parser


class Generator:
    """No comment"""

    def __init__(self, file=None):
        if file is not None:
            self.parser = Parser.Parser(file)
            self.arbre = self.parser.jackclass()
            self.vmfile = open(self.arbre[0]['name'] + '.vm', "w")
            self.symbolClassTable = []
            self.symbolRoutineTable = []
            self.label_counter = 0


    def jackclass(self, arbre):
        """
            {'line': line, 'col': col, 'type': 'class', 'name': className,
            'varDec': [variable], 'subroutine':[subroutine]}
        """
        class_name = arbre[0]['name']

        for var in arbre[0]['class_vars']:
            self.variable(var)

        for subroutine in arbre[0]['subroutines']:
            self.subroutineDec(subroutine)

    def variable(self, var):
        """
        Gère l'ajout d'une variable dans la table des symboles.
        """


        # Vérifie que toutes les clés nécessaires sont présentes
        if not all(key in var for key in ('name', 'type', 'kind')):
            self.error(f"Variable mal formée : {var}")

        # Détermine la table des symboles appropriée
        if var['kind'] in {'static', 'field'}:
            table = self.symbolClassTable
        else:  # 'local' ou 'argument'
            table = self.symbolRoutineTable

        # Vérifie si une variable du même nom existe déjà
        for entry in table:
            if entry['name'] == var['name']:
                self.error(f"Variable déjà déclarée : {var['name']}")

        # Calcul de l'index pour cette variable
        index = len([entry for entry in table if entry['kind'] == var['kind']])

        # Création de l'entrée pour la table des symboles
        entry = {
            'name': var['name'],
            'type': var['type'],
            'kind': var['kind'],
            'index': index
        }

        # Ajout de l'entrée dans la table des symboles
        table.append(entry)

        # Debugging


    def subroutineDec(self, routine):
        """
        Génère le code VM pour une sous-routine.
        """
        subroutine_name = routine['name']
        subroutine_type = routine['subroutine_type']  # function, method, constructor
        return_type = routine['return_type']
        parameters = routine['parameters']['parameters']
        local_vars = routine['body']['local_vars']

        # Réinitialise la table des symboles pour cette sous-routine
        self.symbolRoutineTable = []

        # Ajoute les paramètres à la table des symboles
        for i, param in enumerate(parameters):
            self.symbolRoutineTable.append({
                'name': param['name'],  # Nom de l'argument
                'type': param['type'],  # Type (par ex., int)
                'kind': 'argument',  # Segment : argument
                'index': i  # Index de l'argument
            })

        # Ajoute les variables locales à la table des symboles
        for var in local_vars:
            self.variable(var)

        # Génère l'en-tête de la sous-routine
        num_locals = len(local_vars)
        self.vmfile.write(f"function {self.arbre[0]['name']}.{subroutine_name} {num_locals}\n")

        # Instructions spécifiques aux méthodes ou constructeurs
        if subroutine_type == 'method':
            self.vmfile.write("push argument 0\n")  # Référence à l'objet courant
            self.vmfile.write("pop pointer 0\n")  # Initialise `this`
        elif subroutine_type == 'constructor':
            num_fields = len([v for v in self.symbolClassTable if v['kind'] == 'field'])
            self.vmfile.write(f"push constant {num_fields}\n")  # Alloue l'espace pour les champs
            self.vmfile.write("call Memory.alloc 1\n")
            self.vmfile.write("pop pointer 0\n")  # Initialise `this`

        # Génère les instructions de la sous-routine
        for statement in routine['body']['statements']:
            self.statement(statement)

    def statement(self, inst):
        """
        Gère une instruction Jack et appelle la méthode appropriée pour la générer en VM.
        :param inst: dictionnaire décrivant l'instruction, par exemple :
            {'type': 'letStatement', ...}
        """
        match inst['type']:
            case 'letStatement':
                self.letStatement(inst)
            case 'ifStatement':
                self.ifStatement(inst)
            case 'whileStatement':
                self.whileStatement(inst)
            case 'doStatement':
                self.doStatement(inst)
            case 'return':
                self.returnStatement(inst)
            case _:
                self.error(f"Type d'instruction inconnu : {inst['type']}")

    def letStatement(self, inst):
        """
        Génère le code VM pour une instruction let.
        :param inst: Dictionnaire représentant un letStatement.
        """
        print(f"Traitement de letStatement : {inst}")

        # Vérifie si une valeur est assignée
        if 'value_expression' not in inst or inst['value_expression'] is None:
            self.error("value_expression manquant dans letStatement.")

        # Gère l'accès au tableau s'il y a une expression de tableau
        if 'array_expression' in inst and inst['array_expression'] is not None:
            # Accès au tableau (let myArray[2] = value)
            array_access = {
                'varName': inst['var_name'],
                'index': inst['array_expression']
            }
            value_expression = inst['value_expression']
            self.handleArrayAccess(array_access, value=value_expression)  # Utilise handleArrayAccess
        else:
            # Accès simple à une variable (let x = value)
            # Recherche la variable dans les tables de symboles
            var_entry = next(
                (v for v in self.symbolRoutineTable + self.symbolClassTable if v['name'] == inst['var_name']),
                None
            )
            if not var_entry:
                self.error(f"Variable {inst['var_name']} non trouvée.")

            # Génère l'expression pour la valeur assignée
            value_expression = inst['value_expression']
            if value_expression['type'] == 'subroutineCall':
                self.subroutineCall(value_expression)  # Appel à une méthode ou fonction
            else:
                self.expression(value_expression)  # Génère le code pour d'autres expressions

            # Génère l'instruction pop pour stocker la valeur
            segment = {
                'static': 'static',
                'field': 'this',
                'local': 'local',
                'argument': 'argument'
            }[var_entry['kind']]
            self.vmfile.write(f"pop {segment} {var_entry['index']}\n")

    def ifStatement(self, inst):
        """
        Génère le code VM pour une instruction if.
        :param inst: {'type': 'ifStatement', 'condition': dict, 'true': list, 'false': list or None}
        """
        label_true = f"IF_TRUE{self.label_counter}"
        label_end = f"IF_END{self.label_counter}"
        self.label_counter += 1

        # Générer le code pour la condition
        self.expression(inst['condition'])
        self.vmfile.write(f"if-goto {label_true}\n")

        # Générer le code pour le bloc else, s'il existe
        if inst['else_statements']:
            self.statement_list(inst['else_statements'])  # Instructions du bloc else
        self.vmfile.write(f"goto {label_end}\n")

        # Générer le label pour le bloc if
        self.vmfile.write(f"label {label_true}\n")
        self.statement_list(inst['if_statements'])  # Instructions du bloc if

        # Générer le label de fin
        self.vmfile.write(f"label {label_end}\n")

    def whileStatement(self, inst):
        """
        Génère le code VM pour une instruction while.
        """
        while_counter = self.label_counter
        self.label_counter += 1

        # Labels pour le début et la fin du while
        label_start = f"WHILE_EXP{while_counter}"
        label_end = f"WHILE_END{while_counter}"

        # Label de début du while
        self.vmfile.write(f"label {label_start}\n")

        # Générer le code pour la condition
        self.expression(inst['condition'])  # Utilise la clé 'condition'
        self.vmfile.write(f"not\n")  # Négatif de la condition
        self.vmfile.write(f"if-goto {label_end}\n")  # Sauter si la condition est fausse

        # Générer le code pour les instructions du bloc while
        for statement in inst['statements']:  # Utilise la clé 'statements'
            self.statement(statement)

        # Boucler au début
        self.vmfile.write(f"goto {label_start}\n")

        # Label de fin du while
        self.vmfile.write(f"label {label_end}\n")

    def doStatement(self, inst):
        """
        Génère le code VM pour une instruction do.
        :param inst: {'type': 'doStatement', 'subroutine': dict}
        """
        self.subroutineCall(inst['subroutine'])
        self.vmfile.write("pop temp 0\n")  # Détruit la valeur de retour (do n'en utilise pas)

    def returnStatement(self, inst):
        """
        Génère le code VM pour une instruction return.
        :param inst: {'type': 'return', 'valeur': dict or None}
        """
        if inst.get('valeur'):  # Si une valeur est retournée
            self.expression(inst['valeur'])
        else:
            self.vmfile.write("push constant 0\n")  # Retourne 0 par défaut (void)
        self.vmfile.write("return\n")

    def expression(self, exp):
        """
        Génère le code VM pour une expression.
        """
        print(f"Traitement de l'expression : {exp}")
        parts = exp['parts']
        # Génère le code pour le premier terme
        self.term(parts[0])

        # Traite les opérateurs et les termes suivants
        for i in range(1, len(parts), 2):  # Les opérateurs sont aux indices impairs
            operator = parts[i]
            next_term = parts[i + 1]
            self.term(next_term)

            # Génère le code VM pour l'opérateur
            if operator == '+':
                self.vmfile.write("add\n")
            elif operator == '-':
                self.vmfile.write("sub\n")
            elif operator == '*':
                self.vmfile.write("call Math.multiply 2\n")
            elif operator == '/':
                self.vmfile.write("call Math.divide 2\n")
            elif operator == '&':
                self.vmfile.write("and\n")
            elif operator == '|':
                self.vmfile.write("or\n")
            elif operator == '<':
                self.vmfile.write("lt\n")
            elif operator == '>':
                self.vmfile.write("gt\n")
            elif operator == '=':
                self.vmfile.write("eq\n")
            else:
                self.error(f"Opérateur inconnu : {operator}")

    def term(self, t):
        """
        Génère le code VM pour un terme.
        """
        if isinstance(t, dict):
            if t['type'] == 'keywordConstant':
                # Traitement des constantes mot-clés
                if t['value'] == 'true':
                    self.vmfile.write("push constant 0\n")
                    self.vmfile.write("not\n")  # true est représenté par ~0
                elif t['value'] in {'false', 'null'}:
                    self.vmfile.write("push constant 0\n")  # false et null sont identiques
                elif t['value'] == 'this':
                    self.vmfile.write("push pointer 0\n")  # this est représenté par pointer[0]
            elif t['type'] == 'integerConstant':
                self.vmfile.write(f"push constant {t['value']}\n")
            elif t['type'] == 'stringConstant':
                self.handleStringConstant(t['value'])
            elif t['type'] == 'varName':
                var_entry = next(
                    (v for v in self.symbolRoutineTable + self.symbolClassTable if v['name'] == t['value']), None)
                if not var_entry:
                    self.error(f"Variable {t['value']} non trouvée.")
                segment = {
                    'static': 'static',
                    'field': 'this',
                    'local': 'local',
                    'argument': 'argument'
                }[var_entry['kind']]
                self.vmfile.write(f"push {segment} {var_entry['index']}\n")
            elif t['type'] == 'unaryOp':
                self.term(t['term'])
                if t['operator'] == '-':
                    self.vmfile.write("neg\n")
                elif t['operator'] == '~':
                    self.vmfile.write("not\n")
            elif t['type'] == 'expression':
                self.expression(t)
            elif t['type'] == 'subroutineCall':
                self.subroutineCall(t)
            elif t['type'] == 'arrayAccess':
                # Gestion des accès aux tableaux
                self.handleArrayAccess(t)
            else:
                self.error(f"Type de terme inconnu : {t['type']}")
        else:
            self.error(f"Objet inattendu dans term : {t}")

    def subroutineCall(self, call):
        """
        Génère le code VM pour un appel de sous-routine.
        :param call: Dictionnaire décrivant l'appel, par exemple :
            {
                'type': 'subroutineCall',
                'classOrVar': 'Output',           # Nom de la classe ou de la variable
                'subroutineName': 'printInt',    # Nom de la sous-routine
                'arguments': [expression1, ...]  # Liste des expressions (arguments)
            }
        """
        # Déterminer si l'appel est une méthode ou une fonction
        class_or_var = call['classOrVar']  # Nom de la classe ou de la variable (ou None pour un appel direct)
        subroutine_name = call['subroutineName']  # Nom de la sous-routine
        arguments = call['arguments']  # Liste des arguments passés

        # Nombre initial d'arguments
        num_args = 0

        # Cas : appel d'une méthode d'une instance
        if class_or_var:
            # Vérifier si `classOrVar` est une variable dans la table des symboles
            var_entry = next((x for x in self.symbolRoutineTable + self.symbolClassTable if x['name'] == class_or_var),
                             None)

            if var_entry:
                # C'est une variable d'instance, donc il faut passer `this` comme premier argument
                segment = {
                    'static': 'static',
                    'field': 'this',
                    'local': 'local',
                    'argument': 'argument'
                }[var_entry['kind']]
                self.vmfile.write(f"push {segment} {var_entry['index']}\n")
                num_args += 1
                class_name = var_entry['type']  # La classe de l'objet est dans `type`
            else:
                # Sinon, c'est un appel à une classe statique
                class_name = class_or_var
        else:
            # Pas de `classOrVar`, c'est un appel direct (méthode de la même classe)
            self.vmfile.write("push pointer 0\n")  # Pousse `this` comme premier argument
            num_args += 1
            class_name = self.arbre[0]['name']  # Nom de la classe courante

        # Générer le code pour les arguments
        for arg in arguments:
            self.expression(arg)
            num_args += 1

        # Appeler la sous-routine
        self.vmfile.write(f"call {class_name}.{subroutine_name} {num_args}\n")

    def statement_list(self, statements):
        """
        Gère une liste d'instructions Jack et génère le code VM correspondant.
        :param statements: Liste de dictionnaires représentant les instructions.
        """
        for statement in statements:
            self.statement(statement)

    def handleStringConstant(self, string):
        """
        Gère les chaînes de caractères en générant le code VM pour créer et initialiser la chaîne.
        """
        # Appelle String.new pour allouer de l'espace pour la chaîne
        self.vmfile.write(f"push constant {len(string)}\n")  # Taille de la chaîne
        self.vmfile.write("call String.new 1\n")  # Appelle String.new

        # Ajoute chaque caractère à la chaîne
        for char in string:
            self.vmfile.write(f"push constant {ord(char)}\n")  # Code ASCII du caractère
            self.vmfile.write("call String.appendChar 2\n")  # Appelle String.appendChar

    def handleArrayAccess(self, array_access, value=None):
        print(f"Traitement de l'accès au tableau : {array_access}, valeur : {value}")

        # Adresse de base
        array_name = array_access['varName']
        var_entry = next((v for v in self.symbolRoutineTable + self.symbolClassTable if v['name'] == array_name), None)
        if not var_entry:
            self.error(f"Variable tableau {array_name} non trouvée.")
        segment = {
            'static': 'static',
            'field': 'this',
            'local': 'local',
            'argument': 'argument'
        }[var_entry['kind']]
        self.vmfile.write(f"push {segment} {var_entry['index']}\n")  # Adresse de base
        print(f"Base du tableau ({array_name}) : push {segment} {var_entry['index']}")

        # Index
        self.expression(array_access['index'])
        self.vmfile.write("add\n")  # Calcule l'adresse
        print("Ajout de l'index : add")

        if value:
            # Écriture dans le tableau
            self.expression(value)  # Évalue la valeur à écrire
            self.vmfile.write("pop temp 0\n")  # Stocke la valeur dans temp 0
            self.vmfile.write("pop pointer 1\n")  # Déplace l'adresse calculée dans pointer 1
            self.vmfile.write("push temp 0\n")  # Charge la valeur depuis temp 0
            self.vmfile.write("pop that 0\n")  # Écrit la valeur dans that
            print("Écriture de la valeur dans le tableau")
        else:
            # Lecture depuis le tableau
            self.vmfile.write("pop pointer 1\n")  # Déplace l'adresse calculée dans pointer 1
            self.vmfile.write("push that 0\n")  # Lit la valeur à l'adresse
            print("Lecture depuis le tableau")

    def error(self, message=''):
        print(f"SyntaxError: {message}")
        exit()


if __name__ == '__main__':
    file = sys.argv[1]  # Fichier Jack à lire
    print('-----debut')
    generator = Generator(file)
    generator.jackclass(generator.arbre)  # Utilise l'arbre généré par le Parser
    print('-----fin')

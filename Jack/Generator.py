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

    def subroutineDec(self, routine):
        """
        Génère le code VM pour une sous-routine.
        """
        # Extraire les informations de la routine
        subroutine_name = routine['name']
        subroutine_type = routine['subroutine_type']  # function, method, constructor
        return_type = routine['return_type']
        parameters = routine['parameters']['parameters']
        local_vars = routine['body']['local_vars']

        # Réinitialiser la table des symboles des sous-routines
        self.symbolRoutineTable = []

        # Si c'est une méthode, ajouter 'this' en tant qu'argument implicite
        if subroutine_type == 'method':
            self.symbolRoutineTable.append({
                'name': 'this',  # L'instance courante
                'type': self.arbre[0]['name'],  # Le nom de la classe courante
                'kind': 'argument',  # Segment : argument
                'index': 0  # Premier argument
            })

        # Ajouter les paramètres à la table des symboles
        for i, param in enumerate(parameters, start=1 if subroutine_type == 'method' else 0):
            self.symbolRoutineTable.append({
                'name': param['name'],  # Nom de l'argument
                'type': param['type'],  # Type de l'argument
                'kind': 'argument',  # Segment : argument
                'index': i  # Index de l'argument
            })

        # Ajouter les variables locales à la table des symboles
        for var in local_vars:
            self.variable(var)

        # Générer l'en-tête de la sous-routine
        num_locals = len(local_vars)
        self.vmfile.write(f"function {self.arbre[0]['name']}.{subroutine_name} {num_locals}\n")

        # Instructions spécifiques pour les méthodes et constructeurs
        if subroutine_type == 'method':
            self.vmfile.write("push argument 0\n")  # Empile la référence à l'objet courant
            self.vmfile.write("pop pointer 0\n")  # Initialise `this`
        elif subroutine_type == 'constructor':
            num_fields = len([v for v in self.symbolClassTable if v['kind'] == 'field'])
            self.vmfile.write(f"push constant {num_fields}\n")  # Alloue l'espace pour les champs
            self.vmfile.write("call Memory.alloc 1\n")  # Appelle Memory.alloc
            self.vmfile.write("pop pointer 0\n")  # Initialise `this`

        # Générer le code des instructions de la sous-routine
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
        # Vérifie si une valeur est assignée
        if 'value_expression' not in inst or inst['value_expression'] is None:
            self.error("value_expression manquant dans letStatement.")

        value_expression = inst['value_expression']

        # Vérifie si c'est une affectation à un tableau
        if inst['array_expression']:
            # Gestion des tableaux : arr[i] = value
            array_expression = inst['array_expression']  # Expression de l'indice (i)
            var_entry = next(
                (v for v in self.symbolRoutineTable + self.symbolClassTable if v['name'] == inst['var_name']),
                None)
            if not var_entry:
                self.error(f"Variable {inst['var_name']} non trouvée.")

            # Calcul de l'adresse : base + index
            segment = {
                'static': 'static',
                'field': 'this',
                'local': 'local',
                'argument': 'argument'
            }[var_entry['kind']]
            self.vmfile.write(f"push {segment} {var_entry['index']}\n")  # Base du tableau
            self.expression(array_expression)  # Calcul de l'indice (i)
            self.vmfile.write("add\n")  # Adresse finale : base + i

            # Évalue `value_expression` et stocke temporairement
            self.expression(value_expression)
            self.vmfile.write("pop temp 0\n")  # Stocker la valeur temporairement

            # Stocker la valeur dans `that`
            self.vmfile.write("pop pointer 1\n")
            self.vmfile.write("push temp 0\n")
            self.vmfile.write("pop that 0\n")

        else:
            # Affectation normale (pas un tableau)
            var_entry = next(
                (v for v in self.symbolRoutineTable + self.symbolClassTable if v['name'] == inst['var_name']),
                None)
            if not var_entry:
                self.error(f"Variable {inst['var_name']} non trouvée.")

            # Évalue `value_expression`
            if value_expression['type'] in {'integerConstant', 'varName', 'keywordConstant', 'stringConstant'}:
                self.term(value_expression)
            elif value_expression['type'] == 'expression':
                self.expression(value_expression)
            elif value_expression['type'] == 'unaryOp':
                operator = value_expression['operator']
                term = value_expression['term']
                self.term(term)
                if operator == '-':
                    self.vmfile.write("neg\n")
                elif operator == '~':
                    self.vmfile.write("not\n")
            elif value_expression['type'] == 'binaryOp':  # Nouveau cas pour les opérateurs binaires
                left = value_expression['left']
                operator = value_expression['operator']
                right = value_expression['right']
                self.term(left)
                self.term(right)
                self.vmfile.write({
                                      '+': 'add',
                                      '-': 'sub',
                                      '*': 'call Math.multiply 2',
                                      '/': 'call Math.divide 2',
                                      '&': 'and',
                                      '|': 'or',
                                      '<': 'lt',
                                      '>': 'gt',
                                      '=': 'eq',
                                  }[operator] + "\n")
            elif value_expression['type'] == 'subroutineCall':
                self.subroutineCall(value_expression)

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
        self.expression(inst['condition'])
        self.vmfile.write("not\n")  # Négatif de la condition
        self.vmfile.write(f"if-goto {label_end}\n")  # Sauter si la condition est fausse

        # Générer le code pour les instructions du bloc while
        for statement in inst['statements']:
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
        :param inst: {'type': 'return', 'value': dict or None}
        """
        if inst.get('value'):  # Utilise 'value' au lieu de 'valeur'
            self.expression(inst['value'])  # Génère le code pour l'expression de retour
        else:
            self.vmfile.write("push constant 0\n")  # Retourne 0 par défaut (void)
        self.vmfile.write("return\n")

    def expression(self, exp):
        """
        Génère le code VM pour une expression.
        :param exp: Dictionnaire représentant l'expression Jack.
        """
        # Décapsuler une expression imbriquée directement
        if 'value' in exp and exp['type'] == 'expression':
            exp = exp['value']  # Décapsule directement si c'est une expression imbriquée

        # Cas : Accès à un tableau
        if isinstance(exp, dict) and exp.get('type') == 'arrayAccess':
            self.handleArrayAccess(exp)
            return

        # Cas : Constantes, variables ou termes simples
        if exp['type'] in {'varName', 'integerConstant', 'stringConstant', 'keywordConstant'}:
            self.term(exp)  # Génère directement le code pour le terme
            return

        # Cas : Opérateurs unaires
        if exp['type'] == 'unaryOp':
            operator = exp['operator']
            term = exp['term']
            self.term(term)  # Génère le code pour le terme
            # Applique l'opérateur unaire
            if operator == '-':
                self.vmfile.write("neg\n")
            elif operator == '~':
                self.vmfile.write("not\n")
            else:
                raise ValueError(f"Opérateur unaire inconnu : {operator}")
            return

        # Cas : Appel de sous-routine
        if exp['type'] == 'subroutineCall':
            self.subroutineCall(exp)  # Génère le code pour l'appel de sous-routine
            return

        # Cas : Expressions complexes avec opérateurs binaires
        if 'parts' in exp:
            parts = exp['parts']
            if len(parts) % 2 == 0:
                raise ValueError("Expression mal formée : nombre pair d'éléments dans 'parts'.")

            # Génère le code pour le premier terme
            self.term(parts[0])

            # Traite les paires (opérateur, terme)
            for i in range(1, len(parts), 2):
                operator = parts[i]
                next_term = parts[i + 1]

                # Génère le code pour le prochain terme
                self.term(next_term)

                # Applique l'opérateur
                op_map = {
                    '+': "add\n",
                    '-': "sub\n",
                    '*': "call Math.multiply 2\n",
                    '/': "call Math.divide 2\n",
                    '&': "and\n",
                    '|': "or\n",
                    '<': "lt\n",
                    '>': "gt\n",
                    '=': "eq\n"
                }
                if operator in op_map:
                    self.vmfile.write(op_map[operator])
                else:
                    raise ValueError(f"Opérateur inconnu : {operator}")
        else:
            raise ValueError(f"Expression mal formée ou inconnue : {exp}")

    def term(self, t):
        """
        Génère le code VM pour un terme.
        """
        if isinstance(t, dict):
            if t['type'] == 'keywordConstant':
                # Traitement des constantes mot-clés
                if t['value'] == 'true':
                    self.vmfile.write("push constant 1\n")
                    self.vmfile.write("neg\n")  # true est représenté par -1
                elif t['value'] in {'false', 'null'}:
                    self.vmfile.write("push constant 0\n")  # false et null sont identiques
                elif t['value'] == 'this':
                    self.vmfile.write("push pointer 0\n")  # this est représenté par pointer[0]
            elif t['type'] == 'integerConstant':
                self.vmfile.write(f"push constant {t['value']}\n")
            elif t['type'] == 'stringConstant':
                self.handleStringConstant(t['value'][1:-1])  # Enlève les guillemets
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
        # Initialiser les variables nécessaires
        class_or_var = call['classOrVar']  # Nom de la classe ou de la variable
        subroutine_name = call['subroutineName']  # Nom de la sous-routine
        arguments = call['arguments']  # Liste des arguments
        num_args = 0  # Nombre d'arguments effectivement passés

        if class_or_var:
            # Vérifier si `classOrVar` est une variable d'instance
            var_entry = next(
                (x for x in self.symbolRoutineTable + self.symbolClassTable if x['name'] == class_or_var),
                None
            )

            if var_entry:
                # Si `classOrVar` est une variable d'instance
                segment = {
                    'static': 'static',
                    'field': 'this',
                    'local': 'local',
                    'argument': 'argument'
                }[var_entry['kind']]
                self.vmfile.write(f"push {segment} {var_entry['index']}\n")
                num_args += 1
                class_name = var_entry['type']  # La classe de l'objet
            else:
                # Sinon, `classOrVar` est une classe (appel statique)
                class_name = class_or_var
        else:
            # Pas de `classOrVar` -> appel à une méthode de l'instance courante
            self.vmfile.write("push pointer 0\n")
            num_args += 1
            class_name = self.arbre[0]['name']  # Nom de la classe courante

        # Générer le code pour chaque argument
        for arg in arguments:
            self.expression(arg)
            num_args += 1

        # Générer l'appel de sous-routine
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
        :param string: La chaîne de caractères à traiter (type `str`).
        """
        # Vérifie que l'entrée est bien une chaîne de caractères
        if not isinstance(string, str):
            raise ValueError(f"Invalid string constant: {string}")

        # Appelle String.new pour allouer de l'espace pour la chaîne
        self.vmfile.write(f"push constant {len(string)}\n")  # Taille de la chaîne
        self.vmfile.write("call String.new 1\n")  # Appelle String.new pour créer l'objet chaîne

        # Ajoute chaque caractère à la chaîne, un par un
        for char in string:
            ascii_value = ord(char)  # Code ASCII du caractère
            self.vmfile.write(f"push constant {ascii_value}\n")  # Empile le code ASCII
            self.vmfile.write("call String.appendChar 2\n")  # Ajoute le caractère à la chaîne

    def handleArrayAccess(self, t):
        """
        Génère le code VM pour un accès à un tableau.
        :param t: Dictionnaire représentant un accès à un tableau.
            {
                'varName': 'nomDuTableau',
                'index': dict,  # Expression représentant l'indice
                'isAssignment': bool  # Indique si c'est une affectation (optionnel)
            }
        """
        var_name = t['varName']
        index_expression = t['index']

        # Chercher la variable dans les tables de symboles
        var_entry = next((v for v in self.symbolRoutineTable + self.symbolClassTable if v['name'] == var_name), None)
        if not var_entry:
            raise ValueError(f"Variable {var_name} non trouvée.")
        if var_entry['type'] != 'Array':
            raise TypeError(f"Variable {var_name} n'est pas de type Array.")

        # Étape 1 : Pousser la base du tableau
        segment = {
            'static': 'static',
            'field': 'this',
            'local': 'local',
            'argument': 'argument'
        }[var_entry['kind']]
        self.vmfile.write(f"push {segment} {var_entry['index']}\n")  # Base du tableau

        # Étape 2 : Calculer l'adresse (base + index)
        self.expression(index_expression)  # Évaluer l'expression de l'indice
        self.vmfile.write("add\n")  # Adresse finale = base + index

        # Étape 3 : Charger ou affecter la valeur
        if t.get('isAssignment', False):  # Si c'est une affectation
            # Référencer `that` à l'adresse calculée
            self.vmfile.write("pop pointer 1\n")
            # Affecter la valeur au tableau
            self.vmfile.write("pop that 0\n")
        else:  # Sinon, lire la valeur
            # Référencer `that` à l'adresse calculée
            self.vmfile.write("pop pointer 1\n")
            # Charger la valeur du tableau
            self.vmfile.write("push that 0\n")

    def error(self, message=''):
        print(f"SyntaxError: {message}")
        exit()


if __name__ == '__main__':
    file = sys.argv[1]  # Fichier Jack à lire
    print('-----debut')
    generator = Generator(file)
    generator.jackclass(generator.arbre)  # Utilise l'arbre généré par le Parser
    print('-----fin')

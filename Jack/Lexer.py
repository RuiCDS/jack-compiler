import re
import sys
import Reader  # Vous devez avoir une classe Reader pour que ce code fonctionne


class Lexer:
    """Analyseur lexical pour lire les tokens depuis un fichier source."""

    def __init__(self, file):
        self.reader = Reader.Reader(file)
        # Initialise les tokens à lire, en les remplissant avec les deux premiers tokens.
        self.tokens = [self._read(), self._read()]

    def _comment(self):
        """Gestion des commentaires (lignes et blocs)"""
        t = self.reader.next()
        if t is None:
            return None
        if t['char'] == '/':  # Commentaire sur une seule ligne
            while t is not None and t['char'] != '\n':
                t = self.reader.next()
            return None
        elif t['char'] == '*':  # Commentaire sur plusieurs lignes
            while True:
                while t is not None and t['char'] != '*':
                    t = self.reader.next()
                if t is not None:
                    t = self.reader.next()
                if t is not None and t['char'] == '/':
                    self.reader.next()  # Consomme le '/'
                    return None
        return None

    def _skip(self):
        """Ignore les espaces et caractères inutiles."""
        self.reader.next()

    def _toke(self):
        """Gestion des identifiants (variables, noms de fonction, etc.)"""
        res = ''
        while self.reader.hasNext() and re.fullmatch(r'[a-zA-Z0-9_]', self.reader.look()['char']):
            t = self.reader.next()  # Consomme les caractères valides
            res += t['char']
        return res

    def _stringConstant(self):
        """Gestion des chaînes de caractères avec caractères spéciaux"""
        res = ""  # Variable pour accumuler les caractères de la chaîne
        t = self.reader.next()
        t = self.reader.next()# Consommer le guillemet d'ouverture

        # Si la chaîne est vide
        if not self.reader.hasNext():
            return '""'  # Retourne une chaîne vide si rien n'est après les guillemets

        while t is not None and t['char'] != '"':  # Tant que ce n'est pas le guillemet de fin
            res += t['char']  # Ajouter le caractère à la chaîne
            t = self.reader.next() # Lire le caractère suivant


        if t is None or t['char'] != '"':  # Vérification que nous avons bien rencontré un guillemet de fin
            print("Error: Unmatched quotes in string")
            return '""'  # Retourner une chaîne vide en cas d'erreur

        return '"' + res + '"'  # Retourner la chaîne complète incluant les guillemets

        while t is not None and t['char'] != '"':  # Tant que ce n'est pas la fin de la chaîne
            if t['char'] == '\n':  # Pour éviter de laisser passer des sauts de ligne dans la chaîne
                raise SyntaxError(f"Unclosed string constant at line {self.line}, col {self.col}")
            res += t['char']
            t = self.reader.next()

        res += '"'  # Ajouter le guillemet de fin
        print(f"String constant read: {res}")  # Pour débogage
        return res

    def next(self):
        """Renvoie le prochain token"""
        res = self.tokens[0]
        self.tokens[0] = self.tokens[1]
        self.tokens[1] = self._read()
        return res

    def _read(self):
        """Lecture des tokens (identifier, opérateur, mot-clé, etc.)"""
        token = None
        while self.reader.hasNext() and token is None:
            self.line = self.reader._line
            self.col = self.reader._col
            t = self.reader.look()
            if t is None:  # Vérification si t est None avant de l'utiliser
                return None  # Si t est None, on retourne None
            char = t['char']
            match char:
                case '/':  # Détection des commentaires
                    if self._comment() is not None:
                        token = "/"
                case '(' | ')' | '[' | ']' | '{' | '}' | ',' | ';' | '=' | '.' | '+' | '-' | '*' | '&' | '|' | '~' | '<' | '>':
                    token = char  # Symbole comme parenthèses, opérateurs, etc.
                    self._skip()
                case ' ' | '\t' | '\n':  # Ignore les espaces, tabulations, et sauts de ligne
                    self._skip()
                case char if re.fullmatch(r'[a-zA-Z0-9_]', char):  # Gestion des identifiants
                    token = self._toke()
                case '"':  # Gestion des chaînes de caractères
                    token = self._stringConstant()
                case _:
                    print(f'SyntaxError : line={self.line}, col={self.col}')
                    exit()

        if token is None:
            return None
        else:
            pattern = self._pattern()
            group = pattern.fullmatch(token)
            if group is None:
                print(f'SyntaxError (line={self.line}, col={self.col}): {token}')
                exit()
            else:
                return {'line': self.line, 'col': self.col, 'type': group.lastgroup, 'token': token}

    def hasNext(self):
        """Indique s'il reste des tokens à lire."""
        return self.tokens[0] is not None

    def hasNext2(self):
        """Indique s'il reste un token après le prochain."""
        return self.tokens[1] is not None

    def look(self):
        """Regarde le prochain token sans avancer le lecteur."""
        return self.tokens[0]

    def look2(self):
        """Regarde le token suivant sans avancer le lecteur."""
        return self.tokens[1]

    def _pattern(self):
        """Expression régulière pour identifier les symboles, mots-clés, identifiants, etc."""
        return re.compile(r"""
            (?P<symbol>[()[\]{},;=.+\-*/&|~<>]) |
            (?P<keyword>class|constructor|method|function|int|boolean|char|void|var|static|field|let|do|if|else|while|return|true|false|null|this) |
            (?P<identifier>[a-zA-Z_][a-zA-Z0-9_]*) |  # Identifiant (nom de variable ou fonction)
            (?P<StringConstant>"(?:[^"\n]|\\")*") |  # Chaîne de caractères, permet les échappements comme \"
            (?P<IntegerConstant>[0-9]+)  # Nombre entier
        """, re.X)

    def __iter__(self):
        """Retourne l'objet pour qu'il soit itérable."""
        return self

    def __next__(self):
        """Retourne le prochain token."""
        if self.hasNext():
            return self.next()
        else:
            raise StopIteration


if __name__ == "__main__":
    file = sys.argv[1]  # Récupère le nom du fichier depuis la ligne de commande
    print('-----debut')
    lexer = Lexer(file)
    for token in lexer:  # Parcourt tous les tokens générés par le lexer
        print(token)
    print('-----fin')

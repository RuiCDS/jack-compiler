"""
Prototype de code pour répondre à la question 9 du TP1
Vous avez juste à remplacer la chaine de caractères retournée de chaques opérations par du code assembleur.
Vous pouvez aussi ajouter de nouvelles opérations en suivant le même modèle
"""

import re


class ParserBob:
    def __init__(self, programme):
        self.programme = programme.split(' ')

    def push(self, commande):
        return f"""// push : {commande}
    @{commande}     // Charger la valeur ou la variable {commande}
    D=A             // Stocker la valeur dans D (ou A pour une constante)
    @SP             // Accéder à la pile
    A=M             // Accéder à l'adresse pointée par SP
    M=D             // Stocker la valeur de D au sommet de la pile
    @SP             // Accéder à nouveau au pointeur de pile
    M=M+1           // Incrémenter SP pour préparer le prochain emplacement
    """

    def label(self, commande):
        return f"""// label : {commande}
        ({commande}) // Def le label {commande} pour le saut

            """ if commande[0] != '(' else \
        f""" // label : {commande}
        {commande}      // Def le label {commande} pour le saut"""


    def add(self, commande):
        return f"""// add : {commande}
    @SP           // Accéder au sommet de la pile
    AM=M-1        // Déréférencer l'adresse du sommet, décrémenter SP
    D=M           // Charger la première valeur dans le registre D
    @SP           // Accéder à nouveau au sommet de la pile
    AM=M-1        // Décrémenter SP pour obtenir la deuxième valeur
    M=D+M         // Ajouter la valeur en D à la valeur sur la pile, stocker le résultat à l'adresse du sommet
    @SP           // Accéder à nouveau au sommet
    M=M+1         // Incrémenter SP pour préparer le sommet suivant
    """


    def equal(self, commande):
        return f"""// equal : {commande}
    @SP           // Accéder au sommet de la pile
    AM=M-1        // Décrémenter SP et accéder à la première valeur
    D=M           // Charger la première valeur dans D
    @SP           // Accéder à nouveau à la pile
    AM=M-1        // Décrémenter SP pour obtenir la deuxième valeur
    D=D-M         // Soustraire la deuxième valeur de la première (D contient le résultat)
    @EQUAL_TRUE_{commande}  // Aller à l'étiquette EQUAL_TRUE si le résultat est zéro (égalité)
    D;JEQ         // Si D == 0, alors les valeurs sont égales
    @SP           // Si non égal, on place 0 sur la pile
    A=M           // Accéder au sommet de la pile
    M=0           // Placer 0 (faux) au sommet
    @EQUAL_END_{commande}   // Sauter à la fin
    0;JMP
(EQUAL_TRUE_{commande})
    @SP           // Si égal, on place 1 sur la pile
    A=M
    M=-1         // Placer -1 (vrai) au sommet
(EQUAL_END_{commande})
    @SP           // Incrémenter SP
    M=M+1
    """

    def load(self, commande):
        return f"""// load : {commande}
    @{commande}   // Charger la valeur ou la variable {commande}
    D=M           // Charger la valeur de {commande} dans D
    @SP           // Accéder à la pile
    A=M           // Accéder à l'adresse pointée par SP
    M=D           // Stocker la valeur de D au sommet de la pile
    @SP           // Accéder à nouveau au pointeur de pile
    M=M+1         // Incrémenter SP
    """

    def store(self, commande):
        return f"""// store : {commande}
    @SP           // Accéder au sommet de la pile
    AM=M-1        // Décrémenter SP et accéder à la valeur au sommet de la pile
    D=M           // Stocker la valeur dans D
    @{commande}   // Accéder à l'emplacement {commande} où la valeur doit être stockée
    M=D           // Stocker la valeur dans {commande}
    """

    def JEQ(self, commande):
        return f"""// jump if equal : {commande}
    @SP           // Accéder au sommet de la pile
    AM=M-1        // Décrémenter SP pour obtenir la valeur
    D=M           // Charger la valeur dans D
    @{commande}   // Aller au label {commande} si la valeur est égale à 0
    D;JEQ         // Si D == 0, faire un saut au label
    """

    def pattern(self):
        return re.compile(r"""
        (?P<ADD>\+) | # Addition
        (?P<EQUAL>=) | # Égalité
        (?P<LOAD><-) | # Chargement
        (?P<STORE>->) | # Stockage
        (?P<JUMP>JEQ|JNE) | # Jump conditionnel
        (?P<LABEL>\([a-zA-Z]+\)) | # Labels
        (?P<INT>[0-9]+|[a-zA-Z]+) # Entiers ou variables
        """, re.X)

    def parse(self):
        self.asm = []
        pattern = self.pattern()
        for commande in self.programme:
            group = pattern.fullmatch(commande)
            if group is None:
                print('SyntaxError : ' + commande)
                exit()

            match group.lastgroup:
                case 'INT':
                    self.asm.append(self.push(commande))
                case 'LABEL':
                    self.asm.append(self.label(commande))
                case 'ADD':
                    self.asm.append(self.add(commande))
                case 'EQUAL':
                    self.asm.append(self.equal(commande))
                case 'STORE':
                    self.asm.append(self.store(commande))
                case 'LOAD':
                    self.asm.append(self.load(commande))
                case 'JUMP':
                    self.asm.append(self.JEQ(commande))
                case _:
                    print('Groupe oublié : ' + commande)
                    exit()
        return "\n".join(self.asm)

    def bootstrap(self):
        return """// Bootstrap
    @1   // Initialiser SP à 1
    D=A
    @SP
    M=D
    """


if __name__ == "__main__":
    programme = input('Prog: ')
    bob = ParserBob(programme)
    asm = bob.parse()
    print(bob.bootstrap())
    print(asm)
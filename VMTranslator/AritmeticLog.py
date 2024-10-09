import Generator

class ArithmeticLog:

    def __init__(self):
        pass

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




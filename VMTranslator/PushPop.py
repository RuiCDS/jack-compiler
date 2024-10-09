class PushPop:
    
    def __init__(self, command):
        pass
    
    def _commandpushconstant(self, command, commande=None):
        """No comment"""
        parameter = command['parameter']
        return f"""\t//{command['type']} {command['segment']} {parameter}
    @{commande}     // Charger la valeur ou la variable {commande}
    D=A             // Stocker la valeur dans D (ou A pour une constante)
    @SP             // Accéder à la pile
    A=M             // Accéder à l'adresse pointée par SP
    M=D             // Stocker la valeur de D au sommet de la pile
    @SP             // Accéder à nouveau au pointeur de pile
    M=M+1           // Incrémenter SP pour préparer le prochain emplacement"""

    def _commandcall(self, command):
        """No comment"""
        return f"""\t//{command['type']} {command['function']} {command['parameter']}
    Code assembleur de {command}\n"""




class PushPop:
    
    def __init__(self, command):
        pass

    def commandpushpop(self, command):



    def _commandpushconstant(self, command):
        """No comment"""
        parameter = command['parameter']
        return f"""\t//{command['type']} {command['segment']} {parameter}
        @{parameter}     // Charger la valeur ou la variable {parameter}
        D=A             // Stocker la valeur dans D (ou A pour une constante)
        @SP             // Accéder à la pile
        A=M             // Accéder à l'adresse pointée par SP
        M=D             // Stocker la valeur de D au sommet de la pile
        @SP             // Accéder à nouveau au pointeur de pile
        M=M+1           // Incrémenter SP pour préparer le prochain emplacement"""

    def _commandpushsegment(selfself,command):
        """No comment"""
        segment=command['segment']
        parameter = command['parameter']
        if segment == 'local':
            base='LCL'
        elif segment == 'argument':
            base='ARG'
        elif segment == 'this':
            base='THIS'
        elif segment == 'that':
            base='THAT'


        return f"""\t//{command['type']} {segment} {parameter}
        @{base}
        D=M             
        @{parameter}
        A=D+A
        D=M             // Charger la première valeur dans le registre D
        @SP
        A=M
        M=D
        @SP
        M=M+1
        """

    def _commandpushstatic(self,command,commande=None):
        """No comment"""
        parameter = command['parameter']


        
        
        
        






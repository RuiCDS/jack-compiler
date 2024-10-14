class ArithmeticLog:

    def __init__(self):
        pass

    def execute(self, commande):
        type_cmd = commande['type']

        match type_cmd:
            case 'add':
                return self.add(commande)
            case 'sub':
                return self.sub(commande)
            case 'equal':
                return self.equal(commande)
            case 'greater':
                return self.greater(commande)
            case 'lower':
                return self.lower(commande)
            case 'negative':
                return self.negative(commande)
            case 'and':
                return self.AND(commande)


    def add(self, commande):
        return f"""// add : {commande}
        @SP
        A=M
        A=A-1
        D=M     //On stock dans D la deuxième valeur
        M=0
        @SP
        M=M-1
        @SP
        A=M
        A=A-1
        M=D+M       //On ajoute la deuxième valeur à la première
        """

    def sub(self, commande):
        return f"""// sub : {commande}
        @SP
        A=M
        A=A-1
        D=M     //On stock dans D la deuxième valeur
        M=0
        @SP
        M=M-1
        @SP
        A=M
        A=A-1
        M=M-D       //On soustrait la deuxième valeur à la première
        """

    def equal(self, commande):
        return f"""// equal : {commande}
        @SP
        //Aller a la première valeur
        A=M
        A=A-1
        D=M     //On stock dans D la deuxième valeur
        A=A-1
        M=M-D       //On stock la différence entre les deux valeurs à l'emplacement de la première
        @SP
        M=M-1
        A=M
        M=0     //On enlève la deuxième valeur
        //Mettre l'emplacement de la première valeur à -1 si elle est différente de 0
        @SP     //Début condition JUMP (si v1=V2)
        A=M
        A=A-1
        D=M
        @END
        D;JNE       //Fin condition JUMP (si v1!=V2)
        @0
        D=A-1       //D = -1
        @SP
        A=M
        A=A-1
        M=D     //Emplacement de la première valeur = -1
        (END)
        """

    def greater(self, commande):
        return f"""// greater: {commande}
        //Vérifie si val1 > val2
        //Val1=-1 if true else 0
        @SP
        A=M
        A=A-1
        D=M     //On stock dans D la deuxième valeur
        M=0
        @SP
        M=M-1       //val2 dépilée
        @SP
        A=M
        A=A-1
        M=M-D       //On soustrait la deuxième valeur à la première
        D=M
        @IF_TRUE
        D;JGT
        @SP
        A=M
        A=A-1
        M=0
        @END
        0;JMP
        (IF_TRUE)
        @0
        D=A-1
        @SP
        A=M
        A=A-1
        M=D
        (END)
        """

    def lower(self, commande):
        return f"""// greater: {commande}
                //Vérifie si val1 > val2
                //Val1=-1 if true else 0
                @SP
                A=M
                A=A-1
                D=M     //On stock dans D la deuxième valeur
                M=0
                @SP
                M=M-1       //val2 dépilée
                @SP
                A=M
                A=A-1
                M=M-D       //On soustrait la deuxième valeur à la première
                D=M
                @IF_TRUE
                D;JLT
                @SP
                A=M
                A=A-1
                M=0
                @END
                0;JMP
                (IF_TRUE)
                @0
                D=A-1
                @SP
                A=M
                A=A-1
                M=D
                (END)
                """

    def negative(self, commande):
        return f"""// negative: {commande}
        @SP
        A=M
        A=A-1
        D=M
        M=M-D
        M=M-D
        """

    def AND(self, commande):
        return f"""// and: {commande}
        @SP
        A=M
        A=A-1
        D=M     //D=val2
        M=0
        @SP
        M=M-1
        @FALSE
        D=D+1
        D;JNE       //Si val2=false goto FALSE
        @SP
        A=M
        A=A-1
        D=M     //D=val1
        @FALSE
        D=D+1
        D;JNE       //Si val=false goto FALSE
        //Début condition true
        @0
        D=A-1
        @SP
        A=M
        A=A-1
        M=D
        @END
        0;JMP
        //Fin condition true
        //Début condition false
        (FALSE)
        D=0
        @SP
        A=M
        A=A-1
        M=D
        (END)
        """



commande = {'type': 'add'}
arith_log = ArithmeticLog()
print(arith_log.execute(commande))

#label | goto | if -goto |
from VMTranslator.ArithmeticLog import commande


class Branching:
    def __init__(self):
        pass

    def label(self, commande):
        return f"""// label : {commande}
        ({commande['label']}) // Def le label {commande} pour le saut
        
        """

    def goto(self, commande):
        return f""" // goto : {commande}
        @{commande["label"]}
        0;JMP    
        """

    def if_goto(self, commande):
        return f""" // if-goto : {commande}
        @SP
        D=A
        
        @{commande["label"]
        0;JMP
        """








class ArithmeticLog:

    def __init__(self):
        pass

    def execute(self, commande):
        type_cmd = commande['type']

        match type_cmd:
            case 'add':
                return self._add()
            case 'sub':
                return self._sub()
            case 'equal':
                return self._eq()
            case 'greater':
                return self._gt()
            case 'lower':
                return self._lt()
            case 'negative':
                return self._neg()
            case 'and':
                return self._and()
            case 'or':
                return self._or()
            case 'not':
                return self._not()


    def _add(self):
        return """
    @SP
    AM=M-1
    D=M
    A=A-1
    M=D+M
    """

    def _sub(self):
        return """
    @SP
    AM=M-1
    D=M
    A=A-1
    M=M-D
    """

    def _neg(self):
        return """
    @SP
    A=M-1
    M=-M
    """

    def _eq(self):
        label_true = self._get_unique_label()
        label_end = self._get_unique_label()
        return f"""
    @SP
    AM=M-1
    D=M
    A=A-1
    D=M-D
    @{label_true}
    D;JEQ
    @SP
    A=M-1
    M=0
    @{label_end}
    0;JMP
    ({label_true})
    @SP
    A=M-1
    M=-1
    ({label_end})
    """

    def _gt(self):
        label_true = self._get_unique_label()
        label_end = self._get_unique_label()
        return f"""
    @SP
    AM=M-1
    D=M
    A=A-1
    D=M-D
    @{label_true}
    D;JGT
    @SP
    A=M-1
    M=0
    @{label_end}
    0;JMP
    ({label_true})
    @SP
    A=M-1
    M=-1
    ({label_end})
    """

    def _lt(self):
        label_true = self._get_unique_label()
        label_end = self._get_unique_label()
        return f"""
    @SP
    AM=M-1
    D=M
    A=A-1
    D=M-D
    @{label_true}
    D;JLT
    @SP
    A=M-1
    M=0
    @{label_end}
    0;JMP
    ({label_true})
    @SP
    A=M-1
    M=-1
    ({label_end})
    """

    def _and(self):
        return """
    @SP
    AM=M-1
    D=M
    A=A-1
    M=D&M
    """

    def _or(self):
        return """
    @SP
    AM=M-1
    D=M
    A=A-1
    M=D|M
    """

    def _not(self):
        return """
    @SP
    A=M-1
    M=!M
    """



commande = {'type': 'add'}
arith_log = ArithmeticLog()
print(arith_log.execute(commande))

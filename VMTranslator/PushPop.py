class PushPop:
    
    def __init__(self, command):
        self.fileName= ""

    def setFileName(self, fileName):
        self.fileName = fileName

    def _commandpushconstant(self, command):
        """No comment"""
        parameter = command['parameter']
        return f"""\t//{command['type']} {command['segment']} {parameter}
        @{parameter}
        D=A
        @SP
        AM=M+1
        A=M
        M=D
        """

    def _commandpushpointer(self, command):
        """No comment"""
        parameter = command['parameter']
        return f"""\t//{command['type']} {command['segment']} {parameter}
        @{parameter}
        D=M
        @SP
        AM=M+1
        A=M
        M=D
        """

    def _commandpushsegment(self,command):
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

    def _commandpushtemp(self,command):
        """No comment"""
        parameter = command['parameter']
        return f"""\t//{command['type']} {segment} {parameter}
        @5
        D=A
        @{parameter}
        A=A+D
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        """

    def _commandpushstatic (self, command):
        """No comment"""
        parameter = command['parameter']
        file=f"{fileName}.{parameter}"
        return f"""\t//{command['type']} {segment} {parameter}
        @file
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        """

    def _commandpopsegment(self,command):
        """No comment"""
        segment = command['segment']
        parameter = command['parameter']
        if segment == 'local':
            base = 'LCL'
        elif segment == 'argument':
            base = 'ARG'
        elif segment == 'this':
            base = 'THIS'
        elif segment == 'that':
            base = 'THAT'

        return f"""\t//{command['type']} {segment} {parameter}
        @{base}
        D=M
        @{parameter}
        D=D+A
        @R13
        M=D
        @SP
        AM=M-1
        D=M
        @R13
        A=M
        M=D
        """

    def _commandpoppointer(self,command):
        """No comment"""
        parameter = command['parameter']
        return f"""\t//{command['type']} {parameter}
        @SP
        AM=M-1
        D=M
        @{parameter}
        M=D
        """

    def _commandpopstatic(self,command):
        """No comment"""
        parameter = command['parameter']
        file=f"{fileName}.{parameter}"
        return f"""\t//{command['type']} {parameter}
        @file
        AM=M-1
        D=M
        @{parameter}
        M=D
        """


    def _commandpoptemp(self,command):
        """No comment"""
        parameter = command['parameter']
        return f"""\t//{command['type']} {parameter}
        @5
        D=A
        @{parameter}
        D=D+A
        @R13
        M=D
        @SP
        AM=M-1
        D=M
        @R13
        A=M
        M=D
        """
        
        




        
        
        
        






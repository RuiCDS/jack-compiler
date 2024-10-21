class Fonction:
    call_counter = 0

    @classmethod
    def _get_unique_return_label(cls):
        """Generates a unique label for function return address"""
        cls.call_counter += 1
        return f"RETURN_{cls.call_counter}"

    def function_(self, function_name, nvars):
        """Generates assembly code for the 'function' command"""
        init_vars = ''.join([f"    @SP\n    A=M\n    M=0\n    @SP\n    M=M+1\n" for _ in range(int(nvars))])
        return f"""
    ({function_name})
{init_vars}
    """

    def call_(self, function_name, nargs):
        """Generates assembly code for the 'call' command"""
        return_label = self._get_unique_return_label()
        return f"""
    @{return_label}
    D=A
    @SP
    A=M
    M=D
    @SP
    M=M+1
    @LCL
    D=M
    @SP
    A=M
    M=D
    @SP
    M=M+1
    @ARG
    D=M
    @SP
    A=M
    M=D
    @SP
    M=M+1
    @THIS
    D=M
    @SP
    A=M
    M=D
    @SP
    M=M+1
    @THAT
    D=M
    @SP
    A=M
    M=D
    @SP
    M=M+1
    @SP
    D=M
    @{5 + int(nargs)}
    D=D-A
    @ARG
    M=D
    @SP
    D=M
    @LCL
    M=D
    @{function_name}
    0;JMP
    ({return_label})
    """

    def return_(self):
        """Generates assembly code for the 'return' command"""
        return f"""
    @LCL
    D=M
    @R13
    M=D
    @5
    A=D-A
    D=M
    @R14
    M=D
    @SP
    AM=M-1
    D=M
    @ARG
    A=M
    M=D
    @ARG
    D=M+1
    @SP
    M=D
    @R13
    AM=M-1
    D=M
    @THAT
    M=D
    @R13
    AM=M-1
    D=M
    @THIS
    M=D
    @R13
    AM=M-1
    D=M
    @ARG
    M=D
    @R13
    AM=M-1
    D=M
    @LCL
    M=D
    @R14
    A=M
    0;JMP
    """


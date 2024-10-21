import sys
import Parser
import ArithmeticLog
from VMTranslator.PushPop import PushPop


class Generator:
    """No comment"""

    def __init__(self, file=None):
        """No comment"""
        if file is not None:
            self.parser = Parser.Parser(file)


        self.arithmetic_log = ArithmeticLog.ArithmeticLog()

    def __iter__(self):
        return self

    def __next__(self):
        if self.parser is not None and self.parser.hasNext():
            return self._next()
        else:
            raise StopIteration

    def _next(self):
        # No comment
        command = self.parser.next()
        if command is None:
            return None
        else:
            type = command['type']
            # type = push|pop|
            #        add|sub|neg|eq|gt|lt|and|or|not) |
            #        label|goto|if-goto|
            #        Function|Call|return

            match type:
                # Faire une fonction par type de commande
                case 'push':
                    return self.PushPop.commandpushpop(command)
                case 'Call':
                    return self.commandcall(command)
                case 'add':
                    # Appel à l'instance ArithmeticLog avec la commande
                    return self.arithmetic_log.add(command)
                case 'sub':
                    return self.arithmetic_log.sub(command)
                case 'equal':
                    return self.arithmetic_log.equal(command)
                case _:
                    print(f'SyntaxError : {command}')
                    exit()

    def _commandpush(self, command):
        """No comment"""
        segment = command['segment']
        # segment=local|argument|static|constant|this|that|pointer|temp
        match segment:
            # Faire une fonction par type de segment
            case 'constant':
                return PushPop._commandpushconstant(command)
            case 'pointer':
                return PushPop._commandpushpointer(command)
            case 'segment':
                return PushPop._commandpushsegment(command)
            case 'temp':
                return PushPop._commandpushtemp(command)
            case 'static':
                return PushPop._commandpushstatic(command)
            case "":
                print(f'SyntaxError : {command}')
                exit()
    def _commandpop(self, command):
        segment = command['segment']
        match segment:
            case 'constant':
                return PushPop._commandpopconstant(command)
            case 'pointer':
                return PushPop._commandpoppointer(command)
            case 'segment':
                return PushPop._commandpopsegment(command)
            case 'temp':
                return PushPop._commandpoptemp(command)
            case 'static':
                return PushPop._commandpopstatic(command)
            case "":
                print(f'SyntaxError : {command}')
                exit()

    def _commandcall(self, command):
        """No comment"""
        return f"""\t//{command['type']} {command['function']} {command['parameter']}
    Code assembleur de {command}\n"""


if __name__ == '__main__':
    file = sys.argv[1]
    print('-----debut')
    generator = Generator(file)
    for command in generator:
        print(command)
    print('-----fin')

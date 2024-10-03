import os
import glob
import sys

import Generator


class Translator:
    """Une classe pour traduire des fichiers VM en assembleur."""

    def __init__(self, files, asm):
        """Initialise le traducteur avec les fichiers à traduire et un fichier de sortie pour l'assembleur.

        Args:
            files (str): Le chemin du fichier ou du dossier contenant les fichiers VM à traduire.
            asm (str): Le nom du fichier de sortie où l'assembleur traduit sera écrit.
        """
        self.asm = open(asm, "w")
        self.files = files

    def translate(self):
        """Traduit un ou plusieurs fichiers VM en assembleur et les écrit dans le fichier de sortie."""
        # Écrire le code d'initialisation (bootstrap) dans le fichier assembleur.
        self.asm.write(self._bootstrap())
        # Vérifie si le chemin correspond à un fichier, sinon parcourt tous les fichiers .vm dans un répertoire.
        if os.path.isfile(self.files):
            self._translateonefile(self.files)
        else:
            if os.path.isdir(self.files):
                for file in glob.glob(f'{self.files}/*.vm'):
                    self._translateonefile(file)

    def _translateonefile(self, file):
        """Traduit un fichier VM unique et écrit le code généré dans le fichier assembleur.

        Args:
            file (str): Le chemin du fichier VM à traduire.
        """
        # Ajoute un commentaire dans le fichier assembleur pour indiquer le fichier en cours de traduction.
        self.asm.write(f"""\n//code de {file}\n""")
        # Crée un générateur pour parcourir les commandes du fichier VM et les écrire dans l'assembleur.
        generator = Generator.Generator(file)
        for command in generator:
            self.asm.write(command)

    def _bootstrap(self):
        """Génère le code d'initialisation (bootstrap) en assembleur.

        Retourne:
            str: Le code d'initialisation en assembleur, qui initialise le pointeur de pile et appelle 'Sys.init'.
        """
        init = Generator.Generator()._commandcall({'type': 'Call', 'function': 'Sys.init', 'parameter': '0'})

        # Le code assembleur initialise le pointeur de pile à l'adresse 256 et appelle la fonction 'Sys.init'.
        return f"""// Bootstrap
    @256
    D=A
    @SP
    M=D
{init}
"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: Translotor.py <vm file| dir> <asm file>")
    else:
        vmfiles=sys.argv[1]
        asmfile=sys.argv[2]
        translator = Translator(vmfiles,asmfile)
        translator.translate()

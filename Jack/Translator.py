import os
import glob
import sys
import Generator


class Translator:
    """
    Cette classe permet de traduire des fichiers Jack en utilisant la classe Generator.
    Elle peut gérer un fichier unique ou tous les fichiers dans un répertoire donné.
    """

    def __init__(self, files):
        """
        Initialise le traducteur avec un fichier ou un répertoire.

        :param files: Chemin vers un fichier Jack ou un répertoire contenant des fichiers Jack.
        """
        self.files = files

    def translate(self):
        """
        Lance la traduction. Si le chemin correspond à un fichier, il est traduit directement.
        Si le chemin correspond à un répertoire, tous les fichiers .jack qu'il contient sont traduits.
        """
        if os.path.isfile(self.files):
            # Traduction d'un fichier unique
            self._translate_one_file(self.files)
        elif os.path.isdir(self.files):
            # Traduction de tous les fichiers .jack dans le répertoire
            for file in glob.glob(f'{self.files}/*.jack'):
                self._translate_one_file(file)
        else:
            # Gestion des cas où le chemin n'est ni un fichier ni un répertoire
            print(f"Erreur : {self.files} n'est ni un fichier ni un répertoire valide.")

    def _translate_one_file(self, file):
        """
        Traduit un fichier Jack donné.

        :param file: Chemin vers le fichier Jack à traduire.
        """
        try:
            # Création d'une instance de Generator pour traiter le fichier
            generator = Generator.Generator(file)
            generator.jackclass(generator.arbre)  # Appelle la méthode principale de traitement
            print(f"Traduction réussie : {file}")
        except Exception as e:
            print(f"Erreur lors de la traduction du fichier {file} : {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Affichage d'une aide en cas de mauvais usage
        print("Usage: Translator.py <fichier.jack | répertoire>")
    else:
        # Récupération du chemin passé en argument
        jackfiles = sys.argv[1]
        # Création et exécution de l'instance du traducteur
        translator = Translator(jackfiles)
        translator.translate()

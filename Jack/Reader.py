import os
import sys

class Reader:
    """Classe pour la lecture des caractères dans un fichier"""

    def __init__(self, file):
        """Initialise la lecture du fichier."""
        self.char = None  # Caractère courant
        self._line = 1    # Ligne courante
        self._col = 1     # Colonne courante
        self._file_path = file  # Sauvegarde du chemin du fichier
        if os.path.exists(file):  # Vérifie si le fichier existe
            self.file = open(file, "r")
            self.char = self.file.read(1)  # Lit le premier caractère
        else:
            raise FileNotFoundError(f"Le fichier {file} n'existe pas.")

    def look(self):
        """Retourne un dictionnaire avec le caractère actuel, la ligne et la colonne."""
        if self.char:
            return {'line': self._line, 'col': self._col, 'char': self.char}
        return None  # Si le caractère est None, fin du fichier

    def next(self):
        """Lit le prochain caractère et met à jour la ligne et la colonne."""
        if self.char:
            # Sauvegarde du caractère actuel
            res = {'line': self._line, 'col': self._col, 'char': self.char}
            if self.hasNext():  # Si on n'a pas atteint la fin du fichier
                if self.char == '\n':  # Si c'est un saut de ligne, on incrémente la ligne et réinitialise la colonne
                    self._line += 1
                    self._col = 1
                else:
                    self._col += 1  # Sinon, on incrémente juste la colonne

                # Lit le caractère suivant
                self.char = self.file.read(1)

            return res
        else:
            return None  # Si plus de caractères à lire

    def hasNext(self):
        """Retourne True si le fichier n'est pas encore terminé."""
        return self.char is not None

    def close(self):
        """Ferme le fichier proprement."""
        if self.file:
            self.file.close()

    def __iter__(self):
        """Rend l'objet itérable pour être utilisé avec un for."""
        return self  # Retourne l'itérateur

    def __next__(self):
        """Retourne le prochain caractère, lève StopIteration à la fin du fichier."""
        if self.hasNext():
            return self.next()
        else:
            self.close()  # Ferme le fichier une fois que nous avons fini de lire
            raise StopIteration

if __name__ == "__main__":
    # Lecture du fichier spécifié en ligne de commande
    file = sys.argv[1]
    print('-----début')
    lecteur = Reader(file)
    for c in lecteur:  # Parcours des caractères
        print(c)
    print('-----fin')

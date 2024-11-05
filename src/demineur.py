"""Module providing Random variable generators."""
import random
import json
import os
from statistiques import Statistiques

class Demineur:
    """Class representing a Deminer game"""


    def __init__(self, fichier_sauvegarde='demineur.json', difficulte='moyen'):
        """
        Initialize the game with a grid and place mines based on difficulty level.

        :param difficulte: Difficulty level of the game ('facile', 'moyen', 'difficile').
        :raises ValueError: If the difficulty level is not one of 'facile', 'moyen', or 'difficile'.
        """
        if difficulte not in ['facile', 'moyen', 'difficile']:
            raise ValueError("Le niveau de difficulté doit être 'facile', 'moyen' ou 'difficile'.")
        if difficulte == 'facile':
            self.taille = 8
            self.nombre_mines = 10
        elif difficulte == 'difficile':
            self.taille = 16
            self.nombre_mines = 40
        else:  # moyen
            self.taille = 10
            self.nombre_mines = 20
        self.grille = [['.' for _ in range(self.taille)] for _ in range(self.taille)]
        self.grille_visible = [['.' for _ in range(self.taille)] for _ in range(self.taille)]
        self.statistiques = Statistiques()
        self.fichier_sauvegarde = fichier_sauvegarde
        self.marques = set()
        self.__placer_mines()
        self.__calculer_indices()

    def __placer_mines(self):
        mines_placees = 0
        while mines_placees < self.nombre_mines:
            x = random.randint(0, self.taille - 1)
            y = random.randint(0, self.taille - 1)
            if self.grille[y][x] != 'M':
                self.grille[y][x] = 'M'
                mines_placees += 1

    def __calculer_indices(self):
        for y in range(self.taille):
            for x in range(self.taille):
                if self.grille[y][x] == 'M':
                    continue
                mines_autour = 0
                for dx in range(y - 1, y + 2):
                    for dy in range(x - 1, x + 2):
                        nx, ny = x + dx, y + dy
                        if nx < 0 or ny < 0 or nx >= self.taille or ny >= self.taille:
                            continue
                        if self.grille[ny][nx] == 'M':
                            mines_autour += 1
                self.grille[y][x] = str(mines_autour)

    def decouvrir_cases(self, x, y):
        """A Function to uncover a cell"""
        # Vérifier si les coordonnées sont dans les limites de la grille
        if not (0 <= x < self.taille and 0 <= y < self.taille):
            return
        if self.grille_visible[y][x] == 'F':
            self.grille_visible[y][x] = self.grille[y][x]
        if self.grille_visible[y][x] != '.':
            return
        self.grille_visible[y][x] = self.grille[y][x]
        if self.grille[y][x] == '0':
            self.decouvrir_cases(x - 1, y)
            self.decouvrir_cases(x + 1, y)
            self.decouvrir_cases(x, y - 1)
            self.decouvrir_cases(x, y + 1)

    def afficher_grille(self):
        """A Function to show the game's board"""
        for ligne in self.grille_visible:
            print(' '.join(ligne))

    def charger_jeu(self):
        """
        Load the game state from a JSON file.
        """
        if os.path.exists(self.fichier_sauvegarde):
            with open(self.fichier_sauvegarde, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.taille = data.get('taille', 10)
                self.nombre_mines = data.get('nombre_mines', 10)
                self.grille = data.get(
                    'grille', [['.' for _ in range(self.taille)] for _ in range(self.taille)]
                )
                self.grille_visible = data.get(
                    'grille_visible', 
                    [['.' for _ in range(self.taille)] for _ in range(self.taille)]
                )
    def marquer_case(self, x, y):
        """ Mark or unmark a cell with a flag. """
        if not (0 <= x < self.taille and 0 <= y < self.taille):
            return
        if self.grille_visible[y][x] == 'F':
            self.grille_visible[y][x] = '.'
        elif self.grille_visible[y][x] == '.':
            self.grille_visible[y][x] = 'F'
        else:
            print("La case est déjà découverte et ne peut pas être marquée.")

    def jouer(self):
        """A Function to launch the game."""   
        game_in_progress = True
        self.statistiques.start_timer()
        while game_in_progress:
            self.afficher_grille()
            try:
                entree = input("'f x y' pour marquer/démarquer ou 'x y' pour découvrir : ").split()
                if len(entree) == 3 and entree[0] == 'f':
                    # Mark/unmark the cells
                    x, y = map(int, entree[1:])
                    self.marquer_case(x, y)
                    continue
                if len(entree) == 2:
                    # Discover the cells
                    x, y = map(int, entree)
                else:
                    print("Error, entrer les coordonnées sous la forme 'x y' ou 'f x y'.")
                    continue
            except ValueError:
                print("Coordonnées invalides. Veuillez réessayer.")
                continue
            if self.grille[y][x] == 'M':
                #Display the grid with the mine visible
                self.decouvrir_cases(x,y)
                self.afficher_grille()
                print("Perdu !")
                #End the game
                game_in_progress = False
                temps_ecoule = self.statistiques.stop_timer()
                self.statistiques.record_loss()
                break
            self.decouvrir_cases(x, y)
            if sum(row.count('.') for row in self.grille_visible) == self.nombre_mines:
                print("Gagne !")
                #End the game
                game_in_progress = False
                temps_ecoule = self.statistiques.stop_timer()
                self.statistiques.record_victory()
                break
        print(f"Temps écoulé: {temps_ecoule:.2f} secondes")
        self.statistiques.display_statistics()


        # Demande si le joueur souhaite recommencer une partie
        while True:
            restart = input("Voulez-vous recommencer une partie ? (oui/non) : ").lower()
            if restart == 'oui':
                nouveau_jeu = Demineur(self.nombre_mines)
                nouveau_jeu.jouer()
                break
            if restart == 'non':
                print("Partie terminée !")
                break
            print("Réponse invalide, veuillez répondre par 'oui' ou 'non'.")

if __name__ == "__main__":
    niveau_difficulte = input("Choisissez un niveau de difficulte (facile, moyen, difficile): ")
    try:
        jeu = Demineur(niveau_difficulte)
        jeu.charger_jeu()
        jeu.jouer()
    except ValueError as e:
        print(e)

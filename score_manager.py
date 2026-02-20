import os


class ScoreManager:
    def __init__(self, filename="highscores.txt"):
        self.filename = filename
        self.player_name = os.getlogin()  # Récupère le nom de session du PC
        self.scores = self.load_scores()

    def load_scores(self):
        """Charge tous les scores depuis le fichier."""
        scores = {}
        if not os.path.exists(self.filename):
            return scores
        try:
            with open(self.filename, "r") as f:
                for line in f:
                    if ":" in line:
                        name, score = line.strip().split(":")
                        scores[name] = int(score)
        except Exception as e:
            print(f"Erreur chargement scores: {e}")
        return scores

    def save_score(self, current_score):
        """Enregistre le score si c'est le meilleur du joueur actuel."""
        # On ne garde que le meilleur score par joueur
        old_score = self.scores.get(self.player_name, 0)

        if current_score > old_score:
            self.scores[self.player_name] = current_score
            try:
                with open(self.filename, "w") as f:
                    for name, score in self.scores.items():
                        f.write(f"{name}:{score}\n")
                return True  # Nouveau record personnel
            except Exception as e:
                print(f"Erreur sauvegarde scores: {e}")
        return False

    def get_leaderboard(self):
        """Retourne la liste des scores triée du plus grand au plus petit."""
        # Trie le dictionnaire par valeur (le score)
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores
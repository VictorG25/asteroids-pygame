import os

class ScoreManager:
    def __init__(self, filename="highscore.txt"):
        self.filename = filename
        self.highscore = self.load_highscore()

    def load_highscore(self):
        if not os.path.exists(self.filename):
            return 0
        try:
            with open(self.filename, "r") as f:
                return int(f.read())
        except:
            return 0

    def save_highscore(self, score):
        if score > self.highscore:
            self.highscore = score
            with open(self.filename, "w") as f:
                f.write(str(score))
            return True # Nouveau record !
        return False
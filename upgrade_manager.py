import random


class UpgradeManager:
    def __init__(self):
        # Liste des améliorations : (Nom, Description, Rareté)
        # Rareté : 1 = Commun (Blanc), 2 = Rare (Cyan), 3 = Légendaire (Orange)
        self.upgrades = [
            ("Vie +1", "Recupere un coeur", 1),
            ("Cadence de Tir", "+15% vitesse de tir", 1),
            ("Maniabilite", "+20% vitesse de rotation", 1),
            ("Bouclier", "Invincibilite +3s", 2),
            ("Canon Lateral", "+1 projectile de cote", 3),
        ]

    def get_random_choices(self, count=3):
        # On s'assure de ne pas prendre plus d'options qu'il n'en existe
        actual_count = min(count, len(self.upgrades))
        return random.sample(self.upgrades, actual_count)

    def apply(self, player, upgrade_name, game_state):
        # Cette méthode DOIT s'appeler 'apply' pour matcher ton main.py
        if upgrade_name == "Vie +1":
            game_state["lives"] += 1

        elif upgrade_name == "Cadence de Tir":
            # On réduit le multiplicateur (ex: 0.85 * 0.85...)
            player.shoot_cooldown_multiplier *= 0.85

        elif upgrade_name == "Maniabilite":
            # On augmente la vitesse de rotation globale (importée de constants)
            import constants
            player.rotation_speed_bonus = getattr(player, 'rotation_speed_bonus', 1.0) + 0.2

        elif upgrade_name == "Bouclier":
            # On peut imaginer un moyen de déclencher l'invincibilité ici
            # Pour l'instant on va dire qu'on passe par le game_state si besoin
            pass

        elif upgrade_name == "Canon Lateral":
            player.extra_projectiles += 1

        print(f"Amelioration appliquee : {upgrade_name}")
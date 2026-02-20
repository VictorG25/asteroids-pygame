import pygame
import random
import math
from circleshape import CircleShape
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class PowerUp(CircleShape):
    # Dictionnaire pour stocker les images chargées une seule fois
    images = {}

    def __init__(self, x, y, kind=None):
        super().__init__(x, y, 25)

        # Si aucun type n'est précisé (spawn aléatoire via AsteroidField), on choisit au hasard
        if kind is None:
            self.kind = random.choice(["shield", "triple_shot", "torpedo"])
        else:
            self.kind = kind

        self.velocity = pygame.Vector2(random.uniform(-50, 50), random.uniform(-50, 50))
        self.lifetime = 12.0  # Un peu plus de temps pour les ramasser
        self.animation_timer = 0

        # Initialisation des images si le dictionnaire est vide
        if not PowerUp.images:
            self._load_assets()

    def _load_assets(self):
        """Charge et redimensionne toutes les images nécessaires."""
        paths = {
            "shield": "assets/images/shield.png",
            "triple_shot": "assets/images/faivrePowerUp.png",
            "torpedo": "assets/images/torpedo.png"  # On utilise l'image de la torpille
        }

        for key, path in paths.items():
            try:
                raw_img = pygame.image.load(path).convert_alpha()
                # On redimensionne 50x50 par défaut
                PowerUp.images[key] = pygame.transform.scale(raw_img, (50, 50))
            except Exception as e:
                print(f"Erreur chargement PowerUp {key} ({path}): {e}")
                # Fallback : un carré de couleur si l'image manque
                surf = pygame.Surface((40, 40))
                colors = {"shield": "blue", "triple_shot": "green", "torpedo": "orange"}
                surf.fill(colors.get(key, "white"))
                PowerUp.images[key] = surf

    def draw(self, screen):
        if self.kind in PowerUp.images:
            image = PowerUp.images[self.kind]

            # Petit effet de pulsation (zoom) pour rendre le loot vivant
            pulse = 1.0 + 0.1 * math.sin(self.animation_timer * 5)
            if pulse != 1.0:
                new_size = (int(image.get_width() * pulse), int(image.get_height() * pulse))
                display_img = pygame.transform.scale(image, new_size)
            else:
                display_img = image

            rect = display_img.get_rect(center=(self.position.x, self.position.y))
            screen.blit(display_img, rect)
        else:
            pygame.draw.circle(screen, "white", self.position, self.radius, 1)

    def update(self, dt):
        self.animation_timer += dt
        self.position += self.velocity * dt
        self.lifetime -= dt

        # Clignotement quand il va disparaître (moins de 3 secondes)
        if self.lifetime < 3.0:
            if int(self.lifetime * 10) % 2 == 0:
                pass  # On pourrait sauter le draw ici, mais la logique est dans draw()

        if self.lifetime <= 0:
            self.kill()

        self.wrap_position()

    def wrap_position(self):
        if self.position.x > SCREEN_WIDTH + 20:
            self.position.x = -20
        elif self.position.x < -20:
            self.position.x = SCREEN_WIDTH + 20
        if self.position.y > SCREEN_HEIGHT + 20:
            self.position.y = -20
        elif self.position.y < -20:
            self.position.y = SCREEN_HEIGHT + 20
import pygame
import random
from circleshape import CircleShape
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class PowerUp(CircleShape):
    # Dictionnaire pour stocker les images chargées
    images = {}

    def __init__(self, x, y, kind):
        super().__init__(x, y, 25)  # Hitbox de rayon 15
        self.kind = kind  # "shield", "triple_shot", etc.
        self.velocity = pygame.Vector2(random.uniform(-50, 50), random.uniform(-50, 50))
        self.lifetime = 10.0

        # Initialisation des images si le dictionnaire est vide
        if not PowerUp.images:
            self._load_assets()

    def _load_assets(self):
        """Charge et redimensionne toutes les images nécessaires."""
        paths = {
            "shield": "assets/shield.png",
            "triple_shot": "assets/images/faivrePowerUp.png"  # Ton image personnalisée
        }

        for key, path in paths.items():
            try:
                raw_img = pygame.image.load(path).convert_alpha()
                # On redimensionne 50x50
                PowerUp.images[key] = pygame.transform.scale(raw_img, (50, 50))
            except pygame.error as e:
                print(f"Impossible de charger {path}: {e}")
                # Création d'une surface vide en cas d'erreur pour éviter le crash
                PowerUp.images[key] = pygame.Surface((30, 30))

    def draw(self, screen):
        if self.kind in PowerUp.images:
            # get_rect(center=...) est la méthode la plus propre pour centrer une image
            image = PowerUp.images[self.kind]
            rect = image.get_rect(center=(self.position.x, self.position.y))
            screen.blit(image, rect)
        else:
            # Fallback visuel au cas où
            pygame.draw.circle(screen, "white", self.position, self.radius, 1)

    def update(self, dt):
        self.position += self.velocity * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

        # Optionnel : petit effet visuel de flottement (sinusoïdal)
        # self.position.y += math.sin(pygame.time.get_ticks() * 0.005) * 0.5

        self.wrap_position()

    def wrap_position(self):
        if self.position.x > SCREEN_WIDTH:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = SCREEN_WIDTH
        if self.position.y > SCREEN_HEIGHT:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = SCREEN_HEIGHT
import pygame
from circleshape import CircleShape
from constants import SHOT_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT


class Shot(CircleShape):
    def __init__(self, x, y, owner="player"):
        super().__init__(x, y, SHOT_RADIUS)
        self.owner = owner

    def draw(self, screen):
        color = "cyan" if self.owner == "player" else "red"
        pygame.draw.circle(screen, color, self.position, self.radius)
        pygame.draw.circle(screen, "white", self.position, self.radius, 1)

    def update(self, dt):
        # On déplace le tir
        self.position += (self.velocity * dt)

        # --- DÉTECTION SORTIE D'ÉCRAN ---
        # On vérifie si le tir dépasse les limites de l'écran
        if (self.position.x < -self.radius or
                self.position.x > SCREEN_WIDTH + self.radius or
                self.position.y < -self.radius or
                self.position.y > SCREEN_HEIGHT + self.radius):
            self.kill()  # Supprime l'objet de tous les groupes (updatable, drawable, shots)
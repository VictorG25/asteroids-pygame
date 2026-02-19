import pygame
import random
from circleshape import CircleShape

class Particle(CircleShape):
    def __init__(self, x, y):
        # Les particules sont minuscules (rayon de 1 ou 2)
        super().__init__(x, y, random.uniform(1, 2.5))
        
        # Direction aléatoire et vitesse variée
        direction = pygame.Vector2(0, 1).rotate(random.uniform(0, 360))
        speed = random.uniform(50, 150)
        self.velocity = direction * speed
        
        # Durée de vie en secondes
        self.lifetime = random.uniform(0.3, 0.8)

    def update(self, dt):
        self.position += self.velocity * dt
        self.lifetime -= dt
        # La particule rétrécit avec le temps
        self.radius *= 0.95
        if self.lifetime <= 0 or self.radius <0.5:
            self.kill()

    def draw(self, screen):
        # On dessine un petit cercle blanc
        pygame.draw.circle(screen, "white", self.position, self.radius)
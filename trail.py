import pygame
import random


class Trail(pygame.sprite.Sprite):
    # On n'a plus besoin de particle_image externe, on va dessiner des cercles
    def __init__(self, position):
        super().__init__(self.containers)

        self.position = pygame.Vector2(position)
        # Petit décalage aléatoire pour l'éparpillement des bulles
        self.position.x += random.uniform(-8, 8)
        self.position.y += random.uniform(-8, 8)

        # Propriétés de la bulle
        self.radius = random.randint(2, 6)
        self.lifetime = random.uniform(0.6, 1.2)  # Durée de vie variable
        self.max_lifetime = self.lifetime

        # Vitesse : les bulles remontent (Y négatif) et dérivent légèrement sur les côtés
        self.velocity = pygame.Vector2(random.uniform(-15, 15), random.uniform(-60, -30))

        # Création de l'image de la bulle (cercle blanc/bleu transparent)
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.color = (200, 235, 255, 160)  # Bleu très clair et semi-transparent
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)

        self.rect = self.image.get_rect(center=self.position)

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return

        # 1. Mouvement : les bulles montent
        self.position += self.velocity * dt
        self.rect.center = self.position

        # 2. Effet visuel : calcul du ratio de vie
        life_ratio = self.lifetime / self.max_lifetime

        # 3. Réduction de la taille et de l'opacité
        current_radius = max(1, int(self.radius * life_ratio))
        alpha = int(160 * life_ratio)

        # On recrée une petite surface pour le changement de taille
        self.image = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 235, 255, alpha), (current_radius, current_radius), current_radius)
        self.rect = self.image.get_rect(center=self.position)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
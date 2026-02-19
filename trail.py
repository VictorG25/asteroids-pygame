import pygame
import random


class Trail(pygame.sprite.Sprite):
    # On charge l'image de la traînée une seule fois
    particle_image = None

    def __init__(self, position):
        super().__init__(self.containers)

        # Chargement de l'image si ce n'est pas fait
        if Trail.particle_image is None:
            Trail.particle_image = pygame.image.load("assets/images/exhaust_particle.png").convert_alpha()

        # On ne veut pas que la traînée soit exactement sur le centre du vaisseau,
        # mais un peu derrière. On peut ajouter un petit décalage aléatoire
        self.position = pygame.Vector2(position)
        self.position.x += random.uniform(-5, 5)
        self.position.y += random.uniform(-5, 5)

        # On varie un peu la taille de départ pour chaque particule
        scale = random.uniform(0.5, 1.2)
        size = int(20 * scale)  # Taille de base de la particule
        self.original_image = pygame.transform.scale(Trail.particle_image, (size, size))

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=self.position)

        # Durée de vie
        self.lifetime = 0.5
        self.max_lifetime = 0.5
        self.alpha = 200

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return

        life_ratio = self.lifetime / self.max_lifetime

        # Effet : La particule s'estompe et rétrécit
        self.alpha = int(200 * life_ratio)
        new_size = int(self.rect.width * life_ratio)

        if new_size > 0:
            # Note : On réduit ici directement sans re-scale depuis l'original
            # pour économiser de la performance sur beaucoup de particules
            self.image.set_alpha(self.alpha)
            # On ne change pas forcément la taille à chaque frame si c'est trop lourd,
            # mais l'alpha suffit déjà pour un bel effet.

    def draw(self, screen):
        screen.blit(self.image, self.rect)
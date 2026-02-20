import pygame
import math
import random


class Decoration(pygame.sprite.Sprite):
    # Dictionnaires pour stocker les images chargées
    images = {}

    def __init__(self, x, y, type_deco="seaweed"):
        super().__init__()

        # Chargement unique de l'image si elle n'est pas encore en mémoire
        if type_deco not in Decoration.images:
            path = f"assets/images/{type_deco}_sheet.png"
            raw_img = pygame.image.load(path).convert_alpha()
            # On redimensionne le 16x16 en 48x48 ou 64x64
            Decoration.images[type_deco] = pygame.transform.scale(raw_img, (48, 48))

        self.base_image = Decoration.images[type_deco]
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(x, y))

        self.type_deco = type_deco
        self.pos_x = x
        self.pos_y = y
        self.offset = random.uniform(0, 10)  # Pour varier l'oscillation

    def update(self, dt):
        if self.type_deco == "grass":
            # Simulation du courant marin (oscillation)
            time = pygame.time.get_ticks() * 0.002
            angle = math.sin(time + self.offset) * 8  # Oscille de 8 degrés

            # On fait pivoter l'image
            self.image = pygame.transform.rotate(self.base_image, angle)
            # On recentre pour que l'algue reste "plantée" au sol
            self.rect = self.image.get_rect(center=(self.pos_x, self.pos_y))
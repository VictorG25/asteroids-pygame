import pygame
import random
from asteroid import Asteroid
from constants import *


class AsteroidField(pygame.sprite.Sprite):
    edges = [
        [
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT),
        ],
        [
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(
                SCREEN_WIDTH + ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT
            ),
        ],
        [
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS),
        ],
        [
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(
                x * SCREEN_WIDTH, SCREEN_HEIGHT + ASTEROID_MAX_RADIUS
            ),
        ],
    ]

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.spawn_timer = 0.0
        self.difficulty = 1.0  # Facteur de difficulté initial (100%)

    def spawn(self, radius, position, velocity):
        asteroid = Asteroid(position.x, position.y, radius)
        asteroid.velocity = velocity

    def update(self, dt):
        # Augmente la difficulté de 1% toutes les secondes
        # Après 100 secondes, le jeu est 2x plus dur
        self.difficulty += dt * 0.01

        self.spawn_timer += dt

        # On divise le délai de spawn par la difficulté
        # Plus la difficulté monte, plus l'intervalle est court
        current_spawn_rate = ASTEROID_SPAWN_RATE_SECONDS / self.difficulty

        if current_spawn_rate < 0.3:
            current_spawn_rate = 0.3

        if self.spawn_timer > current_spawn_rate:
            self.spawn_timer = 0

            # --- LOGIQUE DE SPAWN ---
            edge = random.choice(self.edges)

            # La vitesse aussi augmente avec la difficulté
            speed = random.randint(40, 100) * self.difficulty

            velocity = edge[0] * speed
            velocity = velocity.rotate(random.randint(-30, 30))
            position = edge[1](random.uniform(0, 1))
            kind = random.randint(1, ASTEROID_KINDS)
            self.spawn(ASTEROID_MIN_RADIUS * kind, position, velocity)
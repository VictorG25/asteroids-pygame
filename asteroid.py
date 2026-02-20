import pygame
import random
from circleshape import CircleShape
from constants import LINE_WIDTH, ASTEROID_MIN_RADIUS
from logger import log_event
from powerup import PowerUp


class Asteroid(CircleShape):
    # On garde les images ici pour ne les charger qu'une seule fois
    images = []

    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

        # --- Chargement des images ---
        if not Asteroid.images:
            try:
                for i in range(1, 4):
                    img = pygame.image.load(f"assets/images/asteroid{i}.png").convert_alpha()
                    Asteroid.images.append(img)
            except:
                print("Note : Images d'astéroïdes introuvables. Utilisation du cercle par défaut.")

        # --- Choix du design et création du RECT ---
        # Le RECT est indispensable pour pygame.sprite.spritecollide
        size_rect = int(radius * 2)
        if Asteroid.images:
            self.original_image = random.choice(Asteroid.images)
            size_img = int(radius * 2.2)
            self.image = pygame.transform.scale(self.original_image, (size_img, size_img))
            self.rect = self.image.get_rect(center=self.position)

            self.rotation = random.randint(0, 360)
            self.rotation_speed = random.uniform(-100, 100)
        else:
            self.image = None
            # Fallback rect si pas d'image
            self.rect = pygame.Rect(x - radius, y - radius, size_rect, size_rect)

    def draw(self, screen):
        if self.image:
            rotated_image = pygame.transform.rotate(self.image, self.rotation)
            new_rect = rotated_image.get_rect(center=self.position)
            screen.blit(rotated_image, new_rect)
        else:
            pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)

    def update(self, dt):
        # 1. Mise à jour de la position
        self.position += (self.velocity * dt)

        # 2. Mise à jour du RECT (Crucial pour les collisions !)
        self.rect.center = (self.position.x, self.position.y)

        # 3. Mise à jour de la rotation visuelle
        if self.image:
            self.rotation += self.rotation_speed * dt

        self.wrap_position()

    def split(self):
        self.kill()

        # Si l'astéroïde est trop petit, il disparaît (avec une chance de loot)
        if self.radius <= ASTEROID_MIN_RADIUS:
            if random.random() < 0.10:
                # On laisse PowerUp choisir aléatoirement le type (incluant torpedo maintenant)
                PowerUp(self.position.x, self.position.y)
            return

        log_event("asteroid_split")
        random_angle = random.uniform(20, 50)
        velocity1 = self.velocity.rotate(random_angle)
        velocity2 = self.velocity.rotate(-random_angle)
        new_radius = self.radius - ASTEROID_MIN_RADIUS

        asteroid1 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid2 = Asteroid(self.position.x, self.position.y, new_radius)

        asteroid1.velocity = velocity1 * 1.2
        asteroid2.velocity = velocity2 * 1.2
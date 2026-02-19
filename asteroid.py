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
                # Adapte la liste selon le nombre d'images que tu as faites
                # Exemple : asteroid1.png, asteroid2.png...
                for i in range(1, 4):
                    img = pygame.image.load(f"assets/images/asteroid{i}.png").convert_alpha()
                    Asteroid.images.append(img)
            except:
                # Si les images n'existent pas encore, on crée une surface vide pour éviter le crash
                print("Note : Images d'astéroïdes introuvables. Utilisation du cercle par défaut.")

        # --- Choix du design ---
        if Asteroid.images:
            self.original_image = random.choice(Asteroid.images)
            # On redimensionne l'image selon le radius (radius * 2 = diamètre)
            size = int(radius * 2.2)  # Un peu plus grand que le cercle de collision pour le look
            self.image = pygame.transform.scale(self.original_image, (size, size))

            # Pour la rotation
            self.rotation = random.randint(0, 360)
            self.rotation_speed = random.uniform(-100, 100)
        else:
            self.image = None

    def draw(self, screen):
        if self.image:
            # On gère la rotation pour le rendu visuel
            # On ne fait pas tourner self.image directement pour ne pas dégrader la qualité
            rotated_image = pygame.transform.rotate(self.image, self.rotation)
            # On centre l'image sur la position de l'astéroïde
            new_rect = rotated_image.get_rect(center=self.position)
            screen.blit(rotated_image, new_rect)
        else:
            # Fallback : dessine le cercle si pas d'image
            pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)

    def update(self, dt):
        # Mise à jour de la position
        self.position += (self.velocity * dt)
        # Mise à jour de la rotation visuelle
        if self.image:
            self.rotation += self.rotation_speed * dt

        self.wrap_position()

    def split(self):
        self.kill()

        if self.radius <= ASTEROID_MIN_RADIUS:
            if random.random() < 0.10:
                kind = random.choice(["shield", "triple_shot"])
                PowerUp(self.position.x, self.position.y, kind)
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
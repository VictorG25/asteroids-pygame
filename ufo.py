import pygame
import random
from circleshape import CircleShape
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SHOOT_SPEED
from shot import Shot


class UFO(CircleShape):
    ufo_image = None

    def __init__(self, x=None, y=None):
        # --- LOGIQUE DE POSITION CORRIGÉE ---
        if x is None or y is None:
            # Comportement UFO normal : spawn aléatoire sur les côtés
            side = random.choice(["left", "right"])
            if side == "left":
                x = -20
                self.direction = 1
            else:
                x = SCREEN_WIDTH + 20
                self.direction = -1
            y = random.randint(50, SCREEN_HEIGHT - 50)
        else:
            # Comportement Boss (ou position forcée)
            self.direction = 0  # Le boss gère sa propre direction

        # On appelle le parent avec les BONNES coordonnées (reçues ou calculées)
        super().__init__(x, y, 35)

        # Vitesse initiale (utile pour l'UFO normal, sera écrasée par le Boss)
        self.velocity = pygame.Vector2(self.direction * 150, 0)
        self.shoot_timer = 2.0

        if UFO.ufo_image is None:
            try:
                raw_image = pygame.image.load("assets/UFO.png").convert_alpha()
                UFO.ufo_image = pygame.transform.scale(raw_image, (70, 70))
            except:
                # Sécurité si le fichier est mal nommé (ex: ufo.png au lieu de UFO.png)
                UFO.ufo_image = pygame.Surface((70, 70))
                UFO.ufo_image.fill("green")

    def draw(self, screen):
        if UFO.ufo_image:
            image_rect = UFO.ufo_image.get_rect(center=(self.position.x, self.position.y))
            screen.blit(UFO.ufo_image, image_rect)

    def update(self, dt, player_position=None):
        self.position += self.velocity * dt
        self.shoot_timer -= dt

        if player_position is not None and self.shoot_timer <= 0:
            self.shoot(player_position)
            self.shoot_timer = 2.0

            # On ne tue l'objet que s'il sort par les côtés (pas par le haut pour le Boss)
        if self.position.x < -100 or self.position.x > SCREEN_WIDTH + 100:
            self.kill()

    def shoot(self, target_pos):
        # S'assurer que la cible n'est pas exactement sur l'UFO pour éviter erreur division par zéro
        if target_pos == self.position:
            return
        direction = (target_pos - self.position).normalize()
        shot = Shot(self.position.x, self.position.y)
        shot.owner = "ufo"  # Assure-toi que Shot accepte owner ou gère-le manuellement
        shot.velocity = direction * (PLAYER_SHOOT_SPEED * 0.7)
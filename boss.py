import pygame
import random
import math
from ufo import UFO, Explosion
from constants import *
from shot import Shot
from asteroid import Asteroid


class Boss(UFO):
    def __init__(self):
        # On initialise via UFO avec le type boss pour éviter les mouvements auto
        super().__init__(kind="boss")

        # Position de départ forcée (en haut, hors champ)
        self.position = pygame.Vector2(SCREEN_WIDTH / 2, -200)
        self.radius = 80
        self.max_health = 40
        self.health = self.max_health

        self.entrance_speed = 120
        self.target_y = 150
        self.shoot_timer = 2.0
        self.is_enraged = False

        try:
            # On charge l'image spécifique du boss
            self.original_image = pygame.image.load("assets/images/faivreBoss.png").convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (160, 160))
            self.image = self.original_image.copy()
            self.rect = self.image.get_rect(center=self.position)
        except:
            # Fallback si l'image est manquante
            self.image = pygame.Surface((160, 160), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 0, 0), (80, 80), 80)
            self.rect = self.image.get_rect(center=self.position)

        # On nettoie la zone pour le combat
        for asteroid in Asteroid.containers[0]:
            asteroid.kill()

    def update(self, dt, player_pos):
        # PHASE 1 : Entrée en scène
        if self.position.y < self.target_y:
            self.position.y += self.entrance_speed * dt
            self.rect.center = self.position
            return

            # PHASE 2 : Mouvement de combat latéral
        speed_factor = 0.001 if self.is_enraged else 0.0007
        self.position.x = (SCREEN_WIDTH / 2) + math.sin(pygame.time.get_ticks() * speed_factor) * (SCREEN_WIDTH * 0.3)
        self.rect.center = self.position

        # Gestion de l'état "Rage"
        if self.health <= self.max_health / 2 and not self.is_enraged:
            self.is_enraged = True
            if self.image:
                self.image.fill((255, 100, 100), special_flags=pygame.BLEND_RGB_MULT)

        # Tir
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot_triple(player_pos)
            self.shoot_timer = 0.8 if self.is_enraged else 1.8

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        Explosion(self.position.x, self.position.y, sound_type="mine")
        self.kill()

    def shoot_triple(self, player_pos):
        direction = (player_pos - self.position).normalize()
        angles = [-0.4, -0.2, 0, 0.2, 0.4] if self.is_enraged else [-0.2, 0, 0.2]

        for angle in angles:
            bullet_dir = direction.rotate_rad(angle)
            s = Shot(self.position.x, self.position.y)
            s.velocity = bullet_dir * (400 if self.is_enraged else 250)
            s.owner = "ufo"

    def draw(self, screen):
        # 1. Dessin du boss
        if self.image:
            screen.blit(self.image, self.rect)

        # 2. Dessin de la barre de vie (seulement quand il est à l'écran)
        if self.position.y >= 0:
            bar_width = 400
            bar_height = 20
            # On centre la barre en haut de l'écran
            bar_x = (SCREEN_WIDTH - bar_width) // 2
            bar_y = 30

            # Calcul du remplissage
            health_ratio = max(0, self.health / self.max_health)
            fill_width = int(bar_width * health_ratio)

            # Fond de la barre (Rouge sombre)
            pygame.draw.rect(screen, (80, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            # Remplissage (Rouge vif)
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, fill_width, bar_height))
            # Contour (Blanc)
            pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

            # Optionnel : Nom du Boss au-dessus
            # font = pygame.font.SysFont(None, 24)
            # name_txt = font.render("COMMANDANT FAIVRE", True, "white")
            # screen.blit(name_txt, (bar_x, bar_y - 20))
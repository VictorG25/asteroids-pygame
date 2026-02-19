import pygame
import random
import math
from ufo import UFO
from constants import *
from shot import Shot
from audio_manager import AudioManager

class Boss(UFO):
    audio = AudioManager()
    audio.load_sound("boss_shoot", "assets/sounds/boss_laser.mp3", 0.4)
    def __init__(self):
        # On l'appelle via super() mais on va booster ses stats
        super().__init__(SCREEN_WIDTH / 2, -100)  # Il arrive d'en haut
        self.radius = 80  # Très gros
        self.health = 20  # Il faut 20 tirs pour le tuer
        self.max_health = 20
        self.velocity = pygame.Vector2(0, 50)  # Il descend doucement
        self.shoot_timer = 1.5
        self.target_y = 150  # Il s'arrête à cette hauteur

        # Image du Boss (tu pourras la remplacer par une image dédiée)
        try:
            self.image = pygame.image.load("assets/images/faivreBoss.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (160, 160))
            # On peut le teinter en rouge pour faire peur
            self.image.fill((255, 100, 100, 255), special_flags=pygame.BLEND_RGBA_MULT)
        except:
            self.image = None

    def update(self, dt, player_pos):
        # Déplacement : descend jusqu'à target_y puis bouge de gauche à droite
        if self.position.y < self.target_y:
            self.position.y += self.velocity.y * dt
        else:
            # Mouvement de va-et-vient horizontal
            self.position.x += math.sin(pygame.time.get_ticks() * 0.002) * 2

        # Tir de barrage : 3 tirs en éventail
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot_triple(player_pos)
            self.shoot_timer = 2.0

    def shoot_triple(self, player_pos):
        Boss.audio.play_sound("boss_shoot")
        direction = (player_pos - self.position).normalize()
        # On crée 3 angles différents
        angles = [-0.2, 0, 0.2]
        for angle in angles:
            bullet_dir = direction.rotate_rad(angle)
            s = Shot(self.position.x, self.position.y)
            s.velocity = bullet_dir * 300
            s.owner = "ufo"

    def draw(self, screen):
        # Dessin de l'image
        if self.image:
            rect = self.image.get_rect(center=(self.position.x, self.position.y))
            screen.blit(self.image, rect)

        # Barre de vie au-dessus du boss
        bar_width = 200
        bar_height = 15
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pygame.Rect(self.position.x - bar_width / 2, self.position.y - 100, bar_width, bar_height)
        fill_rect = pygame.Rect(self.position.x - bar_width / 2, self.position.y - 100, fill, bar_height)
        pygame.draw.rect(screen, (255, 0, 0), fill_rect)
        pygame.draw.rect(screen, (255, 255, 255), outline_rect, 2)
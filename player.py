import pygame
import math
import random
from circleshape import CircleShape
from constants import (PLAYER_RADIUS, PLAYER_TURN_SPEED, PLAYER_SHOOT_COOLDOWN,
                       PLAYER_FRICTION, PLAYER_ACCELERATION, PLAYER_SHOOT_SPEED,
                       SCREEN_WIDTH, SCREEN_HEIGHT)
from shot import Shot
from trail import Trail


class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shoot_timer = 0
        self.velocity = pygame.Vector2(0, 0)
        self.has_triple_shot = 0
        self.trail_timer = 0

        # --- SYSTÈME DE TORPILLES ---
        self.torpedo_stock = 0
        self.torpedo_cooldown = 0

        # --- SYSTÈME DE PROGRESSION ---
        self.level = 1
        self.xp = 0
        self.xp_next_level = 500
        self.shoot_cooldown_multiplier = 1.0
        self.extra_projectiles = 0

        # --- PRÉ-CHARGEMENT DU SON DE TIR ---
        # On le charge ici une seule fois pour éviter les lags en plein jeu
        try:
            self.laser_sound = pygame.mixer.Sound("assets/sounds/laser1.wav")
            self.laser_sound.set_volume(0.3)
        except:
            self.laser_sound = None

        # --- CHARGEMENT DES IMAGES ---
        try:
            self.image_idle = pygame.image.load("assets/images/sub_idle.png").convert_alpha()
            self.image_move = pygame.image.load("assets/images/sub_move.png").convert_alpha()

            orig_width = self.image_idle.get_width()
            orig_height = self.image_idle.get_height()
            aspect_ratio = orig_width / orig_height

            new_height = int(PLAYER_RADIUS * 2.5)
            new_width = int(new_height * aspect_ratio)
            size = (new_width, new_height)

            self.image_idle = pygame.transform.scale(self.image_idle, size)
            self.image_move = pygame.transform.scale(self.image_move, size)

        except Exception as e:
            print(f"Erreur chargement images player: {e}")
            self.image_idle = pygame.Surface((PLAYER_RADIUS * 2, PLAYER_RADIUS * 2))
            self.image_idle.fill("blue")
            self.image_move = self.image_idle.copy()

        self.is_thrusting = False

    def draw(self, screen, is_invincible=False):
        current_img = self.image_move if self.is_thrusting else self.image_idle
        rotated_img = pygame.transform.rotate(current_img, -self.rotation)

        if is_invincible:
            if int(pygame.time.get_ticks() / 100) % 2 == 0:
                return

        new_rect = rotated_img.get_rect(center=self.position)
        screen.blit(rotated_img, new_rect)

    def rotate(self, dt):
        bonus = getattr(self, 'rotation_speed_bonus', 1.0)
        self.rotation += (PLAYER_TURN_SPEED * bonus) * dt

    def update(self, dt):
        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        if self.torpedo_cooldown > 0:
            self.torpedo_cooldown -= dt

        self.position += self.velocity * dt
        self.velocity *= PLAYER_FRICTION

        keys = pygame.key.get_pressed()
        self.is_thrusting = False

        # Contrôles
        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            self.rotate(-dt)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rotate(dt)
        if keys[pygame.K_z] or keys[pygame.K_UP]:
            self.move(dt)
            self.is_thrusting = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.move(-dt)

        # Tir Classique
        if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
            self.shoot()

        # Tir de Torpille
        if keys[pygame.K_v] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.fire_torpedo()

        # Trainée de bulles
        self.trail_timer -= dt
        if self.is_thrusting and self.trail_timer <= 0:
            backward_dir = pygame.Vector2(1, 0).rotate(self.rotation)
            exhaust_pos = self.position + backward_dir * (self.radius * 1.5)
            Trail(exhaust_pos)
            self.trail_timer = 0.05

        self.wrap_position()
        self.has_triple_shot -= dt

    def move(self, dt):
        # L'avant est à gauche (-1, 0)
        forward = pygame.Vector2(-1, 0).rotate(self.rotation)
        self.velocity += forward * PLAYER_ACCELERATION * dt

    def shoot(self):
        if self.shoot_timer > 0:
            return

        self.shoot_timer = PLAYER_SHOOT_COOLDOWN * self.shoot_cooldown_multiplier

        # Lecture du son pré-chargé
        if self.laser_sound:
            self.laser_sound.play()

        direction_base = pygame.Vector2(-1, 0)
        spawn_pos = self.position + direction_base.rotate(self.rotation) * self.radius

        # Tir Principal / Triple Shot
        if self.has_triple_shot > 0:
            for angle in [-15, 0, 15]:
                shot = Shot(spawn_pos.x, spawn_pos.y)
                shot.owner = "player"
                shot.velocity = direction_base.rotate(self.rotation + angle) * PLAYER_SHOOT_SPEED
        else:
            shot = Shot(spawn_pos.x, spawn_pos.y)
            shot.owner = "player"
            shot.velocity = direction_base.rotate(self.rotation) * PLAYER_SHOOT_SPEED

        # Projectiles bonus (Progression)
        for i in range(self.extra_projectiles):
            angle_spread = (i + 1) * 20
            for side in [1, -1]:
                bonus_shot = Shot(spawn_pos.x, spawn_pos.y)
                bonus_shot.owner = "player"
                bonus_shot.velocity = direction_base.rotate(self.rotation + (angle_spread * side)) * PLAYER_SHOOT_SPEED

    def fire_torpedo(self):
        if self.torpedo_stock > 0 and self.torpedo_cooldown <= 0:
            from ufo import Torpedo  # Import local pour éviter les cycles

            direction = pygame.Vector2(-1, 0).rotate(self.rotation)
            spawn_pos = self.position + direction * self.radius

            Torpedo(spawn_pos.x, spawn_pos.y, direction * 500)

            self.torpedo_stock -= 1
            self.torpedo_cooldown = 0.8
import pygame
from circleshape import CircleShape
from constants import (PLAYER_RADIUS, PLAYER_TURN_SPEED, PLAYER_SHOOT_COOLDOWN,
                       PLAYER_FRICTION, PLAYER_ACCELERATION, PLAYER_SHOOT_SPEED)
from shot import Shot
from trail import Trail


class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.timer = 0
        self.velocity = pygame.Vector2(0, 0)
        self.has_triple_shot = 0
        self.trail_timer = 0

        # --- SYSTÈME DE PROGRESSION ---
        self.level = 1
        self.xp = 0
        self.xp_next_level = 500
        self.shoot_cooldown_multiplier = 1.0
        self.extra_projectiles = 0

        # --- CHARGEMENT DES IMAGES ---
        self.image_idle = pygame.image.load("assets/images/player_idle.png").convert_alpha()
        self.image_thrust = pygame.image.load("assets/images/player_thrust.png").convert_alpha()

        size = (int(PLAYER_RADIUS * 2.5), int(PLAYER_RADIUS * 2.5))
        self.image_idle = pygame.transform.scale(self.image_idle, size)
        self.image_thrust = pygame.transform.scale(self.image_thrust, size)

        self.is_thrusting = False

    def draw(self, screen, is_invincible=False):
        current_img = self.image_thrust if self.is_thrusting else self.image_idle
        angle_correction = -90
        rotated_img = pygame.transform.rotate(current_img, -self.rotation + angle_correction)

        if is_invincible:
            if int(pygame.time.get_ticks() / 100) % 2 == 0:
                return

        new_rect = rotated_img.get_rect(center=self.position)
        screen.blit(rotated_img, new_rect)

    def rotate(self, dt):
        # On ajoute un multiplicateur de vitesse de rotation si l'amélioration est prise
        bonus = getattr(self, 'rotation_speed_bonus', 1.0)
        self.rotation += (PLAYER_TURN_SPEED * bonus) * dt

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt

        self.position += self.velocity * dt
        self.velocity *= PLAYER_FRICTION

        keys = pygame.key.get_pressed()
        self.is_thrusting = False

        if keys[pygame.K_SPACE] and self.timer <= 0:
            self.shoot()

        if keys[pygame.K_q]: self.rotate(-dt)
        if keys[pygame.K_d]: self.rotate(dt)
        if keys[pygame.K_z]:
            self.move(dt)
            self.is_thrusting = True
        if keys[pygame.K_s]: self.move(-dt)

        # --- TRAINÉE ---
        self.trail_timer -= dt
        if self.is_thrusting and self.trail_timer <= 0:
            backward_dir = pygame.Vector2(0, -1).rotate(self.rotation)
            exhaust_pos = self.position + backward_dir * (self.radius * 0.8)
            Trail(exhaust_pos)
            self.trail_timer = 0.03

        self.wrap_position()
        self.has_triple_shot -= dt

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.velocity += forward * PLAYER_ACCELERATION * dt

    def shoot(self):
        # Application du bonus de vitesse de tir
        self.timer = PLAYER_SHOOT_COOLDOWN * self.shoot_cooldown_multiplier

        direction_base = pygame.Vector2(0, 1)
        spawn_pos = self.position + direction_base.rotate(self.rotation) * self.radius

        # 1. Tir Principal (Normal ou Triple)
        if self.has_triple_shot > 0:
            for angle in [-15, 0, 15]:
                shot = Shot(spawn_pos.x, spawn_pos.y)
                shot.owner = "player"
                shot.velocity = direction_base.rotate(self.rotation + angle) * PLAYER_SHOOT_SPEED
        else:
            shot = Shot(spawn_pos.x, spawn_pos.y)
            shot.owner = "player"
            shot.velocity = direction_base.rotate(self.rotation) * PLAYER_SHOOT_SPEED

        # 2. Canons Supplémentaires (Amélioration Level Up)
        for i in range(self.extra_projectiles):
            angle = (i + 1) * 20
            for side in [1, -1]:  # Un à gauche, un à droite
                bonus_shot = Shot(spawn_pos.x, spawn_pos.y)
                bonus_shot.owner = "player"
                bonus_shot.velocity = direction_base.rotate(self.rotation + (angle * side)) * PLAYER_SHOOT_SPEED